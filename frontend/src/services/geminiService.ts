/**
 * Gemini 3 Service - Vision Analysis
 * Fixed for Gemini 3 API (removes unsupported media_resolution parameter)
 */

import { GoogleGenerativeAI } from "@google/generative-ai";
import { SYSTEM_INSTRUCTION, GEMINI_CONFIG, FEATURES, COST_CONFIG } from "../constants";
import type { AnalysisResponse } from "../types";

// ============================================================================
// Types
// ============================================================================

interface AnalysisMetrics {
  model: string;
  thinkingLevel: string;
  tokensUsed: number;
  durationMs: number;
  estimatedCost: number;
  escalated: boolean;
}

// ============================================================================
// State Management
// ============================================================================

let genAI: GoogleGenerativeAI | null = null;
let thoughtSignatures: Map<string, any> = new Map();
let recentThreatCount = 0;
let analysisMetrics: AnalysisMetrics[] = [];

// ============================================================================
// Initialization
// ============================================================================

export const initGemini = (): void => {
  const apiKey =
    (import.meta as any).env?.VITE_GEMINI_API_KEY ||
    (window as any).env?.VITE_GEMINI_API_KEY;

  if (!apiKey) {
    console.error("❌ VITE_GEMINI_API_KEY is missing");
    console.error("Add it to frontend/.env.local");
    return;
  }

  try {
    genAI = new GoogleGenerativeAI(apiKey);
    console.log("✅ Gemini 3 initialized successfully");
    console.log(`📊 Default model: ${GEMINI_CONFIG.DEFAULT_MODEL}`);
    console.log(`🧠 Context window: 1,000,000 tokens`);
    console.log(`⚡ Deep Think mode: ${FEATURES.ENABLE_DEEP_THINK ? 'Enabled' : 'Disabled'}`);
  } catch (error) {
    console.error("❌ Failed to initialize Gemini 3:", error);
  }
};

// ============================================================================
// Model Selection
// ============================================================================

function selectModel(context: {
  threatLevel?: number;
  incidentId?: string;
}): string {
  if (context.incidentId) {
    return GEMINI_CONFIG.PRO_MODEL;
  }

  if (GEMINI_CONFIG.ENABLE_AUTO_ESCALATION && 
      context.threatLevel && 
      context.threatLevel > GEMINI_CONFIG.ESCALATE_TO_PRO_THRESHOLD) {
    console.log(`🔼 Escalating to Pro (threat level: ${context.threatLevel})`);
    return GEMINI_CONFIG.PRO_MODEL;
  }

  if (recentThreatCount > 3) {
    return GEMINI_CONFIG.PRO_MODEL;
  }

  return GEMINI_CONFIG.FLASH_MODEL;
}

// ============================================================================
// Core Analysis
// ============================================================================

export const analyzeFrame = async (
  base64Image: string,
  context: {
    frameNumber?: number;
    incidentId?: string;
    threatLevel?: number;
    isEvidence?: boolean;
  } = {}
): Promise<AnalysisResponse | null> => {
  
  if (!genAI) {
    initGemini();
    if (!genAI) return null;
  }

  const startTime = Date.now();

  try {
    const modelName = selectModel(context);

    console.log(`🔍 Analyzing frame with ${modelName}`);

    // Get model instance - NO media_resolution or thinkingConfig
    const model = genAI.getGenerativeModel({
      model: modelName,
      generationConfig: {
        temperature: GEMINI_CONFIG.TEMPERATURE,
        maxOutputTokens: GEMINI_CONFIG.MAX_OUTPUT_TOKENS,
        responseMimeType: GEMINI_CONFIG.RESPONSE_MIME_TYPE
      }
    });

    const contents = buildContentsWithContext(
      base64Image,
      context.incidentId
    );

    // Generate analysis - Simple request without unsupported parameters
    const result = await model.generateContent({
      contents
    });
    
    const response = result.response;
    const text = response.text();
    const parsed = parseResponse(text);

    const duration = Date.now() - startTime;
    const escalated = modelName === GEMINI_CONFIG.PRO_MODEL && 
                     context.threatLevel !== undefined;
    
    trackMetrics({
      model: modelName,
      thinkingLevel: 'standard',
      tokensUsed: estimateTokens(base64Image, text),
      durationMs: duration,
      estimatedCost: calculateCost(modelName, base64Image, text),
      escalated
    });

    if (parsed?.incident) {
      recentThreatCount++;
      setTimeout(() => recentThreatCount = Math.max(0, recentThreatCount - 1), 300000);
    }

    console.log(`✅ Analysis complete (${duration}ms)`);
    return parsed;

  } catch (error) {
    console.error("❌ Gemini 3 API Error:", error);
    return null;
  }
};

// ============================================================================
// Helper Functions
// ============================================================================

function buildContentsWithContext(
  base64Image: string,
  incidentId?: string
): any[] {
  const cleanBase64 = base64Image.includes(",")
    ? base64Image.split(",")[1]
    : base64Image;

  const contents: any[] = [];

  const previousSignature = incidentId 
    ? thoughtSignatures.get(incidentId)
    : null;

  if (previousSignature && FEATURES.ENABLE_THOUGHT_SIGNATURES) {
    contents.push({
      role: 'model',
      parts: [{ thoughtSignature: previousSignature }]
    });
  }

  contents.push({
    role: 'user',
    parts: [
      { text: SYSTEM_INSTRUCTION },
      {
        inlineData: {
          mimeType: "image/jpeg",
          data: cleanBase64
        }
      }
    ]
  });

  return contents;
}

function parseResponse(text: string): AnalysisResponse | null {
  if (!text) {
    console.error("Empty response from Gemini 3");
    return null;
  }

  try {
    let cleanText = text.trim();

    if (cleanText.startsWith("```")) {
      cleanText = cleanText
        .replace(/```json/g, "")
        .replace(/```/g, "")
        .trim();
    }

    const parsed = JSON.parse(cleanText) as AnalysisResponse;

    if (parsed.severity) {
      parsed.severity = parsed.severity.toLowerCase();
    }

    if (typeof parsed.incident === "undefined") {
      parsed.incident = false;
    }

    return parsed;

  } catch (parseError) {
    console.error("❌ JSON parse failed");
    console.error("RAW:", text.substring(0, 500));
    return null;
  }
}

function estimateTokens(image: string, response: string): number {
  const imageTokens = 500;
  const promptTokens = Math.ceil(SYSTEM_INSTRUCTION.length / 4);
  const responseTokens = Math.ceil(response.length / 4);
  
  return imageTokens + promptTokens + responseTokens;
}

function calculateCost(model: string, image: string, response: string): number {
  const isFlash = model.includes('flash');
  
  const inputCost = isFlash 
    ? COST_CONFIG.FLASH_INPUT_COST 
    : COST_CONFIG.PRO_INPUT_COST;
  
  const outputCost = isFlash 
    ? COST_CONFIG.FLASH_OUTPUT_COST 
    : COST_CONFIG.PRO_OUTPUT_COST;

  const tokens = estimateTokens(image, response);
  const inputTokens = tokens * 0.8;
  const outputTokens = tokens * 0.2;

  return (
    (inputTokens / 1_000_000) * inputCost +
    (outputTokens / 1_000_000) * outputCost
  );
}

function trackMetrics(metrics: AnalysisMetrics): void {
  if (!COST_CONFIG.ENABLE_COST_TRACKING) return;

  analysisMetrics.push(metrics);

  if (analysisMetrics.length > 100) {
    analysisMetrics.shift();
  }

  if (analysisMetrics.length % 10 === 0) {
    logMetricsSummary();
  }
}

function logMetricsSummary(): void {
  const totalCost = analysisMetrics.reduce((sum, m) => sum + m.estimatedCost, 0);
  const avgDuration = analysisMetrics.reduce((sum, m) => sum + m.durationMs, 0) / analysisMetrics.length;
  const flashCount = analysisMetrics.filter(m => m.model.includes('flash')).length;
  const proCount = analysisMetrics.filter(m => m.model.includes('pro')).length;
  const escalations = analysisMetrics.filter(m => m.escalated).length;

  console.log(`📊 Gemini 3 Metrics (last ${analysisMetrics.length} analyses):`);
  console.log(`   Total cost: $${totalCost.toFixed(4)}`);
  console.log(`   Avg duration: ${avgDuration.toFixed(0)}ms`);
  console.log(`   Flash: ${flashCount} | Pro: ${proCount}`);
  console.log(`   Escalations: ${escalations}`);
}

export const testConnection = async (): Promise<boolean> => {
  if (!genAI) {
    initGemini();
    if (!genAI) return false;
  }

  try {
    const model = genAI.getGenerativeModel({
      model: GEMINI_CONFIG.FLASH_MODEL
    });

    const result = await model.generateContent('Respond with "OK"');
    const text = result.response.text();
    
    console.log("✅ Gemini 3 test success:", text);
    return true;
    
  } catch (error) {
    console.error("❌ Gemini 3 test failed:", error);
    return false;
  }
};

export const getMetrics = () => {
  return {
    analyses: analysisMetrics.length,
    totalCost: analysisMetrics.reduce((sum, m) => sum + m.estimatedCost, 0),
    avgDuration: analysisMetrics.length > 0
      ? analysisMetrics.reduce((sum, m) => sum + m.durationMs, 0) / analysisMetrics.length
      : 0,
    modelUsage: {
      flash: analysisMetrics.filter(m => m.model.includes('flash')).length,
      pro: analysisMetrics.filter(m => m.model.includes('pro')).length
    },
    escalations: analysisMetrics.filter(m => m.escalated).length
  };
};

export const clearThoughtSignatures = () => {
  thoughtSignatures.clear();
  console.log('🧹 Cleared thought signatures');
};

export const resetMetrics = () => {
  analysisMetrics = [];
  recentThreatCount = 0;
  console.log('🔄 Reset metrics');
};
