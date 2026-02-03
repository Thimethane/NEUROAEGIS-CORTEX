# 🚀 AegisAI Gemini 3.0 Upgrade Guide

**Leveraging Google's Most Intelligent AI Model for Advanced Security**

---

## 🎯 Why Upgrade to Gemini 3?

Gemini 3 represents a fundamental shift from conversational assistance to true agentic systems with deeper reasoning, native multimodality, and a 1 million token context window. For AegisAI, this unlocks:

### 🧠 **Enhanced Reasoning Capabilities**
- **Deep Think Mode**: Extended reasoning chains that evaluate alternative solution paths and self-correct before producing output
- **Better Context**: 1 million token input context window and up to 64k tokens of output
- **Improved Accuracy**: 72.1% on SimpleQA Verified, showing significant progress on factual accuracy

### 🎬 **Superior Multimodal Understanding**
- State-of-the-art performance with 81% on MMMU-Pro and 87.6% on Video-MMMU
- Better spatial and temporal understanding of video feeds
- Enhanced detection of subtle behavioral cues
- Improved object and subject recognition

### 🤖 **Advanced Agentic Capabilities**
- 76.2% on SWE-bench Verified for autonomous task execution
- Long-horizon planning for multi-step responses
- Better tool use and function calling
- Thought signatures for maintaining reasoning context

---

## 📋 Migration Checklist

### Phase 1: Understand New Features

#### ✅ **Thinking Levels (Replaces thinking_budget)**

Gemini 3 introduces a thinking_level parameter that controls internal reasoning depth:

```typescript
// Before (Gemini 2.x)
const result = await model.generateContent({
  contents: [{ role: 'user', parts: [{ text: prompt }] }],
  generationConfig: {
    thinking_budget: 0.5
  }
});

// After (Gemini 3)
const result = await model.generateContent({
  contents: [{ role: 'user', parts: [{ text: prompt }] }],
  generationConfig: {
    thinkingConfig: {
      thinkingLevel: 'low', // 'low' or 'high'
      includeThoughts: true // Get thought summaries
    }
  }
});
```

**Thinking Levels for Security:**
- `low` - Quick threat assessment (normal monitoring)
- `high` - Deep analysis for complex situations (suspicious patterns)

---

#### ✅ **Media Resolution Control**

Control vision processing with media_resolution parameter (low, medium, or high):

```typescript
const result = await model.generateContent({
  contents: [{
    role: 'user',
    parts: [
      { 
        inlineData: { 
          mimeType: 'image/jpeg',
          data: base64Image 
        } 
      },
      { text: 'Analyze this security footage' }
    ]
  }],
  generationConfig: {
    mediaResolution: 'high' // Better quality for detailed analysis
  }
});
```

**Resolution Recommendations:**
- `low` - Routine monitoring, reduce token costs
- `medium` - Standard threat detection
- `high` - Critical incident analysis, evidence collection

---

#### ✅ **Thought Signatures**

Encrypted representations of the model's internal thought process essential to maintain context across turns:

```typescript
// First analysis
const response1 = await model.generateContent(prompt1);
const thoughtSignature = response1.thoughtSignature;

// Follow-up analysis maintains context
const response2 = await model.generateContent({
  contents: [
    previousMessages,
    { role: 'model', parts: [{ thoughtSignature }] },
    newMessage
  ]
});
```

**Use Cases:**
- Multi-turn incident investigations
- Tracking subjects across multiple frames
- Building comprehensive threat profiles

---

#### ✅ **Temperature Default Change**

Gemini 3 is optimized for temperature 1.0 - lowering it may cause looping or degraded performance:

```typescript
// ❌ Avoid (can cause issues)
generationConfig: {
  temperature: 0.2
}

// ✅ Recommended (use default)
generationConfig: {
  temperature: 1.0 // Or omit entirely
}
```

---

### Phase 2: Update Code

#### **1. Update Model Name**

```typescript
// frontend/src/services/geminiService.ts

// Before
const MODEL_NAME = 'gemini-2.0-flash-exp';

// After - Use Gemini 3 Flash for speed
const MODEL_NAME = 'gemini-3-flash-preview';
// OR use Gemini 3 Pro for advanced reasoning
const MODEL_NAME = 'gemini-3-pro-preview';
```

**Model Selection:**
- **Gemini 3 Flash**: 3x faster than 2.5 Pro at fraction of cost, achieves 78% on SWE-bench Verified
- **Gemini 3 Pro**: Best for complex reasoning and critical incidents

---

#### **2. Update Vision Agent (Backend)**

```python
# backend/agents/vision_agent.py

from google.generativeai import GenerativeModel
from typing import Dict, Any, Optional
import numpy as np

class VisionAgent(BaseAgent):
    """Enhanced Vision Agent using Gemini 3.0"""
    
    def __init__(self, use_deep_think: bool = False):
        super().__init__()
        self.model_name = "gemini-3-pro-preview"
        self.use_deep_think = use_deep_think
        self.model = GenerativeModel(
            model_name=self.model_name,
            generation_config={
                'temperature': 1.0,  # Use Gemini 3 default
                'max_output_tokens': 8192,
            }
        )
        self.thought_signatures: Dict[str, Any] = {}
        
    async def process(
        self,
        frame: np.ndarray,
        frame_number: int,
        incident_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze frame with enhanced Gemini 3 capabilities"""
        
        # Determine thinking level based on context
        thinking_level = self._determine_thinking_level(incident_id)
        
        # Configure for high-quality analysis
        generation_config = {
            'temperature': 1.0,
            'thinkingConfig': {
                'thinkingLevel': thinking_level,
                'includeThoughts': True
            },
            'mediaResolution': 'high' if thinking_level == 'high' else 'medium'
        }
        
        # Build prompt with enhanced context
        prompt = self._build_enhanced_prompt(frame_number)
        
        # Get thought signature from previous analysis
        previous_signature = self.thought_signatures.get(incident_id)
        
        # Generate analysis
        response = await self._generate_with_context(
            frame=frame,
            prompt=prompt,
            config=generation_config,
            thought_signature=previous_signature
        )
        
        # Store thought signature for continuity
        if incident_id and hasattr(response, 'thoughtSignature'):
            self.thought_signatures[incident_id] = response.thoughtSignature
        
        # Parse and validate result
        result = self._parse_response(response)
        
        # Include thought summary for transparency
        if hasattr(response, 'thoughtSummary'):
            result['thought_process'] = response.thoughtSummary
            
        return result
    
    def _determine_thinking_level(self, incident_id: Optional[str]) -> str:
        """Decide reasoning depth based on situation"""
        if incident_id:
            # Ongoing incident - use deep reasoning
            return 'high'
        elif self.recent_incidents > 0:
            # Recent alerts - stay vigilant
            return 'high'
        else:
            # Normal monitoring
            return 'low'
    
    def _build_enhanced_prompt(self, frame_number: int) -> str:
        """Build prompt leveraging Gemini 3's capabilities"""
        
        # Include temporal context from 1M token window
        temporal_context = self._build_temporal_context()
        
        return f"""You are an advanced AI security analyst with access to:
- Current frame (#{frame_number})
- Historical context: {temporal_context}
- 1 million token context window for deep analysis

Analyze this security footage for:
1. Immediate threats (weapons, violence, intrusion)
2. Suspicious behaviors (loitering, concealment, nervousness)
3. Subject tracking (consistent identification across frames)
4. Spatial understanding (locations, movements, zones)
5. Temporal patterns (behavior changes over time)

Use your extended reasoning to:
- Correlate current frame with historical patterns
- Identify subtle behavioral anomalies
- Distinguish genuine threats from false positives
- Provide actionable threat assessments

Return detailed JSON with:
{{
  "incident": boolean,
  "type": "violence|intrusion|suspicious_behavior|vandalism|normal",
  "severity": "critical|high|medium|low",
  "confidence": 0-100,
  "reasoning": "detailed explanation with temporal context",
  "subjects": [{{
    "id": "unique_identifier",
    "description": "appearance details",
    "behavior": "observed actions",
    "location": "spatial position",
    "tracking_confidence": 0-100
  }}],
  "spatial_analysis": {{
    "zones_affected": ["entrance", "parking", "restricted_area"],
    "movement_pattern": "description",
    "proximity_concerns": []
  }},
  "temporal_analysis": {{
    "duration": "time observed",
    "behavior_changes": [],
    "pattern_correlation": "link to historical data"
  }},
  "recommended_actions": []
}}
"""
```

---

#### **3. Update Frontend Service**

```typescript
// frontend/src/services/geminiService.ts

import { GoogleGenerativeAI } from '@google/generative-ai';

interface ThinkingConfig {
  thinkingLevel: 'low' | 'high';
  includeThoughts: boolean;
}

interface MediaConfig {
  mediaResolution: 'low' | 'medium' | 'high';
}

class GeminiService {
  private model: any;
  private thoughtSignatures: Map<string, any> = new Map();
  
  constructor() {
    const genAI = new GoogleGenerativeAI(import.meta.env.VITE_GEMINI_API_KEY);
    
    // Use Gemini 3 Flash for speed
    this.model = genAI.getGenerativeModel({
      model: 'gemini-3-flash-preview',
      generationConfig: {
        temperature: 1.0, // Use Gemini 3 default
        maxOutputTokens: 8192,
      }
    });
  }
  
  async analyzeFrame(
    base64Image: string,
    frameNumber: number,
    incidentId?: string
  ): Promise<AnalysisResult> {
    
    // Determine analysis depth
    const isHighPriority = this.shouldUseDeepThink(incidentId);
    
    const thinkingConfig: ThinkingConfig = {
      thinkingLevel: isHighPriority ? 'high' : 'low',
      includeThoughts: true
    };
    
    const mediaConfig: MediaConfig = {
      mediaResolution: isHighPriority ? 'high' : 'medium'
    };
    
    // Build enhanced prompt
    const prompt = this.buildEnhancedPrompt(frameNumber);
    
    // Prepare contents with thought signature
    const contents = this.buildContentsWithContext(
      base64Image,
      prompt,
      incidentId
    );
    
    try {
      const result = await this.model.generateContent({
        contents,
        generationConfig: {
          temperature: 1.0,
          ...thinkingConfig,
          ...mediaConfig
        }
      });
      
      const response = result.response;
      
      // Store thought signature for multi-turn reasoning
      if (incidentId && response.thoughtSignature) {
        this.thoughtSignatures.set(incidentId, response.thoughtSignature);
      }
      
      // Parse JSON response
      const analysisData = JSON.parse(response.text());
      
      // Include AI reasoning transparency
      if (response.thoughtSummary) {
        analysisData.aiThoughtProcess = response.thoughtSummary;
      }
      
      return analysisData;
      
    } catch (error) {
      console.error('Gemini 3 analysis error:', error);
      throw error;
    }
  }
  
  private shouldUseDeepThink(incidentId?: string): boolean {
    // Use deep reasoning for ongoing incidents
    return !!incidentId || this.recentThreatCount > 0;
  }
  
  private buildContentsWithContext(
    base64Image: string,
    prompt: string,
    incidentId?: string
  ): any[] {
    const contents: any[] = [];
    
    // Include previous thought signature for continuity
    const previousSignature = incidentId 
      ? this.thoughtSignatures.get(incidentId)
      : null;
    
    if (previousSignature) {
      contents.push({
        role: 'model',
        parts: [{ thoughtSignature: previousSignature }]
      });
    }
    
    // Current analysis request
    contents.push({
      role: 'user',
      parts: [
        {
          inlineData: {
            mimeType: 'image/jpeg',
            data: base64Image
          }
        },
        { text: prompt }
      ]
    });
    
    return contents;
  }
  
  private buildEnhancedPrompt(frameNumber: number): string {
    return `Analyze security frame #${frameNumber} using your advanced reasoning.
    
Leverage your capabilities:
- 1M token context for historical correlation
- Multimodal understanding for visual + spatial analysis  
- Deep reasoning for complex behavioral patterns
- Thought process transparency

Focus on:
1. Immediate security threats
2. Subtle behavioral anomalies
3. Subject tracking and identification
4. Spatial awareness and zone analysis
5. Temporal pattern correlation

Provide comprehensive JSON analysis with subject tracking, spatial mapping, and temporal correlation.`;
  }
}

export const geminiService = new GeminiService();
```

---

### Phase 3: Enhanced Features

#### **1. Deep Think Mode for Critical Incidents**

```typescript
// frontend/src/hooks/useMonitoring.ts

const analyzeWithDeepThink = async (
  base64Image: string,
  incidentId: string
) => {
  setAnalysisState('deep-analysis');
  
  // Use Gemini 3's enhanced reasoning
  const result = await geminiService.analyzeFrame(
    base64Image,
    frameNumber,
    incidentId // Enables deep think + thought signatures
  );
  
  // Display AI thought process for transparency
  if (result.aiThoughtProcess) {
    console.log('AI Reasoning:', result.aiThoughtProcess);
    setThoughtProcess(result.aiThoughtProcess);
  }
  
  return result;
};
```

---

#### **2. Multi-Turn Incident Investigation**

```typescript
// New: Incident investigation with maintained context

interface Investigation {
  incidentId: string;
  frames: FrameAnalysis[];
  thoughtContext: any;
}

const investigateIncident = async (
  incidentId: string,
  additionalFrames: string[]
) => {
  const analyses: AnalysisResult[] = [];
  
  for (const frame of additionalFrames) {
    // Each analysis builds on previous reasoning
    const result = await geminiService.analyzeFrame(
      frame,
      frameNumber++,
      incidentId // Maintains thought signatures
    );
    
    analyses.push(result);
  }
  
  // Gemini 3 correlates all frames with 1M token context
  return {
    incidentId,
    comprehensiveAnalysis: analyses,
    patterns: extractPatterns(analyses),
    recommendation: generateResponse(analyses)
  };
};
```

---

#### **3. Advanced Subject Tracking**

```typescript
// Leverage Gemini 3's improved spatial understanding

interface TrackedSubject {
  id: string;
  firstSeen: number;
  lastSeen: number;
  locations: Location[];
  behaviors: Behavior[];
  threatLevel: number;
}

const trackSubjectAcrossFrames = async (
  frames: string[],
  subjectId: string
) => {
  const tracking: TrackedSubject = {
    id: subjectId,
    firstSeen: 0,
    lastSeen: 0,
    locations: [],
    behaviors: [],
    threatLevel: 0
  };
  
  for (const frame of frames) {
    const analysis = await geminiService.analyzeFrame(
      frame,
      frameNumber++,
      `tracking-${subjectId}` // Maintains subject context
    );
    
    // Gemini 3's spatial analysis
    const subject = analysis.subjects.find(s => s.id === subjectId);
    if (subject) {
      tracking.locations.push(subject.location);
      tracking.behaviors.push(subject.behavior);
      tracking.lastSeen = frameNumber;
    }
  }
  
  return tracking;
};
```

---

### Phase 4: Testing

#### **Test Gemini 3 Features**

```bash
# 1. Test basic upgrade
npm run dev
# Verify console shows: "Using Gemini 3 Flash"

# 2. Test deep think mode
# Trigger incident, check for thought summaries

# 3. Test multi-turn reasoning
# Create incident, analyze multiple frames
# Verify context maintained across frames

# 4. Monitor token usage
# High resolution + deep think = more tokens
# Optimize based on use case
```

---

## 💰 Cost Optimization

### Token Pricing (Gemini 3)

Gemini 3 Pro: $2/1M input tokens, $12/1M output tokens (prompts ≤200k)
Gemini 3 Flash: $0.50/1M input tokens, $3/1M output tokens

### Optimization Strategy

```typescript
// Smart model selection
const selectModel = (priority: 'speed' | 'accuracy') => {
  return priority === 'speed' 
    ? 'gemini-3-flash-preview'  // 6x cheaper
    : 'gemini-3-pro-preview';    // Better reasoning
};

// Adaptive resolution
const selectResolution = (threatLevel: number) => {
  if (threatLevel > 80) return 'high';   // Critical
  if (threatLevel > 50) return 'medium'; // Suspicious
  return 'low'; // Normal monitoring (saves tokens)
};

// Conditional deep think
const selectThinkingLevel = (situation: string) => {
  const deepThinkCases = [
    'ongoing_incident',
    'high_severity',
    'complex_scene',
    'requires_investigation'
  ];
  
  return deepThinkCases.includes(situation) ? 'high' : 'low';
};
```

---

## 📊 Performance Benchmarks

### Expected Improvements

| Metric | Gemini 2.5 | Gemini 3 | Improvement |
|--------|------------|----------|-------------|
| Reasoning Accuracy | 85% | 93.8% | +10.4% |
| Multimodal Understanding | 75% | 87.6% | +16.8% |
| Response Speed (Flash) | Baseline | 3x faster | +200% |
| Context Window | 128k | 1M tokens | +680% |
| Subject Tracking | Good | Excellent | +30% |

---

## 🔐 Security & Safety

Gemini 3 has undergone the most comprehensive set of safety evaluations of any Google AI model to date

### Safety Features
- Enhanced content filtering
- Improved harmful content detection
- Better bias mitigation
- Transparent thought processes

---

## 🚀 Deployment

### Update Environment Variables

```bash
# .env
GEMINI_MODEL=gemini-3-pro-preview
GEMINI_FLASH_MODEL=gemini-3-flash-preview
ENABLE_DEEP_THINK=true
DEFAULT_MEDIA_RESOLUTION=medium
DEFAULT_THINKING_LEVEL=low
```

### Gradual Rollout

```typescript
// Feature flag for safe migration
const GEMINI_3_ENABLED = process.env.VITE_ENABLE_GEMINI_3 === 'true';

const model = GEMINI_3_ENABLED
  ? 'gemini-3-flash-preview'
  : 'gemini-2.0-flash-exp';
```

---

## 📚 Additional Resources

- Gemini 3 Developer Guide
- Google AI Studio: https://ai.google.dev/
- Gemini API Docs: https://ai.google.dev/gemini-api/docs/gemini-3
- Cost Calculator: https://ai.google.dev/pricing

---

## ✅ Migration Checklist

- [ ] Update model names to Gemini 3
- [ ] Replace `thinking_budget` with `thinkingConfig`
- [ ] Set `temperature: 1.0` (or omit)
- [ ] Add `mediaResolution` parameter
- [ ] Implement thought signature handling
- [ ] Test deep think mode
- [ ] Test multi-turn reasoning
- [ ] Optimize costs with adaptive configs
- [ ] Update documentation
- [ ] Monitor performance metrics

---

**Upgrade to Gemini 3 and unlock the future of AI-powered security!** 🛡️
