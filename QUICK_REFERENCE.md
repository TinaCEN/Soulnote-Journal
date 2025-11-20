# Quick Reference - How to Use & Edit Soulnote 🎨

## For Beginners: Two Ways to Use Soulnote

### Method 1: Simple CLI (VS Code Terminal Only) ⭐ EASIEST

```bash
# Just run this in VS Code terminal:
python simple_cli.py

# Then:
# 1. Type your feelings
# 2. Press Enter TWICE when done
# 3. Get instant analysis + poster!
# 4. No web browser needed!
```

**Perfect for:** Quick journaling, learning Python, testing

---

### Method 2: Full Web App (Browser)

```bash
# 1. Start the backend server:
python backend/app.py

# 2. Open: frontend/index.html in browser
# Or serve it:
cd frontend
python -m http.server 8000
# Then go to: http://localhost:8000
```

**Perfect for:** Full features, voice recording, beautiful UI

---

## How to Customize & Edit

### 🎨 1. Add Beautiful UI Components

**File to edit:** `static/css/style.css`

#### Example: Make buttons glow
```css
/* Add at end of style.css */
.btn-glow {
    background: linear-gradient(45deg, #667eea, #764ba2);
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.6);
    animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.6); }
    50% { box-shadow: 0 0 40px rgba(102, 126, 234, 1); }
}
```

Then in `frontend/index.html`, use it:
```html
<button class="btn btn-primary btn-glow">Analyze</button>
```

#### Example: Add gradient background
```css
/* In style.css, change body background (line 27) */
body {
    background: linear-gradient(135deg, 
        #667eea 0%, 
        #764ba2 50%, 
        #f093fb 100%);
}
```

#### Example: Add floating animation
```css
.logo {
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}
```

---

### 🎭 2. Add New Emotions

**File to edit:** `utils/poster_generator.py` (line 19)

```python
EMOTION_COLORS = {
    'joy': (45, 0.8, 0.95),      # Yellow
    'sadness': (220, 0.6, 0.6),  # Blue
    
    # ADD YOUR NEW EMOTIONS HERE:
    'excited': (30, 1.0, 1.0),   # Bright Orange
    'grateful': (150, 0.7, 0.9), # Green
    'confused': (280, 0.5, 0.7), # Purple
    'proud': (60, 0.8, 0.9),     # Gold
}
```

**Color format:** (Hue 0-360, Saturation 0-1, Value 0-1)
- Hue: 0=Red, 45=Yellow, 120=Green, 180=Cyan, 220=Blue, 280=Purple, 330=Pink
- Saturation: 0=Gray, 1=Vivid
- Value: 0=Dark, 1=Bright

---

### 🤖 3. Change AI Responses

**File to edit:** `models/lmstudio_client.py`

#### Make AI more detailed (line 65):
```python
system_prompt = """You are an expert psychologist and emotion analyst.
Analyze the emotional content with GREAT DETAIL.
Consider subtle nuances and mixed emotions.
Return a JSON response with..."""
```

#### Make AI more poetic (line 116):
```python
system_prompt = """You are a poetic philosopher and emotional guide.
Write BEAUTIFUL, INSPIRING reflections on human emotions.
Use metaphors, imagery, and wisdom from great thinkers.
Make it profound yet accessible."""
```

#### Change response length (line 137):
```python
response = self.generate_completion(
    prompt=user_prompt,
    system_prompt=system_prompt,
    temperature=0.8,
    max_tokens=400  # Change from 200 to 400 for longer notes
)
```

---

### 📏 4. Change Poster Sizes

**File to edit:** `utils/poster_generator.py` (line 47)

```python
# Default (Instagram portrait)
self.width = 1080
self.height = 1350

# Square (Instagram post)
self.width = 1080
self.height = 1080

# Widescreen (Twitter)
self.width = 1200
self.height = 675

# Story (Instagram/Facebook)
self.width = 1080
self.height = 1920

# Desktop wallpaper
self.width = 1920
self.height = 1080
```

---

### 🎨 5. Customize Poster Design

**File to edit:** `utils/poster_generator.py`

#### Change font sizes (line 148):
```python
title_font = ImageFont.truetype("arial.ttf", 60)  # Bigger title
quote_font = ImageFont.truetype("arial.ttf", 40)  # Bigger quotes
```

#### Add more artistic elements (line 244):
```python
def _add_artistic_elements(self, img, primary_color, secondary_color):
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Add MORE circles
    for i in range(10):  # Change from 5 to 10
        size = np.random.randint(50, 400)  # Bigger range
        # ... rest of code
```

---

### 🌈 6. Change Color Themes

**File to edit:** `static/css/style.css` (line 3)

```css
:root {
    /* Original (Purple/Indigo) */
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    
    /* Try these themes: */
    
    /* Ocean Theme */
    --primary-color: #06b6d4;
    --secondary-color: #3b82f6;
    
    /* Sunset Theme */
    --primary-color: #f97316;
    --secondary-color: #ec4899;
    
    /* Forest Theme */
    --primary-color: #10b981;
    --secondary-color: #84cc16;
    
    /* Royal Theme */
    --primary-color: #8b5cf6;
    --secondary-color: #ec4899;
}
```

---

## Common Editing Patterns

### Pattern 1: Change Text
1. Open the file
2. Find the text (Ctrl+F)
3. Change it
4. Save
5. Refresh browser (for HTML/CSS/JS) or restart server (for Python)

### Pattern 2: Change Numbers
1. Find the variable (like `self.width`)
2. Change the number
3. Save
4. Test!

### Pattern 3: Change Colors
1. Find the color code (#6366f1 or RGB)
2. Use a color picker: [color.adobe.com](https://color.adobe.com)
3. Replace the code
4. Save and refresh

---

## File Editing Cheat Sheet

| What to Change | File to Edit | Line |
|---------------|--------------|------|
| Button colors | `static/css/style.css` | 3-10 |
| Button text | `frontend/index.html` | Search for button |
| Poster size | `utils/poster_generator.py` | 47-48 |
| Emotion colors | `utils/poster_generator.py` | 19-33 |
| AI prompts | `models/lmstudio_client.py` | 65, 116 |
| Page title | `frontend/index.html` | 6 |
| Response length | `models/lmstudio_client.py` | 137 |
| Server port | `backend/app.py` | 185 |

---

## Testing Your Changes

### For Python Changes:
```bash
# Stop server (Ctrl+C)
# Restart:
python backend/app.py
```

### For HTML/CSS/JS Changes:
```
Just refresh your browser! (F5 or Ctrl+R)
```

### For CLI Changes:
```bash
python simple_cli.py
```

---

## Learning Path for Beginners

### Week 1: Start Simple
- ✅ Run `simple_cli.py` to understand flow
- ✅ Change emotion colors in `poster_generator.py`
- ✅ Modify CSS colors in `style.css`

### Week 2: Customize UI
- Change button styles
- Add new gradients
- Modify fonts and sizes

### Week 3: Enhance AI
- Edit AI prompts
- Adjust response lengths
- Add new emotion types

### Week 4: Advanced
- Create new poster layouts
- Add new export formats
- Build custom features

---

## Where to Start RIGHT NOW

1. **Try the CLI version:**
   ```bash
   python simple_cli.py
   ```

2. **Make your first edit:**
   - Open `static/css/style.css`
   - Line 25: Change `#667eea` to `#ff6b6b` (red theme!)
   - Save and refresh browser

3. **Add a new emotion:**
   - Open `utils/poster_generator.py`
   - Line 33: Add `'excited': (30, 1.0, 1.0),`
   - Save and test!

---

## 💡 Pro Tips

1. **Always test small changes first**
2. **Save before testing** (Ctrl+S)
3. **Use VS Code's search** (Ctrl+F) to find things
4. **Comment out code** with `#` to test changes
5. **Check the terminal** for error messages

---

## Getting Help

- **Read:** `BEGINNER_GUIDE.md` - Detailed explanations
- **See:** Code comments - Every file has explanations
- **Test:** `python simple_cli.py` - Quick testing
- **Debug:** Check terminal for error messages

Happy coding! 🎨✨
