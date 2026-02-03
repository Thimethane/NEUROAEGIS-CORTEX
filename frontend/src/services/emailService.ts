/**
 * Email Service - Gmail SMTP Integration
 * Sends security alerts via email
 */

import { EMAIL_TEMPLATE } from '../constants';
import type { SecurityEvent } from '../types';

interface EmailConfig {
  smtpHost: string;
  smtpPort: number;
  smtpUser: string;
  smtpPassword: string;
  fromEmail: string;
  toEmail: string;
}

class EmailService {
  private config: EmailConfig | null = null;

  /**
   * Initialize email service with Gmail SMTP settings
   */
  initialize(config: Partial<EmailConfig>) {
    this.config = {
      smtpHost: config.smtpHost || 'smtp.gmail.com',
      smtpPort: config.smtpPort || 587,
      smtpUser: config.smtpUser || '',
      smtpPassword: config.smtpPassword || '',
      fromEmail: config.fromEmail || config.smtpUser || '',
      toEmail: config.toEmail || ''
    };

    console.log('📧 Email service initialized');
  }

  /**
   * Send alert email for security incident
   */
  async sendAlert(incident: SecurityEvent): Promise<boolean> {
    if (!this.config || !this.config.toEmail) {
      console.warn('Email service not configured');
      return false;
    }

    try {
      // Format incident data
      const emailData = {
        id: incident.id || 'N/A',
        type: incident.type,
        severity: incident.severity,
        confidence: incident.confidence,
        reasoning: incident.reasoning,
        timestamp: incident.timestamp,
        recommended_actions: incident.recommended_actions || []
      };

      const emailPayload = {
        to: this.config.toEmail,
        from: this.config.fromEmail,
        subject: EMAIL_TEMPLATE.subject(Number(emailData.id)),
        html: EMAIL_TEMPLATE.body(emailData),
        smtpConfig: {
          host: this.config.smtpHost,
          port: this.config.smtpPort,
          user: this.config.smtpUser,
          pass: this.config.smtpPassword
        }
      };

      // Send via backend API if available
      const response = await fetch('/api/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(emailPayload)
      });

      if (response.ok) {
        console.log('✅ Alert email sent successfully');
        return true;
      } else {
        const error = await response.json();
        console.error('Email send failed:', error);
        return false;
      }

    } catch (error) {
      console.error('Email service error:', error);
      return false;
    }
  }

  /**
   * Test email configuration
   */
  async testConnection(): Promise<boolean> {
    if (!this.config) {
      console.error('Email service not initialized');
      return false;
    }

    try {
      const testPayload = {
        to: this.config.toEmail,
        from: this.config.fromEmail,
        subject: '🛡️ NeuroAegisCortex Test Email',
        html: `
          <html>
            <body style="font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; padding: 20px;">
              <div style="max-width: 600px; margin: 0 auto; background: #2a2a2a; padding: 30px; border-radius: 10px;">
                <h2 style="color: #a78bfa;">✅ Email Configuration Test</h2>
                <p>If you're reading this, your email alerts are properly configured!</p>
                <p style="color: #888; font-size: 12px; margin-top: 30px;">
                  This is a test message from NeuroAegisCortex
                </p>
              </div>
            </body>
          </html>
        `,
        smtpConfig: {
          host: this.config.smtpHost,
          port: this.config.smtpPort,
          user: this.config.smtpUser,
          pass: this.config.smtpPassword
        }
      };

      const response = await fetch('/api/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testPayload)
      });

      if (response.ok) {
        console.log('✅ Test email sent successfully');
        return true;
      } else {
        console.error('Test email failed:', await response.text());
        return false;
      }

    } catch (error) {
      console.error('Email test error:', error);
      return false;
    }
  }

  /**
   * Check if email service is configured
   */
  isConfigured(): boolean {
    return this.config !== null && 
           this.config.toEmail !== '' &&
           this.config.smtpUser !== '';
  }

  /**
   * Get current configuration (without password)
   */
  getConfig(): Partial<EmailConfig> | null {
    if (!this.config) return null;

    return {
      smtpHost: this.config.smtpHost,
      smtpPort: this.config.smtpPort,
      smtpUser: this.config.smtpUser,
      fromEmail: this.config.fromEmail,
      toEmail: this.config.toEmail
    };
  }
}

// Singleton instance
export const emailService = new EmailService();

// Gmail-specific helper
export const configureGmail = (email: string, appPassword: string, toEmail: string) => {
  emailService.initialize({
    smtpHost: 'smtp.gmail.com',
    smtpPort: 587,
    smtpUser: email,
    smtpPassword: appPassword, // Use Gmail App Password, not regular password
    fromEmail: email,
    toEmail: toEmail
  });
};

/**
 * Instructions for setting up Gmail App Password:
 * 
 * 1. Go to myaccount.google.com
 * 2. Security → 2-Step Verification (must be enabled)
 * 3. Security → App passwords
 * 4. Select "Mail" and "Other (Custom name)"
 * 5. Generate and copy the 16-character password
 * 6. Use this password, NOT your regular Gmail password
 * 
 * Example:
 * configureGmail(
 *   'your-email@gmail.com',
 *   'abcd efgh ijkl mnop',  // App password
 *   'security-team@company.com'
 * );
 */