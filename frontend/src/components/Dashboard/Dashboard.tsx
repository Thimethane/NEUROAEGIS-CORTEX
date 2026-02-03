/**
 * Dashboard Component - Fixed Responsive Layout
 * Terminal logs are scrollable and don't affect video feed
 */

import React, { useEffect, useRef } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import type { SecurityEvent, SystemStats } from '../../types';
import { Activity, AlertTriangle, Eye, Cpu, Terminal } from 'lucide-react';

interface DashboardProps {
  events: SecurityEvent[];
  stats: SystemStats;
  isMonitoring: boolean;
  toggleMonitoring: () => void;
  lastAnalysis: SecurityEvent | null;
}

export const Dashboard: React.FC<DashboardProps> = ({
  events,
  stats,
  isMonitoring,
  toggleMonitoring,
  lastAnalysis
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal to bottom on new events
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const chartData = events.slice(-10).map((e) => ({
    time: new Date(e.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    confidence: e.confidence,
    severity:
      e.severity === 'critical' ? 100 :
      e.severity === 'high' ? 80 :
      e.severity === 'medium' ? 50 : 20
  }));

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-purple-400';
      case 'high':
        return 'text-red-500';
      case 'medium':
        return 'text-orange-400';
      case 'low':
        return 'text-blue-400';
      default:
        return 'text-gray-400';
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-purple-500/20 border-purple-500';
      case 'high':
        return 'bg-red-500/20 border-red-500';
      case 'medium':
        return 'bg-orange-500/20 border-orange-500';
      case 'low':
        return 'bg-blue-500/20 border-blue-500';
      default:
        return 'bg-gray-800 border-gray-700';
    }
  };

  return (
    <div className="flex flex-col h-full gap-3 sm:gap-4">

      {/* HEADER STATS */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4">

        <StatCard
          icon={Eye}
          iconColor="text-blue-400"
          iconBg="bg-blue-500/10"
          label="Scans"
          value={stats.scansPerformed}
        />

        <StatCard
          icon={AlertTriangle}
          iconColor={stats.incidentsDetected > 0 ? "text-red-500" : "text-green-500"}
          iconBg={stats.incidentsDetected > 0 ? "bg-red-500/10" : "bg-green-500/10"}
          label="Incidents"
          value={stats.incidentsDetected}
        />

        <StatCard
          icon={Cpu}
          iconColor="text-purple-400"
          iconBg="bg-purple-500/10"
          label="System Load"
          value={`${stats.cpuUsage}%`}
          showProgress
          progress={stats.cpuUsage}
        />

        {/* Toggle Button */}
        <div className="bg-slate-900/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-3 sm:p-4 shadow-lg">
          <button
            onClick={toggleMonitoring}
            className={`w-full h-full rounded flex flex-col items-center justify-center transition-all min-h-[60px] sm:min-h-0 ${
              isMonitoring
                ? 'bg-red-900/20 hover:bg-red-900/40 border border-red-500/50'
                : 'bg-green-900/20 hover:bg-green-900/40 border border-green-500/50'
            }`}
          >
            <div className={`text-[10px] sm:text-sm font-bold tracking-widest uppercase mb-1 ${
              isMonitoring ? 'text-red-400' : 'text-green-400'
            }`}>
              {isMonitoring ? 'STOP' : 'ACTIVATE'}
            </div>
            <div className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${
              isMonitoring ? 'bg-red-500 animate-pulse' : 'bg-green-500'
            }`} />
          </button>
        </div>
      </div>

      {/* MAIN GRID - Fixed Heights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4 flex-1 min-h-0">

        {/* LEFT - Analysis Section */}
        <div className="lg:col-span-2 flex flex-col gap-3 sm:gap-4 min-h-0">
          {/* Chart */}
          <div className="bg-slate-900/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-3 sm:p-4 shadow-lg">
            <h3 className="text-purple-400 font-mono text-xs sm:text-sm uppercase tracking-wider mb-3 flex items-center gap-2">
              <Activity size={14} /> Threat Analysis
            </h3>

            <div className="w-full h-[150px] sm:h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorConf" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#a78bfa" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} />
                  <YAxis stroke="#94a3b8" fontSize={10} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      color: '#f1f5f9',
                      fontSize: 12
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="confidence"
                    stroke="#a78bfa"
                    fill="url(#colorConf)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Latest Analysis */}
          <div className="bg-slate-900/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-3 sm:p-4 shadow-lg flex-shrink-0">
            <h4 className="text-gray-400 text-xs uppercase mb-2">Latest Analysis</h4>

            {lastAnalysis ? (
              <div className={`border p-3 rounded ${getSeverityBg(lastAnalysis.severity)}`}>
                <div className="flex justify-between mb-2 flex-wrap gap-2">
                  <span className={`font-mono text-sm sm:text-lg font-bold uppercase ${getSeverityColor(lastAnalysis.severity)}`}>
                    {lastAnalysis.incident ? '⚠️ THREAT' : '✓ SECURE'}
                  </span>
                  <span className="font-mono text-[10px] sm:text-xs text-gray-400">
                    {new Date(lastAnalysis.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 sm:gap-4 mb-2 text-xs sm:text-sm">
                  <div>
                    <p className="text-gray-500 text-[10px] sm:text-xs uppercase">Type</p>
                    <p className="text-white font-medium truncate">{lastAnalysis.type}</p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-[10px] sm:text-xs uppercase">Confidence</p>
                    <p className="text-white font-medium">{lastAnalysis.confidence}%</p>
                  </div>
                </div>

                <p className="text-slate-300 text-xs sm:text-sm italic line-clamp-2">
                  "{lastAnalysis.reasoning}"
                </p>
              </div>
            ) : (
              <div className="text-center py-4 sm:py-8 text-gray-600 font-mono text-xs sm:text-sm">
                Awaiting analysis...
              </div>
            )}
          </div>
        </div>

        {/* RIGHT - Terminal (Scrollable) */}
        <div className="bg-black border border-purple-500/20 rounded-lg shadow-lg flex flex-col font-mono text-[10px] sm:text-xs overflow-hidden min-h-[300px] lg:min-h-0">

          <div className="flex justify-between px-3 py-2 border-b border-gray-800 flex-shrink-0">
            <span className="flex gap-2 text-gray-400 items-center">
              <Terminal size={12} /> SYSTEM_LOG
            </span>
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <div className="w-2 h-2 rounded-full bg-yellow-500" />
              <div className="w-2 h-2 rounded-full bg-green-500" />
            </div>
          </div>

          {/* Scrollable Terminal Content */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto space-y-2 p-2 scroll-smooth"
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: '#6b21a8 #0a0a0a'
            }}
          >
            {events.length === 0 ? (
              <div className="text-gray-600 text-center py-8">
                No events logged yet
              </div>
            ) : (
              events.map((e) => (
                <div
                  key={e.id}
                  className="border-l-2 border-slate-700 pl-2 hover:border-purple-500 transition-colors"
                >
                  <div className="flex flex-wrap gap-1">
                    <span className="text-gray-500">
                      [{new Date(e.timestamp).toLocaleTimeString()}]
                    </span>
                    <span className={e.incident ? 'text-red-400' : 'text-green-400'}>
                      {e.incident ? 'ALRT' : 'INFO'}
                    </span>
                    <span className="text-blue-300">@{e.type}</span>
                  </div>
                  <p className="text-gray-300 text-[10px] sm:text-xs mt-1">
                    {e.reasoning}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper Component
const StatCard: React.FC<{
  icon: any;
  iconColor: string;
  iconBg: string;
  label: string;
  value: number | string;
  showProgress?: boolean;
  progress?: number;
}> = ({ icon: Icon, iconColor, iconBg, label, value, showProgress, progress }) => (
  <div className="bg-slate-900/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-3 sm:p-4 flex items-center gap-3 sm:gap-4 shadow-lg">
    <div className={`p-2 sm:p-3 ${iconBg} rounded-full ${iconColor} flex-shrink-0`}>
      <Icon size={20} className="sm:w-6 sm:h-6" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-slate-400 text-[10px] sm:text-xs uppercase tracking-wider truncate">
        {label}
      </p>
      <div className="flex items-end gap-2">
        <p className="text-lg sm:text-2xl font-mono font-bold text-white">
          {value}
        </p>
        {showProgress && progress !== undefined && (
          <div className="h-1.5 w-12 sm:w-16 bg-gray-700 rounded-full mb-1 flex-shrink-0">
            <div
              className="h-full bg-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  </div>
);

export default Dashboard;
