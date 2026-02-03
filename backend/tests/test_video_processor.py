import pytest
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock
from services.video_processor import VideoProcessor, DemoScenarioRunner

@pytest.fixture
def mock_frame():
    return np.zeros((720, 1280, 3), dtype=np.uint8)

@pytest.mark.asyncio
async def test_video_processor_full_loop(mock_frame):
    processor = VideoProcessor(source=0)
    
    # Use AsyncMock for the agents since they are awaited
    processor.vision_agent._safe_process = AsyncMock(return_value={
        "incident": True, 
        "type": "theft", 
        "severity": "high",
        "confidence": 95
    })
    processor.planner_agent._safe_process = AsyncMock(return_value=[{"action": "test"}])
    
    # We use patch.multiple or patch specifically for the awaited executor
    with patch("services.video_processor.cv2") as mock_cv2, \
         patch("services.video_processor.db_service") as mock_db, \
         patch("services.video_processor.action_executor", new_callable=AsyncMock) as mock_executor:
        
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, mock_frame)
        mock_cv2.VideoCapture.return_value = mock_cap
        
        # Stop the loop after one iteration
        async def stop_after_one(*args, **kwargs):
            processor.running = False
            return {"incident": True}
        
        processor.vision_agent._safe_process.side_effect = stop_after_one

        await processor.process_stream(display=True)
        
        assert mock_cv2.imshow.called
        assert mock_db.save_incident.called
        # Now this will pass because mock_executor is an AsyncMock
        assert mock_executor.execute_plan.called

@pytest.mark.asyncio
async def test_demo_scenario_runner():
    runner = DemoScenarioRunner()
    runner.vision_agent._safe_process = AsyncMock(return_value={"incident": False})
    
    # Properly close the agents in the runner to clear warnings
    with patch("builtins.print"), \
         patch.object(runner.vision_agent, 'close', new_callable=AsyncMock), \
         patch.object(runner.planner_agent, 'close', new_callable=AsyncMock):
        await runner._run_scenario("Test", "Test Desc", (255, 0, 0))