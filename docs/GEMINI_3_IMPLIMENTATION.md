# 🔧 Gemini 3 Implementation Guide

**Complete technical reference for implementing Gemini 3 features in AegisAI**

---

## 📋 Table of Contents

- [Core Concepts](#core-concepts)
- [Model Selection](#model-selection)
- [Thinking Levels](#thinking-levels)
- [Media Resolution](#media-resolution)
- [Thought Signatures](#thought-signatures)
- [Advanced Patterns](#advanced-patterns)
- [Best Practices](#best-practices)
- [Performance Optimization](#performance-optimization)

---

## 🎯 Core Concepts

### Gemini 3 Architecture

```typescript
// The Gemini 3 request lifecycle

1. Configure Model
   ├─ Select variant (Flash vs Pro)
   ├─ Set thinking level (low vs high)
   ├─ Set media resolution (low/medium/high)
   └─ Configure temperature (always 1.0)

2. Build Context
   ├─ Current frame/input
   ├─ System instruction
   ├─ Previous thought signatures (if multi-turn)
   └─ Historical context (within 1M token limit)

3. Generate Response
   ├─ Gemini 3 processes with extended reasoning
   ├─ Returns response + thought signature
   └─ Optional: thought summary (if includeThoughts=true)

4. Extract Results
   ├─ Parse JSON response
   ├─ Store thought signature for next turn
   ├─ Log thought summary for transparency
   └─ Update application state
```

---

## 🤖 Model Selection

### When to Use Each Model

```typescript
interface ModelSelector {
  selectModel(context: AnalysisContext): ModelConfig;
}

class SmartModelSelector implements ModelSelector {
  selectModel(context: AnalysisContext): ModelConfig {
    const {
      threatLevel,
      isOngoingIncident,
      requiresInvestigation,
      budget,
      latencyRequirement
    } = context;

    // Critical: Use Pro with Deep Think
    if (threatLevel > 80 || isOngoingIncident) {
      return {
        model: 'gemini-3-pro-preview',
        thinkingLevel: 'high',
        mediaResolution: 'high',
        rationale: 'Critical incident requires deep reasoning'
      };
    }

    // Suspicious: Use Pro with standard thinking
    if (threatLevel > 50 || requiresInvestigation) {
      return {
        model: 'gemini-3-pro-preview',
        thinkingLevel: 'low',
        mediaResolution: 'high',
        rationale: 'Elevated threat needs accurate analysis'
      };
    }

    // Budget priority: Use Flash
    if (budget === 'optimized') {
      return {
        model: 'gemini-3-flash-preview',
        thinkingLevel: 'low',
        mediaResolution: 'medium',
        rationale: 'Cost-optimized routine monitoring'
      };
    }

    // Speed priority: Use Flash
    if (latencyRequirement === 'low') {
      return {
        model: 'gemini-3-flash-preview',
        thinkingLevel: 'low',
        mediaResolution: 'medium',
        rationale: 'Low latency required'
      };
    }

    // Default: Flash for routine monitoring
    return {
      model: 'gemini-3-flash-preview',
      thinkingLevel: 'low',
      mediaResolution: 'medium',
      rationale: 'Standard monitoring configuration'
    };
  }
}

// Usage
const selector = new SmartModelSelector();
const config = selector.selectModel({
  threatLevel: 65,
  isOngoingIncident: false,
  requiresInvestigation: true,
  budget: 'balanced',
  latencyRequirement: 'medium'
});

console.log(config);
// { model: 'gemini-3-pro-preview', thinkingLevel: 'low', ... }
```

### Model Comparison Table

| Feature | Gemini 3 Flash | Gemini 3 Pro |
|---------|----------------|--------------|
| **Speed** | 3x faster | Baseline |
| **Cost (Input)** | $0.50/1M | $2/1M |
| **Cost (Output)** | $3/1M | $12/1M |
| **SWE-bench** | 78% | 76.2% |
| **Reasoning Depth** | Good | Excellent |
| **Best For** | High-frequency, cost-sensitive | Complex analysis, critical incidents |

---

## 🧠 Thinking Levels

### Understanding Thinking Levels

```typescript
interface ThinkingConfig {
  thinkingLevel: 'low' | 'high';
  includeThoughts: boolean;
}

// Low Thinking Level
// - Fast responses (~1-2s)
// - Suitable for routine analysis
// - Lower token consumption
// - Similar to "System 1" thinking

const lowThinkingConfig: ThinkingConfig = {
  thinkingLevel: 'low',
  includeThoughts: false
};

// High Thinking Level (Deep Think)
// - Extended reasoning (~3-10s)
// - Evaluates alternative scenarios
// - Self-correction before output
// - Higher accuracy on complex problems
// - Similar to "System 2" thinking

const highThinkingConfig: ThinkingConfig = {
  thinkingLevel: 'high',
  includeThoughts: true  // Get reasoning transparency
};
```

### Implementation Example

```typescript
class ThinkingLevelManager {
  private incidentHistory: Map<string, number> = new Map();

  determineThinkingLevel(context: {
    frameNumber: number;
    previousIncidents: number;
    sceneComplexity: 'simple' | 'moderate' | 'complex';
    incidentId?: string;
  }): ThinkingConfig {
    
    // Ongoing incident investigation
    if (context.incidentId) {
      return {
        thinkingLevel: 'high',
        includeThoughts: true
      };
    }

    // Multiple recent incidents = heightened alert
    if (context.previousIncidents > 3) {
      return {
        thinkingLevel: 'high',
        includeThoughts: true
      };
    }

    // Complex scene needs deeper analysis
    if (context.sceneComplexity === 'complex') {
      return {
        thinkingLevel: 'high',
        includeThoughts: false  // Don't need thought log
      };
    }

    // Default: Fast analysis
    return {
      thinkingLevel: 'low',
      includeThoughts: false
    };
  }

  // Adaptive thinking based on model confidence
  adaptToConfidence(
    initialResult: AnalysisResult,
    config: ThinkingConfig
  ): ThinkingConfig {
    // If model uncertain and using low thinking, escalate
    if (config.thinkingLevel === 'low' && initialResult.confidence < 60) {
      return {
        thinkingLevel: 'high',
        includeThoughts: true
      };
    }
    return config;
  }
}

// Usage
const manager = new ThinkingLevelManager();

const config = manager.determineThinkingLevel({
  frameNumber: 42,
  previousIncidents: 5,
  sceneComplexity: 'complex'
});

// Later: Adapt based on initial result
const result = await analyzeFrame(frame, config);
const adaptedConfig = manager.adaptToConfidence(result, config);
if (adaptedConfig.thinkingLevel !== config.thinkingLevel) {
  // Re-analyze with deeper thinking
  const enhancedResult = await analyzeFrame(frame, adaptedConfig);
}
```

---

## 🖼️ Media Resolution

### Resolution Strategy

```typescript
type MediaResolution = 'low' | 'medium' | 'high';

interface ResolutionImpact {
  resolution: MediaResolution;
  tokenMultiplier: number;
  accuracyIncrease: number;
  useCases: string[];
}

const RESOLUTION_PROFILES: ResolutionImpact[] = [
  {
    resolution: 'low',
    tokenMultiplier: 0.5,
    accuracyIncrease: 0,
    useCases: [
      'Routine monitoring',
      'Cost optimization',
      'High-frequency analysis'
    ]
  },
  {
    resolution: 'medium',
    tokenMultiplier: 1.0,
    accuracyIncrease: 0.15,
    useCases: [
      'Standard security monitoring',
      'Balanced cost/quality',
      'Most common use case'
    ]
  },
  {
    resolution: 'high',
    tokenMultiplier: 2.0,
    accuracyIncrease: 0.30,
    useCases: [
      'Critical incident analysis',
      'Evidence collection',
      'Detailed subject identification',
      'Complex scene understanding'
    ]
  }
];

class ResolutionManager {
  selectResolution(context: {
    threatLevel: number;
    isEvidence: boolean;
    requiresDetail: boolean;
    budget: number;
  }): MediaResolution {
    
    // Evidence collection: Always high
    if (context.isEvidence) {
      return 'high';
    }

    // Critical threats: High resolution
    if (context.threatLevel > 80) {
      return 'high';
    }

    // Suspicious activity: Medium-high
    if (context.threatLevel > 50 || context.requiresDetail) {
      return 'medium';
    }

    // Budget constraints: Low
    if (context.budget < 0.001) {  // $ per frame
      return 'low';
    }

    // Default: Medium
    return 'medium';
  }

  estimateTokens(
    resolution: MediaResolution,
    imageSize: { width: number; height: number }
  ): number {
    const baseTokens = Math.ceil((imageSize.width * imageSize.height) / 750);
    const profile = RESOLUTION_PROFILES.find(p => p.resolution === resolution);
    return Math.ceil(baseTokens * (profile?.tokenMultiplier ?? 1.0));
  }
}

// Usage
const resolutionMgr = new ResolutionManager();

const resolution = resolutionMgr.selectResolution({
  threatLevel: 75,
  isEvidence: false,
  requiresDetail: true,
  budget: 0.002
});

const estimatedTokens = resolutionMgr.estimateTokens(
  resolution,
  { width: 1920, height: 1080 }
);

console.log(`Resolution: ${resolution}, Estimated tokens: ${estimatedTokens}`);
```

---

## 🔐 Thought Signatures

### What Are Thought Signatures?

Thought signatures are encrypted representations of the model's internal thought process essential to maintain reasoning context across API calls.

### Implementation

```typescript
class ThoughtSignatureManager {
  private signatures: Map<string, any> = new Map();
  
  // Store signature after analysis
  storeSignature(incidentId: string, signature: any): void {
    this.signatures.set(incidentId, {
      signature,
      timestamp: Date.now(),
      frameCount: 1
    });
  }

  // Retrieve signature for continued analysis
  getSignature(incidentId: string): any | null {
    const stored = this.signatures.get(incidentId);
    if (!stored) return null;

    // Update usage count
    stored.frameCount++;
    return stored.signature;
  }

  // Clean up old signatures (prevent memory leaks)
  cleanup(maxAge: number = 3600000): void {  // 1 hour default
    const now = Date.now();
    for (const [id, data] of this.signatures.entries()) {
      if (now - data.timestamp > maxAge) {
        this.signatures.delete(id);
      }
    }
  }

  // Build request with thought signature
  buildRequestWithContext(
    incidentId: string,
    currentContent: any[]
  ): any[] {
    const signature = this.getSignature(incidentId);
    
    if (!signature) {
      // First analysis - no prior context
      return currentContent;
    }

    // Multi-turn analysis - include previous reasoning
    return [
      {
        role: 'model',
        parts: [{ thoughtSignature: signature }]
      },
      ...currentContent
    ];
  }
}

// Usage Example: Multi-turn incident investigation

const signatureMgr = new ThoughtSignatureManager();

// Frame 1: Initial detection
const response1 = await model.generateContent({
  contents: [
    {
      role: 'user',
      parts: [
        { inlineData: { mimeType: 'image/jpeg', data: frame1 } },
        { text: 'Analyze for threats' }
      ]
    }
  ],
  generationConfig: {
    temperature: 1.0,
    thinkingConfig: { thinkingLevel: 'high', includeThoughts: true }
  }
});

// Store signature for incident
const incidentId = 'incident_123';
signatureMgr.storeSignature(incidentId, response1.thoughtSignature);

// Frame 2: Continued analysis with context
const response2 = await model.generateContent({
  contents: signatureMgr.buildRequestWithContext(incidentId, [
    {
      role: 'user',
      parts: [
        { inlineData: { mimeType: 'image/jpeg', data: frame2 } },
        { text: 'Continue tracking subject from previous frame' }
      ]
    }
  ]),
  generationConfig: {
    temperature: 1.0,
    thinkingConfig: { thinkingLevel: 'high', includeThoughts: true }
  }
});

// Update signature
signatureMgr.storeSignature(incidentId, response2.thoughtSignature);

// Gemini 3 now correlates both frames with maintained reasoning context
```

---

## 🎨 Advanced Patterns

### Pattern 1: Adaptive Analysis Pipeline

```typescript
class AdaptiveAnalysisPipeline {
  async analyze(frame: string, context: AnalysisContext): Promise<AnalysisResult> {
    // Stage 1: Quick assessment with Flash
    const quickResult = await this.quickScan(frame);
    
    if (quickResult.threatLevel < 30) {
      // Low threat: Return fast result
      return quickResult;
    }

    // Stage 2: Elevated threat - use Pro with medium thinking
    const detailedResult = await this.detailedAnalysis(frame, quickResult);
    
    if (detailedResult.confidence > 85 && detailedResult.threatLevel < 70) {
      // Confident, moderate threat: Return
      return detailedResult;
    }

    // Stage 3: High threat or uncertain - Deep Think mode
    const deepAnalysis = await this.deepThinkAnalysis(frame, detailedResult);
    
    return deepAnalysis;
  }

  private async quickScan(frame: string): Promise<AnalysisResult> {
    return geminiService.analyze(frame, {
      model: 'gemini-3-flash-preview',
      thinkingLevel: 'low',
      mediaResolution: 'low'
    });
  }

  private async detailedAnalysis(
    frame: string,
    priorResult: AnalysisResult
  ): Promise<AnalysisResult> {
    return geminiService.analyze(frame, {
      model: 'gemini-3-pro-preview',
      thinkingLevel: 'low',
      mediaResolution: 'high',
      context: priorResult  // Include quick scan results
    });
  }

  private async deepThinkAnalysis(
    frame: string,
    priorResult: AnalysisResult
  ): Promise<AnalysisResult> {
    return geminiService.analyze(frame, {
      model: 'gemini-3-pro-preview',
      thinkingLevel: 'high',
      mediaResolution: 'high',
      includeThoughts: true,
      context: priorResult
    });
  }
}
```

### Pattern 2: Historical Context Builder

```typescript
class HistoricalContextBuilder {
  private frameBuffer: FrameAnalysis[] = [];
  private readonly MAX_CONTEXT_TOKENS = 500000;  // Reserve 500K for history

  addFrame(analysis: FrameAnalysis): void {
    this.frameBuffer.push(analysis);
    this.pruneIfNeeded();
  }

  buildContextPrompt(): string {
    if (this.frameBuffer.length === 0) return '';

    const summary = this.summarizeHistory();
    const recentDetails = this.getRecentDetails();

    return `
HISTORICAL CONTEXT (Last ${this.frameBuffer.length} frames):

Summary of Activity:
${summary}

Recent Detailed Observations:
${recentDetails}

Use this context to:
1. Identify patterns across time
2. Track subject consistency
3. Detect behavior changes
4. Correlate current frame with history
`;
  }

  private summarizeHistory(): string {
    const incidents = this.frameBuffer.filter(f => f.incident);
    const subjects = this.extractSubjects();

    return `
- Total frames analyzed: ${this.frameBuffer.length}
- Incidents detected: ${incidents.length}
- Unique subjects tracked: ${subjects.size}
- Average threat level: ${this.calculateAvgThreat()}
- Most common behaviors: ${this.getCommonBehaviors()}
`;
  }

  private getRecentDetails(): string {
    return this.frameBuffer
      .slice(-5)  // Last 5 frames
      .map((f, i) => `
Frame ${f.frameNumber}:
  - Incident: ${f.incident}
  - Type: ${f.type}
  - Subjects: ${f.subjects.map(s => s.id).join(', ')}
  - Key observation: ${f.reasoning.slice(0, 100)}...
`)
      .join('\n');
  }

  private pruneIfNeeded(): void {
    let totalTokens = this.estimateTokens();
    
    while (totalTokens > this.MAX_CONTEXT_TOKENS && this.frameBuffer.length > 10) {
      this.frameBuffer.shift();  // Remove oldest
      totalTokens = this.estimateTokens();
    }
  }

  private estimateTokens(): number {
    // Rough estimate: 1 token ≈ 4 characters
    const contextText = this.buildContextPrompt();
    return Math.ceil(contextText.length / 4);
  }
}

// Usage
const contextBuilder = new HistoricalContextBuilder();

// Add each frame analysis
for (const analysis of frameAnalyses) {
  contextBuilder.addFrame(analysis);
}

// Include in next analysis
const prompt = `
${contextBuilder.buildContextPrompt()}

Analyze current frame with full historical awareness.
`;
```

---

## ⚡ Performance Optimization

### Token Budget Management

```typescript
interface TokenBudget {
  maxInputTokens: number;
  maxOutputTokens: number;
  estimatedCost: number;
}

class TokenBudgetManager {
  calculateBudget(config: {
    model: string;
    resolution: MediaResolution;
    thinkingLevel: 'low' | 'high';
    historicalContextFrames: number;
  }): TokenBudget {
    
    // Image tokens (depends on resolution)
    const imageTokens = this.estimateImageTokens(config.resolution);
    
    // Prompt tokens
    const promptTokens = 500;  // Base prompt
    
    // Historical context tokens
    const contextTokens = config.historicalContextFrames * 200;
    
    // Thinking overhead (Deep Think uses more)
    const thinkingMultiplier = config.thinkingLevel === 'high' ? 1.5 : 1.0;
    
    const totalInput = Math.ceil(
      (imageTokens + promptTokens + contextTokens) * thinkingMultiplier
    );
    
    // Output tokens (responses are typically 300-500 tokens)
    const outputTokens = 500;
    
    // Calculate cost
    const pricing = this.getPricing(config.model);
    const cost = (
      (totalInput / 1000000) * pricing.input +
      (outputTokens / 1000000) * pricing.output
    );
    
    return {
      maxInputTokens: totalInput,
      maxOutputTokens: outputTokens,
      estimatedCost: cost
    };
  }

  private estimateImageTokens(resolution: MediaResolution): number {
    const tokenEstimates = {
      low: 200,
      medium: 500,
      high: 1000
    };
    return tokenEstimates[resolution];
  }

  private getPricing(model: string) {
    return model.includes('flash')
      ? { input: 0.50, output: 3.00 }
      : { input: 2.00, output: 12.00 };
  }
}

// Usage
const budgetMgr = new TokenBudgetManager();

const budget = budgetMgr.calculateBudget({
  model: 'gemini-3-pro-preview',
  resolution: 'high',
  thinkingLevel: 'high',
  historicalContextFrames: 100
});

console.log(`Estimated cost per frame: $${budget.estimatedCost.toFixed(4)}`);
// "Estimated cost per frame: $0.0234"
```

---

## ✅ Best Practices

### 1. Always Use Temperature 1.0

```typescript
// ❌ DON'T
const config = {
  temperature: 0.2  // Can cause looping, degraded performance
};

// ✅ DO
const config = {
  temperature: 1.0  // Gemini 3 optimized for this
};

// ✅ BETTER - Omit entirely (uses default)
const config = {};
```

### 2. Start Low, Escalate When Needed

```typescript
// Cost-effective approach
const result = await analyzeWithFlash(frame);

if (result.threatLevel > 70 || result.confidence < 60) {
  // Escalate to Pro with Deep Think
  const detailedResult = await analyzeWithProDeepThink(frame);
}
```

### 3. Use Thought Signatures for Investigations

```typescript
// ❌ DON'T - Each frame analyzed independently
for (const frame of investigationFrames) {
  await analyze(frame);  // No context between frames
}

// ✅ DO - Maintain reasoning context
const incidentId = 'incident_xyz';
for (const frame of investigationFrames) {
  await analyzeWithContext(frame, incidentId);  // Builds on prior reasoning
}
```

### 4. Monitor and Adapt

```typescript
class PerformanceMonitor {
  private metrics: {
    avgLatency: number;
    avgCost: number;
    accuracyRate: number;
  } = { avgLatency: 0, avgCost: 0, accuracyRate: 0 };

  adaptConfiguration(): ModelConfig {
    // If latency high, use Flash
    if (this.metrics.avgLatency > 5000) {
      return { model: 'flash', thinkingLevel: 'low' };
    }

    // If accuracy low, use Pro with Deep Think
    if (this.metrics.accuracyRate < 0.85) {
      return { model: 'pro', thinkingLevel: 'high' };
    }

    // If cost high, optimize
    if (this.metrics.avgCost > 0.01) {
      return { model: 'flash', mediaResolution: 'medium' };
    }

    // Default balanced config
    return { model: 'flash', thinkingLevel: 'low', mediaResolution: 'medium' };
  }
}
```

---

## 🎓 Summary

### Key Takeaways

1. **Model Selection**: Flash for speed/cost, Pro for reasoning/critical incidents
2. **Thinking Levels**: Low for routine, high for complex/critical analysis
3. **Media Resolution**: Adapt based on threat level and budget
4. **Thought Signatures**: Essential for multi-turn investigations
5. **Temperature**: Always 1.0 (or omit)
6. **Context Window**: Leverage 1M tokens for historical correlation
7. **Cost Optimization**: Start cheap, escalate when needed

---

**Ready to implement? See [GEMINI_3_UPGRADE_GUIDE.md](GEMINI_3_UPGRADE_GUIDE.md) for migration steps!**
