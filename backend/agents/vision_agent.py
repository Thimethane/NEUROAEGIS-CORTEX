"""
Vision Agent - Security Frame Analysis
Enhanced with robust error handling and frontend integration
"""

import base64
import numpy as np
from collections import deque
from typing import Dict, Any, Optional
from google.genai import types
from google.genai.types import GenerateContentConfig, Content, Part
from agents.base_agent import BaseAgent
from config.settings import settings, VISION_AGENT_PROMPT


class VisionAgent(BaseAgent):
    """Performs real-time security analysis on video frames using Gemini.

    This agent maintains a temporal history of previous detections to improve
    contextual awareness and reduce false positives across a video stream.
    
    Key improvements:
    - Comprehensive error handling for API failures
    - Always returns all required fields for FastAPI validation
    - Graceful degradation when Gemini API is unavailable
    - Better logging for debugging
    """

    def __init__(self, **kwargs):
        """Initializes the VisionAgent with a 10-frame sliding window history."""
        super().__init__(**kwargs)
        self.max_history = 10
        self.frame_history = deque(maxlen=self.max_history)

    async def process(
        self, 
        frame: np.ndarray = None, 
        base64_image: str = None, 
        frame_number: int = 0
    ) -> Dict[str, Any]:
        """Analyzes visual input for security threats and returns a structured report.

        Args:
            frame: Optional numpy array (OpenCV format) of the video frame.
            base64_image: Optional base64 encoded string of the image.
            frame_number: Current frame index used for temporal tracking.

        Returns:
            Dict[str, Any]: Structured analysis containing incident status, 
                severity, confidence, reasoning, subjects, and recommended_actions.
                ALWAYS returns all required fields even on error.
        """
        try:
            # Prepare image bytes
            try:
                image_bytes = self._prepare_image_bytes(frame, base64_image)
            except Exception as img_error:
                self.logger.error(f"Image preparation failed: {img_error}")
                return self._default_result(f"Image Error: {str(img_error)}")
            
            # Build temporal context
            context = self._build_context()
            
            # Create user prompt
            user_prompt = "Analyze the input based on the security protocol."
            if context:
                user_prompt += f"\n\nTEMPORAL CONTEXT:\n{context}"
    
            # Call Gemini API with comprehensive error handling
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=[
                        types.Content(role="user", parts=[
                            types.Part.from_text(text=user_prompt),
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                        ])
                    ],
                    config=GenerateContentConfig(
                        system_instruction=VISION_AGENT_PROMPT,
                        temperature=settings.TEMPERATURE,
                        response_mime_type="application/json"
                    ),
                )
                
                # Parse response
                result = self._parse_json_response(response.text)
                
                if not result:
                    self.logger.warning("JSON parsing returned None, using default")
                    return self._default_result("JSON parsing failed")
                
                # Validate and return
                validated = self._validate_result(result)
                self._update_history(frame_number, validated)
                return validated
                
            except Exception as api_error:
                # Catch specific Gemini API errors
                error_msg = str(api_error)
                
                # Extract error code if present
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    self.logger.error("Gemini API quota exceeded")
                    return self._default_result("API quota exceeded - try gemini-1.5-flash model")
                elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                    self.logger.error("Gemini API overloaded")
                    return self._default_result("API temporarily unavailable - retrying...")
                elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
                    self.logger.error("Gemini API authentication failed")
                    return self._default_result("API authentication error - check API key")
                else:
                    self.logger.error(f"Vision API Error: {error_msg}")
                    return self._default_result(f"API Error: {error_msg}")
        
        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Unexpected error in vision processing: {e}", exc_info=True)
            return self._default_result(f"Processing Error: {str(e)}")

    def _prepare_image_bytes(
        self, 
        frame: Optional[np.ndarray], 
        base64_str: Optional[str]
    ) -> bytes:
        """Normalizes image input into bytes, handling OpenCV frames and Base64 strings.

        Args:
            frame: Raw image array.
            base64_str: Base64 string (with or without data URI prefix).

        Returns:
            bytes: JPEG encoded image data.
            
        Raises:
            ValueError: If no valid image source provided or encoding fails.
        """
        if frame is not None:
            import cv2
            success, buffer = cv2.imencode(".jpg", frame)
            if not success:
                raise ValueError("Could not encode frame to JPEG")
            return buffer.tobytes()
        
        if base64_str:
            # Remove data URI prefix if present
            if "," in base64_str:
                base64_str = base64_str.split(",")[-1]
            
            # Ensure proper padding for the base64 decoder
            missing_padding = len(base64_str) % 4
            if missing_padding:
                base64_str += "=" * (4 - missing_padding)
                
            try:
                return base64.b64decode(base64_str)
            except Exception as e:
                raise ValueError(f"Base64 decode failed: {e}")
            
        raise ValueError("No valid image source provided (frame or base64_image required)")

    def _build_context(self) -> str:
        """Returns the newline-separated history of recent detections.
        
        Returns:
            str: Formatted string of recent frame analysis history.
        """
        if not self.frame_history:
            return ""
        return "\n".join(self.frame_history)

    def _update_history(self, frame_num: int, result: Dict):
        """Adds the current detection to the sliding window history.
        
        Args:
            frame_num: Current frame number
            result: Analysis result dictionary
        """
        incident_type = result.get('type', 'normal')
        severity = result.get('severity', 'low')
        confidence = result.get('confidence', 0)
        
        summary = f"Frame {frame_num}: {incident_type} ({severity}, {confidence}% conf)"
        self.frame_history.append(summary)

    def _validate_result(self, result: Dict) -> Dict:
        """Clamps confidence scores and ensures all required fields are present.
        
        This is critical for FastAPI response validation. Missing fields will
        cause a 500 error on the frontend.
        
        Args:
            result: Raw result from Gemini API
            
        Returns:
            Dict: Validated result with all required fields
        """
        # Clamp confidence to 0-100 range
        raw_conf = result.get("confidence", 0)
        try:
            confidence = max(0, min(100, int(raw_conf)))
        except (ValueError, TypeError):
            confidence = 0
        
        # Determine incident status based on confidence threshold
        is_incident = result.get("incident", False)
        if confidence < settings.CONFIDENCE_THRESHOLD:
            is_incident = False

        # Normalize severity
        severity = str(result.get("severity", "low")).lower()
        if severity not in ["low", "medium", "high", "critical"]:
            severity = "low"

        # Ensure subjects is a list
        subjects = result.get("subjects", [])
        if not isinstance(subjects, list):
            subjects = []
        
        # Ensure recommended_actions is a list
        recommended_actions = result.get("recommended_actions", [])
        if not isinstance(recommended_actions, list):
            recommended_actions = []

        return {
            "incident": bool(is_incident),
            "type": result.get("type", "unknown"),
            "severity": severity,
            "confidence": confidence,
            "reasoning": result.get("reasoning", "No explanation provided"),
            "subjects": subjects,
            "recommended_actions": recommended_actions
        }

    def _default_result(self, error_msg: str) -> Dict[str, Any]:
        """Returns a safe, non-incident result in case of processing errors.
        
        CRITICAL: This must include ALL fields that FastAPI expects in the response.
        Missing 'subjects' or 'recommended_actions' will cause validation errors.
        
        Args:
            error_msg: Description of the error that occurred
            
        Returns:
            Dict[str, Any]: Complete result with all required fields
        """
        self.logger.info(f"Returning default result due to: {error_msg}")
        
        return {
            "incident": False, 
            "type": "error", 
            "severity": "low", 
            "confidence": 0, 
            "reasoning": error_msg,
            "subjects": [],  # Required field - MUST be present
            "recommended_actions": []  # Required field - MUST be present
        }
    