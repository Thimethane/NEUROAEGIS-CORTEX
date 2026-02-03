# 🛡️ NeuroAegis Cortex

**AI-Powered Security Analysis System Using Google Gemini 3**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0-61DAFB.svg)](https://reactjs.org/)
[![Gemini 3](https://img.shields.io/badge/Gemini-3%20Pro-4285F4.svg)](https://ai.google.dev/)

> **Intelligent security monitoring that understands context, not just motion.**

NeuroAegis Cortex leverages Google's cutting-edge **Gemini 3 Pro Preview** AI model to provide unprecedented security analysis capabilities. Unlike traditional computer vision systems that simply detect objects, NeuroAegis understands *context, intent, and behavior* to provide intelligent threat assessment and automated response planning.

---

## 🎯 The Problem

Traditional security systems suffer from:
- **False Alarm Epidemic:** Motion sensors trigger on everything (pets, shadows, trees)
- **No Context Understanding:** Can't differentiate between delivery person and intruder
- **Manual Response:** Humans must watch, decide, and act
- **No Learning:** Same mistakes repeated every day

**Result:** Security fatigue, missed threats, and wasted resources.

---

## ✨ Our Solution

NeuroAegis Cortex uses **Google Gemini 3's multimodal AI** to:

✅ **Understand Context** - "Person peering into windows at night" vs "Mail carrier at door"  
✅ **Explain Reasoning** - Natural language explanation of why something is a threat  
✅ **Automatic Planning** - AI generates appropriate response actions based on severity  
✅ **Temporal Awareness** - Learns patterns over time to reduce false positives  
✅ **Self-Hosted & Private** - Your video never leaves your premises  

---

## 🚀 Key Features

### 🤖 Powered by Gemini 3 Pro Preview

- **Latest AI Technology** (Released 2025)
- **Multimodal Understanding** - Processes images + text together
- **Natural Language Output** - Human-readable incident reports
- **Structured JSON** - Reliable parsing for automation

### 🎯 Intelligent Threat Detection

```json
{
  "incident": true,
  "type": "intrusion",
  "severity": "high",
  "confidence": 87,
  "reasoning": "Masked individual forcing entry through window. No visible authorization. Aggressive body language.",
  "subjects": ["Adult male, ~6ft, black hoodie, face concealed"],
  "recommended_actions": ["alert", "record", "contact_authorities"]
}
```

### 📊 Two-Agent AI Architecture

```
┌─────────────┐
│ Video Frame │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Vision Agent       │  ← Gemini 3: "What's happening?"
│  (Threat Analysis)  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Planner Agent      │  ← Gemini 3: "What should we do?"
│  (Response Plan)    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Action Executor    │
│  (Execute Actions)  │
└─────────────────────┘
```

### 🔧 Automated Response Actions

- **save_evidence** - High-quality screenshot with metadata
- **send_alert** - Email/SMS with incident details
- **log_incident** - Database record for audit trail
- **escalate** - Human intervention for critical threats
- **monitor** - Enhanced tracking for suspicious activity
- **+ 6 more actions**

---

## 🚦 Getting Started

### Prerequisites

- Docker & Docker Compose
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- Webcam or IP camera
- 4GB+ RAM, 2+ CPU cores

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Thimethane/NEUROAEGIS-CORTEX
cd neuroaegis-cortex

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# 3. Start the system
docker-compose up -d

# 4. Open browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

That's it! The system is now monitoring and analyzing frames from your camera.

---

## 📊 Performance

| Model | Avg Time | Throughput | Use Case |
|-------|----------|------------|----------|
| `gemini-3-pro-preview` | 4.9s | 12 frames/min | Best quality |
| `gemini-3-flash` | 1.2s | 50 frames/min | Production |

**Cost:** ~$0.001 per frame (~$10/month for 10K frames)

---

## 📚 Documentation

- [**Architecture**](./ARCHITECTURE.md) - System design & data flow
- [**Gemini 3 Integration**](./GEMINI_3_INTEGRATION.md) - How we use Gemin

---

## 🙏 Acknowledgments

- **Google Gemini Team** - For the incredible Gemini 3 API
- **FastAPI** - For the excellent Python web framework
- **React Team** - For the robust UI library

---

<div align="center">

**Built with ❤️ using Google Gemini 3**

</div>