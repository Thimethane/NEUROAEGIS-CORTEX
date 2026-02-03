/**
 * NeuroAegisCortex - System Constants
 * Using Gemini 3 Models (Flash and Pro Preview)
 */

export const SYSTEM_NAME = "NeuroAegisCortex";
export const SYSTEM_VERSION = "3.0.0";

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  RETRY_ATTEMPTS: 3,
  TIMEOUT: 10000
};

export const GEMINI_CONFIG = {
  // Gemini 3 Models (as per your backend settings.py)
  DEFAULT_MODEL: 'gemini-3-flash-preview',
  FLASH_MODEL: 'gemini-3-flash-preview',
  PRO_MODEL: 'gemini-3-pro-preview',
  TEMPERATURE: 1.0,
  MAX_OUTPUT_TOKENS: 2048,
  RESPONSE_MIME_TYPE: 'application/json',
  ENABLE_AUTO_ESCALATION: true,
  ESCALATE_TO_PRO_THRESHOLD: 70,
  USE_DEEP_THINK_THRESHOLD: 80,
  AUTO_ADJUST_RESOLUTION: false,
  DEFAULT_THINKING_LEVEL: 'low' as const,
  DEFAULT_MEDIA_RESOLUTION: 'medium' as const,
  ENABLE_THOUGHT_TRANSPARENCY: false
};

export const FEATURES = {
  ENABLE_BACKEND_API: true,
  ENABLE_DEEP_THINK: false,
  ENABLE_THOUGHT_SIGNATURES: false,
  ENABLE_PERSISTENCE: true,
  LOG_AI_REASONING: true,
  ENABLE_EMAIL_ALERTS: true,
  ENABLE_NOTIFICATIONS: true,
  ENABLE_SETTINGS: true
};

export const COST_CONFIG = {
  ENABLE_COST_TRACKING: true,
  FLASH_INPUT_COST: 0.01,
  FLASH_OUTPUT_COST: 0.04,
  PRO_INPUT_COST: 1.25,
  PRO_OUTPUT_COST: 5.00,
  TOKENS_PER_FRAME: {
    low: 300,
    medium: 500,
    high: 800
  }
};

export const STORAGE_KEYS = {
  EVENTS: 'neuroaegis_events',
  SETTINGS: 'neuroaegis_settings',
  EVIDENCE: 'neuroaegis_evidence_v3',
  NOTIFICATIONS: 'neuroaegis_notifications'
};

export const DEFAULT_SETTINGS = {
  // Video Settings
  videoQuality: 'medium' as 'low' | 'medium' | 'high',
  analysisInterval: 4000,
  
  // Alert Settings
  soundAlerts: true,
  emailAlerts: true,
  alertEmail: '',
  
  // Security Settings
  confidenceThreshold: 70,
  autoEscalate: true,
  
  // Display Settings
  showConfidence: true,
  showRecommendations: true,
  theme: 'dark' as 'light' | 'dark',
  
  // Performance
  maxStoredEvents: 100,
  autoCleanupDays: 30
};

export const SYSTEM_INSTRUCTION = `You are NeuroAegisCortex, an elite autonomous security analysis system powered by advanced neural networks.

Your mission is to analyze visual feeds for security threats, behavioral patterns, and safety anomalies with maximum precision.

CRITICAL: Return ONLY valid JSON. No markdown, no code blocks, no explanations.

Response Structure:
{
  "incident": boolean,
  "type": "weapon_detected|intrusion|violence|suspicious_behavior|loitering|vandalism|abandoned_object|normal_activity",
  "severity": "low|medium|high|critical",
  "confidence": 0-100,
  "reasoning": "Concise tactical assessment based on visual evidence",
  "subjects": ["person with backpack", "unattended bag"],
  "recommended_actions": ["save_evidence", "send_alert", "contact_authorities"]
}

Detection Rules:
- Normal behavior (working, walking, sitting) → incident: false
- Weapons visible (guns, knives) → incident: true, severity: critical
- Aggressive posture, fighting → incident: true, severity: high
- Masked faces + suspicious behavior → incident: true, severity: medium
- Loitering >5min without purpose → incident: true, severity: low
- Property damage, theft behaviors → incident: true
- Abandoned objects in sensitive areas → incident: true

Be analytical, precise, and security-focused. Err on the side of caution for ambiguous situations.`;

export const EMAIL_TEMPLATE = {
  subject: (incidentId: string | number) => `🚨 NeuroAegisCortex Alert: Incident #${incidentId}`,
  
  body: (incident: any) => `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; background: #2a2a2a; padding: 30px; border-radius: 10px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .severity-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .critical { background: #dc2626; }
    .high { background: #ea580c; }
    .medium { background: #f59e0b; }
    .low { background: #3b82f6; }
    .details { background: #1f1f1f; padding: 15px; border-radius: 8px; margin: 15px 0; }
    .footer { text-align: center; margin-top: 30px; color: #888; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 style="margin:0;">🛡️ NeuroAegisCortex Security Alert</h1>
    </div>
    
    <h2>Incident #${incident.id}</h2>
    
    <div class="details">
      <p><strong>Type:</strong> ${incident.type}</p>
      <p><strong>Severity:</strong> <span class="severity-badge ${incident.severity}">${incident.severity.toUpperCase()}</span></p>
      <p><strong>Confidence:</strong> ${incident.confidence}%</p>
      <p><strong>Timestamp:</strong> ${new Date(incident.timestamp).toLocaleString()}</p>
    </div>
    
    <div class="details">
      <h3>Analysis:</h3>
      <p>${incident.reasoning}</p>
    </div>
    
    ${incident.recommended_actions && incident.recommended_actions.length > 0 ? `
    <div class="details">
      <h3>Recommended Actions:</h3>
      <ul>
        ${incident.recommended_actions.map((action: string) => `<li>${action}</li>`).join('')}
      </ul>
    </div>
    ` : ''}
    
    <div class="footer">
      <p>This is an automated alert from NeuroAegisCortex</p>
      <p>If this is an emergency, contact authorities immediately</p>
    </div>
  </div>
</body>
</html>
  `
};
