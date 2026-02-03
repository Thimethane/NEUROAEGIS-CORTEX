"""
Base Agent - Foundation for all AegisAI agents
Enhanced with robust error handling and performance tracking
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from google import genai
from config.settings import settings


class BaseAgent(ABC):
    """Abstract base class for all AegisAI agents.

    Provides common patterns for initialization, performance metrics,
    and robust JSON parsing for Gemini-based models.

    Attributes:
        model_name (str): The identifier of the Gemini model being used.
        api_key (str): The API key for Google GenAI services.
        logger (logging.Logger): Class-specific logger instance.
        total_calls (int): Number of times the agent has been invoked.
        total_errors (int): Number of times the agent process failed.
        avg_response_time (float): Running average of processing time in seconds.
    """

    def __init__(
        self, 
        model_name: Optional[str] = None, 
        api_key: Optional[str] = None, 
        **kwargs
    ):
        """Initializes the agent with the Google GenAI Client.

        Args:
            model_name: Gemini model to use. Defaults to settings.GEMINI_MODEL.
            api_key: Gemini API key. Defaults to settings.GEMINI_API_KEY.
            **kwargs: Additional optional parameters stored as instance attributes.
        """
        self.model_name = model_name or settings.GEMINI_MODEL
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.logger = logging.getLogger(self.__class__.__name__)

        # Store any additional kwargs as instance attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.client = None
        self._initialize_client()

        # Performance tracking
        self.total_calls = 0
        self.total_errors = 0
        self.avg_response_time = 0.0

    def _initialize_client(self):
        """Initializes the GenAI client with standard error handling."""
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info(f"✅ Initialized GenAI client for {self.model_name}")
        except Exception as e:
            self.logger.error(f"❌ Client initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize Gemini client: {e}")
            
    def get_stats(self) -> Dict[str, Any]:
        """Returns performance metrics for this specific agent.

        Returns:
            Dict[str, Any]: A dictionary containing call counts, error counts,
                and average response latency.
        """
        success_rate = 0.0
        if self.total_calls > 0:
            success_rate = ((self.total_calls - self.total_errors) / self.total_calls) * 100
        
        return {
            "agent": self.__class__.__name__,
            "model": self.model_name,
            "total_calls": self.total_calls,
            "total_errors": self.total_errors,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(self.avg_response_time, 3)
        }

    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Core logic to be implemented by subclasses.
        
        This method must be overridden by all agent implementations.
        """
        pass

    async def _safe_process(self, *args, **kwargs) -> Any:
        """Wraps process() with error handling, metrics, and fallback logic.

        This ensures that the main pipeline does not crash if an individual 
        agent call fails due to API issues or logic errors.

        Returns:
            The processed result or a subclass-specific fallback result.
        """
        start_time = time.time()
        self.total_calls += 1

        try:
            result = await self.process(*args, **kwargs)
            
            # Update performance metrics
            elapsed = time.time() - start_time
            self.avg_response_time = (
                (self.avg_response_time * (self.total_calls - 1) + elapsed)
                / self.total_calls
            )
            
            self.logger.debug(f"✅ {self.__class__.__name__} processed in {elapsed:.2f}s")
            return result
            
        except Exception as e:
            self.total_errors += 1
            self.logger.error(
                f"❌ Processing error in {self.__class__.__name__}: {e}",
                exc_info=True
            )
            
            # Try to use subclass-specific fallback methods
            if hasattr(self, '_create_fallback_plan'):
                incident = kwargs.get('incident') or (args[0] if args else {})
                return self._create_fallback_plan(incident)
            
            if hasattr(self, '_default_result'):
                return self._default_result(str(e))
            
            # If no fallback available, return None
            return None

    def _parse_json_response(self, response_text: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parses JSON from Gemini, handling Markdown blocks and NoneTypes.

        Gemini sometimes wraps JSON in markdown code blocks like:
        ```json
        {"key": "value"}
        ```
        
        This method handles those cases and extracts pure JSON.

        Args:
            response_text: The raw text string returned by the model.

        Returns:
            A parsed dictionary or None if parsing fails.
        """
        if not response_text:
            self.logger.warning("Received empty response text")
            return None
            
        try:
            text = response_text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```"):
                # Split by ``` and take the middle part
                parts = text.split("```")
                if len(parts) >= 2:
                    text = parts[1]
                    # Remove language identifier (e.g., "json")
                    if text.startswith("json"):
                        text = text[4:]
            
            # Clean up any remaining backticks and whitespace
            text = text.strip("` \n\r\t")
            
            # Parse JSON
            parsed = json.loads(text)
            self.logger.debug(f"✅ Successfully parsed JSON response")
            return parsed
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parse error: {e}")
            self.logger.debug(f"Raw response text: {response_text[:200]}...")
            return None
        except Exception as e:
            self.logger.error(f"❌ Unexpected error parsing response: {e}")
            return None
            
    async def close(self):
        """Closes the GenAI client session to release resources.
        
        This prevents 'unawaited coroutine' warnings by explicitly 
        shutting down the internal HTTP session.
        
        Should be called when the agent is no longer needed.
        """
        if self.client:
            try:
                # Close async client session
                await self.client.aio.close()
                self.logger.info(f"🔒 GenAI client for {self.model_name} closed.")
            except Exception as e:
                self.logger.error(f"❌ Error during client shutdown: {e}")
                
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"model={self.model_name}, "
            f"calls={self.total_calls}, "
            f"errors={self.total_errors})"
        )
