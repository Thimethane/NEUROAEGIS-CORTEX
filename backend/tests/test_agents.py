"""
Comprehensive Unit Tests for NeuroAegis Cortex AI Agents
Covers Vision Agent, Planner Agent, and Action Executor
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

# Import agents
import sys
sys.path.insert(0, '/app')  # Adjust path as needed

from agents.vision_agent import VisionAgent
from agents.planner_agent import PlannerAgent
from agents.base_agent import BaseAgent
from services.action_executor import ActionExecutor
from config.settings import settings


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini API client"""
    client = Mock()
    client.aio = Mock()
    client.models = Mock()
    return client


@pytest.fixture
def sample_frame():
    """Sample video frame data"""
    import numpy as np
    return np.zeros((720, 1280, 3), dtype=np.uint8)


@pytest.fixture
def sample_base64_image():
    """Sample base64-encoded image"""
    return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD"


@pytest.fixture
def sample_incident():
    """Sample incident data"""
    return {
        "incident": True,
        "type": "intrusion",
        "severity": "high",
        "confidence": 87,
        "reasoning": "Masked individual forcing entry",
        "subjects": ["Adult male, black hoodie"],
        "recommended_actions": ["alert", "record"]
    }


@pytest.fixture
def sample_action_plan():
    """Sample action plan"""
    return [
        {
            "step": 1,
            "action": "save_evidence",
            "priority": "immediate",
            "parameters": {},
            "reasoning": "Preserve forensic evidence"
        },
        {
            "step": 2,
            "action": "send_alert",
            "priority": "high",
            "parameters": {"channels": ["email"]},
            "reasoning": "Notify security personnel"
        }
    ]


# ============================================================================
# BASE AGENT TESTS
# ============================================================================

class TestBaseAgent:
    """Test BaseAgent functionality"""
    
    def test_initialization(self):
        """Test agent initialization"""
        agent = VisionAgent(model_name="test-model")
        assert agent.model_name == "test-model"
        assert agent.total_calls == 0
        assert agent.total_errors == 0
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        agent = VisionAgent()
        stats = agent.get_stats()
        
        assert "agent" in stats
        assert "model" in stats
        assert "total_calls" in stats
        assert "success_rate" in stats
        assert stats["total_calls"] == 0
    
    def test_json_parsing_clean(self):
        """Test JSON parsing with clean input"""
        agent = VisionAgent()
        
        json_str = '{"incident": true, "type": "test"}'
        result = agent._parse_json_response(json_str)
        
        assert result is not None
        assert result["incident"] is True
        assert result["type"] == "test"
    
    def test_json_parsing_markdown(self):
        """Test JSON parsing with markdown code blocks"""
        agent = VisionAgent()
        
        json_str = '```json\n{"incident": true}\n```'
        result = agent._parse_json_response(json_str)
        
        assert result is not None
        assert result["incident"] is True
    
    def test_json_parsing_invalid(self):
        """Test JSON parsing with invalid input"""
        agent = VisionAgent()
        
        result = agent._parse_json_response("not valid json")
        assert result is None
    
    def test_json_parsing_none(self):
        """Test JSON parsing with None input"""
        agent = VisionAgent()
        
        result = agent._parse_json_response(None)
        assert result is None


# ============================================================================
# VISION AGENT TESTS
# ============================================================================

class TestVisionAgent:
    """Test VisionAgent functionality"""
    
    def test_initialization(self):
        """Test vision agent initialization"""
        agent = VisionAgent()
        
        assert agent.max_history == 10
        assert len(agent.frame_history) == 0
    
    def test_default_result(self):
        """Test default result generation"""
        agent = VisionAgent()
        
        result = agent._default_result("Test error")
        
        # Check all required fields are present
        assert "incident" in result
        assert "type" in result
        assert "severity" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "subjects" in result
        assert "recommended_actions" in result
        
        # Check values
        assert result["incident"] is False
        assert result["type"] == "error"
        assert result["subjects"] == []
        assert result["recommended_actions"] == []
    
    def test_validate_result(self):
        """Test result validation"""
        agent = VisionAgent()
        
        raw_result = {
            "incident": True,
            "type": "intrusion",
            "severity": "high",
            "confidence": 150,  # Out of range
            "reasoning": "Test",
            "subjects": ["Person 1"],
            "recommended_actions": ["alert"]
        }
        
        validated = agent._validate_result(raw_result)
        
        # Check confidence was clamped
        assert validated["confidence"] == 100
        
        # Check all fields present
        assert validated["incident"] is True
        assert validated["type"] == "intrusion"
        assert validated["severity"] == "high"
    
    def test_validate_result_missing_fields(self):
        """Test validation adds missing fields"""
        agent = VisionAgent()
        
        raw_result = {
            "incident": True,
            "type": "test"
            # Missing other fields
        }
        
        validated = agent._validate_result(raw_result)
        
        # Check defaults were added
        assert "subjects" in validated
        assert "recommended_actions" in validated
        assert isinstance(validated["subjects"], list)
        assert isinstance(validated["recommended_actions"], list)
    
    def test_build_context_empty(self):
        """Test context building with no history"""
        agent = VisionAgent()
        
        context = agent._build_context()
        assert context == ""
    
    def test_build_context_with_history(self):
        """Test context building with frame history"""
        agent = VisionAgent()
        
        agent.frame_history.append("Frame 1: normal")
        agent.frame_history.append("Frame 2: suspicious")
        
        context = agent._build_context()
        
        assert "Frame 1" in context
        assert "Frame 2" in context
    
    def test_update_history(self):
        """Test frame history updates"""
        agent = VisionAgent()
        
        result = {
            "type": "intrusion",
            "severity": "high",
            "confidence": 85
        }
        
        agent._update_history(42, result)
        
        assert len(agent.frame_history) == 1
        assert "Frame 42" in agent.frame_history[0]
        assert "intrusion" in agent.frame_history[0]
    
    def test_prepare_image_bytes_base64(self, sample_base64_image):
        """Test image bytes preparation from base64"""
        agent = VisionAgent()
        
        # Should not raise exception
        image_bytes = agent._prepare_image_bytes(None, sample_base64_image)
        assert isinstance(image_bytes, bytes)
    
    def test_prepare_image_bytes_invalid(self):
        """Test image bytes preparation with invalid input"""
        agent = VisionAgent()
        
        with pytest.raises(ValueError):
            agent._prepare_image_bytes(None, None)


# ============================================================================
# PLANNER AGENT TESTS
# ============================================================================

class TestPlannerAgent:
    """Test PlannerAgent functionality"""
    
    def test_initialization(self):
        """Test planner agent initialization"""
        agent = PlannerAgent()
        
        assert hasattr(agent, 'VALID_ACTIONS')
        assert 'save_evidence' in agent.VALID_ACTIONS
        assert 'send_alert' in agent.VALID_ACTIONS
    
    def test_validate_plan(self, sample_action_plan):
        """Test action plan validation"""
        agent = PlannerAgent()
        
        validated = agent._validate_plan(sample_action_plan)
        
        assert len(validated) == len(sample_action_plan)
        
        for step in validated:
            assert "step" in step
            assert "action" in step
            assert "priority" in step
            assert "parameters" in step
            assert "reasoning" in step
    
    def test_validate_plan_invalid_action(self):
        """Test validation replaces invalid actions"""
        agent = PlannerAgent()
        
        invalid_plan = [
            {
                "step": 1,
                "action": "invalid_action_name",
                "priority": "high",
                "parameters": {},
                "reasoning": "Test"
            }
        ]
        
        validated = agent._validate_plan(invalid_plan)
        
        # Should replace with log_incident
        assert validated[0]["action"] == "log_incident"
    
    def test_validate_plan_invalid_priority(self):
        """Test validation normalizes invalid priorities"""
        agent = PlannerAgent()
        
        invalid_plan = [
            {
                "step": 1,
                "action": "save_evidence",
                "priority": "super_urgent",  # Invalid
                "parameters": {},
                "reasoning": "Test"
            }
        ]
        
        validated = agent._validate_plan(invalid_plan)
        
        # Should default to medium
        assert validated[0]["priority"] == "medium"
    
    def test_create_fallback_plan_low(self):
        """Test fallback plan for low severity"""
        agent = PlannerAgent()
        
        incident = {
            "type": "suspicious_behavior",
            "severity": "low",
            "confidence": 65
        }
        
        plan = agent._create_fallback_plan(incident)
        
        assert len(plan) >= 2
        assert plan[0]["action"] == "save_evidence"
        assert "log_incident" in [step["action"] for step in plan]
    
    def test_create_fallback_plan_critical(self):
        """Test fallback plan for critical severity"""
        agent = PlannerAgent()
        
        incident = {
            "type": "violence",
            "severity": "critical",
            "confidence": 95
        }
        
        plan = agent._create_fallback_plan(incident)
        
        assert len(plan) >= 4
        assert plan[0]["action"] == "save_evidence"
        assert "send_alert" in [step["action"] for step in plan]
        assert "escalate" in [step["action"] for step in plan]
    
    def test_get_action_description(self):
        """Test action description retrieval"""
        agent = PlannerAgent()
        
        desc = agent.get_action_description("save_evidence")
        assert isinstance(desc, str)
        assert len(desc) > 0


# ============================================================================
# ACTION EXECUTOR TESTS
# ============================================================================

class TestActionExecutor:
    """Test ActionExecutor functionality"""
    
    @pytest.fixture
    def executor(self):
        """Create ActionExecutor instance"""
        return ActionExecutor()
    
    def test_initialization(self, executor):
        """Test executor initialization"""
        assert hasattr(executor, 'executed_actions')
        assert len(executor.executed_actions) == 0
    
    @pytest.mark.asyncio
    async def test_save_evidence_action(self, executor):
        """Test save evidence action"""
        # Should not raise exception
        await executor._save_evidence(
            incident_id=1,
            evidence_path="/tmp/test.jpg",
            params={}
        )
    
    @pytest.mark.asyncio
    async def test_log_incident_action(self, executor):
        """Test log incident action"""
        # Should not raise exception
        await executor._log_incident(
            incident_id=1,
            evidence_path="",
            params={}
        )
    
    @pytest.mark.asyncio
    async def test_monitor_action(self, executor):
        """Test monitor action"""
        # Should not raise exception
        await executor._monitor(
            incident_id=1,
            evidence_path="",
            params={"duration": 10}
        )
    
    def test_get_execution_history(self, executor):
        """Test execution history retrieval"""
        # Add some fake history
        executor.executed_actions.append({
            "action": "test",
            "status": "completed"
        })
        
        history = executor.get_execution_history(limit=10)
        assert len(history) == 1
        assert history[0]["action"] == "test"
    
    def test_get_execution_stats_empty(self, executor):
        """Test stats with no executions"""
        stats = executor.get_execution_stats()
        
        assert stats["total_actions"] == 0
        assert stats["success_rate"] == 0.0
    
    def test_get_execution_stats_with_data(self, executor):
        """Test stats with execution data"""
        executor.executed_actions = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "failed"}
        ]
        
        stats = executor.get_execution_stats()
        
        assert stats["total_actions"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, rel=0.1)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_vision_to_planner_workflow(self, sample_incident):
        """Test complete workflow from vision to planning"""
        planner = PlannerAgent()
        
        # Generate plan from incident
        plan = await planner._safe_process(sample_incident)
        
        # Validate plan
        assert plan is not None
        assert len(plan) > 0
        assert all("action" in step for step in plan)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance benchmarking tests"""
    
    def test_json_parsing_performance(self):
        """Benchmark JSON parsing speed"""
        agent = VisionAgent()
        
        json_str = json.dumps({
            "incident": True,
            "type": "test",
            "severity": "high",
            "confidence": 85,
            "reasoning": "Test reasoning",
            "subjects": ["Test subject"],
            "recommended_actions": ["alert"]
        })
        
        import time
        start = time.time()
        
        for _ in range(1000):
            agent._parse_json_response(json_str)
        
        elapsed = time.time() - start
        
        # Should parse 1000 times in under 1 second
        assert elapsed < 1.0
    
    def test_validation_performance(self):
        """Benchmark validation speed"""
        agent = VisionAgent()
        
        result = {
            "incident": True,
            "type": "test",
            "severity": "high",
            "confidence": 85,
            "reasoning": "Test",
            "subjects": ["Person"],
            "recommended_actions": ["alert"]
        }
        
        import time
        start = time.time()
        
        for _ in range(10000):
            agent._validate_result(result)
        
        elapsed = time.time() - start
        
        # Should validate 10000 times in under 1 second
        assert elapsed < 1.0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
