/**
 * Settings Panel Component
 * Manages system configuration and preferences
 */

import React, { useState, useEffect } from 'react';
import {
  X, Settings as SettingsIcon, Save, RotateCcw,
  Bell, Mail, Shield, Video, Zap, Trash2
} from 'lucide-react';
import { STORAGE_KEYS, DEFAULT_SETTINGS } from '../constants';

interface SettingsProps {
  onClose: () => void;
  onSettingsChange: (settings: SystemSettings) => void;
}

export interface SystemSettings {
  videoQuality: 'low' | 'medium' | 'high';
  analysisInterval: number;
  soundAlerts: boolean;
  emailAlerts: boolean;
  alertEmail: string;
  confidenceThreshold: number;
  autoEscalate: boolean;
  showConfidence: boolean;
  showRecommendations: boolean;
  theme: 'light' | 'dark';
  maxStoredEvents: number;
  autoCleanupDays: number;
}

export const SettingsPanel: React.FC<SettingsProps> = ({ onClose, onSettingsChange }) => {
  const [settings, setSettings] = useState<SystemSettings>(DEFAULT_SETTINGS);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');

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

  const handleChange = <K extends keyof SystemSettings>(
    key: K,
    value: SystemSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = () => {
    setSaveStatus('saving');
    
    try {
      localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
      onSettingsChange(settings);
      
      setSaveStatus('saved');
      setTimeout(() => {
        setSaveStatus('idle');
        setHasChanges(false);
      }, 2000);
    } catch (e) {
      console.error('Failed to save settings:', e);
      setSaveStatus('idle');
    }
  };

  const handleReset = () => {
    if (confirm('Reset all settings to defaults?')) {
      setSettings(DEFAULT_SETTINGS);
      setHasChanges(true);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-purple-500/30 rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl my-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <SettingsIcon className="text-purple-400" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">System Settings</h2>
              <p className="text-sm text-slate-400">Configure NeuroAegisCortex</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="text-slate-400" size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Video Settings */}
          <SettingsSection icon={Video} title="Video Analysis">
            <SettingRow
              label="Video Quality"
              description="Higher quality uses more bandwidth"
            >
              <select
                value={settings.videoQuality}
                onChange={(e) => handleChange('videoQuality', e.target.value as any)}
                className="bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:border-purple-500 outline-none"
              >
                <option value="low">Low (640x480)</option>
                <option value="medium">Medium (1280x720)</option>
                <option value="high">High (1920x1080)</option>
              </select>
            </SettingRow>

            <SettingRow
              label="Analysis Interval"
              description="Time between frame analyses (ms)"
            >
              <input
                type="number"
                min="2000"
                max="10000"
                step="1000"
                value={settings.analysisInterval}
                onChange={(e) => handleChange('analysisInterval', parseInt(e.target.value))}
                className="bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white w-32 focus:border-purple-500 outline-none"
              />
            </SettingRow>
          </SettingsSection>

          {/* Alert Settings */}
          <SettingsSection icon={Bell} title="Alerts & Notifications">
            <SettingRow
              label="Sound Alerts"
              description="Play audio for high-severity incidents"
            >
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.soundAlerts}
                  onChange={(e) => handleChange('soundAlerts', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </SettingRow>

            <SettingRow
              label="Email Alerts"
              description="Send email notifications for incidents"
            >
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.emailAlerts}
                  onChange={(e) => handleChange('emailAlerts', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </SettingRow>

            {settings.emailAlerts && (
              <SettingRow
                label="Alert Email"
                description="Email address for security alerts"
              >
                <input
                  type="email"
                  value={settings.alertEmail}
                  onChange={(e) => handleChange('alertEmail', e.target.value)}
                  placeholder="security@company.com"
                  className="bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white w-full max-w-xs focus:border-purple-500 outline-none"
                />
              </SettingRow>
            )}
          </SettingsSection>

          {/* Security Settings */}
          <SettingsSection icon={Shield} title="Security & Detection">
            <SettingRow
              label="Confidence Threshold"
              description="Minimum confidence to trigger alerts (%)"
            >
              <div className="flex items-center gap-3 w-64">
                <input
                  type="range"
                  min="50"
                  max="95"
                  step="5"
                  value={settings.confidenceThreshold}
                  onChange={(e) => handleChange('confidenceThreshold', parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="text-white font-mono w-12 text-right">
                  {settings.confidenceThreshold}%
                </span>
              </div>
            </SettingRow>

            <SettingRow
              label="Auto-Escalate"
              description="Automatically escalate critical threats"
            >
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.autoEscalate}
                  onChange={(e) => handleChange('autoEscalate', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </SettingRow>
          </SettingsSection>

          {/* Performance Settings */}
          <SettingsSection icon={Zap} title="Performance & Storage">
            <SettingRow
              label="Max Stored Events"
              description="Maximum number of events in memory"
            >
              <input
                type="number"
                min="50"
                max="500"
                step="50"
                value={settings.maxStoredEvents}
                onChange={(e) => handleChange('maxStoredEvents', parseInt(e.target.value))}
                className="bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white w-32 focus:border-purple-500 outline-none"
              />
            </SettingRow>

            <SettingRow
              label="Auto-Cleanup (days)"
              description="Delete events older than N days"
            >
              <input
                type="number"
                min="7"
                max="90"
                step="7"
                value={settings.autoCleanupDays}
                onChange={(e) => handleChange('autoCleanupDays', parseInt(e.target.value))}
                className="bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white w-32 focus:border-purple-500 outline-none"
              />
            </SettingRow>
          </SettingsSection>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-700 flex justify-between items-center bg-slate-900/50">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            <RotateCcw size={16} />
            Reset to Defaults
          </button>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges || saveStatus === 'saving'}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors ${
                saveStatus === 'saved'
                  ? 'bg-green-600 text-white'
                  : hasChanges
                  ? 'bg-purple-600 hover:bg-purple-700 text-white'
                  : 'bg-slate-700 text-slate-500 cursor-not-allowed'
              }`}
            >
              <Save size={16} />
              {saveStatus === 'saving' ? 'Saving...' : saveStatus === 'saved' ? 'Saved!' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper Components
const SettingsSection: React.FC<{
  icon: any;
  title: string;
  children: React.ReactNode;
}> = ({ icon: Icon, title, children }) => (
  <div className="space-y-4">
    <div className="flex items-center gap-2 pb-2 border-b border-slate-700">
      <Icon size={18} className="text-purple-400" />
      <h3 className="text-lg font-semibold text-white">{title}</h3>
    </div>
    <div className="space-y-4 pl-2">
      {children}
    </div>
  </div>
);

const SettingRow: React.FC<{
  label: string;
  description: string;
  children: React.ReactNode;
}> = ({ label, description, children }) => (
  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 py-2">
    <div className="flex-1">
      <label className="text-white font-medium block">{label}</label>
      <p className="text-sm text-slate-400">{description}</p>
    </div>
    <div className="sm:ml-4">
      {children}
    </div>
  </div>
);
