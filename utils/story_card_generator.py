"""
Story Card Generator - Create shareable story images (Instagram/WhatsApp/WeChat)
with the Philosophical Reflection text over an emotion-blended background.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import colorsys
import os

# Reuse color mapping logic from PosterGenerator to keep consistency
from .poster_generator import PosterGenerator


class StoryCardGenerator:
    def __init__(self, output_dir: Path = Path('output')):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

        # Story format (suitable for Instagram/WhatsApp/WeChat)
        self.width = 1080
        self.height = 1920

        self._poster_gen = PosterGenerator(output_dir)
        # Short motivational lines keyed by primary emotion
        self.MOTIVATION = {
            'joy': "Keep nurturing your light.",
            'sadness': "You’re healing—take one gentle step.",
            'anger': "Channel it into clear, constructive action.",
            'fear': "Courage is moving softly despite fear.",
            'surprise': "Stay curious—new paths are opening.",
            'disgust': "Choose what aligns with your values.",
            'peace': "Carry this calm into your next step.",
            'neutral': "Small steps still move you forward.",
            'love': "Lead with kindness—start with yourself.",
            'anxiety': "Breathe; one small step at a time.",
            'confusion': "Clarity grows with the next small action.",
        }
        # English labels for a natural sentence
        self.EMO_LABEL_EN = {
            'joy': 'joy',
            'happiness': 'joy',
            'sadness': 'sadness',
            'anger': 'anger',
            'fear': 'fear',
            'surprise': 'surprise',
            'disgust': 'disgust',
            'love': 'love',
            'anxiety': 'anxiety',
            'peace': 'calm',
            'neutral': 'balance',
            'trust': 'trust',
            'anticipation': 'anticipation',
            'calm': 'calm',
            'confusion': 'confusion',
        }

    def _emotion_color(self, name: str) -> Tuple[int, int, int]:
        return self._poster_gen._get_emotion_color(name)

    def _vibrantize_rgb(self, rgb: Tuple[int, int, int], min_s: float = 0.32, sat_boost: float = 1.18) -> Tuple[int, int, int]:
        """Ensure a minimum saturation and gently boost saturation to avoid grays.
        Accepts and returns RGB in 0-255 integers.
        """
        r, g, b = rgb
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if s < min_s:
            s = min_s
            v = max(v, 0.88)
        else:
            s = min(1.0, s * sat_boost)
        rr, gg, bb = colorsys.hsv_to_rgb(h, s, v)
        return (int(rr * 255), int(gg * 255), int(bb * 255))

    def _sorted_emotions(self, emotions: Dict[str, float]) -> List[Tuple[str, float]]:
        items = [(k, max(0.0, float(v))) for k, v in emotions.items() if v is not None]
        total = sum(v for _, v in items)
        if total <= 0:
            return [('neutral', 100.0)]
        # Normalize percentages
        items = [(k, (v / total) * 100.0) for k, v in items]
        items.sort(key=lambda x: x[1], reverse=True)
        # Keep top 3 for clean gradients
        return items[:3]

    def _multi_stop_gradient(self, stops: List[Tuple[float, Tuple[int, int, int]]]) -> Image.Image:
        """
        Create a vertical multi-stop linear gradient image.
        Stops: list of (position_fraction[0-1], (r,g,b)). Must be sorted by position.
        """
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        # Ensure stops cover 0..1
        if not stops or stops[0][0] > 0:
            first = stops[0][1] if stops else (128, 128, 128)
            stops = [(0.0, first)] + stops
        if stops[-1][0] < 1:
            stops = stops + [(1.0, stops[-1][1])]

        # Draw by rows, interpolating within the current stop segment
        seg_idx = 0
        for y in range(self.height):
            t = y / (self.height - 1)
            # Advance segment
            while seg_idx < len(stops) - 2 and t > stops[seg_idx + 1][0]:
                seg_idx += 1
            (t0, c0), (t1, c1) = stops[seg_idx], stops[seg_idx + 1]
            # Local interpolation
            local = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            r = int(c0[0] * (1 - local) + c1[0] * local)
            g = int(c0[1] * (1 - local) + c1[1] * local)
            b = int(c0[2] * (1 - local) + c1[2] * local)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        return img

    def _build_background(self, emotions: Dict[str, float]) -> Image.Image:
        """Create a soft blurred multi-color background from top emotions.
        Uses large translucent blobs with heavy Gaussian blur for a dreamy look.
        """
        top = self._sorted_emotions(emotions)

        # Base canvas tinted from primary emotion (avoid neutral/gray bases)
        primary_name = (top[0][0] if top else 'neutral')
        base_rgb = self._vibrantize_rgb(self._emotion_color(primary_name))
        # Pastelize the base a bit to keep readability
        hr, hg, hb = base_rgb
        bh, bs, bv = colorsys.rgb_to_hsv(hr / 255.0, hg / 255.0, hb / 255.0)
        bs = max(0.28, min(0.5, bs * 0.7))
        bv = min(1.0, max(0.92, bv))
        br, bg, bb = colorsys.hsv_to_rgb(bh, bs, bv)
        base_color = (int(br * 255), int(bg * 255), int(bb * 255), 255)
        base = Image.new('RGBA', (self.width, self.height), base_color)

        # Blobs layer
        blobs = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(blobs)

        # Positions and sizes for up to 3 blobs
        positions = [
            (self.width * 0.5, self.height * 0.32, self.width * 0.95),   # center-top, biggest
            (self.width * 0.28, self.height * 0.72, self.width * 0.85),  # bottom-left
            (self.width * 0.72, self.height * 0.78, self.width * 0.80),  # bottom-right
        ]

        for i, (name, pct) in enumerate(top[:3]):
            cx, cy, diameter = positions[i]
            radius = diameter / 2
            color = self._vibrantize_rgb(self._emotion_color(name))
            alpha = int(170 + min(70, pct))  # slightly stronger for more impact
            bbox = [
                int(cx - radius), int(cy - radius),
                int(cx + radius), int(cy + radius),
            ]
            bdraw.ellipse(bbox, fill=color + (alpha,))

        # Strong blur for blobs
        blobs = blobs.filter(ImageFilter.GaussianBlur(radius=180))

        # Composite onto base
        combined = Image.alpha_composite(base, blobs)

        # Gentle global blur to unify
        combined = combined.filter(ImageFilter.GaussianBlur(radius=3))

        # Subtle vignette for edge softness
        vignette = Image.new('L', (self.width, self.height), 0)
        vdraw = ImageDraw.Draw(vignette)
        margin = 60
        vdraw.ellipse([margin, margin, self.width - margin, self.height - margin], fill=255)
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=120))
        # Colored vignette overlay (tinted to primary hue) to avoid gray edges
        ov_h, ov_s, ov_v = bh, max(bs, 0.45), 0.42
        orr, org, orb = colorsys.hsv_to_rgb(ov_h, ov_s, ov_v)
        overlay = Image.new('RGBA', (self.width, self.height), (int(orr * 255), int(org * 255), int(orb * 255), 70))
        inv_mask = Image.eval(vignette, lambda x: 255 - x)
        combined = Image.alpha_composite(
            combined,
            Image.composite(overlay, Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0)), inv_mask)
        )

        # Higher saturation/brightness for more vibrant look
        combined = ImageEnhance.Color(combined).enhance(1.6)
        combined = ImageEnhance.Brightness(combined).enhance(1.06)

        return combined

    def _try_load(self, names: List[str], size: int) -> ImageFont.ImageFont:
        # Common Windows font directory
        win_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        for name in names:
            # Try direct name
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                pass
            # Try Windows Fonts folder
            try:
                return ImageFont.truetype(os.path.join(win_dir, name), size)
            except Exception:
                pass
        return ImageFont.load_default()

    def _load_fonts(self) -> Tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
        # Prefer elegant serif fonts for philosophical tone
        header = self._try_load(['Garamond.ttf', 'Georgia.ttf', 'Cambria.ttf', 'Times New Roman.ttf', 'times.ttf'], 86)
        body = self._try_load(['Garamond.ttf', 'Georgia.ttf', 'Cambria.ttf', 'Times New Roman.ttf', 'times.ttf'], 36)
        return header, body

    def _wrap_text(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        words = text.split()
        lines: List[str] = []
        line: List[str] = []
        for w in words:
            test = ' '.join(line + [w])
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                line.append(w)
            else:
                if line:
                    lines.append(' '.join(line))
                line = [w]
        if line:
            lines.append(' '.join(line))
        return lines

    def _emotion_label_en(self, name: str) -> str:
        return self.EMO_LABEL_EN.get((name or '').lower(), (name or '').lower())

    def _compose_emotion_of_day(self, emotions: Dict[str, float]) -> str:
        # Build an English sentence using top emotions
        top = self._sorted_emotions(emotions)
        names = [self._emotion_label_en(n) for n, _ in top]
        if not names:
            return "Today I feel balanced."
        if len(names) == 1:
            return f"Today I feel {names[0]}."
        if len(names) == 2:
            return f"Today I feel {names[0]} with shades of {names[1]}."
        return f"Today I feel {names[0]} with hints of {names[1]} and {names[2]}."

    def _make_concise(self, text: str, max_chars: int = 260, max_sentences: int = 3) -> str:
        # Basic heuristic summarization: keep up to N short sentences within a char budget
        t = ' '.join(text.strip().split())
        if not t:
            return t
        # Split on sentence boundaries
        parts: List[str] = []
        sentence = ''
        for ch in t:
            sentence += ch
            if ch in '.!?':
                parts.append(sentence.strip())
                sentence = ''
        if sentence:
            parts.append(sentence.strip())
        concise: List[str] = []
        total = 0
        for p in parts:
            if not p:
                continue
            if len(concise) >= max_sentences:
                break
            if total + len(p) + (1 if concise else 0) > max_chars:
                break
            concise.append(p)
            total += len(p) + (1 if concise else 0)
        out = ' '.join(concise) if concise else (t[:max_chars].rsplit(' ', 1)[0] if len(t) > max_chars else t)
        if len(out) < len(t) and not out.endswith(('.', '!', '?')):
            out = out.rstrip(',;:') + '...'
        return out

    def _make_input_summary(self, text: str, max_keywords: int = 3) -> str:
        """Heuristic one-line summary: extract key terms and form a concise
        first-person phrase (no copy-paste). Supports basic EN/IT stopwords.
        """
        import re
        t = ' '.join((text or '').lower().strip().split())
        if not t:
            return ''
        # Remove URLs and punctuation
        t = re.sub(r'https?://\S+', '', t)
        t = re.sub(r'[^a-zA-ZàèéìòóùçÁÀÉÈÍÌÓÒÚÜüäëïöÄËÏÖñÑ\s]', ' ', t)

        stopwords = set(
            [
                # English
                'the','a','an','and','or','but','of','to','in','on','for','with','about','as','at','by','from','that','this','it','is','was','were','be','been','are','am','i','me','my','we','our','you','your','they','their','he','she','his','her','them','there','here','not','no','so','very','just','really','like','into','out','over','under','than','then','too','also','when','while','because','how','what','why','who','which','where','did','do','does','doing','have','has','had','get','got','makes','made','make','can','could','should','would','will','won','t','s','re','ve',
                # Italian
                'il','lo','la','i','gli','le','un','una','uno','di','a','da','in','con','su','per','tra','fra','che','come','perchè','perché','non','mi','ti','si','ci','vi','loro','io','tu','lui','lei','noi','voi','sono','sei','è','era','ero','eri','erano','stato','stata','stati','state','ho','hai','ha','abbiamo','avete','hanno','fare','fatto','fa','fai','fanno','cosa','come','quando','dove','per','anche','molto','poco','più','meno','molta','tanto','tanta','troppo','così','ma','o','e'
            ]
        )
        words = [w for w in t.split() if len(w) > 2 and w not in stopwords]
        if not words:
            return ''
        # Simple frequency count
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        # Top keywords
        top = sorted(freq.items(), key=lambda x: (-x[1], len(x[0])), reverse=False)[:max_keywords]
        keywords = [w for w, _ in top]
        if not keywords:
            return ''
        if len(keywords) == 1:
            return f"I wrote about {keywords[0]}."
        if len(keywords) == 2:
            return f"I wrote about {keywords[0]} and {keywords[1]}."
        return f"I wrote about {', '.join(keywords[:-1])} and {keywords[-1]}."

    def create_story_card(self, philosophical_text: str, emotions: Dict[str, float], user_text: str = '') -> Path:
        """
        Create a tall story card PNG with the reflection text on top of
        a blended background reflecting the emotion mix.
        """
        bg = self._build_background(emotions)
        img = Image.new('RGBA', (self.width, self.height))
        img.paste(bg, (0, 0))

        draw = ImageDraw.Draw(img)
        header_font, body_font = self._load_fonts()

        # Determine primary emotion (uppercase)
        primary = sorted(((k, float(v)) for k, v in emotions.items()), key=lambda x: x[1], reverse=True)
        primary_name = (primary[0][0] if primary else 'neutral')
        primary_text = primary_name.upper()

        # Central layout
        padding = 96
        max_width = int(self.width * 0.82)

        # Primary emotion heading (centered)
        hb = draw.textbbox((0, 0), primary_text, font=header_font)
        hw = hb[2] - hb[0]
        hh = hb[3] - hb[1]
        hx = (self.width - hw) // 2
        hy = padding + 10
        # Soft glow
        draw.text((hx + 2, hy + 2), primary_text, font=header_font, fill=(0, 0, 0, 120))
        draw.text((hx, hy), primary_text, font=header_font, fill=(255, 255, 255, 240))

        # Body text (centered, wrapped). Combine emotion + day-specific summary from user_text
        emotion_sentence = self._compose_emotion_of_day(emotions)
        day_summary = self._make_input_summary(user_text or '')
        sentence = emotion_sentence if not day_summary else f"{emotion_sentence} {day_summary}"
        # Keep concise if user text is long
        sentence = self._make_concise(sentence, max_chars=240, max_sentences=2)
        lines = self._wrap_text(draw, sentence, body_font, max_width)
        line_height = max(48, (body_font.getbbox('Ay')[3] - body_font.getbbox('Ay')[1]))
        total_height = len(lines) * line_height
        # Vertically center between header bottom and bottom padding
        min_top = hy + hh + 36
        y = max(min_top, (self.height - total_height) // 2)
        for idx, line in enumerate(lines):
            bb = draw.textbbox((0, 0), line, font=body_font)
            lw = bb[2] - bb[0]
            x = (self.width - lw) // 2
            draw.text((x + 1, y + 1), line, font=body_font, fill=(0, 0, 0, 140))
            fill = (246, 246, 246, 255)
            draw.text((x, y), line, font=body_font, fill=fill)
            y += line_height

        # Footer tip
        tip = 'Soulnote • Share your feeling'
        tb = draw.textbbox((0, 0), tip, font=body_font)
        tw = tb[2] - tb[0]
        draw.text(((self.width - tw) // 2, self.height - padding - 8), tip, font=body_font, fill=(255, 255, 255, 180))

        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = self.output_dir / f'story_card_{timestamp}.png'
        img.convert('RGB').save(output_path, quality=95)
        return output_path
