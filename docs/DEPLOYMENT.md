# 🚀 AegisAI Deployment Guide

**Production deployment guide for Gemini 3-powered security systems**

---

## 📋 Table of Contents

- [Deployment Overview](#deployment-overview)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Checklist](#production-checklist)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Scaling Strategies](#scaling-strategies)

---

## 🎯 Deployment Overview

### Deployment Modes

AegisAI supports three deployment architectures:

#### **1. Frontend-Only (Serverless)**
```
Browser → Gemini 3 API (Direct)
```
**Best for:**
- Single-user deployments
- Demos and prototypes
- Quick setup requirements
- No backend infrastructure

**Limitations:**
- API key exposed in browser
- No incident persistence
- Limited to browser capabilities

#### **2. Full Stack (Recommended)**
```
Browser → Backend API → Gemini 3 API
              ↓
         Database
```
**Best for:**
- Production deployments
- Multi-user environments
- Enterprise security
- Compliance requirements

**Benefits:**
- API key secured server-side
- Incident history and analytics
- Advanced response automation
- Multi-camera support

#### **3. Edge Deployment**
```
IP Camera → Edge Device → Gemini 3 API
                ↓
           Local Storage
```
**Best for:**
- Network-restricted environments
- Low-latency requirements
- Bandwidth optimization
- Privacy-sensitive deployments

---

## 🔧 Environment Setup

### Required Environment Variables

#### **Frontend (.env.local)**
```bash
# Gemini 3 Configuration
VITE_GEMINI_API_KEY=your_gemini_3_api_key_here

# Model Selection
VITE_DEFAULT_MODEL=gemini-3-flash-preview
VITE_ENABLE_PRO_ESCALATION=true

# Analysis Configuration
VITE_DEFAULT_THINKING_LEVEL=low
VITE_DEFAULT_MEDIA_RESOLUTION=medium
VITE_ENABLE_THOUGHT_TRANSPARENCY=true

# Backend Integration (if using full stack)
VITE_API_URL=https://your-backend.onrender.com
VITE_ENABLE_BACKEND=true

# Performance
VITE_ANALYSIS_INTERVAL=4000
VITE_MAX_FRAME_HISTORY=1000
```

#### **Backend (.env)**
```bash
# Gemini 3 Configuration
GEMINI_API_KEY=your_gemini_3_api_key_here

# Model Configuration
DEFAULT_MODEL=gemini-3-flash-preview
ENABLE_MODEL_ESCALATION=true
FLASH_MODEL=gemini-3-flash-preview
PRO_MODEL=gemini-3-pro-preview

# Analysis Settings
DEFAULT_THINKING_LEVEL=low
HIGH_THINKING_THRESHOLD=70
DEFAULT_MEDIA_RESOLUTION=medium

# Context Management
MAX_CONTEXT_TOKENS=500000
ENABLE_THOUGHT_SIGNATURES=true
SIGNATURE_RETENTION_HOURS=24

# Database
DATABASE_URL=sqlite:///./aegis.db
# For PostgreSQL: postgresql://user:pass@host:5432/aegis

# Security
CORS_ORIGINS=["https://your-frontend.vercel.app"]
API_KEY_REQUIRED=false  # Set true for production

# Performance
MAX_CONCURRENT_ANALYSES=10
REQUEST_TIMEOUT=30
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=INFO
ENABLE_PERFORMANCE_METRICS=true
```

### Security Best Practices

```bash
# Generate secure API key for backend protection
openssl rand -hex 32

# Add to .env
API_KEY=generated_secure_key_here
API_KEY_REQUIRED=true

# Frontend must include in requests:
# X-API-Key: generated_secure_key_here
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Thimethane/aegisai.git
cd aegisai

# 2. Configure environment
cp .env.example .env
# Edit .env with your Gemini API key

# 3. Build and run
docker-compose up -d

# 4. Verify deployment
curl http://localhost:8000/health
curl http://localhost:3000
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: aegisai-backend
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DEFAULT_MODEL=gemini-3-flash-preview
      - ENABLE_MODEL_ESCALATION=true
      - MAX_CONTEXT_TOKENS=500000
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: 
      context: ./frontend
      args:
        - VITE_GEMINI_API_KEY=${GEMINI_API_KEY}
        - VITE_API_URL=http://backend:8000
    container_name: aegisai-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

  # Optional: PostgreSQL for production
  db:
    image: postgres:15-alpine
    container_name: aegisai-db
    environment:
      - POSTGRES_USER=aegis
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=aegisai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Production Docker Configuration

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Security: Run as non-root user
RUN useradd -m -u 1000 aegis && chown -R aegis:aegis /app
USER aegis

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ☁️ Cloud Deployment

### Option 1: Vercel (Frontend) + Render (Backend)

#### **Deploy Frontend to Vercel**

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
cd frontend
vercel --prod

# 3. Set environment variables in Vercel dashboard:
# - VITE_GEMINI_API_KEY
# - VITE_API_URL (your Render backend URL)
# - VITE_DEFAULT_MODEL=gemini-3-flash-preview
```

#### **Deploy Backend to Render**

```bash
# 1. Create render.yaml
cat > render.yaml << EOF
services:
  - type: web
    name: aegisai-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port 8000
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: DEFAULT_MODEL
        value: gemini-3-flash-preview
      - key: ENABLE_MODEL_ESCALATION
        value: true
      - key: MAX_CONTEXT_TOKENS
        value: 500000
      - key: PYTHON_VERSION
        value: 3.11.0
    healthCheckPath: /health
EOF

# 2. Push to GitHub and connect Render
git add render.yaml
git commit -m "Add Render configuration"
git push origin main

# 3. In Render dashboard:
# - Create new Web Service
# - Connect GitHub repo
# - Render auto-detects render.yaml
# - Add GEMINI_API_KEY in environment variables
# - Deploy
```

### Option 2: Google Cloud Platform

#### **Deploy to Cloud Run**

```bash
# 1. Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/aegisai-backend

# 2. Deploy
gcloud run deploy aegisai-backend \
  --image gcr.io/PROJECT_ID/aegisai-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=${GEMINI_API_KEY} \
  --set-env-vars DEFAULT_MODEL=gemini-3-flash-preview \
  --set-env-vars MAX_CONTEXT_TOKENS=500000 \
  --allow-unauthenticated

# 3. Deploy frontend to Firebase Hosting
cd frontend
npm run build
firebase deploy --only hosting
```

### Option 3: AWS

#### **Deploy Backend to ECS Fargate**

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name aegisai-backend

# 2. Build and push image
docker build -t aegisai-backend ./backend
docker tag aegisai-backend:latest ${AWS_ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/aegisai-backend:latest
docker push ${AWS_ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/aegisai-backend:latest

# 3. Create ECS task definition (task-definition.json)
# 4. Create ECS service
# 5. Configure ALB and domain
```

#### **Deploy Frontend to S3 + CloudFront**

```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Upload to S3
aws s3 sync dist/ s3://aegisai-frontend

# 3. Create CloudFront distribution
# 4. Configure custom domain
```

---

## ✅ Production Checklist

### Pre-Deployment

- [ ] **Environment Variables**
  - [ ] All required variables set
  - [ ] Gemini API key valid and tested
  - [ ] No hardcoded secrets in code
  - [ ] Different keys for dev/staging/prod

- [ ] **Gemini 3 Configuration**
  - [ ] Model selection strategy configured
  - [ ] Thinking level defaults set appropriately
  - [ ] Media resolution optimized for use case
  - [ ] Context window limits configured
  - [ ] Thought signature retention set

- [ ] **Security**
  - [ ] CORS configured for production domains only
  - [ ] API key protection enabled (backend)
  - [ ] HTTPS enforced
  - [ ] Rate limiting configured
  - [ ] Input validation in place

- [ ] **Database**
  - [ ] Backup strategy configured
  - [ ] Connection pooling set up
  - [ ] Migration scripts ready
  - [ ] For PostgreSQL: proper indexes created

- [ ] **Testing**
  - [ ] All unit tests passing
  - [ ] Integration tests passing
  - [ ] Load testing completed
  - [ ] Security scanning done

### Post-Deployment

- [ ] **Monitoring**
  - [ ] Health check endpoint responding
  - [ ] Logging configured and working
  - [ ] Error tracking set up (Sentry/etc)
  - [ ] Performance metrics collecting

- [ ] **Verification**
  - [ ] Frontend accessible via HTTPS
  - [ ] Backend API responding correctly
  - [ ] Gemini 3 integration working
  - [ ] Database operations successful
  - [ ] WebSocket connections stable (if used)

- [ ] **Performance**
  - [ ] Response times acceptable (< 3s)
  - [ ] No memory leaks detected
  - [ ] Gemini API rate limits not exceeded
  - [ ] Cost monitoring active

---

## 📊 Monitoring & Maintenance

### Health Checks

```typescript
// Comprehensive health check endpoint
app.get('/health', async (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    components: {
      database: await checkDatabase(),
      gemini_api: await checkGeminiAPI(),
      storage: await checkStorage(),
    },
    metrics: {
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cpu: process.cpuUsage(),
    },
    gemini3: {
      default_model: process.env.DEFAULT_MODEL,
      flash_available: true,
      pro_available: true,
      context_window: '1000000 tokens',
      deep_think_enabled: true
    }
  };

  const isHealthy = Object.values(health.components).every(c => c === 'ok');
  res.status(isHealthy ? 200 : 503).json(health);
});
```

### Performance Monitoring

```typescript
// Track Gemini 3 usage and performance
class GeminiMetricsCollector {
  private metrics = {
    flash_calls: 0,
    pro_calls: 0,
    deep_think_calls: 0,
    total_tokens: 0,
    avg_latency: 0,
    errors: 0,
    escalations: 0  // Flash → Pro upgrades
  };

  recordAnalysis(result: AnalysisMetrics) {
    if (result.model.includes('flash')) this.metrics.flash_calls++;
    if (result.model.includes('pro')) this.metrics.pro_calls++;
    if (result.thinkingLevel === 'high') this.metrics.deep_think_calls++;
    
    this.metrics.total_tokens += result.tokensUsed;
    this.updateLatency(result.duration);
    
    if (result.escalated) this.metrics.escalations++;
  }

  getReport() {
    return {
      ...this.metrics,
      flash_percentage: (this.metrics.flash_calls / this.totalCalls()) * 100,
      avg_tokens_per_call: this.metrics.total_tokens / this.totalCalls(),
      escalation_rate: (this.metrics.escalations / this.metrics.flash_calls) * 100
    };
  }
}
```

### Cost Tracking

```typescript
// Monitor Gemini 3 costs
class CostTracker {
  private readonly FLASH_INPUT_COST = 0.50 / 1_000_000;
  private readonly FLASH_OUTPUT_COST = 3.00 / 1_000_000;
  private readonly PRO_INPUT_COST = 2.00 / 1_000_000;
  private readonly PRO_OUTPUT_COST = 12.00 / 1_000_000;

  calculateCost(analysis: AnalysisResult): number {
    const isFlash = analysis.model.includes('flash');
    const inputCost = isFlash ? this.FLASH_INPUT_COST : this.PRO_INPUT_COST;
    const outputCost = isFlash ? this.FLASH_OUTPUT_COST : this.PRO_OUTPUT_COST;

    return (
      analysis.inputTokens * inputCost +
      analysis.outputTokens * outputCost
    );
  }

  getDailySummary(): CostSummary {
    return {
      total_cost: this.costs.reduce((a, b) => a + b, 0),
      flash_cost: this.flashCosts.reduce((a, b) => a + b, 0),
      pro_cost: this.proCosts.reduce((a, b) => a + b, 0),
      projected_monthly: this.projectMonthlyCost(),
      recommendations: this.getCostOptimizationTips()
    };
  }
}
```

### Logging Best Practices

```python
# backend/config/logging_config.py
import logging
import json

class GeminiAnalysisLogger:
    def __init__(self):
        self.logger = logging.getLogger('aegisai.gemini')
        
    def log_analysis(self, result: AnalysisResult):
        """Log Gemini 3 analysis with structured data"""
        self.logger.info(json.dumps({
            'event': 'gemini_analysis',
            'model': result.model,
            'thinking_level': result.thinkingLevel,
            'media_resolution': result.mediaResolution,
            'incident_detected': result.incident,
            'confidence': result.confidence,
            'tokens_used': result.tokensUsed,
            'duration_ms': result.durationMs,
            'cost': result.estimatedCost,
            'thought_signature_used': result.usedThoughtSignature
        }))
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aegisai-backend
spec:
  replicas: 3  # Scale based on load
  selector:
    matchLabels:
      app: aegisai-backend
  template:
    metadata:
      labels:
        app: aegisai-backend
    spec:
      containers:
      - name: backend
        image: aegisai-backend:latest
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: aegisai-secrets
              key: gemini-api-key
        - name: DEFAULT_MODEL
          value: "gemini-3-flash-preview"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

### Multi-Camera Architecture

```
┌─────────────────────────────────────────┐
│         Load Balancer                    │
└─────────────────────────────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌─────────┐      ┌─────────┐
│ Backend │      │ Backend │
│ Pod 1   │      │ Pod 2   │
└─────────┘      └─────────┘
     │                 │
     └────────┬────────┘
              ▼
     ┌─────────────┐
     │  Gemini 3   │
     │  API Pool   │
     └─────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌─────────┐      ┌─────────┐
│Camera 1 │      │Camera 2 │
│ Stream  │      │ Stream  │
└─────────┘      └─────────┘
```

### Cost Optimization at Scale

```typescript
// Intelligent request batching
class BatchAnalyzer {
  private batch: Frame[] = [];
  private readonly BATCH_SIZE = 10;

  async addFrame(frame: Frame): Promise<void> {
    this.batch.push(frame);

    if (this.batch.length >= this.BATCH_SIZE) {
      await this.processBatch();
    }
  }

  private async processBatch(): Promise<void> {
    // Use Gemini 3 Flash for quick batch screening
    const results = await this.screenWithFlash(this.batch);

    // Escalate only suspicious frames to Pro
    const suspicious = results.filter(r => r.threatLevel > 50);
    
    if (suspicious.length > 0) {
      await this.deepAnalyzeWithPro(suspicious);
    }

    this.batch = [];
  }
}

// Savings: 90%+ cost reduction while maintaining accuracy
```

---

## 🔒 Security Hardening

```bash
# 1. Use secrets management
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name aegisai/gemini-api-key \
  --secret-string ${GEMINI_API_KEY}

# 2. Enable WAF
# Configure rate limiting, geo-blocking, etc.

# 3. Set up VPC (private backend)
# Backend not publicly accessible

# 4. Enable encryption
# - HTTPS only
# - Encrypt data at rest
# - Encrypt database connections

# 5. Regular security updates
docker pull python:3.11-slim  # Latest security patches
npm audit fix  # Frontend dependencies
```

---

## 📚 Additional Resources

- **[Scaling Guide](SCALING.md)** - Multi-camera deployments
- **[Security Guide](SECURITY.md)** - Security best practices
- **[Monitoring Guide](MONITORING.md)** - Observability setup
- **[Cost Optimization](COST_OPTIMIZATION.md)** - Reduce Gemini 3 costs

---

**Deploy AegisAI with confidence!** 🛡️
