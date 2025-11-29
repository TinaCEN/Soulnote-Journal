# Soulnote — AI Emotional Journal

Soulnote is an AI‑powered emotional journaling tool. It analyzes emotions from voice or text, generates artistic visual posters, and writes short philosophical reflections related to what you feel.

## Team：3YT
Numbers:
- Cen Sitian-25052928g:
(Planning) proposes requirements and the framework. & (Delivery) integrates all outputs and completes project closure.
- Peng Quanyi-25069109g
(Implementation) codes according to the design and requirements.
- MA Huanyu Noel-25058293g
(Design) designs the interface based on requirements.
- LI Yi-25049079g
 (Validation) tests the finished product and creates demo materials.

## About us


![About us](https://github.com/user-attachments/assets/0e2121fc-ee42-470e-ab32-9b698cea6834)

 
## Modes

- Experience mode (recommended): Uses a built‑in shared DeepSeek API key so you can try real AI analysis immediately.
- Demo mode: Auto‑enabled when no API key is available. Features and UI work with smart sample data.
- Personal mode: Use your own DeepSeek API key for full, private usage and cost control.

## Features

- Voice recording and speech‑to‑text


![The voice way](https://github.com/user-attachments/assets/f283e0ae-4d90-4982-bc74-c6c748646ae0)
- Adjust the words to a better outcome

 
 ![Adjust the words to a better outcome](https://github.com/user-attachments/assets/5c34a69c-9d6b-4537-b501-3009b41708ed)
 - Use text to input content


  ![The text way](https://github.com/user-attachments/assets/225b4223-a8a5-462f-b22b-620029aa8729)

- Personal emotional history 

 
 ![Personal emotional history ](https://github.com/user-attachments/assets/b76c6137-a719-494a-abb1-cc3b8ba99a58)
- Social art cart export (Instagram, X/Twitter)

 
 ![Social art cart export](https://github.com/user-attachments/assets/1f78e941-b6ce-4c7d-aed1-fd7fcb340512)


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
