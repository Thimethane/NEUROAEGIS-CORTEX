# ⚙️ AegisAI Configuration Guide

**Complete configuration reference for Gemini 3-powered deployments**

---

## 📋 Table of Contents

- [Configuration Files](#configuration-files)
- [Gemini 3 Settings](#gemini-3-settings)
- [Performance Tuning](#performance-tuning)
- [Security Configuration](#security-configuration)
- [Cost Optimization](#cost-optimization)
- [Advanced Features](#advanced-features)

---

## 📁 Configuration Files

### File Structure

```
aegisai/
├── .env                          # Backend environment
├── .env.example                  # Template
├── frontend/
│   ├── .env.local               # Frontend environment
│   └── src/
│       └── constants.ts         # App configuration
├── backend/
│   └── config/
│       ├── settings.py          # Backend settings
│       └── constants.py         # System constants
└── docker-compose.yml           # Docker configuration
```

---

## 🤖 Gemini 3 Settings

### Frontend Configuration

#### **constants.ts** - Primary Configuration

```typescript
// frontend/src/constants.ts

export const GEMINI_CONFIG = {
  // Model Selection Strategy
  DEFAULT_MODEL: 'gemini-3-flash-preview' as const,
  PRO_MODEL: 'gemini-3-pro-preview' as const,
  ENABLE_AUTO_ESCALATION: true,
  
  // Escalation Thresholds
  ESCALATE_TO_PRO_THRESHOLD: 70,      // Threat level > 70 → Use Pro
  USE_DEEP_THINK_THRESHOLD: 80,       // Threat level > 80 → Deep Think
  
  // Context Window Management
  MAX_CONTEXT_TOKENS: 500000,         // Reserve 500K of 1M for history
  MAX_FRAME_HISTORY: 1000,            // ~66 minutes at 4s/frame
  ENABLE_THOUGHT_SIGNATURES: true,    // Multi-turn reasoning
  
  // Thinking Configuration
  DEFAULT_THINKING_LEVEL: 'low' as const,
  ENABLE_THOUGHT_TRANSPARENCY: true,  // Log AI reasoning
  
  // Media Processing
  DEFAULT_MEDIA_RESOLUTION: 'medium' as const,
  AUTO_ADJUST_RESOLUTION: true,       // Based on threat level
  
  // Performance
  TEMPERATURE: 1.0,                   // Gemini 3 optimized
  MAX_OUTPUT_TOKENS: 8192,
};

export const ANALYSIS_CONFIG = {
  // Frame Capture
  ANALYSIS_INTERVAL: 4000,            // 4 seconds between frames
  AUTO_CAPTURE_ENABLED: true,
  
  // Quality Settings
  VIDEO_WIDTH: 1920,
  VIDEO_HEIGHT: 1080,
  JPEG_QUALITY: 0.85,
  
  // Confidence Thresholds
  MIN_CONFIDENCE: 60,                 // Ignore results < 60%
  HIGH_CONFIDENCE: 85,                // Auto-accept > 85%
  
  // Incident Detection
  INCIDENT_TYPES: [
    'violence',
    'weapon',
    'intrusion',
    'suspicious_behavior',
    'loitering',
    'vandalism'
  ] as const,
  
  SEVERITY_LEVELS: {
    critical: { threshold: 90, color: '#DC2626' },
    high: { threshold: 75, color: '#EA580C' },
    medium: { threshold: 50, color: '#F59E0B' },
    low: { threshold: 0, color: '#3B82F6' }
  }
};

export const BACKEND_CONFIG = {
  // API Integration
  ENABLE_BACKEND_API: false,          // Toggle full stack mode
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  API_TIMEOUT: 30000,                 // 30 seconds
  
  // WebSocket
  ENABLE_WEBSOCKET: false,
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  WS_RECONNECT_DELAY: 5000,
};
```

#### **.env.local** - Environment Variables

```bash
# Gemini 3 API Key
VITE_GEMINI_API_KEY=your_gemini_3_api_key_here

# Model Configuration
VITE_DEFAULT_MODEL=gemini-3-flash-preview
VITE_ENABLE_PRO_MODEL=true

# Analysis Settings
VITE_DEFAULT_THINKING_LEVEL=low
VITE_DEFAULT_MEDIA_RESOLUTION=medium
VITE_ANALYSIS_INTERVAL=4000

# Backend Integration (Full Stack Mode)
VITE_ENABLE_BACKEND=false
VITE_API_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_THOUGHT_TRANSPARENCY=true
VITE_ENABLE_AUTO_ESCALATION=true
VITE_ENABLE_DEEP_THINK=true

# Performance
VITE_MAX_FRAME_HISTORY=1000
VITE_MAX_CONTEXT_TOKENS=500000

# Debug
VITE_DEBUG_MODE=false
VITE_LOG_LEVEL=info
```

### Backend Configuration

#### **settings.py** - Backend Settings

```python
# backend/config/settings.py

from pydantic_settings import BaseSettings
from typing import Literal

class GeminiConfig(BaseSettings):
    """Gemini 3 API Configuration"""
    
    # API Key
    GEMINI_API_KEY: str
    
    # Model Selection
    DEFAULT_MODEL: str = "gemini-3-flash-preview"
    FLASH_MODEL: str = "gemini-3-flash-preview"
    PRO_MODEL: str = "gemini-3-pro-preview"
    ENABLE_MODEL_ESCALATION: bool = True
    
    # Escalation Rules
    ESCALATE_TO_PRO_THRESHOLD: int = 70
    USE_DEEP_THINK_THRESHOLD: int = 80
    
    # Context Management
    MAX_CONTEXT_TOKENS: int = 500000
    ENABLE_THOUGHT_SIGNATURES: bool = True
    SIGNATURE_RETENTION_HOURS: int = 24
    
    # Thinking Configuration
    DEFAULT_THINKING_LEVEL: Literal['low', 'high'] = 'low'
    
    # Media Processing
    DEFAULT_MEDIA_RESOLUTION: Literal['low', 'medium', 'high'] = 'medium'
    AUTO_ADJUST_RESOLUTION: bool = True
    
    # Generation Config
    TEMPERATURE: float = 1.0
    MAX_OUTPUT_TOKENS: int = 8192
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class AnalysisConfig(BaseSettings):
    """Analysis & Detection Configuration"""
    
    # Frame Processing
    FRAME_SAMPLE_RATE: int = 2          # Analyze every 2 seconds
    MAX_CONCURRENT_ANALYSES: int = 5
    REQUEST_TIMEOUT: int = 30
    
    # Confidence Thresholds
    MIN_CONFIDENCE_THRESHOLD: int = 60
    HIGH_CONFIDENCE_THRESHOLD: int = 85
    
    # Incident Detection
    INCIDENT_TYPES: list[str] = [
        "violence", "weapon", "intrusion",
        "suspicious_behavior", "loitering", "vandalism"
    ]
    
    # Severity Mapping
    CRITICAL_SEVERITY_THRESHOLD: int = 90
    HIGH_SEVERITY_THRESHOLD: int = 75
    MEDIUM_SEVERITY_THRESHOLD: int = 50


class DatabaseConfig(BaseSettings):
    """Database Configuration"""
    
    DATABASE_URL: str = "sqlite:///./aegis.db"
    # For PostgreSQL: "postgresql://user:pass@localhost:5432/aegis"
    
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30
    ENABLE_QUERY_LOGGING: bool = False


class SecurityConfig(BaseSettings):
    """Security Configuration"""
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # API Protection
    API_KEY_REQUIRED: bool = False
    API_KEY: str | None = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Authentication (for multi-user)
    ENABLE_AUTH: bool = False
    JWT_SECRET: str | None = None
    JWT_EXPIRY_HOURS: int = 24


class PerformanceConfig(BaseSettings):
    """Performance & Optimization"""
    
    # Caching
    ENABLE_RESPONSE_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 300
    
    # Resource Limits
    MAX_MEMORY_MB: int = 1024
    MAX_CPU_PERCENT: int = 80
    
    # Monitoring
    ENABLE_PERFORMANCE_METRICS: bool = True
    METRICS_RETENTION_DAYS: int = 30


class LoggingConfig(BaseSettings):
    """Logging Configuration"""
    
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File Logging
    ENABLE_FILE_LOGGING: bool = True
    LOG_FILE_PATH: str = './logs/aegis.log'
    LOG_FILE_MAX_BYTES: int = 10_000_000  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # Structured Logging
    ENABLE_JSON_LOGGING: bool = False
    
    # External Services
    SENTRY_DSN: str | None = None
    ENABLE_SENTRY: bool = False


# Initialize configurations
gemini_config = GeminiConfig()
analysis_config = AnalysisConfig()
database_config = DatabaseConfig()
security_config = SecurityConfig()
performance_config = PerformanceConfig()
logging_config = LoggingConfig()
```

#### **.env** - Backend Environment

```bash
# Gemini 3 Configuration
GEMINI_API_KEY=your_gemini_3_api_key_here
DEFAULT_MODEL=gemini-3-flash-preview
FLASH_MODEL=gemini-3-flash-preview
PRO_MODEL=gemini-3-pro-preview

# Model Behavior
ENABLE_MODEL_ESCALATION=true
ESCALATE_TO_PRO_THRESHOLD=70
USE_DEEP_THINK_THRESHOLD=80

# Context & Memory
MAX_CONTEXT_TOKENS=500000
ENABLE_THOUGHT_SIGNATURES=true
SIGNATURE_RETENTION_HOURS=24

# Analysis Settings
DEFAULT_THINKING_LEVEL=low
DEFAULT_MEDIA_RESOLUTION=medium
AUTO_ADJUST_RESOLUTION=true
TEMPERATURE=1.0
MAX_OUTPUT_TOKENS=8192

# Database
DATABASE_URL=sqlite:///./aegis.db
# Or PostgreSQL: postgresql://user:pass@host:5432/aegis

# Security
CORS_ORIGINS=["http://localhost:3000"]
API_KEY_REQUIRED=false
# API_KEY=your_secure_api_key_here

# Performance
FRAME_SAMPLE_RATE=2
MAX_CONCURRENT_ANALYSES=5
REQUEST_TIMEOUT=30
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
LOG_FILE_PATH=./logs/aegis.log
ENABLE_JSON_LOGGING=false

# Optional: External Services
# SENTRY_DSN=your_sentry_dsn_here
# ENABLE_SENTRY=false
```

---

## 🎯 Performance Tuning

### Cost vs Performance Profiles

#### **Profile 1: Economy Mode**
```typescript
// Optimize for cost (95% savings)
export const ECONOMY_CONFIG = {
  DEFAULT_MODEL: 'gemini-3-flash-preview',
  DEFAULT_THINKING_LEVEL: 'low',
  DEFAULT_MEDIA_RESOLUTION: 'low',
  ANALYSIS_INTERVAL: 8000,              // 8 seconds
  ENABLE_AUTO_ESCALATION: false,
  MAX_FRAME_HISTORY: 100,
};
// Cost: ~$0.05/hour | Accuracy: ~85%
```

#### **Profile 2: Balanced Mode** (Recommended)
```typescript
// Balance cost and accuracy
export const BALANCED_CONFIG = {
  DEFAULT_MODEL: 'gemini-3-flash-preview',
  DEFAULT_THINKING_LEVEL: 'low',
  DEFAULT_MEDIA_RESOLUTION: 'medium',
  ANALYSIS_INTERVAL: 4000,              // 4 seconds
  ENABLE_AUTO_ESCALATION: true,
  ESCALATE_TO_PRO_THRESHOLD: 70,
  MAX_FRAME_HISTORY: 500,
};
// Cost: ~$0.20/hour | Accuracy: ~92%
```

#### **Profile 3: Premium Mode**
```typescript
// Optimize for accuracy
export const PREMIUM_CONFIG = {
  DEFAULT_MODEL: 'gemini-3-pro-preview',
  DEFAULT_THINKING_LEVEL: 'low',
  DEFAULT_MEDIA_RESOLUTION: 'high',
  ANALYSIS_INTERVAL: 2000,              // 2 seconds
  ENABLE_AUTO_ESCALATION: true,
  USE_DEEP_THINK_THRESHOLD: 70,
  MAX_FRAME_HISTORY: 1000,
};
// Cost: ~$2.50/hour | Accuracy: ~96%
```

#### **Profile 4: Critical Infrastructure**
```typescript
// Maximum security
export const CRITICAL_CONFIG = {
  DEFAULT_MODEL: 'gemini-3-pro-preview',
  DEFAULT_THINKING_LEVEL: 'high',       // Always Deep Think
  DEFAULT_MEDIA_RESOLUTION: 'high',
  ANALYSIS_INTERVAL: 2000,
  ENABLE_THOUGHT_TRANSPARENCY: true,
  ENABLE_AUTO_ESCALATION: false,        // Always use Pro
  MAX_FRAME_HISTORY: 2000,
};
// Cost: ~$5.00/hour | Accuracy: ~98%
```

### Apply Profile

```typescript
// frontend/src/constants.ts

import { BALANCED_CONFIG } from './profiles';

export const CONFIG = {
  ...BALANCED_CONFIG,
  // Override specific settings if needed
  ANALYSIS_INTERVAL: 3000,
};
```

---

## 🔒 Security Configuration

### API Key Protection

```typescript
// ✅ SECURE (Backend mode)
export const CONFIG = {
  ENABLE_BACKEND_API: true,
  // Key stored server-side only
};

// ❌ INSECURE (Frontend-only mode)
export const CONFIG = {
  ENABLE_BACKEND_API: false,
  // Key exposed in browser
};
```

### CORS Configuration

```python
# backend/config/settings.py

# Development
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# Production
CORS_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com",
]
```

### Rate Limiting

```python
# Per-endpoint rate limits
RATE_LIMITS = {
    "/api/analyze": "10/minute",        # Analysis endpoint
    "/api/incidents": "60/minute",      # Read operations
    "/health": "unlimited",             # Health checks
}
```

---

## 💰 Cost Optimization

### Adaptive Model Selection

```typescript
// Automatically choose cheapest model that meets requirements
class CostOptimizer {
  selectOptimalConfig(context: {
    threatLevel: number;
    budget: number;
    latencyTarget: number;
  }): ModelConfig {
    
    // Critical threat → Always use Pro
    if (context.threatLevel > 80) {
      return this.getProConfig('high');
    }
    
    // Budget constrained → Flash only
    if (context.budget < 0.001) {
      return this.getFlashConfig('low');
    }
    
    // Low latency required → Flash
    if (context.latencyTarget < 2000) {
      return this.getFlashConfig('low');
    }
    
    // Suspicious → Pro without Deep Think
    if (context.threatLevel > 50) {
      return this.getProConfig('low');
    }
    
    // Default → Flash
    return this.getFlashConfig('low');
  }
  
  private getFlashConfig(thinking: 'low' | 'high'): ModelConfig {
    return {
      model: 'gemini-3-flash-preview',
      thinkingLevel: thinking,
      mediaResolution: thinking === 'high' ? 'high' : 'medium',
      estimatedCost: thinking === 'high' ? 0.0012 : 0.0004
    };
  }
  
  private getProConfig(thinking: 'low' | 'high'): ModelConfig {
    return {
      model: 'gemini-3-pro-preview',
      thinkingLevel: thinking,
      mediaResolution: 'high',
      estimatedCost: thinking === 'high' ? 0.0048 : 0.0024
    };
  }
}
```

### Token Budget Management

```typescript
// Limit context size to control costs
export const CONTEXT_CONFIG = {
  MAX_CONTEXT_TOKENS: 500000,           // Half of 1M window
  
  // Dynamic context sizing
  getContextBudget: (threatLevel: number) => {
    if (threatLevel > 80) return 500000;  // Full context
    if (threatLevel > 50) return 250000;  // Half context
    return 100000;                        // Minimal context
  },
  
  // Prune strategy
  PRUNE_OLDEST_FRAMES: true,
  KEEP_INCIDENT_FRAMES: true,           // Never prune incidents
};
```

---

## 🚀 Advanced Features

### Multi-Turn Investigation

```typescript
// Enable thought signatures for investigations
export const INVESTIGATION_CONFIG = {
  ENABLE_THOUGHT_SIGNATURES: true,
  SIGNATURE_RETENTION_HOURS: 24,
  
  // Investigation modes
  QUICK_INVESTIGATION: {
    max_turns: 3,
    thinkingLevel: 'low',
  },
  
  DEEP_INVESTIGATION: {
    max_turns: 10,
    thinkingLevel: 'high',
    mediaResolution: 'high',
  },
};
```

### Subject Tracking

```typescript
// Configure subject tracking across frames
export const TRACKING_CONFIG = {
  ENABLE_SUBJECT_TRACKING: true,
  SUBJECT_ID_RETENTION: 1000,           // Frames
  
  // Matching thresholds
  APPEARANCE_MATCH_THRESHOLD: 0.85,
  BEHAVIOR_MATCH_THRESHOLD: 0.75,
  
  // Context window for tracking
  TRACKING_CONTEXT_FRAMES: 100,
};
```

### Custom Prompts

```typescript
// Override default system instruction
export const PROMPT_CONFIG = {
  SYSTEM_INSTRUCTION: `You are an expert security analyst...`,
  
  // Specialized prompts
  AIRPORT_SECURITY_PROMPT: `Focus on aviation-specific threats...`,
  RETAIL_SECURITY_PROMPT: `Prioritize shoplifting detection...`,
  WORKPLACE_SECURITY_PROMPT: `Monitor for workplace violence...`,
  
  // Use custom prompt
  USE_CUSTOM_PROMPT: false,
  CUSTOM_PROMPT_NAME: 'AIRPORT_SECURITY_PROMPT',
};
```

---

## 🧪 Testing Configuration

```typescript
// frontend/src/config/test.config.ts

export const TEST_CONFIG = {
  // Use lower cost settings for testing
  DEFAULT_MODEL: 'gemini-3-flash-preview',
  DEFAULT_THINKING_LEVEL: 'low',
  ANALYSIS_INTERVAL: 10000,             // 10 seconds
  
  // Mock responses for unit tests
  ENABLE_MOCK_RESPONSES: true,
  
  // Test data
  MOCK_INCIDENT_PROBABILITY: 0.2,       // 20% incident rate
};
```

---

## 📚 Configuration Examples

### Example 1: Airport Security

```typescript
export const AIRPORT_CONFIG = {
  // High accuracy required
  DEFAULT_MODEL: 'gemini-3-pro-preview',
  DEFAULT_THINKING_LEVEL: 'low',
  DEFAULT_MEDIA_RESOLUTION: 'high',
  
  // Frequent analysis
  ANALYSIS_INTERVAL: 2000,
  
  // Low false positive tolerance
  MIN_CONFIDENCE: 80,
  ESCALATE_TO_PRO_THRESHOLD: 60,
  USE_DEEP_THINK_THRESHOLD: 70,
  
  // Extended context
  MAX_FRAME_HISTORY: 2000,
  MAX_CONTEXT_TOKENS: 800000,
  
  // Specialized prompt
  CUSTOM_PROMPT: 'AIRPORT_SECURITY_PROMPT',
};
```

### Example 2: Retail Store

```typescript
export const RETAIL_CONFIG = {
  // Balance cost and accuracy
  DEFAULT_MODEL: 'gemini-3-flash-preview',
  DEFAULT_THINKING_LEVEL: 'low',
  DEFAULT_MEDIA_RESOLUTION: 'medium',
  
  // Standard monitoring
  ANALYSIS_INTERVAL: 4000,
  
  // Shoplifting-specific
  INCIDENT_TYPES: [
    'shoplifting_suspected',
    'concealment_behavior',
    'tag_removal',
    'suspicious_behavior'
  ],
  
  // Moderate context
  MAX_FRAME_HISTORY: 500,
  
  // Cost optimization
  ENABLE_AUTO_ESCALATION: true,
  ESCALATE_TO_PRO_THRESHOLD: 75,
};
```

### Example 3: Parking Lot

```typescript
export const PARKING_CONFIG = {
  // Optimize for cost
  DEFAULT_MODEL: 'gemini-3-flash-preview',
  DEFAULT_THINKING_LEVEL: 'low',
  DEFAULT_MEDIA_RESOLUTION: 'low',
  
  // Less frequent
  ANALYSIS_INTERVAL: 8000,
  
  // Vehicle-specific
  INCIDENT_TYPES: [
    'vandalism',
    'break_in',
    'loitering',
    'suspicious_behavior'
  ],
  
  // Minimal context
  MAX_FRAME_HISTORY: 200,
  
  // Cost efficient
  ENABLE_AUTO_ESCALATION: false,
};
```

---

## ✅ Configuration Validation

```typescript
// Validate configuration at startup
export function validateConfig(config: typeof CONFIG): void {
  // Model validation
  const validModels = ['gemini-3-flash-preview', 'gemini-3-pro-preview'];
  if (!validModels.includes(config.DEFAULT_MODEL)) {
    throw new Error(`Invalid model: ${config.DEFAULT_MODEL}`);
  }
  
  // Thinking level
  if (!['low', 'high'].includes(config.DEFAULT_THINKING_LEVEL)) {
    throw new Error(`Invalid thinking level: ${config.DEFAULT_THINKING_LEVEL}`);
  }
  
  // Resolution
  if (!['low', 'medium', 'high'].includes(config.DEFAULT_MEDIA_RESOLUTION)) {
    throw new Error(`Invalid resolution: ${config.DEFAULT_MEDIA_RESOLUTION}`);
  }
  
  // Thresholds
  if (config.ESCALATE_TO_PRO_THRESHOLD < 0 || config.ESCALATE_TO_PRO_THRESHOLD > 100) {
    throw new Error('Escalation threshold must be 0-100');
  }
  
  // Temperature (must be 1.0 for Gemini 3)
  if (config.TEMPERATURE !== 1.0) {
    console.warn('⚠️  Gemini 3 is optimized for temperature=1.0');
  }
}
```

---

**Configure AegisAI for optimal performance!** ⚙️
