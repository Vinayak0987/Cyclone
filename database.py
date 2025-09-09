#!/usr/bin/env python3
"""
Database module for AstroAlert Multi-Location Monitoring System
Handles user accounts, locations, analyses, alerts, and notifications
"""

import sqlite3
import json
import datetime
from typing import Dict, List, Optional, Tuple
import os
import uuid
from contextlib import contextmanager

class AstroAlertDatabase:
    def __init__(self, db_path: str = "astroalert.db"):
        """
        Initialize AstroAlert database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    preferences TEXT DEFAULT '{}',
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    monitoring_enabled BOOLEAN DEFAULT 1,
                    alert_threshold TEXT DEFAULT 'MODERATE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_analysis TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Analyses table (historical data)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    location_id TEXT NOT NULL,
                    analysis_timestamp TIMESTAMP NOT NULL,
                    ai_cyclones_detected INTEGER DEFAULT 0,
                    ai_avg_confidence REAL DEFAULT 0,
                    ai_risk_score INTEGER DEFAULT 0,
                    vrs_score INTEGER DEFAULT 0,
                    vrs_risk_level TEXT DEFAULT 'LOW',
                    combined_risk_score REAL DEFAULT 0,
                    final_risk_level TEXT DEFAULT 'LOW',
                    full_results TEXT NOT NULL,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (location_id) REFERENCES locations (id)
                )
            """)
            
            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    location_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    analysis_id TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    alert_type TEXT DEFAULT 'RISK_CHANGE',
                    message TEXT NOT NULL,
                    triggered_at TIMESTAMP NOT NULL,
                    acknowledged BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (location_id) REFERENCES locations (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (analysis_id) REFERENCES analyses (id)
                )
            """)
            
            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    alert_id TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    subject TEXT,
                    content TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (alert_id) REFERENCES alerts (id)
                )
            """)
            
            conn.commit()
            print("✅ Database initialized successfully")

    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()

    # User Management
    def create_user(self, email: str, name: str, phone: str = None, preferences: Dict = None) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        preferences_json = json.dumps(preferences or {})
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, email, name, phone, preferences)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, email, name, phone, preferences_json))
            conn.commit()
        
        return user_id

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,))
            row = cursor.fetchone()
            
            if row:
                user = dict(row)
                user['preferences'] = json.loads(user['preferences'])
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
            row = cursor.fetchone()
            
            if row:
                user = dict(row)
                user['preferences'] = json.loads(user['preferences'])
                return user
        return None

    # Location Management
    def add_location(self, user_id: str, name: str, latitude: float, longitude: float, 
                     alert_threshold: str = 'MODERATE') -> str:
        """Add a new monitoring location"""
        location_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO locations (id, user_id, name, latitude, longitude, alert_threshold)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (location_id, user_id, name, latitude, longitude, alert_threshold))
            conn.commit()
        
        return location_id

    def get_user_locations(self, user_id: str) -> List[Dict]:
        """Get all locations for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM locations 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_active_locations(self) -> List[Dict]:
        """Get all locations with monitoring enabled"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM locations 
                WHERE monitoring_enabled = 1
                ORDER BY created_at DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]

    def update_location(self, location_id: str, **kwargs) -> bool:
        """Update location settings"""
        if not kwargs:
            return False
            
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [location_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE locations 
                SET {set_clause}
                WHERE id = ?
            """, values)
            conn.commit()
            
            return cursor.rowcount > 0

    # Analysis Storage
    def save_analysis(self, location_id: str, analysis_results: Dict, image_path: str = None) -> str:
        """Save analysis results to database"""
        analysis_id = str(uuid.uuid4())
        
        # Extract key metrics from analysis results
        detection = analysis_results.get('results', {}).get('detection', {})
        astrology = analysis_results.get('results', {}).get('astrology', {}).get('vrs_analysis', {})
        combined = analysis_results.get('results', {}).get('combined', {}).get('combined_assessment', {})
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analyses (
                    id, location_id, analysis_timestamp, ai_cyclones_detected,
                    ai_avg_confidence, ai_risk_score, vrs_score, vrs_risk_level,
                    combined_risk_score, final_risk_level, full_results, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id, location_id, analysis_results.get('analysis_timestamp'),
                detection.get('total_cyclones', 0), detection.get('avg_confidence', 0),
                combined.get('ai_risk_score', 0), astrology.get('vrs_score', 0),
                astrology.get('risk_level', 'LOW'), combined.get('combined_risk_score', 0),
                combined.get('final_risk_level', 'LOW'), json.dumps(analysis_results),
                image_path
            ))
            conn.commit()
            
        # Update location's last analysis time
        self.update_location(location_id, last_analysis=analysis_results.get('analysis_timestamp'))
        
        return analysis_id

    def get_location_analyses(self, location_id: str, limit: int = 100) -> List[Dict]:
        """Get analysis history for a location"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM analyses 
                WHERE location_id = ? 
                ORDER BY analysis_timestamp DESC 
                LIMIT ?
            """, (location_id, limit))
            
            analyses = []
            for row in cursor.fetchall():
                analysis = dict(row)
                analysis['full_results'] = json.loads(analysis['full_results'])
                analyses.append(analysis)
            
            return analyses

    # Alert Management
    def create_alert(self, location_id: str, user_id: str, analysis_id: str, 
                     risk_level: str, message: str) -> str:
        """Create a new alert"""
        alert_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (id, location_id, user_id, analysis_id, risk_level, message, triggered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (alert_id, location_id, user_id, analysis_id, risk_level, message, datetime.datetime.now()))
            conn.commit()
        
        return alert_id

    def get_user_alerts(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get alerts for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, l.name as location_name 
                FROM alerts a
                JOIN locations l ON a.location_id = l.id
                WHERE a.user_id = ? 
                ORDER BY a.triggered_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]

    # Analytics Methods
    def get_analytics_summary(self, user_id: str, days: int = 30) -> Dict:
        """Get analytics summary for user's locations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            
            # Total analyses
            cursor.execute("""
                SELECT COUNT(*) as total_analyses
                FROM analyses a
                JOIN locations l ON a.location_id = l.id
                WHERE l.user_id = ? AND a.analysis_timestamp >= ?
            """, (user_id, start_date))
            total_analyses = cursor.fetchone()[0]
            
            # Risk level distribution
            cursor.execute("""
                SELECT final_risk_level, COUNT(*) as count
                FROM analyses a
                JOIN locations l ON a.location_id = l.id
                WHERE l.user_id = ? AND a.analysis_timestamp >= ?
                GROUP BY final_risk_level
            """, (user_id, start_date))
            risk_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Active alerts
            cursor.execute("""
                SELECT COUNT(*) as active_alerts
                FROM alerts a
                JOIN locations l ON a.location_id = l.id
                WHERE l.user_id = ? AND a.acknowledged = 0
            """, (user_id,))
            active_alerts = cursor.fetchone()[0]
            
            # Monitored locations
            cursor.execute("""
                SELECT COUNT(*) as monitored_locations
                FROM locations
                WHERE user_id = ? AND monitoring_enabled = 1
            """, (user_id,))
            monitored_locations = cursor.fetchone()[0]
            
            return {
                'total_analyses': total_analyses,
                'risk_distribution': risk_distribution,
                'active_alerts': active_alerts,
                'monitored_locations': monitored_locations,
                'period_days': days
            }

    def get_trend_data(self, location_id: str, days: int = 30) -> List[Dict]:
        """Get trend data for a location"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            
            cursor.execute("""
                SELECT 
                    DATE(analysis_timestamp) as date,
                    AVG(combined_risk_score) as avg_risk,
                    MAX(combined_risk_score) as max_risk,
                    COUNT(*) as analysis_count
                FROM analyses
                WHERE location_id = ? AND analysis_timestamp >= ?
                GROUP BY DATE(analysis_timestamp)
                ORDER BY date
            """, (location_id, start_date))
            
            return [dict(row) for row in cursor.fetchall()]

# Initialize default database instance
db = AstroAlertDatabase()

# Example usage and testing
if __name__ == "__main__":
    print("🗄️ Testing Database Module")
    print("=" * 40)
    
    # Test user creation
    user_id = db.create_user("test@example.com", "Test User", "+1234567890")
    print(f"Created user: {user_id}")
    
    # Test location creation
    location_id = db.add_location(user_id, "Mumbai", 19.0760, 72.8777, "HIGH")
    print(f"Created location: {location_id}")
    
    # Test data retrieval
    user = db.get_user(user_id)
    print(f"Retrieved user: {user['name']}")
    
    locations = db.get_user_locations(user_id)
    print(f"User has {len(locations)} locations")
    
    print("✅ Database test completed successfully")