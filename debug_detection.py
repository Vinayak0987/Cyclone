#!/usr/bin/env python3
"""
Simple debug script to test cyclone detection
"""

from main_astroalert_fixed import AstroAlert
import datetime

def debug_detection():
    """Debug cyclone detection with very low threshold"""
    print("🐛 Debug: Testing cyclone detection with very low threshold")
    print("=" * 60)
    
    astroalert = AstroAlert()
    
    # Test with low threshold to get some detections
    image_path = "data/train/images/2.jpg"
    threshold = 0.02
    
    print(f"Testing: {image_path}")
    print(f"Threshold: {threshold}")
    
    try:
        results = astroalert.detect_cyclones(image_path, conf_threshold=threshold)
        
        print(f"Total detections: {results.get('total_cyclones', 0)}")
        
        if results.get('total_cyclones', 0) > 0:
            print(f"Average confidence: {results.get('avg_confidence', 0):.4f}")
            print(f"Max confidence: {results.get('max_confidence', 0):.4f}")
            print(f"Quality: {results.get('detection_quality', 'N/A')}")
            
            # Show first few detections
            detections = results.get('detections', [])[:5]
            confidence_scores = results.get('confidence_scores', [])[:5]
            
            print("\nFirst 5 detections:")
            for i, (det, conf) in enumerate(zip(detections, confidence_scores)):
                bbox = det.get('bbox', [])
                print(f"  {i+1}. Confidence: {conf:.4f}, BBox: {bbox}")
                
            # Test full analysis
            print("\n🔄 Full Analysis:")
            full_results = astroalert.run_complete_analysis(
                image_path,
                latitude=19.0760,
                longitude=72.8777,
                date_time=datetime.datetime.now()
            )
            
            combined = full_results['results']['combined']
            print(f"AI Risk Score: {combined['ai_detection']['ai_risk_score']}")
            print(f"Combined Risk: {combined['combined_assessment']['combined_risk_score']:.1f}/100")
            print(f"Risk Level: {combined['combined_assessment']['final_risk_level']}")
            
        else:
            print("❌ No detections found even with threshold 0.01")
            print("This suggests the YOLOv5 model is not detecting anything at all.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_detection()
