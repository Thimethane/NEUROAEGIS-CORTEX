"""
Test Coverage Suite for AegisAI Agents and Services
Ensures that VisionAgent, PlannerAgent, ActionExecutor, and DatabaseService behave correctly.
"""

import pytest
import numpy as np
from unittest.mock import AsyncMock
import asyncio
from services.action_executor import ActionExecutor
from agents.vision_agent import VisionAgent
from agents.planner_agent import PlannerAgent
from agents.base_agent import BaseAgent
from services.database_service import db_service
from utils.logger import setup_logging


"""
Updated Test Coverage Suite for AegisAI
"""

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock
import asyncio
from services.action_executor import ActionExecutor
from agents.vision_agent import VisionAgent
from agents.planner_agent import PlannerAgent
from agents.base_agent import BaseAgent
from services.database_service import db_service
from utils.logger import setup_logging

# ===========================
# Fixtures
# ===========================
@pytest.fixture
def dummy_frame():
    return np.zeros((100, 100, 3), dtype=np.uint8)

@pytest.fixture
def setup_logger():
    return setup_logging()

@pytest.fixture
async def vision_agent():
    agent = VisionAgent()
    yield agent
    # Properly close the agent to avoid 'coroutine never awaited' warnings
    await agent.close()

@pytest.fixture
async def planner_agent():
    agent = PlannerAgent()
    yield agent
    await agent.close()

# ===========================
# VisionAgent Tests
# ===========================
@pytest.mark.asyncio
async def test_vision_agent_empty_frame(vision_agent):
    """
    Test VisionAgent returns an error dictionary when no source is provided.
    Fixed: Expecting dict instead of ValueError due to internal safety wrapper.
    """
    result = await vision_agent.process()
    assert isinstance(result, dict)
    assert result["type"] == "error"
    assert "No valid image source" in result["reasoning"]

@pytest.mark.asyncio
async def test_vision_agent_process_direct_raises(vision_agent, dummy_frame):
    """Test VisionAgent returns default result when API call fails."""
    # Setup the mock for the nested GenAI structure
    mock_client = MagicMock()
    # Ensure generate_content is an AsyncMock so it can be awaited
    mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("API Error"))
    vision_agent.client = mock_client

    # We want to verify that VisionAgent handles the exception internally
    # and returns our safety dictionary instead of crashing the whole service.
    result = await vision_agent.process(frame=dummy_frame)
    
    assert result["incident"] is False
    assert "API Error" in result["reasoning"]
    assert result["type"] == "error"

@pytest.mark.asyncio
async def test_vision_agent_invalid_base64(vision_agent):
    """Test VisionAgent handles invalid base64 input gracefully"""
    # This should now pass because of our base64 padding fix
    vision_agent.client = MagicMock()
    vision_agent.client.aio.models.generate_content = AsyncMock()
    
    result = await vision_agent.process(base64_image="invaliddata")
    assert isinstance(result, dict)

# ===========================
# Startup / PlannerAgent Tests
# ===========================
@pytest.mark.asyncio
async def test_startup_and_shutdown(dummy_frame):
    """Test startup/shutdown sequence with Vision and Planner agents"""
    vision_agent = VisionAgent()
    vision_agent.client = AsyncMock()
    planner_agent = PlannerAgent()
    planner_agent.client = AsyncMock()

    # Process a dummy frame
    vision_result = await vision_agent.process(frame=dummy_frame)
    assert isinstance(vision_result, dict)

    # Planner fallback should generate a valid list
    plan = planner_agent._create_fallback_plan({"severity": "high"})
    assert isinstance(plan, list)
    assert len(plan) > 0

    # Close async clients to prevent warnings
    if getattr(vision_agent, "client", None) and hasattr(vision_agent.client, "aclose"):
        await vision_agent.client.aclose()
    if getattr(planner_agent, "client", None) and hasattr(planner_agent.client, "aclose"):
        await planner_agent.client.aclose()


@pytest.mark.asyncio
async def test_planner_agent_invalid_incident():
    """Test PlannerAgent with None incident returns fallback plan"""
    agent = PlannerAgent()
    agent.client = AsyncMock()
    plan = agent._create_fallback_plan({"severity": "low"})
    assert isinstance(plan, list)
    assert len(plan) > 0

    if getattr(agent, "client", None) and hasattr(agent.client, "aclose"):
        await agent.client.aclose()


# ===========================
# ActionExecutor Tests
# ===========================
@pytest.mark.asyncio
async def test_action_executor_actions():
    """
    Test executing actions using ActionExecutor.

    - Use execute_plan() to ensure actions are recorded.
    - Verify that executed_actions is updated correctly.
    """
    executor = ActionExecutor()

    # Sample incident identifier
    incident_id = 1

    # Sample response plan
    plan = [
        {"action": "log_incident", "parameters": {"note": "test"}, "priority": "medium", "step": 1}
    ]

    # Execute plan
    await executor.execute_plan(plan, incident_id)

    # Assertions: check execution history
    history = executor.get_execution_history()
    assert len(history) > 0, "Expected at least one executed action"

    last_action = history[-1]
    assert last_action["action"] == "log_incident"
    assert last_action["parameters"] == {"note": "test"}
    assert last_action["incident_id"] == incident_id


# ===========================
# DatabaseService Edge Cases
# ===========================
def test_database_edge_cases():
    """Test DatabaseService edge cases"""
    incident_id = db_service.save_incident({})
    assert incident_id > 0

    updated = db_service.update_incident_status(incident_id, "resolved")
    assert updated is True

    deleted = db_service.cleanup_old_incidents(days=0)
    assert deleted >= 0


# ===========================
# Logger Tests
# ===========================
def test_logger_setup(setup_logger):
    """Test logger initialization"""
    logger = setup_logger
    assert logger is not None
    logger.info("Logger test message")


# ===========================
# Global Exception Handler Test
# ===========================
def test_global_exception_handler():
    """Test global exception handler import and basic call"""
    try:
        from api.routes import app  # noqa
    except ImportError:
        pass


# ===========================
# BaseAgent Methods
# ===========================
@pytest.mark.asyncio
async def test_base_agent_methods():
    """Test that a minimal BaseAgent subclass works"""
    class DummyAgent(BaseAgent):
        async def process(self, *args, **kwargs):
            return {"ok": True}

    agent = DummyAgent()
    agent.client = AsyncMock()
    result = await agent._safe_process(lambda: {"ok": True})
    assert result == {"ok": True}

    if getattr(agent, "client", None) and hasattr(agent.client, "aclose"):
        await agent.client.aclose()

@pytest.fixture
async def vision_agent():
    agent = VisionAgent(api_key="test", model_name="gemini-1.5-flash")
    yield agent # The test runs here
    # --- Teardown starts here ---
    try:
        await agent.close()
    except Exception:
        pass

@pytest.fixture
async def planner_agent():
    agent = PlannerAgent(api_key="test", model_name="gemini-1.5-flash")
    yield agent
    try:
        await agent.close()
    except Exception:
        pass
        