# ✅ COMPLETE VERIFICATION & TESTING GUIDE

## System Verification and Testing Instructions for NeuroAegis Cortex

---

## 📋 PRE-FLIGHT CHECKLIST

### Before You Begin

Ensure you have all the files from `/mnt/user-data/outputs/` in your project:

```bash
# Check critical files exist
ls -la backend/agents/vision_agent.py
ls -la backend/agents/planner_agent.py
ls -la backend/agents/base_agent.py
ls -la backend/services/action_executor.py
ls -la backend/services/database_service.py
ls -la backend/video_processor.py
ls -la backend/api/routes.py
ls -la frontend/src/App.tsx
ls -la frontend/src/components/Dashboard.tsx
ls -la docker-compose.yml
```

**Expected Output:** All files should exist (no "No such file" errors)

---

## 🔧 STEP 1: ENVIRONMENT CONFIGURATION

### 1.1 Backend Configuration

```bash
# Navigate to backend directory
cd backend

# Check if .env file exists
ls -la .env

# If not exists, create from example
cp .env.example .env
```

### 1.2 Verify Critical Environment Variables

```bash
# Edit .env file
nano .env  # or vim .env, or use any text editor
```

**Required Variables:**
```bash
# ========================================
# CRITICAL - MUST BE SET
# ========================================
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Model Configuration (DO NOT change - use Gemini 3!)
GEMINI_MODEL=gemini-3-pro-preview

# Processing Configuration
FRAME_SAMPLE_RATE=4
CONFIDENCE_THRESHOLD=70

# ========================================
# OPTIONAL - IoT Integration
# ========================================
ENABLE_IOT_ACTIONS=false
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# ========================================
# OPTIONAL - Alert Services
# ========================================
ENABLE_EMAIL_ALERTS=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

ENABLE_SMS_ALERTS=false
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE=
ALERT_PHONE=
```

### 1.3 Get Gemini API Key

If you don't have a Gemini API key:

```bash
# Visit: https://aistudio.google.com/apikey
# Click "Create API key"
# Copy the key
# Paste into .env file: GEMINI_API_KEY=your_key_here
```

**Verify API Key Format:**
```bash
# Should look like: AIzaSyC...
# Should be 39 characters
echo $GEMINI_API_KEY | wc -c
# Expected output: 39 (or 40 with newline)
```

---

## 🐳 STEP 2: DOCKER ENVIRONMENT

### 2.1 Verify Docker Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10+ or higher

# Check Docker Compose version
docker-compose --version
# Expected: docker-compose version 1.29+ or higher

# Check Docker daemon is running
docker ps
# Expected: Should list containers or show empty table (not error)
```

### 2.2 Clean Previous Containers (if any)

```bash
# Stop all running containers
docker-compose down

# Remove old containers, volumes, and images
docker-compose down -v
docker system prune -f

# Verify clean state
docker ps -a
# Expected: No aegisai containers listed
```

---

## 🚀 STEP 3: BUILD AND START SYSTEM

### 3.1 Build Docker Images

```bash
# From project root directory
docker-compose build --no-cache

# Expected output:
# [+] Building ...
# => [backend ...] 
# => [frontend ...]
# Successfully built ...
```

**If build fails:**
```bash
# Check for common issues:
# 1. Internet connection
curl -I https://www.google.com

# 2. Docker disk space
docker system df

# 3. View detailed build logs
docker-compose build --no-cache --progress=plain
```

### 3.2 Start All Services

```bash
# Start in detached mode
docker-compose up -d

# Expected output:
# [+] Running 3/3
#  ✔ Network aegisai_default      Created
#  ✔ Container aegisai-backend    Started
#  ✔ Container aegisai-frontend   Started
```

### 3.3 Verify Containers Are Running

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# aegisai-backend     Up X seconds        0.0.0.0:8000->8000/tcp
# aegisai-frontend    Up X seconds        0.0.0.0:3000->3000/tcp
```

**All containers should show STATUS: "Up"**

### 3.4 Monitor Container Logs

```bash
# View backend logs
docker-compose logs -f backend

# Expected output (within 30 seconds):
# ✅ Initialized GenAI client for gemini-3-pro-preview
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000

# View frontend logs (in new terminal)
docker-compose logs -f frontend

# Expected output:
# VITE v5.x.x ready in XXX ms
# ➜ Local:   http://localhost:3000/
# ➜ Network: use --host to expose
```

**Press Ctrl+C to exit logs (containers keep running)**

---

## 🧪 STEP 4: BACKEND VERIFICATION

### 4.1 Health Check Endpoint

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected output (should be valid JSON):
{
  "status": "healthy",
  "timestamp": "2026-02-03T...",
  "version": "1.0.0",
  "gemini_model": "gemini-3-pro-preview",
  "components": {
    "database": "healthy",
    "gemini_api": "configured",
    "action_executor": "healthy",
    "evidence_storage": "healthy"
  }
}
```

**If you get connection refused:**
```bash
# Check if backend is actually running
docker ps | grep backend

# Check backend logs for errors
docker-compose logs backend | tail -50

# Restart backend if needed
docker-compose restart backend
```

### 4.2 API Documentation (Swagger UI)

```bash
# Open in browser:
open http://localhost:8000/docs
# (On Linux: xdg-open http://localhost:8000/docs)

# You should see:
# - "NeuroAegis Cortex API" title
# - Multiple endpoints listed
# - Interactive API documentation
```

### 4.3 Test Gemini Integration

```bash
# Create a simple test image (base64)
TEST_IMAGE="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="

# Test analyze endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"image\":\"$TEST_IMAGE\"}" | jq

# Expected output (valid JSON with all required fields):
{
  "incident": false,
  "type": "normal",
  "severity": "low",
  "confidence": 5,
  "reasoning": "...",
  "subjects": [],
  "recommended_actions": []
}
```

**If you get 500 error:**
```bash
# Check Gemini API key is set correctly
docker-compose exec backend env | grep GEMINI_API_KEY

# Check backend logs for specific error
docker-compose logs backend | grep -A 10 "ERROR"

# Common issues:
# - Invalid API key: Check .env file
# - API quota exceeded: Wait or upgrade quota
# - Network issue: Check internet connection
```

### 4.4 Database Verification

```bash
# Check if database file exists
docker-compose exec backend ls -la /app/aegis.db

# Expected output:
# -rw-r--r-- ... aegis.db

# Check database tables
docker-compose exec backend sqlite3 /app/aegis.db ".tables"

# Expected output:
# incidents    evidence_metadata    actions
```

### 4.5 Evidence Directory

```bash
# Check evidence directory exists
docker-compose exec backend ls -la /app/evidence/

# Expected output:
# drwxr-xr-x ... evidence/

# Should be empty initially (no files)
```

---

## 🎨 STEP 5: FRONTEND VERIFICATION

### 5.1 Access Frontend

```bash
# Open in browser:
open http://localhost:3000

# You should see:
# - NeuroAegis Cortex title
# - Gemini 3 Pro Preview badge
# - Dashboard with Video Feed section
# - "ACTIVATE" button
# - Settings panel
```

### 5.2 Browser Console Check

```bash
# Open browser developer tools:
# Chrome: F12 or Cmd+Opt+I (Mac)
# Firefox: F12 or Cmd+Opt+I (Mac)

# Go to Console tab
# You should see:
# - No red errors
# - Possibly some info logs
# - No CORS errors
# - No 404 errors
```

**If you see CORS errors:**
```bash
# This should NOT happen with Vite proxy
# Check frontend/vite.config.ts has:
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}

# Restart frontend
docker-compose restart frontend
```

### 5.3 Test Frontend-Backend Connection

```bash
# In browser console (F12 → Console tab), paste:
fetch('/api/health')
  .then(r => r.json())
  .then(console.log)

# Expected output:
# {status: "healthy", timestamp: "...", ...}
```

---

## 📹 STEP 6: VIDEO PROCESSING TEST

### 6.1 Webcam Access (Optional)

```bash
# Check if webcam is available
ls /dev/video0

# Expected output:
# /dev/video0

# If not available:
# - You can use demo mode instead
# - Or upload test images via API
```

### 6.2 Demo Mode Test

```bash
# Run video processor in demo mode
docker-compose exec backend python video_processor.py demo

# Expected output:
# ========================================
# 🎬 DEMO MODE - 4 Test Scenarios
# ========================================
# 
# Scenario 1: Normal Activity
# Analyzing demo frame 1/4...
# ✅ Analysis complete: normal (confidence: 5%)
# 
# Scenario 2: Suspicious Behavior
# Analyzing demo frame 2/4...
# ✅ Analysis complete: suspicious_behavior (confidence: 75%)
# 
# Scenario 3: Security Breach
# Analyzing demo frame 3/4...
# ✅ Analysis complete: intrusion (confidence: 88%)
# 
# Scenario 4: Critical Threat
# Analyzing demo frame 4/4...
# ✅ Analysis complete: violence (confidence: 95%)
```

**If demo mode fails:**
```bash
# Check Gemini API is working
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."}' \
  | jq '.incident'

# Check backend logs
docker-compose logs backend | tail -100
```

### 6.3 Live Processing Test

```bash
# In frontend browser:
# 1. Click "ACTIVATE" button
# 2. Grant camera permission if prompted
# 3. Wait 4 seconds
# 4. Check Analysis panel updates

# You should see:
# - Video feed showing camera
# - Analysis panel with Gemini 3 results
# - Confidence score
# - Reasoning text
# - Incident type
```

---

## 🧪 STEP 7: UNIT TESTS

### 7.1 Run Backend Tests

```bash
# Install pytest in backend container
docker-compose exec backend pip install pytest pytest-asyncio

# Copy test file
docker cp test_agents.py aegisai-backend:/app/tests/

# Run tests
docker-compose exec backend pytest tests/test_agents.py -v

# Expected output:
# ======================== test session starts =========================
# tests/test_agents.py::TestBaseAgent::test_initialization PASSED
# tests/test_agents.py::TestBaseAgent::test_get_stats PASSED
# tests/test_agents.py::TestBaseAgent::test_json_parsing_clean PASSED
# ...
# ======================== X passed in X.XXs ==========================
```

**Expected Results:**
- 20+ tests should PASS
- 0 tests should FAIL
- Some tests may SKIP (if dependencies missing)

### 7.2 Test Individual Components

```bash
# Test Vision Agent
docker-compose exec backend python -c "
from agents.vision_agent import VisionAgent
agent = VisionAgent()
print('✅ Vision Agent initialized')
print(f'Model: {agent.model_name}')
print(f'Stats: {agent.get_stats()}')
"

# Expected output:
# ✅ Vision Agent initialized
# Model: gemini-3-pro-preview
# Stats: {'agent': 'VisionAgent', 'model': '...', ...}
```

```bash
# Test Planner Agent
docker-compose exec backend python -c "
from agents.planner_agent import PlannerAgent
agent = PlannerAgent()
print('✅ Planner Agent initialized')
print(f'Valid Actions: {len(agent.VALID_ACTIONS)}')
"

# Expected output:
# ✅ Planner Agent initialized
# Valid Actions: 11
```

```bash
# Test Action Executor
docker-compose exec backend python -c "
from services.action_executor import action_executor
print('✅ Action Executor initialized')
stats = action_executor.get_execution_stats()
print(f'Stats: {stats}')
"

# Expected output:
# ✅ Action Executor initialized
# Stats: {'total_actions': 0, 'successful': 0, ...}
```

---

## 📊 STEP 8: PERFORMANCE TESTING

### 8.1 Measure Processing Time

```bash
# Run performance test script
docker-compose exec backend python << 'EOF'
import asyncio
import time
from agents.vision_agent import VisionAgent

async def test_performance():
    agent = VisionAgent()
    
    # Test image (1x1 pixel JPEG)
    test_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
    
    times = []
    for i in range(5):
        start = time.time()
        result = await agent._safe_process(test_image, i)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Test {i+1}: {elapsed:.2f}s - Incident: {result.get('incident', False)}")
    
    avg = sum(times) / len(times)
    print(f"\nAverage: {avg:.2f}s")
    print(f"Min: {min(times):.2f}s")
    print(f"Max: {max(times):.2f}s")
    
    await agent.close()

asyncio.run(test_performance())
EOF

# Expected output:
# Test 1: 4.52s - Incident: False
# Test 2: 3.21s - Incident: False
# Test 3: 5.67s - Incident: False
# Test 4: 4.03s - Incident: False
# Test 5: 3.89s - Incident: False
#
# Average: 4.26s
# Min: 3.21s
# Max: 5.67s
```

### 8.2 Check System Resources

```bash
# Monitor Docker resource usage
docker stats --no-stream

# Expected output:
# CONTAINER        CPU %    MEM USAGE / LIMIT     MEM %
# aegisai-backend  10-30%   500MB / 4GB          12-15%
# aegisai-frontend <5%      200MB / 4GB          5%
```

---

## 🔍 STEP 9: END-TO-END INTEGRATION TEST

### 9.1 Complete Workflow Test

```bash
# Create test script
cat > /tmp/test_workflow.sh << 'EOF'
#!/bin/bash
set -e

echo "========================================="
echo "🧪 END-TO-END INTEGRATION TEST"
echo "========================================="
echo ""

# Test 1: Health Check
echo "1️⃣ Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8000/api/health)
echo "$HEALTH" | jq -r '.status' | grep -q "healthy" && echo "✅ Health check passed" || exit 1

# Test 2: Frame Analysis
echo ""
echo "2️⃣ Testing frame analysis..."
ANALYSIS=$(curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="}')

# Check all required fields exist
echo "$ANALYSIS" | jq -e '.incident' > /dev/null && echo "✅ Field 'incident' present" || exit 1
echo "$ANALYSIS" | jq -e '.type' > /dev/null && echo "✅ Field 'type' present" || exit 1
echo "$ANALYSIS" | jq -e '.severity' > /dev/null && echo "✅ Field 'severity' present" || exit 1
echo "$ANALYSIS" | jq -e '.confidence' > /dev/null && echo "✅ Field 'confidence' present" || exit 1
echo "$ANALYSIS" | jq -e '.reasoning' > /dev/null && echo "✅ Field 'reasoning' present" || exit 1
echo "$ANALYSIS" | jq -e '.subjects' > /dev/null && echo "✅ Field 'subjects' present" || exit 1
echo "$ANALYSIS" | jq -e '.recommended_actions' > /dev/null && echo "✅ Field 'recommended_actions' present" || exit 1

# Test 3: Statistics
echo ""
echo "3️⃣ Testing statistics endpoint..."
STATS=$(curl -s http://localhost:8000/api/stats)
echo "$STATS" | jq -e '.total_incidents' > /dev/null && echo "✅ Statistics endpoint working" || exit 1

# Test 4: Performance Metrics
echo ""
echo "4️⃣ Testing performance endpoint..."
PERF=$(curl -s http://localhost:8000/api/performance)
echo "$PERF" | jq -e '.vision_agent' > /dev/null && echo "✅ Performance metrics available" || exit 1

echo ""
echo "========================================="
echo "✅ ALL TESTS PASSED!"
echo "========================================="
EOF

chmod +x /tmp/test_workflow.sh
/tmp/test_workflow.sh
```

**Expected output:**
```
=========================================
🧪 END-TO-END INTEGRATION TEST
=========================================

1️⃣ Testing health endpoint...
✅ Health check passed

2️⃣ Testing frame analysis...
✅ Field 'incident' present
✅ Field 'type' present
✅ Field 'severity' present
✅ Field 'confidence' present
✅ Field 'reasoning' present
✅ Field 'subjects' present
✅ Field 'recommended_actions' present

3️⃣ Testing statistics endpoint...
✅ Statistics endpoint working

4️⃣ Testing performance endpoint...
✅ Performance metrics available

=========================================
✅ ALL TESTS PASSED!
=========================================
```

---

## 🎯 STEP 10: PRODUCTION READINESS CHECKS

### 10.1 Security Checklist

```bash
# ✅ Check API key is not hardcoded
grep -r "AIza" backend/*.py
# Expected: No matches (key should only be in .env)

# ✅ Check .env is in .gitignore
grep ".env" .gitignore
# Expected: .env should be listed

# ✅ Check no secrets in git history
git log --all --full-history --source --pretty=format:"%H %s" -- "*.env"
# Expected: No commits with .env files
```

### 10.2 Performance Checklist

```bash
# ✅ Verify Gemini 3 model is set
docker-compose exec backend env | grep GEMINI_MODEL
# Expected: GEMINI_MODEL=gemini-3-pro-preview

# ✅ Check confidence threshold
docker-compose exec backend env | grep CONFIDENCE_THRESHOLD
# Expected: CONFIDENCE_THRESHOLD=70

# ✅ Check frame sample rate
docker-compose exec backend env | grep FRAME_SAMPLE_RATE
# Expected: FRAME_SAMPLE_RATE=4
---

## 🐛 TROUBLESHOOTING GUIDE

### Issue: "Cannot connect to Docker daemon"

```bash
# Start Docker daemon
sudo systemctl start docker  # Linux
# or
open -a Docker  # macOS

# Verify
docker ps
```

### Issue: "Port 8000 already in use"

```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Issue: "Gemini API Error 429 (Quota Exceeded)"

```bash
# Solution 1: Wait for quota reset (usually 1 minute)
sleep 60

# Solution 2: Check quota limits
# Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

# Solution 3: Increase frame sample rate to reduce calls
# Edit .env:
FRAME_SAMPLE_RATE=6  # Analyze every 6 seconds instead of 4
```

### Issue: "Frontend shows blank page"

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend

# Clear browser cache
# Chrome: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

### Issue: "Analysis returns error result"

```bash
# Check backend logs for specific error
docker-compose logs backend | grep -A 20 "ERROR"

# Test Gemini API directly
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."}' \
  | jq

# If reasoning contains "API", check:
# 1. API key is valid
# 2. Internet connection works
# 3. Quota is not exceeded
```