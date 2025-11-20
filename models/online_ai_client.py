"""
Online AI Client - Interface with various online AI services
Supports OpenAI, Anthropic, and other providers
"""

import requests
import json
import os
from typing import Dict, Optional
from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                          temperature: float = 0.7, max_tokens: int = 500) -> str:
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI API Provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        
    def is_connected(self) -> bool:
        """Check if OpenAI API is accessible"""
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
        """Generate completion using OpenAI API"""
        if not self.api_key:
            return "Error: OpenAI API key not configured"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
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
            print(f"OpenAI API Error: {e}")
            return ""


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude API Provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        
    def is_connected(self) -> bool:
        """Check if Anthropic API is accessible"""
        if not self.api_key:
            return False
        # Anthropic doesn't have a simple health check endpoint
        # We'll just check if we have an API key
        return True
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                          temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate completion using Anthropic API"""
        if not self.api_key:
            return "Error: Anthropic API key not configured"
        
        # Combine system and user prompts for Anthropic
        full_prompt = ""
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
        else:
            full_prompt = f"Human: {prompt}\n\nAssistant:"
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['content'][0]['text']
        except Exception as e:
            print(f"Anthropic API Error: {e}")
            return ""


class MockAIProvider(BaseAIProvider):
    """Mock AI Provider for testing without API keys"""
    
    def is_connected(self) -> bool:
        return True
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                          temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate mock responses for testing"""
        
        # Mock emotion analysis
        if "analyze the emotions" in prompt.lower() or "emotion" in prompt.lower():
            return json.dumps({
                "primary_emotion": "contemplative",
                "emotions": {
                    "contemplative": 70,
                    "hopeful": 20,
                    "curious": 10
                },
                "intensity": "medium",
                "sentiment": "neutral"
            })
        
        # Mock philosophical note
        elif "philosophical note" in prompt.lower() or "philosophical" in prompt.lower():
            return "In the garden of consciousness, every emotion is a seed that grows into wisdom. Your feelings today are not just passing clouds, but teachers showing you the depths of your humanity."
        
        # Default response
        else:
            return "This is a mock response. To use real AI, configure an API key for OpenAI or Anthropic."


class OnlineAIClient:
    """Main client that manages different AI providers"""
    
    def __init__(self, provider_type: str = "auto"):
        """
        Initialize with a specific provider or auto-detect
        
        Args:
            provider_type: "openai", "anthropic", "mock", or "auto"
        """
        self.provider = None
        
        if provider_type == "auto":
            # Try to auto-detect available provider
            if os.getenv("OPENAI_API_KEY"):
                self.provider = OpenAIProvider()
                print("🤖 Using OpenAI for AI processing")
            elif os.getenv("ANTHROPIC_API_KEY"):
                self.provider = AnthropicProvider()
                print("🤖 Using Anthropic Claude for AI processing")
            else:
                print("🤖 No API keys found, using mock provider for testing")
                print("   To use real AI, set OPENAI_API_KEY or ANTHROPIC_API_KEY")
                self.provider = MockAIProvider()
        elif provider_type == "openai":
            self.provider = OpenAIProvider()
        elif provider_type == "anthropic":
            self.provider = AnthropicProvider()
        elif provider_type == "mock":
            self.provider = MockAIProvider()
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    def is_connected(self) -> bool:
        """Check if the AI provider is connected"""
        return self.provider.is_connected() if self.provider else False
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None,
                          temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate text completion"""
        if not self.provider:
            return "Error: No AI provider configured"
        return self.provider.generate_completion(prompt, system_prompt, temperature, max_tokens)
    
    def analyze_emotions(self, text: str) -> Dict:
        """Analyze emotions in the given text"""
        system_prompt = """You are an expert emotion analyst. Analyze the emotional content of the user's text.
Return a JSON response with the following structure:
{
    "primary_emotion": "the dominant emotion (joy, sadness, anger, fear, surprise, disgust, trust, anticipation, love, anxiety, etc.)",
    "emotions": {
        "emotion_name": confidence_score (0-100)
    },
    "intensity": "low/medium/high",
    "sentiment": "positive/negative/neutral"
}
Only return valid JSON, no additional text."""

        user_prompt = f"Analyze the emotions in this text:\n\n{text}"
        
        response = self.generate_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        try:
            # Parse JSON response
            emotion_data = json.loads(response)
            return emotion_data
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "primary_emotion": "neutral",
                "emotions": {"neutral": 50},
                "intensity": "medium",
                "sentiment": "neutral"
            }
    
    def generate_philosophical_note(self, primary_emotion: str, emotions: Dict[str, float], 
                                  text_context: str = "") -> str:
        """Generate a philosophical note related to the detected emotions"""
        system_prompt = """You are a philosophical writer who creates profound, poetic reflections on human emotions.
Write a short philosophical note (2-3 sentences) that captures the essence of the detected emotion.
Be poetic, introspective, and meaningful. Draw from philosophy, psychology, and wisdom traditions."""

        emotion_list = ", ".join([f"{k} ({v}%)" for k, v in emotions.items()])
        
        user_prompt = f"""Create a philosophical note for someone experiencing:
Primary emotion: {primary_emotion}
All emotions: {emotion_list}

Make it beautiful, profound, and comforting."""

        response = self.generate_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=200
        )
        
        return response.strip()
    
    def get_provider_info(self) -> str:
        """Get information about the current provider"""
        if isinstance(self.provider, OpenAIProvider):
            return f"OpenAI ({self.provider.model})"
        elif isinstance(self.provider, AnthropicProvider):
            return f"Anthropic ({self.provider.model})"
        elif isinstance(self.provider, MockAIProvider):
            return "Mock Provider (Testing Mode)"
        else:
            return "Unknown Provider"
