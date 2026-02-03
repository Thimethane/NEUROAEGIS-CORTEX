"""
AegisAI Video Processor Service - Enhanced
Handles webcam ingestion, frame processing, and demo scenarios with Gemini Vision
"""

import asyncio
import time
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

# Internal AegisAI imports
from config.settings import settings
from agents.vision_agent import VisionAgent
from agents.planner_agent import PlannerAgent
from services.action_executor import action_executor
from services.database_service import db_service

# Logging setup
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class VideoProcessor:
    """Enhanced video processing pipeline with better error handling and performance"""
    
    def __init__(self, source: int = 0, frame_rate: int = None):
        """
        Initialize video processor
        
        Args:
            source: Video source (0 for webcam, or video file path)
            frame_rate: Seconds between frame processing (default from settings)
        """
        self.source = source
        self.frame_rate = frame_rate or settings.FRAME_SAMPLE_RATE
        self.cap: Optional[cv2.VideoCapture] = None
        
        # Initialize Gemini agents with configuration
        agent_config = {
            "model_name": settings.GEMINI_MODEL,
            "api_key": settings.GEMINI_API_KEY,
        }
        self.vision_agent = VisionAgent(**agent_config)
        self.planner_agent = PlannerAgent(**agent_config)
        
        # Processing state
        self.running = False
        self.frame_count = 0
        self.incident_count = 0
        self.last_incident_time = 0
        
        # Performance tracking
        self.total_processing_time = 0
        self.frames_processed = 0
        
        logger.info(f"✅ VideoProcessor initialized (source: {source}, rate: {frame_rate}s)")

    def initialize_capture(self) -> bool:
        """Initialize video capture with error handling"""
        try:
            self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                logger.error(f"❌ Failed to open video source: {self.source}")
                return False
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.VIDEO_RESOLUTION_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.VIDEO_RESOLUTION_HEIGHT)
            
            # Get actual resolution
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"✅ Video capture initialized: {actual_width}x{actual_height}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize capture: {e}")
            return False

    async def process_stream(self, display: bool = True):
        """
        Main processing loop for video stream
        
        Args:
            display: Whether to show video feed in window
        """
        if not self.initialize_capture():
            logger.error("❌ Cannot start processing - capture initialization failed")
            return
        
        self.running = True
        last_process_time = 0
        
        logger.info("🎥 Starting video stream processing...")

        try:
            while self.running:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("⚠️ Failed to read frame from video source")
                    break
                
                self.frame_count += 1
                now = time.time()
                
                # Process frame at specified interval
                if now - last_process_time >= self.frame_rate:
                    await self._process_frame(frame)
                    last_process_time = now

                # Display video feed if enabled
                if display:
                    # Add overlay with system info
                    self._add_overlay(frame)
                    
                    cv2.imshow('AegisAI Monitor', frame)
                    
                    # ESC key to exit
                    if cv2.waitKey(1) & 0xFF == 27:
                        logger.info("⏹️ ESC pressed - stopping...")
                        break
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Keyboard interrupt received - stopping...")
        except Exception as e:
            logger.error(f"❌ Error in processing loop: {e}", exc_info=True)
        finally:
            self.cleanup()
            self._print_session_summary()

    async def _process_frame(self, frame: np.ndarray):
        """
        Process a single frame through the AI pipeline
        
        Args:
            frame: OpenCV frame (numpy array)
        """
        start_time = time.time()
        
        try:
            # Analyze frame with VisionAgent
            analysis = await self.vision_agent._safe_process(
                frame=frame, 
                frame_number=self.frame_count
            )
            
            if not analysis:
                logger.warning(f"⚠️ Frame {self.frame_count} analysis returned None")
                return
            
            # Log analysis result
            logger.debug(
                f"Frame {self.frame_count}: {analysis.get('type', 'unknown')} | "
                f"Severity: {analysis.get('severity', 'low')} | "
                f"Confidence: {analysis.get('confidence', 0)}%"
            )
            
            # Handle incident detection
            if analysis.get('incident'):
                await self._handle_incident(frame, analysis)
            
            # Update performance metrics
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            self.frames_processed += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing frame {self.frame_count}: {e}")

    async def _handle_incident(self, frame: np.ndarray, analysis: Dict[str, Any]):
        """
        Handle detected incident with evidence saving and response planning
        
        Args:
            frame: Original video frame
            analysis: VisionAgent analysis result
        """
        self.incident_count += 1
        incident_type = analysis.get('type', 'unknown')
        severity = analysis.get('severity', 'low')
        confidence = analysis.get('confidence', 0)
        
        logger.warning(
            f"🚨 INCIDENT #{self.incident_count} DETECTED | "
            f"Type: {incident_type} | Severity: {severity} | Confidence: {confidence}%"
        )
        
        try:
            # Save evidence frame
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            evidence_filename = f"incident_{self.incident_count}_{timestamp}.jpg"
            evidence_path = settings.EVIDENCE_DIR / evidence_filename
            
            # Ensure evidence directory exists
            settings.EVIDENCE_DIR.mkdir(exist_ok=True, parents=True)
            
            # Save high-quality evidence
            cv2.imwrite(str(evidence_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            logger.info(f"💾 Evidence saved: {evidence_path}")
            
            # Generate response plan
            plan = await self.planner_agent._safe_process(analysis)
            
            if not plan:
                logger.warning(f"⚠️ No response plan generated for incident #{self.incident_count}")
                plan = []
            else:
                logger.info(f"📋 Generated {len(plan)}-step response plan")
            
            # Save incident to database
            incident_data = {
                **analysis,
                "evidence_path": str(evidence_path),
                "response_plan": plan,
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat()
            }
            
            incident_id = db_service.save_incident(incident_data)
            
            if incident_id <= 0:
                logger.error(f"❌ Failed to save incident to database")
                return
            
            # Execute response plan
            if plan:
                logger.info(f"🚀 Executing response plan for incident #{incident_id}")
                await action_executor.execute_plan(plan, incident_id, str(evidence_path))
            
            self.last_incident_time = time.time()
            
        except Exception as e:
            logger.error(f"❌ Error handling incident: {e}", exc_info=True)

    def _add_overlay(self, frame: np.ndarray):
        """Add informational overlay to video frame"""
        try:
            # System status
            status_text = f"AegisAI | Frame: {self.frame_count} | Incidents: {self.incident_count}"
            cv2.putText(
                frame, status_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )
            
            # Processing rate
            if self.frames_processed > 0:
                avg_time = self.total_processing_time / self.frames_processed
                rate_text = f"Avg Processing: {avg_time:.2f}s | Rate: {self.frame_rate}s"
                cv2.putText(
                    frame, rate_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
                )
            
            # Recording indicator
            if self.running:
                cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
                
        except Exception as e:
            logger.error(f"❌ Error adding overlay: {e}")

    def _print_session_summary(self):
        """Print summary of processing session"""
        logger.info("=" * 60)
        logger.info("📊 SESSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Frames: {self.frame_count}")
        logger.info(f"Frames Processed: {self.frames_processed}")
        logger.info(f"Incidents Detected: {self.incident_count}")
        
        if self.frames_processed > 0:
            avg_time = self.total_processing_time / self.frames_processed
            logger.info(f"Avg Processing Time: {avg_time:.2f}s/frame")
            
            detection_rate = (self.incident_count / self.frames_processed) * 100
            logger.info(f"Detection Rate: {detection_rate:.2f}%")
        
        logger.info("=" * 60)

    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("✅ Video processor cleaned up")

    def stop(self):
        """Stop processing (can be called from another thread)"""
        self.running = False
        logger.info("⏹️ Stop requested")


# ============================================================================
# DEMO SCENARIO RUNNER
# ============================================================================

class DemoScenarioRunner:
    """Runs high-visibility demo scenarios with terminal output"""
    
    def __init__(self):
        """Initialize demo runner with AI agents"""
        agent_config = {
            "model_name": settings.GEMINI_MODEL,
            "api_key": settings.GEMINI_API_KEY,
        }
        self.vision_agent = VisionAgent(**agent_config)
        self.planner_agent = PlannerAgent(**agent_config)
        
        logger.info("✅ DemoScenarioRunner initialized")

    async def run_demo_sequence(self):
        """Run complete demo scenario sequence"""
        print("\n" + "🛡️ STARTING AEGISAI DEMO SCENARIO".center(70, "="))
        print("=" * 70 + "\n")

        scenarios = [
            (
                "Normal Activity", 
                "A person walking calmly through a hallway, going about their day",
                (0, 255, 0),
                "low"
            ),
            (
                "Suspicious Behavior", 
                "Someone wearing a mask and peering into windows suspiciously",
                (0, 165, 255),
                "medium"
            ),
            (
                "Security Breach",
                "An unauthorized person attempting to open a locked door",
                (0, 100, 255),
                "high"
            ),
            (
                "Critical Threat", 
                "A physical altercation with visible weapon",
                (0, 0, 255),
                "critical"
            )
        ]

        for i, (title, desc, color, expected_severity) in enumerate(scenarios, 1):
            print(f"\n{'='*70}")
            print(f"SCENARIO {i}/{len(scenarios)}: {title}")
            print(f"{'='*70}")
            await self._run_scenario(title, desc, color, expected_severity)
            
            if i < len(scenarios):
                await asyncio.sleep(3)  # Pause between scenarios

        print("\n" + "✅ DEMO SEQUENCE COMPLETED".center(70, "="))
        print("=" * 70 + "\n")
        
        # Print session stats
        self._print_demo_stats()

    async def _run_scenario(
        self, 
        title: str, 
        description: str, 
        color: tuple,
        expected_severity: str
    ):
        """Run a single demo scenario"""
        print(f"\n📝 Description: {description}")
        print(f"🎯 Expected Severity: {expected_severity.upper()}\n")
        
        # Create visual frame
        frame = self._create_demo_frame(description, color)
        
        # Analyze using VisionAgent
        start_time = time.time()
        result = await self.vision_agent._safe_process(frame=frame, frame_number=1)
        processing_time = time.time() - start_time

        # Display results
        if result:
            incident_detected = result.get('incident', False)
            detected_type = result.get('type', 'unknown')
            severity = result.get('severity', 'N/A')
            confidence = result.get('confidence', 0)
            
            print(f"{'🚨' if incident_detected else '✅'} Incident Detected: {incident_detected}")
            print(f"📊 Type: {detected_type}")
            print(f"⚠️  Severity: {severity.upper()}")
            print(f"🎯 Confidence: {confidence}%")
            print(f"⏱️  Processing Time: {processing_time:.2f}s")
            
            if result.get('reasoning'):
                print(f"\n💭 Analysis: {result['reasoning']}")
            
            # Generate and display response plan if incident
            if incident_detected:
                plan = await self.planner_agent._safe_process(result)
                if plan:
                    print(f"\n📋 Response Plan ({len(plan)} actions):")
                    for i, step in enumerate(plan, 1):
                        action = step.get('action', 'unknown')
                        priority = step.get('priority', 'medium')
                        print(f"   {i}. [{priority.upper()}] {action}")
        else:
            print("❌ Analysis failed - No result returned")

    def _create_demo_frame(self, text: str, color: tuple) -> np.ndarray:
        """Create a demo frame with text overlay"""
        # Create black canvas
        frame = np.zeros(
            (settings.VIDEO_RESOLUTION_HEIGHT, settings.VIDEO_RESOLUTION_WIDTH, 3), 
            dtype=np.uint8
        )
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2
        
        # Calculate text size for centering
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Center text
        x = (frame.shape[1] - text_width) // 2
        y = (frame.shape[0] + text_height) // 2
        
        # Add text with shadow for better visibility
        cv2.putText(frame, text, (x + 2, y + 2), font, font_scale, (0, 0, 0), thickness + 1)
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
        
        return frame

    def _print_demo_stats(self):
        """Print demo statistics"""
        vision_stats = self.vision_agent.get_stats()
        planner_stats = self.planner_agent.get_stats()
        
        print(f"\n{'='*70}")
        print("📊 DEMO STATISTICS")
        print(f"{'='*70}")
        print(f"\nVision Agent:")
        print(f"  Total Calls: {vision_stats['total_calls']}")
        print(f"  Errors: {vision_stats['total_errors']}")
        print(f"  Success Rate: {vision_stats['success_rate']}%")
        print(f"  Avg Response Time: {vision_stats['avg_response_time']}s")
        
        print(f"\nPlanner Agent:")
        print(f"  Total Calls: {planner_stats['total_calls']}")
        print(f"  Errors: {planner_stats['total_errors']}")
        print(f"  Success Rate: {planner_stats['success_rate']}%")
        print(f"  Avg Response Time: {planner_stats['avg_response_time']}s")
        print(f"\n{'='*70}\n")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for video processor"""
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "demo":
            # Run demo scenarios
            runner = DemoScenarioRunner()
            await runner.run_demo_sequence()
        else:
            # Run live video processing
            processor = VideoProcessor(source=settings.VIDEO_SOURCE)
            await processor.process_stream(display=True)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
