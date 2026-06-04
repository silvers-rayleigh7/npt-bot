#!/usr/bin/env python3
"""Yandex SpeechKit v3 TTS → Telegram voice (oggopus напрямую, без ffmpeg).

Нативно-русский движок: правильные ударения и интонация из коробки.
Голос по умолчанию — anton (v3). Usage: python3 tts.py "текст" [output.ogg]

Env: YANDEX_API_KEY, YANDEX_VOICE (по умолч. anton), YANDEX_SPEED (опц.).
"""
import base64
import json
import os
import re
import sys
import time

import requests

API_URL = "https://tts.api.cloud.yandex.net/tts/v3/utteranceSynthesis"
DEFAULT_VOICE = "anton"


def normalize_for_tts(text: str) -> str:
    """Очистить текст для озвучки: убрать markdown/эмодзи, склеить переносы, тире → запятая."""
    text = re.sub(r"[*_#`>]", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    text = re.sub(r"[^\w\s.,!?;:()«»\"'\-+]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def synthesize(text: str, out_path: str = "/tmp/answer.ogg", retries: int = 3) -> str:
    """Озвучить текст через Yandex SpeechKit v3, сохранить oggopus (формат Telegram voice)."""
    api_key = os.environ["YANDEX_API_KEY"]
    hint = {"voice": os.environ.get("YANDEX_VOICE", DEFAULT_VOICE)}
    if os.environ.get("YANDEX_SPEED"):
        hint["speed"] = float(os.environ["YANDEX_SPEED"])
    body = {
        "text": normalize_for_tts(text),
        "outputAudioSpec": {"containerAudio": {"containerAudioType": "OGG_OPUS"}},
        "hints": [hint],
        "loudnessNormalizationType": "LUFS",
    }
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.post(
                API_URL,
                headers={"Authorization": f"Api-Key {api_key}"},
                json=body,
                timeout=30,
            )
            r.raise_for_status()
            audio = b""
            for line in r.text.strip().split("\n"):
                if not line:
                    continue
                try:
                    chunk = json.loads(line).get("result", {}).get("audioChunk", {}).get("data")
                    if chunk:
                        audio += base64.b64decode(chunk)
                except (json.JSONDecodeError, ValueError):
                    pass
            if not audio:
                raise RuntimeError("Yandex v3 вернул пустой аудиопоток")
            with open(out_path, "wb") as f:
                f.write(audio)
            return out_path
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise last_err


if __name__ == "__main__":
    text = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/answer.ogg"
    print(synthesize(text, out))
