# Soulnote Journal

An AI-powered emotional journaling app that transforms your feelings into visual and sonic diary entries.

## Features

🎤 **Voice Recording** - Speak your emotions naturally
🧠 **AI Emotion Analysis** - Categorizes emotions (happy/sad/calm/angry)
🎨 **Visual Art Generation** - Creates dynamic emotional graphics
🎵 **Music Generation** - Generates emotional soundscapes
💭 **AI Reflection** - Philosophical responses to your emotions
📖 **Daily Diary** - Tracks your emotional journey
📱 **Social Sharing** - Share to Instagram, WeChat, or save locally

## "It's not just a journal — it's a mirror that feels."

## Development Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Install Expo CLI:
   ```bash
   npm install -g expo-cli
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Use Expo Go app on your iOS device to scan the QR code and test the app

## Project Structure

```
SoulnoteJournal/
├── App.js              # Main application component
├── app.json            # Expo configuration
├── package.json        # Dependencies and scripts
├── babel.config.js     # Babel configuration
├── assets/             # Images, icons, sounds
├── components/         # Reusable UI components
├── services/           # API integrations (OpenAI, emotion analysis)
├── utils/              # Helper functions
└── screens/            # Different app screens
```

## Next Steps

- [ ] Implement voice recording functionality
- [ ] Integrate emotion analysis AI
- [ ] Build visual art generation system
- [ ] Create audio/music generation
- [ ] Integrate GPT for text responses
- [ ] Add diary and storage system
- [ ] Implement sharing functionality
- [ ] iOS App Store preparation

## Technologies Used

- React Native + Expo
- OpenAI GPT API
- Audio processing libraries
- Canvas/SVG for visual generation
- iOS native integrations
