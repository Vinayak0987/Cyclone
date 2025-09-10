"""
Enhanced Cyclone Analysis Package
Provides advanced meteorological analysis for YOLOv5 cyclone detection
"""

__version__ = "1.0.0"

try:
    from .yolo_enhanced_analyzer import YOLOEnhancedAnalyzer, CycloneFeatureExtractor
    from .enhanced_astroalert import EnhancedAstroAlert
    
    __all__ = ['YOLOEnhancedAnalyzer', 'CycloneFeatureExtractor', 'EnhancedAstroAlert']
    
except ImportError as e:
    # Graceful degradation if dependencies are missing
    print(f"⚠️ Enhanced analysis not fully available: {e}")
    __all__ = []
