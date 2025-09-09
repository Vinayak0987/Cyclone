"""
AstroAlert - Enhanced Vedic Astrology Risk Assessment Module
Calculates planetary positions and Vedic Astrology Risk Scores (VRS) for cyclone prediction
"""

import datetime
import math
from typing import Dict, List, Tuple, Optional

try:
    import swisseph as swe
    SWISS_EPHEMERIS_AVAILABLE = True
except ImportError:
    SWISS_EPHEMERIS_AVAILABLE = False
    print("⚠️ Swiss Ephemeris not available. Using fallback calculations.")

class VedicAstrologyAnalyzer:
    def __init__(self, ephemeris_path: str = "ephe"):
        """
        Initialize the Enhanced Vedic Astrology Analyzer
        
        Args:
            ephemeris_path: Path to Swiss Ephemeris files
        """
        self.ephemeris_path = ephemeris_path
        
        if SWISS_EPHEMERIS_AVAILABLE:
            try:
                swe.set_ephe_path(ephemeris_path)
                print("✅ Swiss Ephemeris initialized")
            except:
                print("⚠️ Swiss Ephemeris path not found, using built-in data")
        
        # Planetary IDs for Swiss Ephemeris
        self.planets = {
            'Sun': swe.SUN if SWISS_EPHEMERIS_AVAILABLE else 0,
            'Moon': swe.MOON if SWISS_EPHEMERIS_AVAILABLE else 1,
            'Mercury': swe.MERCURY if SWISS_EPHEMERIS_AVAILABLE else 2,
            'Venus': swe.VENUS if SWISS_EPHEMERIS_AVAILABLE else 3,
            'Mars': swe.MARS if SWISS_EPHEMERIS_AVAILABLE else 4,
            'Jupiter': swe.JUPITER if SWISS_EPHEMERIS_AVAILABLE else 5,
            'Saturn': swe.SATURN if SWISS_EPHEMERIS_AVAILABLE else 6,
            'Rahu': swe.MEAN_NODE if SWISS_EPHEMERIS_AVAILABLE else 7,
            'Ketu': None  # Calculated from Rahu
        }
        
        # Nakshatra names
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
            "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        # Tithi names
        self.tithis = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
        ]
        
        print("🔮 Enhanced Vedic Astrology Analyzer initialized")

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
        if SWISS_EPHEMERIS_AVAILABLE:
            return self._calculate_with_swiss_ephemeris(date_time, latitude, longitude)
        else:
            return self._calculate_with_fallback(date_time, latitude, longitude)

    def _calculate_with_swiss_ephemeris(self, date_time: datetime.datetime, latitude: float, longitude: float) -> Dict:
        """Calculate using Swiss Ephemeris (accurate)"""
        try:
            # Convert to Julian Day Number
            jd = swe.julday(date_time.year, date_time.month, date_time.day, 
                           date_time.hour + date_time.minute/60.0)
            
            # Calculate planetary positions
            planetary_data = {}
            
            for planet_name, planet_id in self.planets.items():
                if planet_id is not None:
                    try:
                        # Get planetary position
                        result = swe.calc_ut(jd, planet_id)
                        planet_longitude = result[0]  # Ecliptic longitude
                        
                        # Calculate additional data
                        nakshatra = self._get_nakshatra(planet_longitude)
                        house = self._calculate_vedic_house(planet_longitude, latitude, longitude)
                        
                        planetary_data[planet_name] = {
                            'longitude': planet_longitude,
                            'nakshatra': nakshatra,
                            'house': house,
                            'degree': planet_longitude % 30,
                            'sign': self._get_zodiac_sign(planet_longitude)
                        }
                    except Exception as e:
                        print(f"Error calculating {planet_name}: {e}")
                        planetary_data[planet_name] = None
            
            # Calculate Ketu (South Node) - 180° opposite to Rahu
            if 'Rahu' in planetary_data and planetary_data['Rahu']:
                rahu_long = planetary_data['Rahu']['longitude']
                ketu_long = (rahu_long + 180) % 360
                ketu_nakshatra = self._get_nakshatra(ketu_long)
                ketu_house = self._calculate_vedic_house(ketu_long, latitude, longitude)
                
                planetary_data['Ketu'] = {
                    'longitude': ketu_long,
                    'nakshatra': ketu_nakshatra,
                    'house': ketu_house,
                    'degree': ketu_long % 30,
                    'sign': self._get_zodiac_sign(ketu_long)
                }
            
            # Calculate tithi (lunar phase)
            sun_long = planetary_data['Sun']['longitude'] if planetary_data['Sun'] else 0
            moon_long = planetary_data['Moon']['longitude'] if planetary_data['Moon'] else 0
            tithi = self._calculate_tithi(sun_long, moon_long)
            
            # Calculate ascendant (Lagna)
            ascendant = self._calculate_ascendant(jd, latitude, longitude)
            
            return {
                'planets': planetary_data,
                'tithi': tithi,
                'ascendant': ascendant,
                'julian_day': jd,
                'date_time': date_time,
                'location': {'latitude': latitude, 'longitude': longitude},
                'calculation_method': 'swiss_ephemeris'
            }
            
        except Exception as e:
            print(f"Swiss Ephemeris calculation failed: {e}")
            return self._calculate_with_fallback(date_time, latitude, longitude)

    def _calculate_with_fallback(self, date_time: datetime.datetime, latitude: float, longitude: float) -> Dict:
        """Fallback calculation method using simplified algorithms"""
        print("🔄 Using fallback calculation method")
        
        # Simplified planetary position calculations
        # These are approximations and not astronomically accurate
        julian_day = self._calculate_julian_day(date_time)
        
        # Generate pseudo-realistic planetary positions
        planetary_data = {}
        
        # Use date-based seed for consistent results
        date_seed = date_time.toordinal()
        
        for i, planet_name in enumerate(['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu']):
            # Generate longitude based on date and planet characteristics
            if planet_name == 'Sun':
                # Sun's annual motion
                longitude = ((date_time.timetuple().tm_yday - 1) * 0.9856) % 360
            elif planet_name == 'Moon':
                # Moon's monthly motion (approximation)
                longitude = ((date_time.day - 1) * 12.19) % 360
            elif planet_name == 'Mercury':
                # Mercury's quick motion
                longitude = ((date_seed * 4.092) % 360)
            elif planet_name == 'Venus':
                # Venus motion
                longitude = ((date_seed * 1.602) % 360)
            elif planet_name == 'Mars':
                # Mars motion
                longitude = ((date_seed * 0.524) % 360)
            elif planet_name == 'Jupiter':
                # Jupiter motion
                longitude = ((date_seed * 0.083) % 360)
            elif planet_name == 'Saturn':
                # Saturn motion
                longitude = ((date_seed * 0.034) % 360)
            else:  # Rahu
                # Rahu retrograde motion
                longitude = (360 - (date_seed * 0.053) % 360)
            
            # Add some realistic variation
            longitude = (longitude + math.sin(date_seed * 0.1) * 15) % 360
            
            planetary_data[planet_name] = {
                'longitude': longitude,
                'nakshatra': self._get_nakshatra(longitude),
                'house': (int(longitude / 30) + 1),
                'degree': longitude % 30,
                'sign': self._get_zodiac_sign(longitude)
            }
        
        # Calculate Ketu
        if 'Rahu' in planetary_data:
            rahu_long = planetary_data['Rahu']['longitude']
            ketu_long = (rahu_long + 180) % 360
            
            planetary_data['Ketu'] = {
                'longitude': ketu_long,
                'nakshatra': self._get_nakshatra(ketu_long),
                'house': (int(ketu_long / 30) + 1),
                'degree': ketu_long % 30,
                'sign': self._get_zodiac_sign(ketu_long)
            }
        
        # Calculate tithi
        sun_long = planetary_data['Sun']['longitude']
        moon_long = planetary_data['Moon']['longitude']
        tithi = self._calculate_tithi(sun_long, moon_long)
        
        # Simple ascendant calculation
        ascendant = (longitude + (date_time.hour * 15)) % 360
        
        return {
            'planets': planetary_data,
            'tithi': tithi,
            'ascendant': ascendant,
            'julian_day': julian_day,
            'date_time': date_time,
            'location': {'latitude': latitude, 'longitude': longitude},
            'calculation_method': 'fallback_approximation'
        }

    def calculate_vrs_score(self, planetary_data: Dict) -> Dict:
        """
        Calculate Enhanced Vedic Astrology Risk Score (VRS) for cyclone prediction
        
        Args:
            planetary_data: Planetary positions and astrological data
            
        Returns:
            Dictionary with VRS score and detailed analysis
        """
        vrs_score = 0
        risk_factors = []
        
        planets = planetary_data['planets']
        
        # Factor 1: Malefic planets in water signs (Cancer, Scorpio, Pisces)
        water_signs = ['Cancer', 'Scorpio', 'Pisces']
        malefic_planets = ['Mars', 'Saturn', 'Rahu', 'Ketu']
        
        for planet in malefic_planets:
            if planet in planets and planets[planet]:
                sign = planets[planet]['sign']
                if sign in water_signs:
                    vrs_score += 15
                    risk_factors.append(f"{planet} in water sign {sign} (+15)")
        
        # Factor 2: Sun-Moon conjunction or opposition (eclipse-like conditions)
        if planets.get('Sun') and planets.get('Moon'):
            sun_long = planets['Sun']['longitude']
            moon_long = planets['Moon']['longitude']
            angle = abs(sun_long - moon_long)
            angle = min(angle, 360 - angle)  # Take smaller angle
            
            if angle <= 10:  # Conjunction
                vrs_score += 25
                risk_factors.append(f"Sun-Moon conjunction: {angle:.1f}° (+25)")
            elif angle >= 170:  # Opposition
                vrs_score += 20
                risk_factors.append(f"Sun-Moon opposition: {angle:.1f}° (+20)")
        
        # Factor 3: Saturn in critical houses (4th, 8th, 12th)
        if planets.get('Saturn'):
            house = planets['Saturn']['house']
            if house in [4, 8, 12]:
                vrs_score += 18
                risk_factors.append(f"Saturn in critical house {house} (+18)")
        
        # Factor 4: Rahu-Ketu axis in water signs
        if planets.get('Rahu') and planets.get('Ketu'):
            rahu_sign = planets['Rahu']['sign']
            ketu_sign = planets['Ketu']['sign']
            if rahu_sign in water_signs or ketu_sign in water_signs:
                vrs_score += 12
                risk_factors.append(f"Rahu-Ketu axis in water signs (+12)")
        
        # Factor 5: Mars-Saturn conjunction or opposition
        if planets.get('Mars') and planets.get('Saturn'):
            mars_long = planets['Mars']['longitude']
            saturn_long = planets['Saturn']['longitude']
            angle = abs(mars_long - saturn_long)
            angle = min(angle, 360 - angle)
            
            if angle <= 8:  # Conjunction
                vrs_score += 25
                risk_factors.append(f"Mars-Saturn conjunction: {angle:.1f}° (+25)")
            elif angle >= 172:  # Opposition
                vrs_score += 22
                risk_factors.append(f"Mars-Saturn opposition: {angle:.1f}° (+22)")
        
        # Factor 6: Critical nakshatras (water-related)
        water_nakshatras = ['Rohini', 'Ardra', 'Pushya', 'Ashlesha', 'Purva Ashadha', 'Uttara Ashadha', 'Revati']
        for planet_name, planet_data in planets.items():
            if planet_data and planet_data['nakshatra'] in water_nakshatras:
                if planet_name in malefic_planets:
                    vrs_score += 10
                    risk_factors.append(f"{planet_name} in water nakshatra {planet_data['nakshatra']} (+10)")
                elif planet_name in ['Sun', 'Moon']:
                    vrs_score += 8
                    risk_factors.append(f"{planet_name} in water nakshatra {planet_data['nakshatra']} (+8)")
        
        # Factor 7: Tithi analysis (critical lunar phases)
        tithi = planetary_data['tithi']
        critical_tithis = ['Chaturdashi', 'Purnima/Amavasya', 'Ashtami', 'Navami']
        if tithi in critical_tithis:
            vrs_score += 10
            risk_factors.append(f"Critical tithi: {tithi} (+10)")
        
        # Factor 8: Ascendant in water signs
        ascendant_sign = self._get_zodiac_sign(planetary_data['ascendant'])
        if ascendant_sign in water_signs:
            vrs_score += 12
            risk_factors.append(f"Ascendant in water sign {ascendant_sign} (+12)")
        
        # Factor 9: Seasonal considerations
        month = planetary_data['date_time'].month
        if month in [6, 7, 8, 9]:  # Monsoon season in India
            vrs_score += 8
            risk_factors.append("Monsoon season influence (+8)")
        
        # Factor 10: Location-based factors
        latitude = planetary_data['location']['latitude']
        if abs(latitude) < 30:  # Tropical regions
            vrs_score += 5
            risk_factors.append("Tropical latitude (+5)")
        
        # Normalize VRS score to 0-100 range
        vrs_score = min(100, vrs_score)
        
        # Determine risk level with enhanced thresholds
        if vrs_score >= 70:
            risk_level = "EXTREME"
        elif vrs_score >= 50:
            risk_level = "HIGH"
        elif vrs_score >= 30:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        return {
            'vrs_score': vrs_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'total_factors': len(risk_factors),
            'analysis': self._get_risk_analysis(vrs_score, risk_level),
            'calculation_method': planetary_data.get('calculation_method', 'unknown')
        }

    def _get_zodiac_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_index = int(longitude / 30) % 12
        return signs[sign_index]
    
    def _get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra from longitude"""
        nakshatra_index = int(longitude / 13.333333) % 27
        return self.nakshatras[nakshatra_index]
    
    def _calculate_tithi(self, sun_long: float, moon_long: float) -> str:
        """Calculate tithi (lunar phase)"""
        angle = (moon_long - sun_long) % 360
        tithi_index = min(int(angle / 12), 14)
        return self.tithis[tithi_index]

    def _calculate_vedic_house(self, longitude: float, latitude: float, asc_long: float) -> int:
        """Calculate Vedic house position (simplified)"""
        house_angle = (longitude - asc_long) % 360
        house_number = int(house_angle / 30) + 1
        return house_number if house_number <= 12 else house_number - 12

    def _calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> float:
        """Calculate ascendant (Lagna)"""
        if SWISS_EPHEMERIS_AVAILABLE:
            try:
                st = swe.sidtime(jd)
                result = swe.house_pos(st, latitude, longitude, b'P')
                return result[0]
            except:
                pass
        
        # Fallback calculation
        lst = (jd - 2451545.0) * 0.00273781 * 15 + longitude
        return lst % 360

    def _calculate_julian_day(self, date_time: datetime.datetime) -> float:
        """Calculate Julian Day Number (fallback method)"""
        a = (14 - date_time.month) // 12
        y = date_time.year + 4800 - a
        m = date_time.month + 12 * a - 3
        
        jd = date_time.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd += (date_time.hour + date_time.minute / 60.0) / 24.0
        
        return jd

    def _get_risk_analysis(self, vrs_score: float, risk_level: str) -> str:
        """Get detailed risk analysis based on VRS score"""
        if risk_level == "EXTREME":
            return f"Extreme cyclone risk detected (VRS: {vrs_score:.1f}/100). Multiple critical planetary combinations suggest very high probability of severe weather conditions. Immediate emergency preparedness required."
        elif risk_level == "HIGH":
            return f"High cyclone risk detected (VRS: {vrs_score:.1f}/100). Several concerning planetary alignments present. Enhanced monitoring and preparedness measures recommended."
        elif risk_level == "MODERATE":
            return f"Moderate cyclone risk detected (VRS: {vrs_score:.1f}/100). Some planetary factors indicate elevated risk. Monitor weather conditions and maintain standard preparedness."
        else:
            return f"Low cyclone risk detected (VRS: {vrs_score:.1f}/100). Planetary positions are generally favorable. Standard weather monitoring recommended."

    def get_cyclone_prediction(self, date_time: datetime.datetime, latitude: float, longitude: float) -> Dict:
        """
        Complete cyclone prediction using Enhanced Vedic astrology
        
        Args:
            date_time: Date and time for prediction
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Complete prediction with VRS score and analysis
        """
        try:
            # Calculate planetary positions
            planetary_data = self.calculate_planetary_positions(date_time, latitude, longitude)
            
            # Calculate VRS score
            vrs_analysis = self.calculate_vrs_score(planetary_data)
            
            return {
                'prediction_time': date_time.isoformat(),
                'location': {'latitude': latitude, 'longitude': longitude},
                'planetary_positions': planetary_data,
                'vrs_analysis': vrs_analysis,
                'summary': f"Cyclone Risk: {vrs_analysis['risk_level']} (VRS: {vrs_analysis['vrs_score']:.1f}/100)",
                'system_status': 'operational'
            }
            
        except Exception as e:
            print(f"Error in cyclone prediction: {e}")
            return {
                'prediction_time': date_time.isoformat(),
                'location': {'latitude': latitude, 'longitude': longitude},
                'vrs_analysis': {
                    'vrs_score': 25,  # Default moderate score
                    'risk_level': 'MODERATE',
                    'risk_factors': ['System calculation error - using default values'],
                    'analysis': f'Error in calculation: {str(e)}. Using default moderate risk assessment.',
                    'calculation_method': 'error_fallback'
                },
                'summary': 'Moderate Cyclone Risk (Error Fallback)',
                'system_status': 'error',
                'error': str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    print("🔮 Testing Enhanced Vedic Astrology Module")
    print("=" * 60)
    
    # Test the enhanced astrology module
    analyzer = VedicAstrologyAnalyzer()
    
    # Test with various dates and locations
    test_cases = [
        (datetime.datetime(2024, 8, 15, 12, 0, 0), 19.0760, 72.8777, "Mumbai"),
        (datetime.datetime(2024, 6, 20, 10, 30, 0), 13.0827, 80.2707, "Chennai"),
        (datetime.datetime(2024, 9, 10, 15, 45, 0), 22.5726, 88.3639, "Kolkata")
    ]
    
    for date_time, lat, lon, location_name in test_cases:
        print(f"\
🌍 Testing: {location_name} - {date_time.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 50)
        
        try:
            result = analyzer.get_cyclone_prediction(date_time, lat, lon)
            
            print(f"📊 Prediction: {result['summary']}")
            print(f"🎯 Risk Level: {result['vrs_analysis']['risk_level']}")
            print(f"📈 VRS Score: {result['vrs_analysis']['vrs_score']:.1f}/100")
            print(f"🔍 Risk Factors: {len(result['vrs_analysis']['risk_factors'])}")
            print(f"⚙️  Method: {result['vrs_analysis'].get('calculation_method', 'unknown')}")
            
            if result['vrs_analysis']['risk_factors']:
                print("📋 Key Risk Factors:")
                for factor in result['vrs_analysis']['risk_factors'][:3]:  # Show top 3
                    print(f"  • {factor}")
            
            print(f"📝 Analysis: {result['vrs_analysis']['analysis'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
    
    print(f"\
✅ Enhanced Vedic Astrology Module testing completed")
    print(f"🔧 Swiss Ephemeris Available: {SWISS_EPHEMERIS_AVAILABLE}")