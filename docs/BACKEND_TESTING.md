# 🧪 Backend Testing Guide

Complete testing guide for AegisAI backend services.

---

## 📋 **Prerequisites**

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx
```

---

## 🚀 **Quick Start**

### Run All Tests and make sure that .env is inside the backend folder.

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_agents.py -v
pytest tests/test_services.py -v
pytest tests/test_api.py -v
```

### Run by Marker

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# API tests
pytest -m api
```

---

## 📁 **Test Structure**

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_agents.py          # AI agent tests
│   ├── test_services.py        # Service layer tests
│   ├── test_api.py             # API endpoint tests
│   └── conftest.py             # Shared fixtures (optional)
├── pytest.ini                  # Pytest configuration
└── .coveragerc                 # Coverage configuration
```

---

## 🧪 **Test Categories**

### 1. Agent Tests (`test_agents.py`)

**Coverage**: 
- VisionAgent initialization
- Frame analysis (numpy & base64)
- Result validation
- Temporal context building
- History management
- Stats tracking
- PlannerAgent plan generation
- Plan validation
- Fallback plans

**Run**:
```bash
pytest tests/test_agents.py -v
```

**Expected Output**:
```
tests/test_agents.py::TestVisionAgent::test_agent_initialization PASSED
tests/test_agents.py::TestVisionAgent::test_analyze_frame_with_numpy PASSED
tests/test_agents.py::TestVisionAgent::test_validate_result PASSED
...
==================== 15 passed in 12.34s ====================
```

---

### 2. Service Tests (`test_services.py`)

**Coverage**:
- Database initialization & schema
- Incident CRUD operations
- Action logging
- Statistics retrieval
- Status updates
- Cleanup operations
- ActionExecutor plan execution
- Individual action handlers

**Run**:
```bash
pytest tests/test_services.py -v
```

**Expected Output**:
```
tests/test_services.py::TestDatabaseService::test_save_incident PASSED
tests/test_services.py::TestDatabaseService::test_get_statistics PASSED
...
==================== 12 passed in 5.67s ====================
```

---

### 3. API Tests (`test_api.py`)

**Coverage**:
- Root & health endpoints
- Incident CRUD via API
- Query parameters & filtering
- Error handling (404, 422, 405)
- CORS headers
- End-to-end workflows

**Run**:
```bash
pytest tests/test_api.py -v
```

**Expected Output**:
```
tests/test_api.py::TestRootEndpoints::test_root PASSED
tests/test_api.py::TestIncidentEndpoints::test_get_incidents PASSED
...
==================== 18 passed in 8.91s ====================
```

---

## 🎯 **Manual Backend Tests**

### Test 1: Server Startup

**Steps**:
```bash
cd backend
source venv/bin/activate
python main.py
```

**Expected Output**:
```
INFO: ✅ AegisAI Backend Ready
INFO: 📡 API: http://0.0.0.0:8000
INFO: 📖 Docs: http://0.0.0.0:8000/docs
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Verification**:
```bash
curl http://localhost:8000/
# Should return: {"name":"AegisAI","version":"2.5.0",...}
```

✅ **Pass**: Server starts without errors

---

### Test 2: Health Check

```bash
curl http://localhost:8000/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "components": {
    "database": "ok",
    "vision_agent": "ok",
    "planner_agent": "ok"
  },
  "timestamp": "2024-XX-XXTXX:XX:XX"
}
```

✅ **Pass**: All components healthy

---

### Test 3: API Documentation

**Visit**: http://localhost:8000/docs

**Expected**:
- Swagger UI loads
- All endpoints listed:
  - GET `/`
  - GET `/health`
  - GET `/api/incidents`
  - GET `/api/incidents/{id}`
  - POST `/api/incidents/{id}/status`
  - GET `/api/stats`
  - GET `/api/agents/stats`
  - DELETE `/api/incidents/cleanup`

✅ **Pass**: Docs accessible and complete

---

### Test 4: Create Incident via Database

```bash
# Start Python shell
python

>>> from services.database_service import db_service
>>> from datetime import datetime
>>> 
>>> incident_id = db_service.save_incident({
...     'timestamp': datetime.now().isoformat(),
...     'type': 'test',
...     'severity': 'medium',
...     'confidence': 80,
...     'reasoning': 'Manual test',
...     'subjects': [],
...     'evidence_path': '',
...     'response_plan': []
... })
>>> 
>>> print(f"Created incident ID: {incident_id}")
>>> exit()
```

**Verify via API**:
```bash
curl http://localhost:8000/api/incidents
```

✅ **Pass**: Incident appears in response

---

### Test 5: Video Processor Demo

```bash
cd backend
source venv/bin/activate
python -m services.video_processor demo
```

**Expected Output**:
```
🎬 Starting AegisAI Demo Scenario

=== SCENARIO: Normal Activity ===
✓ No incident detected - Normal operation

=== SCENARIO: Suspicious Behavior ===
✓ Detected: suspicious_behavior
  Severity: medium
  Confidence: 82%

=== SCENARIO: Critical Threat ===
✓ Detected: violence
  Severity: high
  Response plan executed: 5 actions

✓ Demo sequence completed
```

✅ **Pass**: All scenarios execute successfully

---

### Test 6: Agent Performance Test

```bash
cd backend
python

>>> from agents.vision_agent import VisionAgent
>>> import numpy as np
>>> import asyncio
>>> 
>>> agent = VisionAgent()
>>> frame = np.zeros((480, 640, 3), dtype=np.uint8)
>>> 
>>> # Test multiple analyses
>>> async def test_performance():
...     for i in range(10):
...         result = await agent.process(frame=frame, frame_number=i)
...         print(f"Frame {i}: {result['type']}")
...     stats = agent.get_stats()
...     print(f"\nStats: {stats}")
>>> 
>>> asyncio.run(test_performance())
```

**Expected**:
- All 10 frames analyzed
- Stats show:
  - `total_calls`: 10
  - `total_errors`: 0
  - `avg_response_time`: < 3.0 seconds

✅ **Pass**: Consistent performance

---

### Test 7: Database Persistence

```bash
# Create incident
python

>>> from services.database_service import db_service
>>> incident_id = db_service.save_incident({
...     'timestamp': '2024-01-01T12:00:00',
...     'type': 'persistence_test',
...     'severity': 'low',
...     'confidence': 75,
...     'reasoning': 'Test persistence',
...     'subjects': [],
...     'evidence_path': '',
...     'response_plan': []
... })
>>> exit()

# Restart server
# (Press Ctrl+C, then `python main.py`)

# Verify incident still exists
curl http://localhost:8000/api/incidents
```

✅ **Pass**: Incident persists across restarts

---

## 📊 **Performance Benchmarks**

### Expected Performance:

| Metric | Target | Acceptable |
|--------|--------|------------|
| API Response Time | < 100ms | < 500ms |
| Frame Analysis | < 2s | < 5s |
| Database Query | < 50ms | < 200ms |
| Memory Usage | < 300MB | < 500MB |
| CPU Usage | < 20% | < 40% |

### Measure Performance:

```bash
# API response time
time curl http://localhost:8000/api/incidents

# Memory usage
ps aux | grep python
# Look at RSS (Resident Set Size)

# Load test with Apache Bench
ab -n 100 -c 10 http://localhost:8000/api/stats
```

---

## 🐛 **Common Issues**

### Issue 1: "No module named 'agents'"

**Solution**:
```bash
# Make sure you're running from backend/ directory
cd backend
python -m pytest tests/
```

### Issue 2: "Database locked"

**Solution**:
```bash
# Stop any running instances
pkill -f "python main.py"
# Delete test database
rm test_*.db
```

### Issue 3: Import errors

**Solution**:
```bash
# Ensure __init__.py files exist
ls backend/__init__.py
ls backend/agents/__init__.py
ls backend/services/__init__.py
```

### Issue 4: Gemini API failures

**Solution**:
```bash
# Check API key is set
echo $GEMINI_API_KEY

# Test connection manually
python
>>> from agents.vision_agent import VisionAgent
>>> agent = VisionAgent()
>>> # If no errors, API key is valid
```

---

## ✅ **Test Checklist**

Before deployment, verify:

- [ ] ✅ All unit tests pass (`pytest tests/test_agents.py`)
- [ ] ✅ All service tests pass (`pytest tests/test_services.py`)
- [ ] ✅ All API tests pass (`pytest tests/test_api.py`)
- [ ] ✅ Server starts without errors
- [ ] ✅ Health check returns "healthy"
- [ ] ✅ API docs accessible
- [ ] ✅ Database operations work
- [ ] ✅ Video processor demo runs
- [ ] ✅ Agent performance acceptable
- [ ] ✅ No memory leaks (run for 10 min)
- [ ] ✅ Code coverage > 70%

---

## 📈 **Coverage Report**

After running tests with coverage:

```bash
pytest --cov --cov-report=html
```

Open `htmlcov/index.html` in browser.

**Target Coverage**:
- Overall: > 70%
- Agents: > 80%
- Services: > 75%
- API: > 80%

---

## 🚀 **CI/CD Integration**

For automated testing:

```yaml
# .github/workflows/backend-tests.yml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📝 **Test Report Template**

```markdown
# Backend Test Report

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Environment**: [Local/Docker/CI]

## Unit Tests
- Agents: X/15 passed
- Services: X/12 passed
- API: X/18 passed

## Integration Tests
- E2E Flow: ✅/❌
- Database: ✅/❌
- Video Processor: ✅/❌

## Performance
- API Response: XXX ms
- Frame Analysis: X.X s
- Memory: XXX MB
- CPU: XX%

## Coverage
- Overall: XX%
- Agents: XX%
- Services: XX%
- API: XX%

## Issues
1. [Description]

## Recommendation
[ ] Ready for deployment
[ ] Needs fixes
```

---

**Happy Testing!** 🧪
