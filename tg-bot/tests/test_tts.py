"""Тесты tts.py (Yandex SpeechKit v1): нормализация + формирование запроса.
Сеть мокается — токены Yandex не расходуются."""
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tts


def test_normalize_убирает_разметку_и_эмодзи():
    r = tts.normalize_for_tts("Вот **парадокс** — свет белый.\n\nНебо голубое! 🌌")
    assert "*" not in r and "🌌" not in r and "\n" not in r and "—" not in r
    assert "парадокс" in r and "голубое" in r


def test_synthesize_шлёт_oggopus_voice_folder():
    with patch.dict(os.environ, {"YANDEX_API_KEY": "k", "YANDEX_FOLDER_ID": "f", "YANDEX_VOICE": "filipp"}):
        with patch("tts.requests.post") as post:
            resp = MagicMock()
            resp.content = b"OGGfake"
            resp.raise_for_status = MagicMock()
            post.return_value = resp
            out = tts.synthesize("Привет, наука.", "/tmp/_t.ogg")
            assert out == "/tmp/_t.ogg"
            data = post.call_args.kwargs["data"]
            assert data["format"] == "oggopus"
            assert data["voice"] == "filipp"
            assert data["lang"] == "ru-RU"
            assert data["folderId"] == "f"
            assert os.path.exists("/tmp/_t.ogg")
    os.remove("/tmp/_t.ogg")
