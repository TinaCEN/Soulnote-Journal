#!/usr/bin/env python3
"""
完整版Soulnote应用 - 包含语音输入和视觉海报生成
"""

from flask import Flask, jsonify, request, render_template_string, send_file, send_from_directory
from flask_cors import CORS
import sys
import os
import uuid
from pathlib import Path

from models.online_ai_client import OnlineAIClient
from utils.audio_processor import AudioProcessor
from utils.poster_generator import PosterGenerator

app = Flask(__name__)
CORS(app)

# 配置路径（以当前文件目录为根）
PROJECT_ROOT = Path(__file__).parent.resolve()
UPLOAD_FOLDER = PROJECT_ROOT / 'uploads'
OUTPUT_FOLDER = PROJECT_ROOT / 'output'
STATIC_FOLDER = PROJECT_ROOT / 'static'

# 确保目录存在
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# 初始化组件
ai_client = OnlineAIClient()
audio_processor = AudioProcessor()
poster_generator = PosterGenerator()

# 主页HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soulnote - AI情感日记</title>
    <style>
        :root {
            --primary-color: #6366f1;
            --secondary-color: #8b5cf6;
            --success-color: #10b981;
            --danger-color: #ef4444;
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
            max-width: 900px;
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

        .status-indicator {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 20px;
            border-radius: 25px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        .status-indicator.connected {
            background: rgba(16, 185, 129, 0.2);
        }

        .status-indicator.error {
            background: rgba(239, 68, 68, 0.2);
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
        }

        .tab-btn.active {
            background: var(--bg-primary);
            color: var(--primary-color);
        }

        .tab-content {
            display: none;
            padding: 40px;
        }

        .tab-content.active {
            display: block;
        }

        .voice-input {
            text-align: center;
        }

        .recording-visualizer {
            width: 100%;
            height: 200px;
            background: var(--bg-secondary);
            border-radius: 15px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }

        .recording-visualizer canvas {
            width: 100%;
            height: 100%;
        }

        .btn {
            background: var(--primary-color);
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
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }

        .btn-large {
            font-size: 1.3rem;
            padding: 20px 40px;
        }

        .btn.recording {
            background: var(--danger-color);
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }

        .btn-success {
            background: var(--success-color);
        }

        .hint {
            color: var(--text-secondary);
            margin-top: 15px;
        }

        .audio-playback {
            margin-top: 30px;
        }

        .audio-playback audio {
            width: 100%;
            margin-bottom: 20px;
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
        }

        .text-input textarea:focus {
            outline: none;
            border-color: var(--primary-color);
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
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .results-section {
            padding: 40px;
        }

        .results-section h2 {
            text-align: center;
            margin-bottom: 40px;
            color: var(--text-primary);
        }

        .emotion-analysis {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }

        .primary-emotion {
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-transform: capitalize;
        }

        .emotions-list {
            display: grid;
            gap: 15px;
        }

        .emotion-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px;
            background: white;
            border-radius: 10px;
        }

        .emotion-name {
            font-weight: 600;
            text-transform: capitalize;
        }

        .emotion-score {
            font-weight: 700;
            color: var(--primary-color);
        }

        .philosophical-note {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }

        .philosophical-note blockquote {
            font-size: 1.2rem;
            font-style: italic;
            text-align: center;
            color: var(--text-secondary);
            line-height: 1.8;
        }

        .poster-preview {
            text-align: center;
            margin-bottom: 30px;
        }

        .poster-container {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 15px;
            display: inline-block;
        }

        .poster-container img {
            max-width: 100%;
            max-height: 500px;
            border-radius: 10px;
        }

        .export-section {
            text-align: center;
            margin-bottom: 30px;
        }

        .export-buttons {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }

        .btn-export {
            background: var(--secondary-color);
            font-size: 0.9rem;
            padding: 12px 20px;
        }

        .transcribed-text {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
        }

        .transcribed-text h3 {
            margin-bottom: 15px;
            color: var(--text-primary);
        }

        .transcribed-text p {
            color: var(--text-secondary);
            font-style: italic;
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
                padding: 15px 25px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1 class="logo">🌟 Soulnote</h1>
            <p class="tagline">AI驱动的情感日记工具</p>
        </header>

        <!-- Status indicator -->
        <div id="statusIndicator" class="status-indicator">
            <span id="statusText">正在连接AI服务...</span>
        </div>

        <!-- Main content -->
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
                    <div class="voice-input">
                        <div class="recording-visualizer" id="recordingVisualizer">
                            <canvas id="visualizerCanvas"></canvas>
                        </div>
                        
                        <div class="voice-controls">
                            <button id="recordBtn" class="btn btn-large">
                                <span id="recordBtnIcon">🎤</span>
                                <span id="recordBtnText">开始录制</span>
                            </button>
                            <p class="hint">点击开始录制你的声音日记</p>
                        </div>

                        <div id="audioPlayback" class="audio-playback hidden">
                            <audio id="audioElement" controls></audio>
                            <button id="analyzeVoiceBtn" class="btn btn-success">
                                分析情感
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Text Input Tab -->
                <div class="tab-content" id="textTab">
                    <div class="text-input">
                        <textarea 
                            id="journalText" 
                            placeholder="在这里分享你的想法和感受...&#10;&#10;今天你在想什么？"
                        ></textarea>
                        
                        <button id="analyzeTextBtn" class="btn btn-large">
                            分析情感
                        </button>
                    </div>
                </div>
            </section>

            <!-- Loading Section -->
            <section class="loading-section hidden" id="loadingSection">
                <div class="spinner"></div>
                <p id="loadingText">正在分析你的情感...</p>
            </section>

            <!-- Results Section -->
            <section class="results-section hidden" id="resultsSection">
                <h2>🎭 你的情感分析</h2>

                <!-- Transcribed Text (for voice input) -->
                <div id="transcribedTextContainer" class="transcribed-text hidden">
                    <h3>你说的话：</h3>
                    <p id="transcribedText"></p>
                </div>

                <!-- Emotion Analysis -->
                <div class="emotion-analysis">
                    <h3>检测到的情感</h3>
                    <div id="primaryEmotion" class="primary-emotion"></div>
                    <div id="emotionsList" class="emotions-list"></div>
                </div>

                <!-- Philosophical Note -->
                <div class="philosophical-note">
                    <h3>📖 深度思考</h3>
                    <blockquote id="philosophicalNote"></blockquote>
                </div>

                <!-- Generated Poster -->
                <div class="poster-preview">
                    <h3>🎨 你的情感海报</h3>
                    <div class="poster-container">
                        <img id="posterImage" src="" alt="生成的海报" style="display: none;">
                        <div id="posterLoading">正在生成海报...</div>
                    </div>
                </div>

                <!-- Export Options -->
                <div class="export-section">
                    <h3>📱 分享你的情感之旅</h3>
                    <div class="export-buttons">
                        <button class="btn btn-export" data-platform="instagram">
                            📷 Instagram
                        </button>
                        <button class="btn btn-export" data-platform="twitter">
                            🐦 Twitter/X
                        </button>
                        <button class="btn btn-export" data-platform="square">
                            🖼️ 方形格式
                        </button>
                    </div>
                </div>

                <!-- New Journey Button -->
                <button id="newJourneyBtn" class="btn">
                    ✨ 开始新的情感之旅
                </button>
            </section>
        </main>
    </div>

    <script>
        // 应用状态
        const state = {
            isRecording: false,
            mediaRecorder: null,
            audioChunks: [],
            audioBlob: null,
            currentAnalysis: null,
            posterPath: null
        };

        // DOM元素
        const elements = {
            tabBtns: document.querySelectorAll('.tab-btn'),
            tabContents: document.querySelectorAll('.tab-content'),
            recordBtn: document.getElementById('recordBtn'),
            recordBtnIcon: document.getElementById('recordBtnIcon'),
            recordBtnText: document.getElementById('recordBtnText'),
            audioPlayback: document.getElementById('audioPlayback'),
            audioElement: document.getElementById('audioElement'),
            analyzeVoiceBtn: document.getElementById('analyzeVoiceBtn'),
            visualizerCanvas: document.getElementById('visualizerCanvas'),
            journalText: document.getElementById('journalText'),
            analyzeTextBtn: document.getElementById('analyzeTextBtn'),
            inputSection: document.getElementById('inputSection'),
            loadingSection: document.getElementById('loadingSection'),
            resultsSection: document.getElementById('resultsSection'),
            loadingText: document.getElementById('loadingText'),
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.getElementById('statusText'),
            transcribedTextContainer: document.getElementById('transcribedTextContainer'),
            transcribedText: document.getElementById('transcribedText'),
            primaryEmotion: document.getElementById('primaryEmotion'),
            emotionsList: document.getElementById('emotionsList'),
            philosophicalNote: document.getElementById('philosophicalNote'),
            posterImage: document.getElementById('posterImage'),
            posterLoading: document.getElementById('posterLoading'),
            exportBtns: document.querySelectorAll('.btn-export'),
            newJourneyBtn: document.getElementById('newJourneyBtn')
        };

        // 初始化
        async function init() {
            setupEventListeners();
            await checkServerHealth();
            setupVisualizer();
        }

        // 事件监听器
        function setupEventListeners() {
            elements.tabBtns.forEach(btn => {
                btn.addEventListener('click', () => switchTab(btn.dataset.tab));
            });
            
            elements.recordBtn.addEventListener('click', toggleRecording);
            elements.analyzeVoiceBtn.addEventListener('click', analyzeVoice);
            elements.analyzeTextBtn.addEventListener('click', analyzeText);
            elements.newJourneyBtn.addEventListener('click', resetApp);
            
            elements.exportBtns.forEach(btn => {
                btn.addEventListener('click', () => exportCard(btn.dataset.platform));
            });
        }

        // 标签切换
        function switchTab(tabName) {
            elements.tabBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tab === tabName);
            });
            
            elements.tabContents.forEach(content => {
                content.classList.toggle('active', content.id === tabName + 'Tab');
            });
        }

        // 服务器健康检查
        async function checkServerHealth() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                
                if (data.status === 'healthy') {
                    updateStatus(`已连接 - ${data.ai_provider}`, 'connected');
                } else {
                    updateStatus('服务器错误', 'error');
                }
            } catch (error) {
                updateStatus('无法连接到服务器', 'error');
                console.error('健康检查失败:', error);
            }
        }

        function updateStatus(message, type = '') {
            elements.statusText.textContent = message;
            elements.statusIndicator.className = `status-indicator ${type}`;
        }

        // 语音录制
        async function toggleRecording() {
            if (state.isRecording) {
                stopRecording();
            } else {
                await startRecording();
            }
        }

        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                let options = { mimeType: 'audio/wav' };
                if (!MediaRecorder.isTypeSupported('audio/wav')) {
                    options = { mimeType: 'audio/webm' };
                }
                
                state.mediaRecorder = new MediaRecorder(stream, options);
                state.audioChunks = [];
                
                state.mediaRecorder.ondataavailable = (event) => {
                    state.audioChunks.push(event.data);
                };
                
                state.mediaRecorder.onstop = async () => {
                    const blob = new Blob(state.audioChunks, { type: state.mediaRecorder.mimeType });
                    state.audioBlob = blob;
                    
                    const audioUrl = URL.createObjectURL(blob);
                    elements.audioElement.src = audioUrl;
                    elements.audioPlayback.classList.remove('hidden');
                };
                
                state.mediaRecorder.start();
                state.isRecording = true;
                
                elements.recordBtnIcon.textContent = '⏹️';
                elements.recordBtnText.textContent = '停止录制';
                elements.recordBtn.classList.add('recording');
                
                animateVisualizer();
                
            } catch (error) {
                console.error('录制失败:', error);
                alert('无法访问麦克风，请检查权限设置。');
            }
        }

        function stopRecording() {
            if (state.mediaRecorder && state.isRecording) {
                state.mediaRecorder.stop();
                state.mediaRecorder.stream.getTracks().forEach(track => track.stop());
                state.isRecording = false;
                
                elements.recordBtnIcon.textContent = '🎤';
                elements.recordBtnText.textContent = '开始录制';
                elements.recordBtn.classList.remove('recording');
            }
        }

        // 可视化器
        function setupVisualizer() {
            const canvas = elements.visualizerCanvas;
            const ctx = canvas.getContext('2d');
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            
            ctx.fillStyle = '#e5e7eb';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#6b7280';
            ctx.font = '16px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('音频可视化器', canvas.width / 2, canvas.height / 2);
        }

        function animateVisualizer() {
            if (!state.isRecording) return;
            
            const canvas = elements.visualizerCanvas;
            const ctx = canvas.getContext('2d');
            
            const draw = () => {
                if (!state.isRecording) return;
                
                ctx.fillStyle = '#f3f4f6';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                const barWidth = 5;
                const gap = 3;
                const numBars = Math.floor(canvas.width / (barWidth + gap));
                
                for (let i = 0; i < numBars; i++) {
                    const height = Math.random() * canvas.height * 0.8;
                    const x = i * (barWidth + gap);
                    const y = (canvas.height - height) / 2;
                    
                    ctx.fillStyle = '#667eea';
                    ctx.fillRect(x, y, barWidth, height);
                }
                
                requestAnimationFrame(draw);
            };
            
            draw();
        }

        // 分析功能
        async function analyzeVoice() {
            if (!state.audioBlob) {
                alert('请先录制音频');
                return;
            }
            
            showLoading('正在分析你的语音...');
            
            try {
                const formData = new FormData();
                formData.append('audio', state.audioBlob, 'recording.wav');
                
                const response = await fetch('/api/analyze/voice', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('分析失败');
                }
                
                const data = await response.json();
                state.currentAnalysis = data;
                
                await generatePoster(data);
                displayResults(data, true);
                
            } catch (error) {
                console.error('语音分析失败:', error);
                alert('语音分析失败，请重试。');
                hideLoading();
            }
        }

        async function analyzeText() {
            const text = elements.journalText.value.trim();
            
            if (!text) {
                alert('请输入一些文字');
                return;
            }
            
            showLoading('正在分析你的文字...');
            
            try {
                const response = await fetch('/api/analyze/text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                
                if (!response.ok) {
                    throw new Error('分析失败');
                }
                
                const data = await response.json();
                state.currentAnalysis = data;
                
                await generatePoster(data);
                displayResults(data, false);
                
            } catch (error) {
                console.error('文字分析失败:', error);
                alert('文字分析失败，请重试。');
                hideLoading();
            }
        }

        // 海报生成
        async function generatePoster(analysisData) {
            elements.loadingText.textContent = '正在创建你的艺术海报...';
            
            try {
                const response = await fetch('/api/generate/poster', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(analysisData)
                });
                
                if (!response.ok) {
                    throw new Error('海报生成失败');
                }
                
                const data = await response.json();
                state.posterPath = data.poster_path;
                
                elements.posterImage.src = data.poster_url;
                elements.posterImage.style.display = 'block';
                elements.posterLoading.style.display = 'none';
                
            } catch (error) {
                console.error('海报生成失败:', error);
                elements.posterLoading.textContent = '海报生成失败';
            }
        }

        // 显示结果
        function displayResults(data, isVoice) {
            if (isVoice && data.text) {
                elements.transcribedText.textContent = data.text;
                elements.transcribedTextContainer.classList.remove('hidden');
            } else {
                elements.transcribedTextContainer.classList.add('hidden');
            }
            
            const emotionColor = getEmotionColor(data.primary_emotion);
            elements.primaryEmotion.textContent = data.primary_emotion;
            elements.primaryEmotion.style.background = `linear-gradient(135deg, ${emotionColor}30, ${emotionColor}60)`;
            elements.primaryEmotion.style.color = emotionColor;
            
            elements.emotionsList.innerHTML = '';
            for (const [emotion, score] of Object.entries(data.emotions)) {
                const emotionItem = document.createElement('div');
                emotionItem.className = 'emotion-item';
                emotionItem.innerHTML = `
                    <div class="emotion-name">${emotion}</div>
                    <div class="emotion-score">${score}%</div>
                `;
                elements.emotionsList.appendChild(emotionItem);
            }
            
            elements.philosophicalNote.textContent = data.philosophical_note;
            
            hideLoading();
            elements.inputSection.classList.add('hidden');
            elements.resultsSection.classList.remove('hidden');
        }

        // 工具函数
        function showLoading(message) {
            elements.loadingText.textContent = message;
            elements.inputSection.classList.add('hidden');
            elements.resultsSection.classList.add('hidden');
            elements.loadingSection.classList.remove('hidden');
        }

        function hideLoading() {
            elements.loadingSection.classList.add('hidden');
        }

        function resetApp() {
            state.audioBlob = null;
            state.currentAnalysis = null;
            state.posterPath = null;
            
            elements.journalText.value = '';
            elements.audioPlayback.classList.add('hidden');
            elements.resultsSection.classList.add('hidden');
            elements.inputSection.classList.remove('hidden');
            elements.posterImage.style.display = 'none';
            elements.posterLoading.style.display = 'block';
            elements.posterLoading.textContent = '正在生成海报...';
            
            checkServerHealth();
        }

        function getEmotionColor(emotion) {
            const colors = {
                joy: '#fbbf24', happiness: '#fbbf24', sadness: '#3b82f6',
                anger: '#ef4444', fear: '#8b5cf6', surprise: '#f97316',
                disgust: '#10b981', love: '#ec4899', anxiety: '#a855f7',
                peace: '#06b6d4', neutral: '#6b7280', trust: '#60a5fa',
                anticipation: '#84cc16', contemplative: '#6366f1',
                hopeful: '#10b981', curious: '#8b5cf6'
            };
            return colors[emotion.toLowerCase()] || '#6366f1';
        }

        async function exportCard(platform) {
            if (!state.posterPath) {
                alert('没有海报可以导出');
                return;
            }
            
            try {
                const response = await fetch('/api/export/card', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        poster_path: state.posterPath,
                        platform: platform
                    })
                });
                
                if (!response.ok) {
                    throw new Error('导出失败');
                }
                
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `soulnote_${platform}_${Date.now()}.png`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
            } catch (error) {
                console.error('导出失败:', error);
                alert('导出失败，请重试。');
            }
        }

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', init);
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

@app.route('/api/analyze/voice', methods=['POST'])
def analyze_voice():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # 保存上传的音频
        audio_filename = f"{uuid.uuid4().hex}.wav"
        audio_path = UPLOAD_FOLDER / audio_filename
        audio_file.save(audio_path)
        
        # 语音转文字
        text = audio_processor.speech_to_text(audio_path)
        
        if not text:
            return jsonify({'error': 'Could not transcribe audio'}), 400
        
        # 分析情感
        emotion_data = ai_client.analyze_emotions(text)
        
        # 生成waveform数据
        waveform_data = audio_processor.generate_waveform_data(audio_path)
        
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
            'waveform_data': waveform_data,
            'audio_filename': audio_filename,
            'timestamp': '2025-11-04T16:00:00'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/poster', methods=['POST'])
def generate_poster():
    try:
        data = request.json
        
        poster_path = poster_generator.create_poster(
            text=data.get('text', ''),
            primary_emotion=data.get('primary_emotion'),
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
    try:
        return send_from_directory(OUTPUT_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/export/card', methods=['POST'])
def export_card():
    try:
        data = request.json
        platform = data.get('platform', 'instagram')
        poster_path = data.get('poster_path')
        
        if not poster_path:
            return jsonify({'error': 'No poster path provided'}), 400
        
        # 简单地返回原始海报（在实际应用中可以调整尺寸）
        poster_filename = Path(poster_path).name
        return send_from_directory(
            OUTPUT_FOLDER, 
            poster_filename,
            as_attachment=True,
            download_name=f'soulnote_{platform}_{poster_filename}'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 启动完整版Soulnote服务器...")
    print(f"🤖 AI提供商: {ai_client.get_provider_info()}")
    print("🌟 访问: http://localhost:5004")
    print("✨ 功能: 语音录制 + 文字输入 + 情感分析 + 视觉海报")
    app.run(debug=True, host='0.0.0.0', port=5004)
