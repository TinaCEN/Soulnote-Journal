"""
Emotion Archive Manager - Persist generated story cards and emotions over time.

Stores entries in a JSON file under output/emotion_archive.json.
Each entry:
{
  "id": str,                # unique id
  "timestamp": iso8601,     # UTC time
  "date": "YYYY-MM-DD",     # local date string
  "primary_emotion": str,
  "emotions": {emotion: int},
  "text": str,              # original user text (optional)
  "summary": str,           # concise sentence for display
  "card_path": str          # relative/absolute path to saved image
}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import threading


class EmotionArchive:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.archive_path = self.output_dir / 'emotion_archive.json'
        self._lock = threading.Lock()
        if not self.archive_path.exists():
            self._write_json({"entries": []})

    def _read_json(self) -> Dict:
        try:
            with self.archive_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"entries": []}

    def _write_json(self, data: Dict):
        tmp = self.archive_path.with_suffix('.json.tmp')
        with tmp.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self.archive_path)

    def _today_str(self) -> str:
        # Local date string
        return datetime.now().strftime('%Y-%m-%d')

    def add_entry(
        self,
        primary_emotion: str,
        emotions: Dict[str, int],
        card_path: str,
        summary: str,
        text: str = '',
        philosophical_note: str = '',
        source: str = 'text'
    ) -> Dict:
        entry = {
            'id': uuid.uuid4().hex,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'date': self._today_str(),
            'primary_emotion': primary_emotion,
            'emotions': emotions,
            'text': text,
            'summary': summary,
            'card_path': card_path,
            'philosophical_note': philosophical_note,
            'source': source,
        }
        with self._lock:
            data = self._read_json()
            # Keep BeReal-like: first entry of the day is the "daily"; others are "retakes"
            entries: List[Dict] = data.get('entries', [])
            entries.append(entry)
            # Keep only last 1000 entries to avoid unbounded growth
            data['entries'] = entries[-1000:]
            self._write_json(data)
        return entry

    def list_entries(self, limit: Optional[int] = None) -> List[Dict]:
        data = self._read_json()
        entries = data.get('entries', [])
        entries.sort(key=lambda e: e.get('timestamp', ''), reverse=True)
        return entries[:limit] if limit else entries

    def stats(self, days: Optional[int] = None) -> Dict[str, int]:
        from datetime import timedelta
        entries = self.list_entries()
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            entries = [e for e in entries if _parse_ts(e.get('timestamp')) >= cutoff]
        agg: Dict[str, int] = {}
        for e in entries:
            p = (e.get('primary_emotion') or '').lower()
            if not p:
                continue
            agg[p] = agg.get(p, 0) + 1
        return agg


def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        return datetime.utcnow()
