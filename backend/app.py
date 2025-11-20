"""
Soulnote Backend - Main Flask Application
Handles API endpoints for emotion analysis, poster generation, and card export
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.emotion_analyzer import EmotionAnalyzer
from models.online_ai_client import OnlineAIClient
from utils.audio_processor import AudioProcessor
from utils.poster_generator import PosterGenerator
from utils.card_exporter import CardExporter

# Configuration - use absolute paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent

# Initialize Flask with custom static folder
app = Flask(__name__, 
            static_folder=str(PROJECT_ROOT / 'static'),
            static_url_path='/static')
CORS(app)  # Enable CORS for frontend communication
UPLOAD_FOLDER = PROJECT_ROOT / 'uploads'
OUTPUT_FOLDER = PROJECT_ROOT / 'output'
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize components
ai_client = OnlineAIClient()  # Auto-detect available AI provider
emotion_analyzer = EmotionAnalyzer(ai_client)
audio_processor = AudioProcessor()
poster_generator = PosterGenerator()
card_exporter = CardExporter()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_provider': ai_client.get_provider_info(),
        'ai_connected': ai_client.is_connected()
    })


@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Analyze emotions from text input"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Analyze emotions
        emotion_result = emotion_analyzer.analyze_text(text)
        
        # Generate philosophical note
        philosophical_note = emotion_analyzer.generate_philosophical_note(
            emotion_result['primary_emotion'],
            emotion_result['emotions']
        )
        
        return jsonify({
            'text': text,
            'emotions': emotion_result['emotions'],
            'primary_emotion': emotion_result['primary_emotion'],
            'philosophical_note': philosophical_note,
            'timestamp': emotion_result['timestamp']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/voice', methods=['POST'])
def analyze_voice():
    """Analyze emotions from voice recording"""
    print("=" * 60)
    print("📝 Voice analysis request received")
    print(f"Request files: {list(request.files.keys())}")
    print(f"Request form: {list(request.form.keys())}")
    print("=" * 60)
    
    try:
        if 'audio' not in request.files:
            print("❌ No audio file in request")
            print(f"Available keys: {list(request.files.keys())}")
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        print(f"📁 Audio file received: {audio_file.filename}")
        
        # Save uploaded audio
        audio_path = UPLOAD_FOLDER / audio_file.filename
        audio_file.save(audio_path)
        print(f"💾 Audio saved to: {audio_path}")
        
        # Convert speech to text
        print("🎤 Starting speech-to-text conversion...")
        text = audio_processor.speech_to_text(audio_path)
        print(f"📝 Transcribed text: '{text}'")
        
        if not text:
            print("❌ Speech-to-text returned empty")
            return jsonify({'error': 'Could not transcribe audio'}), 400
        
        # Analyze emotions
        emotion_result = emotion_analyzer.analyze_text(text)
        
        # Generate waveform data
        waveform_data = audio_processor.generate_waveform_data(audio_path)
        
        # Generate philosophical note
        philosophical_note = emotion_analyzer.generate_philosophical_note(
            emotion_result['primary_emotion'],
            emotion_result['emotions']
        )
        
        return jsonify({
            'text': text,
            'emotions': emotion_result['emotions'],
            'primary_emotion': emotion_result['primary_emotion'],
            'philosophical_note': philosophical_note,
            'waveform_data': waveform_data,
            'audio_filename': audio_file.filename,
            'timestamp': emotion_result['timestamp']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/poster', methods=['POST'])
def generate_poster():
    """Generate artistic visual poster"""
    print("=" * 60)
    print("🎨 Poster generation request received")
    try:
        data = request.json
        print(f"Data keys: {list(data.keys())}")
        print(f"Primary emotion: {data.get('primary_emotion')}")
        print(f"Emotions: {data.get('emotions')}")
        
        poster_path = poster_generator.create_poster(
            text=data.get('text', ''),
            primary_emotion=data.get('primary_emotion'),
            emotions=data.get('emotions', {}),
            philosophical_note=data.get('philosophical_note', ''),
            waveform_data=data.get('waveform_data'),
            audio_filename=data.get('audio_filename')
        )
        
        print(f"✅ Poster created: {poster_path}")
        print("=" * 60)
        
        return jsonify({
            'poster_path': str(poster_path),
            'poster_url': f'/api/output/{poster_path.name}'
        })
    
    except Exception as e:
        print(f"❌ Poster generation error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/card', methods=['POST'])
def export_card():
    """Export as social media card"""
    try:
        data = request.json
        platform = data.get('platform', 'instagram')  # instagram, twitter, square
        poster_path = data.get('poster_path')
        
        if not poster_path:
            return jsonify({'error': 'No poster path provided'}), 400
        
        card_path = card_exporter.export_for_platform(
            poster_path=OUTPUT_FOLDER / Path(poster_path).name,
            platform=platform
        )
        
        return send_file(
            card_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'soulnote_{platform}_{card_path.stem}.png'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/output/<filename>', methods=['GET'])
def get_output_file(filename):
    """Serve generated output files"""
    try:
        file_path = OUTPUT_FOLDER / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Serve Frontend
# Serve Frontend
@app.route('/')
def index():
    """Serve the main frontend page"""
    try:
        frontend_path = PROJECT_ROOT / 'frontend' / 'index.html'
        return send_file(frontend_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Soulnote Backend Server...")
    print(f"AI Provider: {ai_client.get_provider_info()}")
    print("\n" + "=" * 60)
    print("🌟 Open your browser and go to: http://localhost:5002")
    print("=" * 60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5002)
