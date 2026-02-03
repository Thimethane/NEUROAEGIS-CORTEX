/**
 * API Services - Backend Communication
 * Handles all API calls to the backend
 */

import { API_CONFIG } from '../constants';

// Detect if we're in browser and can reach backend
const getApiBaseUrl = (): string => {
  // If running in Docker container, use service name
  if (typeof window !== 'undefined') {
    // Browser environment - use localhost
    return 'http://localhost:8000';
  }
  // Server-side rendering or build time
  return API_CONFIG.BASE_URL;
};

const BASE_URL = getApiBaseUrl();

/**
 * Check if backend is healthy and reachable
 */
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

    const response = await fetch(`${BASE_URL}/api/health`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      return data.status === 'healthy';
    }
    return false;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

/**
 * Analyze frame via backend API
 */
export const analyzeFrameViaBackend = async (
  base64Image: string
): Promise<any | null> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout for analysis

    console.log(`📡 Sending frame to backend at ${BASE_URL}/api/analyze`);

    const response = await fetch(`${BASE_URL}/api/analyze`, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        image: base64Image
      }),
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend returned ${response.status}:`, errorText);
      return null;
    }

    const data = await response.json();
    console.log('✅ Backend analysis successful');
    return data;

  } catch (error: any) {
    if (error.name === 'AbortError') {
      console.error('❌ Backend request timeout');
    } else {
      console.error('❌ Backend analysis error:', error.message);
    }
    return null;
  }
};

/**
 * Get recent incidents from backend
 */
export const getRecentIncidents = async (
  limit: number = 50,
  severity?: string
): Promise<any[]> => {
  try {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (severity) {
      params.append('severity', severity);
    }

    const response = await fetch(`${BASE_URL}/api/incidents?${params}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch incidents:', error);
    return [];
  }
};

/**
 * Get single incident by ID
 */
export const getIncidentById = async (id: number): Promise<any | null> => {
  try {
    const response = await fetch(`${BASE_URL}/api/incidents/${id}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch incident:', error);
    return null;
  }
};

/**
 * Get system statistics
 */
export const getStatistics = async (): Promise<any | null> => {
  try {
    const response = await fetch(`${BASE_URL}/api/stats`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch statistics:', error);
    return null;
  }
};

/**
 * Update incident status
 */
export const updateIncidentStatus = async (
  id: number,
  status: string
): Promise<boolean> => {
  try {
    const response = await fetch(`${BASE_URL}/api/incidents/${id}/status?status=${status}`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
    });

    return response.ok;
  } catch (error) {
    console.error('Failed to update incident status:', error);
    return false;
  }
};

/**
 * Test backend connectivity
 */
export const testBackendConnection = async (): Promise<{
  reachable: boolean;
  latency: number;
  error?: string;
}> => {
  const startTime = Date.now();
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${BASE_URL}/api/health`, {
      method: 'GET',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    const latency = Date.now() - startTime;

    if (response.ok) {
      return { reachable: true, latency };
    }

    return {
      reachable: false,
      latency,
      error: `HTTP ${response.status}`
    };

  } catch (error: any) {
    return {
      reachable: false,
      latency: Date.now() - startTime,
      error: error.name === 'AbortError' ? 'Timeout' : error.message
    };
  }
};

/**
 * Get current API configuration
 */
export const getApiConfig = () => {
  return {
    baseUrl: BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    retryAttempts: API_CONFIG.RETRY_ATTEMPTS
  };
};

console.log(`🌐 API Service initialized: ${BASE_URL}`);
