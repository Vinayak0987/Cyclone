"""
AstroAlert - Vedic Astrology Risk Assessment Module (Clean Version)
Calculates planetary positions and Vedic Astrology Risk Scores (VRS) for cyclone prediction
"""

import swisseph as swe
import datetime
import math
from typing import Dict, List, Tuple, Optional

class VedicAstrologyAnalyzer:
    def __init__(self, ephemeris_path: str = "ephe"):
        """
        Initialize the Vedic Astrology Analyzer
        
        Args:
            ephemeris_path: Path to Swiss Ephemeris files
        """
        self.ephemeris_path = ephemeris_path
        swe.set_ephe_path(ephemeris_path)
        
        # Planetary IDs for Swiss Ephemeris
        self.planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE
        }
        
        # Zodiac signs
        self.zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        # Nakshatras (27 lunar mansions)
        self.nakshatras = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
                          'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
                          'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
                          'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana',
                          'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']
        
        # Tithis (lunar days)
        self.tithis = ['Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami', 'Shashthi',
                      'Saptami', 'Ashtami', 'Navami', 'Dashami', 'Ekadashi', 'Dwadashi',
                      'Trayodashi', 'Chaturdashi', 'Purnima', 'Pratipada', 'Dwitiya', 'Tritiya',
                      'Chaturthi', 'Panchami', 'Shashthi', 'Saptami', 'Ashtami', 'Navami',
                      'Dashami', 'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Amavasya']

    def calculate_planetary_positions(self, date_time: datetime.datetime, latitude: float, longitude: float) -> Dict:
        """
        Calculate planetary positions for given date, time, and location
        
        Args:
            date_time: Date and time of the event
            latitude: Latitude of the location
            longitude: Location longitude
            
        Returns:
            Dictionary with planetary positions and astrological data
        """
        # Convert to Julian Day Number
        jd = swe.julday(date_time.year, date_time.month, date_time.day, 
                       date_time.hour + date_time.minute/60.0)
        
        # Calculate planetary positions
        planetary_data = {}
        
        for planet_name, planet_id in self.planets.items():
            try:
                # Calculate planetary position
                planet_pos = swe.calc_ut(jd, planet_id)
                if planet_pos[0] == 0:  # Success
                    longitude_deg = planet_pos[1][0]  # Longitude
                    planetary_data[planet_name] = {
                        'longitude': longitude_deg,
                        'sign': self._get_zodiac_sign(longitude_deg),
                        'nakshatra': self._get_nakshatra(longitude_deg),
                        'house': self._get_house(longitude_deg)
                    }
                else:
                    planetary_data[planet_name] = None
            except Exception as e:
                print(f"Error calculating {planet_name}: {e}")
                planetary_data[planet_name] = None
        
        # Calculate ascendant
        try:
            ascendant = swe.house_pos(jd, latitude, longitude)[0]
        except:
            ascendant = 0
        
        # Calculate tithi (lunar day)
        try:
            moon_pos = planetary_data.get('Moon', {})
            sun_pos = planetary_data.get('Sun', {})
            if moon_pos and sun_pos:
                moon_long = moon_pos['longitude']
                sun_long = sun_pos['longitude']
                tithi_num = int((moon_long - sun_long) / 12) % 30
                tithi = self.tithis[tithi_num]
            else:
                tithi = "Unknown"
        except:
            tithi = "Unknown"
        
        return {
            'planets': planetary_data,
            'tithi': tithi,
            'ascendant': ascendant,
            'julian_day': jd,
            'date_time': date_time.isoformat(),
            'location': {
                'latitude': latitude,
                'longitude': longitude
            }
        }

    def _get_zodiac_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude"""
        sign_index = int(longitude / 30)
        return self.zodiac_signs[sign_index]
    
    def _get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra from longitude"""
        nakshatra_index = int(longitude / 13.333333)
        return self.nakshatras[nakshatra_index]
    
    def _get_house(self, longitude: float) -> int:
        """Get house number from longitude (1-12)"""
        house_num = int(longitude / 30) + 1
        return house_num if house_num <= 12 else house_num - 12

    def calculate_vrs_score(self, planetary_data: Dict) -> Dict:
        """
        Calculate Vedic Astrology Risk Score (VRS) based on planetary positions
        
        Args:
            planetary_data: Dictionary with planetary positions
            
        Returns:
            Dictionary with VRS analysis
        """
        vrs_score = 0
        risk_factors = []
        
        try:
            # Check ascendant position
            ascendant = planetary_data.get('ascendant', 0)
            if ascendant:
                ascendant_sign = self._get_zodiac_sign(ascendant)
                if ascendant_sign in ['Cancer', 'Scorpio', 'Pisces']:  # Water signs
                    vrs_score += 12
                    risk_factors.append(f"Ascendant in water sign {ascendant_sign} (+12)")
                
                if ascendant_sign in ['Aries', 'Leo', 'Sagittarius']:  # Fire signs
                    vrs_score += 8
                    risk_factors.append(f"Ascendant in fire sign {ascendant_sign} (+8)")
            
            # Check planetary positions
            planets = planetary_data.get('planets', {})
            
            # Check Sun position
            sun = planets.get('Sun')
            if sun:
                sun_sign = sun['sign']
                if sun_sign in ['Cancer', 'Scorpio']:
                    vrs_score += 15
                    risk_factors.append(f"Sun in water sign {sun_sign} (+15)")
            
            # Check Moon position
            moon = planets.get('Moon')
            if moon:
                moon_sign = moon['sign']
                if moon_sign in ['Cancer', 'Scorpio', 'Pisces']:
                    vrs_score += 10
                    risk_factors.append(f"Moon in water sign {moon_sign} (+10)")
            
            # Check Mars position
            mars = planets.get('Mars')
            if mars:
                mars_sign = mars['sign']
                if mars_sign in ['Cancer', 'Scorpio']:
                    vrs_score += 20
                    risk_factors.append(f"Mars in water sign {mars_sign} (+20)")
            
            # Check Saturn position
            saturn = planets.get('Saturn')
            if saturn:
                saturn_sign = saturn['sign']
                if saturn_sign in ['Cancer', 'Scorpio']:
                    vrs_score += 18
                    risk_factors.append(f"Saturn in water sign {saturn_sign} (+18)")
            
            # Check Rahu position
            rahu = planets.get('Rahu')
            if rahu:
                rahu_sign = rahu['sign']
                if rahu_sign in ['Cancer', 'Scorpio', 'Pisces']:
                    vrs_score += 25
                    risk_factors.append(f"Rahu in water sign {rahu_sign} (+25)")
            
            # Determine risk level
            if vrs_score >= 70:
                risk_level = "EXTREME"
            elif vrs_score >= 50:
                risk_level = "HIGH"
            elif vrs_score >= 30:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW"
            
            # Generate analysis
            if risk_level == "EXTREME":
                analysis = f"Extreme cyclone risk detected (VRS: {vrs_score:.1f}/100). Critical planetary alignments suggest severe weather conditions. Immediate action required."
            elif risk_level == "HIGH":
                analysis = f"High cyclone risk detected (VRS: {vrs_score:.1f}/100). Planetary positions indicate significant weather disturbances. Prepare for severe conditions."
            elif risk_level == "MODERATE":
                analysis = f"Moderate cyclone risk detected (VRS: {vrs_score:.1f}/100). Some planetary factors suggest weather instability. Monitor conditions closely."
            else:
                analysis = f"Low cyclone risk detected (VRS: {vrs_score:.1f}/100). Planetary positions are generally favorable. Standard weather monitoring recommended."
            
            return {
                'vrs_score': vrs_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'total_factors': len(risk_factors),
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Error calculating VRS: {e}")
            return {
                'vrs_score': 0,
                'risk_level': 'UNKNOWN',
                'risk_factors': [],
                'total_factors': 0,
                'analysis': 'Error in VRS calculation'
            }

    def get_cyclone_prediction(self, date_time: datetime.datetime, latitude: float, longitude: float) -> Dict:
        """
        Get complete cyclone prediction using Vedic astrology
        
        Args:
            date_time: Date and time for prediction
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Complete prediction results
        """
        try:
            # Calculate planetary positions
            planetary_data = self.calculate_planetary_positions(date_time, latitude, longitude)
            
            # Calculate VRS score
            vrs_analysis = self.calculate_vrs_score(planetary_data)
            
            # Generate summary
            summary = f"Cyclone Risk: {vrs_analysis['risk_level']} (VRS: {vrs_analysis['vrs_score']:.1f}/100)"
            
            return {
                'prediction_time': date_time.isoformat(),
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'planetary_positions': planetary_data,
                'vrs_analysis': vrs_analysis,
                'summary': summary
            }
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return {
                'error': str(e),
                'vrs_analysis': {
                    'vrs_score': 0,
                    'risk_level': 'UNKNOWN',
                    'risk_factors': [],
                    'analysis': 'Error in prediction'
                }
            }

# Test the module
if __name__ == "__main__":
    print("Testing Vedic Astrology Module...")
    print("=" * 40)
    
    try:
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
        
        print(f"🔮 Prediction: {result['summary']}")
        print(f"⚠️  Risk Level: {result['vrs_analysis']['risk_level']}")
        print(f"🔢 VRS Score: {result['vrs_analysis']['vrs_score']:.1f}/100")
        print(f"📊 Risk Factors: {result['vrs_analysis']['total_factors']}")
        
        if result['vrs_analysis']['risk_factors']:
            print("📋 Risk Factors:")
            for factor in result['vrs_analysis']['risk_factors']:
                print(f"  • {factor}")
        
        print(f"📝 Analysis: {result['vrs_analysis']['analysis']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Please check if Swiss Ephemeris files are available in the 'ephe' directory.")
