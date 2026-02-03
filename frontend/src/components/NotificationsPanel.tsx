/**
 * Notifications Panel Component
 * Displays system notifications and alerts
 */

import React, { useState, useEffect } from 'react';
import {
  X, Bell, AlertTriangle, Info, CheckCircle, XCircle, Trash2, Filter
} from 'lucide-react';
import { STORAGE_KEYS } from '../constants';
import type { SecurityEvent } from '../types';

interface NotificationsProps {
  onClose: () => void;
  events: SecurityEvent[];
}

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  eventId?: string;
}

export const NotificationsPanel: React.FC<NotificationsProps> = ({ onClose, events }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<'all' | 'unread' | 'incidents'>('all');

  // Load and generate notifications
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.NOTIFICATIONS);
    let existingNotifs: Notification[] = stored ? JSON.parse(stored) : [];

    // Generate notifications from recent events
    const eventNotifs: Notification[] = events.map(event => ({
      id: `event_${event.id}`,
      type: event.incident 
        ? (event.severity === 'critical' || event.severity === 'high' ? 'error' : 'warning')
        : 'info',
      title: event.incident ? `Security Alert: ${event.type}` : 'Analysis Complete',
      message: event.reasoning,
      timestamp: event.timestamp,
      read: false,
      eventId: event.id
    }));

    // Merge and deduplicate
    const merged = [...eventNotifs, ...existingNotifs];
    const unique = merged.filter((notif, index, self) => 
      index === self.findIndex(n => n.id === notif.id)
    );

    // Sort by timestamp (newest first)
    unique.sort((a, b) => b.timestamp - a.timestamp);

    setNotifications(unique.slice(0, 100)); // Keep last 100
  }, [events]);

  // Save notifications when they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(notifications));
  }, [notifications]);

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    if (confirm('Clear all notifications?')) {
      setNotifications([]);
    }
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read;
    if (filter === 'incidents') return n.type === 'error' || n.type === 'warning';
    return true;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  const getIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertTriangle className="text-red-500" size={20} />;
      case 'warning':
        return <AlertTriangle className="text-orange-500" size={20} />;
      case 'success':
        return <CheckCircle className="text-green-500" size={20} />;
      default:
        return <Info className="text-blue-500" size={20} />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-purple-500/30 rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg relative">
              <Bell className="text-purple-400" size={24} />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Notifications</h2>
              <p className="text-sm text-slate-400">
                {unreadCount} unread • {filteredNotifications.length} total
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="text-slate-400" size={20} />
          </button>
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-slate-900/50">
          <div className="flex gap-2">
            <FilterButton
              active={filter === 'all'}
              onClick={() => setFilter('all')}
              label="All"
            />
            <FilterButton
              active={filter === 'unread'}
              onClick={() => setFilter('unread')}
              label="Unread"
              count={unreadCount}
            />
            <FilterButton
              active={filter === 'incidents'}
              onClick={() => setFilter('incidents')}
              label="Incidents"
            />
          </div>
          
          <div className="flex gap-2">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-xs px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded transition-colors"
              >
                Mark all read
              </button>
            )}
            <button
              onClick={clearAll}
              className="text-xs px-3 py-1 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded transition-colors flex items-center gap-1"
            >
              <Trash2 size={12} />
              Clear
            </button>
          </div>
        </div>

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Bell size={48} className="mx-auto mb-3 opacity-50" />
              <p>No notifications</p>
            </div>
          ) : (
            filteredNotifications.map(notif => (
              <NotificationCard
                key={notif.id}
                notification={notif}
                onRead={() => markAsRead(notif.id)}
                onDelete={() => deleteNotification(notif.id)}
                getIcon={getIcon}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Helper Components
const FilterButton: React.FC<{
  active: boolean;
  onClick: () => void;
  label: string;
  count?: number;
}> = ({ active, onClick, label, count }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      active
        ? 'bg-purple-600 text-white'
        : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
    }`}
  >
    {label}
    {count !== undefined && count > 0 && (
      <span className="ml-2 px-2 py-0.5 bg-white/20 rounded-full text-xs">
        {count}
      </span>
    )}
  </button>
);

const NotificationCard: React.FC<{
  notification: Notification;
  onRead: () => void;
  onDelete: () => void;
  getIcon: (type: string) => React.ReactNode;
}> = ({ notification, onRead, onDelete, getIcon }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`p-4 rounded-lg border transition-all ${
        notification.read
          ? 'bg-slate-800/50 border-slate-700'
          : 'bg-slate-800 border-purple-500/30 shadow-lg'
      }`}
      onClick={() => {
        if (!notification.read) onRead();
        setExpanded(!expanded);
      }}
    >
      <div className="flex items-start gap-3 cursor-pointer">
        {getIcon(notification.type)}
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <h4 className={`font-medium ${notification.read ? 'text-slate-300' : 'text-white'}`}>
              {notification.title}
            </h4>
            {!notification.read && (
              <div className="w-2 h-2 bg-purple-500 rounded-full flex-shrink-0" />
            )}
          </div>
          
          <p className={`text-sm ${notification.read ? 'text-slate-500' : 'text-slate-400'} ${
            expanded ? '' : 'line-clamp-2'
          }`}>
            {notification.message}
          </p>
          
          <p className="text-xs text-slate-600 mt-2">
            {new Date(notification.timestamp).toLocaleString()}
          </p>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="p-1 hover:bg-slate-700 rounded transition-colors flex-shrink-0"
        >
          <X className="text-slate-500" size={16} />
        </button>
      </div>
    </div>
  );
};

// Default and named exports
export default NotificationsPanel;
