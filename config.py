"""
Configuration management for Soulnote
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for Soulnote application"""
    
    def __init__(self):
        # Load environment variables from .env file if it exists
        self._load_env_file()
        
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    # AI Provider Settings
    @property
    def ai_provider(self) -> str:
        """Get AI provider type"""
        return os.getenv('AI_PROVIDER', 'mock')
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def openai_model(self) -> str:
        """Get OpenAI model"""
        return os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Get Anthropic API key"""
        return os.getenv('ANTHROPIC_API_KEY')
    
    @property
    def anthropic_model(self) -> str:
        """Get Anthropic model"""
        return os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    
    # Server Settings
    @property
    def server_port(self) -> int:
        """Get server port"""
        return int(os.getenv('SERVER_PORT', 5001))
    
    @property
    def debug_mode(self) -> bool:
        """Get debug mode"""
        return os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Audio Settings
    @property
    def max_audio_length(self) -> int:
        """Get maximum audio length in seconds"""
        return int(os.getenv('MAX_AUDIO_LENGTH', 300))
    
    @property
    def supported_audio_formats(self) -> list:
        """Get supported audio formats"""
        formats = os.getenv('SUPPORTED_AUDIO_FORMATS', 'wav,mp3,webm,m4a')
        return [f.strip() for f in formats.split(',')]
    
    # Image Settings
    @property
    def poster_width(self) -> int:
        """Get poster width"""
        return int(os.getenv('POSTER_WIDTH', 1080))
    
    @property
    def poster_height(self) -> int:
        """Get poster height"""
        return int(os.getenv('POSTER_HEIGHT', 1350))
    
    @property
    def card_formats(self) -> list:
        """Get supported card formats"""
        formats = os.getenv('CARD_FORMATS', 'instagram,twitter,square')
        return [f.strip() for f in formats.split(',')]


# Global config instance
config = Config()
