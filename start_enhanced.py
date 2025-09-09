#!/usr/bin/env python3
"""
Enhanced AstroAlert Startup Script
Initializes database, starts monitoring, and launches the Flask server
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'flask_cors', 'sqlite3', 'schedule', 
        'requests', 'datetime', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'flask_cors':
                import flask_cors
            elif package == 'schedule':
                import schedule
            elif package == 'requests':
                import requests
            elif package == 'datetime':
                import datetime
            elif package == 'numpy':
                import numpy
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Installing missing packages...")
        
        for package in missing_packages:
            if package == 'flask_cors':
                package = 'Flask-CORS'
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    print("✅ All dependencies satisfied")
    return True

def initialize_database():
    """Initialize the database with required tables"""
    print("🗄️ Initializing database...")
    
    try:
        from database import db
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_enhanced_server():
    """Start the enhanced AstroAlert server"""
    print("🌪 Starting Enhanced AstroAlert Server...")
    print("=" * 60)
    
    # Check if enhanced app exists, fallback to original
    if os.path.exists('app_enhanced.py'):
        print("🚀 Using Enhanced App (app_enhanced.py)")
        from app_enhanced import app
    else:
        print("🔄 Falling back to Original App (app.py)")
        from app import app
    
    print("📍 Server will be available at: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard.html")
    print("🤖 API Documentation: http://localhost:5000/api/health")
    print("=" * 60)
    
    # Start the server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )

def main():
    """Main startup function"""
    print("🌪 Enhanced AstroAlert System - Startup")
    print("=" * 60)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages manually.")
        sys.exit(1)
    
    # Step 2: Initialize database
    if not initialize_database():
        print("❌ Database initialization failed.")
        print("💡 The system will still work with reduced functionality.")
    
    # Step 3: Start the server
    try:
        start_enhanced_server()
    except KeyboardInterrupt:
        print("\
🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("💡 Trying fallback server...")
        
        # Fallback to simple Flask server
        try:
            from app import app
            app.run(host='127.0.0.1', port=5000, debug=True)
        except Exception as fallback_error:
            print(f"❌ Fallback server also failed: {fallback_error}")
            sys.exit(1)

if __name__ == "__main__":
    main()