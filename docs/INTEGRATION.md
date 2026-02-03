# 🔗 Frontend-Backend Integration Guide

Complete guide to connecting AegisAI frontend and backend.

---

## 🎯 **Two Deployment Modes**

### **Mode 1: Client-Side (Current Default)**

```
Browser → Gemini API (Direct)
```

**Pros:**
- ✅ Simpler setup (no backend needed)
- ✅ Works immediately
- ✅ Perfect for demos
- ✅ No server costs

**Cons:**
- ❌ API key exposed in browser
- ❌ No incident storage
- ❌ No multi-user support
- ❌ Limited to browser capabilities

**Use When:**
- Quick demos
- Development
- Single-user scenarios

---

### **Mode 2: Full Stack (Production)**

```
Browser → Backend API → Gemini API
              ↓
         Database (SQLite)
```

**Pros:**
- ✅ API key secured on server
- ✅ Incidents stored in database
- ✅ Multi-user support
- ✅ Advanced features (actions, analytics)
- ✅ Production-ready

**Cons:**
- ❌ Requires backend setup
- ❌ More complex deployment

**Use When:**
- Production deployments
- Multiple users
- Need incident history
- Enterprise use

---

## 🚀 **Quick Start: Enable Full Stack**

### **Step 1: Start Backend**

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

**Verify**: http://localhost:8000/health should return:
```json
{"status":"healthy","components":{...}}
```

---

### **Step 2: Enable Backend in Frontend**

Edit `frontend/src/constants.ts`:

```typescript
// Change this line:
ENABLE_BACKEND_API: false

// To this:
ENABLE_BACKEND_API: true
```

---

### **Step 3: Configure Backend URL**

Edit `frontend/.env.local`:

```bash
VITE_API_URL=http://localhost:8000
```

---

### **Step 4: Start Frontend**

```bash
cd frontend
npm run dev
```

---

### **Step 5: Verify Connection**

Open http://localhost:3000

Look for **two indicators** in header:
- `SYSTEM ONLINE` (green) - Frontend working
- `BACKEND` (blue pulsing) - Connected to backend

If shows `CLIENT-SIDE` (orange) - Backend not connected

---

## 🔧 **Testing the Connection**

### **Test 1: Health Check**

```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "components": {
    "database": "ok",
    "vision_agent": "ok",
    "planner_agent": "ok"
  }
}
```

---

### **Test 2: Analyze Endpoint**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="}'
```

**Expected**:
```json
{
  "incident": false,
  "type": "normal",
  "severity": "low",
  "confidence": 80,
  "reasoning": "...",
  "subjects": [],
  "recommended_actions": []
}
```

---

### **Test 3: Frontend → Backend Flow**

1. Open http://localhost:3000
2. Check header shows `BACKEND` (blue)
3. Activate monitoring
4. Trigger threat
5. Check backend logs:

**Backend Terminal Should Show**:
```
INFO: POST /api/analyze
INFO: Analysis complete: {"incident":true,...}
```

---

## 📊 **Architecture Comparison**

### **Client-Side Mode**

```
┌──────────────────────────┐
│  Browser (Port 3000)     │
│                          │
│  ┌────────────────────┐  │
│  │   React Frontend   │  │
│  │                    │  │
│  │   ↓ (direct call)  │  │
│  │                    │  │
│  │   Gemini API       │  │
│  └────────────────────┘  │
└──────────────────────────┘

Data Flow:
1. Capture frame
2. Call Gemini API directly
3. Display result
4. Store in browser memory (lost on refresh)
```

---

### **Full Stack Mode**

```
┌──────────────────────┐      ┌──────────────────────┐
│ Browser (Port 3000)  │      │  Backend (Port 8000) │
│                      │      │                      │
│  ┌────────────────┐  │      │  ┌────────────────┐  │
│  │ React Frontend │  │ POST │  │  FastAPI       │  │
│  │                ├──┼──────┼─▶│                │  │
│  │  (UI only)     │  │      │  │  Vision Agent  │  │
│  └────────────────┘  │      │  │      ↓         │  │
│                      │      │  │  Planner Agent │  │
│                      │      │  │      ↓         │  │
│                      │      │  │  Actions       │  │
│                      │      │  │      ↓         │  │
│                      │      │  │  Database      │  │
│                      │      │  └────────────────┘  │
└──────────────────────┘      └──────────────────────┘

Data Flow:
1. Capture frame
2. Send to backend API
3. Backend analyzes with Gemini
4. Backend saves to database
5. Backend executes actions
6. Return result to frontend
7. Display result
```

---

## 🔄 **Switching Between Modes**

### **Switch to Client-Side**

```typescript
// frontend/src/constants.ts
ENABLE_BACKEND_API: false
```

Restart frontend:
```bash
npm run dev
```

**Indicator**: Shows `CLIENT-SIDE` (orange)

---

### **Switch to Full Stack**

```typescript
// frontend/src/constants.ts
ENABLE_BACKEND_API: true
```

Start backend first:
```bash
cd backend && python main.py
```

Then frontend:
```bash
cd frontend && npm run dev
```

**Indicator**: Shows `BACKEND` (blue)

---

## 🐛 **Troubleshooting**

### **Issue 1: Shows CLIENT-SIDE but Backend is Running**

**Check:**
1. Backend URL in `.env.local`:
   ```bash
   VITE_API_URL=http://localhost:8000
   ```
2. CORS is enabled (should be by default)
3. No firewall blocking port 8000

**Test:**
```bash
curl http://localhost:8000/health
```

---

### **Issue 2: CORS Errors**

**Error**: `Access-Control-Allow-Origin`

**Fix**: Ensure backend `.env` has:
```bash
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

Restart backend.

---

### **Issue 3: 404 on /api/analyze**

**Fix**: Update backend to latest version with analyze endpoint.

Check:
```bash
curl http://localhost:8000/docs
```

Should list `/api/analyze` endpoint.

---

### **Issue 4: Backend Not Responding**

**Check**:
```bash
# Is it running?
curl http://localhost:8000/

# Check logs
# (Look at terminal where you ran python main.py)
```

**Restart**:
```bash
cd backend
python main.py
```

---

## 📈 **Feature Comparison**

| Feature | Client-Side | Full Stack |
|---------|-------------|------------|
| Threat Detection | ✅ | ✅ |
| Real-time Analysis | ✅ | ✅ |
| Incident Storage | ❌ | ✅ |
| Action Execution | ❌ | ✅ |
| Multi-user | ❌ | ✅ |
| API Security | ❌ | ✅ |
| Database | ❌ | ✅ |
| Email Alerts | ❌ | ✅ |
| Historical Data | ❌ | ✅ |
| Load Balancing | ❌ | ✅ |

---

## ✅ **Verification Checklist**

### **Client-Side Mode**
- [ ] Frontend runs on port 3000
- [ ] Shows `CLIENT-SIDE` in header
- [ ] Threat detection works
- [ ] Dashboard updates
- [ ] No backend required

### **Full Stack Mode**
- [ ] Backend runs on port 8000
- [ ] Frontend runs on port 3000
- [ ] Shows `BACKEND` in header (blue)
- [ ] `/health` returns healthy
- [ ] Threat detection works
- [ ] Incidents saved to database
- [ ] Can query incidents via API

---

## 🚀 **Production Deployment**

### **Client-Side**

```bash
# Build frontend only
cd frontend
npm run build

# Deploy to Vercel
vercel --prod
```

**Environment Variables** (Vercel):
- `VITE_GEMINI_API_KEY` = your_key

---

### **Full Stack**

**Backend → Render:**
```bash
git push render main
```

**Frontend → Vercel:**
```bash
cd frontend
vercel --prod
```

**Environment Variables**:

**Render** (Backend):
- `GEMINI_API_KEY` = your_key

**Vercel** (Frontend):
- `VITE_GEMINI_API_KEY` = your_key
- `VITE_API_URL` = https://your-backend.onrender.com
- Set `ENABLE_BACKEND_API: true` in constants.ts

---

## 📝 **Summary**

| Aspect | Current State | After Integration |
|--------|---------------|-------------------|
| **Default Mode** | Client-Side | Client-Side |
| **Can Use Backend** | ❌ No | ✅ Yes |
| **Toggle** | N/A | `ENABLE_BACKEND_API` flag |
| **Indicator** | None | Blue "BACKEND" or Orange "CLIENT-SIDE" |
| **Flexibility** | One mode only | Switch anytime |

**Key Point**: You can now use **BOTH** modes! Switch by changing one flag in `constants.ts`.

---

**Integration Complete!** 🎉
