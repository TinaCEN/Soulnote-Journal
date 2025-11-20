#!/usr/bin/env python3
"""
Soulnote - Full Version (Speech + DeepSeek AI)
Use your own API key for full AI features.
"""

from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import os
import sys
import uuid
from pathlib import Path

# Load .env file
def load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

from models.deepseek_client_new import DeepSeekProvider, DeepSeekRealtimeClient, EnhancedOnlineAIClient
from utils.audio_processor import AudioProcessor
from utils.poster_generator import PosterGenerator
from utils.story_card_generator import StoryCardGenerator
from utils.archive_manager import EmotionArchive

app = Flask(__name__)
CORS(app)

# Set DeepSeek API key
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
if DEEPSEEK_API_KEY:
    os.environ['DEEPSEEK_API_KEY'] = DEEPSEEK_API_KEY

# Paths: use this file's directory as project root
PROJECT_ROOT = Path(__file__).parent.resolve()
UPLOAD_FOLDER = PROJECT_ROOT / 'uploads'
OUTPUT_FOLDER = PROJECT_ROOT / 'output'

# Ensure directories exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# Initialize components
try:
    ai_client = EnhancedOnlineAIClient("deepseek")
    deepseek_realtime = DeepSeekRealtimeClient(DEEPSEEK_API_KEY)
    DEEPSEEK_AVAILABLE = True
    print("✅ DeepSeek client initialized")
except Exception as e:
    DEEPSEEK_AVAILABLE = False
    print(f"⚠️ DeepSeek initialization failed: {e}")

audio_processor = AudioProcessor()
poster_generator = PosterGenerator()
story_card_generator = StoryCardGenerator()
archive_manager = EmotionArchive(OUTPUT_FOLDER)

# Helpers
def _normalize_emotions(emotions: dict) -> dict:
    """Ensure emotion scores do not exceed a 100 total.
    - Casts values to float when possible
    - Drops non-numeric values
    - If total > 100, scales down proportionally to sum to 100
    - Rounds to 2 decimal places
    """
    if not isinstance(emotions, dict):
        return {}
    numeric = {}
    for k, v in emotions.items():
        try:
            numeric[k] = float(v)
        except (TypeError, ValueError):
            continue
    total = sum(v for v in numeric.values() if v > 0)
    if total <= 0:
        return {k: 0.0 for k in numeric}
    if total > 100:
        scale = 100.0 / total
        return {k: int(round(max(0.0, v) * scale)) for k, v in numeric.items()}
    return {k: int(round(max(0.0, v))) for k, v in numeric.items()}

# Demo mode sample data
DEMO_EMOTIONS = {
    "joy": {"emotion": "Joy", "confidence": 0.92, "description": "Feeling happiness and contentment"},
    "sadness": {"emotion": "Sadness", "confidence": 0.88, "description": "Experiencing sadness and loss"},
    "calm": {"emotion": "Calm", "confidence": 0.95, "description": "Inner peace and serenity"},
    "confusion": {"emotion": "Confusion", "confidence": 0.78, "description": "Feeling puzzled and lost"},
    "excitement": {"emotion": "Excitement", "confidence": 0.86, "description": "Full of excitement and anticipation"}
}

DEMO_QUOTES = {
    "joy": "Happiness grows when we count our blessings, not our possessions.",
    "sadness": "Tears are not weakness; they are the beginning of healing.",
    "calm": "A still mind reflects who we truly are.",
    "confusion": "Confusion is part of growth; it leads us to our direction.",
    "excitement": "Every beginning carries infinite possibilities."
}

# Check API key configuration
api_key = os.getenv('DEEPSEEK_API_KEY', '')

# Experience mode API key (shared key)
EXPERIENCE_API_KEY = "sk-57ead472ce9b474c85d498c799eaa2e7"

# Use experience key if personal key is not provided
if not api_key and EXPERIENCE_API_KEY:
    api_key = EXPERIENCE_API_KEY
    os.environ['DEEPSEEK_API_KEY'] = api_key
    print("🎉 Using experience API key")

DEMO_MODE = not api_key or api_key == 'your_deepseek_api_key_here'

if DEMO_MODE:
    DEEPSEEK_AVAILABLE = False
    DEEPSEEK_CONNECTED = False
    print("🎭 Running in demo mode - using sample data")
else:
    # Check DeepSeek connection/credits status
    try:
        if DEEPSEEK_AVAILABLE:
            DEEPSEEK_CONNECTED = ai_client.is_connected()
        else:
            DEEPSEEK_CONNECTED = False
    except Exception as e:
        DEEPSEEK_CONNECTED = False
        print(f"DeepSeek connection check failed: {e}")

status_text = '🎭 Demo mode' if DEMO_MODE else ('✅ Connected' if DEEPSEEK_CONNECTED else '❌ Not connected (may require credits)')
print(f"DeepSeek status: {status_text}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soulnote - AI Emotional Journal</title>
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg1: #5a7cff;
            --bg2: #8c5cff;
            --bg3: #ff9b6a;
            --glass: rgba(255,255,255,0.14);
            --glass-strong: rgba(255,255,255,0.22);
            --text: #0b1021;
            --text-soft: #55607a;
            --white: #ffffff;
            --cta: #ffffff;
            --display-font: 'EB Garamond', Georgia, 'Times New Roman', serif;
            --body-font: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
            --panel-height: 260px;
            --panel-radius: 16px;
            --panel-bg: rgba(255,255,255,0.08);
            --panel-border: 1px solid rgba(255,255,255,0.35);
        }

        body {
            font-family: var(--body-font);
            min-height: 100vh;
            margin: 0;
            color: var(--white);
            background:
                radial-gradient(60% 50% at 10% 20%, #8ab9ff55 0%, #ffffff00 70%),
                radial-gradient(60% 50% at 80% 15%, #ff8ad955 0%, #ffffff00 70%),
                radial-gradient(70% 60% at 50% 85%, #ffd68a55 0%, #ffffff00 70%),
                linear-gradient(120deg, var(--bg1), var(--bg2));
            background-attachment: fixed;
            overflow-x: hidden;
        }

        /* Minimal animated background orbs */
        .bg-orbs { position: fixed; inset: 0; z-index: -1; pointer-events: none; filter: saturate(115%); }
        .bg-orbs .orb {
            position: absolute; width: 48vmax; height: 48vmax; border-radius: 999px;
            filter: blur(50px); opacity: 0.42; mix-blend-mode: screen;
            background: radial-gradient(circle at 30% 30%, rgba(138,185,255,0.85) 0%, rgba(138,185,255,0.0) 60%);
            animation: float-a 70s ease-in-out infinite alternate;
        }
        .bg-orbs .orb:nth-child(2) { background: radial-gradient(circle at 60% 40%, rgba(255,138,217,0.85) 0%, rgba(255,138,217,0.0) 62%); animation: float-b 85s ease-in-out infinite alternate; }
        .bg-orbs .orb:nth-child(3) { background: radial-gradient(circle at 40% 60%, rgba(255,214,138,0.85) 0%, rgba(255,214,138,0.0) 60%); animation: float-c 95s ease-in-out infinite alternate; }
        @keyframes float-a { from { transform: translate(-6vmax,-4vmax) scale(1); } to { transform: translate(6vmax,4vmax) scale(1.02); } }
        @keyframes float-b { from { transform: translate(30vmax,-3vmax) scale(0.99); } to { transform: translate(18vmax,5vmax) scale(1.01); } }
        @keyframes float-c { from { transform: translate(-3vmax,22vmax) scale(1.01); } to { transform: translate(8vmax,14vmax) scale(0.99); } }
        @media (prefers-reduced-motion: reduce) {
            .bg-orbs .orb { animation: none; }
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            color: #e8ecff;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 600;
            font-size: 12px;
            padding: 14px 4px 8px 4px;
        }

        .api-status {
            background: transparent;
            padding: 8px 12px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.25);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            backdrop-filter: blur(6px);
        }

        .api-status.connected {
            border-color: rgba(16, 185, 129, 0.6);
        }

        .api-status.disconnected {
            border-color: rgba(239, 68, 68, 0.6);
        }

        .hero {
            text-align: center;
            padding: 40px 0 10px 0;
        }

        .hero h1 {
            font-size: clamp(42px, 10vw, 92px);
            font-weight: 800;
            letter-spacing: 0.04em;
            margin: 18px 0 10px 0;
            text-transform: uppercase;
            color: #ffffff;
            font-family: var(--display-font);
        }

        .hero p {
            font-size: clamp(16px, 2.2vw, 28px);
            color: #e9ecff;
            opacity: 0.95;
            margin-bottom: 26px;
            font-family: var(--display-font);
        }

        .hero .hint { font-size: clamp(14px, 1.8vw, 18px); opacity: .95; color: #eef1ff; margin-top: -6px; }
        .helper-hint { text-align:center; color:#eaf0ff; opacity:.9; margin:10px 0 6px 0; font-size:14px; }

        /* Daily Prompt removed for a minimal look */

        /* Removed external CTAs per request */

        .card {
            background: linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.12));
            border: 1px solid rgba(255,255,255,0.28);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 28px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.18);
            margin-bottom: 20px;
            color: #0e1330;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }

        .tab-btn {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid rgba(255,255,255,0.35);
            background: rgba(255,255,255,0.08);
            color: #fff;
            border-radius: 999px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.25s;
            backdrop-filter: blur(8px);
        }
        .tab-btn.active { background: rgba(255,255,255,0.28); border-color: rgba(255,255,255,0.65); box-shadow: 0 0 0 2px rgba(255,255,255,0.25) inset, 0 8px 24px rgba(0,0,0,0.12); }

        .tab-content {
            display: none;
            /* Ensure identical overall panel height for Voice and Text */
            min-height: calc(var(--panel-height) + 130px);
            padding-bottom: 10px;
        }

        .tab-content.active {
            display: block;
        }

        .voice-visualizer {
            width: 100%;
            height: var(--panel-height);
            background: var(--panel-bg);
            border-radius: var(--panel-radius);
            margin-bottom: 20px;
            position: relative;
            border: var(--panel-border);
        }

        .voice-visualizer.recording { box-shadow: 0 0 0 2px rgba(255,255,255,0.18) inset, 0 12px 30px rgba(0,0,0,0.14); border-color: rgba(255,255,255,0.5); animation: vglow 2.2s ease-in-out infinite; }
        @keyframes vglow { 0%,100% { box-shadow: 0 0 0 2px rgba(255,255,255,0.18) inset, 0 12px 30px rgba(0,0,0,0.14); } 50% { box-shadow: 0 0 0 2px rgba(255,255,255,0.30) inset, 0 16px 40px rgba(0,0,0,0.16); } }

        .voice-visualizer canvas {
            width: 100%;
            height: 100%;
        }

        .voice-placeholder { position:absolute; top:16px; left:16px; font-size: 1.1rem; color: rgba(20,32,60,0.6); pointer-events:none; }

        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }

        .btn-primary { background: rgba(255,255,255,0.14); color: #fff; border: 1px solid rgba(255,255,255,0.4); }
        .btn-primary:hover { background: rgba(255,255,255,0.22); transform: translateY(-2px); }

        .btn-danger {
            background: #ef4444cc;
            color: white;
        }

        .btn-success {
            background: #10b981cc;
            color: white;
        }

        textarea {
            width: 100%;
            height: var(--panel-height); /* match Voice visualizer height */
            padding: 15px;
            border: var(--panel-border);
            background: var(--panel-bg);
            color: #fff;
            border-radius: var(--panel-radius);
            font-size: 1.1rem;
            font-family: inherit;
            resize: none !important; /* remove handle to avoid artifacts */
            margin-bottom: 20px; /* align with visualizer spacing */
            overflow-y: auto;
        }

        textarea:focus { outline: none; border-color: rgba(255,255,255,0.6); }

        .results {
            display: none;
        }

        .results.show {
            display: block;
        }

        .emotion-display { text-align: center; padding: 30px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.3); border-radius: 18px; margin-bottom: 20px; color: #fff; }

        .primary-emotion {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 20px;
            text-transform: uppercase;
        }

        .emotions-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 20px;
        }

        .emotion-card {
            background: #ffffff;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
            color: #4f62c7; /* readable on white cards */
            min-height: 86px;
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            box-shadow: inset 0 0 0 1px rgba(102,126,234,0.08);
        }

        .emotion-name {
            font-weight: 600;
            margin-bottom: 4px;
            color: #4f62c7;
        }

        .emotion-score {
            font-size: 1.5rem;
            color: #4f62c7;
        }

        .emotion-card.top {
            border: 2px solid #f59e0b; /* amber */
            box-shadow: 0 12px 30px rgba(245, 158, 11, 0.25);
            position: relative;
        }

        .emotion-card.top::before {
            content: '★';
            position: absolute;
            top: -10px;
            left: -10px;
            background: #f59e0b;
            color: #fff;
            font-size: 12px;
            padding: 4px 6px;
            border-radius: 999px;
        }

        .philosophical { background: rgba(255,255,255,0.08); padding: 25px; border-radius: 18px; border: 1px solid rgba(255,255,255,0.3); margin: 20px 0; color: #eaf0ff; }

        .philosophical-text { font-size: 1.1rem; line-height: 1.8; color: #eef3ff; font-style: italic; }

        .sharecard-container {
            text-align: center;
            margin: 20px 0;
        }

        /* Shared centered action row for primary buttons */
        .action-row { display:flex; align-items:center; justify-content:center; gap:12px; margin-top: 6px; }
        .action-row .btn { margin: 8px; }

        /* Archive-only mode hides other UI */
        .archive-only .hero { display:none; }
        .archive-only .tabs { display:none; }
        .archive-only #results, .archive-only #voiceTab, .archive-only #textTab, .archive-only #loading { display:none !important; }

        /* Archive detail modal layout */
        .archive-modal { position:fixed; inset:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:50; }
        .archive-modal .inner { background:linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.12)); border:1px solid rgba(255,255,255,0.3); backdrop-filter: blur(12px); border-radius:20px; width:min(980px,92vw); max-height:90vh; overflow:auto; padding:20px; color:#fff; }
        .archive-modal .header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
        .archive-modal .grid { display:grid; grid-template-columns: minmax(240px, 380px) 1fr; gap:16px; align-items:start; }
        .archive-modal img { width:100%; height:auto; max-height:62vh; object-fit:contain; border-radius:12px; }
        @media (max-width: 860px) { .archive-modal .grid { grid-template-columns: 1fr; } }

        .sharecard-container img {
            max-width: 100%;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            100% { transform: rotate(360deg); }
        }

        .hidden {
            display: none !important;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .card {
                padding: 20px;
            }
            
            .emotions-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="bg-orbs" aria-hidden="true">
        <span class="orb"></span>
        <span class="orb"></span>
        <span class="orb"></span>
    </div>
    <div class="container">
        <div class="topbar">
            <div id="apiStatus" class="api-status"><span id="statusText">Checking API status...</span></div>
            <div style="display:flex; gap:16px; align-items:center;">
                <a id="openArchiveLink" style="color:#e8ecff; text-decoration:none; border-bottom:0; padding-bottom:2px; cursor:pointer;">ARCHIVE</a>
                <a id="openHomeLink" style="color:#e8ecff; text-decoration:none; border-bottom:0; padding-bottom:2px; cursor:pointer;">HOME</a>
            </div>
        </div>

        <section class="hero">
            <h1>SOULNOTE</h1>
            <p>AI-powered emotional journaling</p>
        </section>

        <div class="card">
            <div class="tabs">
                <button class="tab-btn active" data-tab="voice">Voice</button>
                <button class="tab-btn" data-tab="text">Text</button>
            </div>

            <div id="voiceTab" class="tab-content active">
                <div class="voice-visualizer" id="visualizer">
                    <div class="voice-placeholder" id="voicePlaceholder">Share your thoughts and feelings here...</div>
                    <canvas id="canvas"></canvas>
                </div>
                <div class="action-row">
                    <button id="recordBtn" class="btn btn-primary">Start Recording</button>
                </div>
                <div id="audioPlayback" class="hidden" style="margin-top: 20px; text-align:center;">
                    <audio id="audioElement" controls style="width: 100%;"></audio>
                    <button id="analyzeVoiceBtn" class="btn btn-success" style="margin-top:12px;">Transcribe Audio</button>
                </div>
                <div id="voiceEditBlock" class="hidden" style="margin-top:26px;">
                    <div class="transcription-title" style="font-weight:700; color:#0b1021; background:rgba(255,255,255,0.85); display:inline-block; padding:10px 14px; border-radius:12px; margin-bottom:10px;">Transcription</div>
                    <textarea id="voiceTextEdit" placeholder="Review and edit the transcribed text..."></textarea>
                    <button id="analyzeFromVoiceTextBtn" class="btn btn-primary" style="display:block; margin: 12px auto 0;">Analyze Edited Text</button>
                </div>
            </div>

            <div id="textTab" class="tab-content">
                <textarea id="textInput" placeholder="Share your thoughts and feelings here..."></textarea>
                <div class="action-row"><button id="analyzeTextBtn" class="btn btn-primary">Analyze Text</button></div>
            </div>

            <div id="archiveTab" class="tab-content">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
                    <h3>Your Emotion Archive</h3>
                    <button id="refreshArchiveBtn" class="btn">Refresh</button>
                </div>
                <div id="trends" class="card" style="color:#fff;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0;">Emotion Trends (last 30 days)</h4>
                        <small id="trendSummary" style="opacity:.9;"></small>
                    </div>
                    <canvas id="trendChart" width="900" height="200" style="width:100%;"></canvas>
                </div>
                <div id="archiveGrid" style="display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:12px;"></div>
                <!-- Modal for archive details -->
                <div id="archiveModal" class="hidden archive-modal">
                    <div class="inner">
                        <div class="header">
                            <div>
                                <div id="modalDate" style="font-size:12px; opacity:0.9;"></div>
                                <div id="modalEmotion" style="font-size:18px; font-weight:700; text-transform:uppercase;"></div>
                            </div>
                            <button id="closeArchiveModal" class="btn">Close</button>
                        </div>
                        <div class="grid">
                            <div>
                                <img id="modalImage" src="" alt="card" />
                            </div>
                            <div>
                                <div id="modalPhilosophy" style="font-style:italic; line-height:1.7; font-size:16px; margin-bottom:12px;"></div>
                                <div id="modalPromptWrap" style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.25); border-radius:12px; padding:12px;">
                                    <div id="modalPromptTitle" style="font-weight:600; font-size:13px; opacity:.95; margin-bottom:6px;">Original entry</div>
                                    <div id="modalPrompt" style="white-space:pre-wrap; line-height:1.6; font-size:14px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p id="loadingText">AI is analyzing...</p>
            </div>

            <div id="results" class="results">
                <div id="transcriptSection" class="hidden" style="background: #f9fafb; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                    <h3>Transcription</h3>
                    <p id="transcriptText"></p>
                </div>

                <div class="emotion-display">
                    <div class="primary-emotion" id="primaryEmotion"></div>
                    <div class="emotions-grid" id="emotionsGrid"></div>
                </div>

                <div class="philosophical">
                    <h3 style="margin-bottom: 15px;">Philosophical Reflection</h3>
                    <div class="philosophical-text" id="philosophicalText"></div>
                </div>

                <div class="sharecard-container">
                    <h3>Share Card</h3>
                    <img id="shareCardImage" src="" alt="Share Card" style="display: none;">
                    <p id="shareCardLoading">Generating card...</p>
                    <div style="margin-top:10px;">
                        <a id="downloadCardBtn" class="btn btn-primary" href="#" download style="display:none;">Download Image</a>
                    </div>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <button id="resetBtn" class="btn btn-primary">Start New Analysis</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let isRecording = false;
        let mediaRecorder = null;
        let audioChunks = [];
        let audioBlob = null;
        let visPhase = 0; // smooth phase for minimal visualizer

        // Tab management helpers
        function setActiveTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            const content = document.getElementById(tab + 'Tab');
            if (content) content.classList.add('active');
            const tabBtn = document.querySelector(`[data-tab="${tab}"]`);
            if (tabBtn) tabBtn.classList.add('active');
            if (tab === 'archive') {
                document.body.classList.add('archive-only');
                loadArchive();
            } else {
                document.body.classList.remove('archive-only');
            }
        }
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => setActiveTab(btn.dataset.tab));
        });

        // Check API status (minimal text, no emojis)
        fetch('/api/status')
            .then(r => r.json())
            .then(data => {
                const status = document.getElementById('apiStatus');
                const statusText = document.getElementById('statusText');
                if (data.demo_mode) {
                    status.className = 'api-status connected';
                    statusText.textContent = data.message;
                } else if (data.connected) {
                    status.className = 'api-status connected';
                    statusText.textContent = `DeepSeek AI connected`;
                } else {
                    status.className = 'api-status disconnected';
                    statusText.textContent = data.message || 'API not connected';
                }
            });
        // CTA quick switches
        document.getElementById('openArchiveLink').addEventListener('click', () => {
            setActiveTab('archive');
        });
        document.getElementById('openHomeLink').addEventListener('click', () => {
            resetUI();
        });

        // Recording
        document.getElementById('recordBtn').addEventListener('click', toggleRecording);


        async function toggleRecording() {
            const btn = document.getElementById('recordBtn');
            const visualizer = document.getElementById('visualizer');
            
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = async () => {
                        audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        document.getElementById('audioElement').src = URL.createObjectURL(audioBlob);
                        document.getElementById('audioPlayback').classList.remove('hidden');
                        await transcribeAudio();
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    btn.textContent = 'Stop Recording';
                    btn.className = 'btn btn-danger';
                    visualizer.classList.add('recording');
                    const ph = document.getElementById('voicePlaceholder');
                    if (ph) ph.style.display = 'none';
                    animateVisualizer();
                } catch (err) {
                    alert('Cannot access microphone: ' + err.message);
                }
            } else {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(t => t.stop());
                isRecording = false;
                btn.textContent = 'Start Recording';
                btn.className = 'btn btn-primary';
                visualizer.classList.remove('recording');
                const ph = document.getElementById('voicePlaceholder');
                if (ph) ph.style.display = '';
            }
        }
        async function transcribeAudio() {
            try {
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.wav');
                const response = await fetch('/api/transcribe/voice', { method: 'POST', body: formData });
                const data = await response.json();
                if (response.ok) {
                    const block = document.getElementById('voiceEditBlock');
                    const ta = document.getElementById('voiceTextEdit');
                    ta.value = data.text || '';
                    block.classList.remove('hidden');
                }
            } catch (err) {
                console.error('Transcription failed', err);
            }
        }


        function animateVisualizer() {
            if (!isRecording) return;
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            
            function draw() {
                if (!isRecording) return;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const w = canvas.width, h = canvas.height;
                const bars = Math.max(28, Math.floor(w / 18));
                const barWidth = w / bars;
                const centerY = h / 2;
                const gradient = ctx.createLinearGradient(0, 0, 0, h);
                gradient.addColorStop(0, 'rgba(170,191,255,0.9)');
                gradient.addColorStop(1, 'rgba(202,168,255,0.9)');
                ctx.lineCap = 'round';
                ctx.strokeStyle = gradient;
                ctx.lineWidth = Math.max(2, barWidth * 0.38);

                for (let i = 0; i < bars; i++) {
                    const t = visPhase + i * 0.33;
                    const amp = 0.25 + 0.55 * (0.5 + Math.sin(t) * 0.5);
                    const height = amp * h * 0.7;
                    const x = i * barWidth + barWidth / 2;
                    ctx.beginPath();
                    ctx.moveTo(x, centerY - height / 2);
                    ctx.lineTo(x, centerY + height / 2);
                    ctx.stroke();
                }
                visPhase += 0.04;
                requestAnimationFrame(draw);
            }
            draw();
        }

        // Analyze voice
        document.getElementById('analyzeVoiceBtn').addEventListener('click', async () => {
            if (!audioBlob) { alert('Record audio first'); return; }
            // Only transcribe first; analysis is done via the edited text button
            await transcribeAudio();
            const block = document.getElementById('voiceEditBlock');
            block.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });

        // Analyze text
        document.getElementById('analyzeTextBtn').addEventListener('click', async () => {
            const text = document.getElementById('textInput').value.trim();
            if (!text) {
                alert('Please enter text');
                return;
            }
            
            showLoading('Analyzing text...');
            
            try {
                const response = await fetch('/api/analyze/text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                
                const data = await response.json();
                if (response.ok) {
                    data.source = 'text';
                    await generateStoryCard(data);
                    displayResults(data, false);
                } else {
                    alert(data.error || 'Analysis failed');
                    hideLoading();
                }
            } catch (err) {
                alert('Analysis failed: ' + err.message);
                hideLoading();
            }
        });

        // Analyze edited text from voice transcription
        document.getElementById('analyzeFromVoiceTextBtn').addEventListener('click', async () => {
            const text = document.getElementById('voiceTextEdit').value.trim();
            if (!text) { alert('Please enter text'); return; }
            showLoading('Analyzing text...');
            try {
                const response = await fetch('/api/analyze/text', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
                const data = await response.json();
                if (response.ok) {
                    data.source = 'audio';
                    data.text = text;
                    await generateStoryCard(data);
                    displayResults(data, false);
                } else {
                    alert(data.error || 'Analysis failed');
                    hideLoading();
                }
            } catch (err) {
                alert('Analysis failed: ' + err.message);
                hideLoading();
            }
        });

        async function generateStoryCard(data) {
            document.getElementById('loadingText').textContent = 'Generating share card...';
            try {
                const response = await fetch('/api/generate/story-card', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    document.getElementById('shareCardImage').src = result.card_url;
                    document.getElementById('shareCardImage').style.display = 'block';
                    document.getElementById('shareCardLoading').style.display = 'none';
                    const downloadBtn = document.getElementById('downloadCardBtn');
                    downloadBtn.href = result.card_url;
                    downloadBtn.style.display = 'inline-block';
                }
            } catch (err) {
                document.getElementById('shareCardLoading').textContent = 'Card generation failed';
            }
        }

        function displayResults(data, isVoice) {
            if (isVoice && data.text) {
                document.getElementById('transcriptText').textContent = data.text;
                document.getElementById('transcriptSection').classList.remove('hidden');
            }
            
            document.getElementById('primaryEmotion').textContent = (data.primary_emotion || '').toUpperCase();
            
            const grid = document.getElementById('emotionsGrid');
            grid.innerHTML = '';
            const entries = Object.entries(data.emotions).sort((a, b) => b[1] - a[1]);
            for (const [emotion, score] of entries) {
                const topClass = emotion === data.primary_emotion ? ' top' : '';
                grid.innerHTML += `
                    <div class="emotion-card${topClass}">
                        <div class="emotion-name">${emotion}</div>
                        <div class="emotion-score">${Math.round(score)}%</div>
                    </div>
                `;
            }
            
            document.getElementById('philosophicalText').textContent = data.philosophical_note;
            
            hideLoading();
            document.getElementById('results').classList.add('show');
        }

        function showLoading(text) {
            document.getElementById('loadingText').textContent = text;
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
        }

        function hideLoading() {
            document.getElementById('loading').classList.remove('show');
        }

        document.getElementById('resetBtn').addEventListener('click', () => resetUI());

        function resetUI() {
            try { hideLoading(); } catch(e) {}
            // Stop recording if active
            if (isRecording && mediaRecorder) {
                try { mediaRecorder.stop(); } catch(e) {}
                try { mediaRecorder.stream.getTracks().forEach(t => t.stop()); } catch(e) {}
                isRecording = false;
            }
            const visualizer = document.getElementById('visualizer');
            if (visualizer) visualizer.classList.remove('recording');
            const ph = document.getElementById('voicePlaceholder');
            if (ph) ph.style.display = '';
            // Clear audio state
            audioChunks = [];
            audioBlob = null;
            const audioEl = document.getElementById('audioElement');
            if (audioEl) { audioEl.pause(); audioEl.src = ''; }
            const playback = document.getElementById('audioPlayback');
            if (playback) playback.classList.add('hidden');
            // Clear text inputs
            const taText = document.getElementById('textInput');
            if (taText) taText.value = '';
            const voiceEdit = document.getElementById('voiceTextEdit');
            if (voiceEdit) voiceEdit.value = '';
            const voiceBlock = document.getElementById('voiceEditBlock');
            if (voiceBlock) voiceBlock.classList.add('hidden');
            // Results area
            const res = document.getElementById('results');
            if (res) res.classList.remove('show');
            const grid = document.getElementById('emotionsGrid');
            if (grid) grid.innerHTML = '';
            const prim = document.getElementById('primaryEmotion');
            if (prim) prim.textContent = '';
            const phil = document.getElementById('philosophicalText');
            if (phil) phil.textContent = '';
            const transcriptSec = document.getElementById('transcriptSection');
            if (transcriptSec) transcriptSec.classList.add('hidden');
            // Share card visuals
            const img = document.getElementById('shareCardImage');
            if (img) { img.style.display = 'none'; img.src = ''; }
            const loadingP = document.getElementById('shareCardLoading');
            if (loadingP) { loadingP.style.display = 'block'; loadingP.textContent = 'Generating card...'; }
            const dBtn = document.getElementById('downloadCardBtn');
            if (dBtn) dBtn.style.display = 'none';
            // Reset record button UI
            const rBtn = document.getElementById('recordBtn');
            if (rBtn) { rBtn.textContent = 'Start Recording'; rBtn.className = 'btn btn-primary'; }
            // Return to home (Voice tab) and ensure non-archive mode
            setActiveTab('voice');
            document.body.classList.remove('archive-only');
        }

        document.getElementById('refreshArchiveBtn').addEventListener('click', loadArchive);

        async function loadArchive() {
            const grid = document.getElementById('archiveGrid');
            grid.innerHTML = '<p>Loading...</p>';
            try {
                const res = await fetch('/api/archive/list?limit=100');
                const data = await res.json();
                const entries = data.entries || [];
                if (!entries.length) { grid.innerHTML = '<p>No entries yet.</p>'; return; }
                // Build trends chart
                buildTrends(entries);
                grid.innerHTML = entries.map((e, idx) => `
                    <div class="card" data-index="${idx}" style="padding:10px; cursor:pointer;">
                        <div style="font-size:12px; color:#e7ebff; margin-bottom:6px;">${e.date} • ${e.primary_emotion?.toUpperCase?.() || ''}</div>
                        <img src="${e.card_url}" alt="card" style="width:100%; border-radius:10px;">
                        <div style="font-size:12px; color:#e7ebff; margin-top:6px;">${e.summary || ''}</div>
                    </div>
                `).join('');
                // Bind click to open modal with philosophy
                const cards = grid.querySelectorAll('.card');
                cards.forEach(card => {
                    card.addEventListener('click', () => {
                        const i = Number(card.getAttribute('data-index'));
                        const e = entries[i];
                        document.getElementById('modalDate').textContent = e.date || '';
                        document.getElementById('modalEmotion').textContent = (e.primary_emotion || '').toUpperCase();
                        document.getElementById('modalImage').src = e.card_url || '';
                        document.getElementById('modalPhilosophy').textContent = e.philosophical_note || '(No reflection saved)';
                        document.getElementById('modalPrompt').textContent = e.text || '(No original entry)';
                        const title = (e.source === 'audio') ? 'Original audio' : 'Original text';
                        document.getElementById('modalPromptTitle').textContent = title;
                        document.getElementById('archiveModal').classList.remove('hidden');
                    });
                });
            } catch (err) {
                grid.innerHTML = '<p>Failed to load archive.</p>';
            }
        }

        document.getElementById('closeArchiveModal').addEventListener('click', () => {
            document.getElementById('archiveModal').classList.add('hidden');
        });

        // Trends drawing
        const EMO_COLORS = {
            joy: '#FFD166', happiness:'#FFD166', sadness:'#5B8DEF', anger:'#FF6B6B', fear:'#9B5DE5', surprise:'#F7971E', disgust:'#2ECC71', love:'#FF69B4', anxiety:'#7A5AF8', peace:'#2ED1C4', neutral:'#9AA0A6', trust:'#5EC8E5', anticipation:'#90EE90', calm:'#60E1DC', confusion:'#A0AEC0'
        };
        function buildTrends(entries) {
            const byEmotion = {};
            const now = new Date();
            const cutoff = new Date(now.getTime() - 30*24*3600*1000);
            for (const e of entries) {
                const ts = new Date(e.timestamp || e.date);
                if (ts < cutoff) continue;
                const p = (e.primary_emotion || 'neutral').toLowerCase();
                byEmotion[p] = (byEmotion[p] || 0) + 1;
            }
            const ctx = document.getElementById('trendChart').getContext('2d');
            const labels = Object.keys(byEmotion).sort((a,b)=>byEmotion[b]-byEmotion[a]).slice(0,8);
            const total = labels.reduce((acc,k)=>acc+byEmotion[k],0) || 1;
            // Clear
            ctx.clearRect(0,0,ctx.canvas.width, ctx.canvas.height);
            const barH = 18, gap = 10; let y = 14;
            labels.forEach(lbl => {
                const val = byEmotion[lbl];
                const pct = val/total;
                const w = Math.max(8, Math.floor((ctx.canvas.width-140) * pct));
                ctx.fillStyle = EMO_COLORS[lbl] || '#ffffff';
                ctx.fillRect(120, y, w, barH);
                ctx.fillStyle = '#eaf0ff';
                ctx.font = '14px Inter';
                ctx.fillText(lbl.toUpperCase(), 10, y+barH-4);
                ctx.fillText(String(val), 120 + w + 8, y+barH-4);
                y += barH + gap;
            });
            document.getElementById('trendSummary').textContent = `${total} entries`;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    """检查API状态"""
    if DEMO_MODE:
        return jsonify({
            'connected': True,
            'demo_mode': True,
            'provider': 'Demo Mode',
            'message': '🎭 Demo mode - using sample data'
        })
    else:
        return jsonify({
            'connected': DEEPSEEK_CONNECTED,
            'demo_mode': False,
            'provider': 'DeepSeek',
            'message': '✅ DeepSeek connected' if DEEPSEEK_CONNECTED else '⚠️ Please add credits to your DeepSeek account'
        })

@app.route('/api/analyze/voice', methods=['POST'])
def analyze_voice():
    """Analyze voice input"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Please provide an audio file'}), 400
        
        audio_file = request.files['audio']
        audio_filename = f"{uuid.uuid4().hex}.wav"
        audio_path = UPLOAD_FOLDER / audio_filename
        audio_file.save(audio_path)
        
        # Speech to text
        text = audio_processor.speech_to_text(audio_path)
        
        if not text:
            return jsonify({'error': 'Speech recognition failed, please try again'}), 400
        
        # Emotion analysis
        if DEEPSEEK_CONNECTED:
            emotion_data = deepseek_realtime.analyze_emotions_realtime(text)
            philosophical_note = deepseek_realtime.generate_philosophical_note_realtime(
                emotion_data.get('primary_emotion', 'neutral'),
                emotion_data.get('emotions', {}),
                text
            )
        else:
            # Fallback
            emotion_data = {
                'primary_emotion': 'neutral',
                'emotions': {'joy': 30, 'sadness': 20, 'anger': 10, 'fear': 10, 'surprise': 10, 'disgust': 5, 'peace': 45}
            }
            philosophical_note = "Every emotion is a color of life, forming a unique life canvas."
        
        waveform_data = audio_processor.generate_waveform_data(audio_path)
        # Normalize emotion scores so total <= 100
        normalized_emotions = _normalize_emotions(emotion_data.get('emotions', {}))
        
        return jsonify({
            'text': text,
            'primary_emotion': emotion_data.get('primary_emotion'),
            'emotions': normalized_emotions,
            'philosophical_note': philosophical_note,
            'waveform_data': waveform_data,
            'audio_filename': audio_filename
        })
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Analyze text input"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Please provide text content'}), 400
        
        # Emotion analysis
        if DEEPSEEK_CONNECTED and not DEMO_MODE:
            emotion_data = deepseek_realtime.analyze_emotions_realtime(text)
            philosophical_note = deepseek_realtime.generate_philosophical_note_realtime(
                emotion_data.get('primary_emotion', 'neutral'),
                emotion_data.get('emotions', {}),
                text
            )
        else:
            # Demo mode: choose emotion by keywords
            import random
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['开心', '快乐', '高兴', 'happy', 'joy', '兴奋', '满意']):
                demo_key = 'joy'
            elif any(word in text_lower for word in ['难过', '伤心', 'sad', '悲伤', '失落', '沮丧']):
                demo_key = 'sadness'
            elif any(word in text_lower for word in ['平静', 'calm', '安静', '宁静', '放松']):
                demo_key = 'calm'
            elif any(word in text_lower for word in ['困惑', 'confused', '迷茫', '不知道', '混乱']):
                demo_key = 'confusion'
            else:
                demo_key = random.choice(list(DEMO_EMOTIONS.keys()))
            
            demo_emotion = DEMO_EMOTIONS[demo_key]
            emotion_data = {
                'primary_emotion': demo_emotion['emotion'],
                'emotions': {demo_emotion['emotion']: int(demo_emotion['confidence'] * 100)},
                'description': demo_emotion['description']
            }
            philosophical_note = DEMO_QUOTES[demo_key]
        # Normalize emotion scores so total <= 100
        normalized_emotions = _normalize_emotions(emotion_data.get('emotions', {}))

        return jsonify({
            'text': text,
            'primary_emotion': emotion_data.get('primary_emotion'),
            'emotions': normalized_emotions,
            'philosophical_note': philosophical_note
        })
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/generate/poster', methods=['POST'])
def generate_poster():
    """Generate poster"""
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
        return jsonify({'error': f'Poster generation failed: {str(e)}'}), 500

@app.route('/api/generate/story-card', methods=['POST'])
def generate_story_card():
    """Generate a shareable story card with reflection text and blended background."""
    try:
        data = request.json or {}
        philosophical_text = data.get('philosophical_note', '')
        emotions = data.get('emotions', {})
        user_text = data.get('text', '')
        card_path = story_card_generator.create_story_card(philosophical_text, emotions, user_text)
        # Compose archive summary similar to the one shown on card
        def compose_summary(emotions: dict) -> str:
            # Use top 3 emotions
            items = sorted(((k, v) for k, v in emotions.items()), key=lambda x: x[1], reverse=True)[:3]
            names = [k for k, _ in items]
            if not names:
                return 'Today I feel balanced.'
            if len(names) == 1:
                return f"Today I feel {names[0]}."
            if len(names) == 2:
                return f"Today I feel {names[0]} with shades of {names[1]}."
            return f"Today I feel {names[0]} with hints of {names[1]} and {names[2]}."

        summary = compose_summary(emotions)
        archive_entry = archive_manager.add_entry(
            primary_emotion=data.get('primary_emotion', ''),
            emotions=emotions,
            card_path=str(card_path),
            summary=summary,
            text=user_text or data.get('text', ''),
            philosophical_note=philosophical_text,
            source=(data.get('source') or 'text')
        )
        return jsonify({
            'card_path': str(card_path),
            'card_url': f'/api/output/{card_path.name}'
        })
    except Exception as e:
        return jsonify({'error': f'Card generation failed: {str(e)}'}), 500

@app.route('/api/archive/list')
def archive_list():
    try:
        limit = request.args.get('limit', type=int)
        entries = archive_manager.list_entries(limit=limit)
        # Convert local file paths to URLs
        for e in entries:
            p = Path(e.get('card_path', ''))
            e['card_url'] = f'/api/output/{p.name}' if p.name else ''
        return jsonify({'entries': entries})
    except Exception as e:
        return jsonify({'error': f'List failed: {str(e)}'}), 500

@app.route('/api/archive/stats')
def archive_stats():
    try:
        days = request.args.get('days', type=int)
        data = archive_manager.stats(days=days)
        return jsonify({'stats': data})
    except Exception as e:
        return jsonify({'error': f'Stats failed: {str(e)}'}), 500

@app.route('/api/output/<filename>')
def get_output_file(filename):
    """Get output file"""
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/api/transcribe/voice', methods=['POST'])
def transcribe_voice():
    """Return only the transcription for a recorded audio clip (no emotion analysis)."""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Please provide an audio file'}), 400
        audio_file = request.files['audio']
        audio_filename = f"{uuid.uuid4().hex}.wav"
        audio_path = UPLOAD_FOLDER / audio_filename
        audio_file.save(audio_path)
        text = audio_processor.speech_to_text(audio_path)
        return jsonify({'text': text or ''})
    except Exception as e:
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Soulnote - AI Emotional Journal...")
    
    if DEMO_MODE:
        print("🎭 Mode: Demo")
        print("🔑 API: Using sample data")
        print("🧠 AI: Demo mode (all features available)")
    else:
        if EXPERIENCE_API_KEY and api_key == EXPERIENCE_API_KEY:
            print("🎉 Mode: Experience")
            print("🔑 API: Using shared experience key")
            print("🧠 AI: ✅ Real AI analysis enabled")
        else:
            print(f"🔑 DeepSeek API: {'✅ Configured' if DEEPSEEK_API_KEY else '❌ Not configured'}")
            print(f"🧠 AI: {'✅ Connected' if DEEPSEEK_CONNECTED else '⚠️  Not connected (add credits to enable)'}")
    
    print(f"🎤 Speech recognition: ✅ Ready")
    print(f"🎨 Poster generation: ✅ Ready")
    print("\n🌟 Visit: http://localhost:5007")
    print("\n💡 Tips:")
    
    if DEMO_MODE:
        print("   - Currently in demo mode, using sample data")
        print("   - Configure an API key to enable real AI analysis")
        print("   - See API_SETUP_GUIDE.md for details")
    elif EXPERIENCE_API_KEY and api_key == EXPERIENCE_API_KEY:
        print("   - 🎉 Experience: real AI emotion analysis enabled")
        print("   - 💬 Try voice recording and text input")
        print("   - 🧠 AI provides personalized emotional insights")
        print("   - 📖 Receive philosophical reflections")
    elif not DEEPSEEK_CONNECTED:
        print("   - Your DeepSeek account needs credits to use AI features")
        print("   - Add credits at: https://platform.deepseek.com")
        print("   - AI analysis will be enabled automatically afterward")
    
    print("   - Supports voice recording and text input")
    print("   - Automatically generates emotion posters\n")
    
    app.run(debug=True, host='0.0.0.0', port=5007)
