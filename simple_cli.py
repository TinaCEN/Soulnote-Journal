"""
Simple Command-Line Version of Soulnote
Run this directly in VS Code terminal - NO WEB BROWSER NEEDED!

Usage:
    1. Make sure LM Studio is running
    2. In VS Code terminal: python simple_cli.py
    3. Type your feelings and press Enter twice
    4. Get your emotion analysis and poster!
"""

import sys
from pathlib import Path

# Add project to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from models.lmstudio_client import LMStudioClient
from models.emotion_analyzer import EmotionAnalyzer
from utils.poster_generator import PosterGenerator


def print_header():
    """Print a nice header"""
    print("\n" + "="*60)
    print(" " * 15 + "🎨 SOULNOTE - CLI VERSION 🎨")
    print("="*60 + "\n")


def get_user_input():
    """Get text from user"""
    print("📝 How are you feeling today?")
    print("   (Type your thoughts, then press Enter TWICE when done)\n")
    print("→ ", end="")
    
    lines = []
    empty_count = 0
    
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 1 and lines:  # One empty line ends input
                break
        else:
            empty_count = 0
            lines.append(line)
            print("→ ", end="")
    
    return "\n".join(lines)


def display_emotions(result):
    """Display emotion analysis in a pretty way"""
    print("\n" + "="*60)
    print("📊 EMOTION ANALYSIS")
    print("="*60 + "\n")
    
    # Primary emotion with emoji
    emotion_emojis = {
        'joy': '😊', 'happiness': '😊', 'sadness': '😢', 
        'anger': '😠', 'fear': '😰', 'love': '❤️',
        'anxiety': '😟', 'peace': '😌', 'neutral': '😐'
    }
    emoji = emotion_emojis.get(result['primary_emotion'], '🎭')
    
    print(f"🎯 Primary Emotion: {emoji} {result['primary_emotion'].upper()}")
    print(f"📈 Intensity: {result['intensity']}")
    print(f"💭 Sentiment: {result['sentiment']}\n")
    
    print("All detected emotions:")
    print("-" * 60)
    
    # Sort by score
    sorted_emotions = sorted(
        result['emotions'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for emotion, score in sorted_emotions:
        # Create progress bar
        bar_length = int(score / 2)  # 50 chars max
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {emotion:15s} │ {bar} │ {score:3d}%")


def display_philosophy(note):
    """Display philosophical note"""
    print("\n" + "="*60)
    print("📖 PHILOSOPHICAL REFLECTION")
    print("="*60 + "\n")
    
    # Wrap text nicely
    words = note.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > 55:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    for line in lines:
        print(f"  {line}")
    print()


def main():
    """Main function"""
    try:
        print_header()
        
        # Initialize
        print("🔌 Connecting to LM Studio...", end=" ")
        lm_client = LMStudioClient()
        
        if not lm_client.is_connected():
            print("❌ FAILED\n")
            print("Error: LM Studio is not running!")
            print("\nPlease:")
            print("  1. Open LM Studio")
            print("  2. Load a model")
            print("  3. Start the local server")
            print("  4. Try again\n")
            return
        
        print("✅ Connected!\n")
        
        analyzer = EmotionAnalyzer(lm_client)
        poster_gen = PosterGenerator()
        
        # Get input
        text = get_user_input()
        
        if not text.strip():
            print("\n⚠️  No text entered. Goodbye! 👋\n")
            return
        
        # Analyze
        print("\n🧠 Analyzing your emotions...", end=" ")
        result = analyzer.analyze_text(text)
        print("✅ Done!")
        
        # Display results
        display_emotions(result)
        
        # Generate philosophy
        print("\n💭 Generating philosophical note...", end=" ")
        note = analyzer.generate_philosophical_note(
            result['primary_emotion'],
            result['emotions']
        )
        print("✅ Done!")
        
        display_philosophy(note)
        
        # Generate poster
        print("="*60)
        print("🎨 Creating your artistic poster...", end=" ")
        
        poster_path = poster_gen.create_poster(
            text=text,
            primary_emotion=result['primary_emotion'],
            emotions=result['emotions'],
            philosophical_note=note,
            waveform_data=None,
            audio_filename=None
        )
        
        print("✅ Done!")
        print("="*60 + "\n")
        
        print(f"📁 Poster saved to: {poster_path.name}")
        print(f"📂 Location: {poster_path.parent.absolute()}\n")
        
        print("="*60)
        print(" " * 15 + "✨ Session Complete! ✨")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nMake sure:")
        print("  • LM Studio is running")
        print("  • The local server is started")
        print("  • A model is loaded\n")


if __name__ == "__main__":
    main()
