#!/usr/bin/env python3
"""
Enhanced AstroAlert - Integration of YOLOv5 with Advanced Meteorological Analysis
Combines cyclone detection with detailed intensity and eye analysis
"""

import os
import sys
import datetime
import json
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

try:
    from .yolo_enhanced_analyzer import YOLOEnhancedAnalyzer
    print("✅ Enhanced analyzer loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import enhanced analyzer: {e}")
    sys.exit(1)

# Import the original AstroAlert
try:
    from main_astroalert_fixed import AstroAlert
    print("✅ Original AstroAlert loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import original AstroAlert: {e}")
    sys.exit(1)


class EnhancedAstroAlert(AstroAlert):
    """Enhanced AstroAlert with advanced meteorological analysis"""
    
    def __init__(self, model_path: str = "yolov5/runs/train/cyclone_detector_improved/weights/best.pt"):
        """
        Initialize Enhanced AstroAlert system
        
        Args:
            model_path: Path to trained YOLOv5 model weights
        """
        # Initialize the parent AstroAlert class
        super().__init__(model_path)
        
        # Initialize the enhanced analyzer
        try:
            self.enhanced_analyzer = YOLOEnhancedAnalyzer()
            print("✅ Enhanced meteorological analyzer initialized")
        except Exception as e:
            print(f"⚠️ Warning: Enhanced analyzer initialization failed: {e}")
            print("💡 Some advanced features may not be available")
            self.enhanced_analyzer = None
        
        print("Enhanced AstroAlert - Advanced Cyclone Analysis System Initialized")
        print("=" * 70)
    
    def run_enhanced_complete_analysis(self, image_path: str, latitude: float, longitude: float, 
                                     date_time: datetime.datetime = None) -> dict:
        """
        Run complete enhanced analysis combining YOLO, meteorological analysis, and astrology
        
        Args:
            image_path: Path to satellite image
            latitude: Location latitude
            longitude: Location longitude
            date_time: Date and time (defaults to current time)
            
        Returns:
            Complete enhanced analysis results
        """
        if date_time is None:
            date_time = datetime.datetime.now()
        
        print("Starting Enhanced AstroAlert Analysis")
        print("=" * 70)
        
        # Step 1: Run original YOLO detection
        print("🎯 Step 1: YOLOv5 Cyclone Detection")
        detection_results = self.detect_cyclones(image_path)
        
        # Step 2: Enhanced meteorological analysis
        enhanced_meteorological = None
        if self.enhanced_analyzer:
            print("🌀 Step 2: Enhanced Meteorological Analysis")
            try:
                enhanced_meteorological = self.enhanced_analyzer.analyze_yolo_detection(
                    image_path, detection_results
                )
                print("✅ Enhanced meteorological analysis completed")
            except Exception as e:
                print(f"⚠️ Enhanced meteorological analysis failed: {e}")
                enhanced_meteorological = {'error': str(e)}
        else:
            print("⚠️ Step 2: Enhanced meteorological analysis skipped (not available)")
        
        # Step 3: Astrology Risk Assessment
        print("🔮 Step 3: Vedic Astrology Risk Assessment")
        astrology_results = self.calculate_astrology_risk(date_time, latitude, longitude)
        
        # Step 4: Enhanced Combined Risk Assessment
        print("⚖️ Step 4: Enhanced Combined Risk Assessment")
        combined_assessment = self.generate_enhanced_combined_assessment(
            detection_results, enhanced_meteorological, astrology_results
        )
        
        # Step 5: Generate Enhanced Final Report
        print("📊 Step 5: Generating Enhanced Report")
        final_report = {
            'analysis_id': f"enhanced_astroalert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'analysis_timestamp': datetime.datetime.now().isoformat(),
            'analysis_type': 'enhanced_astroalert',
            'input_data': {
                'image_path': image_path,
                'location': {'latitude': latitude, 'longitude': longitude},
                'date_time': date_time.isoformat()
            },
            'results': {
                'yolo_detection': detection_results,
                'enhanced_meteorological': enhanced_meteorological,
                'astrology': astrology_results,
                'combined_enhanced': combined_assessment
            },
            'model_performance': self._get_enhanced_model_performance()
        }
        
        # Save enhanced results
        self._save_enhanced_results(final_report)
        
        print("\n🎉 Enhanced AstroAlert Analysis Complete!")
        print("=" * 70)
        print(f"Results saved to: results/enhanced_astroalert_report.json")
        
        return final_report
    
    def generate_enhanced_combined_assessment(self, detection_results: dict, 
                                            enhanced_meteorological: dict, 
                                            astrology_results: dict) -> dict:
        """
        Generate enhanced combined risk assessment
        
        Args:
            detection_results: YOLOv5 detection results
            enhanced_meteorological: Enhanced meteorological analysis
            astrology_results: Vedic astrology analysis results
            
        Returns:
            Enhanced combined risk assessment
        """
        print("Generating enhanced combined risk assessment...")
        
        # Get base AI risk from YOLO detection
        ai_risk = self._calculate_base_ai_risk(detection_results)
        
        # Enhanced meteorological risk analysis
        meteorological_risk = 0
        meteorological_insights = {}
        
        if enhanced_meteorological and 'error' not in enhanced_meteorological:
            meteorological_analysis = self._analyze_meteorological_risk(enhanced_meteorological)
            meteorological_risk = meteorological_analysis['risk_score']
            meteorological_insights = meteorological_analysis['insights']
        
        # Astrology risk
        astrology_risk = astrology_results.get('vrs_analysis', {}).get('vrs_score', 0)
        
        # Enhanced combined risk calculation
        # Weight: YOLO (35%), Enhanced Meteorological (40%), Astrology (25%)
        if enhanced_meteorological and 'error' not in enhanced_meteorological:
            combined_risk = min(100, (ai_risk * 0.35 + meteorological_risk * 0.40 + astrology_risk * 0.25))
            analysis_confidence = 'High'
        else:
            # Fallback to original calculation if enhanced analysis not available
            combined_risk = min(100, (ai_risk + astrology_risk) / 2)
            analysis_confidence = 'Medium'
        
        # Determine enhanced risk level
        risk_level_info = self._determine_enhanced_risk_level(combined_risk, meteorological_insights)
        
        enhanced_assessment = {
            'timestamp': datetime.datetime.now().isoformat(),
            'analysis_components': {
                'yolo_detection': {
                    'cyclones_detected': detection_results.get('total_cyclones', 0),
                    'average_confidence': detection_results.get('avg_confidence', 0),
                    'detection_quality': detection_results.get('detection_quality', 'Unknown'),
                    'ai_risk_score': ai_risk
                },
                'enhanced_meteorological': meteorological_insights,
                'astrology_analysis': {
                    'vrs_score': astrology_risk,
                    'risk_level': astrology_results.get('vrs_analysis', {}).get('risk_level', 'UNKNOWN'),
                    'risk_factors': astrology_results.get('vrs_analysis', {}).get('risk_factors', [])
                }
            },
            'enhanced_combined_assessment': {
                'combined_risk_score': combined_risk,
                'final_risk_level': risk_level_info['level'],
                'threat_category': risk_level_info['category'],
                'confidence': analysis_confidence,
                'key_findings': risk_level_info['key_findings'],
                'action_required': risk_level_info['action_required']
            },
            'enhanced_recommendations': self._generate_enhanced_recommendations(
                combined_risk, risk_level_info, meteorological_insights
            )
        }
        
        print(f"Enhanced Combined Risk Assessment Complete!")
        print(f"Final Risk Level: {risk_level_info['level']}")
        print(f"Combined Risk Score: {combined_risk:.1f}/100")
        print(f"Threat Category: {risk_level_info['category']}")
        
        return enhanced_assessment
    
    def _calculate_base_ai_risk(self, detection_results: dict) -> float:
        """Calculate base AI risk from YOLO detection results"""
        total_cyclones = detection_results.get('total_cyclones', 0)
        if total_cyclones == 0:
            return 0
        
        detection_quality = detection_results.get('detection_quality', 'NO_DETECTION')
        
        # Enhanced quality-based risk scoring
        quality_scores = {
            'EXCELLENT': 50,
            'GOOD': 40,
            'MODERATE': 30,
            'FAIR': 22,
            'WEAK_MULTIPLE': 15,
            'WEAK_MANY': 10,
            'POOR': 5
        }
        
        return quality_scores.get(detection_quality, 0)
    
    def _analyze_meteorological_risk(self, enhanced_meteorological: dict) -> dict:
        """Analyze risk from enhanced meteorological data"""
        risk_analysis = {
            'risk_score': 0,
            'insights': {
                'meteorological_risk_score': 0,
                'intensity_analysis': {},
                'eye_analysis': {},
                'structural_assessment': {},
                'threat_indicators': []
            }
        }
        
        try:
            overall_assessment = enhanced_meteorological.get('overall_assessment', {})
            enhanced_analysis = enhanced_meteorological.get('enhanced_analysis', [])
            
            # Analyze intensity predictions
            max_intensity = 0
            intensity_confidences = []
            for analysis in enhanced_analysis:
                if analysis.get('intensity_prediction'):
                    intensity = analysis['intensity_prediction'].get('prediction', 0)
                    confidence = analysis['intensity_prediction'].get('confidence', 0)
                    max_intensity = max(max_intensity, intensity)
                    intensity_confidences.append(confidence)
            
            # Calculate intensity risk
            intensity_risk = 0
            if max_intensity >= 5:
                intensity_risk = 45
            elif max_intensity >= 4:
                intensity_risk = 35
            elif max_intensity >= 3:
                intensity_risk = 25
            elif max_intensity >= 2:
                intensity_risk = 15
            elif max_intensity >= 1:
                intensity_risk = 5
            
            risk_analysis['insights']['intensity_analysis'] = {
                'max_intensity_category': max_intensity,
                'avg_ml_confidence': sum(intensity_confidences) / len(intensity_confidences) if intensity_confidences else 0,
                'intensity_risk_contribution': intensity_risk
            }
            
            # Analyze eye detections
            eyes_detected = overall_assessment.get('eye_analysis_summary', {}).get('total_eyes_detected', 0)
            if eyes_detected > 0:
                eye_risk = 15  # Eye presence indicates mature system
                risk_analysis['insights']['threat_indicators'].append('Eye wall structure detected')
            else:
                eye_risk = 0
            
            risk_analysis['insights']['eye_analysis'] = {
                'eyes_detected': eyes_detected,
                'eye_risk_contribution': eye_risk
            }
            
            # Overall structural assessment
            overall_risk_level = overall_assessment.get('overall_risk_level', 'Low')
            structural_risk = {
                'High': 20,
                'Moderate': 15,
                'Low to Moderate': 10,
                'Low': 5
            }.get(overall_risk_level, 0)
            
            risk_analysis['insights']['structural_assessment'] = {
                'overall_risk_level': overall_risk_level,
                'structural_risk_contribution': structural_risk
            }
            
            # Calculate total meteorological risk
            total_meteorological_risk = min(100, intensity_risk + eye_risk + structural_risk)
            risk_analysis['risk_score'] = total_meteorological_risk
            risk_analysis['insights']['meteorological_risk_score'] = total_meteorological_risk
            
        except Exception as e:
            print(f"⚠️ Error analyzing meteorological risk: {e}")
            risk_analysis['insights']['error'] = str(e)
        
        return risk_analysis
    
    def _determine_enhanced_risk_level(self, combined_risk: float, meteorological_insights: dict) -> dict:
        """Determine enhanced risk level with additional threat categorization"""
        
        # Enhanced risk level determination
        if combined_risk >= 75:
            level = "EXTREME"
            category = "CATASTROPHIC_THREAT"
            action_required = "IMMEDIATE EVACUATION - Life-threatening conditions expected"
        elif combined_risk >= 60:
            level = "VERY_HIGH"
            category = "MAJOR_THREAT"
            action_required = "Urgent evacuation preparations - Destructive conditions likely"
        elif combined_risk >= 45:
            level = "HIGH"
            category = "SIGNIFICANT_THREAT"
            action_required = "High alert - Prepare for severe weather conditions"
        elif combined_risk >= 30:
            level = "MODERATE"
            category = "MODERATE_THREAT"
            action_required = "Moderate risk - Enhanced monitoring and preparedness required"
        elif combined_risk >= 15:
            level = "LOW_TO_MODERATE"
            category = "MINOR_THREAT"
            action_required = "Low to moderate risk - Standard preparedness recommended"
        else:
            level = "LOW"
            category = "MINIMAL_THREAT"
            action_required = "Low risk - Continue standard monitoring"
        
        # Extract key findings from meteorological insights
        key_findings = []
        
        if meteorological_insights:
            intensity_analysis = meteorological_insights.get('intensity_analysis', {})
            max_intensity = intensity_analysis.get('max_intensity_category', 0)
            
            if max_intensity >= 3:
                key_findings.append(f"Major hurricane intensity detected (Category {max_intensity})")
            elif max_intensity >= 1:
                key_findings.append(f"Tropical cyclone intensity detected (Category {max_intensity})")
            
            eyes_detected = meteorological_insights.get('eye_analysis', {}).get('eyes_detected', 0)
            if eyes_detected > 0:
                key_findings.append("Well-defined eye wall structure present")
            
            threat_indicators = meteorological_insights.get('threat_indicators', [])
            key_findings.extend(threat_indicators)
        
        if not key_findings:
            key_findings = ["Analysis based on satellite imagery and astrological factors"]
        
        return {
            'level': level,
            'category': category,
            'action_required': action_required,
            'key_findings': key_findings
        }
    
    def _generate_enhanced_recommendations(self, risk_score: float, risk_level_info: dict, 
                                         meteorological_insights: dict) -> list:
        """Generate enhanced recommendations based on comprehensive analysis"""
        recommendations = []
        
        risk_level = risk_level_info['level']
        
        # Base recommendations by risk level
        if risk_level in ["EXTREME", "VERY_HIGH"]:
            recommendations.extend([
                "🚨 IMMEDIATE EVACUATION of all coastal and low-lying areas",
                "🆘 Activate maximum emergency response protocols",
                "📡 Issue EXTREME weather warnings to all media outlets",
                "🏥 Prepare emergency medical facilities for mass casualties",
                "🚁 Deploy all available rescue and relief teams",
                "⛑️ Establish emergency shelters in safe zones",
                "📱 Activate emergency communication systems"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "⚠️ Issue HIGH-LEVEL severe weather warnings",
                "🏠 Begin voluntary evacuations of vulnerable areas",
                "📻 Activate emergency broadcast systems",
                "🚒 Pre-position emergency response teams at strategic locations",
                "🏥 Alert all medical facilities and prepare for emergencies",
                "🌊 Monitor tide levels and storm surge forecasts closely"
            ])
        elif risk_level == "MODERATE":
            recommendations.extend([
                "📢 Issue weather advisories and public warnings",
                "🏠 Review and update evacuation procedures",
                "📡 Enhance weather monitoring and surveillance",
                "🚒 Prepare emergency response teams for deployment",
                "📱 Keep public informed with regular updates",
                "⛵ Advise mariners to seek safe harbor"
            ])
        else:
            recommendations.extend([
                "📊 Continue standard weather monitoring protocols",
                "📱 Maintain public awareness campaigns",
                "🏠 Conduct routine preparedness reviews",
                "📡 Regular analysis of satellite imagery",
                "📋 Document conditions for meteorological records"
            ])
        
        # Enhanced recommendations based on meteorological insights
        if meteorological_insights:
            intensity_analysis = meteorological_insights.get('intensity_analysis', {})
            max_intensity = intensity_analysis.get('max_intensity_category', 0)
            
            if max_intensity >= 4:
                recommendations.append("🌪️ Category 4+ Hurricane detected - Expect catastrophic damage")
            elif max_intensity >= 3:
                recommendations.append("🌀 Major hurricane intensity - Expect extensive damage")
            
            eyes_detected = meteorological_insights.get('eye_analysis', {}).get('eyes_detected', 0)
            if eyes_detected > 0:
                recommendations.append("👁️ Mature cyclone with eye wall - Intense winds expected")
        
        # Astrological timing recommendations
        current_hour = datetime.datetime.now().hour
        if 6 <= current_hour <= 18:
            recommendations.append("☀️ Daylight hours - Optimal time for preparations and evacuations")
        else:
            recommendations.append("🌙 Night hours - Exercise extra caution during preparations")
        
        return recommendations
    
    def _get_enhanced_model_performance(self) -> dict:
        """Get performance metrics for all models"""
        performance = {
            'yolo_detection': {
                'model_type': 'YOLOv5',
                'status': 'operational' if os.path.exists(self.model_path) else 'unavailable'
            },
            'enhanced_meteorological': None,
            'astrology_analysis': {
                'model_type': 'Vedic Astrology Risk Score (VRS)',
                'status': 'operational'
            }
        }
        
        if self.enhanced_analyzer:
            performance['enhanced_meteorological'] = self.enhanced_analyzer.get_model_performance()
        
        return performance
    
    def _save_enhanced_results(self, results: dict):
        """Save enhanced analysis results to file"""
        os.makedirs('results', exist_ok=True)
        
        # Save timestamped report
        output_file = f"results/enhanced_astroalert_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save latest report
        with open('results/enhanced_astroalert_report.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"✅ Enhanced results saved to: {output_file}")


def main():
    """Main function for testing and demonstration"""
    print("Enhanced AstroAlert - Advanced Cyclone Analysis System")
    print("=" * 70)
    
    # Initialize Enhanced AstroAlert
    try:
        enhanced_astroalert = EnhancedAstroAlert()
        
        # Test with sample data
        test_image = "data/test_images/sample_cyclone.jpg"  # Update with your test image
        test_latitude = 19.0760
        test_longitude = 72.8777
        test_datetime = datetime.datetime.now()
        
        print(f"\n🧪 Running test analysis...")
        print(f"Image: {test_image}")
        print(f"Location: {test_latitude}, {test_longitude}")
        print(f"Time: {test_datetime}")
        
        if os.path.exists(test_image):
            # Run enhanced analysis
            results = enhanced_astroalert.run_enhanced_complete_analysis(
                test_image, test_latitude, test_longitude, test_datetime
            )
            
            print("\n📊 Test Analysis Results:")
            print("-" * 50)
            
            combined = results['results']['combined_enhanced']['enhanced_combined_assessment']
            print(f"Risk Level: {combined['final_risk_level']}")
            print(f"Risk Score: {combined['combined_risk_score']:.1f}/100")
            print(f"Threat Category: {combined['threat_category']}")
            print(f"Action Required: {combined['action_required']}")
            
        else:
            print(f"⚠️ Test image not found: {test_image}")
            print("💡 Please update the test_image path with a valid cyclone satellite image")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
