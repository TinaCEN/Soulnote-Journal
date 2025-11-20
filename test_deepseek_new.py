#!/usr/bin/env python3
"""
Test DeepSeek API connection with new client
"""

import os
import sys
sys.path.insert(0, '/Users/cenyoushan/Desktop/Soulnote.v1')

from models.deepseek_client_new import DeepSeekProvider, DeepSeekRealtimeClient, EnhancedOnlineAIClient

def test_deepseek_connection():
    """Test DeepSeek API connection"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return False
    
    print(f"🔑 Using API Key: {api_key[:8]}...")
    
    # Test basic provider
    print("\n1. Testing DeepSeekProvider...")
    provider = DeepSeekProvider(api_key)
    
    if provider.is_connected():
        print("✅ DeepSeek connection successful!")
        
        # Test simple completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Say hello in Chinese"}
        ]
        
        response = provider.generate_completion(messages, max_tokens=50)
        print(f"📝 Response: {response}")
        
        # Test emotion analysis
        print("\n2. Testing emotion analysis...")
        realtime_client = DeepSeekRealtimeClient(api_key)
        emotion_result = realtime_client.analyze_emotions_realtime("我今天很开心，因为工作进展顺利")
        print(f"😊 Emotion Analysis: {emotion_result}")
        
        # Test philosophical note
        print("\n3. Testing philosophical note...")
        philosophical_note = realtime_client.generate_philosophical_note_realtime(
            emotion_result.get('primary_emotion', '快乐'),
            emotion_result.get('emotions', {}),
            "我今天很开心，因为工作进展顺利"
        )
        print(f"🧘 Philosophical Note: {philosophical_note}")
        
        return True
    else:
        print("❌ DeepSeek connection failed")
        return False

if __name__ == "__main__":
    # Set API key
    os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')
    
    print("🧠 Testing DeepSeek API with OpenAI SDK...")
    success = test_deepseek_connection()
    
    if success:
        print("\n🎉 All tests passed! DeepSeek integration is working.")
    else:
        print("\n❌ Tests failed. Please check your API key and connection.")
