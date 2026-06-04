#!/usr/bin/env python3
"""Yandex SpeechKit v1 TTS → Telegram voice (oggopus напрямую, без ffmpeg).

v1: нативно-русский, голос filipp (классический мужской диктор), готовый ogg
одним ответом — надёжная доставка. Usage: python3 tts.py "текст" [output.ogg]

Env: YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_VOICE (по умолч. filipp), YANDEX_SPEED.
"""
import os
import re
import sys
import time

import requests

API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
DEFAULT_VOICE = "filipp"


def normalize_for_tts(text: str) -> str:
    """Очистить текст для озвучки: убрать markdown/эмодзи, склеить переносы, тире → запятая."""
    text = re.sub(r"[*_#`>]", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    text = re.sub(r"[^\w\s.,!?;:()«»\"'\-+]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def synthesize(text: str, out_path: str = "/tmp/answer.ogg", retries: int = 3) -> str:
    """Озвучить текст через Yandex SpeechKit v1, сохранить oggopus (формат Telegram voice)."""
    api_key = os.environ["YANDEX_API_KEY"]
    data = {
        "text": normalize_for_tts(text),
        "voice": os.environ.get("YANDEX_VOICE", DEFAULT_VOICE),
        "folderId": os.environ["YANDEX_FOLDER_ID"],
        "lang": "ru-RU",
        "format": "oggopus",
        "sampleRateHertz": "48000",
    }
    if os.environ.get("YANDEX_SPEED"):
        data["speed"] = os.environ["YANDEX_SPEED"]
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.post(
                API_URL,
                headers={"Authorization": f"Api-Key {api_key}"},
                data=data,
                timeout=30,
            )
            r.raise_for_status()
            if not r.content:
                raise RuntimeError("Yandex вернул пустой ответ")
            with open(out_path, "wb") as f:
                f.write(r.content)
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
