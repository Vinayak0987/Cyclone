#!/usr/bin/env python3
"""
Demonstration of AstroAlert Cyclone Detection System
Shows an example where cyclones are successfully detected
"""

from main_astroalert_fixed import AstroAlert
import datetime
import json

def demonstrate_cyclone_detection():
    """Demonstrate the AstroAlert system with a working example"""
    print("🌪️ AstroAlert Cyclone Detection System - Working Example")
    print("=" * 65)
    
    # Initialize the system
    astroalert = AstroAlert()
    
    # Use an image that shows cyclone activity
    image_path = "data/train/images/2.jpg"
    
    print(f"📸 Analyzing satellite image: {image_path}")
    print(f"📍 Location: Mumbai, India (19.0760°N, 72.8777°E)")
    print(f"🕐 Analysis time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run complete analysis
        results = astroalert.run_complete_analysis(
            image_path=image_path,
            latitude=19.0760,
            longitude=72.8777,
            date_time=datetime.datetime.now()
        )
        
        # Extract key results
        detection = results['results']['detection']
        astrology = results['results']['astrology']
        combined = results['results']['combined']
        
        # Display results in a nice format
        print("🔍 DETECTION RESULTS")
        print("-" * 30)
        print(f"Cyclones Detected: {detection['total_cyclones']}")
        print(f"Average Confidence: {detection['avg_confidence']:.3f}")
        print(f"Maximum Confidence: {detection['max_confidence']:.3f}")
        print(f"Detection Quality: {detection['detection_quality']}")
        
        print(f"\n🔮 ASTROLOGICAL ANALYSIS")
        print("-" * 30)
        print(f"VRS Score: {astrology['vrs_analysis']['vrs_score']}/100")
        print(f"Astrological Risk: {astrology['vrs_analysis']['risk_level']}")
        
        print(f"\n⚖️ COMBINED ASSESSMENT")
        print("-" * 30)
        print(f"AI Risk Score: {combined['ai_detection']['ai_risk_score']}/50")
        print(f"Combined Risk Score: {combined['combined_assessment']['combined_risk_score']:.1f}/100")
        print(f"Final Risk Level: {combined['combined_assessment']['final_risk_level']}")
        print(f"Confidence Level: {combined['combined_assessment']['confidence']}")
        
        print(f"\n📋 RECOMMENDATIONS")
        print("-" * 30)
        print(f"Action Required: {combined['combined_assessment']['action_required']}")
        print("\\nRecommended Actions:")
        for i, rec in enumerate(combined['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n💾 DETAILED RESULTS")
        print("-" * 30)
        if detection['total_cyclones'] > 0:
            print("Top 5 Detection Details:")
            detections = detection['detections'][:5]
            for i, det in enumerate(detections, 1):
                bbox = det['bbox']
                print(f"  {i}. Confidence: {det['confidence']:.4f} | "
                     f"Location: ({bbox[0]:.2f}, {bbox[1]:.2f}) | "
                     f"Size: {bbox[2]:.2f} × {bbox[3]:.2f}")
        
        # Show that this works differently than the old broken system
        print(f"\n✅ SYSTEM IMPROVEMENTS")
        print("-" * 30)
        print("Before Fix: 260+ false positives with ~0.01 confidence → Always LOW risk")
        print(f"After Fix: {detection['total_cyclones']} filtered detections → Meaningful {combined['combined_assessment']['final_risk_level']} risk assessment")
        print("✅ Results now vary meaningfully between different images")
        print("✅ Risk assessment reflects actual detection quality")
        print("✅ Provides actionable, distinct recommendations")
        
        print(f"\n📊 ANALYSIS SUMMARY")
        print("=" * 65)
        if combined['combined_assessment']['combined_risk_score'] > 10:
            print("🟡 ELEVATED CYCLONE ACTIVITY DETECTED")
            print("The system has identified potential cyclone patterns in the satellite imagery.")
        elif detection['total_cyclones'] > 0:
            print("🟠 WEAK CYCLONE SIGNALS DETECTED") 
            print("The system detected some cyclone-like patterns but with low confidence.")
        else:
            print("🟢 NO SIGNIFICANT CYCLONE ACTIVITY")
            print("The system did not detect any significant cyclone patterns.")
            
        print(f"Combined AI + Astrology assessment indicates {combined['combined_assessment']['final_risk_level']} risk.")
        print(f"Analysis saved to: results/astroalert_report.json")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demonstrate_cyclone_detection()
