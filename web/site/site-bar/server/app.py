"""site-bar бэкенд: прокси между виджетом сайта и LLM (GigaChat → OpenRouter fallback)."""
from __future__ import annotations

import html as _html
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
# Подхватываем .env рядом с приложением (для systemd дублируется через EnvironmentFile).
load_dotenv(ROOT / ".env")

from providers import build_providers, generate, ProviderError  # noqa: E402  (после load_dotenv)
SYSTEM_PROMPT = (ROOT / "system_prompt.md").read_text(encoding="utf-8")
LESSON_PROMPT = (ROOT / "lesson_prompt.md").read_text(encoding="utf-8")
METHODICHKA_PROMPT = (ROOT / "methodichka_prompt.md").read_text(encoding="utf-8")
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

# Гео-слой: тот же код, что у бота (site-bar/server/geo/, держится в синхроне sync-geo.sh).
# Мягкий импорт: если модуль/индекс недоступны — /api/geo вернёт мягкую ошибку, остальное живёт.
import sys as _sys  # noqa: E402
_GEO_DIR = ROOT / "geo"
try:
    _sys.path.insert(0, str(_GEO_DIR))
    from geo_place import build_geo_prompt, reverse_place  # noqa: E402
    from geo_match import nearest_storylines               # noqa: E402
    _GEO_INDEX = json.loads((_GEO_DIR / "geo_index.json").read_text(encoding="utf-8"))
    GEO_ENABLED = bool(_GEO_INDEX)
except Exception:
    GEO_ENABLED = False
    _GEO_INDEX = []

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


class GeoIn(BaseModel):
    lat: float
    lon: float
    question: str = ""
    page_context: str = ""
    history: list[Msg] = Field(default_factory=list)


class NearbyItem(BaseModel):
    title: str
    slug: str
    url: str
    dist_m: float


class GeoOut(BaseModel):
    answer: str
    provider: str
    place: dict = Field(default_factory=dict)
    nearby: list[NearbyItem] = Field(default_factory=list)


@app.post("/api/geo", response_model=GeoOut)
def geo(inp: GeoIn):
    """Гео-ответ: где пользователь + ближайшие сюжеты тропы. Та же логика, что у бота.

    Ближайшие сюжеты берём из geo_index.json (без сканирования markdown), а reverse_place/
    nearby_objects опрашивают OSM внутри build_geo_prompt — отказоустойчиво (try/except+кэш)."""
    if not GEO_ENABLED:
        return GeoOut(
            answer="Гео-подсказки временно недоступны — задайте вопрос обычным текстом.",
            provider="geo:disabled",
        )
    near = nearest_storylines(inp.lat, inp.lon, "", top=3, index=_GEO_INDEX)
    site = os.environ.get("SITE_URL", "https://tropa.fmin.xyz")
    nearby = [NearbyItem(title=n["title"], slug=n["slug"],
                         url=f"{site}/storylines/{n['slug']}/", dist_m=n["dist_m"])
              for n in near if n.get("title") and n.get("slug")]

    geo_prompt = build_geo_prompt(inp.lat, inp.lon, "", near=near)
    q = inp.question.strip() or "Что интересного рядом со мной?"
    ctx = inp.page_context.strip()[:MAX_CONTEXT_CHARS]
    user_block = (
        geo_prompt + "\n\n"
        + (f"Текст открытой страницы:\n{ctx}\n\n" if ctx else "")
        + f"Вопрос читателя: {q}"
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
    except ProviderError as e:
        answer, provider = (
            "Извините, сейчас не получилось ответить. Попробуйте ещё раз чуть позже.",
            f"error:{e}",
        )
    place = {}
    try:
        place = reverse_place(inp.lat, inp.lon) or {}   # для «вы рядом с …», кэшируется
    except Exception:
        place = {}
    return GeoOut(answer=answer, provider=provider, place=place, nearby=nearby)


class LessonIn(BaseModel):
    grade: str = ""       # класс (1–11)
    subject: str = ""     # предмет
    textbook: str = ""    # учебник/автор (опц.)
    topic: str = ""       # тема (опц.)
    location: str = ""    # город/локация (опц.)
    season: str = ""      # сезон (опц.)
    when: str = ""        # когда урок: «сейчас», «завтра утром» … (опц.)


class LessonOut(BaseModel):
    lesson: str
    provider: str
    sources: list[str] = Field(default_factory=list)   # заголовки источников опоры (для показа)


SITE_URL = os.environ.get("SITE_URL", "https://tropa.fmin.xyz")
# Иллюстрация в методичке (Викисклад, свободные лицензии). Флаг — на случай отключения.
IMAGES_ENABLED = os.environ.get("IMAGES_ENABLED", "1").strip() not in ("", "0", "false", "False")
# Если настоящего фото не нашлось — рисуем иллюстрацию сами (в подписи это помечается).
IMAGES_GENERATE = os.environ.get("IMAGES_GENERATE", "1").strip() not in ("", "0", "false", "False")


def _lesson_context(inp: "LessonIn"):
    """Блок опоры + источники. Возвращает (ctx, titles, refs), где refs — [{title,url}]
    для блока «Источники» в PDF. Любая ошибка → пустые значения: урок не ломается."""
    if not (RETRIEVAL_ENABLED and _RETRIEVERS and RetrievalQuery):
        return "", [], []
    try:
        from retrieval import collect_snippets
        q = RetrievalQuery(grade=inp.grade, subject=inp.subject, topic=inp.topic,
                           location=inp.location, season=inp.season, text=inp.textbook)
        snippets = collect_snippets(q, retrievers=_RETRIEVERS)
        ctx = gather_context(q, retrievers=_RETRIEVERS, snippets=snippets)
        titles, refs, seen = [], [], set()
        for s in snippets:
            title = (getattr(s, "title", "") or "").strip()
            url = (getattr(s, "url", "") or "").strip()
            if url.startswith("/"):            # сюжеты хранят относительный путь
                url = SITE_URL.rstrip("/") + url
            key = (title, url)
            if not title or key in seen:
                continue
            seen.add(key)
            titles.append(title)
            refs.append({"title": title, "url": url})
        return ctx, titles[:6], refs[:8]
    except Exception:
        return "", [], []


@app.post("/api/lesson", response_model=LessonOut)
def lesson(inp: LessonIn):
    body = _form_body(inp)
    if not body:
        return LessonOut(lesson="Заполните хотя бы класс и предмет.", provider="none")

    ctx, sources, _refs = _lesson_context(inp)
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


def _weather_line(inp: "LessonIn") -> str:
    """Погода на час урока по названию города. Нет города/сбой → "" (урок не страдает)."""
    if not (inp.location or "").strip():
        return ""
    try:
        from weather import weather_for
        return weather_for(inp.location, inp.when)
    except Exception:
        return ""


def _form_body(inp: "LessonIn") -> str:
    fields = [
        ("Класс", inp.grade), ("Предмет", inp.subject),
        ("Учебник/автор", inp.textbook), ("Тема", inp.topic),
        ("Локация", inp.location), ("Сезон", inp.season),
        ("Когда урок", inp.when), ("Погода", _weather_line(inp)),
    ]
    return "\n".join(f"{k}: {v.strip()}" for k, v in fields if v and v.strip())


@app.post("/api/lesson/pdf")
def lesson_pdf(inp: LessonIn):
    """Развёрнутая методичка (GigaChat + опора из RAG) → рендер в PDF (Typst)."""
    body = _form_body(inp)
    if not body:
        return Response("Заполните хотя бы класс и предмет.", status_code=400,
                        media_type="text/plain; charset=utf-8")
    ctx, _titles, refs = _lesson_context(inp)
    try:                                   # возрастная градация подачи
        from grade_levels import profile_for
        age_block = profile_for(inp.grade)
    except Exception:
        age_block = ""
    user_content = (
        (f"{ctx}\n\n" if ctx else "")
        + (f"{age_block}\n\n" if age_block else "")
        + "Данные формы учителя:\n" + body
    )
    messages = [
        {"role": "system", "content": METHODICHKA_PROMPT},
        {"role": "user", "content": user_content},
    ]
    # Иллюстрацию качаем ПАРАЛЛЕЛЬНО с генерацией текста — она не должна добавлять секунд.
    img_future = None
    if IMAGES_ENABLED:
        try:
            from concurrent.futures import ThreadPoolExecutor
            from images import illustration_for, generate_illustration

            def _find_or_draw(topic, subject):
                """Сначала ищем настоящее фото; не нашли — рисуем сами (с пометкой в подписи)."""
                got = illustration_for(topic, subject)
                if got:
                    return got
                if IMAGES_GENERATE:
                    return generate_illustration(topic, subject)
                return {}

            _img_pool = ThreadPoolExecutor(max_workers=1)
            img_future = _img_pool.submit(_find_or_draw, inp.topic or inp.subject, inp.subject)
            _img_pool.shutdown(wait=False)
        except Exception:
            img_future = None

    try:
        md, _ = generate(
            messages, _PROVIDERS,
            max_tokens=int(os.environ.get("METHODICHKA_MAX_TOKENS", "4000")),
            temperature=float(os.environ.get("METHODICHKA_TEMPERATURE", "0.5")),
        )
    except ProviderError:
        return Response("Сейчас не удалось собрать методичку. Попробуйте позже.",
                        status_code=503, media_type="text/plain; charset=utf-8")

    img = {}
    if img_future is not None:
        try:
            img = img_future.result(timeout=float(os.environ.get("IMAGE_TIMEOUT", "60"))) or {}
        except Exception:
            img = {}
    if img.get("page") or img.get("origin") == "generated":   # автор и лицензия — в «Источники»
        credit = f"Фото: {img.get('title', '')}".strip()
        if img.get("author"):
            credit += f" — {img['author']}"
        if img.get("license"):
            credit += f" ({img['license']})"
        refs = list(refs) + [{"title": credit, "url": img["page"]}]

    try:
        from lesson_pdf import render_lesson_pdf
        pdf = render_lesson_pdf(md, sources=refs, image=img)
    except Exception:
        return Response("Не удалось сформировать PDF.", status_code=500,
                        media_type="text/plain; charset=utf-8")
    finally:
        p = img.get("path")
        if p and os.path.exists(p):
            try:
                os.unlink(p)              # временный файл картинки за собой убираем
            except Exception:
                pass
    return Response(
        content=pdf, media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="urok-tropa.pdf"'},
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
