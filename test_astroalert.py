"""
Test Script for AstroAlert System
Tests individual components and integration
"""

import datetime
from astrology_module import VedicAstrologyAnalyzer

def test_astrology_module():
    """Test the astrology module independently"""
    print("🧪 Testing Astrology Module...")
    print("=" * 40)
    
    try:
        # Initialize analyzer
        analyzer = VedicAstrologyAnalyzer()
        print("✅ Astrology analyzer initialized successfully")
        
        # Test with sample data
        test_date = datetime.datetime(2024, 8, 15, 12, 0, 0)
        test_lat = 19.0760  # Mumbai
        test_lon = 72.8777  # Mumbai
        
        print(f"📅 Test Date: {test_date}")
        print(f"📍 Test Location: {test_lat}, {test_lon}")
        
        # Get prediction
        result = analyzer.get_cyclone_prediction(test_date, test_lat, test_lon)
        
        print(f"🔮 VRS Score: {result['vrs_analysis']['vrs_score']:.1f}/100")
        print(f"⚠️  Risk Level: {result['vrs_analysis']['risk_level']}")
        print(f"📊 Risk Factors: {len(result['vrs_analysis']['risk_factors'])}")
        
        if result['vrs_analysis']['risk_factors']:
            print("📋 Risk Factors:")
            for factor in result['vrs_analysis']['risk_factors']:
                print(f"  • {factor}")
        
        print(f"📝 Analysis: {result['vrs_analysis']['analysis']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing astrology module: {e}")
        return False

def test_planetary_calculations():
    """Test planetary position calculations"""
    print("\n🔮 Testing Planetary Calculations...")
    print("=" * 40)
    
    try:
        analyzer = VedicAstrologyAnalyzer()
        
        # Test different dates
        test_dates = [
            datetime.datetime(2024, 8, 15, 12, 0, 0),  # August 15
            datetime.datetime(2024, 9, 15, 12, 0, 0),  # September 15
            datetime.datetime(2024, 10, 15, 12, 0, 0), # October 15
        ]
        
        for test_date in test_dates:
            print(f"\n📅 Testing Date: {test_date.strftime('%Y-%m-%d')}")
            
            planetary_data = analyzer.calculate_planetary_positions(
                test_date, 19.0760, 72.8777
            )
            
            if planetary_data['planets']:
                print(f"  🌞 Sun: {planetary_data['planets']['Sun']['sign']} {planetary_data['planets']['Sun']['nakshatra']}")
                print(f"  🌙 Moon: {planetary_data['planets']['Moon']['sign']} {planetary_data['planets']['Moon']['nakshatra']}")
                print(f"  🔴 Mars: {planetary_data['planets']['Mars']['sign']} {planetary_data['planets']['Mars']['nakshatra']}")
                print(f"  🪐 Saturn: {planetary_data['planets']['Saturn']['sign']} {planetary_data['planets']['Saturn']['nakshatra']}")
                print(f"  📅 Tithi: {planetary_data['tithi']}")
                print(f"  🏠 Ascendant: {planetary_data['planets']['Sun']['sign']}")  # Using Sun sign as proxy
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing planetary calculations: {e}")
        return False

def main():
    """Run all tests"""
    print("🌪 AstroAlert System Testing")
    print("=" * 50)
    
    # Test 1: Astrology Module
    test1_passed = test_astrology_module()
    
    # Test 2: Planetary Calculations
    test2_passed = test_planetary_calculations()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Astrology Module: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Planetary Calculations: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! AstroAlert system is ready.")
        print("Next step: Test with YOLOv5 integration")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return test1_passed and test2_passed

if __name__ == "__main__":
    main()
