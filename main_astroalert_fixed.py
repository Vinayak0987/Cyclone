"""
AstroAlert - Main Application (Fixed Version)
Cyclone Prediction and Risk Assessment using AI and Astrology
Combines YOLOv5 cyclone detection with Vedic Astrology Risk Score (VRS)
"""

import os
import sys
import cv2
import numpy as np
import datetime
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from astrology_module_clean import VedicAstrologyAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure astrology_module_clean.py is available")
    sys.exit(1)

class AstroAlert:
    def __init__(self, model_path: str = "yolov5/runs/train/cyclone_detector52/weights/best.pt"):
        """
        Initialize AstroAlert system
        
        Args:
            model_path: Path to trained YOLOv5 model weights
        """
        self.model_path = model_path
        self.astrology_analyzer = VedicAstrologyAnalyzer()
        
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"Warning: Model not found at {model_path}")
            print("Please train the model first or provide correct path")
        
        print("AstroAlert - Cyclone Prediction System Initialized")
        print("=" * 60)

    def detect_cyclones(self, image_path: str, conf_threshold: float = 0.01) -> Dict:
        """
        Detect cyclones in satellite image using YOLOv5
        
        Args:
            image_path: Path to satellite image
            conf_threshold: Confidence threshold for detection
            
        Returns:
            Dictionary with detection results
        """
        print(f"Detecting cyclones in: {image_path}")
        
        try:
            # Run YOLOv5 detection using subprocess
            cmd = [
                'python', 'yolov5/detect.py',
                '--weights', self.model_path,
                '--source', image_path,
                '--conf', str(conf_threshold),
                '--save-txt',
                '--save-conf',
                '--project', 'runs/detect',
                '--name', 'astroalert_detection'
            ]
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            # Parse results from saved files
            detection_results = {
                'image_path': image_path,
                'detections': [],
                'total_cyclones': 0,
                'confidence_scores': [],
                'detection_time': datetime.datetime.now().isoformat()
            }
            
            # Check if detection files were created
            labels_dir = f"runs/detect/astroalert_detection/labels"
            if os.path.exists(labels_dir):
                # Count detections from label files
                for file in os.listdir(labels_dir):
                    if file.endswith('.txt'):
                        with open(os.path.join(labels_dir, file), 'r') as f:
                            lines = f.readlines()
                            for line in lines:
                                parts = line.strip().split()
                                if len(parts) >= 5:
                                    class_id, x_center, y_center, width, height = parts[:5]
                                    confidence = float(parts[5]) if len(parts) > 5 else 0.5
                                    
                                    detection_results['detections'].append({
                                        'bbox': [float(x_center), float(y_center), float(width), float(height)],
                                        'confidence': confidence,
                                        'class': int(class_id)
                                    })
                                    detection_results['confidence_scores'].append(confidence)
                
                detection_results['total_cyclones'] = len(detection_results['detections'])
                
                if detection_results['total_cyclones'] > 0:
                    detection_results['avg_confidence'] = np.mean(detection_results['confidence_scores'])
                    detection_results['max_confidence'] = np.max(detection_results['confidence_scores'])
                else:
                    detection_results['avg_confidence'] = 0
                    detection_results['max_confidence'] = 0
            
            print(f"Detected {detection_results['total_cyclones']} cyclones")
            return detection_results
            
        except Exception as e:
            print(f"Error during cyclone detection: {e}")
            return {
                'image_path': image_path,
                'error': str(e),
                'detections': [],
                'total_cyclones': 0
            }

    def calculate_astrology_risk(self, date_time: datetime.datetime, latitude: float, longitude: float) -> Dict:
        """
        Calculate Vedic Astrology Risk Score (VRS) for cyclone prediction
        
        Args:
            date_time: Date and time for prediction
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dictionary with VRS analysis
        """
        print(f"Calculating Vedic Astrology Risk Score...")
        print(f"Location: {latitude:.4f}, {longitude:.4f}")
        print(f"Time: {date_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            result = self.astrology_analyzer.get_cyclone_prediction(date_time, latitude, longitude)
            print(f"VRS Score: {result['vrs_analysis']['vrs_score']:.1f}/100")
            print(f"Risk Level: {result['vrs_analysis']['risk_level']}")
            return result
        except Exception as e:
            print(f"Error during astrology calculation: {e}")
            return {
                'error': str(e),
                'vrs_analysis': {
                    'vrs_score': 0,
                    'risk_level': 'UNKNOWN',
                    'risk_factors': [],
                    'analysis': 'Error in calculation'
                }
            }

    def generate_combined_risk_assessment(self, detection_results: Dict, astrology_results: Dict) -> Dict:
        """
        Generate combined risk assessment combining AI detection and astrology
        
        Args:
            detection_results: YOLOv5 detection results
            astrology_results: Vedic astrology analysis results
            
        Returns:
            Combined risk assessment
        """
        print("Generating combined risk assessment...")
        
        # Base risk from AI detection
        ai_risk = 0
        if detection_results.get('total_cyclones', 0) > 0:
            avg_conf = detection_results.get('avg_confidence', 0)
            if avg_conf > 0.8:
                ai_risk = 30
            elif avg_conf > 0.5:
                ai_risk = 20
            elif avg_conf > 0.2:
                ai_risk = 10
        
        # Astrology risk
        astrology_risk = astrology_results.get('vrs_analysis', {}).get('vrs_score', 0)
        
        # Combined risk calculation
        combined_risk = min(100, (ai_risk + astrology_risk) / 2)
        
        # Determine final risk level
        if combined_risk >= 70:
            final_risk_level = "EXTREME"
            action_required = "Immediate evacuation and emergency response required"
        elif combined_risk >= 50:
            final_risk_level = "HIGH"
            action_required = "High alert - prepare for severe weather conditions"
        elif combined_risk >= 30:
            final_risk_level = "MODERATE"
            action_required = "Moderate risk - maintain preparedness and monitor conditions"
        else:
            final_risk_level = "LOW"
            action_required = "Low risk - standard monitoring recommended"
        
        combined_assessment = {
            'timestamp': datetime.datetime.now().isoformat(),
            'ai_detection': {
                'cyclones_detected': detection_results.get('total_cyclones', 0),
                'average_confidence': detection_results.get('avg_confidence', 0),
                'ai_risk_score': ai_risk
            },
            'astrology_analysis': {
                'vrs_score': astrology_risk,
                'risk_level': astrology_results.get('vrs_analysis', {}).get('risk_level', 'UNKNOWN'),
                'risk_factors': astrology_results.get('vrs_analysis', {}).get('risk_factors', [])
            },
            'combined_assessment': {
                'combined_risk_score': combined_risk,
                'final_risk_level': final_risk_level,
                'action_required': action_required,
                'confidence': 'High' if detection_results.get('total_cyclones', 0) > 0 else 'Medium'
            },
            'recommendations': self._generate_recommendations(combined_risk, final_risk_level)
        }
        
        print(f"Combined Risk Assessment Complete!")
        print(f"Final Risk Level: {final_risk_level}")
        print(f"Combined Risk Score: {combined_risk:.1f}/100")
        print(f"Action Required: {action_required}")
        
        return combined_assessment

    def _generate_recommendations(self, risk_score: float, risk_level: str) -> List[str]:
        """Generate specific recommendations based on risk level"""
        recommendations = []
        
        if risk_level == "EXTREME":
            recommendations.extend([
                "🚨 IMMEDIATE EVACUATION of coastal areas",
                "🆘 Activate emergency response protocols",
                "📡 Issue highest level weather warnings",
                "🏥 Prepare emergency medical facilities",
                "🚁 Deploy rescue and relief teams"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "⚠️ Issue high-level weather alerts",
                "🏠 Prepare evacuation plans",
                "📻 Activate emergency communication systems",
                "🚒 Pre-position emergency response teams",
                "🏥 Alert medical facilities"
            ])
        elif risk_level == "MODERATE":
            recommendations.extend([
                "📢 Issue weather advisories",
                "🏠 Review evacuation procedures",
                "📡 Monitor weather conditions closely",
                "🚒 Prepare emergency response teams",
                "📱 Keep public informed of developments"
            ])
        else:
            recommendations.extend([
                "📊 Continue standard weather monitoring",
                "📱 Maintain public awareness programs",
                "🏠 Regular preparedness reviews",
                "📡 Monitor satellite imagery",
                "📋 Document conditions for future reference"
            ])
        
        return recommendations

    def run_complete_analysis(self, image_path: str, latitude: float, longitude: float, 
                             date_time: Optional[datetime.datetime] = None) -> Dict:
        """
        Run complete AstroAlert analysis
        
        Args:
            image_path: Path to satellite image
            latitude: Location latitude
            longitude: Location longitude
            date_time: Date and time (defaults to current time)
            
        Returns:
            Complete analysis results
        """
        if date_time is None:
            date_time = datetime.datetime.now()
        
        print("Starting Complete AstroAlert Analysis")
        print("=" * 60)
        
        # Step 1: AI Cyclone Detection
        detection_results = self.detect_cyclones(image_path)
        
        # Step 2: Astrology Risk Assessment
        astrology_results = self.calculate_astrology_risk(date_time, latitude, longitude)
        
        # Step 3: Combined Risk Assessment
        combined_assessment = self.generate_combined_risk_assessment(detection_results, astrology_results)
        
        # Step 4: Generate Final Report
        final_report = {
            'analysis_id': f"astroalert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'analysis_timestamp': datetime.datetime.now().isoformat(),
            'input_data': {
                'image_path': image_path,
                'location': {'latitude': latitude, 'longitude': longitude},
                'date_time': date_time.isoformat()
            },
            'results': {
                'detection': detection_results,
                'astrology': astrology_results,
                'combined': combined_assessment
            }
        }
        
        # Save results
        self._save_results(final_report)
        
        print("\nAstroAlert Analysis Complete!")
        print("=" * 60)
        print(f"Results saved to: results/astroalert_report.json")
        
        return final_report

    def _save_results(self, results: Dict):
        """Save analysis results to file"""
        os.makedirs('results', exist_ok=True)
        
        output_file = f"results/astroalert_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Also save latest report
        with open('results/astroalert_report.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

def main():
    """Main function for testing and demonstration"""
    print("AstroAlert - Cyclone Prediction System (Fixed Version)")
    print("=" * 60)
    
    # Initialize AstroAlert
    astroalert = AstroAlert()
    
    # Example usage
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        latitude = float(sys.argv[2]) if len(sys.argv) > 2 else 19.0760  # Mumbai
        longitude = float(sys.argv[3]) if len(sys.argv) > 3 else 72.8777  # Mumbai
        
        print(f"Analyzing image: {image_path}")
        print(f"Location: {latitude}, {longitude}")
        
        # Run complete analysis
        results = astroalert.run_complete_analysis(image_path, latitude, longitude)
        
        # Display summary
        print("\nANALYSIS SUMMARY")
        print("-" * 30)
        print(f"Cyclones Detected: {results['results']['detection']['total_cyclones']}")
        
        # Safely access VRS score
        try:
            vrs_score = results['results']['astrology'].get('vrs_analysis', {}).get('vrs_score', 0)
            print(f"VRS Score: {vrs_score:.1f}/100")
        except:
            print("VRS Score: Not available")
        
        try:
            combined_risk = results['results']['combined']['combined_risk_score']
            final_risk = results['results']['combined']['final_risk_level']
            print(f"Combined Risk: {combined_risk:.1f}/100")
            print(f"Final Risk Level: {final_risk}")
        except:
            print("Combined Risk: Not available")
        
    else:
        print("Usage: python main_astroalert_fixed.py <image_path> [latitude] [longitude]")
        print("Example: python main_astroalert_fixed.py data/train/images/1.jpg 19.0760 72.8777")
        
        # Test with sample data
        print("\n🧪 Running test analysis...")
        test_image = "data/train/images/1.jpg"
        if os.path.exists(test_image):
            results = astroalert.run_complete_analysis(test_image, 19.0760, 72.8777)
        else:
            print(f"Test image not found: {test_image}")

if __name__ == "__main__":
    main()
