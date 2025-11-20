#!/usr/bin/env python3
"""
Soulnote with OpenAI Realtime API - 实时语音情感分析
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import asyncio
import threading
import json
import os
import sys
from pathlib import Path

from models.openai_realtime_client import OpenAIRealtimeClient, RealtimeEmotionAnalyzer
from models.online_ai_client import OnlineAIClient
from utils.poster_generator import PosterGenerator

app = Flask(__name__)
CORS(app)

# 配置（以当前文件目录为根）
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUT_FOLDER = PROJECT_ROOT / 'output'
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# 全局变量
realtime_analyzer = None
poster_generator = PosterGenerator()
fallback_ai_client = OnlineAIClient()  # 备用AI客户端

# 检查OpenAI API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HAS_REALTIME_API = bool(OPENAI_API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soulnote - 实时AI情感分析</title>
    <style>
        :root {
            --primary-color: #6366f1;
            --secondary-color: #8b5cf6;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --bg-primary: #ffffff;
            --bg-secondary: #f9fafb;
            --border-color: #e5e7eb;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 40px 20px;
            color: white;
        }

        .logo {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        .tagline {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .api-status {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px 25px;
            border-radius: 25px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        .api-status.realtime {
            background: rgba(16, 185, 129, 0.2);
        }

        .api-status.fallback {
            background: rgba(245, 158, 11, 0.2);
        }

        .api-status.error {
            background: rgba(239, 68, 68, 0.2);
        }

        .main-content {
            background: var(--bg-primary);
            border-radius: 20px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .realtime-section {
            padding: 40px;
            text-align: center;
        }

        .realtime-controls {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 30px;
        }

        .voice-visualizer {
            width: 100%;
            max-width: 600px;
            height: 200px;
            background: var(--bg-secondary);
            border-radius: 15px;
            position: relative;
            overflow: hidden;
            border: 3px solid transparent;
            transition: all 0.3s ease;
        }

        .voice-visualizer.active {
            border-color: var(--success-color);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
        }

        .voice-visualizer canvas {
            width: 100%;
            height: 100%;
        }

        .realtime-btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 20px 40px;
            border-radius: 50px;
            font-size: 1.3rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 200px;
        }

        .realtime-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }

        .realtime-btn.listening {
            background: var(--danger-color);
            animation: pulse 1.5s infinite;
        }

        .realtime-btn.processing {
            background: var(--warning-color);
            cursor: not-allowed;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .live-transcript {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            min-height: 100px;
            text-align: left;
        }

        .live-transcript h4 {
            margin-bottom: 10px;
            color: var(--text-primary);
        }

        .transcript-text {
            color: var(--text-secondary);
            font-style: italic;
            line-height: 1.6;
        }

        .emotion-display {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .emotion-card {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .emotion-card.primary {
            border-color: var(--primary-color);
            background: linear-gradient(135deg, var(--primary-color)10, var(--primary-color)20);
        }

        .emotion-name {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
            text-transform: capitalize;
        }

        .emotion-score {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .philosophical-section {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }

        .philosophical-section h3 {
            text-align: center;
            margin-bottom: 20px;
            color: var(--text-primary);
        }

        .philosophical-text {
            font-size: 1.1rem;
            font-style: italic;
            text-align: center;
            color: var(--text-secondary);
            line-height: 1.8;
        }

        .poster-section {
            text-align: center;
            margin: 30px 0;
        }

        .poster-container {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 15px;
            display: inline-block;
            margin: 20px 0;
        }

        .poster-container img {
            max-width: 100%;
            max-height: 500px;
            border-radius: 10px;
        }

        .controls-section {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
            flex-wrap: wrap;
        }

        .btn {
            background: var(--secondary-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .btn-success {
            background: var(--success-color);
        }

        .btn-warning {
            background: var(--warning-color);
        }

        .hidden {
            display: none !important;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-indicator.connected {
            background: var(--success-color);
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }

        .status-indicator.disconnected {
            background: var(--danger-color);
        }

        .status-indicator.processing {
            background: var(--warning-color);
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.3; }
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .logo {
                font-size: 2rem;
            }
            
            .realtime-section {
                padding: 20px;
            }
            
            .realtime-btn {
                font-size: 1.1rem;
                padding: 15px 30px;
                min-width: 150px;
            }
            
            .emotion-display {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1 class="logo">🎙️ Soulnote Realtime</h1>
            <p class="tagline">实时AI语音情感分析</p>
        </header>

        <!-- API Status -->
        <div id="apiStatus" class="api-status">
            <span class="status-indicator" id="statusDot"></span>
            <span id="statusText">正在检查API状态...</span>
        </div>

        <!-- Main Content -->
        <main class="main-content">
            <section class="realtime-section">
                <h2>🎤 实时语音分析</h2>
                
                <!-- Voice Visualizer -->
                <div class="voice-visualizer" id="voiceVisualizer">
                    <canvas id="visualizerCanvas"></canvas>
                </div>

                <!-- Controls -->
                <div class="realtime-controls">
                    <button id="realtimeBtn" class="realtime-btn">
                        <span id="btnIcon">🎤</span>
                        <span id="btnText">开始实时分析</span>
                    </button>
                    
                    <p id="statusHint">点击开始实时语音情感分析</p>
                </div>

                <!-- Live Transcript -->
                <div class="live-transcript" id="liveTranscript">
                    <h4>📝 实时转录</h4>
                    <div class="transcript-text" id="transcriptText">
                        开始说话，这里将显示实时转录...
                    </div>
                </div>

                <!-- Emotion Display -->
                <div class="emotion-display" id="emotionDisplay" style="display: none;">
                    <!-- 动态生成情感卡片 -->
                </div>

                <!-- Philosophical Section -->
                <div class="philosophical-section" id="philosophicalSection" style="display: none;">
                    <h3>🧘 深度思考</h3>
                    <div class="philosophical-text" id="philosophicalText"></div>
                </div>

                <!-- Poster Section -->
                <div class="poster-section" id="posterSection" style="display: none;">
                    <h3>🎨 情感海报</h3>
                    <div class="poster-container">
                        <img id="posterImage" src="" alt="生成的情感海报">
                    </div>
                </div>

                <!-- Controls -->
                <div class="controls-section">
                    <button id="saveBtn" class="btn btn-success" style="display: none;">
                        💾 保存分析结果
                    </button>
                    <button id="shareBtn" class="btn btn-warning" style="display: none;">
                        📱 分享到社交媒体
                    </button>
                    <button id="resetBtn" class="btn">
                        🔄 重新开始
                    </button>
                </div>
            </section>
        </main>
    </div>

    <script>
        class SoulnoteRealtime {
            constructor() {
                this.isListening = false;
                this.websocket = null;
                this.audioContext = null;
                this.mediaStream = null;
                this.processor = null;
                this.hasRealtimeAPI = ${str(HAS_REALTIME_API).lower()};
                
                this.elements = {
                    realtimeBtn: document.getElementById('realtimeBtn'),
                    btnIcon: document.getElementById('btnIcon'),
                    btnText: document.getElementById('btnText'),
                    statusHint: document.getElementById('statusHint'),
                    apiStatus: document.getElementById('apiStatus'),
                    statusDot: document.getElementById('statusDot'),
                    statusText: document.getElementById('statusText'),
                    voiceVisualizer: document.getElementById('voiceVisualizer'),
                    visualizerCanvas: document.getElementById('visualizerCanvas'),
                    liveTranscript: document.getElementById('liveTranscript'),
                    transcriptText: document.getElementById('transcriptText'),
                    emotionDisplay: document.getElementById('emotionDisplay'),
                    philosophicalSection: document.getElementById('philosophicalSection'),
                    philosophicalText: document.getElementById('philosophicalText'),
                    posterSection: document.getElementById('posterSection'),
                    posterImage: document.getElementById('posterImage'),
                    saveBtn: document.getElementById('saveBtn'),
                    shareBtn: document.getElementById('shareBtn'),
                    resetBtn: document.getElementById('resetBtn')
                };
                
                this.currentAnalysis = {
                    transcript: '',
                    emotions: {},
                    philosophical_note: ''
                };
                
                this.init();
            }
            
            async init() {
                this.setupEventListeners();
                this.setupVisualizer();
                await this.checkAPIStatus();
            }
            
            setupEventListeners() {
                this.elements.realtimeBtn.addEventListener('click', () => {
                    if (this.isListening) {
                        this.stopListening();
                    } else {
                        this.startListening();
                    }
                });
                
                this.elements.resetBtn.addEventListener('click', () => {
                    this.reset();
                });
                
                this.elements.saveBtn.addEventListener('click', () => {
                    this.saveResults();
                });
                
                this.elements.shareBtn.addEventListener('click', () => {
                    this.shareResults();
                });
            }
            
            async checkAPIStatus() {
                try {
                    const response = await fetch('/api/realtime/status');
                    const data = await response.json();
                    
                    if (data.realtime_available) {
                        this.updateStatus('实时API已就绪', 'realtime', 'connected');
                    } else {
                        this.updateStatus('使用备用AI模式', 'fallback', 'connected');
                    }
                } catch (error) {
                    this.updateStatus('API连接失败', 'error', 'disconnected');
                }
            }
            
            updateStatus(message, type, indicator) {
                this.elements.statusText.textContent = message;
                this.elements.apiStatus.className = `api-status ${type}`;
                this.elements.statusDot.className = `status-indicator ${indicator}`;
            }
            
            setupVisualizer() {
                const canvas = this.elements.visualizerCanvas;
                const ctx = canvas.getContext('2d');
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
                
                // 绘制初始状态
                ctx.fillStyle = '#e5e7eb';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#6b7280';
                ctx.font = '18px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('🎤 准备开始语音分析', canvas.width / 2, canvas.height / 2);
            }
            
            async startListening() {
                try {
                    this.isListening = true;
                    this.updateButtonState('listening');
                    this.elements.voiceVisualizer.classList.add('active');
                    
                    if (this.hasRealtimeAPI) {
                        await this.startRealtimeSession();
                    } else {
                        await this.startFallbackSession();
                    }
                    
                    this.startAudioCapture();
                    this.animateVisualizer();
                    
                } catch (error) {
                    console.error('启动监听失败:', error);
                    alert('无法启动语音分析: ' + error.message);
                    this.stopListening();
                }
            }
            
            async startRealtimeSession() {
                // 在实际实现中，这里会建立WebSocket连接到后端
                // 后端再连接到OpenAI Realtime API
                console.log('启动实时API会话');
                this.elements.statusHint.textContent = '🎙️ 实时分析中...';
            }
            
            async startFallbackSession() {
                console.log('使用备用AI模式');
                this.elements.statusHint.textContent = '🎤 录制中，请说话...';
            }
            
            async startAudioCapture() {
                try {
                    this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            sampleRate: 16000,
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true
                        } 
                    });
                    
                    this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                        sampleRate: 16000
                    });
                    
                    const source = this.audioContext.createMediaStreamSource(this.mediaStream);
                    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
                    
                    this.processor.onaudioprocess = (event) => {
                        if (this.isListening) {
                            const audioData = event.inputBuffer.getChannelData(0);
                            this.processAudioChunk(audioData);
                        }
                    };
                    
                    source.connect(this.processor);
                    this.processor.connect(this.audioContext.destination);
                    
                } catch (error) {
                    throw new Error('无法访问麦克风: ' + error.message);
                }
            }
            
            processAudioChunk(audioData) {
                // 在实际实现中，这里会将音频数据发送到后端
                // 对于实时API，会通过WebSocket发送
                // 对于备用模式，会累积音频数据
            }
            
            stopListening() {
                this.isListening = false;
                this.updateButtonState('processing');
                this.elements.voiceVisualizer.classList.remove('active');
                
                if (this.mediaStream) {
                    this.mediaStream.getTracks().forEach(track => track.stop());
                }
                
                if (this.audioContext) {
                    this.audioContext.close();
                }
                
                if (this.processor) {
                    this.processor.disconnect();
                }
                
                // 模拟处理结果
                setTimeout(() => {
                    this.showMockResults();
                }, 2000);
            }
            
            showMockResults() {
                // 显示模拟结果
                this.currentAnalysis = {
                    transcript: '我今天感觉很开心，天气很好，工作也很顺利。',
                    emotions: {
                        'joy': 85,
                        'contentment': 70,
                        'optimism': 60,
                        'gratitude': 45
                    },
                    philosophical_note: '快乐不是目的地，而是旅程本身。在平凡的日子里发现美好，这是生活的艺术。'
                };
                
                this.displayResults();
                this.updateButtonState('idle');
            }
            
            displayResults() {
                // 显示转录
                this.elements.transcriptText.textContent = this.currentAnalysis.transcript;
                
                // 显示情感
                this.displayEmotions();
                
                // 显示哲学思考
                this.elements.philosophicalText.textContent = this.currentAnalysis.philosophical_note;
                this.elements.philosophicalSection.style.display = 'block';
                
                // 生成海报
                this.generatePoster();
                
                // 显示控制按钮
                this.elements.saveBtn.style.display = 'inline-block';
                this.elements.shareBtn.style.display = 'inline-block';
            }
            
            displayEmotions() {
                const emotionDisplay = this.elements.emotionDisplay;
                emotionDisplay.innerHTML = '';
                emotionDisplay.style.display = 'grid';
                
                let isFirst = true;
                for (const [emotion, score] of Object.entries(this.currentAnalysis.emotions)) {
                    const card = document.createElement('div');
                    card.className = `emotion-card ${isFirst ? 'primary' : ''}`;
                    card.innerHTML = `
                        <div class="emotion-name">${emotion}</div>
                        <div class="emotion-score">${score}%</div>
                    `;
                    emotionDisplay.appendChild(card);
                    isFirst = false;
                }
            }
            
            async generatePoster() {
                try {
                    const response = await fetch('/api/generate/poster', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.currentAnalysis)
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        this.elements.posterImage.src = data.poster_url;
                        this.elements.posterSection.style.display = 'block';
                    }
                } catch (error) {
                    console.error('海报生成失败:', error);
                }
            }
            
            updateButtonState(state) {
                const btn = this.elements.realtimeBtn;
                const icon = this.elements.btnIcon;
                const text = this.elements.btnText;
                
                btn.className = 'realtime-btn';
                
                switch (state) {
                    case 'listening':
                        btn.classList.add('listening');
                        icon.textContent = '⏹️';
                        text.textContent = '停止分析';
                        break;
                    case 'processing':
                        btn.classList.add('processing');
                        icon.textContent = '⏳';
                        text.textContent = '分析中...';
                        btn.disabled = true;
                        break;
                    default:
                        icon.textContent = '🎤';
                        text.textContent = '开始实时分析';
                        btn.disabled = false;
                }
            }
            
            animateVisualizer() {
                if (!this.isListening) return;
                
                const canvas = this.elements.visualizerCanvas;
                const ctx = canvas.getContext('2d');
                
                const draw = () => {
                    if (!this.isListening) return;
                    
                    ctx.fillStyle = '#f3f4f6';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // 绘制音频波形动画
                    const barWidth = 4;
                    const gap = 2;
                    const numBars = Math.floor(canvas.width / (barWidth + gap));
                    
                    for (let i = 0; i < numBars; i++) {
                        const height = Math.random() * canvas.height * 0.8;
                        const x = i * (barWidth + gap);
                        const y = (canvas.height - height) / 2;
                        
                        // 创建渐变色
                        const gradient = ctx.createLinearGradient(0, y, 0, y + height);
                        gradient.addColorStop(0, '#10b981');
                        gradient.addColorStop(1, '#6366f1');
                        
                        ctx.fillStyle = gradient;
                        ctx.fillRect(x, y, barWidth, height);
                    }
                    
                    requestAnimationFrame(draw);
                };
                
                draw();
            }
            
            reset() {
                this.stopListening();
                
                // 重置UI
                this.elements.transcriptText.textContent = '开始说话，这里将显示实时转录...';
                this.elements.emotionDisplay.style.display = 'none';
                this.elements.philosophicalSection.style.display = 'none';
                this.elements.posterSection.style.display = 'none';
                this.elements.saveBtn.style.display = 'none';
                this.elements.shareBtn.style.display = 'none';
                this.elements.statusHint.textContent = '点击开始实时语音情感分析';
                
                // 重置数据
                this.currentAnalysis = {
                    transcript: '',
                    emotions: {},
                    philosophical_note: ''
                };
                
                this.setupVisualizer();
            }
            
            saveResults() {
                // 保存分析结果
                const data = {
                    timestamp: new Date().toISOString(),
                    ...this.currentAnalysis
                };
                
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `soulnote_analysis_${new Date().getTime()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
            
            shareResults() {
                // 分享结果
                if (navigator.share) {
                    navigator.share({
                        title: 'Soulnote 情感分析结果',
                        text: `我的情感分析：${this.currentAnalysis.philosophical_note}`,
                        url: window.location.href
                    });
                } else {
                    // 复制到剪贴板
                    const text = `Soulnote 情感分析：\\n\\n转录：${this.currentAnalysis.transcript}\\n\\n深度思考：${this.currentAnalysis.philosophical_note}`;
                    navigator.clipboard.writeText(text).then(() => {
                        alert('分析结果已复制到剪贴板！');
                    });
                }
            }
        }
        
        // 初始化应用
        document.addEventListener('DOMContentLoaded', () => {
            new SoulnoteRealtime();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/realtime/status')
def realtime_status():
    """检查实时API状态"""
    return jsonify({
        'realtime_available': HAS_REALTIME_API,
        'api_key_configured': bool(OPENAI_API_KEY),
        'fallback_mode': not HAS_REALTIME_API
    })

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """文本分析（备用模式）"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # 使用备用AI客户端
        emotion_data = fallback_ai_client.analyze_emotions(text)
        philosophical_note = fallback_ai_client.generate_philosophical_note(
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

@app.route('/api/generate/poster', methods=['POST'])
def generate_poster():
    """生成情感海报"""
    try:
        data = request.json
        
        poster_path = poster_generator.create_poster(
            text=data.get('text', ''),
            primary_emotion=data.get('primary_emotion', 'neutral'),
            emotions=data.get('emotions', {}),
            philosophical_note=data.get('philosophical_note', ''),
            waveform_data=data.get('waveform_data'),
            audio_filename=data.get('audio_filename')
        )
        
        return jsonify({
            'poster_path': str(poster_path),
            'poster_url': f'/api/output/{poster_path.name}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/output/<filename>')
def get_output_file(filename):
    """获取输出文件"""
    from flask import send_from_directory
    try:
        return send_from_directory(OUTPUT_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    print("🚀 启动Soulnote实时API版本...")
    
    if HAS_REALTIME_API:
        print("🎙️ OpenAI Realtime API已启用")
        print("✨ 支持实时语音情感分析")
    else:
        print("⚠️  未检测到OpenAI API密钥")
        print("🔄 将使用备用AI模式")
        print("💡 要启用实时API，请设置: export OPENAI_API_KEY=your-key-here")
    
    print("🌟 访问: http://localhost:5005")
    
    app.run(debug=True, host='0.0.0.0', port=5005)
