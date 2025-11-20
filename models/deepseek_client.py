"""
DeepSeek API Client - Professional integration for emotion analysis
"""

import os
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI

import requests
import json
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DeepSeekProvider:
    """DeepSeek API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
        
    def is_connected(self) -> bool:
        """Check if DeepSeek API is reachable"""
        if not self.api_key:
            return False
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                          temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate content using the DeepSeek API"""
        if not self.api_key:
            return "Error: DeepSeek API key not configured"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"DeepSeek API Error: {e}")
            return f"Error: {str(e)}"


class DeepSeekRealtimeClient:
    """DeepSeek realtime client - simulated realtime behavior"""
    
    def __init__(self, api_key: str):
        self.provider = DeepSeekProvider(api_key)
        self.session_active = False
        
    def is_connected(self) -> bool:
        return self.provider.is_connected()
        
    def start_session(self) -> bool:
        """Start realtime session"""
        if self.provider.is_connected():
            self.session_active = True
            logger.info("DeepSeek realtime session started")
            return True
        return False
        
    def end_session(self):
        """End realtime session"""
        self.session_active = False
        logger.info("DeepSeek realtime session ended")
        
    def analyze_emotions_realtime(self, text: str) -> Dict:
        """Realtime emotion analysis"""
        if not self.session_active:
            return {"error": "Session not active"}
            
        system_prompt = """You are a professional emotion analyst. Analyze the user's text and identify emotional state.

    Return valid JSON with:
    1. primary_emotion: one of [joy, sadness, anger, fear, surprise, disgust, trust, anticipation, neutral]
    2. emotions: confidence scores for emotions (0-100 numbers)
    3. intensity: one of [low, medium, high]
    4. sentiment: one of [positive, negative, neutral]

    Return JSON only, no extra text."""

        user_prompt = f"Analyze the emotions in this text:\n\n{text}"
        
        response = self.provider.generate_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        try:
            # Try to parse JSON response
            emotion_data = json.loads(response)
            return emotion_data
        except json.JSONDecodeError:
            # Fallback when parsing fails
            logger.warning(f"Failed to parse JSON response: {response}")
            return {
                "primary_emotion": "neutral",
                "emotions": {"neutral": 50, "contemplative": 30},
                "intensity": "medium",
                "sentiment": "neutral"
            }
    
    def generate_philosophical_note_realtime(self, primary_emotion: str, emotions: Dict[str, float], text_context: str = "") -> str:
        """Generate philosophical reflection in realtime"""
        if not self.session_active:
            return "Session not active"
            
        system_prompt = """You are a wise philosopher-psychologist. Based on the user's emotional state, write a short, warm, and inspiring reflection.

    Guidelines:
    1. 2–3 sentences, concise and deep
    2. Show understanding and acceptance
    3. Offer positive life insight
    4. Graceful, slightly poetic language
    5. Avoid lecturing; focus on companionship and empathy"""

        emotion_list = ", ".join([f"{k}({v}%)" for k, v in emotions.items()])
        
        user_prompt = f"""User's current emotional state:
    Primary emotion: {primary_emotion}
    Emotion distribution: {emotion_list}
    Original text: {text_context}

    Please write a short philosophical reflection for this state."""

        response = self.provider.generate_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=200
        )
        
        return response.strip()


class EnhancedOnlineAIClient:
    """Enhanced online AI client with DeepSeek support"""
    
    def __init__(self, provider_type: str = "auto"):
        self.provider = None
        self.provider_name = ""
        
        if provider_type == "auto":
            # Check DeepSeek API key
            if os.getenv("DEEPSEEK_API_KEY"):
                self.provider = DeepSeekProvider()
                self.provider_name = "DeepSeek"
                print("🤖 Using DeepSeek AI for emotion analysis")
            elif os.getenv("OPENAI_API_KEY"):
                from models.online_ai_client import OpenAIProvider
                self.provider = OpenAIProvider()
                self.provider_name = "OpenAI"
                print("🤖 Using OpenAI for emotion analysis")
            elif os.getenv("ANTHROPIC_API_KEY"):
                from models.online_ai_client import AnthropicProvider
                self.provider = AnthropicProvider()
                self.provider_name = "Anthropic"
                print("🤖 Using Anthropic Claude for emotion analysis")
            else:
                from models.online_ai_client import MockAIProvider
                self.provider = MockAIProvider()
                self.provider_name = "Mock Provider"
                print("🤖 Using mock AI for testing")
        elif provider_type == "deepseek":
            self.provider = DeepSeekProvider()
            self.provider_name = "DeepSeek"
        
    def is_connected(self) -> bool:
        return self.provider.is_connected() if self.provider else False
    
    def get_provider_info(self) -> str:
        return f"{self.provider_name} (Connected)" if self.is_connected() else f"{self.provider_name} (Disconnected)"
    
    def analyze_emotions(self, text: str) -> Dict:
        """Analyze emotions"""
        if isinstance(self.provider, DeepSeekProvider):
            # 使用DeepSeek的特殊情感分析
            return self._analyze_emotions_deepseek(text)
        else:
            # 使用通用方法
            return self._analyze_emotions_generic(text)
    
    def _analyze_emotions_deepseek(self, text: str) -> Dict:
        """DeepSeek-specific emotion analysis"""
        system_prompt = """You are an expert emotion analyst. Analyze the user's text and return JSON only:
    {
      "primary_emotion": "emotion name",
      "emotions": { "emotion": score },
      "intensity": "low/medium/high",
      "sentiment": "positive/negative/neutral"
    }"""

        user_prompt = f"Analyze the emotions in this text: {text}"
        
        response = self.provider.generate_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        try:
            return json.loads(response)
        except:
            return {
                "primary_emotion": "contemplative",
                "emotions": {"contemplative": 70, "curious": 30},
                "intensity": "medium",
                "sentiment": "neutral"
            }
    
    def _analyze_emotions_generic(self, text: str) -> Dict:
        """Generic emotion analysis method"""
        # 这里可以调用其他AI提供商的方法
        if hasattr(self.provider, 'analyze_emotions'):
            return self.provider.analyze_emotions(text)
        else:
            # Fallback
            return {
                "primary_emotion": "neutral",
                "emotions": {"neutral": 50},
                "intensity": "medium", 
                "sentiment": "neutral"
            }
    
    def generate_philosophical_note(self, primary_emotion: str, emotions: Dict[str, float], text_context: str = "") -> str:
        """Generate philosophical reflection"""
        system_prompt = """You are a wise philosopher. Based on the user's emotional state, write a deep and warm reflection.

    Guidelines:
    - 2–3 sentences
    - Show understanding and empathy
    - Offer positive insight
    - Poetic tone, avoid lecturing"""

        emotion_desc = f"Primary emotion: {primary_emotion}, distribution: {emotions}"
        user_prompt = f"Write a short reflection for this emotional state: {emotion_desc}"
        
        if text_context:
            user_prompt += f"\nOriginal text: {text_context}"
        
        response = self.provider.generate_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=200
        )
        
        return response.strip()
