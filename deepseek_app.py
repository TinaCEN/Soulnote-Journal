#!/usr/bin/env python3
"""
Soulnote with DeepSeek API - 使用DeepSeek进行实时情感分析
"""

from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import os
import sys
import uuid
from pathlib import Path

from models.deepseek_client import DeepSeekProvider, DeepSeekRealtimeClient, EnhancedOnlineAIClient
from utils.audio_processor import AudioProcessor
from utils.poster_generator import PosterGenerator

app = Flask(__name__)
CORS(app)

# 设置DeepSeek API密钥
os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')

# 配置路径（以当前文件目录为根）
PROJECT_ROOT = Path(__file__).parent.resolve()
UPLOAD_FOLDER = PROJECT_ROOT / 'uploads'
OUTPUT_FOLDER = PROJECT_ROOT / 'output'

# 确保目录存在
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# 初始化组件
ai_client = EnhancedOnlineAIClient("deepseek")
audio_processor = AudioProcessor()
poster_generator = PosterGenerator()
deepseek_realtime = DeepSeekRealtimeClient(os.getenv('DEEPSEEK_API_KEY'))

# 检查DeepSeek连接
DEEPSEEK_CONNECTED = ai_client.is_connected()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soulnote - DeepSeek AI情感分析</title>
    <style>
        :root {
            --primary-color: #0066cc;
            --secondary-color: #4d94ff;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --deepseek-blue: #1e40af;
            --deepseek-light: #3b82f6;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --border-color: #e5e7eb;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
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
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .tagline {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 10px;
        }

        .deepseek-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            display: inline-block;
            backdrop-filter: blur(10px);
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

        .api-status.connected {
            background: rgba(16, 185, 129, 0.3);
            border: 2px solid rgba(16, 185, 129, 0.5);
        }

        .api-status.error {
            background: rgba(239, 68, 68, 0.3);
            border: 2px solid rgba(239, 68, 68, 0.5);
        }

        .main-content {
            background: var(--bg-primary);
            border-radius: 20px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .tab-container {
            display: flex;
            background: var(--bg-secondary);
        }

        .tab-btn {
            flex: 1;
            padding: 20px;
            border: none;
            background: transparent;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            color: var(--text-secondary);
        }

        .tab-btn.active {
            background: var(--bg-primary);
            color: var(--deepseek-blue);
            border-bottom: 3px solid var(--deepseek-blue);
        }

        .tab-content {
            display: none;
            padding: 40px;
        }

        .tab-content.active {
            display: block;
        }

        .voice-section {
            text-align: center;
        }

        .voice-visualizer {
            width: 100%;
            height: 200px;
            background: var(--bg-secondary);
            border-radius: 15px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
            border: 3px solid transparent;
            transition: all 0.3s ease;
        }

        .voice-visualizer.active {
            border-color: var(--deepseek-blue);
            box-shadow: 0 0 20px rgba(30, 64, 175, 0.3);
        }

        .voice-visualizer canvas {
            width: 100%;
            height: 100%;
        }

        .btn {
            background: var(--deepseek-blue);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(30, 64, 175, 0.3);
            background: var(--deepseek-light);
        }

        .btn-large {
            font-size: 1.3rem;
            padding: 20px 40px;
            border-radius: 50px;
        }

        .btn.recording {
            background: var(--danger-color);
            animation: pulse 1.5s infinite;
        }

        .btn.processing {
            background: var(--warning-color);
            cursor: not-allowed;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .btn-success {
            background: var(--success-color);
        }

        .text-input textarea {
            width: 100%;
            min-height: 200px;
            padding: 20px;
            border: 2px solid var(--border-color);
            border-radius: 12px;
            font-size: 1.1rem;
            font-family: inherit;
            resize: vertical;
            margin-bottom: 20px;
            transition: border-color 0.3s ease;
        }

        .text-input textarea:focus {
            outline: none;
            border-color: var(--deepseek-blue);
        }

        .results-section {
            padding: 40px;
            display: none;
        }

        .results-section.show {
            display: block;
        }

        .results-section h2 {
            text-align: center;
            margin-bottom: 40px;
            color: var(--deepseek-blue);
            font-size: 2rem;
        }

        .transcript-section {
            background: var(--bg-secondary);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }

        .transcript-section h3 {
            margin-bottom: 15px;
            color: var(--text-primary);
        }

        .transcript-text {
            color: var(--text-secondary);
            font-style: italic;
            line-height: 1.6;
        }

        .emotion-analysis {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }

        .primary-emotion {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-transform: capitalize;
            background: linear-gradient(135deg, var(--deepseek-blue)20, var(--deepseek-light)40);
            color: var(--deepseek-blue);
        }

        .emotions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .emotion-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid var(--deepseek-blue);
        }

        .emotion-name {
            font-weight: 600;
            text-transform: capitalize;
            color: var(--text-primary);
            margin-bottom: 10px;
        }

        .emotion-score {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--deepseek-blue);
        }

        .philosophical-section {
            background: linear-gradient(135deg, var(--bg-secondary), white);
            padding: 35px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid var(--deepseek-blue);
        }

        .philosophical-section h3 {
            text-align: center;
            margin-bottom: 25px;
            color: var(--deepseek-blue);
        }

        .philosophical-text {
            font-size: 1.2rem;
            font-style: italic;
            text-align: center;
            color: var(--text-secondary);
            line-height: 1.8;
            font-weight: 500;
        }

        .poster-section {
            text-align: center;
            margin-bottom: 30px;
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
            gap: 15px;
            margin: 30px 0;
            flex-wrap: wrap;
        }

        .hidden {
            display: none !important;
        }

        .loading-section {
            text-align: center;
            padding: 60px 40px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--deepseek-blue);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .logo {
                font-size: 2rem;
            }
            
            .tab-content {
                padding: 20px;
            }
            
            .btn-large {
                font-size: 1.1rem;
                padding: 15px 30px;
            }
            
            .emotions-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1 class="logo">🧠 Soulnote</h1>
            <p class="tagline">DeepSeek AI驱动的情感分析工具</p>
            <div class="deepseek-badge">
                🚀 Powered by DeepSeek
            </div>
        </header>

        <!-- API Status -->
        <div id="apiStatus" class="api-status">
            <span class="status-indicator" id="statusDot"></span>
            <span id="statusText">正在连接DeepSeek AI...</span>
        </div>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Input Section -->
            <section class="input-section" id="inputSection">
                <div class="tab-container">
                    <button class="tab-btn active" data-tab="voice">
                        🎤 语音录制
                    </button>
                    <button class="tab-btn" data-tab="text">
                        ✍️ 文字输入
                    </button>
                </div>

                <!-- Voice Input Tab -->
                <div class="tab-content active" id="voiceTab">
                    <div class="voice-section">
                        <div class="voice-visualizer" id="voiceVisualizer">
                            <canvas id="visualizerCanvas"></canvas>
                        </div>
                        
                        <div class="voice-controls">
                            <button id="recordBtn" class="btn btn-large">
                                <span id="recordBtnIcon">🎤</span>
                                <span id="recordBtnText">开始录制</span>
                            </button>
                            <p id="statusHint">点击开始录制你的声音日记</p>
                        </div>

                        <div id="audioPlayback" class="audio-playback hidden">
                            <audio id="audioElement" controls style="width: 100%; margin: 20px 0;"></audio>
                            <button id="analyzeVoiceBtn" class="btn btn-success">
                                🧠 DeepSeek情感分析
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Text Input Tab -->
                <div class="tab-content" id="textTab">
                    <div class="text-input">
                        <textarea 
                            id="journalText" 
                            placeholder="在这里分享你的想法和感受...&#10;&#10;DeepSeek AI将深度分析你的情感状态"
                        ></textarea>
                        
                        <button id="analyzeTextBtn" class="btn btn-large">
                            🧠 DeepSeek情感分析
                        </button>
                    </div>
                </div>
            </section>

            <!-- Loading Section -->
            <section class="loading-section hidden" id="loadingSection">
                <div class="spinner"></div>
                <p id="loadingText">DeepSeek AI正在分析你的情感...</p>
            </section>

            <!-- Results Section -->
            <section class="results-section" id="resultsSection">
                <h2>🎭 DeepSeek情感分析结果</h2>

                <!-- Transcribed Text -->
                <div id="transcriptSection" class="transcript-section hidden">
                    <h3>📝 语音转录</h3>
                    <div class="transcript-text" id="transcriptText"></div>
                </div>

                <!-- Emotion Analysis -->
                <div class="emotion-analysis">
                    <h3>🎯 情感识别</h3>
                    <div id="primaryEmotion" class="primary-emotion"></div>
                    <div id="emotionsGrid" class="emotions-grid"></div>
                </div>

                <!-- Philosophical Section -->
                <div class="philosophical-section">
                    <h3>🧘 AI深度思考</h3>
                    <div class="philosophical-text" id="philosophicalText"></div>
                </div>

                <!-- Poster Section -->
                <div class="poster-section">
                    <h3>🎨 情感视觉化</h3>
                    <div class="poster-container">
                        <img id="posterImage" src="" alt="生成的情感海报" style="display: none;">
                        <div id="posterLoading">正在生成个性化海报...</div>
                    </div>
                </div>

                <!-- Controls -->
                <div class="controls-section">
                    <button id="saveBtn" class="btn">
                        💾 保存分析结果
                    </button>
                    <button id="shareBtn" class="btn">
                        📱 分享到社交媒体
                    </button>
                    <button id="resetBtn" class="btn">
                        🔄 开始新的分析
                    </button>
                </div>
            </section>
        </main>
    </div>

    <script>
        class SoulnoteDeepSeek {
            constructor() {
                this.isRecording = false;
                this.mediaRecorder = null;
                this.audioChunks = [];
                this.audioBlob = null;
                this.currentAnalysis = null;
                
                this.elements = {
                    // Tabs
                    tabBtns: document.querySelectorAll('.tab-btn'),
                    tabContents: document.querySelectorAll('.tab-content'),
                    
                    // Voice
                    recordBtn: document.getElementById('recordBtn'),
                    recordBtnIcon: document.getElementById('recordBtnIcon'),
                    recordBtnText: document.getElementById('recordBtnText'),
                    statusHint: document.getElementById('statusHint'),
                    voiceVisualizer: document.getElementById('voiceVisualizer'),
                    visualizerCanvas: document.getElementById('visualizerCanvas'),
                    audioPlayback: document.getElementById('audioPlayback'),
                    audioElement: document.getElementById('audioElement'),
                    analyzeVoiceBtn: document.getElementById('analyzeVoiceBtn'),
                    
                    // Text
                    journalText: document.getElementById('journalText'),
                    analyzeTextBtn: document.getElementById('analyzeTextBtn'),
                    
                    // Status
                    apiStatus: document.getElementById('apiStatus'),
                    statusDot: document.getElementById('statusDot'),
                    statusText: document.getElementById('statusText'),
                    
                    // Sections
                    inputSection: document.getElementById('inputSection'),
                    loadingSection: document.getElementById('loadingSection'),
                    resultsSection: document.getElementById('resultsSection'),
                    loadingText: document.getElementById('loadingText'),
                    
                    // Results
                    transcriptSection: document.getElementById('transcriptSection'),
                    transcriptText: document.getElementById('transcriptText'),
                    primaryEmotion: document.getElementById('primaryEmotion'),
                    emotionsGrid: document.getElementById('emotionsGrid'),
                    philosophicalText: document.getElementById('philosophicalText'),
                    posterImage: document.getElementById('posterImage'),
                    posterLoading: document.getElementById('posterLoading'),
                    
                    // Controls
                    saveBtn: document.getElementById('saveBtn'),
                    shareBtn: document.getElementById('shareBtn'),
                    resetBtn: document.getElementById('resetBtn')
                };
                
                this.init();
            }
            
            async init() {
                this.setupEventListeners();
                this.setupVisualizer();
                await this.checkAPIStatus();
            }
            
            setupEventListeners() {
                // Tab switching
                this.elements.tabBtns.forEach(btn => {
                    btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
                });
                
                // Voice recording
                this.elements.recordBtn.addEventListener('click', () => this.toggleRecording());
                this.elements.analyzeVoiceBtn.addEventListener('click', () => this.analyzeVoice());
                
                // Text analysis
                this.elements.analyzeTextBtn.addEventListener('click', () => this.analyzeText());
                
                // Controls
                this.elements.saveBtn.addEventListener('click', () => this.saveResults());
                this.elements.shareBtn.addEventListener('click', () => this.shareResults());
                this.elements.resetBtn.addEventListener('click', () => this.reset());
            }
            
            switchTab(tabName) {
                this.elements.tabBtns.forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.tab === tabName);
                });
                
                this.elements.tabContents.forEach(content => {
                    content.classList.toggle('active', content.id === tabName + 'Tab');
                });
            }
            
            async checkAPIStatus() {
                try {
                    const response = await fetch('/api/deepseek/status');
                    const data = await response.json();
                    
                    if (data.connected) {
                        this.updateStatus(`✅ DeepSeek AI已连接 - ${data.model}`, 'connected');
                    } else {
                        this.updateStatus('❌ DeepSeek AI连接失败', 'error');
                    }
                } catch (error) {
                    this.updateStatus('❌ API连接失败', 'error');
                }
            }
            
            updateStatus(message, type) {
                this.elements.statusText.textContent = message;
                this.elements.apiStatus.className = `api-status ${type}`;
                this.elements.statusDot.className = `status-indicator ${type === 'connected' ? 'connected' : 'disconnected'}`;
            }
            
            setupVisualizer() {
                const canvas = this.elements.visualizerCanvas;
                const ctx = canvas.getContext('2d');
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
                
                // DeepSeek主题色
                ctx.fillStyle = '#f8fafc';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#1e40af';
                ctx.font = '18px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('🎤 DeepSeek AI 语音分析', canvas.width / 2, canvas.height / 2);
            }
            
            async toggleRecording() {
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    await this.startRecording();
                }
            }
            
            async startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    
                    let options = { mimeType: 'audio/wav' };
                    if (!MediaRecorder.isTypeSupported('audio/wav')) {
                        options = { mimeType: 'audio/webm' };
                    }
                    
                    this.mediaRecorder = new MediaRecorder(stream, options);
                    this.audioChunks = [];
                    
                    this.mediaRecorder.ondataavailable = (event) => {
                        this.audioChunks.push(event.data);
                    };
                    
                    this.mediaRecorder.onstop = () => {
                        const blob = new Blob(this.audioChunks, { type: this.mediaRecorder.mimeType });
                        this.audioBlob = blob;
                        
                        const audioUrl = URL.createObjectURL(blob);
                        this.elements.audioElement.src = audioUrl;
                        this.elements.audioPlayback.classList.remove('hidden');
                    };
                    
                    this.mediaRecorder.start();
                    this.isRecording = true;
                    
                    this.elements.recordBtnIcon.textContent = '⏹️';
                    this.elements.recordBtnText.textContent = '停止录制';
                    this.elements.recordBtn.classList.add('recording');
                    this.elements.voiceVisualizer.classList.add('active');
                    this.elements.statusHint.textContent = '🎙️ 正在录制，请说话...';
                    
                    this.animateVisualizer();
                    
                } catch (error) {
                    alert('无法访问麦克风：' + error.message);
                }
            }
            
            stopRecording() {
                if (this.mediaRecorder && this.isRecording) {
                    this.mediaRecorder.stop();
                    this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    this.isRecording = false;
                    
                    this.elements.recordBtnIcon.textContent = '🎤';
                    this.elements.recordBtnText.textContent = '开始录制';
                    this.elements.recordBtn.classList.remove('recording');
                    this.elements.voiceVisualizer.classList.remove('active');
                    this.elements.statusHint.textContent = '录制完成，点击分析按钮进行情感分析';
                }
            }
            
            animateVisualizer() {
                if (!this.isRecording) return;
                
                const canvas = this.elements.visualizerCanvas;
                const ctx = canvas.getContext('2d');
                
                const draw = () => {
                    if (!this.isRecording) return;
                    
                    ctx.fillStyle = '#f8fafc';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    const barWidth = 4;
                    const gap = 2;
                    const numBars = Math.floor(canvas.width / (barWidth + gap));
                    
                    for (let i = 0; i < numBars; i++) {
                        const height = Math.random() * canvas.height * 0.8;
                        const x = i * (barWidth + gap);
                        const y = (canvas.height - height) / 2;
                        
                        // DeepSeek渐变色
                        const gradient = ctx.createLinearGradient(0, y, 0, y + height);
                        gradient.addColorStop(0, '#1e40af');
                        gradient.addColorStop(1, '#3b82f6');
                        
                        ctx.fillStyle = gradient;
                        ctx.fillRect(x, y, barWidth, height);
                    }
                    
                    requestAnimationFrame(draw);
                };
                
                draw();
            }
            
            async analyzeVoice() {
                if (!this.audioBlob) {
                    alert('请先录制音频');
                    return;
                }
                
                this.showLoading('DeepSeek AI正在分析你的语音...');
                
                try {
                    const formData = new FormData();
                    formData.append('audio', this.audioBlob, 'recording.wav');
                    
                    const response = await fetch('/api/deepseek/analyze/voice', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error('语音分析失败');
                    }
                    
                    const data = await response.json();
                    this.currentAnalysis = data;
                    
                    await this.generatePoster(data);
                    this.displayResults(data, true);
                    
                } catch (error) {
                    alert('语音分析失败：' + error.message);
                    this.hideLoading();
                }
            }
            
            async analyzeText() {
                const text = this.elements.journalText.value.trim();
                
                if (!text) {
                    alert('请输入一些文字');
                    return;
                }
                
                this.showLoading('DeepSeek AI正在分析你的文字...');
                
                try {
                    const response = await fetch('/api/deepseek/analyze/text', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text })
                    });
                    
                    if (!response.ok) {
                        throw new Error('文字分析失败');
                    }
                    
                    const data = await response.json();
                    this.currentAnalysis = data;
                    
                    await this.generatePoster(data);
                    this.displayResults(data, false);
                    
                } catch (error) {
                    alert('文字分析失败：' + error.message);
                    this.hideLoading();
                }
            }
            
            async generatePoster(analysisData) {
                this.elements.loadingText.textContent = 'DeepSeek AI正在创建你的情感海报...';
                
                try {
                    const response = await fetch('/api/generate/poster', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(analysisData)
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        this.elements.posterImage.src = data.poster_url;
                        this.elements.posterImage.style.display = 'block';
                        this.elements.posterLoading.style.display = 'none';
                    }
                } catch (error) {
                    this.elements.posterLoading.textContent = '海报生成失败';
                }
            }
            
            displayResults(data, isVoice) {
                // 显示转录（语音）
                if (isVoice && data.text) {
                    this.elements.transcriptText.textContent = data.text;
                    this.elements.transcriptSection.classList.remove('hidden');
                }
                
                // 显示主要情感
                this.elements.primaryEmotion.textContent = data.primary_emotion;
                
                // 显示情感网格
                this.displayEmotions(data.emotions);
                
                // 显示哲学思考
                this.elements.philosophicalText.textContent = data.philosophical_note;
                
                // 显示结果
                this.hideLoading();
                this.elements.inputSection.style.display = 'none';
                this.elements.resultsSection.classList.add('show');
            }
            
            displayEmotions(emotions) {
                const grid = this.elements.emotionsGrid;
                grid.innerHTML = '';
                
                for (const [emotion, score] of Object.entries(emotions)) {
                    const card = document.createElement('div');
                    card.className = 'emotion-card';
                    card.innerHTML = `
                        <div class="emotion-name">${emotion}</div>
                        <div class="emotion-score">${score}%</div>
                    `;
                    grid.appendChild(card);
                }
            }
            
            showLoading(message) {
                this.elements.loadingText.textContent = message;
                this.elements.inputSection.style.display = 'none';
                this.elements.resultsSection.classList.remove('show');
                this.elements.loadingSection.classList.remove('hidden');
            }
            
            hideLoading() {
                this.elements.loadingSection.classList.add('hidden');
            }
            
            reset() {
                // 重置状态
                this.audioBlob = null;
                this.currentAnalysis = null;
                
                // 重置UI
                this.elements.journalText.value = '';
                this.elements.audioPlayback.classList.add('hidden');
                this.elements.transcriptSection.classList.add('hidden');
                this.elements.resultsSection.classList.remove('show');
                this.elements.inputSection.style.display = 'block';
                this.elements.posterImage.style.display = 'none';
                this.elements.posterLoading.style.display = 'block';
                this.elements.posterLoading.textContent = '正在生成个性化海报...';
                
                this.setupVisualizer();
                this.checkAPIStatus();
            }
            
            saveResults() {
                if (!this.currentAnalysis) return;
                
                const data = {
                    timestamp: new Date().toISOString(),
                    provider: 'DeepSeek',
                    ...this.currentAnalysis
                };
                
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `deepseek_analysis_${new Date().getTime()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
            
            shareResults() {
                if (!this.currentAnalysis) return;
                
                const text = `DeepSeek AI情感分析结果：\\n\\n主要情感：${this.currentAnalysis.primary_emotion}\\n\\n深度思考：${this.currentAnalysis.philosophical_note}\\n\\n#Soulnote #DeepSeek #AI情感分析`;
                
                if (navigator.share) {
                    navigator.share({
                        title: 'DeepSeek AI情感分析',
                        text: text
                    });
                } else {
                    navigator.clipboard.writeText(text).then(() => {
                        alert('分析结果已复制到剪贴板！');
                    });
                }
            }
        }
        
        // 初始化应用
        document.addEventListener('DOMContentLoaded', () => {
            new SoulnoteDeepSeek();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/deepseek/status')
def deepseek_status():
    """检查DeepSeek API状态"""
    return jsonify({
        'connected': DEEPSEEK_CONNECTED,
        'provider': 'DeepSeek',
        'model': 'deepseek-chat',
        'api_key_configured': bool(os.getenv('DEEPSEEK_API_KEY'))
    })

@app.route('/api/deepseek/analyze/text', methods=['POST'])
def analyze_text_deepseek():
    """使用DeepSeek分析文本"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': '请提供文本内容'}), 400
        
        # 使用DeepSeek实时客户端分析
        emotion_data = deepseek_realtime.analyze_emotions_realtime(text)
        
        # 生成哲学思考
        philosophical_note = deepseek_realtime.generate_philosophical_note_realtime(
            emotion_data.get('primary_emotion', 'neutral'),
            emotion_data.get('emotions', {}),
            text
        )
        
        return jsonify({
            'text': text,
            'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
            'emotions': emotion_data.get('emotions', {}),
            'philosophical_note': philosophical_note,
            'provider': 'DeepSeek',
            'timestamp': '2025-11-04T17:00:00'
        })
    
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@app.route('/api/deepseek/analyze/voice', methods=['POST'])
def analyze_voice_deepseek():
    """使用DeepSeek分析语音"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': '请提供音频文件'}), 400
        
        audio_file = request.files['audio']
        
        # 保存音频文件
        audio_filename = f"{uuid.uuid4().hex}.wav"
        audio_path = UPLOAD_FOLDER / audio_filename
        audio_file.save(audio_path)
        
        # 语音转文字
        text = audio_processor.speech_to_text(audio_path)
        
        if not text:
            return jsonify({'error': '无法转录音频，请重新录制'}), 400
        
        # 使用DeepSeek分析情感
        emotion_data = deepseek_realtime.analyze_emotions_realtime(text)
        
        # 生成哲学思考
        philosophical_note = deepseek_realtime.generate_philosophical_note_realtime(
            emotion_data.get('primary_emotion', 'neutral'),
            emotion_data.get('emotions', {}),
            text
        )
        
        # 生成波形数据
        waveform_data = audio_processor.generate_waveform_data(audio_path)
        
        return jsonify({
            'text': text,
            'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
            'emotions': emotion_data.get('emotions', {}),
            'philosophical_note': philosophical_note,
            'waveform_data': waveform_data,
            'audio_filename': audio_filename,
            'provider': 'DeepSeek',
            'timestamp': '2025-11-04T17:00:00'
        })
    
    except Exception as e:
        return jsonify({'error': f'语音分析失败: {str(e)}'}), 500

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
        return jsonify({'error': f'海报生成失败: {str(e)}'}), 500

@app.route('/api/output/<filename>')
def get_output_file(filename):
    """获取输出文件"""
    try:
        return send_from_directory(OUTPUT_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    print("🚀 启动Soulnote - DeepSeek AI版本...")
    print(f"🧠 DeepSeek API: {'✅ 已连接' if DEEPSEEK_CONNECTED else '❌ 连接失败'}")
    
    if DEEPSEEK_CONNECTED:
        print("✨ 功能: 实时语音录制 + DeepSeek情感分析 + 哲学思考 + 视觉海报")
        deepseek_realtime.start_session()
    else:
        print("⚠️  DeepSeek连接失败，请检查API密钥")
    
    print("🌟 访问: http://localhost:5006")
    
    app.run(debug=True, host='0.0.0.0', port=5006)
