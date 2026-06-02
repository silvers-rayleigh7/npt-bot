"""Тест tts.py: конвертация mp3 → opus ogg (формат Telegram voice).

fetch_audio() (ElevenLabs) мокается; to_voice() тестируется на реальном
ffmpeg-сгенерированном mp3 — без расхода ElevenLabs-токенов.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tts import to_voice


def _make_test_mp3(path):
    """Сгенерировать валидный 1-сек mp3 тоном 440 Гц (без ElevenLabs)."""
    subprocess.run(
        ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
         "-c:a", "libmp3lame", path, "-y"],
        check=True, capture_output=True,
    )


def test_to_voice_produces_opus_ogg():
    with tempfile.TemporaryDirectory() as d:
        mp3 = os.path.join(d, "in.mp3")
        ogg = os.path.join(d, "out.ogg")
        _make_test_mp3(mp3)
        with open(mp3, "rb") as f:
            result = to_voice(f.read(), ogg)
        assert os.path.exists(result)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name", "-of", "csv=p=0", result],
            capture_output=True, text=True,
        )
        assert "opus" in probe.stdout  # Telegram voice требует opus
