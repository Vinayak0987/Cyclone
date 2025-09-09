#!/usr/bin/env python3
"""
Notification Service for AstroAlert
Handles email and SMS notifications for alerts
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import requests
import json
import datetime

from database import db

class NotificationService:
    def __init__(self):
        """Initialize notification service with email and SMS configurations"""
        # Email configuration (using environment variables for security)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # SMS configuration (using Twilio or similar service)
        self.sms_service_url = os.getenv('SMS_SERVICE_URL')
        self.sms_api_key = os.getenv('SMS_API_KEY')
        
        print("📧 Notification Service initialized")

    def send_email(self, recipient_email: str, subject: str, message: str, is_html: bool = False) -> bool:
        """
        Send email notification
        
        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            message: Email content
            is_html: Whether message content is HTML
            
        Returns:
            Success status
        """
        try:
            if not self.email_user or not self.email_password:
                print("⚠️ Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Attach message
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, recipient_email, text)
            server.quit()
            
            print(f"✅ Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {recipient_email}: {e}")
            return False

    def send_sms(self, recipient_phone: str, message: str) -> bool:
        """
        Send SMS notification
        
        Args:
            recipient_phone: Recipient's phone number
            message: SMS content
            
        Returns:
            Success status
        """
        try:
            if not self.sms_service_url or not self.sms_api_key:
                print("⚠️ SMS service not configured - simulating SMS")
                print(f"📱 SMS to {recipient_phone}: {message[:100]}...")
                return True  # Simulate successful SMS for demo
            
            # Example API call (adjust based on your SMS provider)
            payload = {
                'to': recipient_phone,
                'message': message,
                'api_key': self.sms_api_key
            }
            
            response = requests.post(self.sms_service_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SMS sent to {recipient_phone}")
                return True
            else:
                print(f"❌ Failed to send SMS to {recipient_phone}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send SMS to {recipient_phone}: {e}")
            return False

    def send_alert_notifications(self, user: Dict, alert_id: str, message: str, risk_level: str):
        """
        Send alert notifications via email and SMS
        
        Args:
            user: User information dictionary
            alert_id: Alert ID from database
            message: Alert message content
            risk_level: Risk level (LOW, MODERATE, HIGH, EXTREME)
        """
        print(f"📨 Sending alert notifications for {risk_level} risk to {user['name']}")
        
        # Determine urgency based on risk level
        urgency_map = {
            'LOW': ('📊', 'Info'),
            'MODERATE': ('⚠️', 'Warning'), 
            'HIGH': ('🚨', 'High Alert'),
            'EXTREME': ('🆘', 'EMERGENCY')
        }
        
        icon, urgency_text = urgency_map.get(risk_level, ('ℹ️', 'Alert'))
        
        # Email notification
        if user.get('email'):
            email_subject = f"{icon} AstroAlert {urgency_text}: Cyclone Risk Detected"
            email_message = self._format_email_message(message, risk_level, user['name'])
            
            email_success = self.send_email(user['email'], email_subject, email_message, is_html=True)
            
            # Record email notification
            self._record_notification(user['id'], alert_id, 'EMAIL', user['email'], 
                                    email_subject, email_message, email_success)
        
        # SMS notification (for HIGH and EXTREME alerts)
        if user.get('phone') and risk_level in ['HIGH', 'EXTREME']:
            sms_message = self._format_sms_message(message, risk_level)
            
            sms_success = self.send_sms(user['phone'], sms_message)
            
            # Record SMS notification
            self._record_notification(user['id'], alert_id, 'SMS', user['phone'],
                                    None, sms_message, sms_success)

    def _format_email_message(self, message: str, risk_level: str, user_name: str) -> str:
        """Format email message with HTML styling"""
        # Color scheme based on risk level
        color_map = {
            'LOW': '#28a745',
            'MODERATE': '#ffc107', 
            'HIGH': '#fd7e14',
            'EXTREME': '#dc3545'
        }
        
        color = color_map.get(risk_level, '#6c757d')
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ padding: 30px; }}
                .risk-level {{ font-size: 24px; font-weight: bold; color: {color}; margin: 10px 0; }}
                .message {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; white-space: pre-line; }}
                .footer {{ background: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; color: #6c757d; font-size: 12px; }}
                .cta {{ background: {color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌪️ AstroAlert Notification</h1>
                </div>
                <div class="content">
                    <p>Dear {user_name},</p>
                    <div class="risk-level">Risk Level: {risk_level}</div>
                    <div class="message">{message}</div>
                    <p>Please review your AstroAlert dashboard for detailed analysis and recommendations.</p>
                    <a href="#" class="cta">View Dashboard</a>
                    <p><strong>Stay Safe!</strong><br>
                    The AstroAlert Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from AstroAlert Cyclone Monitoring System.<br>
                    Generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_message

    def _format_sms_message(self, message: str, risk_level: str) -> str:
        """Format SMS message (keeping it short due to character limits)"""
        lines = message.strip().split('\n')
        
        # Extract key information
        location = next((line for line in lines if 'ALERT:' in line), 'Unknown Location')
        risk_score = next((line for line in lines if 'Risk Score:' in line), '')
        action = next((line for line in lines if 'Action Required:' in line), '')
        
        sms = f"🌪️ {location}\n{risk_score}\n{action}\n\nCheck AstroAlert dashboard for details."
        
        # Truncate if too long (SMS limit ~160 characters)
        if len(sms) > 160:
            sms = f"🌪️ CYCLONE ALERT: {risk_level} risk detected. Check AstroAlert dashboard immediately."
        
        return sms

    def _record_notification(self, user_id: str, alert_id: str, notification_type: str, 
                           recipient: str, subject: str, content: str, success: bool):
        """Record notification in database"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications 
                    (id, user_id, alert_id, notification_type, recipient, subject, content, status, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"notif_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{notification_type.lower()}",
                    user_id, alert_id, notification_type, recipient, subject, content,
                    'SENT' if success else 'FAILED',
                    datetime.datetime.now() if success else None
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Failed to record notification: {e}")

    def send_test_notifications(self, user_email: str, user_phone: str = None):
        """Send test notifications to verify configuration"""
        print("🧪 Sending test notifications...")
        
        test_message = """
🌪️ TEST ALERT: AstroAlert System Test

This is a test notification to verify your notification settings are working correctly.

Risk Level: LOW (Test)
Location: Test Location
Risk Score: 25.0/100

If you received this message, your notifications are configured properly!

Test conducted at: """ + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Test email
        email_success = self.send_email(
            user_email,
            "🧪 AstroAlert Test Notification",
            self._format_email_message(test_message, 'LOW', 'Test User'),
            is_html=True
        )
        
        # Test SMS if phone provided
        sms_success = True
        if user_phone:
            sms_success = self.send_sms(user_phone, "🧪 AstroAlert test: Notifications working!")
        
        return {
            'email_sent': email_success,
            'sms_sent': sms_success if user_phone else None,
            'timestamp': datetime.datetime.now().isoformat()
        }

# Global notification service instance
notification_service = NotificationService()

if __name__ == "__main__":
    print("📧 Testing Notification Service")
    print("=" * 40)
    
    # Test email (you can replace with your email)
    test_result = notification_service.send_test_notifications("test@example.com")
    print(f"Test results: {test_result}")
    
    print("✅ Notification service test completed")