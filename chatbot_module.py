#!/usr/bin/env python3
"""
Gemini Flash Chatbot for Cyclone Risk Analysis
Provides intelligent responses about cyclones, risk assessment, and analysis results
"""

import google.generativeai as genai
import json
import datetime
from typing import Dict, List, Optional
import os

class CycloneChatbot:
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini Flash chatbot for cyclone analysis
        
        Args:
            api_key: Google Gemini API key (can also be set via GEMINI_API_KEY env var)
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini Flash model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System context for the chatbot
        self.system_context = """
        You are CycloneBot, an expert AI assistant specializing in tropical cyclone analysis, meteorology, and disaster preparedness. 
        You work with the AstroAlert cyclone prediction system that combines:
        
        1. AI-based satellite image analysis using YOLOv5 for cyclone detection
        2. Vedic Astrology Risk Score (VRS) calculations based on planetary positions
        3. Combined risk assessment providing actionable insights
        
        Your expertise includes:
        - Tropical cyclone formation, structure, and behavior
        - Satellite meteorology and image interpretation
        - Risk assessment and emergency preparedness
        - Vedic astrology applications in weather prediction
        - Disaster management and safety protocols
        
        Guidelines for responses:
        - Provide accurate, scientific information about cyclones
        - Explain technical concepts in accessible language
        - Offer practical safety advice and recommendations
        - Be supportive and reassuring while maintaining scientific accuracy
        - If asked about specific analysis results, interpret them clearly
        - For Vedic astrology questions, explain the traditional approach respectfully while noting scientific limitations
        - Always prioritize safety in your recommendations
        
        Keep responses concise but informative (2-3 paragraphs max unless specifically asked for detailed explanations).
        """
        
        # Conversation history
        self.conversation_history = []
        
        print("🤖 CycloneBot initialized with Gemini Flash API")

    def add_analysis_context(self, analysis_results: Dict):
        """
        Add recent analysis results as context for the chatbot
        
        Args:
            analysis_results: Results from AstroAlert analysis
        """
        if not analysis_results:
            return
            
        try:
            # Extract key information for context
            detection = analysis_results.get('results', {}).get('detection', {})
            astrology = analysis_results.get('results', {}).get('astrology', {}).get('vrs_analysis', {})
            combined = analysis_results.get('results', {}).get('combined', {}).get('combined_assessment', {})
            
            context_summary = f"""
            Recent Analysis Results:
            - AI Detection: {detection.get('total_cyclones', 0)} cyclones detected with {detection.get('avg_confidence', 0)*100:.1f}% average confidence
            - VRS Score: {astrology.get('vrs_score', 0)}/100 ({astrology.get('risk_level', 'UNKNOWN')} risk)
            - Combined Risk: {combined.get('combined_risk_score', 0):.1f}/100 ({combined.get('final_risk_level', 'UNKNOWN')} level)
            - Risk Factors: {len(astrology.get('risk_factors', []))} factors identified
            - Analysis Time: {analysis_results.get('analysis_timestamp', 'Unknown')}
            """
            
            self.current_analysis_context = context_summary
            
        except Exception as e:
            print(f"Error adding analysis context: {e}")
            self.current_analysis_context = None

    def chat(self, user_message: str, include_analysis: bool = True) -> Dict:
        """
        Process user message and generate response
        
        Args:
            user_message: User's question or message
            include_analysis: Whether to include recent analysis results in context
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Prepare conversation context
            context_parts = [self.system_context]
            
            # Add analysis context if available and requested
            if include_analysis and hasattr(self, 'current_analysis_context'):
                context_parts.append(self.current_analysis_context)
            
            # Add conversation history (last 6 messages to maintain context)
            recent_history = self.conversation_history[-6:] if self.conversation_history else []
            if recent_history:
                history_text = "\n".join([
                    f"User: {msg['user']}\nAssistant: {msg['assistant']}" 
                    for msg in recent_history
                ])
                context_parts.append(f"Recent conversation:\n{history_text}")
            
            # Add current user message
            context_parts.append(f"User: {user_message}")
            
            # Generate response
            full_prompt = "\n\n".join(context_parts)
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                    top_p=0.8,
                    top_k=20
                )
            )
            
            # Extract response text
            response_text = response.text
            
            # Add to conversation history
            self.conversation_history.append({
                'user': user_message,
                'assistant': response_text,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            # Determine response category for UI styling
            category = self._categorize_response(user_message.lower())
            
            return {
                'response': response_text,
                'category': category,
                'timestamp': datetime.datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again in a moment or contact support if the problem persists.",
                'category': 'error',
                'timestamp': datetime.datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }

    def _categorize_response(self, user_message: str) -> str:
        """Categorize the user message for UI styling"""
        if any(word in user_message for word in ['emergency', 'evacuate', 'danger', 'immediate', 'urgent']):
            return 'emergency'
        elif any(word in user_message for word in ['explain', 'what', 'how', 'why', 'understand']):
            return 'educational'
        elif any(word in user_message for word in ['vrs', 'astrology', 'planetary', 'vedic']):
            return 'astrology'
        elif any(word in user_message for word in ['prepare', 'safety', 'protect', 'advice']):
            return 'safety'
        elif any(word in user_message for word in ['analysis', 'result', 'score', 'detection']):
            return 'analysis'
        else:
            return 'general'

    def get_suggested_questions(self, analysis_results: Dict = None) -> List[str]:
        """
        Generate contextual suggested questions based on analysis results
        
        Args:
            analysis_results: Recent analysis results (optional)
            
        Returns:
            List of suggested questions
        """
        base_questions = [
            "How do tropical cyclones form?",
            "What should I do if a cyclone is approaching?",
            "How reliable are satellite-based cyclone predictions?",
            "What factors make a cyclone more dangerous?"
        ]
        
        if not analysis_results:
            return base_questions
        
        try:
            detection = analysis_results.get('results', {}).get('detection', {})
            astrology = analysis_results.get('results', {}).get('astrology', {}).get('vrs_analysis', {})
            combined = analysis_results.get('results', {}).get('combined', {}).get('combined_assessment', {})
            
            contextual_questions = []
            
            # Add questions based on detection results
            cyclone_count = detection.get('total_cyclones', 0)
            if cyclone_count > 0:
                contextual_questions.append(f"What does it mean that {cyclone_count} cyclone{'s' if cyclone_count > 1 else ''} {'were' if cyclone_count > 1 else 'was'} detected?")
                contextual_questions.append("How accurate is AI-based cyclone detection?")
            
            # Add questions based on VRS score
            vrs_score = astrology.get('vrs_score', 0)
            risk_level = astrology.get('risk_level', 'UNKNOWN')
            if vrs_score > 0:
                contextual_questions.append(f"Why is my VRS score {vrs_score} and risk level {risk_level}?")
                contextual_questions.append("How does Vedic astrology predict weather patterns?")
            
            # Add questions based on combined risk
            final_risk = combined.get('final_risk_level', 'UNKNOWN')
            if final_risk in ['HIGH', 'EXTREME']:
                contextual_questions.append("What immediate steps should I take for high cyclone risk?")
                contextual_questions.append("How quickly can weather conditions change?")
            elif final_risk == 'MODERATE':
                contextual_questions.append("What precautions should I take for moderate risk?")
            
            # Combine and return top questions
            all_questions = contextual_questions + base_questions
            return all_questions[:6]  # Return up to 6 questions
            
        except Exception as e:
            print(f"Error generating suggested questions: {e}")
            return base_questions

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        if hasattr(self, 'current_analysis_context'):
            delattr(self, 'current_analysis_context')

    def get_conversation_summary(self) -> Dict:
        """Get summary of current conversation"""
        return {
            'message_count': len(self.conversation_history),
            'last_message_time': self.conversation_history[-1]['timestamp'] if self.conversation_history else None,
            'topics_discussed': len(set(msg.get('category', 'general') for msg in self.conversation_history))
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the chatbot (requires API key)
    try:
        # Initialize chatbot
        # You'll need to set GEMINI_API_KEY environment variable
        chatbot = CycloneChatbot()
        
        print("🤖 CycloneBot Test")
        print("=" * 40)
        
        # Test basic conversation
        test_questions = [
            "What is a tropical cyclone?",
            "How dangerous are Category 5 hurricanes?",
            "What emergency supplies should I have?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            response = chatbot.chat(question)
            if response['success']:
                print(f"🤖 Response: {response['response']}")
                print(f"📋 Category: {response['category']}")
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
        
        # Test suggested questions
        print(f"\n💡 Suggested Questions:")
        suggestions = chatbot.get_suggested_questions()
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
            
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please set your GEMINI_API_KEY environment variable")
        print("   Example: export GEMINI_API_KEY='your-api-key-here'")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
