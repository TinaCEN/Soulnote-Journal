#!/usr/bin/env python3
"""
简化的Soulnote测试服务器
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import sys
import os

from models.online_ai_client import OnlineAIClient

app = Flask(__name__)
CORS(app)

# 初始化AI客户端
ai_client = OnlineAIClient()

# 简单的HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Soulnote - 情感日记</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        textarea { width: 100%; height: 100px; margin: 10px 0; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
        .result { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <h1>🌟 Soulnote - AI情感日记</h1>
    
    <div class="container">
        <h3>📝 文本情感分析</h3>
        <textarea id="inputText" placeholder="输入你的想法和感受..."></textarea>
        <button onclick="analyzeText()">分析情感</button>
        <div id="result"></div>
    </div>

    <div class="container">
        <h3>🔧 系统状态</h3>
        <button onclick="checkHealth()">检查状态</button>
        <div id="healthResult"></div>
    </div>

    <script>
        async function analyzeText() {
            const text = document.getElementById('inputText').value;
            if (!text.trim()) {
                alert('请输入一些文字');
                return;
            }

            try {
                const response = await fetch('/api/analyze/text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const result = await response.json();
                document.getElementById('result').innerHTML = `
                    <div class="result">
                        <h4>🎭 主要情感: ${result.primary_emotion}</h4>
                        <p><strong>📊 情感分析:</strong> ${JSON.stringify(result.emotions, null, 2)}</p>
                        <p><strong>📖 哲学思考:</strong> ${result.philosophical_note}</p>
                        <p><strong>🕒 时间:</strong> ${new Date(result.timestamp).toLocaleString()}</p>
                    </div>
                `;
            } catch (error) {
                document.getElementById('result').innerHTML = `<div class="result" style="border-color: red;">❌ 错误: ${error.message}</div>`;
            }
        }

        async function checkHealth() {
            try {
                const response = await fetch('/api/health');
                const result = await response.json();
                document.getElementById('healthResult').innerHTML = `
                    <div class="result">
                        <p><strong>状态:</strong> ${result.status}</p>
                        <p><strong>AI提供商:</strong> ${result.ai_provider}</p>
                        <p><strong>连接状态:</strong> ${result.ai_connected ? '✅ 已连接' : '❌ 未连接'}</p>
                    </div>
                `;
            } catch (error) {
                document.getElementById('healthResult').innerHTML = `<div class="result" style="border-color: red;">❌ 错误: ${error.message}</div>`;
            }
        }

        // 页面加载时检查状态
        window.onload = checkHealth;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'ai_provider': ai_client.get_provider_info(),
        'ai_connected': ai_client.is_connected()
    })

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # 分析情感
        emotion_data = ai_client.analyze_emotions(text)
        
        # 生成哲学思考
        philosophical_note = ai_client.generate_philosophical_note(
            emotion_data.get('primary_emotion', 'neutral'),
            emotion_data.get('emotions', {})
        )
        
        return jsonify({
            'text': text,
            'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
            'emotions': emotion_data.get('emotions', {}),
            'philosophical_note': philosophical_note,
            'timestamp': '2025-11-04T16:00:00'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 启动Soulnote简化版服务器...")
    print(f"🤖 AI提供商: {ai_client.get_provider_info()}")
    print("🌟 访问: http://localhost:5003")
    app.run(debug=True, host='0.0.0.0', port=5003)
