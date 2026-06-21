"""TTS: Silero (primary, offline) → edge-tts (fallback, online)."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import shutil
import subprocess
import wave
from pathlib import Path

log = logging.getLogger(__name__)


class SileroTTS:
    """Локальный, бесплатный, лучшее качество русского.

    Установка:
        pip install torch numpy
    Модель скачается автоматически с github.com/snakers4/silero-models при первом вызове.
    """

    def __init__(
        self,
        model_id: str = "v4_ru",
        speaker: str = "eugene",
        sample_rate: int = 48000,
        cache_dir: str | Path = "logs/tts_cache",
    ):
        import torch

        self.torch = torch
        self.speaker = speaker
        self.sample_rate = sample_rate
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # CPU достаточно — модель ~50 MB, синтез ~1s на ~30s аудио
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="ru",
            speaker=model_id,
            trust_repo=True,
        )
        self.model.to("cpu")

    def synth(self, text: str) -> Path:
        key = hashlib.sha1(f"{self.speaker}|{text}".encode()).hexdigest()[:16]
        out_mp3 = self.cache_dir / f"{key}.mp3"
        if out_mp3.exists() and out_mp3.stat().st_size > 0:
            return out_mp3
        out = self.cache_dir / f"{key}.wav"
        if out.exists() and out.stat().st_size > 0:
            return out
        audio = self.model.apply_tts(
            text=text,
            speaker=self.speaker,
            sample_rate=self.sample_rate,
            put_accent=True,
            put_yo=True,
        )
        import numpy as np  # noqa: WPS433 — отдельная зависимость

        samples = audio.detach().cpu().numpy()
        samples_i16 = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
        with wave.open(str(out), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(samples_i16.tobytes())
        if shutil.which("ffmpeg"):
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-loglevel",
                    "error",
                    "-i",
                    str(out),
                    "-codec:a",
                    "libmp3lame",
                    "-b:a",
                    "96k",
                    str(out_mp3),
                ],
                check=True,
            )
            if out_mp3.exists() and out_mp3.stat().st_size > 0:
                out.unlink(missing_ok=True)
                return out_mp3
        return out


class EdgeTTS:
    """Fallback: Microsoft Edge online TTS, тоже бесплатный, без API-ключа.

    Установка:
        pip install edge-tts
    """

    def __init__(
        self,
        voice: str = "ru-RU-DmitryNeural",
        rate: str = "+0%",
        volume: str = "+0%",
        cache_dir: str | Path = "logs/tts_cache",
    ):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def _synth_async(self, text: str, out: Path) -> Path:
        import edge_tts
        communicate = edge_tts.Communicate(
            text, self.voice, rate=self.rate, volume=self.volume
        )
        await communicate.save(str(out))
        return out

    def synth(self, text: str) -> Path:
        key = hashlib.sha1(f"{self.voice}|{text}".encode()).hexdigest()[:16]
        out = self.cache_dir / f"{key}.mp3"
        if out.exists() and out.stat().st_size > 0:
            return out
        return asyncio.run(self._synth_async(text, out))


def make_tts(cfg: dict):
    """Фабрика TTS с автоматическим fallback."""
    fallback = cfg.get("fallback", {})
    primary_cfg = cfg.get("silero", {})
    cache_dir = primary_cfg.get("cache_dir", "logs/tts_cache")
    if cfg.get("provider") == "edge_tts":
        return EdgeTTS(
            voice=fallback.get("voice", "ru-RU-DmitryNeural"),
            rate=fallback.get("rate", "+0%"),
            volume=fallback.get("volume", "+0%"),
            cache_dir=cache_dir,
        )
    primary_cfg = cfg.get("silero", {})
    try:
        return SileroTTS(
            model_id=primary_cfg.get("model_id", "v4_ru"),
            speaker=primary_cfg.get("speaker", "eugene"),
            sample_rate=primary_cfg.get("sample_rate", 48000),
            cache_dir=primary_cfg.get("cache_dir", "logs/tts_cache"),
        )
    except Exception as e:
        log.warning("Silero недоступен (%s) — переключаюсь на edge-tts", e)
        return EdgeTTS(
            voice=fallback.get("voice", "ru-RU-DmitryNeural"),
            rate=fallback.get("rate", "+0%"),
            volume=fallback.get("volume", "+0%"),
            cache_dir=cache_dir,
        )
