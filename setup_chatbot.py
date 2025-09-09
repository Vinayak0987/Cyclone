#!/usr/bin/env python3
"""
Setup script for CycloneBot - Gemini API Configuration
Helps configure the Gemini API key for the chatbot functionality
"""

import os
import sys

def setup_gemini_api_key():
    """Interactive setup for Gemini API key"""
    print("🤖 CycloneBot Setup - Gemini API Configuration")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv('GEMINI_API_KEY')
    if current_key:
        print(f"✅ Gemini API key is already configured")
        print(f"Current key: {current_key[:10]}...{current_key[-10:] if len(current_key) > 20 else current_key}")
        
        update = input("\nDo you want to update it? (y/N): ").strip().lower()
        if update not in ['y', 'yes']:
            print("🎯 Setup complete - using existing API key")
            return True
    
    print("\n📋 To enable CycloneBot, you need a Gemini API key.")
    print("1. Go to: https://aistudio.google.com/app/apikey")
    print("2. Click 'Create API key'")
    print("3. Copy your API key")
    print("4. Paste it below")
    print()
    
    # Get API key from user
    api_key = input("🔑 Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. CycloneBot will be disabled.")
        return False
    
    # Validate API key format (basic check)
    if not api_key.startswith('AIza') or len(api_key) < 30:
        print("⚠️  Warning: This doesn't look like a valid Gemini API key.")
        print("   Gemini API keys typically start with 'AIza' and are ~39 characters long.")
        
        proceed = input("Do you want to continue anyway? (y/N): ").strip().lower()
        if proceed not in ['y', 'yes']:
            print("❌ Setup cancelled.")
            return False
    
    # Test the API key
    print("\n🔍 Testing API key...")
    try:
        from chatbot_module import CycloneChatbot
        test_bot = CycloneChatbot(api_key=api_key)
        
        # Quick test
        test_response = test_bot.chat("Hello")
        if test_response['success']:
            print("✅ API key is working!")
        else:
            print("❌ API key test failed:", test_response.get('error', 'Unknown error'))
            return False
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        print("💡 Make sure you have 'google-generativeai' installed:")
        print("   pip install google-generativeai")
        return False
    
    # Set environment variable
    try:
        # For Windows - set user environment variable
        if sys.platform.startswith('win'):
            import subprocess
            subprocess.run([
                'setx', 'GEMINI_API_KEY', api_key
            ], check=True, capture_output=True)
            print("✅ Environment variable set for Windows")
            print("💡 Please restart your terminal/IDE for changes to take effect")
            
        else:
            # For Unix-like systems
            print("💡 Add this line to your ~/.bashrc or ~/.zshrc:")
            print(f"export GEMINI_API_KEY='{api_key}'")
            print("Then run: source ~/.bashrc (or ~/.zshrc)")
            
            # Try to set for current session
            os.environ['GEMINI_API_KEY'] = api_key
            
    except Exception as e:
        print(f"⚠️  Could not set environment variable automatically: {e}")
        print(f"💡 Please set GEMINI_API_KEY='{api_key}' manually")
    
    # Create a .env file as backup
    try:
        with open('.env', 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print("✅ API key saved to .env file")
        print("💡 Your Flask app can load this automatically")
    except Exception as e:
        print(f"⚠️  Could not create .env file: {e}")
    
    print("\n🎉 Setup complete!")
    print("🚀 You can now start your Flask server and use CycloneBot")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'google-generativeai',
        'flask',
        'flask-cors',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("💡 Install them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def main():
    """Main setup function"""
    print("🌪 AstroAlert Chatbot Setup")
    print("=" * 30)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before continuing.")
        return
    
    # Setup API key
    if setup_gemini_api_key():
        print("\n🎯 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Restart your terminal/IDE")
        print("2. Run: python app.py")
        print("3. Open http://localhost:5000 in your browser")
        print("4. Click on the CycloneBot chatbot in the bottom-right corner")
        print("\n🤖 CycloneBot will be ready to help with cyclone analysis questions!")
    else:
        print("\n❌ Setup incomplete. CycloneBot will be disabled.")
        print("💡 You can run this setup again anytime with: python setup_chatbot.py")

if __name__ == "__main__":
    main()
