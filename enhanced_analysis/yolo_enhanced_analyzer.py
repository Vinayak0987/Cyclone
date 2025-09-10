#!/usr/bin/env python3
"""
YOLOv5 Enhanced Analyzer
Integrates advanced cyclone image analysis with existing YOLOv5 detection
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
import cv2
from PIL import Image, ImageEnhance
import datetime
warnings.filterwarnings('ignore')

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

try:
    import joblib
    from sklearn.preprocessing import StandardScaler
    print("✅ Enhanced analysis dependencies loaded")
except ImportError as e:
    print(f"❌ Error loading enhanced analysis dependencies: {e}")
    print("💡 Install required packages: pip install scikit-learn joblib")

class YOLOEnhancedAnalyzer:
    """Enhanced analyzer that combines YOLOv5 detection with meteorological analysis"""
    
    def __init__(self, models_dir=None):
        """
        Initialize the enhanced analyzer
        
        Args:
            models_dir: Directory containing trained models (defaults to ./trained_models)
        """
        if models_dir is None:
            models_dir = current_dir / 'trained_models'
        
        self.models_dir = Path(models_dir)
        self.models = {}
        self.training_report = None
        
        # Initialize feature extractor
        self.feature_extractor = CycloneFeatureExtractor()
        
        # Load trained models
        self.load_models()
    
    def load_models(self):
        """Load all trained models for enhanced analysis"""
        self.models = {}
        
        try:
            # Load feature-based intensity classifier
            feature_model_path = self.models_dir / 'cyclone_feature_classifier.joblib'
            if feature_model_path.exists():
                try:
                    self.models['feature_classifier'] = joblib.load(feature_model_path)
                    print("✅ Loaded feature-based intensity classifier")
                except Exception as model_error:
                    print(f"⚠️ Feature classifier found but couldn't load due to sklearn compatibility: {model_error}")
                    print("💡 Continuing without ML-based intensity classification - using fallback methods")
            else:
                print("⚠️ Feature classifier not found - intensity analysis will be limited")
            
            # Load eye detection model
            eye_model_path = self.models_dir / 'cyclone_eye_detector.joblib'
            if eye_model_path.exists():
                try:
                    self.models['eye_detector'] = joblib.load(eye_model_path)
                    print("✅ Loaded eye detection model")
                except Exception as model_error:
                    print(f"⚠️ Eye detector found but couldn't load due to sklearn compatibility: {model_error}")
                    print("💡 Continuing without ML-based eye detection - using fallback methods")
            else:
                print("⚠️ Eye detector not found - eye analysis will be limited")
            
            # Load training report for metadata
            report_path = self.models_dir / 'real_image_training_report.json'
            if report_path.exists():
                with open(report_path, 'r') as f:
                    self.training_report = json.load(f)
                print("✅ Loaded training report")
            else:
                self.training_report = None
                
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            print("💡 Continuing with fallback analysis methods")
            self.models = {}
            self.training_report = None
    
    def analyze_yolo_detection(self, image_path, yolo_detections):
        """
        Enhance YOLO detections with meteorological analysis
        
        Args:
            image_path: Path to the analyzed image
            yolo_detections: YOLO detection results dictionary
            
        Returns:
            Enhanced analysis results combining YOLO + meteorological insights
        """
        print("🔍 Starting enhanced YOLO analysis...")
        
        # Load the image
        try:
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Could not load image from {image_path}")
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image_path  # Assume it's already a numpy array
                
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return self._create_error_result(str(e))
        
        enhanced_results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'image_path': str(image_path),
            'yolo_detections': yolo_detections,
            'enhanced_analysis': [],
            'global_features': {},
            'overall_assessment': {}
        }
        
        # Extract global image features (for the entire image)
        enhanced_results['global_features'] = self._extract_global_features(image_rgb)
        
        # Process each YOLO detection
        detections = yolo_detections.get('detections', [])
        if len(detections) == 0:
            print("ℹ️ No YOLO detections to enhance - analyzing full image")
            # Analyze the full image if no detections
            full_image_analysis = self._analyze_image_region(image_rgb, None, "full_image")
            enhanced_results['enhanced_analysis'].append(full_image_analysis)
        else:
            print(f"🎯 Enhancing {len(detections)} YOLO detections...")
            
            for i, detection in enumerate(detections):
                # Extract the detected cyclone region
                cyclone_region = self._extract_cyclone_region(image_rgb, detection)
                
                # Perform enhanced analysis on this region
                region_analysis = self._analyze_image_region(
                    cyclone_region, detection, f"detection_{i}"
                )
                
                enhanced_results['enhanced_analysis'].append(region_analysis)
        
        # Generate overall assessment
        enhanced_results['overall_assessment'] = self._generate_overall_assessment(
            enhanced_results
        )
        
        print("✅ Enhanced YOLO analysis complete!")
        return enhanced_results
    
    def _extract_cyclone_region(self, image_rgb, detection):
        """Extract the cyclone region from YOLO detection bbox"""
        bbox = detection['bbox']
        confidence = detection['confidence']
        
        # YOLO bbox format: [x_center, y_center, width, height] (normalized)
        h, w = image_rgb.shape[:2]
        
        x_center, y_center, width, height = bbox
        
        # Convert normalized coordinates to pixel coordinates
        x_center *= w
        y_center *= h
        width *= w
        height *= h
        
        # Calculate bounding box corners
        x1 = int(x_center - width/2)
        y1 = int(y_center - height/2)
        x2 = int(x_center + width/2)
        y2 = int(y_center + height/2)
        
        # Ensure coordinates are within image bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        
        # Extract the region
        cyclone_region = image_rgb[y1:y2, x1:x2]
        
        # Add padding if region is too small
        if cyclone_region.shape[0] < 50 or cyclone_region.shape[1] < 50:
            # Expand the region slightly
            padding = 20
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(w, x2 + padding)
            y2 = min(h, y2 + padding)
            cyclone_region = image_rgb[y1:y2, x1:x2]
        
        return cyclone_region
    
    def _analyze_image_region(self, image_region, detection, region_id):
        """Perform comprehensive analysis on a cyclone region"""
        analysis = {
            'region_id': region_id,
            'yolo_detection': detection,
            'region_shape': image_region.shape,
            'features': {},
            'intensity_prediction': None,
            'eye_detection': None,
            'meteorological_assessment': {}
        }
        
        try:
            # Extract comprehensive features
            features = self.feature_extractor.extract_comprehensive_features(
                image_region, region_id
            )
            analysis['features'] = features
            
            # Predict intensity if model is available
            if 'feature_classifier' in self.models:
                intensity_result = self._predict_intensity(features)
                analysis['intensity_prediction'] = intensity_result
            
            # Detect eye if model is available  
            if 'eye_detector' in self.models:
                eye_result = self._detect_eye(features)
                analysis['eye_detection'] = eye_result
            
            # Generate meteorological assessment
            analysis['meteorological_assessment'] = self._assess_meteorology(
                features, analysis.get('intensity_prediction'), analysis.get('eye_detection')
            )
            
        except Exception as e:
            print(f"⚠️ Error in region analysis: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _predict_intensity(self, features_dict):
        """Predict cyclone intensity from extracted features"""
        if 'feature_classifier' not in self.models:
            return None
            
        try:
            model_data = self.models['feature_classifier']
            feature_columns = model_data['feature_columns']
            
            # Create feature vector
            feature_values = []
            for col in feature_columns:
                feature_values.append(features_dict.get(col, 0))
            
            feature_vector = np.array(feature_values).reshape(1, -1)
            
            # Make prediction
            model = model_data['model']
            prediction = model.predict(feature_vector)[0]
            
            # Get prediction probabilities if available
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(feature_vector)[0]
                confidence = np.max(probabilities)
            else:
                confidence = 0.8
            
            # Map prediction to intensity category
            intensity_mapping = {
                1: "Tropical Depression",
                2: "Tropical Storm", 
                3: "Category 1 Hurricane",
                4: "Category 2 Hurricane",
                5: "Category 3+ Hurricane"
            }
            
            intensity_name = intensity_mapping.get(prediction, f"Category {prediction}")
            
            return {
                'prediction': int(prediction),
                'intensity_name': intensity_name,
                'confidence': float(confidence),
                'model_type': model_data.get('model_type', 'Unknown'),
                'performance': model_data.get('performance', {})
            }
            
        except Exception as e:
            print(f"❌ Intensity prediction error: {e}")
            return {'error': str(e)}
    
    def _detect_eye(self, features_dict):
        """Detect cyclone eye using trained model"""
        if 'eye_detector' not in self.models:
            return None
            
        try:
            model_data = self.models['eye_detector']
            feature_columns = model_data['feature_columns']
            
            # Create feature vector
            feature_values = []
            for col in feature_columns:
                feature_values.append(features_dict.get(col, 0))
            
            feature_vector = np.array(feature_values).reshape(1, -1)
            
            # Make prediction
            model = model_data['model']
            eye_detected = model.predict(feature_vector)[0]
            
            # Get confidence if available
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(feature_vector)[0]
                confidence = probabilities[1] if eye_detected else probabilities[0]
            else:
                confidence = 0.9 if eye_detected else 0.8
            
            return {
                'eye_detected': bool(eye_detected),
                'confidence': float(confidence),
                'eye_clarity': features_dict.get('eye_clarity', 0),
                'center_brightness': features_dict.get('center_brightness', 0),
                'symmetry_score': features_dict.get('overall_symmetry', 0),
                'performance': model_data.get('performance', {})
            }
            
        except Exception as e:
            print(f"❌ Eye detection error: {e}")
            return {'error': str(e)}
    
    def _extract_global_features(self, image_rgb):
        """Extract global features from the entire image"""
        try:
            return self.feature_extractor.extract_comprehensive_features(
                image_rgb, "global_image"
            )
        except Exception as e:
            print(f"⚠️ Error extracting global features: {e}")
            return {}
    
    def _assess_meteorology(self, features, intensity_pred, eye_detection):
        """Generate meteorological assessment from analysis results"""
        assessment = {
            'structural_organization': 'Unknown',
            'development_stage': 'Unknown',
            'threat_level': 'Unknown',
            'key_indicators': []
        }
        
        try:
            # Assess structural organization
            symmetry = features.get('overall_symmetry', 0)
            if symmetry > 0.7:
                assessment['structural_organization'] = 'Highly Organized'
            elif symmetry > 0.5:
                assessment['structural_organization'] = 'Well Organized'
            elif symmetry > 0.3:
                assessment['structural_organization'] = 'Moderately Organized'
            else:
                assessment['structural_organization'] = 'Poorly Organized'
            
            # Assess development stage
            if eye_detection and eye_detection.get('eye_detected'):
                if eye_detection.get('eye_clarity', 0) > 0.7:
                    assessment['development_stage'] = 'Mature Hurricane'
                else:
                    assessment['development_stage'] = 'Developing Hurricane'
                assessment['key_indicators'].append('Eye structure detected')
            elif features.get('spiral_patterns', 0) > 0.5:
                assessment['development_stage'] = 'Tropical Storm'
                assessment['key_indicators'].append('Spiral patterns visible')
            else:
                assessment['development_stage'] = 'Tropical Depression'
            
            # Assess threat level
            if intensity_pred:
                intensity_level = intensity_pred.get('prediction', 1)
                if intensity_level >= 4:
                    assessment['threat_level'] = 'Extreme'
                elif intensity_level >= 3:
                    assessment['threat_level'] = 'High'
                elif intensity_level >= 2:
                    assessment['threat_level'] = 'Moderate'
                else:
                    assessment['threat_level'] = 'Low'
                
                assessment['key_indicators'].append(
                    f"Intensity: {intensity_pred.get('intensity_name', 'Unknown')}"
                )
            
            # Add additional indicators
            if features.get('edge_density', 0) > 0.3:
                assessment['key_indicators'].append('High convective activity')
            
            if features.get('texture_variance', 0) > 1000:
                assessment['key_indicators'].append('Strong cloud organization')
                
        except Exception as e:
            print(f"⚠️ Error in meteorological assessment: {e}")
            assessment['error'] = str(e)
        
        return assessment
    
    def _generate_overall_assessment(self, enhanced_results):
        """Generate overall assessment from all analysis results"""
        assessment = {
            'timestamp': datetime.datetime.now().isoformat(),
            'detection_summary': {},
            'intensity_summary': {},
            'eye_analysis_summary': {},
            'overall_risk_level': 'Unknown',
            'recommendations': []
        }
        
        try:
            yolo_detections = enhanced_results.get('yolo_detections', {})
            enhanced_analysis = enhanced_results.get('enhanced_analysis', [])
            
            # Summarize detections
            total_detections = yolo_detections.get('total_cyclones', 0)
            avg_yolo_confidence = yolo_detections.get('avg_confidence', 0)
            max_yolo_confidence = yolo_detections.get('max_confidence', 0)
            
            assessment['detection_summary'] = {
                'total_cyclones': total_detections,
                'avg_yolo_confidence': avg_yolo_confidence,
                'max_yolo_confidence': max_yolo_confidence,
                'detection_quality': yolo_detections.get('detection_quality', 'Unknown')
            }
            
            # Analyze intensity predictions
            intensity_predictions = []
            for analysis in enhanced_analysis:
                if analysis.get('intensity_prediction'):
                    intensity_predictions.append(analysis['intensity_prediction'])
            
            if intensity_predictions:
                max_intensity = max(pred.get('prediction', 1) for pred in intensity_predictions)
                avg_confidence = np.mean([pred.get('confidence', 0) for pred in intensity_predictions])
                
                assessment['intensity_summary'] = {
                    'max_intensity_category': max_intensity,
                    'avg_ml_confidence': avg_confidence,
                    'total_predictions': len(intensity_predictions)
                }
            
            # Analyze eye detections
            eye_detections = []
            for analysis in enhanced_analysis:
                if analysis.get('eye_detection'):
                    eye_detections.append(analysis['eye_detection'])
            
            if eye_detections:
                eyes_detected = sum(1 for eye in eye_detections if eye.get('eye_detected'))
                assessment['eye_analysis_summary'] = {
                    'total_eyes_detected': eyes_detected,
                    'eye_detection_rate': eyes_detected / len(eye_detections) if eye_detections else 0
                }
            
            # Determine overall risk level
            risk_factors = []
            
            if total_detections > 0:
                risk_factors.append(f"{total_detections} cyclone(s) detected")
                
            if assessment.get('intensity_summary', {}).get('max_intensity_category', 0) >= 3:
                risk_factors.append("Major hurricane intensity detected")
                assessment['overall_risk_level'] = 'High'
            elif assessment.get('intensity_summary', {}).get('max_intensity_category', 0) >= 2:
                risk_factors.append("Hurricane intensity detected")
                assessment['overall_risk_level'] = 'Moderate'
            elif total_detections > 0:
                assessment['overall_risk_level'] = 'Low to Moderate'
            else:
                assessment['overall_risk_level'] = 'Low'
            
            if assessment.get('eye_analysis_summary', {}).get('total_eyes_detected', 0) > 0:
                risk_factors.append("Eye wall structure present")
            
            # Generate recommendations
            if assessment['overall_risk_level'] == 'High':
                assessment['recommendations'] = [
                    "🚨 High intensity cyclone detected - issue severe weather warnings",
                    "📡 Monitor closely with satellite and radar",
                    "🏠 Prepare evacuation plans for affected areas",
                    "🚒 Alert emergency response teams"
                ]
            elif assessment['overall_risk_level'] == 'Moderate':
                assessment['recommendations'] = [
                    "⚠️ Moderate cyclone activity detected - issue weather advisories",
                    "📊 Continue monitoring with enhanced surveillance",
                    "📱 Keep public informed of developments",
                    "🏠 Review preparedness plans"
                ]
            else:
                assessment['recommendations'] = [
                    "📊 Continue standard monitoring",
                    "📱 Maintain public awareness",
                    "📡 Regular satellite imagery analysis"
                ]
            
            assessment['risk_factors'] = risk_factors
            
        except Exception as e:
            print(f"⚠️ Error generating overall assessment: {e}")
            assessment['error'] = str(e)
        
        return assessment
    
    def _create_error_result(self, error_message):
        """Create error result structure"""
        return {
            'timestamp': pd.Timestamp.now().isoformat(),
            'error': error_message,
            'enhanced_analysis': [],
            'global_features': {},
            'overall_assessment': {'error': error_message}
        }
    
    def get_model_performance(self):
        """Get model performance metrics"""
        if not self.training_report:
            return None
        
        return {
            'dataset_info': self.training_report.get('dataset_info', {}),
            'feature_models': self.training_report.get('training_results', {}).get('feature_models', {}),
            'eye_detection': self.training_report.get('training_results', {}).get('eye_detection', {}),
            'training_date': self.training_report.get('training_date', 'Unknown')
        }


class CycloneFeatureExtractor:
    """Extract comprehensive features from cyclone satellite images"""
    
    def extract_comprehensive_features(self, image, image_id):
        """Extract comprehensive features from cyclone image"""
        
        # Convert to numpy array if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Ensure image is in correct format
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Initialize feature dict
        features = {
            'image_id': image_id,
            'height': image.shape[0],
            'width': image.shape[1]
        }
        
        try:
            # Eye detection features
            eye_features = self.detect_eye_features(gray)
            features.update(eye_features)
            
            # Structural features
            structure_features = self.extract_structural_features(gray)
            features.update(structure_features)
            
            # Intensity indicators
            intensity_features = self.extract_intensity_features(gray)
            features.update(intensity_features)
            
            # Symmetry analysis
            symmetry_features = self.analyze_symmetry(gray)
            features.update(symmetry_features)
            
            # Bounding box features
            bbox_features = self.extract_bbox_features(gray)
            features.update(bbox_features)
        
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            # Fill with default values
            default_features = {
                'eye_detected': 0, 'eye_clarity': 0, 'center_brightness': 0,
                'spiral_patterns': 0, 'largest_circle_radius': 0,
                'edge_density': 0, 'texture_variance': 0, 'brightness_std': 0, 'mean_brightness': 0,
                'horizontal_symmetry': 0, 'vertical_symmetry': 0, 'overall_symmetry': 0,
                'bbox_width': image.shape[1], 'bbox_height': image.shape[0], 
                'bbox_area': image.shape[0] * image.shape[1]
            }
            features.update(default_features)
        
        return features
    
    def detect_eye_features(self, gray_image):
        """Detect eye-related features"""
        features = {}
        
        # Get image center
        h, w = gray_image.shape
        center_x, center_y = w // 2, h // 2
        
        # Center brightness analysis
        center_region = gray_image[center_y-20:center_y+20, center_x-20:center_x+20]
        features['center_brightness'] = np.mean(center_region) if center_region.size > 0 else 0
        
        # Eye detection using circular patterns
        try:
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray_image, (9, 9), 2)
            
            # Detect circles using HoughCircles
            circles = cv2.HoughCircles(
                blurred, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30, minRadius=5, maxRadius=min(50, min(h, w)//4)
            )
            
            eye_detected = 0
            eye_clarity = 0
            
            if circles is not None:
                circles = np.around(circles[0, :]).astype("int")
                
                # Check if any circle is near center
                for (x, y, r) in circles:
                    distance_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance_from_center < min(w, h) * 0.3:  # Within center region
                        eye_detected = 1
                        # Calculate eye clarity based on gradient around circle
                        mask = np.zeros_like(gray_image)
                        cv2.circle(mask, (x, y), r, 255, -1)
                        eye_region = cv2.bitwise_and(gray_image, mask)
                        eye_clarity = np.std(eye_region[mask > 0]) if np.sum(mask > 0) > 0 else 0
                        break
            
            features['eye_detected'] = eye_detected
            features['eye_clarity'] = eye_clarity
        
        except Exception:
            features['eye_detected'] = 0
            features['eye_clarity'] = 0
        
        return features
    
    def extract_structural_features(self, gray_image):
        """Extract structural features like spirals and patterns"""
        features = {}
        
        # Spiral pattern detection using edge analysis
        try:
            # Edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Count edge pixels as proxy for spiral complexity
            features['spiral_patterns'] = np.sum(edges > 0) / edges.size
            
            # Find largest circular structure
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Fit circle to largest contour
                if len(largest_contour) >= 5:
                    (x, y), radius = cv2.minEnclosingCircle(largest_contour)
                    features['largest_circle_radius'] = radius
                else:
                    features['largest_circle_radius'] = 0
            else:
                features['largest_circle_radius'] = 0
        
        except Exception:
            features['spiral_patterns'] = 0
            features['largest_circle_radius'] = 0
        
        return features
    
    def extract_intensity_features(self, gray_image):
        """Extract intensity-related features"""
        features = {}
        
        # Basic intensity statistics
        features['mean_brightness'] = np.mean(gray_image)
        features['brightness_std'] = np.std(gray_image)
        
        # Texture analysis
        features['texture_variance'] = np.var(gray_image)
        
        # Edge density
        try:
            edges = cv2.Canny(gray_image, 50, 150)
            features['edge_density'] = np.sum(edges > 0) / edges.size
        except Exception:
            features['edge_density'] = 0
        
        return features
    
    def analyze_symmetry(self, gray_image):
        """Analyze symmetry of the cyclone"""
        features = {}
        
        h, w = gray_image.shape
        
        # Horizontal symmetry
        left_half = gray_image[:, :w//2]
        right_half = np.fliplr(gray_image[:, w//2:])
        
        # Ensure same size
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Calculate correlation
        try:
            corr_matrix = np.corrcoef(left_half.flatten(), right_half.flatten())
            features['horizontal_symmetry'] = corr_matrix[0, 1] if not np.isnan(corr_matrix[0, 1]) else 0
        except:
            features['horizontal_symmetry'] = 0
        
        # Vertical symmetry
        top_half = gray_image[:h//2, :]
        bottom_half = np.flipud(gray_image[h//2:, :])
        
        # Ensure same size
        min_height = min(top_half.shape[0], bottom_half.shape[0])
        top_half = top_half[:min_height, :]
        bottom_half = bottom_half[:min_height, :]
        
        try:
            corr_matrix = np.corrcoef(top_half.flatten(), bottom_half.flatten())
            features['vertical_symmetry'] = corr_matrix[0, 1] if not np.isnan(corr_matrix[0, 1]) else 0
        except:
            features['vertical_symmetry'] = 0
        
        # Overall symmetry
        features['overall_symmetry'] = (
            abs(features['horizontal_symmetry']) + abs(features['vertical_symmetry'])
        ) / 2
        
        return features
    
    def extract_bbox_features(self, gray_image):
        """Extract bounding box features"""
        h, w = gray_image.shape
        
        return {
            'bbox_width': w,
            'bbox_height': h,
            'bbox_area': w * h
        }
