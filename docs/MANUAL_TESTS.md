# 📝 Manual Test Cases - AegisAI

Detailed step-by-step test cases for manual verification.

---

## 🎯 Test Case 1: First Run Experience

**Objective**: Verify clean installation works end-to-end

**Prerequisites**: Fresh clone of repository

**Steps**:

1. Open PowerShell in project root
2. Run: `.\verify.ps1`
3. **Expected**: All checks pass OR clear instructions shown
4. Run: `.\create-files.ps1` (if needed)
5. Edit `.env` - add Gemini API key
6. Edit `frontend\.env.local` - add Gemini API key
7. Run backend setup:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
8. Run frontend setup:
   ```powershell
   cd frontend
   npm install
   ```
9. Start frontend:
   ```powershell
   npm run dev
   ```
10. Open browser to http://localhost:3000

**Expected Result**:
- ✅ Page loads without errors
- ✅ Dark theme with cyan accents
- ✅ "AEGISAI" header visible
- ✅ 4 stat cards showing zeros
- ✅ Video placeholder or camera prompt
- ✅ Dashboard with empty chart

**Pass Criteria**: All expected results achieved

---

## 🎯 Test Case 2: Camera Permission Flow

**Objective**: Verify camera access works correctly

**Steps**:

1. Open http://localhost:3000 in **Chrome** (recommended)
2. Browser shows permission prompt
3. Click **"Allow"**
4. Wait 2 seconds

**Expected Result**:
- ✅ Video feed shows webcam stream
- ✅ HUD elements visible:
  - Corner brackets (4 corners)
  - Center reticle (circle with red dot)
  - "AEGIS // STANDBY" text (top-left)
  - "CAM_01 // 1080p // 30FPS" (bottom-right)
  - Current time (top-right)
- ✅ No console errors (F12 → Console)

**Alternative Test** (if "Block" was clicked):
1. Click camera icon in browser address bar
2. Change to "Allow"
3. Refresh page
4. Verify video appears

**Pass Criteria**: Video stream visible with HUD overlay

---

## 🎯 Test Case 3: Monitoring Activation

**Objective**: Verify monitoring can be started and stopped

**Steps**:

1. Ensure camera is active (from Test Case 2)
2. Click **"ACTIVATE AEGIS"** button (green, top-right)
3. Observe changes for 10 seconds
4. Click **"STOP SURVEILLANCE"** button (now red)
5. Wait 5 seconds

**Expected During Monitoring (Active)**:
- ✅ Button turns red with "STOP SURVEILLANCE"
- ✅ Red indicator dot pulses
- ✅ Video shows "AEGIS // LIVE"
- ✅ Scan line animation appears (blue gradient moving)
- ✅ Center reticle enlarges and becomes more opaque
- ✅ Console logs appear every ~4 seconds:
  ```
  Processing frame...
  Analysis complete: {...}
  ```
- ✅ "Scans Performed" counter increments (every 4 sec)
- ✅ "System Load" fluctuates (40-60%)

**Expected After Stopping**:
- ✅ Button turns green with "ACTIVATE AEGIS"
- ✅ Indicator dot stops pulsing (solid green)
- ✅ Video shows "AEGIS // STANDBY"
- ✅ Scan line disappears
- ✅ No new console logs
- ✅ Counters stop incrementing

**Pass Criteria**: All transitions work as expected

---

## 🎯 Test Case 4: Normal Behavior Detection

**Objective**: Verify system correctly identifies safe behavior

**Steps**:

1. Activate monitoring (Test Case 3)
2. Sit normally facing camera
3. Type on keyboard naturally
4. Look at screen
5. Wait for 2 analysis cycles (~8 seconds)
6. Check "Latest Inference" card

**Expected Result**:
- ✅ Type: "normal" or "None"
- ✅ Incident: false (shows "✓ SECURE")
- ✅ Severity: "low"
- ✅ Confidence: 60-95%
- ✅ Reasoning mentions: "normal activity", "working", "sitting"
- ✅ NO red border on video
- ✅ NO alert sound
- ✅ Event log shows: `[HH:MM:SS] INFO @normal`

**Pass Criteria**: System recognizes normal behavior

---

## 🎯 Test Case 5: Threat Detection - Gun Gesture

**Objective**: Verify threat detection works

**Steps**:

1. Activate monitoring
2. Make hand into gun shape (index finger pointed, thumb up)
3. Point at camera
4. Hold steady for 6 seconds
5. Wait for analysis (~4 sec)
6. Observe UI changes

**Expected Result**:
- ✅ **Red border** appears on video (pulsing animation)
- ✅ **"THREAT DETECTED"** overlay bounces
- ✅ **Alert sound** plays (short beep)
- ✅ Latest Inference shows:
  - Incident: true
  - Type: "violence", "suspicious_behavior", or "threat"
  - Severity: "medium" or "high"
  - Confidence: 70-95%
  - Reasoning mentions: "weapon", "gun", "threatening gesture", "simulated threat"
- ✅ "Incidents Detected" counter increments to 1
- ✅ Event log shows: `[HH:MM:SS] ALRT @[type]`
- ✅ Chart updates with spike in confidence

**If Detection Fails**:
- Try more exaggerated gesture
- Ensure good lighting
- Hold longer (10 seconds)
- Check console for errors
- Verify API key is correct

**Pass Criteria**: Threat detected within 12 seconds

---

## 🎯 Test Case 6: Threat Detection - Suspicious Behavior

**Objective**: Verify detection of subtle threats

**Scenario A: Face Covering**

**Steps**:
1. Activate monitoring
2. Cover lower face with hand/cloth
3. Move head side to side suspiciously
4. Hold for 8 seconds
5. Wait for analysis

**Expected**:
- Type: "suspicious_behavior" or "concealment"
- Severity: "low" or "medium"
- Reasoning mentions: "covering face", "concealment", "suspicious"

**Scenario B: Nervous Behavior**

**Steps**:
1. Look around rapidly
2. Glance at camera then away quickly
3. Fidget hands nervously
4. Repeat for 10 seconds

**Expected**:
- Type: "suspicious_behavior" or "loitering"
- Reasoning mentions: "nervous", "erratic", "unusual behavior"

**Pass Criteria**: At least 1 of 2 scenarios detected

---

## 🎯 Test Case 7: Dashboard Real-time Updates

**Objective**: Verify all dashboard elements update correctly

**Setup**: Activate monitoring, trigger 2-3 incidents

**Verify Each Element**:

**Stats Cards**:
- ✅ Scans Performed: Increments every 4 sec
- ✅ Incidents: Shows correct count
- ✅ System Load: Animates between 10-60%
- ✅ Activate/Stop button: Works both ways

**Threat Analysis Chart**:
- ✅ X-axis shows timestamps (HH:MM:SS)
- ✅ Y-axis shows 0-100
- ✅ Blue gradient area appears
- ✅ Line updates with new data points
- ✅ Shows last 10 data points maximum
- ✅ Tooltip shows confidence on hover

**Latest Inference Card**:
- ✅ Updates with each analysis
- ✅ Shows correct type, severity, confidence
- ✅ Reasoning text displayed
- ✅ Color matches severity (red/orange/blue)
- ✅ Timestamp accurate

**Event Log (Terminal)**:
- ✅ New events appear at bottom
- ✅ Auto-scrolls to latest
- ✅ Format: `[time] TYPE @incident`
- ✅ Color coding: Green=INFO, Red=ALRT
- ✅ Reasoning text shown
- ✅ At least last 20 events visible

**Pass Criteria**: All elements update correctly

---

## 🎯 Test Case 8: Performance Under Load

**Objective**: Verify system stability during extended use

**Steps**:

1. Activate monitoring
2. Let run for 5 minutes continuously
3. Trigger 5 incidents during this time
4. Monitor browser performance (F12 → Performance tab)

**During Test, Verify**:
- ✅ No browser crashes
- ✅ No UI freezing
- ✅ Memory usage stable (< 500MB)
- ✅ CPU usage reasonable (< 50% average)
- ✅ All incidents logged correctly
- ✅ Chart doesn't overflow/break
- ✅ Event log doesn't cause lag

**After 5 Minutes**:
- Check total scans: Should be ~75 (1 per 4 sec)
- Check UI responsiveness: Should still be smooth
- Check console: No memory leak warnings

**Pass Criteria**: Runs smoothly for 5 minutes

---

## 🎯 Test Case 9: Error Handling

**Objective**: Verify graceful error handling

**Scenario A: Invalid API Key**

**Steps**:
1. Edit `frontend\.env.local`
2. Change API key to: `VITE_GEMINI_API_KEY=invalid_key_123`
3. Restart frontend: `npm run dev`
4. Activate monitoring
5. Wait for analysis

**Expected**:
- ✅ Error in console: "API error" or "Invalid key"
- ✅ UI still functional (no crash)
- ✅ Error message shown in Latest Inference
- ✅ System continues trying

**Scenario B: Camera Disconnected**

**Steps**:
1. Start with camera working
2. Physically cover/disconnect webcam
3. Observe behavior

**Expected**:
- ✅ Error message in video feed area
- ✅ Option to retry/refresh
- ✅ No crash

**Pass Criteria**: Errors handled gracefully

---

## 🎯 Test Case 10: Browser Compatibility

**Objective**: Verify cross-browser support

**Browsers to Test**:
1. Chrome (primary)
2. Edge
3. Firefox

**For Each Browser**:
1. Open http://localhost:3000
2. Allow camera
3. Activate monitoring
4. Trigger 1 incident
5. Verify all UI elements work

**Expected**:
- ✅ Chrome: Full support (reference)
- ✅ Edge: Full support
- ✅ Firefox: Full support (may need different camera permissions)

**Known Issues**:
- Safari: May have camera issues (not primary target)
- Mobile: Not optimized (desktop-first design)

**Pass Criteria**: Works in Chrome, Edge, Firefox

---

## 🎯 Test Case 11: Docker Deployment

**Objective**: Verify Docker setup works

**Steps**:

1. Ensure Docker Desktop is running
2. From project root:
   ```powershell
   docker-compose build
   ```
3. Wait for build (3-5 minutes)
4. Run:
   ```powershell
   docker-compose up
   ```
5. Wait for startup
6. Open http://localhost:3000

**Expected**:
- ✅ Build completes without errors
- ✅ Both containers start:
  - `aegisai-backend`
  - `aegisai-frontend`
- ✅ Frontend accessible at :3000
- ✅ Backend accessible at :8000
- ✅ All features work same as local

**Test API**:
```powershell
curl http://localhost:8000/health
curl http://localhost:8000/api/stats
```

**Pass Criteria**: Docker deployment functional

---

## 📊 Test Report Template

After running all tests, fill out:

```markdown
# Test Report - AegisAI v2.5.0

**Date**: _____________
**Tester**: _____________
**Environment**: Local / Docker / Cloud

## Test Results

| # | Test Case | Result | Notes |
|---|-----------|--------|-------|
| 1 | First Run | ✅ / ❌ | |
| 2 | Camera Access | ✅ / ❌ | |
| 3 | Monitoring | ✅ / ❌ | |
| 4 | Normal Detection | ✅ / ❌ | |
| 5 | Threat: Gun | ✅ / ❌ | Detected in X seconds |
| 6 | Threat: Suspicious | ✅ / ❌ | X/2 scenarios |
| 7 | Dashboard Updates | ✅ / ❌ | |
| 8 | Performance | ✅ / ❌ | Memory: XXX MB |
| 9 | Error Handling | ✅ / ❌ | |
| 10 | Browser Compat | ✅ / ❌ | Chrome/Edge/Firefox |
| 11 | Docker | ✅ / ❌ | |

## Summary

**Passed**: __/11
**Failed**: __/11

**Critical Issues**: 
- 

**Minor Issues**:
-

**Recommendation**: 
[ ] Approved for deployment
[ ] Needs fixes
```

---

## ✅ Acceptance Criteria

To pass testing phase:
- Minimum 9/11 tests must pass
- No critical failures (Test 1, 2, 3, 5 must pass)
- Performance acceptable
- No crashes during normal use

---

**Ready to test!** 🧪
