#!/usr/bin/env python3
"""
Test script to verify the cyclone detection fixes
"""

import os
import datetime
import json
from main_astroalert_fixed import AstroAlert

def test_detection_improvements():
    """Test the improved detection logic"""
    print("Testing AstroAlert Detection Improvements")
    print("=" * 50)
    
    # Initialize AstroAlert
    astroalert = AstroAlert()
    
    # Check if we have any test images
    test_images = []
    
    # Look for uploaded images
    if os.path.exists('temp_uploads'):
        for file in os.listdir('temp_uploads'):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join('temp_uploads', file))
                break  # Just test one image
    
    # Look for training images
    if not test_images and os.path.exists('data/train/images'):
        for file in os.listdir('data/train/images'):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join('data/train/images', file))
                break  # Just test one image
    
    if not test_images:
        print("❌ No test images found. Please add an image to test.")
        return
    
    for image_path in test_images:
        print(f"\n🖼️  Testing image: {image_path}")
        print("-" * 40)
        
        try:
            # Test cyclone detection with different confidence thresholds
            print("Testing detection with conf=0.5 (new default):")
            results_05 = astroalert.detect_cyclones(image_path, conf_threshold=0.5)
            
            print(f"  - Cyclones detected: {results_05['total_cyclones']}")
            if results_05['total_cyclones'] > 0:
                print(f"  - Average confidence: {results_05['avg_confidence']:.3f}")
                print(f"  - Max confidence: {results_05['max_confidence']:.3f}")
                print(f"  - Quality: {results_05.get('detection_quality', 'N/A')}")
            
            print("\nTesting detection with conf=0.3 (old default):")
            results_03 = astroalert.detect_cyclones(image_path, conf_threshold=0.3)
            
            print(f"  - Cyclones detected: {results_03['total_cyclones']}")
            if results_03['total_cyclones'] > 0:
                print(f"  - Average confidence: {results_03['avg_confidence']:.3f}")
                print(f"  - Max confidence: {results_03['max_confidence']:.3f}")
                print(f"  - Quality: {results_03.get('detection_quality', 'N/A')}")
            
            # Test full analysis
            print("\n🔄 Testing full AstroAlert analysis:")
            full_results = astroalert.run_complete_analysis(
                image_path=image_path,
                latitude=19.0760,
                longitude=72.8777,
                date_time=datetime.datetime.now()
            )
            
            detection = full_results['results']['detection']
            combined = full_results['results']['combined']
            
            print(f"  - Final cyclones detected: {detection['total_cyclones']}")
            print(f"  - AI risk score: {combined['ai_detection']['ai_risk_score']}")
            print(f"  - Combined risk score: {combined['combined_assessment']['combined_risk_score']:.1f}/100")
            print(f"  - Final risk level: {combined['combined_assessment']['final_risk_level']}")
            
        except Exception as e:
            print(f"❌ Error testing {image_path}: {e}")
    
    print(f"\n✅ Testing complete!")

if __name__ == "__main__":
    test_detection_improvements()
