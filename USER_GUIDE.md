# 🌪 AstroAlert - Complete User Guide

## 🚀 **SIMPLEST WAY TO START**

### **Option 1: Double-Click Start (Easiest)**
1. **Double-click** `start_server.bat`
2. **Wait** for "Server running..." message
3. **Open browser** to `http://localhost:5000`
4. **Upload an image** and get instant results!

### **Option 2: Manual Start**
```bash
# In Command Prompt or PowerShell
cd C:\Users\Vinayak\Desktop\Cyclone
python app.py
```

---

## 🌐 **Using the Web Interface**

### **Step-by-Step:**
1. **📁 Upload Image:** Click "Choose satellite image..." and select any image file
2. **📍 Set Location:** Enter latitude and longitude coordinates (defaults to Mumbai)
3. **🕐 Set Time:** Choose date and time for analysis (defaults to current time)
4. **🔍 Analyze:** Click "Analyze Cyclone Risk" button
5. **📊 View Results:** Get comprehensive AI + Astrology analysis!

### **What You'll See:**
- **🤖 AI Detection:** Number of cyclones detected with confidence scores
- **🔮 Astrology Analysis:** VRS (Vedic Risk Score) and astrological risk factors
- **⚡ Combined Assessment:** Final risk level with color-coded indicators
- **📋 Recommendations:** Specific actions based on risk level

---

## 🔧 **System Features**

### **✅ Real-Time Analysis**
- **Live backend processing** using your trained AI model
- **Swiss Ephemeris calculations** for accurate astrological data
- **Combined risk assessment** merging AI and astrology insights

### **✅ Intelligent Fallback**
- **Auto-detects** if server is running
- **Falls back to demo mode** if server is offline
- **Shows connection status** indicator in top-right corner

### **✅ Modern Interface**
- **Glass-morphism design** with smooth animations
- **Responsive layout** works on desktop, tablet, and mobile
- **Real-time loading** animations with progress steps
- **Color-coded risk indicators** (Green=Low, Yellow=Moderate, Orange=High, Red=Extreme)

---

## 📊 **Understanding Results**

### **AI Detection Results:**
- **Cyclones Detected:** Number of potential cyclones found
- **Average Confidence:** How confident the AI is in its detections
- **AI Risk Score:** Risk contribution from AI analysis (0-30 points)

### **Vedic Astrology Results:**
- **VRS Score:** Vedic Risk Score out of 100
- **Risk Level:** LOW/MODERATE/HIGH/EXTREME based on planetary positions
- **Risk Factors:** Specific astrological indicators contributing to risk

### **Combined Assessment:**
- **Combined Risk Score:** Final score combining AI and astrology (0-100)
- **Final Risk Level:** Overall assessment with color coding
- **Action Required:** Specific recommendations based on risk level
- **Recommendations:** Detailed action items for emergency preparedness

---

## 🎯 **Risk Level Guide**

| Risk Level | Score Range | Color | Action Required |
|------------|-------------|-------|-----------------|
| **LOW** | 0-29 | 🟢 Green | Standard monitoring |
| **MODERATE** | 30-49 | 🟡 Yellow | Increased preparedness |
| **HIGH** | 50-69 | 🟠 Orange | High alert protocols |
| **EXTREME** | 70-100 | 🔴 Red | Emergency evacuation |

---

## 💡 **Tips for Best Results**

### **📸 Image Selection:**
- Use **satellite weather images** for best accuracy
- **Clear, high-resolution** images work better
- **Meteorological images** give more reliable results than regular photos

### **📍 Location Accuracy:**
- Use **precise coordinates** for better astrological calculations
- **Coastal coordinates** may show higher risk due to cyclone vulnerability
- **Use GPS coordinates** or maps to get exact latitude/longitude

### **🕐 Timing:**
- **Current time** gives most relevant analysis
- **Monsoon seasons** typically show higher astrological risk
- **Different times of day** can affect planetary position calculations

---

## 🔍 **Troubleshooting**

### **Server Won't Start:**
```bash
# Check if Python is installed
python --version

# Install missing packages
pip install flask flask-cors

# Try starting manually
python app.py
```

### **Browser Shows Demo Mode:**
- ✅ Server is not running - start with `python app.py`
- ✅ Wrong URL - use `http://localhost:5000` (not file:// path)
- ✅ Port conflict - try changing port in app.py

### **Analysis Fails:**
- ✅ Check image file format (PNG, JPG, JPEG, GIF only)
- ✅ Verify coordinates are valid numbers
- ✅ Check server console for error messages

---

## 🚀 **Advanced Usage**

### **Command Line Interface:**
```bash
# Direct analysis without web interface
python main_astroalert_fixed.py image.jpg 19.0760 72.8777

# View JSON results
type results\astroalert_report.json
```

### **API Endpoints:**
- `GET /api/health` - Check server status
- `POST /api/analyze` - Submit analysis request
- `GET /api/test` - Test backend components

### **Batch Processing:**
```bash
# Process multiple images
for file in data/train/images/*.jpg; do
    python main_astroalert_fixed.py "$file" 19.0760 72.8777
done
```

---

## 📁 **File Structure**

```
Cyclone/
├── 🚀 start_server.bat         # Easy start script
├── 🌐 app.py                   # Flask web server
├── 🖥️ index.html               # Main interface
├── 🎨 styles.css               # Visual styling
├── ⚡ script.js                # Interactive features
├── 🤖 main_astroalert_fixed.py # Core AI system
├── 🔮 astrology_module_clean.py# Astrology engine
├── ✅ verify_setup.py          # System verification
├── 📊 data/                    # Training data
├── 🔮 ephe/                    # Swiss Ephemeris
├── 📈 results/                 # Analysis outputs
└── 🤖 yolov5/                  # AI model
```

---

## 🎉 **Success Indicators**

When everything is working correctly, you should see:
- ✅ **Green status indicator** showing "Real Backend Connected"
- ✅ **Smooth loading animations** with progress steps
- ✅ **Real analysis results** with actual detection counts
- ✅ **Detailed recommendations** based on risk assessment
- ✅ **Color-coded risk visualization** in the results

---

## 🆘 **Support**

If you need help:
1. **Check the console** for error messages
2. **Run verification:** `python verify_setup.py`
3. **Test individual components** using the command line interface
4. **Check log files** in the results folder

---

**🌪 AstroAlert combines cutting-edge AI with ancient wisdom for comprehensive cyclone risk assessment!**
