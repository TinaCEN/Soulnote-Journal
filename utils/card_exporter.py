"""
Card Exporter - Export posters for different social media platforms
"""

from PIL import Image
from pathlib import Path
from typing import Literal


PlatformType = Literal['instagram', 'twitter', 'square', 'story']


class CardExporter:
    """Export posters in different formats for social media"""
    
    # Social media dimensions
    DIMENSIONS = {
        'instagram': (1080, 1080),      # Square post
        'instagram_portrait': (1080, 1350),  # Portrait post
        'instagram_story': (1080, 1920),     # Story
        'twitter': (1200, 675),         # Twitter post
        'square': (1080, 1080),         # Generic square
        'story': (1080, 1920),          # Generic story
    }
    
    def __init__(self, output_dir: Path = Path('output')):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def export_for_platform(
        self,
        poster_path: Path,
        platform: str = 'instagram'
    ) -> Path:
        """
        Export poster optimized for specific platform
        
        Args:
            poster_path: Path to original poster
            platform: Target platform (instagram, twitter, square, story)
            
        Returns:
            Path to exported card
        """
        # Load original poster
        img = Image.open(poster_path)
        
        # Get target dimensions
        if platform == 'instagram':
            target_size = self.DIMENSIONS['instagram']
        elif platform == 'twitter':
            target_size = self.DIMENSIONS['twitter']
        elif platform == 'story':
            target_size = self.DIMENSIONS['story']
        else:
            target_size = self.DIMENSIONS['square']
        
        # Resize and crop to fit
        resized_img = self._resize_and_crop(img, target_size)
        
        # Generate output filename
        stem = poster_path.stem
        output_filename = f"{stem}_{platform}.png"
        output_path = self.output_dir / output_filename
        
        # Save with optimization
        resized_img.save(output_path, quality=95, optimize=True)
        
        return output_path
    
    def _resize_and_crop(
        self,
        img: Image.Image,
        target_size: tuple
    ) -> Image.Image:
        """
        Resize and crop image to target size maintaining aspect ratio
        
        Args:
            img: Source image
            target_size: (width, height) tuple
            
        Returns:
            Resized and cropped image
        """
        target_width, target_height = target_size
        target_ratio = target_width / target_height
        
        # Calculate current ratio
        current_width, current_height = img.size
        current_ratio = current_width / current_height
        
        if current_ratio > target_ratio:
            # Image is wider than target, fit to height
            new_height = target_height
            new_width = int(new_height * current_ratio)
        else:
            # Image is taller than target, fit to width
            new_width = target_width
            new_height = int(new_width / current_ratio)
        
        # Resize
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop to center
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        img = img.crop((left, top, right, bottom))
        
        return img
    
    def export_all_formats(self, poster_path: Path) -> dict:
        """
        Export poster in all supported formats
        
        Args:
            poster_path: Path to original poster
            
        Returns:
            Dictionary mapping platform to output path
        """
        exports = {}
        
        for platform in ['instagram', 'twitter', 'square', 'story']:
            try:
                output_path = self.export_for_platform(poster_path, platform)
                exports[platform] = output_path
            except Exception as e:
                print(f"Error exporting for {platform}: {e}")
        
        return exports
