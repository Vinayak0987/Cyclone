# 🤖 CycloneBot - AI-Powered Chatbot Integration

CycloneBot is an intelligent chatbot powered by Google's Gemini Flash API that provides expert assistance for cyclone analysis, meteorology, and disaster preparedness within the AstroAlert system.

## 🌟 Features

### **Intelligent Conversations**
- 🧠 Powered by Google Gemini 1.5 Flash for accurate, contextual responses
- 🌪 Expert knowledge in tropical cyclones, meteorology, and disaster management
- 📊 Contextual understanding of your analysis results
- 🔮 Respectful explanations of Vedic astrology approaches

### **Interactive Interface**
- 💬 Modern, responsive chat interface
- 📱 Mobile-friendly design
- ⚡ Real-time typing indicators
- 💡 Smart suggested questions based on your analysis
- 🗑️ Conversation history management

### **Safety-Focused**
- 🚨 Prioritizes safety in all recommendations
- 📋 Provides actionable emergency guidance
- 🎯 Categorizes responses (emergency, safety, educational, etc.)
- 🛡️ Scientifically accurate information

## 🚀 Quick Setup

### 1. **Get Gemini API Key**
```bash
# Visit Google AI Studio
https://aistudio.google.com/app/apikey
```
1. Click "Create API key"
2. Copy your API key (starts with "AIza...")

### 2. **Run Setup Script**
```bash
python setup_chatbot.py
```
Follow the interactive prompts to configure your API key.

### 3. **Alternative Manual Setup**
```bash
# Windows
setx GEMINI_API_KEY "your-api-key-here"

# Linux/Mac
export GEMINI_API_KEY="your-api-key-here"
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 4. **Start the Server**
```bash
python app.py
```

## 💡 Usage Examples

### **General Cyclone Questions**
- "What is a tropical cyclone?"
- "How do cyclones form?"
- "What's the difference between hurricanes and typhoons?"

### **Analysis Interpretation**
- "Why is my VRS score 43?"
- "What does MODERATE risk level mean?"
- "How reliable is AI-based detection?"

### **Safety & Preparedness**
- "What should I do if a cyclone is approaching?"
- "What emergency supplies do I need?"
- "How quickly can weather conditions change?"

### **Vedic Astrology Questions**
- "How does Vedic astrology predict weather?"
- "What are the risk factors in my analysis?"
- "What does Saturn in Pisces mean for cyclone risk?"

## 🔧 Technical Details

### **API Endpoints**
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/suggestions` - Get contextual suggestions
- `POST /api/chat/clear` - Clear conversation history
- `GET /api/chat/status` - Check chatbot availability

### **Response Categories**
- `emergency` - Urgent safety matters (red styling)
- `safety` - Safety recommendations (orange styling)
- `educational` - Explanatory content (blue styling)
- `astrology` - Vedic astrology topics (purple styling)
- `analysis` - Result interpretations (default styling)
- `general` - General conversations (default styling)

### **Architecture**
```
Frontend (JavaScript) ←→ Flask API ←→ Gemini Flash API
     ↓                       ↓
   Chat UI              CycloneChatbot
     ↓                       ↓
 Suggestions          Analysis Context
```

## ⚙️ Configuration

### **Environment Variables**
```bash
GEMINI_API_KEY=your-api-key-here  # Required for chatbot functionality
```

### **Chatbot Parameters**
```python
# In chatbot_module.py - CycloneChatbot.__init__()
temperature=0.7        # Response creativity (0-1)
max_output_tokens=500  # Maximum response length
top_p=0.8             # Nucleus sampling
top_k=20              # Top-k sampling
```

## 🎨 UI Components

### **Chatbot Container**
- Fixed position bottom-right corner
- Minimizable/expandable interface
- Glassmorphism design with backdrop blur
- Responsive design for mobile devices

### **Message Types**
- **User Messages**: Right-aligned, gradient background
- **Bot Messages**: Left-aligned, light background with border
- **Category-specific styling**: Color-coded by response type
- **Typing Indicator**: Animated dots during response generation

### **Suggested Questions**
- Context-aware suggestions based on analysis results
- Clickable buttons for quick interaction
- Updates dynamically after conversations

## 🛡️ Safety Features

### **Content Moderation**
- Built-in safety guidelines in system prompt
- Prioritizes scientific accuracy
- Focuses on disaster preparedness
- Respectful approach to traditional knowledge

### **Error Handling**
- Graceful degradation when API is unavailable
- Connection status indicators
- Retry mechanisms for failed requests
- User-friendly error messages

## 📊 Integration with AstroAlert

### **Analysis Context**
The chatbot automatically receives context from your cyclone analysis:
- AI detection results (cyclones detected, confidence levels)
- VRS scores and risk factors
- Combined risk assessments
- Timestamp and location data

### **Contextual Responses**
Based on your analysis, the chatbot provides:
- Explanations of your specific results
- Personalized safety recommendations
- Detailed interpretations of risk factors
- Follow-up questions relevant to your situation

## 🔍 Troubleshooting

### **Chatbot Shows "Offline"**
1. Check if `GEMINI_API_KEY` is set correctly
2. Verify API key is valid at Google AI Studio
3. Check internet connection
4. Restart the Flask server

### **No Response from Chatbot**
1. Check browser console for JavaScript errors
2. Verify Flask server is running
3. Check API key quotas in Google AI Studio
4. Try refreshing the page

### **Setup Script Issues**
```bash
# Install required packages
pip install google-generativeai flask flask-cors

# Run setup script
python setup_chatbot.py

# Manual API key test
python -c "from chatbot_module import CycloneChatbot; bot = CycloneChatbot(); print('✅ Working!')"
```

## 📈 Performance Optimization

### **Response Caching**
- Conversation history maintained for context
- Suggested questions cached between interactions
- Analysis context preserved during session

### **Rate Limiting**
- Built-in protection against rapid-fire requests
- Typing indicators prevent multiple simultaneous requests
- Input validation and sanitization

## 🔐 Security Considerations

### **API Key Management**
- Environment variables preferred over hardcoding
- .env file support for development
- API key masking in logs and display

### **Input Sanitization**
- Message length limits (500 characters)
- Special character handling
- XSS prevention in message display

## 🎯 Future Enhancements

### **Planned Features**
- [ ] Voice input/output support
- [ ] Multi-language support
- [ ] Advanced weather data integration
- [ ] Conversation export functionality
- [ ] Custom prompt templates

### **Integration Ideas**
- [ ] Real-time weather API data
- [ ] Historical cyclone database queries
- [ ] Evacuation route recommendations
- [ ] Emergency contact integration

## 📝 License

This chatbot integration is part of the AstroAlert system and follows the same licensing terms.

---

**Need Help?** 
- 🐛 Report issues in the main repository
- 💡 Suggest features via GitHub issues
- 📧 Contact support for urgent matters
- 🤖 Ask CycloneBot itself for help with cyclone-related questions!
