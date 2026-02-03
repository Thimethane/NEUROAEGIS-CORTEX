function Create-File {
    param (
        [string]$Path,
        [string]$Content
    )

    $dir = Split-Path $Path
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    Set-Content -Path $Path -Value $Content
    Write-Host "✏️  Written: $Path"
}

# backend/__init__.py
Create-File "backend/__init__.py" @'
"""AegisAI Backend - Autonomous Security & Incident Response Agent"""

__version__ = "2.5.0"
__author__ = "AegisAI Team"
'@

# backend/agents/__init__.py
Create-File "backend/agents/__init__.py" @'
"""AI Agents for security analysis and planning"""

from .base_agent import BaseAgent
from .vision_agent import VisionAgent
from .planner_agent import PlannerAgent

__all__ = ["BaseAgent", "VisionAgent", "PlannerAgent"]
'@

# backend/services/__init__.py
Create-File "backend/services/__init__.py" @'
"""Business logic services"""

from .database_service import DatabaseService, db_service
from .action_executor import ActionExecutor, action_executor

__all__ = [
    "DatabaseService",
    "db_service",
    "ActionExecutor", 
    "action_executor"
]
'@

# backend/config/__init__.py
Create-File "backend/config/__init__.py" @'
"""Configuration management"""

from .settings import settings, VISION_AGENT_PROMPT, PLANNER_AGENT_PROMPT

__all__ = ["settings", "VISION_AGENT_PROMPT", "PLANNER_AGENT_PROMPT"]
'@

# backend/api/__init__.py
Create-File "backend/api/__init__.py" @'
"""API routes and WebSocket handlers"""

from .routes import router

__all__ = ["router"]
'@

# backend/utils/__init__.py
Create-File "backend/utils/__init__.py" @'
"""Utility functions and helpers"""

from .logger import setup_logging

__all__ = ["setup_logging"]
'@

Write-Host "`n🎉 Backend package files overwritten successfully."
