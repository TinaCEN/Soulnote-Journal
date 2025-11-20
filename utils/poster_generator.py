"""
Poster Generator - Create artistic visual posters
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import colorsys


class PosterGenerator:
    """Generate artistic posters with emotion-based visuals"""
    
    # Emotion color mappings (HSV)
    EMOTION_COLORS = {
        'joy': (45, 0.8, 0.95),      # Yellow
        'happiness': (45, 0.8, 0.95),
        'sadness': (220, 0.6, 0.6),  # Blue
        'anger': (0, 0.9, 0.8),      # Red
        'fear': (270, 0.5, 0.5),     # Purple
        'surprise': (30, 0.9, 0.95), # Orange
        'disgust': (120, 0.5, 0.5),  # Green
        'love': (330, 0.8, 0.9),     # Pink
        'anxiety': (280, 0.6, 0.6),  # Violet
        'peace': (180, 0.5, 0.8),    # Cyan
        # Use a soft periwinkle for neutral to avoid gray
        'neutral': (225, 0.28, 0.94),
        'trust': (200, 0.6, 0.8),    # Light Blue
        'anticipation': (60, 0.7, 0.85), # Yellow-Green
    }
    
    def __init__(self, output_dir: Path = Path('output')):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        
        # Poster dimensions
        self.width = 1080
        self.height = 1350  # Instagram portrait ratio
    
    def _get_emotion_color(self, emotion: str) -> tuple:
        """Get RGB color for emotion"""
        # Default fallback aligns with non-gray neutral
        hsv = self.EMOTION_COLORS.get(emotion.lower(), (225, 0.28, 0.94))
        rgb = colorsys.hsv_to_rgb(hsv[0]/360, hsv[1], hsv[2])
        return tuple(int(c * 255) for c in rgb)
    
    def _create_gradient_background(
        self,
        primary_color: tuple,
        secondary_color: tuple
    ) -> Image.Image:
        """Create gradient background"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(primary_color[0] * (1 - ratio) + secondary_color[0] * ratio)
            g = int(primary_color[1] * (1 - ratio) + secondary_color[1] * ratio)
            b = int(primary_color[2] * (1 - ratio) + secondary_color[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
    
    def _draw_waveform(
        self,
        img: Image.Image,
        waveform_data: List[float],
        color: tuple,
        y_position: int = None
    ):
        """Draw sonic waveform visualization"""
        if not waveform_data:
            return
        
        draw = ImageDraw.Draw(img)
        
        if y_position is None:
            y_position = self.height // 2
        
        # Calculate spacing
        point_spacing = self.width / len(waveform_data)
        max_amplitude = 150  # Maximum wave height
        
        # Draw waveform as connected lines
        points = []
        for i, amplitude in enumerate(waveform_data):
            x = int(i * point_spacing)
            y = int(y_position + (amplitude - 0.5) * max_amplitude)
            points.append((x, y))
        
        # Draw the waveform
        if len(points) > 1:
            draw.line(points, fill=color, width=3)
            
            # Add glow effect
            for offset in [5, 10, 15]:
                alpha_color = color + (int(255 * (1 - offset/20)),)
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    draw.line(
                        [(x1, y1 - offset), (x2, y2 - offset)],
                        fill=alpha_color[:3],
                        width=2
                    )
                    draw.line(
                        [(x1, y1 + offset), (x2, y2 + offset)],
                        fill=alpha_color[:3],
                        width=2
                    )
    
    def _add_text_overlay(
        self,
        img: Image.Image,
        text: str,
        philosophical_note: str,
        primary_emotion: str
    ):
        """Add text overlays to poster"""
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            quote_font = ImageFont.truetype("arial.ttf", 32)
            emotion_font = ImageFont.truetype("arial.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            quote_font = ImageFont.load_default()
            emotion_font = ImageFont.load_default()
        
        # Add emotion label at top
        emotion_text = primary_emotion.upper()
        bbox = draw.textbbox((0, 0), emotion_text, font=emotion_font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        
        # Add shadow
        draw.text((x + 2, 52), emotion_text, fill=(0, 0, 0, 180), font=emotion_font)
        draw.text((x, 50), emotion_text, fill=(255, 255, 255), font=emotion_font)
        
        # Add philosophical note at bottom
        if philosophical_note:
            # Word wrap
            max_width = self.width - 100
            words = philosophical_note.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                bbox = draw.textbbox((0, 0), ' '.join(current_line), font=quote_font)
                if bbox[2] - bbox[0] > max_width:
                    if len(current_line) > 1:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw lines
            y_start = self.height - 200
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=quote_font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                y = y_start + i * 40
                
                # Shadow
                draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 180), font=quote_font)
                draw.text((x, y), line, fill=(255, 255, 255), font=quote_font)
    
    def create_poster(
        self,
        text: str,
        primary_emotion: str,
        emotions: Dict[str, float],
        philosophical_note: str,
        waveform_data: Optional[List[float]] = None,
        audio_filename: Optional[str] = None
    ) -> Path:
        """
        Create complete artistic poster
        
        Args:
            text: Original journal text
            primary_emotion: Primary detected emotion
            emotions: All detected emotions with scores
            philosophical_note: Generated philosophical note
            waveform_data: Audio waveform data (optional)
            audio_filename: Original audio filename (optional)
            
        Returns:
            Path to generated poster
        """
        # Get colors for primary and secondary emotions
        primary_color = self._get_emotion_color(primary_emotion)
        
        # Get secondary emotion if exists
        sorted_emotions = sorted(
            emotions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        secondary_emotion = sorted_emotions[1][0] if len(sorted_emotions) > 1 else primary_emotion
        secondary_color = self._get_emotion_color(secondary_emotion)
        
        # Create gradient background
        img = self._create_gradient_background(primary_color, secondary_color)
        
        # Add waveform if available
        if waveform_data:
            wave_color = tuple(int(c * 0.8) for c in primary_color)  # Slightly darker
            self._draw_waveform(img, waveform_data, wave_color)
        
        # Add artistic elements (circles, shapes)
        self._add_artistic_elements(img, primary_color, secondary_color)
        
        # Add text overlays
        self._add_text_overlay(img, text, philosophical_note, primary_emotion)
        
        # Apply subtle blur for artistic effect
        # img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Save poster
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poster_{primary_emotion}_{timestamp}.png"
        output_path = self.output_dir / filename
        
        img.save(output_path, quality=95)
        
        return output_path
    
    def _add_artistic_elements(
        self,
        img: Image.Image,
        primary_color: tuple,
        secondary_color: tuple
    ):
        """Add decorative artistic elements"""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Add semi-transparent circles
        for i in range(5):
            size = np.random.randint(100, 300)
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            
            color = primary_color if i % 2 == 0 else secondary_color
            alpha = np.random.randint(20, 50)
            
            draw.ellipse(
                [x - size//2, y - size//2, x + size//2, y + size//2],
                fill=color + (alpha,),
                outline=None
            )
