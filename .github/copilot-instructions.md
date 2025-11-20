# Soulnote - Emotional Journaling Tool

## Project Overview
An AI-powered emotional journaling tool that analyzes emotions from voice or text input, generates artistic visual posters with sonic graphics, and creates philosophical notes related to the detected emotions.

## Tech Stack
- **Backend**: Python with Flask
- **AI Model**: LM Studio (local LLM for emotion analysis)
- **Audio Processing**: SpeechRecognition, PyDub, Librosa
- **Image Generation**: Pillow, Matplotlib, Cairo
- **Frontend**: HTML, CSS, JavaScript
- **Audio Visualization**: WaveSurfer.js

## Project Structure
- `/backend` - Flask API server
- `/frontend` - Web interface
- `/static` - CSS, JS, images
- `/models` - AI model integrations
- `/utils` - Helper functions for audio, image processing
- `/output` - Generated posters and cards

## Key Features
1. Voice recording and speech-to-text conversion
2. Text input for journaling
3. Emotion analysis using LM Studio
4. Artistic poster generation with waveform visualization
5. Philosophical quote generation
6. Social media card export (Instagram, X/Twitter formats)
