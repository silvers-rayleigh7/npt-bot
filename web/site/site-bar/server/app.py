"""site-bar бэкенд: прокси между виджетом сайта и LLM (GigaChat → OpenRouter fallback)."""
from __future__ import annotations

import html as _html
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
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

# Retrieval-слой урока (опора на сюжеты/программу/веб). Мастер-флаг + мягкий импорт:
# если что-то не так с модулем — урок работает как раньше, без опоры.
RETRIEVAL_ENABLED = os.environ.get("RETRIEVAL_ENABLED", "0").strip() not in ("", "0", "false", "False")
try:
    from retrieval import gather_context, build_retrievers  # noqa: E402
    from retrieval.base import RetrievalQuery               # noqa: E402
    _RETRIEVERS = build_retrievers() if RETRIEVAL_ENABLED else []
except Exception:
    RETRIEVAL_ENABLED = False
    _RETRIEVERS = []
    RetrievalQuery = None

# Заявки гидов копятся в jsonl (append-only), уведомление — в Telegram админу.
GUIDE_APPLICATIONS = Path(os.environ.get("GUIDE_APPLICATIONS_PATH", ROOT / "guide_applications.jsonl"))
TG_NOTIFY_TOKEN = os.environ.get("TG_NOTIFY_TOKEN", "")
TG_NOTIFY_CHAT = os.environ.get("TG_NOTIFY_CHAT", "")


def _notify_telegram(text: str) -> bool:
    """Шлёт уведомление админу через Bot API (stateless, без процесса бота)."""
    if not (TG_NOTIFY_TOKEN and TG_NOTIFY_CHAT):
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_NOTIFY_TOKEN}/sendMessage",
            json={"chat_id": TG_NOTIFY_CHAT, "text": text,
                  "parse_mode": "HTML", "disable_web_page_preview": True},
            timeout=10,
        )
        return r.ok
    except Exception:
        return False

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
    sources: list[str] = Field(default_factory=list)   # заголовки источников опоры (для показа)


def _lesson_context(inp: "LessonIn"):
    """Собирает блок опоры и список источников. Любая ошибка → ("", []): урок не ломается."""
    if not (RETRIEVAL_ENABLED and _RETRIEVERS and RetrievalQuery):
        return "", []
    try:
        q = RetrievalQuery(grade=inp.grade, subject=inp.subject, topic=inp.topic,
                           location=inp.location, season=inp.season, text=inp.textbook)
        ctx = gather_context(q, retrievers=_RETRIEVERS)
        sources = []
        for line in ctx.splitlines()[1:]:
            # «[сюжет] Заголовок — …» → берём заголовок для показа под уроком
            if "]" in line and "—" in line:
                sources.append(line.split("]", 1)[1].split("—", 1)[0].strip())
        return ctx, sources[:6]
    except Exception:
        return "", []


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

    ctx, sources = _lesson_context(inp)
    user_content = (f"{ctx}\n\n" if ctx else "") + "Данные формы учителя:\n" + body
    messages = [
        {"role": "system", "content": LESSON_PROMPT},
        {"role": "user", "content": user_content},
    ]
    try:
        answer, provider = generate(
            messages, _PROVIDERS,
            max_tokens=int(os.environ.get("LESSON_MAX_TOKENS", "1100")),
            temperature=float(os.environ.get("LESSON_TEMPERATURE", "0.5")),
        )
        return LessonOut(lesson=answer, provider=provider, sources=sources)
    except ProviderError as e:
        return LessonOut(
            lesson="Не получилось собрать урок. Попробуйте ещё раз чуть позже.",
            provider=f"error:{e}",
        )


class GuideIn(BaseModel):
    name: str = ""          # ФИО
    contact: str = ""       # телефон / @telegram / email
    region: str = ""        # город/регион
    attestation: str = ""   # аттестация экскурсовода
    topics: str = ""        # темы/специализация
    experience: str = ""    # опыт (кратко)
    link: str = ""          # соцсети/сайт (опц.)
    consent: bool = False   # согласие на обработку ПД (152-ФЗ)
    website: str = ""        # honeypot: у людей пусто, боты заполняют


class GuideOut(BaseModel):
    ok: bool
    message: str


@app.post("/api/guide-register", response_model=GuideOut)
def guide_register(inp: GuideIn):
    if inp.website.strip():                       # honeypot сработал — тихо принимаем и игнорируем
        return GuideOut(ok=True, message="Заявка принята.")
    name, contact = inp.name.strip(), inp.contact.strip()
    if not name or not contact:
        return GuideOut(ok=False, message="Укажите, пожалуйста, имя и контакт.")
    if not inp.consent:
        return GuideOut(ok=False, message="Нужно согласие на обработку персональных данных.")

    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": name, "contact": contact, "region": inp.region.strip(),
        "attestation": inp.attestation.strip(), "topics": inp.topics.strip(),
        "experience": inp.experience.strip(), "link": inp.link.strip(),
    }
    try:
        GUIDE_APPLICATIONS.parent.mkdir(parents=True, exist_ok=True)
        with GUIDE_APPLICATIONS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        return GuideOut(ok=False, message="Не удалось сохранить заявку. Попробуйте позже.")

    esc = lambda s: _html.escape(s or "—")
    _notify_telegram(
        "🧭 <b>Новая заявка гида</b>\n"
        f"<b>Имя:</b> {esc(name)}\n"
        f"<b>Контакт:</b> {esc(contact)}\n"
        f"<b>Регион:</b> {esc(rec['region'])}\n"
        f"<b>Аттестация:</b> {esc(rec['attestation'])}\n"
        f"<b>Темы:</b> {esc(rec['topics'])}\n"
        f"<b>Опыт:</b> {esc(rec['experience'])}\n"
        f"<b>Ссылка:</b> {esc(rec['link'])}"
    )
    return GuideOut(ok=True, message="Спасибо! Заявка отправлена — свяжемся по указанному контакту.")
