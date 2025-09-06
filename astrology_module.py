"""
AstroAlert - Vedic Astrology Risk Assessment Module
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
            'Rahu': swe.MEAN_NODE,  # North Node
            'Ketu': None  # South Node (calculated from Rahu)
        }
        
        # Nakshatra boundaries (27 nakshatras, each 13°20')
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
            "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        # Tithi boundaries (15 tithis in waxing and waning phases)
        self.tithis = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
        ]

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
            if planet_id is not None:
                try:
                    # Get planetary position
                    result = swe.calc_ut(jd, planet_id)
                    planet_longitude = result[0]  # Ecliptic longitude
                    
                    # Calculate nakshatra
                    nakshatra = self._get_nakshatra(planet_longitude)
                    
                    # Calculate house position (Vedic houses)
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
            'location': {'latitude': latitude, 'longitude': longitude}
        }

    def calculate_vrs_score(self, planetary_data: Dict) -> Dict:
        """
        Calculate Vedic Astrology Risk Score (VRS) for cyclone prediction
        
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
        if planets['Sun'] and planets['Moon']:
            sun_long = planets['Sun']['longitude']
            moon_long = planets['Moon']['longitude']
            angle = abs(sun_long - moon_long)
            if angle <= 10 or (angle >= 170 and angle <= 190):
                vrs_score += 20
                risk_factors.append(f"Sun-Moon critical angle: {angle:.1f}° (+20)")
        
        # Factor 3: Saturn in critical houses (4th, 8th, 12th)
        if planets['Saturn']:
            house = planets['Saturn']['house']
            if house in [4, 8, 12]:
                vrs_score += 18
                risk_factors.append(f"Saturn in critical house {house} (+18)")
        
        # Factor 4: Rahu-Ketu axis in water signs
        if planets['Rahu'] and planets['Ketu']:
            rahu_sign = planets['Rahu']['sign']
            ketu_sign = planets['Ketu']['sign']
            if rahu_sign in water_signs or ketu_sign in water_signs:
                vrs_score += 12
                risk_factors.append(f"Rahu-Ketu axis in water signs (+12)")
        
        # Factor 5: Mars-Saturn conjunction or opposition
        if planets['Mars'] and planets['Saturn']:
            mars_long = planets['Mars']['longitude']
            saturn_long = planets['Saturn']['longitude']
            angle = abs(mars_long - saturn_long)
            if angle <= 8 or (angle >= 172 and angle <= 188):
                vrs_score += 25
                risk_factors.append(f"Mars-Saturn critical angle: {angle:.1f}° (+25)")
        
        # Factor 6: Critical nakshatras (water-related)
        water_nakshatras = ['Rohini', 'Ardra', 'Pushya', 'Ashlesha', 'Purva Ashadha', 'Uttara Ashadha']
        for planet_name, planet_data in planets.items():
            if planet_data and planet_data['nakshatra'] in water_nakshatras:
                vrs_score += 8
                risk_factors.append(f"{planet_name} in water nakshatra {planet_data['nakshatra']} (+8)")
        
        # Factor 7: Tithi analysis (critical lunar phases)
        tithi = planetary_data['tithi']
        critical_tithis = ['Chaturdashi', 'Purnima/Amavasya', 'Ashtami']
        if tithi in critical_tithis:
            vrs_score += 10
            risk_factors.append(f"Critical tithi: {tithi} (+10)")
        
        # Factor 8: Ascendant in water signs
        ascendant_sign = self._get_zodiac_sign(planetary_data['ascendant'])
        if ascendant_sign in water_signs:
            vrs_score += 12
            risk_factors.append(f"Ascendant in water sign {ascendant_sign} (+12)")
        
        # Normalize VRS score to 0-100 range
        vrs_score = min(100, vrs_score)
        
        # Determine risk level
        if vrs_score >= 70:
            risk_level = "HIGH"
        elif vrs_score >= 40:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        return {
            'vrs_score': vrs_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'total_factors': len(risk_factors),
            'analysis': self._get_risk_analysis(vrs_score, risk_level)
        }

    def _get_zodiac_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_index = int(longitude / 30)
        return signs[sign_index]
    
    def _get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra from longitude"""
        nakshatras = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
                     'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
                     'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
                     'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana',
                     'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']
        nakshatra_index = int(longitude / 13.333333)
        return nakshatras[nakshatra_index]
    
    def _get_house(self, longitude: float) -> int:
        """Get house number from longitude (1-12)"""
        house_num = int(longitude / 30) + 1
        return house_num if house_num <= 12 else house_num - 12

    def _calculate_tithi(self, sun_long: float, moon_long: float) -> str:
        """Calculate tithi (lunar phase)"""
        angle = (moon_long - sun_long) % 360
        tithi_index = int(angle / 12)
        return self.tithis[tithi_index]

    def _calculate_vedic_house(self, longitude: float, latitude: float, asc_long: float) -> int:
        """Calculate Vedic house position (simplified)"""
        # Simplified house calculation
        house_angle = (longitude - asc_long) % 360
        house_number = int(house_angle / 30) + 1
        return house_number if house_number <= 12 else house_number - 12

    def _calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> float:
        """Calculate ascendant (Lagna)"""
        try:
            # Get sidereal time
            st = swe.sidtime(jd)
            
            # Calculate ascendant
            result = swe.house_pos(st, latitude, longitude, b'P')
            return result[0]  # Ascendant longitude
        except:
            # Fallback calculation
            return (st * 15 + longitude) % 360

    def _get_risk_analysis(self, vrs_score: float, risk_level: str) -> str:
        """Get detailed risk analysis based on VRS score"""
        if risk_level == "HIGH":
            return f"High cyclone risk detected (VRS: {vrs_score:.1f}/100). Multiple malefic planetary combinations suggest increased probability of severe weather conditions. Immediate attention required for disaster preparedness."
        elif risk_level == "MODERATE":
            return f"Moderate cyclone risk detected (VRS: {vrs_score:.1f}/100). Some concerning planetary alignments present. Monitor weather conditions and maintain preparedness."
        else:
            return f"Low cyclone risk detected (VRS: {vrs_score:.1f}/100). Planetary positions are generally favorable. Standard weather monitoring recommended."

    def get_cyclone_prediction(self, date_time: datetime.datetime, latitude: float, longitude: float) -> Dict:
        """
        Complete cyclone prediction using Vedic astrology
        
        Args:
            date_time: Date and time for prediction
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Complete prediction with VRS score and analysis
        """
        # Calculate planetary positions
        planetary_data = self.calculate_planetary_positions(date_time, latitude, longitude)
        
        # Calculate VRS score
        vrs_analysis = self.calculate_vrs_score(planetary_data)
        
        return {
            'prediction_time': date_time.isoformat(),
            'location': {'latitude': latitude, 'longitude': longitude},
            'planetary_positions': planetary_data,
            'vrs_analysis': vrs_analysis,
            'summary': f"Cyclone Risk: {vrs_analysis['risk_level']} (VRS: {vrs_analysis['vrs_score']:.1f}/100)"
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the astrology module
    analyzer = VedicAstrologyAnalyzer()
    
    # Test with a sample date and location (Mumbai coordinates)
    test_date = datetime.datetime(2024, 8, 15, 12, 0, 0)  # August 15, 2024, 12 PM
    test_lat = 19.0760  # Mumbai latitude
    test_lon = 72.8777  # Mumbai longitude
    
    print("Testing Vedic Astrology Module...")
    print("=" * 50)
    
    try:
        result = analyzer.get_cyclone_prediction(test_date, test_lat, test_lon)
        print(f"Prediction: {result['summary']}")
        print(f"Risk Level: {result['vrs_analysis']['risk_level']}")
        print(f"VRS Score: {result['vrs_analysis']['vrs_score']:.1f}/100")
        print(f"Risk Factors: {len(result['vrs_analysis']['risk_factors'])}")
        print("\nDetailed Analysis:")
        for factor in result['vrs_analysis']['risk_factors']:
            print(f"  • {factor}")
        print(f"\nAnalysis: {result['vrs_analysis']['analysis']}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Please check if Swiss Ephemeris files are available in the 'ephe' directory.")
