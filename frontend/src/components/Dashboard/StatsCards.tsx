/**
 * StatsCards Component
 * Displays system statistics in card format
 */

import React from 'react';
import { Eye, AlertTriangle, Cpu } from 'lucide-react';
import type { SystemStats } from '../../types';

interface StatsCardsProps {
  stats: SystemStats;
  isMonitoring: boolean;
  toggleMonitoring: () => void;
}

export const StatsCards: React.FC<StatsCardsProps> = ({
  stats,
  isMonitoring,
  toggleMonitoring
}) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {/* Scans Performed */}
      <StatCard
        icon={<Eye size={24} />}
        label="Scans Performed"
        value={stats.scansPerformed}
        iconBgColor="bg-blue-500/10"
        iconColor="text-blue-400"
      />

      {/* Incidents Detected */}
      <StatCard
        icon={<AlertTriangle size={24} />}
        label="Incidents"
        value={stats.incidentsDetected}
        iconBgColor={
          stats.incidentsDetected > 0 
            ? 'bg-red-500/10' 
            : 'bg-green-500/10'
        }
        iconColor={
          stats.incidentsDetected > 0 
            ? 'text-red-500' 
            : 'text-green-500'
        }
      />

      {/* System Load */}
      <div className="bg-aegis-panel border border-slate-700 rounded-lg p-4 flex items-center gap-4 shadow-lg">
        <div className="p-3 bg-purple-500/10 rounded-full text-purple-400">
          <Cpu size={24} />
        </div>
        <div className="flex-1">
          <p className="text-slate-400 text-xs uppercase tracking-wider">
            System Load
          </p>
          <div className="flex items-end gap-2">
            <p className="text-2xl font-mono font-bold text-white">
              {stats.cpuUsage}%
            </p>
            <div className="h-1.5 w-16 bg-gray-700 rounded-full mb-2">
              <div
                className="h-full bg-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${stats.cpuUsage}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Toggle Monitoring Button */}
      <div className="bg-aegis-panel border border-slate-700 rounded-lg p-4 shadow-lg">
        <button
          onClick={toggleMonitoring}
          className={`w-full h-full rounded flex flex-col items-center justify-center transition-all ${
            isMonitoring
              ? 'bg-red-900/20 hover:bg-red-900/40 border border-red-500/50'
              : 'bg-green-900/20 hover:bg-green-900/40 border border-green-500/50'
          }`}
        >
          <div
            className={`text-sm font-bold tracking-widest uppercase mb-1 ${
              isMonitoring ? 'text-red-400' : 'text-green-400'
            }`}
          >
            {isMonitoring ? 'STOP SURVEILLANCE' : 'ACTIVATE AEGIS'}
          </div>
          <div
            className={`w-3 h-3 rounded-full ${
              isMonitoring
                ? 'bg-red-500 animate-pulse'
                : 'bg-green-500'
            }`}
          />
        </button>
      </div>
    </div>
  );
};

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  iconBgColor: string;
  iconColor: string;
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  value,
  iconBgColor,
  iconColor
}) => {
  return (
    <div className="bg-aegis-panel border border-slate-700 rounded-lg p-4 flex items-center gap-4 shadow-lg">
      <div className={`p-3 ${iconBgColor} rounded-full ${iconColor}`}>
        {icon}
      </div>
      <div>
        <p className="text-slate-400 text-xs uppercase tracking-wider">
          {label}
        </p>
        <p className="text-2xl font-mono font-bold text-white">{value}</p>
      </div>
    </div>
  );
};
