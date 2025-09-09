#!/usr/bin/env python3
"""
Simple Flask API for AstroAlert Frontend
Connects the web interface with the Python backend
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import tempfile
import datetime
import traceback
from werkzeug.utils import secure_filename
import json

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

# Import our AstroAlert system
try:
    from main_astroalert_fixed import AstroAlert
    print("✅ AstroAlert backend imported successfully")
except ImportError as e:
    print(f"❌ Failed to import AstroAlert: {e}")
    exit(1)

# Import chatbot system
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

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('.', filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_cyclone():
    """
    Main API endpoint for cyclone analysis
    Expects: multipart form data with image, latitude, longitude, datetime
    Returns: JSON with complete analysis results
    """
    try:
        print("🔍 Received analysis request")
        
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
                # Handle HTML datetime-local format: YYYY-MM-DDTHH:MM
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
            # Add timestamp to make filename unique
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
                    pass  # Don't fail if cleanup fails
                
                # Add analysis context to chatbot if available
                if chatbot:
                    try:
                        chatbot.add_analysis_context(results)
                    except Exception as chatbot_error:
                        print(f"Warning: Failed to add analysis context to chatbot: {chatbot_error}")
                
                # Return successful results
                return jsonify({
                    'success': True,
                    'results': results['results'],  # Extract just the results part
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
            'status': 'Backend is working!',
            'astrology_test': 'passed',
            'vrs_score': test_result['vrs_analysis']['vrs_score'],
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'Backend test failed',
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Chatbot API endpoint
    Expects: JSON with 'message' field
    Returns: JSON with chatbot response
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
    """
    Get suggested questions for the chatbot
    """
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
    """
    Clear chatbot conversation history
    """
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
    """
    Get chatbot status and availability
    """
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
    print("🌪 Starting AstroAlert Flask Server")
    print("=" * 50)
    print("Frontend available at: http://localhost:5000")
    print("API endpoint: http://localhost:5000/api/analyze")
    print("Health check: http://localhost:5000/api/health")
    print("=" * 50)
    
    # Run the Flask development server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid issues with imported modules
    )
