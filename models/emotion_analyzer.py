"""
Emotion Analyzer - Main emotion analysis logic
"""

from datetime import datetime
from typing import Dict
from models.online_ai_client import OnlineAIClient


class EmotionAnalyzer:
    """Analyzes emotions from text using online AI services"""
    
    def __init__(self, ai_client: OnlineAIClient):
        self.ai_client = ai_client
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze emotions in text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with emotion analysis results
        """
        # Get emotion analysis from online AI
        emotion_data = self.ai_client.analyze_emotions(text)
        
        return {
            'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
            'emotions': emotion_data.get('emotions', {}),
            'intensity': emotion_data.get('intensity', 'medium'),
            'sentiment': emotion_data.get('sentiment', 'neutral'),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_philosophical_note(
        self,
        primary_emotion: str,
        emotions: Dict[str, float]
    ) -> str:
        """
        Generate philosophical note based on emotions
        
        Args:
            primary_emotion: Primary detected emotion
            emotions: Dictionary of all emotions
            
        Returns:
            Philosophical note as string
        """
        return self.ai_client.generate_philosophical_note(
            primary_emotion=primary_emotion,
            emotions=emotions
        )
