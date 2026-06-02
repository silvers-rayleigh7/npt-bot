#!/usr/bin/env python3
"""ElevenLabs TTS → Telegram voice (opus ogg).

Usage: python3 tts.py "текст ответа" [output.ogg]

Две функции:
  fetch_audio(text) -> mp3-байты   (ElevenLabs API)
  to_voice(mp3, out) -> путь .ogg  (ffmpeg mp3→opus, формат Telegram voice)
"""
import os
import subprocess
import sys
import tempfile

import requests

MODEL = "eleven_multilingual_v2"


def fetch_audio(text: str) -> bytes:
    """Запросить озвучку у ElevenLabs, вернуть mp3-байты."""
    voice_id = os.environ["ELEVENLABS_VOICE_ID"]
    api_key = os.environ["ELEVENLABS_API_KEY"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    resp = requests.post(
        url,
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": MODEL,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content


def to_voice(mp3_bytes: bytes, out_path: str) -> str:
    """Конвертировать mp3-байты в opus ogg (формат Telegram voice)."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(mp3_bytes)
        mp3_path = f.name
    try:
        subprocess.run(
            ["ffmpeg", "-i", mp3_path, "-c:a", "libopus", "-b:a", "32k",
             "-ar", "48000", out_path, "-y"],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(mp3_path)
    return out_path


def synthesize(text: str, out_path: str = "/tmp/answer.ogg") -> str:
    return to_voice(fetch_audio(text), out_path)


if __name__ == "__main__":
    text = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/answer.ogg"
    print(synthesize(text, out))
