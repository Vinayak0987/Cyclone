#!/usr/bin/env python3
"""
Comprehensive test to find examples where cyclones should be detected
"""

import os
import datetime
from main_astroalert_fixed import AstroAlert

def test_cyclone_detection_examples():
    """Test multiple images with different thresholds to find cyclone detections"""
    print("🌪️ Testing Cyclone Detection with Multiple Images and Thresholds")
    print("=" * 70)
    
    # Initialize AstroAlert
    astroalert = AstroAlert()
    
    # Get all available test images
    test_images = []
    
    # Training images
    train_dir = "data/train/images"
    if os.path.exists(train_dir):
        for file in os.listdir(train_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(train_dir, file))
    
    # Validation images
    val_dir = "data/val/images"
    if os.path.exists(val_dir):
        for file in os.listdir(val_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(val_dir, file))
    
    if not test_images:
        print("❌ No test images found!")
        return
    
    # Test with different confidence thresholds
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    print(f"Testing {len(test_images)} images with {len(thresholds)} confidence thresholds\n")
    
    best_detections = []
    
    for image_path in test_images:
        print(f"🖼️  Testing: {os.path.basename(image_path)}")
        print("-" * 50)
        
        for threshold in thresholds:
            try:
                results = astroalert.detect_cyclones(image_path, conf_threshold=threshold)
                
                total = results.get('total_cyclones', 0)
                if total > 0:
                    avg_conf = results.get('avg_confidence', 0)
                    max_conf = results.get('max_confidence', 0)
                    quality = results.get('detection_quality', 'N/A')
                    
                    print(f"  Threshold {threshold}: {total} cyclones (avg: {avg_conf:.3f}, max: {max_conf:.3f}, quality: {quality})")
                    
                    # Store good detections for further analysis
                    if max_conf > 0.2 or (total <= 10 and avg_conf > 0.1):
                        best_detections.append({
                            'image': image_path,
                            'threshold': threshold,
                            'total': total,
                            'avg_conf': avg_conf,
                            'max_conf': max_conf,
                            'quality': quality,
                            'results': results
                        })
                else:
                    print(f"  Threshold {threshold}: No cyclones detected")
                    
            except Exception as e:
                print(f"  Threshold {threshold}: Error - {e}")
        
        print()
    
    # Show best detections
    if best_detections:
        print("\n🎯 Best Detection Results Found:")
        print("=" * 70)
        
        # Sort by max confidence
        best_detections.sort(key=lambda x: x['max_conf'], reverse=True)
        
        for i, detection in enumerate(best_detections[:5]):  # Show top 5
            print(f"\n{i+1}. {os.path.basename(detection['image'])}")
            print(f"   Threshold: {detection['threshold']}")
            print(f"   Cyclones: {detection['total']}")
            print(f"   Max Confidence: {detection['max_conf']:.3f}")
            print(f"   Avg Confidence: {detection['avg_conf']:.3f}")
            print(f"   Quality: {detection['quality']}")
            
            # Test full analysis for the best detection
            if i == 0:  # Only for the very best
                print(f"\n   🔄 Running Full Analysis:")
                try:
                    full_results = astroalert.run_complete_analysis(
                        detection['image'],
                        latitude=19.0760,
                        longitude=72.8777,
                        date_time=datetime.datetime.now()
                    )
                    
                    combined = full_results['results']['combined']
                    print(f"   AI Risk Score: {combined['ai_detection']['ai_risk_score']}")
                    print(f"   Combined Risk: {combined['combined_assessment']['combined_risk_score']:.1f}/100")
                    print(f"   Risk Level: {combined['combined_assessment']['final_risk_level']}")
                    
                except Exception as e:
                    print(f"   Full analysis error: {e}")
    
    else:
        print("\n❌ No meaningful cyclone detections found!")
        print("This might indicate:")
        print("1. The model needs retraining")
        print("2. The test images don't contain visible cyclones")
        print("3. The confidence thresholds are still too high")
        print("4. The model weights are missing or incorrect")
    
    print(f"\n✅ Detection testing complete!")

def test_specific_image_detailed(image_path, threshold=0.1):
    """Test a specific image with detailed output"""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
        
    print(f"\n🔍 Detailed Analysis of: {image_path}")
    print("=" * 60)
    
    astroalert = AstroAlert()
    
    try:
        # Test detection
        results = astroalert.detect_cyclones(image_path, conf_threshold=threshold)
        
        print(f"Confidence Threshold: {threshold}")
        print(f"Total Detections: {results.get('total_cyclones', 0)}")
        
        if results.get('total_cyclones', 0) > 0:
            print(f"Average Confidence: {results.get('avg_confidence', 0):.4f}")
            print(f"Max Confidence: {results.get('max_confidence', 0):.4f}")
            print(f"Detection Quality: {results.get('detection_quality', 'N/A')}")
            
            # Show individual detections
            detections = results.get('detections', [])
            confidence_scores = results.get('confidence_scores', [])
            
            print(f"\nIndividual Detections:")
            for i, (det, conf) in enumerate(zip(detections[:10], confidence_scores[:10])):  # Show first 10
                bbox = det.get('bbox', [])
                print(f"  {i+1}. Confidence: {conf:.4f}, BBox: [{bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f}, {bbox[3]:.3f}]")
            
            if len(detections) > 10:
                print(f"  ... and {len(detections)-10} more detections")
                
            # Full analysis
            print(f"\n🔄 Full AstroAlert Analysis:")
            full_results = astroalert.run_complete_analysis(
                image_path,
                latitude=19.0760,
                longitude=72.8777,
                date_time=datetime.datetime.now()
            )
            
            combined = full_results['results']['combined']
            print(f"AI Risk Score: {combined['ai_detection']['ai_risk_score']}")
            print(f"Combined Risk Score: {combined['combined_assessment']['combined_risk_score']:.1f}/100")
            print(f"Final Risk Level: {combined['combined_assessment']['final_risk_level']}")
            print(f"Action Required: {combined['combined_assessment']['action_required']}")
            
        else:
            print("No cyclones detected with this threshold")
            
    except Exception as e:
        print(f"❌ Error during detailed analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run comprehensive test
    test_cyclone_detection_examples()
    
    # Test a specific image in detail (you can change this)
    print("\n" + "="*80)
    test_specific_image_detailed("data/train/images/2.jpg", threshold=0.1)
