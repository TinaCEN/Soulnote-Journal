# Known Issues & Solutions

## Python Version Compatibility

### Issue: Librosa Installation Fails

**Problem**: Librosa and its dependency Numba don't yet support Python 3.14

**Error Message**:
```
RuntimeError: Cannot install on Python version 3.14.0; only versions >=3.10,<3.14 are supported.
```

**Solutions**:

### Solution 1: Use Python 3.11 or 3.12 (Recommended)

1. Download Python 3.12 from [python.org](https://www.python.org/downloads/)
2. Create a new virtual environment with Python 3.12:
   ```bash
   # Specify Python version
   py -3.12 -m venv venv_312
   
   # Or on macOS/Linux
   python3.12 -m venv venv_312
   ```
3. Activate and install:
   ```bash
   # Windows
   venv_312\Scripts\activate
   
   # macOS/Linux
   source venv_312/bin/activate
   
   pip install -r requirements.txt
   ```

### Solution 2: Skip Audio Features (Quick Workaround)

If you only want to use text input (not voice), you can skip librosa:

1. Edit `requirements.txt` and comment out:
   ```
   # librosa>=0.10.0
   ```

2. Modify `utils/audio_processor.py` to handle missing librosa:
   ```python
   try:
       import librosa
       LIBROSA_AVAILABLE = True
   except ImportError:
       LIBROSA_AVAILABLE = False
       print("Warning: librosa not available. Voice features disabled.")
   ```

3. Update the backend to skip voice analysis when librosa isn't available

### Solution 3: Use Pre-built Environment

Create a conda environment with compatible versions:

```bash
# Install Miniconda/Anaconda first
conda create -n soulnote python=3.12
conda activate soulnote
pip install -r requirements.txt
```

## Other Common Issues

### FFmpeg Warning

**Warning**: `Couldn't find ffmpeg or avconv`

**Impact**: Low - only affects certain audio format conversions

**Solution** (optional):
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Add to system PATH
3. Or install via package manager:
   ```bash
   # Windows (with Chocolatey)
   choco install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Linux
   sudo apt install ffmpeg
   ```

### LM Studio Connection

**Error**: `Cannot connect to LM Studio`

**Solutions**:
1. Verify LM Studio is running
2. Check the local server is started (port 1234)
3. Load a model first, then start server
4. Check firewall settings

### Microphone Access

**Error**: `Could not access microphone`

**Solutions**:
1. Grant browser microphone permissions
2. Use Chrome or Edge (best compatibility)
3. Check system microphone settings
4. Try a different browser

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solutions**:
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall all dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Workarounds for Current Setup

Since you're using Python 3.14, here are immediate options:

### Option A: Text-Only Mode (No Voice Features)

The app will work perfectly for text input without librosa:

1. Comment out librosa in requirements.txt
2. Use text input tab only
3. All other features (emotion analysis, poster generation, export) work fine

### Option B: Downgrade Python

Use Python 3.11 or 3.12 for full compatibility:

```bash
# Check available Python versions
py --list

# Create venv with specific version
py -3.12 -m venv venv
```

### Option C: Wait for Updates

Librosa/Numba will eventually support Python 3.14. Check:
- [Librosa releases](https://github.com/librosa/librosa/releases)
- [Numba releases](https://github.com/numba/numba/releases)

## Testing Your Installation

Run the test script to see what's working:

```bash
python test_installation.py
```

This will show you:
- ✅ What's installed and working
- ❌ What needs attention
- ⚠️  Optional components (like LM Studio)

## Recommended Versions

For best compatibility:

```
Python: 3.11.x or 3.12.x
Flask: 3.0.0
Librosa: 0.10.1
NumPy: 1.24.x - 1.26.x
Pillow: 10.x
```

## Getting Help

If you encounter other issues:

1. Check this file first
2. Review error messages carefully
3. Check the README.md for detailed setup
4. Ensure all prerequisites are installed
5. Try the test installation script

## Current Status

As of your installation:

✅ **Working**:
- Flask server
- Text input and analysis
- LM Studio connection
- Poster generation (basic)
- Export functionality
- Frontend UI

⚠️ **Limited** (due to Python 3.14):
- Voice recording (works)
- Speech-to-text (works with SpeechRecognition)
- Waveform visualization (needs librosa)
- Audio feature extraction (needs librosa)

**Recommendation**: For full features, use Python 3.12 or 3.11

---

*Last updated: Based on Python 3.14.0 compatibility check*
