"""
AegisAI Backend Configuration
Centralized settings management with environment variable support
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    GEMINI_API_KEY: str = Field(..., json_schema_extra={"env_names": ["GEMINI_API_KEY"]})
    API_HOST: str = Field("0.0.0.0", json_schema_extra={"env_names": ["API_HOST"]})
    API_PORT: int = Field(8000, json_schema_extra={"env_names": ["API_PORT"]})

    # Video Processing
    VIDEO_SOURCE: int = Field(0, json_schema_extra={"env_names": ["VIDEO_SOURCE"]})
    FRAME_SAMPLE_RATE: int = Field(2, json_schema_extra={"env_names": ["FRAME_SAMPLE_RATE"]})
    VIDEO_RESOLUTION_WIDTH: int = Field(1280, json_schema_extra={"env_names": ["VIDEO_RESOLUTION_WIDTH"]})
    VIDEO_RESOLUTION_HEIGHT: int = Field(720, json_schema_extra={"env_names": ["VIDEO_RESOLUTION_HEIGHT"]})

    # Storage
    EVIDENCE_DIR: Path = Field(Path("evidence"), json_schema_extra={"env_names": ["EVIDENCE_DIR"]})
    DB_PATH: Path = Field(Path("aegis.db"), json_schema_extra={"env_names": ["DB_PATH"]})
    MAX_EVIDENCE_AGE_DAYS: int = Field(30, json_schema_extra={"env_names": ["MAX_EVIDENCE_AGE_DAYS"]})

    # AI Model Configuration
    GEMINI_MODEL: str = Field("gemini-3-pro-preview", json_schema_extra={"env_names": ["GEMINI_MODEL"]})
    TEMPERATURE: float = Field(0.4, json_schema_extra={"env_names": ["TEMPERATURE"]})
    MAX_OUTPUT_TOKENS: int = Field(300, json_schema_extra={"env_names": ["MAX_OUTPUT_TOKENS"]})

    # Analysis Thresholds
    CONFIDENCE_THRESHOLD: int = Field(70, json_schema_extra={"env_names": ["CONFIDENCE_THRESHOLD"]})
    HIGH_SEVERITY_THRESHOLD: int = Field(85, json_schema_extra={"env_names": ["HIGH_SEVERITY_THRESHOLD"]})

    # Action Execution
    ENABLE_EMAIL_ALERTS: bool = Field(False, json_schema_extra={"env_names": ["ENABLE_EMAIL_ALERTS"]})
    ENABLE_SMS_ALERTS: bool = Field(False, json_schema_extra={"env_names": ["ENABLE_SMS_ALERTS"]})
    ENABLE_IOT_ACTIONS: bool = Field(False, json_schema_extra={"env_names": ["ENABLE_IOT_ACTIONS"]})

    # Email Configuration (Optional)
    SMTP_HOST: Optional[str] = Field(None, json_schema_extra={"env_names": ["SMTP_HOST"]})
    SMTP_PORT: Optional[int] = Field(None, json_schema_extra={"env_names": ["SMTP_PORT"]})
    SMTP_USER: Optional[str] = Field(None, json_schema_extra={"env_names": ["SMTP_USER"]})
    SMTP_PASSWORD: Optional[str] = Field(None, json_schema_extra={"env_names": ["SMTP_PASSWORD"]})
    ALERT_EMAIL: Optional[str] = Field(None, json_schema_extra={"env_names": ["ALERT_EMAIL"]})

    # Twilio Configuration (Optional)
    TWILIO_ACCOUNT_SID: Optional[str] = Field(None, json_schema_extra={"env_names": ["TWILIO_ACCOUNT_SID"]})
    TWILIO_AUTH_TOKEN: Optional[str] = Field(None, json_schema_extra={"env_names": ["TWILIO_AUTH_TOKEN"]})
    TWILIO_PHONE: Optional[str] = Field(None, json_schema_extra={"env_names": ["TWILIO_PHONE"]})
    ALERT_PHONE: Optional[str] = Field(None, json_schema_extra={"env_names": ["ALERT_PHONE"]})

    # CORS Configuration
    CORS_ORIGINS: list = Field(
        ["http://localhost:3000", "http://localhost:5173"],
        json_schema_extra={"env_names": ["CORS_ORIGINS"]}
    )

    # Logging
    LOG_LEVEL: str = Field("INFO", json_schema_extra={"env_names": ["LOG_LEVEL"]})
    LOG_FILE: Optional[Path] = Field(None, json_schema_extra={"env_names": ["LOG_FILE"]})

    # Performance
    MAX_CONCURRENT_ANALYSES: int = Field(3, json_schema_extra={"env_names": ["MAX_CONCURRENT_ANALYSES"]})
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(30, json_schema_extra={"env_names": ["WEBSOCKET_HEARTBEAT_INTERVAL"]})

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.EVIDENCE_DIR.mkdir(exist_ok=True, parents=True)
        if self.LOG_FILE:
            self.LOG_FILE.parent.mkdir(exist_ok=True, parents=True)


# Singleton instance
settings = Settings()


# ====================================================================
# System Prompts
# ====================================================================

VISION_AGENT_PROMPT = """You are AegisAI, an elite autonomous security agent.
Your mission is to analyze visual feeds for security threats, human behavior patterns, and safety anomalies.

Analyze the image provided and return STRICT JSON object.
Do not use Markdown formatting. Return ONLY raw JSON.

Structure:
{
  "incident": boolean,
  "type": "theft|intrusion|violence|stalking|loitering|vandalism|suspicious_behavior|normal",
  "severity": "low|medium|high|critical",
  "confidence": 0-100,
  "reasoning": "Brief tactical explanation based on body language, objects, context",
  "subjects": ["description of people/objects"],
  "recommended_actions": ["action1", "action2", "action3"]
}

Detection Rules:
- Normal behavior (working, sitting, walking) -> incident: false
- Weapons, aggressive posture, sneaking, masked faces -> incident: true
- Simulated threats or "gun" gestures -> incident: true (training drill)
- Loitering >5min without authorization -> incident: true
- Property damage, theft behaviors -> incident: true

Be analytical and precise. Consider temporal context when available."""

PLANNER_AGENT_PROMPT = """You are a security response planner. Create executable action plans.

INCIDENT DETAILS:
- Type: {incident_type}
- Severity: {severity}
- Reasoning: {reasoning}
- Confidence: {confidence}%

CREATE structured response plan with specific actions.

RESPOND with ONLY valid JSON array:
[
  {{
    "step": 1,
    "action": "save_evidence|send_alert|log_incident|lock_door|sound_alarm|contact_authorities",
    "priority": "immediate|high|medium|low",
    "parameters": {{}} ,
    "reasoning": "why this action is needed"
  }}
]

PRIORITIZATION:
1. Evidence preservation (immediate)
2. Alert relevant parties (high)
3. Prevent escalation (high)
4. Document thoroughly (medium)

Be specific and actionable. Focus on automated responses."""
