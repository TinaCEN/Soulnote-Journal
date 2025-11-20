"""
DeepSeek API Client - Using OpenAI SDK format
"""

import os
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI


class DeepSeekProvider:
    """DeepSeek API provider using OpenAI SDK"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"
    
    def is_connected(self) -> bool:
        """Test DeepSeek API connection"""
        try:
            # Test with a simple completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"DeepSeek connection test failed: {e}")
            return False
    
    def generate_completion(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Generate completion using DeepSeek API with OpenAI SDK"""
        try:
            print(f"🧠 DeepSeek API Request using OpenAI SDK")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                stream=False
            )
            
            content = response.choices[0].message.content
            print(f"✅ DeepSeek Response: {content[:100]}...")
            return content
                
        except Exception as e:
            error_msg = f"DeepSeek API Error: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"


class DeepSeekRealtimeClient:
    """DeepSeek client with realtime capabilities"""
    
    def __init__(self, api_key: str):
        self.provider = DeepSeekProvider(api_key)
        self.session_active = False
        
    def is_connected(self) -> bool:
        return self.provider.is_connected()
        
    def start_session(self) -> bool:
        """Start realtime session"""
        if self.provider.is_connected():
            self.session_active = True
            print("🚀 DeepSeek realtime session started")
            return True
        return False
        
    def end_session(self):
        """End realtime session"""
        self.session_active = False
        print("🔚 DeepSeek realtime session ended")
    
    def analyze_emotions_realtime(self, text: str) -> Dict[str, Any]:
        """Real-time emotion analysis using DeepSeek"""
        if not self.session_active:
            print("⚠️ Session not active, starting...")
            self.start_session()
        
        prompt = f"""Analyze the emotional state of the following text and return JSON only.

Text: "{text}"

Return strictly this JSON structure:
{{
    "primary_emotion": "one of [joy, sadness, anger, fear, surprise, disgust, peace, neutral]",
    "emotions": {{
        "joy": 0-100,
        "sadness": 0-100,
        "anger": 0-100,
        "fear": 0-100,
        "surprise": 0-100,
        "disgust": 0-100,
        "peace": 0-100,
        "neutral": 0-100
    }}
}}

Return JSON only, with no extra text."""

        messages = [
            {"role": "system", "content": "You are a professional emotion analyst. Analyze text and output concise JSON with an English emotion label and scores."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.provider.generate_completion(messages, max_tokens=500)
            
            # Try to parse JSON response
            if response.startswith("Error"):
                return self._fallback_emotion_analysis(text)
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate result structure
                if 'primary_emotion' in result and 'emotions' in result:
                    return result
            
            return self._fallback_emotion_analysis(text)
            
        except Exception as e:
            print(f"❌ DeepSeek emotion analysis failed: {e}")
            return self._fallback_emotion_analysis(text)
    
    def generate_philosophical_note_realtime(
        self, 
        primary_emotion: str, 
        emotions: Dict[str, int], 
        original_text: str
    ) -> str:
        """Generate philosophical note using DeepSeek"""
        
        prompt = f"""Based on the following emotion analysis, write a short philosophical reflection:

    Original text: "{original_text}"
    Primary emotion: {primary_emotion}
    Emotion distribution: {emotions}

    Write ~120-180 words that are:
    1. Deep and insightful
    2. Clearly connected to the detected emotion
    3. Comforting and inspiring
    4. Graceful and slightly poetic

    Avoid meta phrases like "according to the analysis"; simply state the reflection."""

        messages = [
            {"role": "system", "content": "You are a thoughtful philosopher-psychologist who distills life wisdom from emotional states."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.provider.generate_completion(messages, max_tokens=800)
            
            if response.startswith("Error"):
                return self._fallback_philosophical_note(primary_emotion)
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ DeepSeek philosophical note failed: {e}")
            return self._fallback_philosophical_note(primary_emotion)
    
    def _fallback_emotion_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback emotion analysis when API fails"""
        # Simple keyword-based analysis
        text_lower = text.lower()
        
        emotions = {
            "joy": 20,
            "sadness": 20,
            "anger": 10,
            "fear": 10,
            "surprise": 10,
            "disgust": 5,
            "peace": 25,
            "neutral": 10
        }
        
        # Keyword detection
        if any(word in text_lower for word in ['开心', '高兴', '快乐', '兴奋', '愉快', 'happy', 'joy', 'joyful', 'excited', 'pleased', 'glad']):
            emotions['joy'] = 80
            primary = "joy"
        elif any(word in text_lower for word in ['难过', '悲伤', '伤心', '失落', '沮丧', 'sad', 'unhappy', 'down', 'depressed', 'blue']):
            emotions['sadness'] = 75
            primary = "sadness"
        elif any(word in text_lower for word in ['生气', '愤怒', '恼火', '气愤', 'angry', 'mad', 'furious', 'irritated', 'annoyed']):
            emotions['anger'] = 70
            primary = "anger"
        elif any(word in text_lower for word in ['害怕', '恐惧', '担心', '焦虑', '紧张', 'afraid', 'scared', 'fear', 'anxious', 'nervous']):
            emotions['fear'] = 65
            primary = "fear"
        elif any(word in text_lower for word in ['惊讶', 'surprised', 'astonished', 'amazed', 'shocked']):
            emotions['surprise'] = 65
            primary = "surprise"
        elif any(word in text_lower for word in ['厌恶', 'disgust', 'gross', 'nauseated', 'repulsed']):
            emotions['disgust'] = 60
            primary = "disgust"
        elif any(word in text_lower for word in ['平静', '宁静', '安宁', 'calm', 'peace', 'peaceful', 'relaxed']):
            emotions['peace'] = 70
            primary = "peace"
        else:
            primary = "neutral"
        
        return {
            "primary_emotion": primary,
            "emotions": emotions
        }
    
    def _fallback_philosophical_note(self, emotion: str) -> str:
        """Fallback philosophical notes"""
        notes = {
            "joy": "Joy is like spring sunlight: brief yet warming the whole heart. Lasting joy comes less from what we have than from how deeply we are grateful.",
            "sadness": "Sadness is a deep breath of the soul, teaching us to grow through pain. Like night makes us cherish dawn, sorrow helps us treasure moments of light.",
            "anger": "Anger is an inner fire that can destroy or forge. Learning to live with it is learning our boundaries. Turn anger into the strength to change.",
            "fear": "Fear rings like a bell in the heart, reminding us to honor the present. Courage is not the absence of fear, but moving forward with it.",
            "peace": "Peace is a home within, an inner stillness found amid noise. True peace is not escape, but a steady center after life's swells."
        }
        
        return notes.get(emotion, "Every emotion is a color of life, composing a singular human tapestry.")


class EnhancedOnlineAIClient:
    """Enhanced AI client with DeepSeek support"""
    
    def __init__(self, provider: str = "auto"):
        self.provider_name = provider
        self.client = None
        
        if provider == "auto":
            # Auto-detect available provider
            if os.getenv('DEEPSEEK_API_KEY'):
                self.provider_name = "deepseek"
                self.client = DeepSeekProvider(os.getenv('DEEPSEEK_API_KEY'))
            else:
                self.provider_name = "mock"
                self.client = None
        elif provider == "deepseek":
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if api_key:
                self.client = DeepSeekProvider(api_key)
            else:
                raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        if self.client:
            return self.client.is_connected()
        return False
    
    def analyze_emotions(self, text: str) -> Dict[str, Any]:
        """Analyze emotions in text"""
        if self.provider_name == "deepseek" and self.client:
            realtime_client = DeepSeekRealtimeClient(self.client.api_key)
            return realtime_client.analyze_emotions_realtime(text)
        else:
            # Mock analysis
            return {
                "primary_emotion": "neutral",
                "emotions": {
                    "joy": 30,
                    "sadness": 20,
                    "anger": 10,
                    "fear": 10,
                    "surprise": 10,
                    "disgust": 5,
                    "peace": 45,
                    "neutral": 25
                }
            }
    
    def generate_philosophical_note(
        self, 
        primary_emotion: str, 
        emotions: Dict[str, int], 
        text: str
    ) -> str:
        """Generate philosophical note"""
        if self.provider_name == "deepseek" and self.client:
            realtime_client = DeepSeekRealtimeClient(self.client.api_key)
            return realtime_client.generate_philosophical_note_realtime(
                primary_emotion, emotions, text
            )
        else:
            # Mock philosophical note
            return f"On {primary_emotion}: every emotion is a vital part of being human, revealing ourselves and the world more clearly."
