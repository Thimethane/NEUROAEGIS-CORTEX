/**
 * Notification Service - Integrated with Settings
 * Sends email notifications when enabled
 */

import React from 'react';
import { SecurityEvent } from '../types';
import { SystemSettings } from '../components/SettingsPanel';
import { API_CONFIG, EMAIL_TEMPLATE } from '../constants';

class NotificationService {
  private settings: SystemSettings | null = null;

  /**
   * Initialize with user settings
   */
  initialize(settings: SystemSettings) {
    this.settings = settings;
    console.log('📬 Notification service initialized');
    console.log(`   Email alerts: ${settings.emailAlerts ? 'ENABLED' : 'DISABLED'}`);
    console.log(`   Sound alerts: ${settings.soundAlerts ? 'ENABLED' : 'DISABLED'}`);
  }

  /**
   * Send notification for an incident
   */
  async sendNotification(incident: SecurityEvent): Promise<boolean> {
    if (!this.settings) {
      console.warn('Notification service not initialized');
      return false;
    }

    // Only send for actual incidents
    if (!incident.incident) {
      return false;
    }

    // Check severity threshold
    const highSeverity = incident.severity === 'high' || incident.severity === 'critical';

    // Send email if enabled and configured
    if (this.settings.emailAlerts && this.settings.alertEmail && highSeverity) {
      await this.sendEmailNotification(incident);
    }

    // Play sound if enabled
    if (this.settings.soundAlerts && highSeverity) {
      this.playAlertSound();
    }

    // Browser notification if permitted
    if (highSeverity) {
      this.showBrowserNotification(incident);
    }

    return true;
  }

  /**
   * Send email notification via backend
   */
  private async sendEmailNotification(incident: SecurityEvent): Promise<boolean> {
    if (!this.settings?.alertEmail) {
      return false;
    }

    try {
      console.log(`📧 Sending email alert to ${this.settings.alertEmail}...`);

      const emailData = {
        id: incident.id || 'N/A',
        type: incident.type,
        severity: incident.severity,
        confidence: incident.confidence,
        reasoning: incident.reasoning,
        timestamp: incident.timestamp,
        recommended_actions: incident.recommended_actions || []
      };

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/email/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          to: this.settings.alertEmail,
          from_: this.settings.alertEmail, // Use same email or configure separately
          subject: EMAIL_TEMPLATE.subject(emailData.id),
          html: EMAIL_TEMPLATE.body(emailData),
          smtpConfig: {
            host: 'smtp.gmail.com',
            port: 587,
            user: this.settings.alertEmail,
            pass_: '' // User needs to configure in backend .env
          }
        })
      });

      if (response.ok) {
        console.log('✅ Email notification sent successfully');
        return true;
      } else {
        const error = await response.json().catch(() => ({}));
        console.error('❌ Email notification failed:', error);
        return false;
      }

    } catch (error) {
      console.error('❌ Email notification error:', error);
      return false;
    }
  }

  /**
   * Play alert sound
   */
  private playAlertSound() {
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'sawtooth';
      gainNode.gain.value = 0.1;

      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.5);

      console.log('🔊 Alert sound played');
    } catch (error) {
      console.error('Sound playback error:', error);
    }
  }

  /**
   * Show browser notification
   */
  private async showBrowserNotification(incident: SecurityEvent) {
    // Request permission if not granted
    if (Notification.permission === 'default') {
      await Notification.requestPermission();
    }

    if (Notification.permission === 'granted') {
      try {
        new Notification('🚨 NeuroAegisCortex Alert', {
          body: `${incident.type}: ${incident.reasoning}`,
          icon: '/favicon.ico',
          badge: '/favicon.ico',
          tag: incident.id,
          requireInteraction: incident.severity === 'critical'
        });

        console.log('🔔 Browser notification shown');
      } catch (error) {
        console.error('Browser notification error:', error);
      }
    }
  }

  /**
   * Test notification system
   */
  async testNotifications(): Promise<void> {
    if (!this.settings) {
      console.error('Notification service not initialized');
      return;
    }

    const testIncident: SecurityEvent = {
      id: 'test-notification',
      timestamp: Date.now(),
      incident: true,
      type: 'test_alert',
      severity: 'high',
      confidence: 99,
      reasoning: 'This is a test notification from NeuroAegisCortex',
      subjects: [],
      recommended_actions: ['Verify notification settings', 'Check email inbox']
    };

    console.log('🧪 Testing notification system...');
    await this.sendNotification(testIncident);
  }
}

// Singleton instance
export const notificationService = new NotificationService();

/**
 * Hook to use notifications with settings
 */
export const useNotifications = (settings: SystemSettings) => {
  // Initialize service when settings change
  React.useEffect(() => {
    notificationService.initialize(settings);
  }, [settings]);

  return {
    sendNotification: (incident: SecurityEvent) => 
      notificationService.sendNotification(incident),
    testNotifications: () => 
      notificationService.testNotifications()
  };
};
