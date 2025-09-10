import json
import webbrowser
import os
import tempfile
from pathlib import Path

def debug_frontend_display():
    """
    Create a simple HTML page that displays the JSON values the same way
    the frontend should, to verify they're visible
    """
    # Load the most recent report
    try:
        with open('results/astroalert_report.json', 'r') as f:
            data = json.load(f)
            
        print("Successfully loaded JSON report")
        
        # Extract key values
        results = data.get('results', {})
        detection = results.get('detection', {})
        
        total_cyclones = detection.get('total_cyclones', 0)
        avg_confidence = detection.get('avg_confidence', 0)
        
        # Get combined assessment
        combined = results.get('combined', {})
        ai_detection = combined.get('ai_detection', {})
        ai_risk_score = ai_detection.get('ai_risk_score', 0)
        
        # Get astrology data
        astrology = results.get('astrology', {})
        vrs_analysis = astrology.get('vrs_analysis', {})
        vrs_score = vrs_analysis.get('vrs_score', 0)
        risk_level = vrs_analysis.get('risk_level', 'UNKNOWN')
        
        # Get combined results
        combined_assessment = combined.get('combined_assessment', {})
        combined_risk_score = combined_assessment.get('combined_risk_score', 0)
        final_risk_level = combined_assessment.get('final_risk_level', 'UNKNOWN')
        
        # Create HTML display
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AstroAlert Debug Display</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .card {{ background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                h2 {{ color: #333; }}
                .value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .label {{ color: #777; font-size: 14px; }}
                .HIGH {{ color: red; }}
                .MODERATE {{ color: orange; }}
                .LOW {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>AstroAlert Frontend Debug</h1>
            <p>This page displays the values that should be shown in the frontend:</p>
            
            <div class="grid">
                <div class="card">
                    <h2>AI Detection</h2>
                    <div class="label">Cyclones Detected:</div>
                    <div class="value">{total_cyclones}</div>
                    <div class="label">Average Confidence:</div>
                    <div class="value">{avg_confidence * 100:.1f}%</div>
                    <div class="label">AI Risk Score:</div>
                    <div class="value">{ai_risk_score}</div>
                </div>
                
                <div class="card">
                    <h2>Vedic Astrology</h2>
                    <div class="label">VRS Score:</div>
                    <div class="value">{vrs_score}/100</div>
                    <div class="label">Risk Level:</div>
                    <div class="value {risk_level}">{risk_level}</div>
                </div>
                
                <div class="card">
                    <h2>Combined Assessment</h2>
                    <div class="label">Combined Risk Score:</div>
                    <div class="value">{combined_risk_score}</div>
                    <div class="label">Final Risk Level:</div>
                    <div class="value {final_risk_level}">{final_risk_level}</div>
                </div>
            </div>
            
            <h2>JSON Data Structure:</h2>
            <pre>{json.dumps(data, indent=2)}</pre>
        </body>
        </html>
        """
        
        # Write to a temporary file
        temp_file = os.path.join(tempfile.gettempdir(), 'astroalert_debug.html')
        with open(temp_file, 'w') as f:
            f.write(html_content)
            
        print(f"Created debug HTML at: {temp_file}")
        
        # Open in browser
        print("Opening in browser...")
        webbrowser.open('file://' + temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    debug_frontend_display()
