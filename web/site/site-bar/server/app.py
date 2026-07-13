"""site-bar бэкенд: прокси между виджетом сайта и LLM (GigaChat → OpenRouter fallback)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
# Подхватываем .env рядом с приложением (для systemd дублируется через EnvironmentFile).
load_dotenv(ROOT / ".env")

from providers import build_providers, generate, ProviderError  # noqa: E402  (после load_dotenv)
SYSTEM_PROMPT = (ROOT / "system_prompt.md").read_text(encoding="utf-8")
LESSON_PROMPT = (ROOT / "lesson_prompt.md").read_text(encoding="utf-8")
MAX_CONTEXT_CHARS = 6000
MAX_HISTORY = 8

app = FastAPI(title="Tropa site-bar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

_PROVIDERS = build_providers()


class Msg(BaseModel):
    role: str
    content: str


class ChatIn(BaseModel):
    question: str
    page_context: str = ""
    history: list[Msg] = Field(default_factory=list)


class ChatOut(BaseModel):
    answer: str
    provider: str


@app.get("/api/health")
def health():
    return {"ok": True, "providers": [p.name for p in _PROVIDERS]}


@app.post("/api/chat", response_model=ChatOut)
def chat(inp: ChatIn):
    ctx = inp.page_context.strip()[:MAX_CONTEXT_CHARS]
    user_block = (
        (f"Текст сюжета, который читатель сейчас открыл:\n{ctx}\n\n" if ctx else "")
        + f"Вопрос читателя: {inp.question.strip()}"
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in inp.history[-MAX_HISTORY:]:
        if m.role in ("user", "assistant") and m.content.strip():
            messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": user_block})

    try:
        answer, provider = generate(
            messages, _PROVIDERS,
            max_tokens=int(os.environ.get("MAX_TOKENS", "700")),
            temperature=float(os.environ.get("TEMPERATURE", "0.4")),
        )
        return ChatOut(answer=answer, provider=provider)
    except ProviderError as e:
        return ChatOut(
            answer="Извините, сейчас не получилось ответить. Попробуйте ещё раз чуть позже.",
            provider=f"error:{e}",
        )


class LessonIn(BaseModel):
    grade: str = ""       # класс (1–11)
    subject: str = ""     # предмет
    textbook: str = ""    # учебник/автор (опц.)
    topic: str = ""       # тема (опц.)
    location: str = ""    # город/локация (опц.)
    season: str = ""      # сезон (опц.)


class LessonOut(BaseModel):
    lesson: str
    provider: str


@app.post("/api/lesson", response_model=LessonOut)
def lesson(inp: LessonIn):
    fields = [
        ("Класс", inp.grade), ("Предмет", inp.subject),
        ("Учебник/автор", inp.textbook), ("Тема", inp.topic),
        ("Локация", inp.location), ("Сезон", inp.season),
    ]
    body = "\n".join(f"{k}: {v.strip()}" for k, v in fields if v and v.strip())
    if not body:
        return LessonOut(lesson="Заполните хотя бы класс и предмет.", provider="none")
    messages = [
        {"role": "system", "content": LESSON_PROMPT},
        {"role": "user", "content": "Данные формы учителя:\n" + body},
    ]
    try:
        answer, provider = generate(
            messages, _PROVIDERS,
            max_tokens=int(os.environ.get("LESSON_MAX_TOKENS", "1100")),
            temperature=float(os.environ.get("LESSON_TEMPERATURE", "0.5")),
        )
        return LessonOut(lesson=answer, provider=provider)
    except ProviderError as e:
        return LessonOut(
            lesson="Не получилось собрать урок. Попробуйте ещё раз чуть позже.",
            provider=f"error:{e}",
        )
