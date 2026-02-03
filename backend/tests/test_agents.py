"""
AegisAI Enhanced Unit Tests
Run with: pytest tests/test_agents.py -v
"""

import pytest
import numpy as np
import asyncio
from collections import deque
from unittest.mock import MagicMock, patch

from agents.vision_agent import VisionAgent
from agents.planner_agent import PlannerAgent
from config.settings import settings

class TestVisionAgent:
    """Test VisionAgent functionality and Gemini 3 integration logic"""

    @pytest.fixture
    def vision_agent(self):
        agent = VisionAgent()
        return agent

    @pytest.fixture
    def sample_frame(self):
        return np.zeros((720, 1280, 3), dtype=np.uint8)

    def test_agent_initialization(self, vision_agent):
        assert vision_agent.client is not None
        assert vision_agent.model_name == settings.GEMINI_MODEL
        assert isinstance(vision_agent.frame_history, deque)
        assert vision_agent.total_calls == 0

    @pytest.mark.asyncio
    async def test_safe_process_metrics(self, vision_agent, sample_frame):
        """Verify that _safe_process tracks metrics and handles responses."""
        # Mock the underlying process method to avoid API calls
        with patch.object(vision_agent, 'process', return_value={'incident': False, 'confidence': 90}):
            result = await vision_agent._safe_process(frame=sample_frame)
            assert vision_agent.total_calls == 1
            assert vision_agent.avg_response_time > 0
            assert result['incident'] is False

    def test_confidence_threshold_logic(self, vision_agent):
        """
        Test your logic: If confidence < CONFIDENCE_THRESHOLD, 
        incident must be forced to False.
        """
        low_confidence_result = {
            'incident': True,
            'type': 'theft',
            'severity': 'high',
            'confidence': settings.CONFIDENCE_THRESHOLD - 5,
            'reasoning': 'Too blurry to be sure'
        }
        validated = vision_agent._validate_result(low_confidence_result)
        assert validated['incident'] is False
        assert validated['confidence'] == settings.CONFIDENCE_THRESHOLD - 5

    def test_validate_result_clamping(self, vision_agent):
        """Test normalization and data clamping."""
        raw_result = {
            'incident': True,
            'severity': 'CRITICAL', # Test case normalization
            'confidence': 150,      # Test upper clamp
            'type': 'violence'
        }
        validated = vision_agent._validate_result(raw_result)
        assert validated['severity'] == 'critical'
        assert validated['confidence'] == 100
        assert isinstance(validated['subjects'], list)

    def test_history_rotation(self, vision_agent):
        """Ensure temporal context doesn't exceed max_history."""
        vision_agent.frame_history.clear()
        for i in range(vision_agent.max_history + 5):
            vision_agent._update_history(i, {'type': 'normal', 'reasoning': 'test'})
        
        assert len(vision_agent.frame_history) == vision_agent.max_history
        assert "Frame 0:" not in vision_agent._build_context()
        assert f"Frame {vision_agent.max_history + 4}:" in vision_agent._build_context()


class TestPlannerAgent:
    """Test PlannerAgent tactical logic"""

    @pytest.fixture
    def planner_agent(self):
        return PlannerAgent()

    def test_validate_plan_normalization(self, planner_agent):
        """Ensure invalid actions are defaulted to 'log_incident'."""
        bad_plan = [{'step': 1, 'action': 'dance_party', 'priority': 'low'}]
        validated = planner_agent._validate_plan(bad_plan)
        assert validated[0]['action'] == 'log_incident'
        assert validated[0]['step'] == 1

    def test_fallback_plan_critical_severity(self, planner_agent):
        """Ensure critical incidents trigger authorities in fallback."""
        incident = {'severity': 'critical', 'type': 'intrusion'}
        plan = planner_agent._create_fallback_plan(incident)
        
        actions = [step['action'] for step in plan]
        assert 'save_evidence' in actions
        assert 'send_alert' in actions
        # Check that high severity adds more steps than low severity
        assert len(plan) >= 3

    @pytest.mark.asyncio
    async def test_planner_safe_process_error_handling(self, planner_agent):
        """Test that Planner returns a fallback plan even if the API fails."""
        with patch.object(planner_agent.client.models, 'generate_content', side_effect=Exception("API Down")):
            # _safe_process should catch the error and return the fallback
            result = await planner_agent._safe_process(incident={'severity': 'low'})
            assert result is not None
            assert any(step['action'] == 'save_evidence' for step in result)


@pytest.mark.asyncio
async def test_end_to_end_logic_flow():
    """
    Integration test: Mocking the API but testing the 
    data handover between Vision and Planner.
    """
    vision = VisionAgent()
    planner = PlannerAgent()
    
    mock_vision_return = {
        'incident': True,
        'type': 'theft',
        'severity': 'high',
        'confidence': 95,
        'reasoning': 'Detected concealed item'
    }

    with patch.object(vision, 'process', return_value=mock_vision_return):
        # 1. Vision Analysis
        analysis = await vision.process(frame=np.zeros((10, 10, 3)))
        
        # 2. Planner Receipt
        with patch.object(planner, 'process', wraps=planner.process) as planner_spy:
            plan = await planner.process(analysis)
            
            planner_spy.assert_called_once_with(mock_vision_return)
            assert len(plan) > 0
            assert plan[0]['step'] == 1
