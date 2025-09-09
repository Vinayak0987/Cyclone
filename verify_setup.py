#!/usr/bin/env python3
"""
AstroAlert System Verification Script
Tests all components of the cyclone prediction system
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def check_directory_structure():
    """Check if all required directories exist"""
    print_header("DIRECTORY STRUCTURE CHECK")
    
    required_dirs = [
        "data/train/images",
        "data/train/labels", 
        "data/val/images",
        "data/val/labels",
        "data/custom_data",
        "ephe",
        "results",
        "yolov5"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Missing directory: {dir_path}")
            all_good = False
    
    return all_good

def check_required_files():
    """Check if all required files exist"""
    print_header("REQUIRED FILES CHECK")
    
    required_files = [
        "astrology_module_clean.py",
        "main_astroalert_fixed.py",
        "dataset.yaml",
        "index.html",
        "styles.css",
        "script.js",
        "ephe/semo_18.se1",
        "ephe/seas_18.se1", 
        "ephe/sepl_18.se1"
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"Missing file: {file_path}")
            all_good = False
    
    return all_good

def check_python_packages():
    """Check if all required Python packages are installed"""
    print_header("PYTHON PACKAGES CHECK")
    
    required_packages = [
        "torch",
        "torchvision", 
        "ultralytics",
        "cv2",
        "numpy",
        "yaml",
        "scipy",
        "tqdm",
        "pandas",
        "seaborn",
        "matplotlib",
        "swisseph",
        "PIL",
        "requests"
    ]
    
    all_good = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"Package installed: {package}")
        except ImportError:
            print_error(f"Missing package: {package}")
            all_good = False
    
    return all_good

def check_data_files():
    """Check if training and validation data exists"""
    print_header("DATA FILES CHECK")
    
    train_images = len([f for f in os.listdir("data/train/images") if f.endswith(('.jpg', '.png', '.jpeg'))])
    train_labels = len([f for f in os.listdir("data/train/labels") if f.endswith('.txt')])
    val_images = len([f for f in os.listdir("data/val/images") if f.endswith(('.jpg', '.png', '.jpeg'))])
    val_labels = len([f for f in os.listdir("data/val/labels") if f.endswith('.txt')])
    
    print_success(f"Training images: {train_images}")
    print_success(f"Training labels: {train_labels}")
    print_success(f"Validation images: {val_images}")
    print_success(f"Validation labels: {val_labels}")
    
    if train_images > 0 and val_images > 0:
        print_success("Dataset appears to be ready")
        return True
    else:
        print_error("Dataset is incomplete")
        return False

def check_model_weights():
    """Check if trained model weights exist"""
    print_header("MODEL WEIGHTS CHECK")
    
    model_paths = [
        "yolov5/runs/train/cyclone_detector52/weights/best.pt",
        "yolov5/runs/train/cyclone_detector52/weights/last.pt"
    ]
    
    weights_exist = False
    for model_path in model_paths:
        if os.path.exists(model_path):
            print_success(f"Model weights found: {model_path}")
            weights_exist = True
        else:
            print_warning(f"Model weights not found: {model_path}")
    
    if not weights_exist:
        print_error("No trained model weights found. Training is required.")
    
    return weights_exist

def test_astrology_module():
    """Test the astrology module"""
    print_header("ASTROLOGY MODULE TEST")
    
    try:
        from astrology_module_clean import VedicAstrologyAnalyzer
        analyzer = VedicAstrologyAnalyzer()
        
        # Test prediction
        test_date = datetime.datetime(2024, 8, 15, 12, 0, 0)
        result = analyzer.get_cyclone_prediction(test_date, 19.0760, 72.8777)
        
        print_success("Astrology module initialized successfully")
        print_success(f"Test prediction completed: VRS Score = {result['vrs_analysis']['vrs_score']}")
        return True
        
    except Exception as e:
        print_error(f"Astrology module test failed: {e}")
        return False

def test_yolov5_detection():
    """Test YOLOv5 detection"""
    print_header("YOLOV5 DETECTION TEST")
    
    try:
        # Check if we have images to test with
        train_images = [f for f in os.listdir("data/train/images") if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        if not train_images:
            print_error("No test images available")
            return False
        
        test_image = f"data/train/images/{train_images[0]}"
        
        # Test with high confidence threshold to avoid too many detections
        cmd = [
            'python', 'yolov5/detect.py',
            '--weights', 'yolov5/runs/train/cyclone_detector52/weights/best.pt',
            '--source', test_image,
            '--conf', '0.5',
            '--save-txt',
            '--project', 'runs/detect',
            '--name', 'verification_test'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print_success("YOLOv5 detection test completed successfully")
            return True
        else:
            print_error(f"YOLOv5 detection test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"YOLOv5 detection test failed: {e}")
        return False

def test_main_application():
    """Test the main AstroAlert application"""
    print_header("MAIN APPLICATION TEST")
    
    try:
        # Check if we have images to test with
        train_images = [f for f in os.listdir("data/train/images") if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        if not train_images:
            print_error("No test images available")
            return False
        
        test_image = f"data/train/images/{train_images[0]}"
        
        # Test main application
        cmd = ['python', 'main_astroalert_fixed.py', test_image, '19.0760', '72.8777']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("Main application test completed successfully")
            
            # Check if results file was created
            if os.path.exists("results/astroalert_report.json"):
                print_success("Results file created successfully")
                return True
            else:
                print_warning("Results file not created")
                return False
        else:
            print_error(f"Main application test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Main application test timed out")
        return False
    except Exception as e:
        print_error(f"Main application test failed: {e}")
        return False

def check_frontend_files():
    """Check frontend files"""
    print_header("FRONTEND FILES CHECK")
    
    frontend_files = ["index.html", "styles.css", "script.js"]
    all_good = True
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print_success(f"Frontend file exists: {file_path} ({file_size} bytes)")
        else:
            print_error(f"Missing frontend file: {file_path}")
            all_good = False
    
    if all_good:
        print_success("Frontend appears to be ready")
    
    return all_good

def generate_summary_report():
    """Generate a summary report"""
    print_header("VERIFICATION SUMMARY")
    
    tests = [
        ("Directory Structure", check_directory_structure()),
        ("Required Files", check_required_files()),
        ("Python Packages", check_python_packages()),
        ("Data Files", check_data_files()),
        ("Model Weights", check_model_weights()),
        ("Astrology Module", test_astrology_module()),
        ("YOLOv5 Detection", test_yolov5_detection()),
        ("Main Application", test_main_application()),
        ("Frontend Files", check_frontend_files())
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print(f"\n{'='*60}")
    print(f"🎯 FINAL RESULTS: {passed}/{total} tests passed")
    print('='*60)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! AstroAlert system is fully operational!")
        print(f"🌐 Open index.html in your browser to use the frontend")
        print(f"🐍 Use 'python main_astroalert_fixed.py <image> <lat> <lon>' for command line")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please address the issues above.")
        
    return passed == total

if __name__ == "__main__":
    print("🌪 AstroAlert System Verification")
    print("=" * 60)
    print("This script will verify that your AstroAlert system is properly set up")
    print("and all components are working correctly.")
    
    success = generate_summary_report()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
