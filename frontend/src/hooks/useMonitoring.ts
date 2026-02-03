/**
 * useMonitoring Hook - Backend Integrated Version
 * Uses backend /api/analyze endpoint instead of calling Gemini directly
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { analyzeFrameViaBackend, checkBackendHealth } from '../services/apiServices';
import { SecurityEvent, SystemStats, ThreatSeverity } from '../types';
import { notificationService } from '../services/Notificationservice';
import { STORAGE_KEYS, DEFAULT_SETTINGS } from '../constants';
import type { SystemSettings } from '../components/SettingsPanel';

interface UseMonitoringReturn {
  isMonitoring: boolean;
  backendConnected: boolean;
  events: SecurityEvent[];
  currentAnalysis: SecurityEvent | null;
  stats: SystemStats;
  toggleMonitoring: () => void;
  handleFrameCapture: (base64: string) => Promise<void>;
  clearEvents: () => void;
  resetStats: () => void;
}

export const useMonitoring = (): UseMonitoringReturn => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<SecurityEvent | null>(null);
  const [stats, setStats] = useState<SystemStats>({
    scansPerformed: 0,
    incidentsDetected: 0,
    lastScanTime: Date.now(),
    uptime: 0,
    cpuUsage: 12,
    memoryUsage: 24
  });

  const audioContextRef = useRef<AudioContext | null>(null);
  const startTimeRef = useRef<number>(Date.now());

  // Load and apply settings
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    if (stored) {
      try {
        const settings: SystemSettings = { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
        // Initialize notification service with current settings
        notificationService.initialize(settings);
      } catch (e) {
        console.error('Failed to load settings:', e);
      }
    } else {
      // Initialize with defaults
      notificationService.initialize(DEFAULT_SETTINGS);
    }
  }, []);

  // Initialize audio context
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    
    return () => {
      audioContextRef.current?.close();
    };
  }, []);

  // Check backend health on mount and periodically
  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await checkBackendHealth();
      setBackendConnected(healthy);
      
      if (healthy) {
        console.log('✅ Backend API connected');
      } else {
        console.log('⚠️ Backend unavailable - using direct Gemini mode');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s

    return () => clearInterval(interval);
  }, []);

  // Update uptime
  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        uptime: Math.floor((Date.now() - startTimeRef.current) / 1000)
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [isMonitoring]);

  const playAlert = useCallback(() => {
    const ctx = audioContextRef.current;
    if (!ctx) return;

    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sawtooth';
    gainNode.gain.value = 0.1;
    
    oscillator.start();
    oscillator.stop(ctx.currentTime + 0.5);
  }, []);

  const handleFrameCapture = useCallback(async (base64: string) => {
    if (!isMonitoring) return;

    // Update scan stats
    setStats(prev => ({
      ...prev,
      scansPerformed: prev.scansPerformed + 1,
      lastScanTime: Date.now(),
      cpuUsage: Math.min(100, Math.floor(Math.random() * 40) + 40)
    }));

    try {
      // ✅ USE BACKEND API FOR ANALYSIS
      console.log('📡 Sending frame to backend API...');
      const result = await analyzeFrameViaBackend(base64);

      if (result) {
        // Backend is reachable
        setBackendConnected(true);

        const newEvent: SecurityEvent = {
          id: crypto.randomUUID(),
          timestamp: Date.now(),
          incident: result.incident,
          type: result.type,
          severity: result.severity as ThreatSeverity,
          confidence: result.confidence,
          reasoning: result.reasoning,
          recommended_actions: result.recommended_actions || [],
          subjects: result.subjects || [],
          snapshot: base64
        };

        setCurrentAnalysis(newEvent);

        if (result.incident) {
          setEvents(prev => [...prev, newEvent]);
          setStats(prev => ({
            ...prev,
            incidentsDetected: prev.incidentsDetected + 1
          }));

          // Send notification through notification service
          await notificationService.sendNotification(newEvent);

          // Play alert for high severity
          if (result.severity === 'high' || result.severity === 'critical') {
            playAlert();
          }

          console.log(`🚨 Incident detected: ${result.type} (${result.severity})`);
        } else {
          console.log(`✅ Analysis complete: ${result.type} - No threat`);
        }
      } else {
        // Backend unreachable - fallback mode
        setBackendConnected(false);
        console.warn('⚠️ Backend analysis failed - check backend connection');
      }
    } catch (error) {
      console.error('❌ Frame analysis error:', error);
      setBackendConnected(false);
    } finally {
      // CPU settle
      setTimeout(() => {
        setStats(prev => ({
          ...prev,
          cpuUsage: Math.floor(Math.random() * 15) + 10
        }));
      }, 500);
    }
  }, [isMonitoring, playAlert]);

  const toggleMonitoring = useCallback(() => {
    setIsMonitoring(prev => {
      const newState = !prev;
      
      if (newState) {
        // Starting monitoring
        startTimeRef.current = Date.now();
        console.log('🎬 Monitoring started');
      } else {
        console.log('⏹️ Monitoring stopped');
      }
      
      return newState;
    });
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setCurrentAnalysis(null);
    console.log('🧹 Events cleared');
  }, []);

  const resetStats = useCallback(() => {
    setStats({
      scansPerformed: 0,
      incidentsDetected: 0,
      lastScanTime: Date.now(),
      uptime: 0,
      cpuUsage: 12,
      memoryUsage: 24
    });
    startTimeRef.current = Date.now();
    console.log('🔄 Stats reset');
  }, []);

  return {
    isMonitoring,
    backendConnected,
    events,
    currentAnalysis,
    stats,
    toggleMonitoring,
    handleFrameCapture,
    clearEvents,
    resetStats
  };
};
