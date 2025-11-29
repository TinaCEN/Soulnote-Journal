# Soulnote — AI Emotional Journal

Soulnote is an AI‑powered emotional journaling tool. It analyzes emotions from voice or text, generates artistic visual posters, and writes short philosophical reflections related to what you feel.

Team：3YT
Numbers:
Cen Sitian-25052928g:
(Planning) proposes requirements and the framework. & (Delivery) integrates all outputs and completes project closure.
Peng Quanyi-25069109g
(Implementation) codes according to the design and requirements.
MA Huanyu Noel-25058293g
(Design) designs the interface based on requirements.
LI Yi-25049079g
 (Validation) tests the finished product and creates demo materials.
 
## Modes

- Experience mode (recommended): Uses a built‑in shared DeepSeek API key so you can try real AI analysis immediately.
- Demo mode: Auto‑enabled when no API key is available. Features and UI work with smart sample data.
- Personal mode: Use your own DeepSeek API key for full, private usage and cost control.

## Features

- Voice recording and speech‑to‑text
- Text journaling
- Emotion analysis with AI
- Artistic poster generation
- Short philosophical notes
- Social card export (Instagram, X/Twitter)

## Tech Stack

- Backend: Python (Flask)
- AI: DeepSeek API (pluggable)
- Audio: SpeechRecognition, Librosa, PyDub, FFmpeg
- Imaging: Pillow, Matplotlib
- Frontend: HTML, CSS, JavaScript

## Requirements

- Python 3.8+
- FFmpeg
- Git (optional, to clone)

## Quickstart (Windows/macOS/Linux)

```powershell
# 1) Clone
git clone <repository-url>
cd Soulnote-JournalV4

# 2) Create venv and install deps
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt

# 3) Ensure FFmpeg is installed (Windows)
winget install --id=Gyan.FFmpeg -e

# 4) Run the combined app
python soulnote_complete.py
# Or on Windows: .\start_app.bat

# 5) Open in browser
http://localhost:5007
```

By default, Soulnote runs in Experience mode (shared API key) if you haven’t set your own.

## Personal API Key (optional)

Set `DEEPSEEK_API_KEY` in your environment (or a `.env` file next to `soulnote_complete.py`) and restart:

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."; python soulnote_complete.py
```

## Project Structure

```
Soulnote-JournalV4/
├── soulnote_complete.py        # One-file app (UI + API)
├── models/                     # AI provider clients
├── utils/                      # Audio + poster tools
├── frontend/                   # Optional static UI (not required by the one-file app)
├── static/                     # Shared assets
├── uploads/                    # Temp audio uploads
├── output/                     # Generated posters
└── requirements.txt
```

## API (served by `soulnote_complete.py`)

- `POST /api/analyze/text` — Analyze emotions from text
- `POST /api/analyze/voice` — Analyze emotions from recorded voice
- `POST /api/generate/poster` — Generate poster
- `GET /api/output/<filename>` — Serve generated files

## Troubleshooting

- Use the virtual environment’s Python: `./venv/Scripts/python.exe soulnote_complete.py`
- Install FFmpeg and restart terminal if microphone fails.
- Browser must allow microphone access for voice mode.

## License

MIT — see `LICENSE` if present.

Made with care for emotional well‑being.
