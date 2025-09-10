from main_astroalert_fixed import AstroAlert
import datetime

aa = AstroAlert()
result = aa.detect_cyclones('data/train/images/1.jpg')
print('Detection result:')
print(f'Total cyclones: {result.get("total_cyclones", 0)}')
print(f'Avg confidence: {result.get("avg_confidence", 0)}')
print(f'Max confidence: {result.get("max_confidence", 0)}')
print(f'Detection quality: {result.get("detection_quality", "N/A")}')
print(f'Error: {result.get("error", "None")}')
print(f'Full result keys: {list(result.keys())}')
