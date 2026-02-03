#!/usr/bin/env bash
set -e

ROOT="aegisai"

safe_touch() {
  for file in "$@"; do
    mkdir -p "$(dirname "$file")"
    if [ -f "$file" ]; then
      echo "⏭ Skipped: $file"
    else
      touch "$file"
      echo "✅ Created: $file"
    fi
  done
}

# Root
mkdir -p "$ROOT"

# ---------------- Backend ----------------
mkdir -p \
"$ROOT/backend/agents" \
"$ROOT/backend/services" \
"$ROOT/backend/config" \
"$ROOT/backend/api" \
"$ROOT/backend/utils"

safe_touch \
"$ROOT/backend/agents/__init__.py" \
"$ROOT/backend/agents/base_agent.py" \
"$ROOT/backend/agents/vision_agent.py" \
"$ROOT/backend/agents/planner_agent.py" \
"$ROOT/backend/services/__init__.py" \
"$ROOT/backend/services/database_service.py" \
"$ROOT/backend/services/action_executor.py" \
"$ROOT/backend/config/__init__.py" \
"$ROOT/backend/config/settings.py" \
"$ROOT/backend/api/__init__.py" \
"$ROOT/backend/api/routes.py" \
"$ROOT/backend/utils/__init__.py" \
"$ROOT/backend/utils/logger.py" \
"$ROOT/backend/main.py" \
"$ROOT/backend/requirements.txt" \
"$ROOT/backend/Dockerfile"

# ---------------- Frontend ----------------
mkdir -p \
"$ROOT/frontend/src/components/Dashboard" \
"$ROOT/frontend/src/hooks" \
"$ROOT/frontend/src/services" \
"$ROOT/frontend/src/types"

safe_touch \
"$ROOT/frontend/src/components/VideoFeed.tsx" \
"$ROOT/frontend/src/components/Dashboard.tsx" \
"$ROOT/frontend/src/components/Dashboard/StatsCards.tsx" \
"$ROOT/frontend/src/hooks/useMonitoring.ts" \
"$ROOT/frontend/src/hooks/useCamera.ts" \
"$ROOT/frontend/src/services/geminiService.ts" \
"$ROOT/frontend/src/types/index.ts" \
"$ROOT/frontend/src/App.tsx" \
"$ROOT/frontend/src/index.tsx" \
"$ROOT/frontend/package.json" \
"$ROOT/frontend/vite.config.ts" \
"$ROOT/frontend/tsconfig.json" \
"$ROOT/frontend/Dockerfile"

# ---------------- Root Files ----------------
safe_touch \
"$ROOT/docker-compose.yml" \
"$ROOT/.env.example" \
"$ROOT/.gitignore" \
"$ROOT/README-REFACTORED.md" \
"$ROOT/QUICKSTART.md" \
"$ROOT/DEPLOYMENT.md"

echo "🎉 Refactored structure initialized safely."
