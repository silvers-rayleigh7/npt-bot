#!/usr/bin/env python3
"""Yandex SpeechKit TTS → Telegram voice (oggopus напрямую, без ffmpeg).

Нативно-русский движок: правильные ударения и интонация из коробки.
Usage: python3 tts.py "текст ответа" [output.ogg]

Env: YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_VOICE (по умолч. filipp), YANDEX_SPEED.
"""
import os
import re
import sys
import time

import requests

API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
DEFAULT_VOICE = "filipp"  # мужской русский; альтернативы: ermil, zahar, alena, jane


def normalize_for_tts(text: str) -> str:
    """Очистить текст для озвучки: убрать markdown/эмодзи, склеить переносы,
    тире → запятая. Знак «+» сохраняем — это разметка ударения Yandex (опционально)."""
    text = re.sub(r"[*_#`>]", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    text = re.sub(r"[^\w\s.,!?;:()«»\"'\-+]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def synthesize(text: str, out_path: str = "/tmp/answer.ogg", retries: int = 3) -> str:
    """Озвучить текст через Yandex SpeechKit, сохранить oggopus (формат Telegram voice)."""
    api_key = os.environ["YANDEX_API_KEY"]
    folder = os.environ["YANDEX_FOLDER_ID"]
    data = {
        "text": normalize_for_tts(text),
        "voice": os.environ.get("YANDEX_VOICE", DEFAULT_VOICE),
        "folderId": folder,
        "lang": "ru-RU",
        "format": "oggopus",
        "sampleRateHertz": "48000",
        "speed": os.environ.get("YANDEX_SPEED", "1.0"),
    }
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
