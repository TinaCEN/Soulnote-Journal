# API Key Setup Guide for Soulnote

## For Students/Teachers - Getting DeepSeek API Key

### Option 1: Free Trial (Recommended for Testing)
1. Visit https://platform.deepseek.com/
2. Sign up with email or GitHub account
3. After registration, you get $5 free credit
4. Go to https://platform.deepseek.com/api_keys
5. Click "Create API Key"
6. Copy the key (starts with `sk-`)

### Option 2: For Teachers/Demo Mode
If you don't want to get an API key, the application will run in **Demo Mode**:
- All basic features work (voice recording, UI)
- Shows example emotions and philosophical notes
- Generates sample posters with placeholder data
- Perfect for reviewing the project structure and design

## Setup Instructions

### Step 1: Configure Your Environment
```bash
# Copy the example file
cp .env.example .env

# Edit .env file and add your API key:
DEEPSEEK_API_KEY=sk-your-actual-key-here
```

### Step 2: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# Or: venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt

# Install FFmpeg (required for audio processing)
# On macOS:
brew install ffmpeg
# On Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg
# On Windows: Download from https://ffmpeg.org/download.html
```

### Step 3: Run the Application
```bash
# Make sure you're in the project directory
cd Soulnote.v1

# Run the application
python soulnote_complete.py
```

### Step 4: Access the Application
Open your browser and go to: http://localhost:5007

## Cost Information (for Reference)

DeepSeek Pricing (Very Affordable):
- Input: ~$0.14 per 1M tokens
- Output: ~$0.28 per 1M tokens
- For typical use: ~$0.01-0.05 per journal entry

Example costs:
- 100 journal entries: ~$1-5
- 1000 journal entries: ~$10-50

## Sharing API Keys

### For Teammates:
- You can share your API key temporarily
- Create a shared `.env` file with the key
- **Important**: Don't commit `.env` to GitHub

### For Teachers:
- Run in Demo Mode (no API key needed)
- Or provide a small credit API key for testing
- All features work except real AI analysis

## Demo Mode Features

When no API key is provided:
- ✅ Voice recording and playback
- ✅ Speech-to-text conversion
- ✅ UI and interactions
- ✅ Poster generation with sample data
- ✅ Example emotions: joy, sadness, calm, confusion
- ✅ Sample philosophical quotes
- ✅ Export to social media formats

Real AI features (with API key):
- 🤖 Actual emotion analysis of your text
- 🤖 Personalized philosophical insights
- 🤖 Context-aware responses

## Troubleshooting

### Common Issues:
1. **FFmpeg not found**: Install FFmpeg system-wide
2. **Module not found**: Activate virtual environment first
3. **API key invalid**: Check key format and account balance
4. **Port already in use**: Change port in soulnote_complete.py

### Support:
- Check TROUBLESHOOTING.md for detailed solutions
- All features work in Demo Mode without API keys
