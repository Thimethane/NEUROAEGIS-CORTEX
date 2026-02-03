/**
 * NeuroAegisCortex - Main Application
 * Integrated Security Surveillance System
 */

import React, { useState, useEffect } from 'react';
import {
  Shield, Settings, Bell, Upload, Download,
  Activity, AlertTriangle, Eye
} from 'lucide-react';

// Components
import { VideoFeed } from './components/VideoFeed';
import { Dashboard } from './components/Dashboard/Dashboard';
import { DiagnosticOverlay } from './components/DiagnosticOverlay';
import { EvidenceManager } from './components/EvidenceManager';
import { SettingsPanel } from './components/SettingsPanel';
import type { SystemSettings } from './components/SettingsPanel';
import { NotificationsPanel } from './components/NotificationsPanel';

// Hooks
import { useCamera } from './hooks/useCamera';
import { useMonitoring } from './hooks/useMonitoring';
import { useEvidence } from './hooks/useEvidence';

// Constants
import { SYSTEM_NAME, SYSTEM_VERSION, DEFAULT_SETTINGS, STORAGE_KEYS } from './constants';

function App() {
  // State Management
  const [settings, setSettings] = useState<SystemSettings>(DEFAULT_SETTINGS);
  const [showSettings, setShowSettings] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  
  const {
    isMonitoring,
    backendConnected,
    events,
    currentAnalysis,
    stats,
    toggleMonitoring,
    handleFrameCapture,
    clearEvents,
    resetStats
  } = useMonitoring();

  const {
    showEvidencePanel,
    toggleEvidencePanel,
    uploadEvidence,
    downloadEvidence,
    saveFrameSnapshot,
    evidenceCount
  } = useEvidence();

  // Load settings on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    if (stored) {
      try {
        setSettings({ ...DEFAULT_SETTINGS, ...JSON.parse(stored) });
      } catch (e) {
        console.error('Failed to load settings:', e);
      }
    }
  }, []);

  // Handle settings changes and apply them
  const handleSettingsChange = (newSettings: SystemSettings) => {
    setSettings(newSettings);
    console.log('✅ Settings updated:', newSettings);
    
    // Apply analysis interval if changed
    if (newSettings.analysisInterval !== settings.analysisInterval) {
      console.log(`⏱️ Analysis interval changed to ${newSettings.analysisInterval}ms`);
      window.location.reload(); // Reload to apply new interval
    }
    
    // Clear old events if max limit reduced
    if (newSettings.maxStoredEvents < events.length) {
      console.log(`🧹 Trimming events to ${newSettings.maxStoredEvents}`);
    }
  };

  // Get unread notifications count
  const unreadCount = events.filter(e => e.incident && e.severity === 'high' || e.severity === 'critical').length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-purple-950 text-white overflow-hidden">
      
      {/* Header */}
      <header className="bg-slate-900/50 backdrop-blur-md border-b border-purple-500/20 sticky top-0 z-40">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            
            {/* Logo & Branding */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg">
                <Shield className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                  {SYSTEM_NAME}
                </h1>
                <div className="flex items-center gap-2 text-[10px] text-slate-400">
                  <span>v{SYSTEM_VERSION}</span>
                  <span className="text-purple-400">•</span>
                  <span className="text-purple-400 font-mono px-2 py-0.5 bg-purple-900/30 rounded">
                    GEMINI 3
                  </span>
                  <span className="text-purple-400">•</span>
                  <span>Neural Security</span>
                </div>
              </div>
            </div>

            {/* Status Indicators - Desktop */}
            <div className="hidden md:flex items-center gap-3">
              {/* System Status */}
              <div className="flex items-center gap-2 px-3 py-2 bg-slate-800 rounded-lg">
                <Activity size={14} className="text-blue-400" />
                <span className="text-xs text-slate-300">
                  {stats.scansPerformed} scans
                </span>
              </div>
              
              {/* Backend Connection */}
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                backendConnected ? 'bg-blue-900/30' : 'bg-orange-900/30'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  backendConnected ? 'bg-blue-400 animate-pulse' : 'bg-orange-400'
                }`} />
                <span className="text-xs text-slate-300">
                  {backendConnected ? 'API Connected' : 'Direct Mode'}
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              
              {/* Evidence Upload/Download */}
              <button
                onClick={() => toggleEvidencePanel('upload')}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors group"
                title="Upload Evidence"
              >
                <Upload className="text-slate-400 group-hover:text-blue-400" size={18} />
              </button>

              <button
                onClick={() => toggleEvidencePanel('download')}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors relative group"
                title="Download Evidence"
              >
                <Download className="text-slate-400 group-hover:text-green-400" size={18} />
                {evidenceCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-purple-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center text-[10px]">
                    {evidenceCount > 9 ? '9+' : evidenceCount}
                  </span>
                )}
              </button>

              {/* Notifications */}
              <button
                onClick={() => setShowNotifications(true)}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors relative group"
                title="Notifications"
              >
                <Bell className="text-slate-400 group-hover:text-yellow-400" size={18} />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center text-[10px] animate-pulse">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>

              {/* Settings */}
              <button
                onClick={() => setShowSettings(true)}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors group"
                title="Settings"
              >
                <Settings className="text-slate-400 group-hover:text-purple-400" size={18} />
              </button>
            </div>
          </div>

          {/* Mobile Status Bar */}
          <div className="md:hidden mt-2 flex items-center gap-2 text-xs overflow-x-auto">
            <div className="flex items-center gap-1 px-2 py-1 bg-slate-800 rounded whitespace-nowrap">
              <Activity size={12} className="text-blue-400" />
              <span>{stats.scansPerformed}</span>
            </div>
            <div className={`flex items-center gap-1 px-2 py-1 rounded whitespace-nowrap ${
              backendConnected ? 'bg-blue-900/30' : 'bg-orange-900/30'
            }`}>
              <div className={`w-1.5 h-1.5 rounded-full ${
                backendConnected ? 'bg-blue-400' : 'bg-orange-400'
              }`} />
              <span>{backendConnected ? 'API' : 'Direct'}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-2 sm:px-4 py-4 sm:py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          
          {/* Left Column - Video Feed & Actions */}
          <div className="lg:col-span-1 flex flex-col gap-4">
            {/* Video Feed */}
            <div className="bg-slate-900/30 backdrop-blur-sm border border-purple-500/20 rounded-lg p-3 sm:p-4 shadow-xl">
              <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                <Activity size={16} className="text-purple-400" />
                Live Surveillance Feed
              </h2>
              <div className="aspect-video sm:aspect-[4/3] w-full">
                <VideoFeed
                  onFrameCapture={handleFrameCapture}
                  isMonitoring={isMonitoring}
                />
              </div>
            </div>

            {/* Action Response Panel */}
            <div className="bg-slate-900/30 backdrop-blur-sm border border-purple-500/20 rounded-lg p-3 sm:p-4 shadow-xl">
              <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                <Shield size={16} className="text-purple-400" />
                Active Response Plan
              </h3>
              
              {currentAnalysis?.incident ? (
                <div className="space-y-2">
                  {currentAnalysis.recommended_actions?.map((action: string, i: number) => (
                    <div
                      key={i}
                      className="flex items-center gap-3 text-sm bg-slate-800/50 p-2 rounded border-l-2 border-purple-500"
                    >
                      <div className="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-xs text-purple-400 font-mono">
                        {i + 1}
                      </div>
                      <span className="text-slate-300 flex-1 text-xs">{action}</span>
                      {i === 0 ? (
                        <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded animate-pulse">
                          EXEC
                        </span>
                      ) : (
                        <span className="text-[10px] text-gray-600 px-2">PEND</span>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-slate-600 text-xs font-mono">
                  NO ACTIVE THREATS
                  <div className="text-green-500 text-[10px] mt-1">SYSTEM STANDBY</div>
                </div>
              )}
            </div>

            {/* Quick Actions - Mobile */}
            <div className="lg:hidden bg-slate-900/30 backdrop-blur-sm border border-purple-500/20 rounded-lg p-3">
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={toggleMonitoring}
                  className={`p-3 rounded-lg font-medium text-sm transition-colors ${
                    isMonitoring
                      ? 'bg-red-900/30 hover:bg-red-900/40 border border-red-500/50 text-red-400'
                      : 'bg-green-900/30 hover:bg-green-900/40 border border-green-500/50 text-green-400'
                  }`}
                >
                  {isMonitoring ? 'STOP' : 'ACTIVATE'}
                </button>
                
                <button
                  onClick={clearEvents}
                  className="p-3 rounded-lg font-medium text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  Clear Log
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Dashboard */}
          <div className="lg:col-span-2">
            <Dashboard
              events={events}
              stats={stats}
              isMonitoring={isMonitoring}
              toggleMonitoring={toggleMonitoring}
              lastAnalysis={currentAnalysis}
            />
          </div>
        </div>
      </main>

      {/* Modals */}
      {showSettings && (
        <SettingsPanel
          onClose={() => setShowSettings(false)}
          onSettingsChange={handleSettingsChange}
        />
      )}

      {showNotifications && (
        <NotificationsPanel
          onClose={() => setShowNotifications(false)}
          events={events}
        />
      )}

      {showEvidencePanel && (
        <EvidenceManager
          mode={showEvidencePanel}
          onClose={() => toggleEvidencePanel(null)}
          onUpload={uploadEvidence}
          onDownload={downloadEvidence}
          incidents={events.filter(e => e.incident)}
        />
      )}

      {/* Diagnostic Overlay */}
      <DiagnosticOverlay
        isMonitoring={isMonitoring}
        stats={stats}
        events={events}
        currentAnalysis={currentAnalysis}
        backendConnected={backendConnected}
      />

      {/* Footer - Hidden on mobile */}
      <footer className="hidden sm:block text-center text-xs text-slate-600 py-4 mt-8">
        <p>{SYSTEM_NAME} v{SYSTEM_VERSION} • Powered by Gemini 3 • Press 'D' for diagnostics</p>
      </footer>
    </div>
  );
}

export default App;