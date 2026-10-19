"""Voice-over for the reels: reads a narration script and speaks it with Piper.

Piper (https://github.com/OHF-Voice/piper1-gpl) is a free, offline neural
text-to-speech engine. The voice model is downloaded into voices/ the first
time it is needed. Generated clips are cached in media/voiceover/, so only
lines you edit are re-synthesised.
"""

import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VOICE_DIR = ROOT / "voices"
CACHE_DIR = ROOT / "media" / "voiceover"

# "joe" is trained on a CC0 (public domain) dataset, so it is safe to post.
VOICE = "en_US-joe-medium"
VOICE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/"
SPEED = 1.0  # >1 is slower, <1 is faster (Piper's "length scale")
SENTENCE_PAUSE = 0.3  # seconds of silence between sentences


def load_script(name):
    """Parse scripts/<name>.md into {section: text}.

    Sections start with "## key". Lines starting with ">" are notes for
    humans and are not spoken.
    """
    sections, key = {}, None
    for line in (ROOT / "scripts" / f"{name}.md").read_text().splitlines():
        if line.startswith("## "):
            key = line[3:].strip()
            sections[key] = []
        elif key and line.strip() and not line.lstrip().startswith(">"):
            sections[key].append(line.strip())
    return {k: " ".join(v) for k, v in sections.items()}


def _voice_model():
    model = VOICE_DIR / f"{VOICE}.onnx"
    for path in (model, model.with_suffix(".onnx.json")):
        if not path.exists():
            VOICE_DIR.mkdir(exist_ok=True)
            print(f"Downloading voice {path.name} ...")
            urllib.request.urlretrieve(VOICE_URL + path.name, path)
    return model


def _duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def speak(text):
    """Synthesise text (cached). Returns (wav_path, duration_seconds)."""
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{SENTENCE_PAUSE}|{text}".encode()).hexdigest()[:16]
    out = CACHE_DIR / f"{key}.wav"
    if not out.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        raw = out.with_suffix(".raw.wav")
        subprocess.run(
            [sys.executable, "-m", "piper", "-m", str(_voice_model()), "-f", str(raw),
             "--length-scale", str(SPEED), "--sentence-silence", str(SENTENCE_PAUSE)],
            input=text, text=True, check=True, capture_output=True,
        )
        # Even out loudness (about -16 LUFS, typical for social video) and resample for AAC.
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
             "-ar", "44100", str(out)],
            check=True,
        )
        raw.unlink()
    return out, _duration(out)
