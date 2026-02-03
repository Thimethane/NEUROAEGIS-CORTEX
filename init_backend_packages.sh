#!/usr/bin/env bash
set -e

create_file() {
  FILE=$1
  CONTENT=$2

  mkdir -p "$(dirname "$FILE")"

  if [ -f "$FILE" ]; then
    echo "⏭ Skipped (exists): $FILE"
  else
    cat > "$FILE" <<EOF
$CONTENT
EOF
    echo "✅ Created: $FILE"
  fi
}

# backend/__init__.py
create_file "backend/__init__.py" \
'"""AegisAI Backend - Autonomous Security & Incident Response Agent"""

__version__ = "2.5.0"
__author__ = "AegisAI Team"'

# backend/agents/__init__.py
create_file "backend/agents/__init__.py" \
'"""AI Agents for security analysis and planning"""

from .base_agent import BaseAgent
from .vision_agent import VisionAgent
from .planner_agent import PlannerAgent

__all__ = ["BaseAgent", "VisionAgent", "PlannerAgent"]'

# backend/services/__init__.py
create_file "backend/services/__init__.py" \
'"""Business logic services"""

from .database_service import DatabaseService, db_service
from .action_executor import ActionExecutor, action_executor

__all__ = [
    "DatabaseService",
    "db_service",
    "ActionExecutor", 
    "action_executor"
]'

# backend/config/__init__.py
create_file "backend/config/__init__.py" \
'"""Configuration management"""

from .settings import settings, VISION_AGENT_PROMPT, PLANNER_AGENT_PROMPT

__all__ = ["settings", "VISION_AGENT_PROMPT", "PLANNER_AGENT_PROMPT"]'

# backend/api/__init__.py
create_file "backend/api/__init__.py" \
'"""API routes and WebSocket handlers"""

from .routes import router

__all__ = ["router"]'

# backend/utils/__init__.py
create_file "backend/utils/__init__.py" \
'"""Utility functions and helpers"""

from .logger import setup_logging

__all__ = ["setup_logging"]'

echo "🎉 Backend package files created safely."
