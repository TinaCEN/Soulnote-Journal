"""
Simple Command-Line Version of Soulnote
Run this directly in VS Code terminal!
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from models.lmstudio_client import LMStudioClient
from models.emotion_analyzer import EmotionAnalyzer
from utils.poster_generator import PosterGenerator

def main():
    print("\n" + "="*50)
    print("🎨 Soulnote - Simple CLI Version")
    print("="*50 + "\n")
    
    # Initialize components
    print("Connecting to LM Studio...")
    lm_client = LMStudioClient()
    
    if not lm_client.is_connected():
        print("❌ Error: LM Studio is not running!")
        print("Please start LM Studio and the local server first.")
        return
    
    print("✅ Connected to LM Studio!\n")
    
    analyzer = EmotionAnalyzer(lm_client)
    poster_gen = PosterGenerator()
    
    # Get user input
    print("How are you feeling today?")
    print("(Type your thoughts and press Enter twice when done)\n")
    
    lines = []
    while True:
        line = input()
        if line == "":
            if lines:  # If we have content and get empty line, we're done
                break
        else:
            lines.append(line)
    
    text = "\n".join(lines)
    
    if not text.strip():
        print("No text entered. Goodbye!")
        return
    
    # Analyze emotions
    print("\n🧠 Analyzing your emotions...")
    result = analyzer.analyze_text(text)
    
    # Display results
    print("\n" + "="*50)
    print("📊 EMOTION ANALYSIS RESULTS")
    print("="*50)
    print(f"\n🎯 Primary Emotion: {result['primary_emotion'].upper()}")
    print(f"📈 Intensity: {result['intensity']}")
    print(f"💭 Sentiment: {result['sentiment']}\n")
    
    print("All detected emotions:")
    for emotion, score in result['emotions'].items():
        bar = "█" * int(score / 5)
        print(f"  {emotion:15s} {score:3d}% {bar}")
    
    # Generate philosophical note
    print("\n" + "="*50)
    print("📖 PHILOSOPHICAL REFLECTION")
    print("="*50)
    note = analyzer.generate_philosophical_note(
        result['primary_emotion'],
        result['emotions']
    )
    print(f"\n{note}\n")
    
    # Generate poster
    print("="*50)
    print("🎨 Generating your poster...")
    poster_path = poster_gen.create_poster(
        text=text,
        primary_emotion=result['primary_emotion'],
        emotions=result['emotions'],
        philosophical_note=note,
        waveform_data=None,
        audio_filename=None
    )
    
    print(f"✅ Poster saved to: {poster_path}")
    print("\nYou can find your poster in the 'output' folder!")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure LM Studio is running!")
