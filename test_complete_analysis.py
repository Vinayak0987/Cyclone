from main_astroalert_fixed import AstroAlert
import datetime

aa = AstroAlert()
result = aa.run_complete_analysis('data/train/images/1.jpg', 19.0760, 72.8777)
print('\n=== COMPLETE ANALYSIS RESULT ===')
print(f'Analysis Type: {result.get("analysis_type", "N/A")}')

# Detection results
detection = result.get('results', {}).get('detection', {})
print('\n--- AI Detection ---')
print(f'Total cyclones: {detection.get("total_cyclones", 0)}')
print(f'Avg confidence: {detection.get("avg_confidence", 0)}')
print(f'Max confidence: {detection.get("max_confidence", 0)}')
print(f'Detection quality: {detection.get("detection_quality", "N/A")}')

# Combined assessment  
combined = result.get('results', {}).get('combined', {})
ai_detection = combined.get('ai_detection', {})
print('\n--- Combined Assessment - AI Detection ---')
print(f'Cyclones detected: {ai_detection.get("cyclones_detected", 0)}')
print(f'Average confidence: {ai_detection.get("average_confidence", 0)}')  
print(f'AI risk score: {ai_detection.get("ai_risk_score", 0)}')

# Astrology results
astrology = result.get('results', {}).get('astrology', {})
vrs_analysis = astrology.get('vrs_analysis', {})
print('\n--- Astrology Analysis ---')
print(f'VRS Score: {vrs_analysis.get("vrs_score", 0)}')
print(f'Risk Level: {vrs_analysis.get("risk_level", "N/A")}')

# Combined final results
combined_assessment = combined.get('combined_assessment', {})
print('\n--- Final Combined Results ---')
print(f'Combined risk score: {combined_assessment.get("combined_risk_score", 0)}')
print(f'Final risk level: {combined_assessment.get("final_risk_level", "N/A")}')
print(f'Action required: {combined_assessment.get("action_required", "N/A")}')
