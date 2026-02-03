# 🧪 AegisAI Testing Guide

Complete testing instructions to verify all features work before deployment.

---

## 📋 **Pre-Deployment Checklist**

### ✅ Phase 1: Environment Setup

```bash
# 1. Verify all files exist
Test-Path frontend/src/constants.ts
Test-Path frontend/src/types/index.ts
Test-Path frontend/src/components/VideoFeed.tsx
Test-Path frontend/src/components/Dashboard/Dashboard.tsx
Test-Path frontend/src/hooks/useMonitoring.ts
Test-Path frontend/src/hooks/useCamera.ts
Test-Path frontend/src/services/geminiService.ts

# 2. Verify environment variables
cat frontend/.env.local
# Should show VITE_GEMINI_API_KEY=your_key

# 3. Install dependencies
cd frontend
npm install

# 4. Check for TypeScript errors
npm run type-check  # or: npx tsc --noEmit
```

**Expected Result**: All files exist, no TypeScript errors.

---

## 🎯 **Phase 2: Frontend Testing**

### Test 1: Build Test

```bash
cd frontend
npm run build
```

**Expected Output**:
```
✓ 50 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.30 kB
dist/assets/index-XXXXXXXX.css    5.21 kB │ gzip:  1.89 kB
dist/assets/index-XXXXXXXX.js   245.67 kB │ gzip: 78.12 kB
✓ built in 3.5s
```

**❌ If Failed**: Check TypeScript errors above.

---

### Test 2: Development Server

```bash
cd frontend
npm run dev
```

**Expected Output**:
```
  VITE v6.2.0  ready in 450 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Open**: http://localhost:3000

**Expected UI**:
- Dark theme with cyan accents
- "AEGISAI" header with shield icon
- "SYSTEM ONLINE" green indicator
- 4 stat cards across top
- Video feed on left (requesting camera permission)
- Dashboard charts/logs on right

---

### Test 3: Camera Access

**Steps**:
1. Open http://localhost:3000
2. Browser should prompt for camera permission
3. Click "Allow"

**Expected Result**:
- Video feed shows webcam stream
- HUD overlay appears (corner brackets, center reticle)
- "AEGIS // STANDBY" in top-left of video
- "CAM_01 // 1080p // 30FPS" in bottom-right

**❌ If Camera Fails**:
- Check browser permissions (chrome://settings/content/camera)
- Try different browser (Chrome/Edge work best)
- Check console for errors (F12 → Console)

---

### Test 4: Monitoring Activation

**Steps**:
1. Click **"ACTIVATE AEGIS"** button (green, top-right stat card)
2. Wait 4 seconds

**Expected Result**:
- Button turns red: "STOP SURVEILLANCE"
- Red dot animates (pulse)
- Video shows "AEGIS // LIVE"
- Scan line animation appears
- Console logs: "Processing frame..."
- After 4-8 seconds: First analysis appears

**Console Output**:
```
✅ Gemini AI initialized successfully
📸 Processing frame...
Analysis complete: { incident: false, type: "normal", ... }
```

---

### Test 5: Threat Detection Simulation

**Scenario A: Gun Gesture**

**Steps**:
1. Activate monitoring
2. Make "gun" hand gesture at camera
3. Hold for 5 seconds
4. Wait for analysis (4 second interval)

**Expected Result**:
- **Red border** flashes on video
- **"THREAT DETECTED"** overlay appears
- **Alert sound** plays (beep)
- **Incident logged** in terminal (right panel)
- **Latest Inference** shows:
  - Type: "suspicious_behavior" or "violence"
  - Severity: "medium" or "high"
  - Confidence: 70-95%

**Scenario B: Suspicious Behavior**

**Steps**:
1. Look around nervously
2. Cover face partially
3. Move erratically

**Expected Result**:
- Incident detected within 8-12 seconds
- Severity: "low" or "medium"
- Reasoning mentions "suspicious movements" or "concealment"

**Scenario C: Normal Activity**

**Steps**:
1. Sit normally
2. Type on keyboard
3. Look at screen

**Expected Result**:
- No incident detected
- Latest Inference: "✓ SECURE"
- Type: "normal"

---

### Test 6: Dashboard Features

**Real-time Chart**:
- Graph should update with each scan
- X-axis: timestamps
- Y-axis: confidence (0-100)
- Blue gradient area under line

**Stats Cards**:
- **Scans Performed**: Increments every 4 seconds
- **Incidents**: Increments when threat detected
- **System Load**: Fluctuates 10-50%

**Event Log (Terminal)**:
- Each analysis logged
- Format: `[HH:MM:SS] INFO @normal` or `[HH:MM:SS] ALRT @threat`
- Auto-scrolls to bottom
- Color-coded: Green=INFO, Red=ALRT

---

## 🐳 **Phase 3: Docker Testing**

### Test 7: Docker Build

```bash
# From project root
docker-compose build
```

**Expected Output**:
```
[+] Building 45.2s (12/12) FINISHED
 => [backend] ...
 => [frontend] ...
Successfully built
```

**❌ If Failed**: Check Dockerfile syntax and file paths.

---

### Test 8: Docker Run

```bash
docker-compose up
```

**Expected Output**:
```
aegisai-backend   | ✅ AegisAI Backend Ready
aegisai-frontend  | ready started server on 0.0.0.0:3000
```

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Test API**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","components":{...}}

curl http://localhost:8000/api/stats
# Expected: {"total_incidents":0,"active_incidents":0,...}
```

---

## 🔬 **Phase 4: Backend Testing (Optional)**

### Test 9: Backend Standalone

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

**Expected Output**:
```
INFO: ✅ AegisAI Backend Ready
INFO: 📡 API: http://0.0.0.0:8000
INFO: 📖 Docs: http://0.0.0.0:8000/docs
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Test Endpoints**:
```bash
# Health check
curl http://localhost:8000/health

# Get incidents
curl http://localhost:8000/api/incidents

# Get stats
curl http://localhost:8000/api/stats
```

---

### Test 10: Video Processor

```bash
cd backend
source venv/bin/activate
python -m services.video_processor demo
```

**Expected Output**:
```
🎬 Starting AegisAI Demo Scenario

=== SCENARIO 1: Normal Activity ===
✓ No incident detected

=== SCENARIO 2: Suspicious Behavior ===
✓ Detected: suspicious_behavior
  Severity: medium
  Confidence: 82%

=== SCENARIO 3: Critical Threat ===
✓ Detected: violence
  Severity: high
  Response plan: 5 actions

✓ Demo sequence completed
```

---

## 🎭 **Phase 5: Integration Testing**

### Test 11: Full Stack Integration

**Setup**:
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Test Flow**:

1. **Frontend connects to backend**:
   - Open http://localhost:3000
   - Check console: Should NOT see CORS errors

2. **Create incident via frontend**:
   - Activate monitoring
   - Trigger threat detection
   - Check backend logs for incident save

3. **Verify database**:
   ```bash
   sqlite3 backend/aegis.db
   SELECT * FROM incidents;
   ```
   Should show saved incidents.

4. **Query via API**:
   ```bash
   curl http://localhost:8000/api/incidents
   ```
   Should return incidents created via frontend.

---

## 📊 **Phase 6: Performance Testing**

### Test 12: Load Test

**Duration**: Run for 5 minutes

**Metrics to Monitor**:
- Memory usage (should stay < 500MB)
- CPU usage (should average < 30%)
- Frame rate (should maintain ~1 frame/4 seconds)
- No memory leaks (memory shouldn't continuously increase)

**Monitor**:
```bash
# In browser console (F12)
performance.memory.usedJSHeapSize / 1048576
# Should stay relatively stable
```

---

### Test 13: Stress Test

**Scenario**: Rapid threat changes

**Steps**:
1. Activate monitoring
2. Rapidly change between:
   - Normal pose
   - Threatening gesture
   - Suspicious behavior
   - Normal pose
3. Repeat 10 times
4. Check for:
   - No crashes
   - All incidents logged
   - UI remains responsive

---

## 🐛 **Common Issues & Solutions**

### Issue 1: "Gemini API Key Missing"

**Solution**:
```bash
cd frontend
echo "VITE_GEMINI_API_KEY=your_actual_key" > .env.local
```

### Issue 2: Camera Not Working

**Solutions**:
- Check permissions in browser settings
- Use HTTPS (camera requires secure context)
- Try different browser

### Issue 3: Build Fails

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue 4: CORS Errors

**Solution**: Ensure backend is running and `CORS_ORIGINS` in `.env` includes frontend URL.

### Issue 5: No Incidents Detected

**Solution**: 
- Check Gemini API key is valid
- Check console for API errors
- Verify `SYSTEM_INSTRUCTION` in constants.ts
- Try more obvious threatening gesture

---

## 📝 **Test Report Template**

```markdown
# AegisAI Test Report

**Date**: YYYY-MM-DD
**Tester**: [Your Name]
**Environment**: [Local/Docker/Production]

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Build | ✅/❌ | |
| Camera | ✅/❌ | |
| Monitoring | ✅/❌ | |
| Threat Detection | ✅/❌ | X/10 attempts successful |
| Dashboard | ✅/❌ | |
| Backend API | ✅/❌ | |
| Docker | ✅/❌ | |

## Issues Found

1. [Description]
   - Severity: High/Medium/Low
   - Steps to reproduce:
   - Expected vs Actual:

## Performance Metrics

- Memory: XXX MB
- CPU: XX%
- Response Time: X.X seconds

## Recommendation

[ ] Ready for deployment
[ ] Needs fixes (see issues above)
```

---

## 🚀 **Deployment Readiness**

If all tests pass:

```bash
# Tag release
git tag -a v2.5.0 -m "Production release"
git push origin v2.5.0

# Deploy
# See DEPLOYMENT.md for instructions
```

---

**Good luck with testing!** 🎉
