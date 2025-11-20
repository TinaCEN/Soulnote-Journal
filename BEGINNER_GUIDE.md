# How Soulnote Works - For Beginners 🎓

## Understanding the File Structure

Think of your project like a **restaurant**:

### 1. **backend/app.py** = HEAD CHEF 👨‍🍳
- **What it does:** Coordinates everything
- **Role:** Receives requests from the web page, delegates tasks to helpers
- **Example:** When you click "Analyze Emotions", this file receives the request

```python
# In app.py line 52:
@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    # 1. Gets your text
    text = request.json.get('text')
    
    # 2. Asks emotion_analyzer to analyze it
    emotion_result = emotion_analyzer.analyze_text(text)
    
    # 3. Asks emotion_analyzer to generate philosophy
    philosophical_note = emotion_analyzer.generate_philosophical_note(...)
    
    # 4. Sends results back to web page
    return jsonify(results)
```

---

### 2. **models/lmstudio_client.py** = INGREDIENT SUPPLIER 🚚
- **What it does:** Talks to the AI (LM Studio)
- **Role:** Sends questions to AI, gets answers back
- **Example:** "AI, what emotions are in this text?"

```python
# This file has ONE main job:
class LMStudioClient:
    def generate_completion(self, prompt):
        # Sends question to AI
        response = requests.post("http://localhost:1234/...")
        return response  # Gets AI's answer
```

---

### 3. **models/emotion_analyzer.py** = QUALITY INSPECTOR 🔍
- **What it does:** Uses the AI to analyze emotions
- **Role:** Creates the right questions for the AI
- **Example:** Formats your text nicely and asks AI about emotions

```python
class EmotionAnalyzer:
    def analyze_text(self, text):
        # Uses lmstudio_client to ask AI about emotions
        emotion_data = self.lm_client.analyze_emotions(text)
        return emotion_data
```

---

### 4. **utils/audio_processor.py** = PREP COOK 🎤
- **What it does:** Converts voice to text, creates waveforms
- **Role:** Handles all audio tasks
- **Example:** Takes your voice recording → converts to text

---

### 5. **utils/poster_generator.py** = PASTRY CHEF 🎨
- **What it does:** Creates beautiful poster images
- **Role:** Takes emotions and text → makes art
- **Example:** "You're sad" → uses blue colors and creates poster

---

### 6. **utils/card_exporter.py** = PACKAGING 📦
- **What it does:** Resizes posters for social media
- **Role:** Takes poster → makes Instagram/Twitter versions

---

## How They Work Together (Step-by-Step)

### Example: User clicks "Analyze Emotions" with text

```
1. frontend/index.html (Web page)
   ↓ User clicks button
   
2. static/js/app.js (JavaScript)
   ↓ Sends text to server: fetch('http://localhost:5000/api/analyze/text')
   
3. backend/app.py (Flask server)
   ↓ Receives request at @app.route('/api/analyze/text')
   ↓ Calls: emotion_analyzer.analyze_text(text)
   
4. models/emotion_analyzer.py
   ↓ Calls: lm_client.analyze_emotions(text)
   
5. models/lmstudio_client.py
   ↓ Sends to AI: "What emotions are in this text?"
   ↓ AI responds with: {"primary_emotion": "joy", "emotions": {...}}
   
6. Back to app.py
   ↓ Calls: poster_generator.create_poster(...)
   
7. utils/poster_generator.py
   ↓ Creates beautiful image
   ↓ Saves to: output/poster_joy_20241029.png
   
8. Back to app.py
   ↓ Returns results to JavaScript
   
9. static/js/app.js
   ↓ Updates web page to show results
   
10. User sees: Emotions + Poster + Philosophy!
```

---

## How to Edit and Customize

### 1. **Add New Emotions** 🎨

Edit `utils/poster_generator.py` (line 19):

```python
EMOTION_COLORS = {
    'joy': (45, 0.8, 0.95),      # Yellow
    'sadness': (220, 0.6, 0.6),  # Blue
    # ADD YOUR NEW EMOTION:
    'excited': (30, 1.0, 1.0),   # Bright Orange
}
```

### 2. **Change AI Prompts** 🤖

Edit `models/lmstudio_client.py` (line 65):

```python
system_prompt = """You are an expert emotion analyst.
Analyze emotions and return JSON.
BE VERY DETAILED AND SPECIFIC."""  # Change this!
```

### 3. **Change Poster Size** 📏

Edit `utils/poster_generator.py` (line 47):

```python
self.width = 1080   # Change to 1920 for bigger
self.height = 1350  # Change to 1080 for square
```

### 4. **Add Beautiful UI Components** 💅

Edit `static/css/style.css` for styles:

```css
/* Add gradient button */
.btn-fancy {
    background: linear-gradient(45deg, #ff6b6b, #ffa500);
    border-radius: 30px;
    box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
}
```

Edit `frontend/index.html` to use it:

```html
<button class="btn btn-fancy">Analyze Emotions</button>
```

### 5. **Change Colors/Themes** 🎨

Edit `static/css/style.css` (line 3):

```css
:root {
    --primary-color: #6366f1;  /* Change to #ff6b6b for red */
    --secondary-color: #8b5cf6; /* Change to #ffa500 for orange */
}
```

---

## Run Without Web Browser (VS Code Only!)

I created a simple version you can run directly in VS Code terminal:

### **File: `simple_cli.py`** (I'll create this for you)

```python
# Just run: python simple_cli.py
# Type your feelings → Get analysis → Get poster
# No web browser needed!
```

Let me create this file now...
