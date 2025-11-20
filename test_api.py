#!/usr/bin/env python3
"""
Simple test script for Soulnote API
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5002"
    
    print("🧪 Testing Soulnote API...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
        return
    
    # Test text analysis
    try:
        data = {
            "text": "I feel really happy today! The weather is beautiful and I'm excited about my new project."
        }
        response = requests.post(f"{base_url}/api/analyze/text", json=data, timeout=10)
        print(f"✅ Text Analysis: {response.status_code}")
        result = response.json()
        print(f"🎭 Primary Emotion: {result.get('primary_emotion')}")
        print(f"📝 Philosophical Note: {result.get('philosophical_note')}")
    except Exception as e:
        print(f"❌ Text Analysis failed: {e}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_api()
