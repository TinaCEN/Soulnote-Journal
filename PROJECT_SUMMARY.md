# Soulnote Project - Setup Complete! 🎉

## What You Just Created

**Soulnote** is a complete AI-powered emotional journaling tool that:
- ✅ Accepts voice or text input
- ✅ Analyzes emotions using local AI (LM Studio)
- ✅ Generates beautiful artistic posters with waveform visualizations
- ✅ Creates philosophical reflections based on detected emotions
- ✅ Exports shareable cards for social media (Instagram, Twitter/X, etc.)

## Project Structure

```
Soulnote/
├── 📁 backend/              # Flask API server
│   ├── app.py              # Main server application
│   └── __init__.py
│
├── 📁 models/               # AI & emotion analysis
│   ├── lmstudio_client.py  # LM Studio API integration
│   ├── emotion_analyzer.py # Emotion detection logic
│   └── __init__.py
│
├── 📁 utils/                # Processing utilities
│   ├── audio_processor.py  # Voice-to-text & waveform
│   ├── poster_generator.py # Artistic poster creation
│   ├── card_exporter.py    # Social media export
│   └── __init__.py
│
├── 📁 frontend/             # Web interface
│   └── index.html          # Main UI
│
├── 📁 static/               # Frontend assets
│   ├── css/
│   │   └── style.css       # Styles
│   └── js/
│       └── app.js          # Frontend logic
│
├── 📁 uploads/              # Temporary audio storage
├── 📁 output/               # Generated posters
│
├── 📄 requirements.txt      # Python dependencies
├── 📄 README.md            # Full documentation
├── 📄 QUICKSTART.md        # Quick start guide
├── 📄 LM_STUDIO_SETUP.md   # LM Studio setup guide
├── 📄 test_installation.py # Installation test script
├── 🚀 start.bat            # Windows launcher
└── 🚀 start.sh             # macOS/Linux launcher
```

## Key Features Implemented

### 1. **Dual Input Methods**
- Voice recording with real-time visualization
- Text input with rich textarea editor
- Seamless tab switching

### 2. **AI Emotion Analysis**
- Integration with LM Studio local LLM
- Detects multiple emotions with confidence scores
- Identifies primary emotion and sentiment
- Analyzes intensity levels

### 3. **Artistic Poster Generation**
- Emotion-based color schemes
- Waveform visualization for voice input
- Gradient backgrounds
- Decorative artistic elements
- Customizable dimensions

### 4. **Philosophical Note Generation**
- AI-generated reflections
- Context-aware based on emotions
- Poetic and meaningful insights

### 5. **Social Media Export**
- Instagram (1080x1080, 1080x1350)
- Twitter/X (1200x675)
- Stories (1080x1920)
- Generic square format
- High-quality PNG export

## Technologies Used

### Backend
- **Flask** - Web framework
- **Python 3.8+** - Core language
- **LM Studio** - Local LLM inference
- **SpeechRecognition** - Voice-to-text
- **Librosa** - Audio analysis
- **Pillow** - Image generation
- **NumPy** - Data processing

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern styling with gradients
- **Vanilla JavaScript** - No frameworks needed
- **Canvas API** - Visualizations
- **MediaRecorder API** - Voice recording

## Getting Started

### Option 1: Quick Start (Recommended)

#### Windows:
```cmd
start.bat
```

#### macOS/Linux:
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

1. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Start backend**
   ```bash
   python backend/app.py
   ```

3. **Open frontend**
   - Open `frontend/index.html` in your browser

### Option 3: Test Installation First

```bash
python test_installation.py
```

This will verify:
- ✓ All packages installed correctly
- ✓ Directory structure is complete
- ✓ LM Studio connection (if running)

## Before First Use

### ⚠️ CRITICAL: Setup LM Studio

Soulnote requires LM Studio to be running for emotion analysis:

1. **Install LM Studio**
   - Download from [lmstudio.ai](https://lmstudio.ai)

2. **Download a Model**
   - Recommended: Llama 2 7B Chat
   - Or: Mistral 7B Instruct

3. **Start Local Server**
   - Load your model
   - Go to "Local Server" tab
   - Click "Start Server"
   - Verify: http://localhost:1234

📖 See `LM_STUDIO_SETUP.md` for detailed instructions

## API Endpoints

The backend server provides these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Server health check |
| `/api/analyze/text` | POST | Analyze text emotions |
| `/api/analyze/voice` | POST | Analyze voice emotions |
| `/api/generate/poster` | POST | Create artistic poster |
| `/api/export/card` | POST | Export social media card |
| `/api/output/<file>` | GET | Serve generated files |

## Configuration

### Change Backend Port
Edit `backend/app.py` line 111:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change here
```

### Change LM Studio URL
Edit `models/lmstudio_client.py` line 11:
```python
def __init__(self, base_url: str = "http://localhost:1234/v1"):
```

### Customize Emotions
Edit `utils/poster_generator.py` lines 19-33 to add/modify emotions:
```python
EMOTION_COLORS = {
    'your_emotion': (hue, saturation, value),  # HSV format
}
```

### Adjust Poster Size
Edit `utils/poster_generator.py` lines 47-48:
```python
self.width = 1080   # Change width
self.height = 1350  # Change height
```

## Common Use Cases

### 1. Daily Journal
- Record your daily thoughts via voice
- Analyze emotional patterns over time
- Create beautiful visual memories

### 2. Emotional Check-in
- Quick text input for current feelings
- Get AI-generated philosophical insights
- Understand your emotional state

### 3. Content Creation
- Generate unique emotional artwork
- Create shareable social media content
- Express feelings visually

### 4. Mindfulness Practice
- Reflect through journaling
- Gain perspective through AI reflections
- Track emotional wellness

## Troubleshooting

### "Cannot connect to server"
```bash
# Make sure backend is running
python backend/app.py
```

### "LM Studio not connected"
```bash
# Check LM Studio local server is running
# Visit: http://localhost:1234/v1/models
```

### "Microphone not accessible"
- Grant microphone permissions in browser settings
- Use Chrome or Edge for best compatibility
- Check system microphone settings

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Test everything
```bash
python test_installation.py
```

## Next Steps

1. ✅ **Test the installation**
   ```bash
   python test_installation.py
   ```

2. ✅ **Setup LM Studio**
   - Follow `LM_STUDIO_SETUP.md`
   - Download a model
   - Start the server

3. ✅ **Start the application**
   ```bash
   # Windows
   start.bat
   
   # macOS/Linux
   ./start.sh
   ```

4. ✅ **Create your first journal entry**
   - Open frontend/index.html
   - Try voice or text input
   - Analyze emotions
   - Download your poster!

## Documentation Files

- 📖 **README.md** - Complete project documentation
- 🚀 **QUICKSTART.md** - Quick start guide
- 🤖 **LM_STUDIO_SETUP.md** - LM Studio installation & setup
- 🔧 **test_installation.py** - Verify installation

## Development

### Run in Development Mode
```bash
# Backend (auto-reload enabled)
python backend/app.py

# Frontend with live server
cd frontend
python -m http.server 8000
```

### Customize the UI
- Edit `static/css/style.css` for styling
- Edit `static/js/app.js` for behavior
- Edit `frontend/index.html` for structure

### Extend Functionality
- Add new emotions in `poster_generator.py`
- Modify prompts in `lmstudio_client.py`
- Add export formats in `card_exporter.py`

## Project Highlights

✨ **What Makes This Special:**
- 100% local AI processing (privacy-first)
- No external API costs
- Beautiful, artistic visualizations
- Combines multiple technologies seamlessly
- Production-ready code structure
- Comprehensive error handling
- Full documentation

## Support & Resources

- Check the README for detailed docs
- Review LM_STUDIO_SETUP for AI setup
- Run test_installation.py to diagnose issues
- Explore the code - it's well-commented!

---

## 🎉 You're All Set!

Your emotional journaling tool is ready to use. Start by:

1. Setting up LM Studio (see LM_STUDIO_SETUP.md)
2. Running `python test_installation.py`
3. Launching the app with `start.bat` or `./start.sh`
4. Creating your first emotional journal entry!

**Enjoy exploring your emotions through AI and art!** ❤️

---

*Created with AI assistance • Built for emotional well-being • Made with Python & LM Studio*
