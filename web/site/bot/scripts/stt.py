"""STT через Groq (whisper-large-v3, бесплатный free-tier, OpenAI-совместимый)."""
from __future__ import annotations

from pathlib import Path

from openai import OpenAI


class GroqSTT:
    def __init__(
        self,
        api_key: str,
        model: str = "whisper-large-v3",
        language: str = "ru",
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=30,
        )
        self.model = model
        self.language = language

    def transcribe(self, audio_path: str | Path) -> str:
        with open(audio_path, "rb") as f:
            r = self.client.audio.transcriptions.create(
                file=f,
                model=self.model,
                language=self.language,
                response_format="text",
            )
        return r.strip() if isinstance(r, str) else r.text.strip()
