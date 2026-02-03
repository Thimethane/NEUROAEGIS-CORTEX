/**
 * Diagnostic Overlay Component
 * Shows real-time system diagnostics for debugging
 * Press 'D' key to toggle
 */

import React, { useState, useEffect } from 'react';
import type { SystemStats, SecurityEvent } from '../types';

interface DiagnosticOverlayProps {
  isMonitoring: boolean;
  stats: SystemStats;
  events: SecurityEvent[];
  currentAnalysis: SecurityEvent | null;
  backendConnected: boolean;
}

export const DiagnosticOverlay: React.FC<DiagnosticOverlayProps> = ({
  isMonitoring,
  stats,
  events,
  currentAnalysis,
  backendConnected
}) => {
  const [visible, setVisible] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  // Toggle with 'D' key
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'd' || e.key === 'D') {
        setVisible(prev => !prev);
      }
    };

    window.addEventListener('keypress', handleKeyPress);
    return () => window.removeEventListener('keypress', handleKeyPress);
  }, []);

  // Capture console logs
  useEffect(() => {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;

    console.log = (...args) => {
      setLogs(prev => [...prev.slice(-19), `[LOG] ${args.join(' ')}`]);
      originalLog(...args);
    };

    console.error = (...args) => {
      setLogs(prev => [...prev.slice(-19), `[ERR] ${args.join(' ')}`]);
      originalError(...args);
    };

    console.warn = (...args) => {
      setLogs(prev => [...prev.slice(-19), `[WRN] ${args.join(' ')}`]);
      originalWarn(...args);
    };

    return () => {
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
    };
  }, []);

  if (!visible) {
    return (
      <div className="fixed bottom-4 left-4 bg-black/80 text-white px-3 py-2 rounded text-xs font-mono">
        Press 'D' for diagnostics
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/90 text-white p-4 overflow-auto z-50 font-mono text-xs">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-xl font-bold">🔍 AegisAI Diagnostics</h1>
          <button
            onClick={() => setVisible(false)}
            className="px-4 py-2 bg-red-600 rounded hover:bg-red-700"
          >
            Close (or press D)
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* System Status */}
          <div className="bg-gray-800 p-4 rounded">
            <h2 className="text-lg font-bold mb-2 text-cyan-400">System Status</h2>
            <div className="space-y-1">
              <div>Monitoring: <span className={isMonitoring ? 'text-green-400' : 'text-red-400'}>{isMonitoring ? 'ACTIVE' : 'INACTIVE'}</span></div>
              <div>Backend: <span className={backendConnected ? 'text-blue-400' : 'text-orange-400'}>{backendConnected ? 'CONNECTED' : 'CLIENT-SIDE'}</span></div>
              <div>Scans: <span className="text-white">{stats.scansPerformed}</span></div>
              <div>Incidents: <span className="text-white">{stats.incidentsDetected}</span></div>
              <div>CPU: <span className="text-white">{stats.cpuUsage}%</span></div>
              <div>Events in Log: <span className="text-white">{events.length}</span></div>
            </div>
          </div>

          {/* Current Analysis */}
          <div className="bg-gray-800 p-4 rounded">
            <h2 className="text-lg font-bold mb-2 text-cyan-400">Latest Analysis</h2>
            {currentAnalysis ? (
              <div className="space-y-1">
                <div>Type: <span className="text-white">{currentAnalysis.type}</span></div>
                <div>Incident: <span className={currentAnalysis.incident ? 'text-red-400' : 'text-green-400'}>{currentAnalysis.incident ? 'YES' : 'NO'}</span></div>
                <div>Severity: <span className="text-white">{currentAnalysis.severity}</span></div>
                <div>Confidence: <span className="text-white">{currentAnalysis.confidence}%</span></div>
                <div>Reasoning: <span className="text-gray-300 text-xs">{currentAnalysis.reasoning.slice(0, 100)}...</span></div>
              </div>
            ) : (
              <div className="text-gray-500">No analysis yet</div>
            )}
          </div>

          {/* Environment */}
          <div className="bg-gray-800 p-4 rounded">
            <h2 className="text-lg font-bold mb-2 text-cyan-400">Environment</h2>
            <div className="space-y-1">
              <div>API Key: <span className={import.meta.env.VITE_GEMINI_API_KEY ? 'text-green-400' : 'text-red-400'}>
                {import.meta.env.VITE_GEMINI_API_KEY ? 'SET' : 'MISSING'}
              </span></div>
              <div>API URL: <span className="text-white">{import.meta.env.VITE_API_URL || 'http://localhost:8000'}</span></div>
              <div>Interval: <span className="text-white">{import.meta.env.VITE_ANALYSIS_INTERVAL || '4000'}ms</span></div>
            </div>
          </div>

          {/* Console Logs */}
          <div className="bg-gray-800 p-4 rounded">
            <h2 className="text-lg font-bold mb-2 text-cyan-400">Recent Logs</h2>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-gray-500">No logs yet</div>
              ) : (
                logs.map((log, i) => (
                  <div
                    key={i}
                    className={
                      log.startsWith('[ERR]')
                        ? 'text-red-400'
                        : log.startsWith('[WRN]')
                        ? 'text-yellow-400'
                        : 'text-gray-300'
                    }
                  >
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-4 bg-blue-900/50 p-4 rounded">
          <h3 className="font-bold mb-2">Debugging Steps:</h3>
          <ol className="list-decimal list-inside space-y-1">
            <li>Check "API Key" is SET above</li>
            <li>Ensure "Monitoring" shows ACTIVE</li>
            <li>Watch "Scans" counter - should increment every 4 seconds</li>
            <li>Check console logs for errors (Recent Logs above)</li>
            <li>Open browser console (F12) for detailed logs</li>
          </ol>
        </div>
      </div>
    </div>
  );
};
