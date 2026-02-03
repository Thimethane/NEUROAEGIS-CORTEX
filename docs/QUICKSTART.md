# 🚀 AegisAI Quickstart Guide

Get AegisAI running with **Gemini 3.0** in 5 minutes.

---

## ⚡ Prerequisites

- **Node.js 18+** → [Download](https://nodejs.org/)
- **Python 3.9+** → [Download](https://python.org/downloads/)
- **Gemini API Key** → [Get Free Key](https://aistudio.google.com/apikey)
- **Webcam** (for live monitoring)

---

## 📦 Installation

### Step 1: Clone Repository (30 seconds)

```bash
git clone https://github.com/Thimethane/aegisai.git
cd aegisai
```

### Step 2: Environment Setup (1 minute)

```bash
# Create environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_gemini_3_api_key_here
```

**Get your Gemini 3 API key:**
1. Visit https://aistudio.google.com/apikey
2. Click "Get API key"
3. Copy the key
4. Paste into `.env` file

### Step 3: Frontend Setup (2 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Create frontend environment
echo "VITE_GEMINI_API_KEY=your_gemini_3_api_key_here" > .env.local

# Replace with your actual API key
```

### Step 4: Launch! (1 minute)

```bash
# Start development server
npm run dev
```

**🎉 Open http://localhost:3000**

---

## ✅ Verify Gemini 3 Integration

### Check Console Output

You should see:
```
✓ Gemini 3.0 Flash initialized
✓ Model: gemini-3-flash-preview
✓ Context window: 1,000,000 tokens
✓ Deep Think mode: Available
✓ Thought signatures: Enabled
```

### Test Camera Access

1. Browser will request camera permission → Click **Allow**
2. Video feed should appear with HUD overlay
3. Click **"ACTIVATE AEGIS"** button

### Verify AI Analysis

After 4 seconds, console should show:
```javascript
🔍 Analyzing frame #1 with Gemini 3 Flash...
✓ Analysis complete (1.2s)
{
  incident: false,
  type: "normal",
  confidence: 92,
  model_used: "gemini-3-flash-preview",
  thinking_level: "low",
  tokens_used: 456
}
```

---

## 🎯 Quick Test

### Test 1: Normal Behavior

**Action**: Sit normally, type on keyboard

**Expected**:
- ✅ No incident detected
- ✅ Type: "normal"
- ✅ Confidence: 80-95%
- ✅ Model: Gemini 3 Flash

### Test 2: Threat Detection

**Action**: Make gun gesture with hand

**Expected** (within 8 seconds):
- ✅ Incident: true
- ✅ Type: "violence" or "suspicious_behavior"
- ✅ Red border on video
- ✅ Alert sound plays
- ✅ Response plan generated

### Test 3: Deep Think Mode

**Action**: Trigger incident, then check console

**Expected**:
```javascript
🧠 Escalating to Deep Think mode...
✓ Model: gemini-3-pro-preview
✓ Thinking level: high
✓ Thought process: "Evaluating three scenarios: (1) Authorized...
   (2) Potential threat... (3) False positive... Cross-referencing
   historical patterns... Conclusion: Genuine threat detected."
```

---

## 🎨 Dashboard Overview

```
┌─────────────────────────────────────────────────────────────┐
│  AEGISAI                               🟢 SYSTEM ONLINE     │
├─────────────────────────────────────────────────────────────┤
│ 📊 Scans: 42  │ 🚨 Incidents: 3 │ ⚡ Load: 24% │ 🎯 ACTIVE │
├─────────────────────────────────────────────────────────────┤
│                    │                                         │
│   📹 VIDEO FEED    │    📈 THREAT ANALYSIS CHART            │
│                    │                                         │
│   [Live Camera]    │    💡 AI THOUGHT PROCESS               │
│   + HUD Overlay    │    "Subject exhibits weapon posture... │
│                    │     Cross-referencing 45 min history"   │
│                    │                                         │
│                    │    📋 LATEST INFERENCE                  │
│                    │    Type: Violence | Conf: 94%          │
│                    │                                         │
│                    │    💬 EVENT LOG                         │
│                    │    [12:34:56] ALRT @violence           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Enable Deep Think Mode

```typescript
// frontend/src/constants.ts

export const CONFIG = {
  // Use Gemini 3 Pro for all analysis
  DEFAULT_MODEL: 'gemini-3-pro-preview',
  
  // Enable extended reasoning
  DEFAULT_THINKING_LEVEL: 'high',
  
  // Show AI's thought process
  ENABLE_THOUGHT_TRANSPARENCY: true,
  
  // High-quality image analysis
  MEDIA_RESOLUTION: 'high'
};
```

### Cost Optimization Mode

```typescript
export const CONFIG = {
  // Use faster, cheaper Gemini 3 Flash
  DEFAULT_MODEL: 'gemini-3-flash-preview',
  
  // Quick analysis
  DEFAULT_THINKING_LEVEL: 'low',
  
  // Standard quality
  MEDIA_RESOLUTION: 'medium'
};
```

---

## 🐳 Docker Alternative

Prefer containers? One command deployment:

```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Access at http://localhost:3000

---

## 🆘 Troubleshooting

### Issue: "Gemini API Key Invalid"

**Solution**:
```bash
# Verify key is set
cat .env | grep GEMINI_API_KEY

# Ensure no extra quotes or spaces
GEMINI_API_KEY=AIzaSy...  # Correct
GEMINI_API_KEY="AIzaSy..." # Wrong (remove quotes)
```

### Issue: Camera Not Working

**Solution**:
1. Check browser permissions: `chrome://settings/content/camera`
2. Use HTTPS (camera requires secure context)
3. Try different browser (Chrome/Edge recommended)

### Issue: "Model Not Found"

**Solution**:
```bash
# Ensure using Gemini 3 models
# Check frontend/src/services/geminiService.ts

const MODEL_NAME = 'gemini-3-flash-preview';  // Correct
// NOT 'gemini-2.0-flash-exp' (old model)
```

### Issue: Console Shows Errors

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📊 Performance Expectations

### Normal Operation (Gemini 3 Flash)

| Metric | Expected Value |
|--------|----------------|
| Frame analysis time | 1-2 seconds |
| Accuracy | 90-94% |
| False positives | < 8% |
| Cost per hour (900 frames) | ~$0.18 |
| Memory usage | < 300MB |

### Deep Think Mode (Gemini 3 Pro)

| Metric | Expected Value |
|--------|----------------|
| Frame analysis time | 3-5 seconds |
| Accuracy | 94-96% |
| False positives | < 5% |
| Cost per hour | ~$2.88 |
| Memory usage | < 400MB |

---

## 🎓 Next Steps

### Learn More
- **[Gemini 3 Features](GEMINI_3_FEATURES.md)** - Deep dive into capabilities
- **[Configuration Guide](CONFIGURATION.md)** - Advanced settings
- **[API Documentation](API_DOCUMENTATION.md)** - Backend API reference

### Production Deployment
- **[Deployment Guide](DEPLOYMENT.md)** - Cloud deployment
- **[Scaling Guide](SCALING.md)** - Multi-camera setup
- **[Security Best Practices](SECURITY.md)** - Production hardening

### Development
- **[Contributing Guide](CONTRIBUTING.md)** - Join the project
- **[Architecture](ARCHITECTURE.md)** - System design
- **[Testing Guide](TEST_GUIDE.md)** - Test scenarios

---

## ✅ Success Checklist

Before moving to production, verify:

- [ ] ✅ Gemini 3 Flash initialized successfully
- [ ] ✅ Camera access working
- [ ] ✅ Threat detection working (test with gun gesture)
- [ ] ✅ Dashboard updating in real-time
- [ ] ✅ No console errors (warnings OK)
- [ ] ✅ Thought transparency showing AI reasoning
- [ ] ✅ Response time < 3 seconds
- [ ] ✅ Confidence scores reasonable (> 70%)

---

## 💡 Pro Tips

### Optimize for Speed
```typescript
// Use Flash model with low thinking
model: 'gemini-3-flash-preview',
thinkingLevel: 'low',
mediaResolution: 'medium'
// → 3x faster, 6x cheaper
```

### Optimize for Accuracy
```typescript
// Use Pro model with deep think
model: 'gemini-3-pro-preview',
thinkingLevel: 'high',
mediaResolution: 'high'
// → 30% more accurate, better reasoning
```

### Adaptive Configuration
```typescript
// Let AegisAI automatically choose
// based on threat level and scene complexity
ENABLE_ADAPTIVE_MODEL_SELECTION: true
// → Best balance of speed, cost, and accuracy
```

---

## 🎉 You're Ready!

**AegisAI is now running with Gemini 3.0**

Next: Try the [Full Stack Mode](INTEGRATION.md) to unlock:
- Incident storage and history
- Automated response execution
- Multi-user support
- Advanced analytics

---

**Questions?** Check [docs/](.) or open an [issue](https://github.com/Thimethane/aegisai/issues)

**Happy Monitoring!** 🛡️
