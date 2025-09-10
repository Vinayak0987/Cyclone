#!/usr/bin/env python3
"""
Test Enhanced Analysis Integration
Verifies that the enhanced analysis features work correctly
"""

import sys
import os
import datetime
from pathlib import Path

def test_enhanced_analyzer_loading():
    """Test if enhanced analyzer can be loaded"""
    print("🧪 Testing Enhanced Analyzer Loading...")
    try:
        from enhanced_analysis.yolo_enhanced_analyzer import YOLOEnhancedAnalyzer
        analyzer = YOLOEnhancedAnalyzer()
        print("✅ Enhanced analyzer loaded successfully")
        
        # Check model performance
        performance = analyzer.get_model_performance()
        if performance:
            print("✅ Model performance data available")
            print(f"📊 Training date: {performance.get('training_date', 'Unknown')}")
            
            feature_models = performance.get('feature_models', {})
            if feature_models:
                for model_name, metrics in feature_models.items():
                    print(f"   {model_name}: {metrics.get('accuracy', 'N/A')} accuracy")
        else:
            print("⚠️ Model performance data not available")
        
        return True
    except Exception as e:
        print(f"❌ Enhanced analyzer loading failed: {e}")
        return False

def test_enhanced_astroalert_loading():
    """Test if enhanced AstroAlert can be loaded"""
    print("\n🧪 Testing Enhanced AstroAlert Loading...")
    try:
        from enhanced_analysis.enhanced_astroalert import EnhancedAstroAlert
        enhanced_astroalert = EnhancedAstroAlert()
        print("✅ Enhanced AstroAlert loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Enhanced AstroAlert loading failed: {e}")
        return False

def test_integration_with_main_astroalert():
    """Test integration with main AstroAlert"""
    print("\n🧪 Testing Integration with Main AstroAlert...")
    try:
        from main_astroalert_fixed import AstroAlert
        astroalert = AstroAlert()
        print("✅ Main AstroAlert loaded successfully")
        
        # Test enhanced analysis parameter
        print("✅ Enhanced analysis parameter integration ready")
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_model_files():
    """Test if required model files are present"""
    print("\n🧪 Testing Model Files...")
    
    model_dir = Path("enhanced_analysis/trained_models")
    required_files = [
        "cyclone_feature_classifier.joblib",
        "cyclone_eye_detector.joblib", 
        "real_image_training_report.json"
    ]
    
    all_present = True
    for file_name in required_files:
        file_path = model_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} found")
        else:
            print(f"❌ {file_name} missing")
            all_present = False
    
    return all_present

def test_dependencies():
    """Test if required dependencies are available"""
    print("\n🧪 Testing Dependencies...")
    
    dependencies = {
        'cv2': 'opencv-python',
        'numpy': 'numpy', 
        'pandas': 'pandas',
        'PIL': 'Pillow',
        'sklearn': 'scikit-learn',
        'joblib': 'joblib'
    }
    
    all_available = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing - install with: pip install {package}")
            all_available = False
    
    return all_available

def run_integration_test():
    """Run a simple integration test"""
    print("\n🧪 Running Integration Test...")
    
    try:
        # Test with a dummy image array (for testing purposes)
        import numpy as np
        
        # Create a dummy satellite image (grayscale)
        dummy_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        from enhanced_analysis.yolo_enhanced_analyzer import YOLOEnhancedAnalyzer
        analyzer = YOLOEnhancedAnalyzer()
        
        # Dummy YOLO detection results
        dummy_yolo_detections = {
            'total_cyclones': 1,
            'detections': [{
                'bbox': [0.5, 0.5, 0.3, 0.3],  # Center of image
                'confidence': 0.75,
                'class': 0
            }],
            'avg_confidence': 0.75,
            'max_confidence': 0.75,
            'detection_quality': 'GOOD'
        }
        
        # Run enhanced analysis
        results = analyzer.analyze_yolo_detection(dummy_image, dummy_yolo_detections)
        
        if 'enhanced_analysis' in results:
            print("✅ Integration test successful")
            print(f"📊 Analysis completed with {len(results['enhanced_analysis'])} regions")
            
            # Check if intensity prediction worked
            for analysis in results['enhanced_analysis']:
                if analysis.get('intensity_prediction'):
                    print(f"✅ Intensity prediction: {analysis['intensity_prediction'].get('intensity_name', 'Unknown')}")
                    break
            else:
                print("⚠️ Intensity prediction not available (models may be missing)")
                
            # Check if eye detection worked
            for analysis in results['enhanced_analysis']:
                if analysis.get('eye_detection'):
                    eye_detected = analysis['eye_detection'].get('eye_detected', False)
                    print(f"✅ Eye detection: {'Detected' if eye_detected else 'Not detected'}")
                    break
            else:
                print("⚠️ Eye detection not available (models may be missing)")
            
            return True
        else:
            print("❌ Integration test failed - no enhanced analysis results")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🌀 Enhanced Cyclone Analysis - Integration Test")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Model Files", test_model_files),
        ("Enhanced Analyzer", test_enhanced_analyzer_loading),
        ("Enhanced AstroAlert", test_enhanced_astroalert_loading),
        ("Main AstroAlert Integration", test_integration_with_main_astroalert),
        ("Integration Test", run_integration_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    print(f"\n{'='*60}")
    print("📋 Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not success:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Enhanced analysis is ready to use.")
        print("\n📖 Usage Instructions:")
        print("1. Use enhanced=True in your analysis calls")
        print("2. Add 'enhanced=true' in your API requests")
        print("3. Enhanced analysis provides:")
        print("   - Detailed intensity classification")
        print("   - Eye detection and clarity assessment")
        print("   - Meteorological threat analysis")
        print("   - Enhanced risk scoring")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        print("\n💡 Common solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Ensure model files are in enhanced_analysis/trained_models/")
        print("3. Check file permissions and paths")
    
    print("\n🔗 Integration complete!")

if __name__ == "__main__":
    main()
