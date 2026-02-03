/**
 * AegisAI Type Definitions
 * Matches backend models from routes.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum ThreatSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum IncidentType {
  THEFT = 'theft',
  INTRUSION = 'intrusion',
  VIOLENCE = 'violence',
  STALKING = 'stalking',
  LOITERING = 'loitering',
  VANDALISM = 'vandalism',
  SUSPICIOUS_BEHAVIOR = 'suspicious_behavior',
  WEAPON = 'weapon',
  NORMAL = 'normal',
  UNKNOWN = 'unknown'
}

export enum IncidentStatus {
  ACTIVE = 'active',
  RESOLVED = 'resolved',
  ESCALATED = 'escalated',
  DISMISSED = 'dismissed'
}

export enum ActionStatus {
  PENDING = 'pending',
  EXECUTING = 'executing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

// ============================================================================
// Backend API Response Models (Match routes.py)
// ============================================================================

/**
 * Matches AnalyzeResponse from routes.py
 */
export interface AnalysisResponse {
  incident: boolean;
  type: string;
  severity: string;
  confidence: number;
  reasoning: string;
  subjects: string[];
  recommended_actions: string[];
}

/**
 * Matches IncidentResponse from routes.py
 */
export interface IncidentResponse {
  id: number;
  timestamp: string;
  type: string;
  severity: string;
  confidence: number;
  reasoning: string;
  subjects: string[];
  evidence_path: string;
  status: string;
  created_at: string;
}

/**
 * Matches StatsResponse from routes.py
 */
export interface StatsResponse {
  total_incidents: number;
  active_incidents: number;
  severity_breakdown: {
    [key: string]: number;
  };
  recent_24h: number;
  system_status: string;
}

/**
 * Matches HealthResponse from routes.py
 */
export interface HealthResponse {
  status: string;
  components: {
    [key: string]: string;
  };
  timestamp: string;
}

// ============================================================================
// Frontend-Specific Types
// ============================================================================

/**
 * Security Event (Frontend representation)
 * Enhanced version of AnalysisResponse for UI
 */
export interface SecurityEvent {
  id: string;
  timestamp: number;
  incident: boolean;
  type: string;
  severity: ThreatSeverity | string;
  confidence: number;
  reasoning: string;
  subjects?: string[] | SubjectDetail[];
  recommended_actions: string[];
  snapshot?: string; // Base64 image
  evidence_path?: string;
  response_plan?: ActionStep[];
  
  // Gemini 3 enhanced fields
  spatial_analysis?: SpatialAnalysis;
  temporal_analysis?: TemporalAnalysis;
  thought_process?: string; // From Gemini 3 thought transparency
}

/**
 * Subject Detail (Gemini 3 enhanced)
 */
export interface SubjectDetail {
  id: string;
  description: string;
  behavior: string;
  location: string;
  tracking_confidence: number;
}

/**
 * Spatial Analysis (Gemini 3 feature)
 */
export interface SpatialAnalysis {
  zones_affected: string[];
  movement_pattern: string;
  proximity_concerns: string[];
}

/**
 * Temporal Analysis (Gemini 3 feature)
 */
export interface TemporalAnalysis {
  duration_observed: string;
  behavior_changes: string[];
  pattern_correlation: string;
}

/**
 * System Stats (Frontend)
 */
export interface SystemStats {
  scansPerformed: number;
  incidentsDetected: number;
  lastScanTime: number;
  uptime: number;
  cpuUsage: number;
  memoryUsage: number;
}

// ============================================================================
// Agent & Planning
// ============================================================================

export interface ActionStep {
  step: number;
  action: string;
  priority: 'immediate' | 'high' | 'medium' | 'low';
  parameters?: Record<string, any>;
  reasoning: string;
  status?: ActionStatus;
}

export interface AgentPlan {
  incident_id: number;
  steps: ActionStep[];
  created_at: string;
}

// ============================================================================
// Evidence Management
// ============================================================================

export interface ProcessedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  data: string; // base64
  thumbnail?: string;
  timestamp: number;
  processed: boolean;
}

export interface EvidenceStore {
  files: ProcessedFile[];
  incidents: {
    [incidentId: string]: {
      files: string[]; // file IDs
      timestamp: number;
    };
  };
}

// ============================================================================
// Component Props
// ============================================================================

export interface VideoFeedProps {
  onFrameCapture: (base64: string) => void;
  isMonitoring: boolean;
}

export interface DashboardProps {
  events: SecurityEvent[];
  stats: SystemStats;
  isMonitoring: boolean;
  toggleMonitoring: () => void;
  lastAnalysis: SecurityEvent | null;
}

export interface StatsCardsProps {
  stats: SystemStats;
  isMonitoring: boolean;
  toggleMonitoring: () => void;
}

export interface EvidenceManagerProps {
  mode: 'upload' | 'download' | null;
  onClose: () => void;
  onUpload: (files: ProcessedFile[]) => Promise<void>;
  onDownload: (incidentIds: string[]) => void;
  incidents: SecurityEvent[];
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseMonitoringReturn {
  isMonitoring: boolean;
  events: SecurityEvent[];
  currentAnalysis: SecurityEvent | null;
  stats: SystemStats;
  toggleMonitoring: () => void;
  handleFrameCapture: (base64: string) => Promise<void>;
  clearEvents: () => void;
  resetStats: () => void;
  backendConnected: boolean;
}

export interface UseCameraReturn {
  videoRef: React.RefObject<HTMLVideoElement>;
  canvasRef: React.RefObject<HTMLCanvasElement>;
  error: string | null;
  streamActive: boolean;
  captureFrame: () => string | null;
  restartCamera: () => Promise<void>;
}

export interface UseEvidenceReturn {
  showEvidencePanel: 'upload' | 'download' | null;
  toggleEvidencePanel: (mode: 'upload' | 'download' | null) => void;
  uploadEvidence: (files: ProcessedFile[]) => Promise<void>;
  downloadEvidence: (incidentIds: string[]) => void;
  saveFrameSnapshot: (base64Image: string, incidentId: string) => void;
  linkEvidenceToIncident: (incidentId: string, fileIds: string[]) => void;
  evidenceCount: number;
  getIncidentsWithEvidence: () => string[];
  cleanupOldEvidence: () => void;
  exportEvidenceStore: () => void;
}

// ============================================================================
// Configuration
// ============================================================================

export interface AppConfig {
  apiUrl: string;
  geminiApiKey: string;
  analysisInterval: number;
  confidenceThreshold: number;
}

export interface GeminiConfig {
  DEFAULT_MODEL: string;
  FLASH_MODEL: string;
  PRO_MODEL: string;
  ENABLE_AUTO_ESCALATION: boolean;
  ESCALATE_TO_PRO_THRESHOLD: number;
  USE_DEEP_THINK_THRESHOLD: number;
  DEFAULT_THINKING_LEVEL: 'low' | 'high';
  ENABLE_THOUGHT_TRANSPARENCY: boolean;
  DEFAULT_MEDIA_RESOLUTION: 'low' | 'medium' | 'high';
  AUTO_ADJUST_RESOLUTION: boolean;
  MAX_CONTEXT_TOKENS: number;
  MAX_FRAME_HISTORY: number;
  ENABLE_THOUGHT_SIGNATURES: boolean;
  TEMPERATURE: number;
  MAX_OUTPUT_TOKENS: number;
}

// ============================================================================
// Error Types
// ============================================================================

export class AegisError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'AegisError';
  }
}

export class CameraError extends AegisError {
  constructor(message: string, details?: any) {
    super(message, 'CAMERA_ERROR', details);
    this.name = 'CameraError';
  }
}

export class AnalysisError extends AegisError {
  constructor(message: string, details?: any) {
    super(message, 'ANALYSIS_ERROR', details);
    this.name = 'AnalysisError';
  }
}

export class BackendError extends AegisError {
  constructor(message: string, details?: any) {
    super(message, 'BACKEND_ERROR', details);
    this.name = 'BackendError';
  }
}

// ============================================================================
// Utility Types
// ============================================================================

export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type AsyncFunction<T = void> = () => Promise<T>;

// ============================================================================
// API Request/Response Types
// ============================================================================

/**
 * Request body for POST /api/analyze
 * Matches AnalyzeRequest in routes.py
 */
export interface AnalyzeRequest {
  image: string; // Base64 encoded image (cleaned, no prefix)
}

/**
 * Query parameters for GET /api/incidents
 */
export interface GetIncidentsParams {
  limit?: number; // 1-500, default 50
  severity?: 'low' | 'medium' | 'high' | 'critical';
}

/**
 * Query parameters for POST /api/incidents/{id}/status
 */
export interface UpdateIncidentStatusParams {
  status: 'active' | 'resolved' | 'escalated' | 'dismissed';
}

/**
 * Query parameters for DELETE /api/incidents/cleanup
 */
export interface CleanupIncidentsParams {
  days?: number; // 7-365, default 30
}

// ============================================================================
// Gemini 3 Specific Types
// ============================================================================

export interface ThinkingConfig {
  thinkingLevel: 'low' | 'high';
  includeThoughts: boolean;
}

export interface MediaConfig {
  mediaResolution: 'low' | 'medium' | 'high';
}

export interface AnalysisMetrics {
  model: string;
  thinkingLevel: string;
  mediaResolution: string;
  tokensUsed: number;
  durationMs: number;
  estimatedCost: number;
  escalated: boolean;
}

export interface AnalysisContext {
  frameNumber?: number;
  incidentId?: string;
  threatLevel?: number;
  isEvidence?: boolean;
}
