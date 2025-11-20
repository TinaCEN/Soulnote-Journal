"""
LM Studio Client - Interface with local LLM
"""

import requests
import json
from typing import Dict, Optional


class LMStudioClient:
    """Client for communicating with LM Studio local LLM server"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.chat_endpoint = f"{base_url}/chat/completions"
        
    def is_connected(self) -> bool:
        """Check if LM Studio server is running"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate text completion from LM Studio
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Generated text response
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with LM Studio: {e}")
            return ""
    
    def analyze_emotions(self, text: str) -> Dict:
        """
        Analyze emotions in the given text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with emotion analysis
        """
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
    
    def generate_philosophical_note(
        self,
        primary_emotion: str,
        emotions: Dict[str, float],
        text_context: str = ""
    ) -> str:
        """
        Generate a philosophical note related to the detected emotions
        
        Args:
            primary_emotion: The primary detected emotion
            emotions: Dictionary of emotions with confidence scores
            text_context: Original text for context
            
        Returns:
            Philosophical note as string
        """
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
