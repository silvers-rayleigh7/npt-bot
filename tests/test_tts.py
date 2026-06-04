"""Тесты tts.py (Yandex SpeechKit v3): нормализация + парсинг потока чанков.
Сеть мокается — токены Yandex не расходуются."""
import base64
import json
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tts


def test_normalize_убирает_разметку_и_эмодзи():
    r = tts.normalize_for_tts("Вот **парадокс** — свет белый.\n\nНебо голубое! 🌌")
    assert "*" not in r and "🌌" not in r and "\n" not in r and "—" not in r
    assert "парадокс" in r and "голубое" in r


def test_synthesize_собирает_чанки_и_шлёт_voice():
    # v3 отдаёт поток JSON-строк с base64-аудио
    chunk = base64.b64encode(b"OGGfakeaudio").decode()
    body = json.dumps({"result": {"audioChunk": {"data": chunk}}})
    with patch.dict(os.environ, {"YANDEX_API_KEY": "k", "YANDEX_VOICE": "anton"}):
        with patch("tts.requests.post") as post:
            resp = MagicMock()
            resp.text = body + "\n" + body  # два чанка
            resp.raise_for_status = MagicMock()
            post.return_value = resp
            out = tts.synthesize("Привет, наука.", "/tmp/_t.ogg")
            assert out == "/tmp/_t.ogg"
            sent = post.call_args.kwargs["json"]
            assert sent["hints"][0]["voice"] == "anton"
            assert sent["outputAudioSpec"]["containerAudio"]["containerAudioType"] == "OGG_OPUS"
            assert os.path.getsize("/tmp/_t.ogg") == len(b"OGGfakeaudio") * 2
    os.remove("/tmp/_t.ogg")
