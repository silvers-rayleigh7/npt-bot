#!/usr/bin/env python3
"""ElevenLabs TTS → Telegram voice (opus ogg).

Usage: python3 tts.py "текст ответа" [output.ogg]

Две функции:
  fetch_audio(text) -> mp3-байты   (ElevenLabs API)
  to_voice(mp3, out) -> путь .ogg  (ffmpeg mp3→opus, формат Telegram voice)
"""
import os
import re
import subprocess
import sys
import tempfile
import time

import requests

MODEL = "eleven_multilingual_v2"


def normalize_for_tts(text: str) -> str:
    """Очистить текст для озвучки: убрать разметку/эмодзи, склеить переносы,
    тире → запятая (мягкая пауза). Это чинит «рваные» паузы ElevenLabs."""
    text = re.sub(r"[*_#`>]", "", text)            # markdown
    text = text.replace("\n", " ")                  # переносы строк → пробел
    text = re.sub(r"\s*[—–]\s*", ", ", text)        # длинное тире → запятая
    text = re.sub(r"[^\w\s.,!?;:()«»\"'\-]", "", text, flags=re.UNICODE)  # убрать эмодзи/символы
    text = re.sub(r"\s+", " ", text)                # схлопнуть пробелы
    return text.strip()


def fetch_audio(text: str, retries: int = 3) -> bytes:
    """Запросить озвучку у ElevenLabs, вернуть mp3-байты. С повторами при сбое."""
    voice_id = os.environ["ELEVENLABS_VOICE_ID"]
    api_key = os.environ["ELEVENLABS_API_KEY"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "model_id": MODEL,
        "voice_settings": {
            "stability": 0.65,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.post(
                url,
                headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))  # backoff: 1.5s, 3s
    raise last_err


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
    return to_voice(fetch_audio(normalize_for_tts(text)), out_path)


if __name__ == "__main__":
    text = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/answer.ogg"
    print(synthesize(text, out))
