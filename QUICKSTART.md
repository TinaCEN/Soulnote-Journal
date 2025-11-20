# Quick Start Guide

## Prerequisites

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install LM Studio**
   - Download from [lmstudio.ai](https://lmstudio.ai)
   - See `LM_STUDIO_SETUP.md` for detailed instructions

## Installation Steps

### Windows

1. **Run the start script**
   ```cmd
   start.bat
   ```

   This will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Start the backend server

2. **Open the frontend**
   - Navigate to `frontend/index.html` in your web browser
   - Or use a simple server:
     ```cmd
     cd frontend
     python -m http.server 8000
     ```
   - Then open `http://localhost:8000`

### macOS/Linux

1. **Make the script executable**
   ```bash
   chmod +x start.sh
   ```

2. **Run the start script**
   ```bash
   ./start.sh
   ```

3. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or use a simple server:
     ```bash
     cd frontend
     python3 -m http.server 8000
     ```
   - Then open `http://localhost:8000`

## Manual Installation

If the automated script doesn't work:

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend**
   ```bash
   python backend/app.py
   ```

5. **Open frontend**
   - Open `frontend/index.html` in your browser

## LM Studio Setup

**CRITICAL**: Make sure LM Studio is running BEFORE starting Soulnote!

1. Open LM Studio
2. Download a model (recommended: Llama 2 7B Chat)
3. Load the model
4. Go to "Local Server" tab
5. Click "Start Server"
6. Verify it's running on `http://localhost:1234`

See `LM_STUDIO_SETUP.md` for detailed instructions.

## Using Soulnote

### Voice Journaling

1. Click "Voice Recording" tab
2. Click "Start Recording"
3. Speak your thoughts
4. Click "Stop Recording"
5. Click "Analyze Emotions"
6. View results and download poster

### Text Journaling

1. Click "Text Input" tab
2. Write your journal entry
3. Click "Analyze Emotions"
4. View results and download poster

## Troubleshooting

### "Cannot connect to server"
- Make sure you ran `python backend/app.py`
- Check if port 5000 is available
- Look for errors in the terminal

### "LM Studio not connected"
- Verify LM Studio local server is running
- Check it's on port 1234
- Load a model first, then start the server

### "Could not access microphone"
- Grant microphone permissions in your browser
- Try Chrome or Edge (best support)
- Check your system microphone settings

### Import errors
```bash
pip install -r requirements.txt
```

### "No module named 'flask'"
- Make sure virtual environment is activated
- Look for `(venv)` at the start of your terminal prompt

## Next Steps

1. Record or write your first journal entry
2. Explore different emotions
3. Download and share your posters
4. Experiment with different journal styles

## Support

- Check `README.md` for detailed documentation
- See `LM_STUDIO_SETUP.md` for LM Studio help
- Review code comments for technical details

---

Enjoy your emotional journaling journey! ❤️
