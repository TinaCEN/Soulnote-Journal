// Soulnote Frontend JavaScript

const API_BASE_URL = 'http://localhost:5000/api';

// State management
const state = {
    isRecording: false,
    mediaRecorder: null,
    audioChunks: [],
    audioBlob: null,
    currentAnalysis: null,
    posterPath: null
};

// DOM Elements
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Voice tab
    recordBtn: document.getElementById('recordBtn'),
    recordBtnIcon: document.getElementById('recordBtnIcon'),
    recordBtnText: document.getElementById('recordBtnText'),
    audioPlayback: document.getElementById('audioPlayback'),
    audioElement: document.getElementById('audioElement'),
    analyzeVoiceBtn: document.getElementById('analyzeVoiceBtn'),
    visualizerCanvas: document.getElementById('visualizerCanvas'),
    
    // Text tab
    journalText: document.getElementById('journalText'),
    analyzeTextBtn: document.getElementById('analyzeTextBtn'),
    
    // Sections
    inputSection: document.getElementById('inputSection'),
    loadingSection: document.getElementById('loadingSection'),
    resultsSection: document.getElementById('resultsSection'),
    loadingText: document.getElementById('loadingText'),
    
    // Status
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),
    
    // Results
    transcribedTextContainer: document.getElementById('transcribedTextContainer'),
    transcribedText: document.getElementById('transcribedText'),
    primaryEmotion: document.getElementById('primaryEmotion'),
    emotionsList: document.getElementById('emotionsList'),
    philosophicalNote: document.getElementById('philosophicalNote'),
    posterImage: document.getElementById('posterImage'),
    
    // Actions
    exportBtns: document.querySelectorAll('.btn-export'),
    newJourneyBtn: document.getElementById('newJourneyBtn')
};

// Initialize app
async function init() {
    setupEventListeners();
    await checkServerHealth();
    setupVisualizer();
}

// Event Listeners
function setupEventListeners() {
    // Tab switching
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Voice recording
    elements.recordBtn.addEventListener('click', toggleRecording);
    elements.analyzeVoiceBtn.addEventListener('click', analyzeVoice);
    
    // Text analysis
    elements.analyzeTextBtn.addEventListener('click', analyzeText);
    
    // Export buttons
    elements.exportBtns.forEach(btn => {
        btn.addEventListener('click', () => exportCard(btn.dataset.platform));
    });
    
    // New journey
    elements.newJourneyBtn.addEventListener('click', resetApp);
}

// Tab Management
function switchTab(tabName) {
    elements.tabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}Tab`);
    });
}

// Server Health Check
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatus('Connected to AI', 'connected');
            if (!data.lmstudio_connected) {
                updateStatus('Warning: LM Studio not connected', 'error');
            }
        } else {
            updateStatus('Server error', 'error');
        }
    } catch (error) {
        updateStatus('Cannot connect to server', 'error');
        console.error('Health check failed:', error);
    }
}

function updateStatus(message, type = '') {
    elements.statusText.textContent = message;
    elements.statusIndicator.className = `status-indicator ${type}`;
}

// Voice Recording
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
        
        // Try WAV format first, fall back to webm
        let options = { mimeType: 'audio/wav' };
        if (!MediaRecorder.isTypeSupported('audio/wav')) {
            console.log('WAV not supported, using webm');
            options = { mimeType: 'audio/webm' };
        }
        
        state.mediaRecorder = new MediaRecorder(stream, options);
        state.audioChunks = [];
        
        console.log('MediaRecorder MIME type:', state.mediaRecorder.mimeType);
        
        state.mediaRecorder.ondataavailable = (event) => {
            console.log('Audio data chunk received:', event.data.size, 'bytes');
            state.audioChunks.push(event.data);
        };
        
        state.mediaRecorder.onstop = async () => {
            // Create blob with recorded audio
            const recordedBlob = new Blob(state.audioChunks, { type: state.mediaRecorder.mimeType });
            console.log('Recording stopped. Audio blob created:', recordedBlob.size, 'bytes', 'type:', recordedBlob.type);
            
            // If it's webm, we need to convert to WAV using Web Audio API
            if (recordedBlob.type.includes('webm')) {
                console.log('Converting webm to WAV...');
                try {
                    state.audioBlob = await convertToWav(recordedBlob);
                    console.log('Converted to WAV:', state.audioBlob.size, 'bytes');
                } catch (error) {
                    console.error('WAV conversion failed:', error);
                    state.audioBlob = recordedBlob; // Use original if conversion fails
                }
            } else {
                state.audioBlob = recordedBlob;
            }
            
            const audioUrl = URL.createObjectURL(state.audioBlob);
            elements.audioElement.src = audioUrl;
            elements.audioPlayback.classList.remove('hidden');
        };
        
        state.mediaRecorder.start();
        state.isRecording = true;
        
        console.log('Recording started...');
        
        elements.recordBtnIcon.textContent = '⏹️';
        elements.recordBtnText.textContent = 'Stop Recording';
        elements.recordBtn.classList.add('recording');
        
        animateVisualizer();
        
    } catch (error) {
        console.error('Recording failed:', error);
        alert('Could not access microphone. Please check permissions.');
    }
}

function stopRecording() {
    if (state.mediaRecorder && state.isRecording) {
        state.mediaRecorder.stop();
        state.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        state.isRecording = false;
        
        elements.recordBtnIcon.textContent = '🎤';
        elements.recordBtnText.textContent = 'Start Recording';
        elements.recordBtn.classList.remove('recording');
    }
}

// Convert audio blob to WAV format using Web Audio API
async function convertToWav(audioBlob) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const arrayBuffer = await audioBlob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    
    // Convert to WAV format
    const wavBuffer = audioBufferToWav(audioBuffer);
    return new Blob([wavBuffer], { type: 'audio/wav' });
}

// Convert AudioBuffer to WAV format
function audioBufferToWav(buffer) {
    const length = buffer.length * buffer.numberOfChannels * 2 + 44;
    const arrayBuffer = new ArrayBuffer(length);
    const view = new DataView(arrayBuffer);
    const channels = [];
    let offset = 0;
    let pos = 0;
    
    // Write WAV header
    const setUint16 = (data) => {
        view.setUint16(pos, data, true);
        pos += 2;
    };
    const setUint32 = (data) => {
        view.setUint32(pos, data, true);
        pos += 4;
    };
    
    // RIFF identifier
    setUint32(0x46464952);
    // File length
    setUint32(length - 8);
    // WAVE identifier
    setUint32(0x45564157);
    // Format chunk identifier
    setUint32(0x20746d66);
    // Format chunk length
    setUint32(16);
    // Sample format (raw)
    setUint16(1);
    // Channel count
    setUint16(buffer.numberOfChannels);
    // Sample rate
    setUint32(buffer.sampleRate);
    // Byte rate (sample rate * block align)
    setUint32(buffer.sampleRate * buffer.numberOfChannels * 2);
    // Block align (channel count * bytes per sample)
    setUint16(buffer.numberOfChannels * 2);
    // Bits per sample
    setUint16(16);
    // Data chunk identifier
    setUint32(0x61746164);
    // Data chunk length
    setUint32(length - pos - 4);
    
    // Write interleaved audio data
    for (let i = 0; i < buffer.numberOfChannels; i++) {
        channels.push(buffer.getChannelData(i));
    }
    
    while (pos < length) {
        for (let i = 0; i < buffer.numberOfChannels; i++) {
            let sample = Math.max(-1, Math.min(1, channels[i][offset]));
            sample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
            view.setInt16(pos, sample, true);
            pos += 2;
        }
        offset++;
    }
    
    return arrayBuffer;
}

// Visualizer
function setupVisualizer() {
    const canvas = elements.visualizerCanvas;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Draw placeholder
    ctx.fillStyle = '#e5e7eb';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#6b7280';
    ctx.font = '16px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Audio visualizer', canvas.width / 2, canvas.height / 2);
}

function animateVisualizer() {
    if (!state.isRecording) return;
    
    const canvas = elements.visualizerCanvas;
    const ctx = canvas.getContext('2d');
    
    // Simple animation
    const draw = () => {
        if (!state.isRecording) return;
        
        ctx.fillStyle = '#f3f4f6';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw bars
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

// Analysis Functions
async function analyzeVoice() {
    if (!state.audioBlob) {
        alert('Please record audio first');
        return;
    }
    
    console.log('Starting voice analysis...');
    console.log('Audio blob size:', state.audioBlob.size, 'bytes');
    console.log('Audio blob type:', state.audioBlob.type);
    
    showLoading('Analyzing your voice...');
    
    try {
        const formData = new FormData();
        // Always use .wav extension since we convert to WAV format
        formData.append('audio', state.audioBlob, 'recording.wav');
        
        console.log('Sending voice analysis request to:', `${API_BASE_URL}/analyze/voice`);
        console.log('Audio file name: recording.wav');
        console.log('Audio MIME type:', state.audioBlob.type);
        
        const response = await fetch(`${API_BASE_URL}/analyze/voice`, {
            method: 'POST',
            body: formData
        });
        
        console.log('Voice analysis response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Voice analysis error response:', errorText);
            throw new Error(`Analysis failed: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Voice analysis result:', data);
        state.currentAnalysis = data;
        
        // Generate poster
        await generatePoster(data);
        
        // Display results
        displayResults(data, true);
        
    } catch (error) {
        console.error('Voice analysis failed:', error);
        alert('Failed to analyze voice. Please try again.\n' + error.message);
        hideLoading();
    }
}

async function analyzeText() {
    const text = elements.journalText.value.trim();
    
    if (!text) {
        alert('Please enter some text');
        return;
    }
    
    showLoading('Analyzing your text...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze/text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        state.currentAnalysis = data;
        
        // Generate poster
        await generatePoster(data);
        
        // Display results
        displayResults(data, false);
        
    } catch (error) {
        console.error('Text analysis failed:', error);
        alert('Failed to analyze text. Please try again.');
        hideLoading();
    }
}

// Poster Generation
async function generatePoster(analysisData) {
    elements.loadingText.textContent = 'Creating your artistic poster...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate/poster`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(analysisData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Poster generation failed');
        }
        
        const data = await response.json();
        state.posterPath = data.poster_path;
        
        // Load poster image - construct full URL correctly
        const posterUrl = `http://localhost:5000${data.poster_url}`;
        elements.posterImage.src = posterUrl;
        console.log('Poster URL:', posterUrl);
        
    } catch (error) {
        console.error('Poster generation failed:', error);
        alert('Failed to generate poster: ' + error.message);
    }
}

// Display Results
function displayResults(data, isVoice) {
    // Show transcribed text for voice input
    if (isVoice && data.text) {
        elements.transcribedText.textContent = data.text;
        elements.transcribedTextContainer.classList.remove('hidden');
    } else {
        elements.transcribedTextContainer.classList.add('hidden');
    }
    
    // Display primary emotion
    const emotionColor = getEmotionColor(data.primary_emotion);
    elements.primaryEmotion.textContent = data.primary_emotion;
    elements.primaryEmotion.style.background = `linear-gradient(135deg, ${emotionColor}30, ${emotionColor}60)`;
    elements.primaryEmotion.style.color = emotionColor;
    
    // Display all emotions
    elements.emotionsList.innerHTML = '';
    for (const [emotion, score] of Object.entries(data.emotions)) {
        const emotionItem = document.createElement('div');
        emotionItem.className = 'emotion-item';
        emotionItem.innerHTML = `
            <div class="emotion-name">${emotion}</div>
            <div class="emotion-score">${score}%</div>
            <div class="emotion-bar">
                <div class="emotion-bar-fill" style="width: ${score}%"></div>
            </div>
        `;
        elements.emotionsList.appendChild(emotionItem);
    }
    
    // Display philosophical note
    elements.philosophicalNote.textContent = data.philosophical_note;
    
    // Show results section
    hideLoading();
    elements.inputSection.classList.add('hidden');
    elements.resultsSection.classList.remove('hidden');
}

// Export Card
async function exportCard(platform) {
    if (!state.posterPath) {
        alert('No poster to export');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/export/card`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                poster_path: state.posterPath,
                platform: platform
            })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        // Download the file
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
        console.error('Export failed:', error);
        alert('Failed to export card. Please try again.');
    }
}

// Utility Functions
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
    // Reset state
    state.audioBlob = null;
    state.currentAnalysis = null;
    state.posterPath = null;
    
    // Reset UI
    elements.journalText.value = '';
    elements.audioPlayback.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
    elements.inputSection.classList.remove('hidden');
    
    // Re-check server
    checkServerHealth();
}

function getEmotionColor(emotion) {
    const colors = {
        joy: '#fbbf24',
        happiness: '#fbbf24',
        sadness: '#3b82f6',
        anger: '#ef4444',
        fear: '#8b5cf6',
        surprise: '#f97316',
        disgust: '#10b981',
        love: '#ec4899',
        anxiety: '#a855f7',
        peace: '#06b6d4',
        neutral: '#6b7280',
        trust: '#60a5fa',
        anticipation: '#84cc16'
    };
    
    return colors[emotion.toLowerCase()] || '#6366f1';
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
