#!/usr/bin/env python3
"""
Background Monitoring Service for AstroAlert
Monitors multiple locations and triggers alerts automatically
"""

import threading
import time
import schedule
import datetime
from typing import List, Dict
import json
import os

from database import db
from main_astroalert_fixed import AstroAlert
from notification_service import NotificationService

class MonitoringService:
    def __init__(self, check_interval_minutes: int = 30):
        """
        Initialize monitoring service
        
        Args:
            check_interval_minutes: How often to check locations (in minutes)
        """
        self.check_interval = check_interval_minutes
        self.astroalert = AstroAlert()
        self.notification_service = NotificationService()
        self.monitoring_active = False
        self.monitoring_thread = None
        
        print(f"🔍 Monitoring Service initialized (check every {check_interval_minutes} minutes)")

    def start_monitoring(self):
        """Start the background monitoring service"""
        if self.monitoring_active:
            print("⚠️ Monitoring already active")
            return
            
        self.monitoring_active = True
        
        # Schedule regular checks
        schedule.every(self.check_interval).minutes.do(self.check_all_locations)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.monitoring_thread.start()
        
        print("🚀 Background monitoring started")

    def stop_monitoring(self):
        """Stop the background monitoring service"""
        self.monitoring_active = False
        schedule.clear()
        print("⏹️ Background monitoring stopped")

    def _run_scheduler(self):
        """Run the scheduler in background thread"""
        while self.monitoring_active:
            schedule.run_pending()
            time.sleep(1)

    def check_all_locations(self):
        """Check all active monitoring locations"""
        print(f"\n🔍 Starting scheduled location check - {datetime.datetime.now()}")
        
        try:
            # Get all locations with monitoring enabled
            locations = db.get_active_locations()
            
            if not locations:
                print("📍 No locations to monitor")
                return
            
            print(f"📍 Checking {len(locations)} locations...")
            
            for location in locations:
                try:
                    self.check_location(location)
                except Exception as e:
                    print(f"❌ Error checking location {location['name']}: {e}")
            
            print("✅ Scheduled check completed")
            
        except Exception as e:
            print(f"❌ Error during scheduled check: {e}")

    def check_location(self, location: Dict):
        """Check a specific location for cyclone risk"""
        print(f"  🌍 Checking {location['name']} ({location['latitude']}, {location['longitude']})")
        
        try:
            # Use a default satellite image for monitoring (in real implementation, 
            # this would fetch real-time satellite data)
            default_image = "data/train/images/1.jpg"  # This should be latest satellite image
            
            if not os.path.exists(default_image):
                print(f"    ⚠️ No satellite image available for {location['name']}")
                return
            
            # Run analysis
            results = self.astroalert.run_complete_analysis(
                image_path=default_image,
                latitude=location['latitude'],
                longitude=location['longitude']
            )
            
            # Save analysis to database
            analysis_id = db.save_analysis(location['id'], results, default_image)
            
            # Check if alert should be triggered
            self.evaluate_alerts(location, results, analysis_id)
            
            print(f"    ✅ {location['name']}: Risk {results['results']['combined']['combined_assessment']['final_risk_level']}")
            
        except Exception as e:
            print(f"    ❌ Error analyzing {location['name']}: {e}")

    def evaluate_alerts(self, location: Dict, analysis_results: Dict, analysis_id: str):
        """Evaluate if alerts should be triggered based on analysis results"""
        combined = analysis_results['results']['combined']['combined_assessment']
        current_risk = combined['final_risk_level']
        risk_score = combined['combined_risk_score']
        
        # Get location's alert threshold
        alert_threshold = location['alert_threshold']
        
        # Define risk level hierarchy
        risk_levels = {'LOW': 1, 'MODERATE': 2, 'HIGH': 3, 'EXTREME': 4}
        
        current_level = risk_levels.get(current_risk, 0)
        threshold_level = risk_levels.get(alert_threshold, 2)
        
        # Trigger alert if current risk meets or exceeds threshold
        if current_level >= threshold_level:
            self.trigger_alert(location, analysis_results, analysis_id, current_risk)

    def trigger_alert(self, location: Dict, analysis_results: Dict, analysis_id: str, risk_level: str):
        """Trigger alert for high risk situation"""
        print(f"    🚨 ALERT: {location['name']} - {risk_level} RISK DETECTED")
        
        # Get user information
        user = db.get_user(location['user_id'])
        if not user:
            print(f"    ❌ Cannot find user for location {location['name']}")
            return
        
        # Create alert message
        combined = analysis_results['results']['combined']['combined_assessment']
        message = f"""
🌪️ CYCLONE ALERT: {location['name']}

Risk Level: {risk_level}
Risk Score: {combined['combined_risk_score']:.1f}/100
Action Required: {combined['action_required']}

Analysis Time: {analysis_results['analysis_timestamp']}
Location: {location['latitude']:.4f}, {location['longitude']:.4f}

Please check your AstroAlert dashboard for detailed information and recommendations.
        """.strip()
        
        # Save alert to database
        alert_id = db.create_alert(
            location_id=location['id'],
            user_id=user['id'], 
            analysis_id=analysis_id,
            risk_level=risk_level,
            message=message
        )
        
        # Send notifications
        self.notification_service.send_alert_notifications(user, alert_id, message, risk_level)

    def manual_check_location(self, location_id: str) -> Dict:
        """Manually trigger check for a specific location"""
        locations = db.get_active_locations()
        location = next((loc for loc in locations if loc['id'] == location_id), None)
        
        if not location:
            return {'error': 'Location not found or not active'}
        
        try:
            self.check_location(location)
            return {'success': True, 'message': f'Successfully checked {location["name"]}'}
        except Exception as e:
            return {'error': str(e)}

    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status"""
        active_locations = db.get_active_locations()
        
        return {
            'monitoring_active': self.monitoring_active,
            'check_interval_minutes': self.check_interval,
            'locations_monitored': len(active_locations),
            'last_check': getattr(self, 'last_check_time', None),
            'locations': [
                {
                    'id': loc['id'],
                    'name': loc['name'],
                    'coordinates': f"{loc['latitude']:.4f}, {loc['longitude']:.4f}",
                    'alert_threshold': loc['alert_threshold'],
                    'last_analysis': loc['last_analysis']
                }
                for loc in active_locations
            ]
        }

# Global monitoring service instance
monitoring_service = MonitoringService()

# Auto-start monitoring when module is imported
def start_background_monitoring():
    """Start background monitoring service"""
    monitoring_service.start_monitoring()

if __name__ == "__main__":
    print("🔍 Testing Monitoring Service")
    print("=" * 40)
    
    # Test manual location check
    locations = db.get_active_locations()
    if locations:
        location = locations[0]
        print(f"Testing check for {location['name']}")
        monitoring_service.check_location(location)
    
    # Test monitoring status
    status = monitoring_service.get_monitoring_status()
    print(f"Monitoring Status: {status}")
    
    print("✅ Monitoring service test completed")