#!/usr/bin/env python3
"""
Enhanced Flask API for AstroAlert Multi-Location Monitoring System
Includes APIs for location management, alerts, analytics, and notifications
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import tempfile
import datetime
import traceback
from werkzeug.utils import secure_filename
import json
import uuid

# Load environment variables from .env file if it exists
try:
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded environment variables from .env file")
except Exception as e:
    print(f"⚠️ Warning: Could not load .env file: {e}")

# Import our enhanced systems
try:
    from main_astroalert_fixed import AstroAlert
    from database import db
    from monitoring_service import monitoring_service
    from notification_service import notification_service
    print("✅ Enhanced AstroAlert backend imported successfully")
except ImportError as e:
    print(f"❌ Failed to import enhanced AstroAlert components: {e}")
    exit(1)

# Import chatbot system (optional)
try:
    from chatbot_module import CycloneChatbot
    print("✅ CycloneBot imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: CycloneBot not available: {e}")
    CycloneChatbot = None

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize AstroAlert system
try:
    astroalert = AstroAlert()
    print("✅ AstroAlert system initialized")
except Exception as e:
    print(f"❌ Failed to initialize AstroAlert: {e}")
    astroalert = None

# Initialize CycloneBot
chatbot = None
if CycloneChatbot:
    try:
        chatbot = CycloneChatbot()
        print("✅ CycloneBot initialized")
    except Exception as e:
        print(f"⚠️ CycloneBot initialization failed: {e}")
        print("💡 Set GEMINI_API_KEY environment variable to enable chatbot")
        chatbot = None

# Start background monitoring
try:
    monitoring_service.start_monitoring()
    print("✅ Background monitoring started")
except Exception as e:
    print(f"⚠️ Background monitoring failed to start: {e}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# STATIC FILE SERVING
# ==========================================

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'dashboard.html')  # Enhanced dashboard

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    # Handle legacy index.html redirect
    if filename == 'index.html':
        return send_from_directory('.', 'dashboard.html')
    return send_from_directory('.', filename)

# ==========================================
# LEGACY API ENDPOINTS (BACKWARD COMPATIBILITY)
# ==========================================

@app.route('/api/analyze', methods=['POST'])
def analyze_cyclone():
    """
    Legacy API endpoint for single cyclone analysis
    Maintains backward compatibility with existing frontend
    """
    try:
        print("🔍 Received legacy analysis request")
        
        # Check if AstroAlert is initialized
        if astroalert is None:
            return jsonify({
                'error': 'AstroAlert system not initialized',
                'success': False
            }), 500
        
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'success': False
            }), 400
        
        file = request.files['image']
        
        # If user does not select file, browser submits empty part without filename
        if file.filename == '':
            return jsonify({
                'error': 'No image file selected',
                'success': False
            }), 400
        
        # Get form data
        try:
            latitude = float(request.form.get('latitude', 19.0760))
            longitude = float(request.form.get('longitude', 72.8777))
            datetime_str = request.form.get('datetime')
            
            # Parse datetime
            if datetime_str:
                analysis_datetime = datetime.datetime.fromisoformat(datetime_str)
            else:
                analysis_datetime = datetime.datetime.now()
                
        except (ValueError, TypeError) as e:
            return jsonify({
                'error': f'Invalid input parameters: {str(e)}',
                'success': False
            }), 400
        
        # Save uploaded file temporarily
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            print(f"📁 Saved uploaded file: {filepath}")
            print(f"📍 Analysis parameters: lat={latitude}, lon={longitude}, time={analysis_datetime}")
            
            try:
                # Run complete AstroAlert analysis
                print("🚀 Starting AstroAlert analysis...")
                results = astroalert.run_complete_analysis(
                    image_path=filepath,
                    latitude=latitude,
                    longitude=longitude,
                    date_time=analysis_datetime
                )
                
                print("✅ Analysis completed successfully")
                
                # Clean up uploaded file
                try:
                    os.remove(filepath)
                    print(f"🗑️ Cleaned up temporary file: {filepath}")
                except:
                    pass
                
                # Add analysis context to chatbot if available
                if chatbot:
                    try:
                        chatbot.add_analysis_context(results)
                    except Exception as chatbot_error:
                        print(f"Warning: Failed to add analysis context to chatbot: {chatbot_error}")
                
                # Return successful results
                return jsonify({
                    'success': True,
                    'results': results['results'],
                    'timestamp': datetime.datetime.now().isoformat(),
                    'input_data': {
                        'latitude': latitude,
                        'longitude': longitude,
                        'datetime': analysis_datetime.isoformat(),
                        'filename': file.filename
                    }
                })
                
            except Exception as e:
                print(f"❌ Analysis failed: {str(e)}")
                print(traceback.format_exc())
                
                # Clean up file on error
                try:
                    os.remove(filepath)
                except:
                    pass
                
                return jsonify({
                    'error': f'Analysis failed: {str(e)}',
                    'success': False
                }), 500
        
        else:
            return jsonify({
                'error': 'Invalid file format. Please upload PNG, JPG, JPEG, or GIF files.',
                'success': False
            }), 400
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': f'Server error: {str(e)}',
            'success': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'astroalert_ready': astroalert is not None,
        'database_ready': True,
        'monitoring_active': monitoring_service.monitoring_active,
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test_backend():
    """Test endpoint to verify backend is working"""
    try:
        # Test astrology module
        test_date = datetime.datetime.now()
        test_result = astroalert.astrology_analyzer.get_cyclone_prediction(test_date, 19.0760, 72.8777)
        
        return jsonify({
            'status': 'Enhanced backend is working!',
            'astrology_test': 'passed',
            'vrs_score': test_result['vrs_analysis']['vrs_score'],
            'database_test': 'passed',
            'monitoring_status': monitoring_service.get_monitoring_status(),
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'Backend test failed',
            'error': str(e)
        }), 500

# ==========================================
# USER MANAGEMENT API
# ==========================================

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user account"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('name'):
            return jsonify({
                'error': 'Email and name are required',
                'success': False
            }), 400
        
        # Check if user already exists
        existing_user = db.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({
                'error': 'User with this email already exists',
                'success': False
            }), 409
        
        # Create new user
        user_id = db.create_user(
            email=data['email'],
            name=data['name'],
            phone=data.get('phone'),
            preferences=data.get('preferences', {})
        )
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'User created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to create user: {str(e)}',
            'success': False
        }), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information"""
    try:
        user = db.get_user(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get user: {str(e)}',
            'success': False
        }), 500

# ==========================================
# LOCATION MANAGEMENT API
# ==========================================

@app.route('/api/locations', methods=['POST'])
def add_location():
    """Add a new monitoring location"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'name', 'latitude', 'longitude']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'user_id, name, latitude, and longitude are required',
                'success': False
            }), 400
        
        # Validate coordinates
        lat, lng = float(data['latitude']), float(data['longitude'])
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({
                'error': 'Invalid coordinates',
                'success': False
            }), 400
        
        # Create location
        location_id = db.add_location(
            user_id=data['user_id'],
            name=data['name'],
            latitude=lat,
            longitude=lng,
            alert_threshold=data.get('alert_threshold', 'MODERATE')
        )
        
        return jsonify({
            'success': True,
            'location_id': location_id,
            'message': 'Location added successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to add location: {str(e)}',
            'success': False
        }), 500

@app.route('/api/users/<user_id>/locations', methods=['GET'])
def get_user_locations(user_id):
    """Get all locations for a user"""
    try:
        locations = db.get_user_locations(user_id)
        
        # Add latest analysis data for each location
        enhanced_locations = []
        for location in locations:
            analyses = db.get_location_analyses(location['id'], limit=1)
            location['latest_analysis'] = analyses[0] if analyses else None
            enhanced_locations.append(location)
        
        return jsonify({
            'success': True,
            'locations': enhanced_locations
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get locations: {str(e)}',
            'success': False
        }), 500

@app.route('/api/locations/<location_id>', methods=['PUT'])
def update_location(location_id):
    """Update location settings"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'success': False
            }), 400
        
        # Update location
        success = db.update_location(location_id, **data)
        
        if not success:
            return jsonify({
                'error': 'Location not found or no changes made',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to update location: {str(e)}',
            'success': False
        }), 500

@app.route('/api/locations/<location_id>/analyze', methods=['POST'])
def analyze_location():
    """Manually trigger analysis for a specific location"""
    try:
        location_id = request.view_args['location_id']
        result = monitoring_service.manual_check_location(location_id)
        
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'success': False
            }), 400
        
        return jsonify({
            'success': True,
            'message': result['message']
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to analyze location: {str(e)}',
            'success': False
        }), 500

# ==========================================
# ANALYTICS API
# ==========================================

@app.route('/api/users/<user_id>/analytics', methods=['GET'])
def get_user_analytics(user_id):
    """Get analytics summary for user"""
    try:
        days = int(request.args.get('days', 30))
        analytics = db.get_analytics_summary(user_id, days)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get analytics: {str(e)}',
            'success': False
        }), 500

@app.route('/api/locations/<location_id>/trends', methods=['GET'])
def get_location_trends(location_id):
    """Get trend data for a location"""
    try:
        days = int(request.args.get('days', 30))
        trends = db.get_trend_data(location_id, days)
        
        return jsonify({
            'success': True,
            'trends': trends
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get trends: {str(e)}',
            'success': False
        }), 500

@app.route('/api/locations/<location_id>/analyses', methods=['GET'])
def get_location_analyses(location_id):
    """Get analysis history for a location"""
    try:
        limit = int(request.args.get('limit', 50))
        analyses = db.get_location_analyses(location_id, limit)
        
        return jsonify({
            'success': True,
            'analyses': analyses
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get analyses: {str(e)}',
            'success': False
        }), 500

# ==========================================
# ALERTS & NOTIFICATIONS API
# ==========================================

@app.route('/api/users/<user_id>/alerts', methods=['GET'])
def get_user_alerts(user_id):
    """Get alerts for a user"""
    try:
        limit = int(request.args.get('limit', 50))
        alerts = db.get_user_alerts(user_id, limit)
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get alerts: {str(e)}',
            'success': False
        }), 500

@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alerts 
                SET acknowledged = 1 
                WHERE id = ?
            """, (alert_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({
                    'error': 'Alert not found',
                    'success': False
                }), 404
        
        return jsonify({
            'success': True,
            'message': 'Alert acknowledged'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to acknowledge alert: {str(e)}',
            'success': False
        }), 500

@app.route('/api/notifications/test', methods=['POST'])
def test_notifications():
    """Test notification settings"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'error': 'Email is required',
                'success': False
            }), 400
        
        result = notification_service.send_test_notifications(
            data['email'], 
            data.get('phone')
        )
        
        return jsonify({
            'success': True,
            'test_result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to send test notifications: {str(e)}',
            'success': False
        }), 500

# ==========================================
# MONITORING STATUS API
# ==========================================

@app.route('/api/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """Get monitoring service status"""
    try:
        status = monitoring_service.get_monitoring_status()
        
        return jsonify({
            'success': True,
            'monitoring': status
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get monitoring status: {str(e)}',
            'success': False
        }), 500

# ==========================================
# CHATBOT API (LEGACY SUPPORT)
# ==========================================

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Chatbot API endpoint (unchanged for backward compatibility)
    """
    try:
        if not chatbot:
            return jsonify({
                'error': 'Chatbot is not available. Please check server configuration.',
                'success': False,
                'available': False
            }), 503
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing message in request',
                'success': False
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'success': False
            }), 400
        
        # Get chatbot response
        response = chatbot.chat(user_message)
        
        return jsonify({
            'success': True,
            'response': response['response'],
            'category': response['category'],
            'timestamp': response['timestamp'],
            'available': True
        })
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        return jsonify({
            'error': f'Chat service error: {str(e)}',
            'success': False,
            'available': chatbot is not None
        }), 500

@app.route('/api/chat/suggestions', methods=['GET'])
def get_chat_suggestions():
    """Get suggested questions for the chatbot"""
    try:
        if not chatbot:
            return jsonify({
                'error': 'Chatbot is not available',
                'suggestions': [],
                'success': False
            }), 503
        
        suggestions = chatbot.get_suggested_questions()
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'available': True
        })
        
    except Exception as e:
        print(f"❌ Suggestions error: {str(e)}")
        return jsonify({
            'error': f'Failed to get suggestions: {str(e)}',
            'suggestions': [],
            'success': False
        }), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """Clear chatbot conversation history"""
    try:
        if not chatbot:
            return jsonify({
                'error': 'Chatbot is not available',
                'success': False
            }), 503
        
        chatbot.clear_conversation()
        
        return jsonify({
            'success': True,
            'message': 'Conversation history cleared',
            'available': True
        })
        
    except Exception as e:
        print(f"❌ Clear chat error: {str(e)}")
        return jsonify({
            'error': f'Failed to clear conversation: {str(e)}',
            'success': False
        }), 500

@app.route('/api/chat/status', methods=['GET'])
def chat_status():
    """Get chatbot status and availability"""
    try:
        if not chatbot:
            return jsonify({
                'available': False,
                'status': 'unavailable',
                'message': 'Chatbot not initialized. Check GEMINI_API_KEY configuration.',
                'success': True
            })
        
        conversation_summary = chatbot.get_conversation_summary()
        
        return jsonify({
            'available': True,
            'status': 'ready',
            'message': 'CycloneBot is ready to help!',
            'conversation_summary': conversation_summary,
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Chat status error: {str(e)}")
        return jsonify({
            'available': False,
            'status': 'error',
            'message': f'Status check failed: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    print("🌪 Starting Enhanced AstroAlert Flask Server")
    print("=" * 60)
    print("Dashboard available at: http://localhost:5000")
    print("API endpoints: http://localhost:5000/api/*")
    print("Health check: http://localhost:5000/api/health")
    print("Monitoring status: http://localhost:5000/api/monitoring/status")
    print("=" * 60)
    
    # Run the Flask development server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid issues with background services
    )