"""Иллюстрация к уроку — Викисклад (Wikimedia Commons).

Почему именно он: свободные лицензии (CC/PD), открытый API без ключа, есть автор и
ссылка на страницу файла — иллюстрацию можно законно вложить в методичку и корректно
атрибутировать. Случайные картинки из поиска для образовательного документа не годятся.

Любая ошибка → None: документ соберётся без фото.
"""
from __future__ import annotations

import os
import re
import tempfile

import requests

_API = "https://commons.wikimedia.org/w/api.php"
_UA = {"User-Agent": "TropaLessonBot/1.0 (+https://tropa.fmin.xyz)"}
_MAX_BYTES = 4 * 1024 * 1024          # не тащим гигантские файлы в PDF

# Вопросительные и служебные слова — из запроса к поиску картинок выкидываем.
_STOP = {"почему", "как", "что", "такое", "зачем", "какой", "какие", "какая", "где",
         "когда", "для", "детей", "чем", "это", "при", "или", "если", "чтобы"}

# Архивное и печатное: обложки журналов, гравюры, титульные листы. Для урока нужна
# современная иллюстрация явления, а не памятник книгопечатания.
_ARCHIVAL = ("журнал", "обложка", "титульный", "гравюр", "литограф", "марка",
             "почтов", "плакат", "афиша", "карикатур", "рукопис", "газет",
             "ведомости", "вестник", "листок", "страница", "разворот",
             "magazine", "cover", "engraving", "lithograph", "stamp", "poster",
             "manuscript", "title page", "book", "newspaper", "scan", "page from")

# Иллюстрация должна быть современной: архивные сканы XIX — начала XX века уроку не подходят.
_MIN_YEAR = 1980


def _year_of(meta: dict) -> int:
    """Год съёмки/создания из метаданных Викисклада; 0 — если не разобрали."""
    import re
    for key in ("DateTimeOriginal", "DateTime"):
        v = _strip_html((meta.get(key) or {}).get("value") or "")
        m = re.search(r"(1[6-9]\d{2}|20\d{2})", v)
        if m:
            return int(m.group(1))
    return 0


def _looks_like_scan_id(title: str) -> bool:
    """«Pn-2008-11-05-n45» и подобные коды — это сканы, а не иллюстрации явления."""
    import re
    letters = len(re.findall(r"[A-Za-zА-Яа-я]", title))
    digits = len(re.findall(r"\d", title))
    return digits >= 6 and letters <= 4


# Порог семантической близости темы и названия файла. Подобран по замерам:
# релевантные названия дают 0.81–0.92, нерелевантные — 0.73–0.75.
_MIN_SIM = float(os.environ.get("IMAGE_MIN_SIM", "0.79"))

_emb_client = None


def _embeddings():
    """Ленивый клиент эмбеддингов. Нет ключа/ошибка → None (упадём на стем-фолбэк)."""
    global _emb_client
    if _emb_client is None:
        try:
            from retrieval.embeddings import EmbeddingsClient
            key = os.environ.get("GIGACHAT_AUTH_KEY")
            _emb_client = EmbeddingsClient(
                auth_key=key,
                scope=os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_CORP"),
            ) if key else False
        except Exception:
            _emb_client = False
    return _emb_client or None


def _semantic_pick(query: str, candidates: list):
    """Лучший по смыслу кандидат: одним запросом эмбеддим тему и все названия,
    берём максимум косинуса выше порога. Эмбеддинги многоязычны, поэтому английские
    названия Викисклада сравниваются с русской темой напрямую.
    → (кандидат, score) или (None, 0.0), если эмбеддинги недоступны или всё ниже порога."""
    client = _embeddings()
    if not client or not candidates:
        return None, 0.0
    try:
        from retrieval.embeddings import cosine
        titles = [c["title"] for c in candidates]
        vecs = client.embed([query] + titles)
        qv, tvs = vecs[0], vecs[1:]
        scored = sorted(
            ((cosine(qv, tv), c) for tv, c in zip(tvs, candidates)),
            key=lambda x: x[0], reverse=True,
        )
        best_score, best = scored[0]
        return (best, best_score) if best_score >= _MIN_SIM else (None, best_score)
    except Exception:
        return None, 0.0


def _llm_pick(topic: str, subject: str, candidates: list):
    """Выбор иллюстрации самой моделью — точнее косинуса.

    Эмбеддинги считают «образование озёр» и «Образование облаков» близкими: формально
    это так, но уроку нужна именно тема. Модель различает это без труда и умеет честно
    ответить «ни одна не подходит».
    → (кандидат, 'llm') или (None, None), если модель недоступна или отказалась выбирать."""
    if not candidates:
        return None, None
    try:
        from providers import build_providers, generate
        listing = "\n".join(f"{i}. {c['title'][:90]}" for i, c in enumerate(candidates[:15], 1))
        msg = (
            f"Тема школьного урока: «{topic}»" + (f" (предмет: {subject})" if subject else "") + ".\n"
            f"Ниже названия фотографий. Выбери номер ОДНОЙ, которая лучше всего иллюстрирует "
            f"именно эту тему. Если ни одна не подходит по смыслу — ответь 0. "
            f"Важно: близкая, но другая тема — это НЕ подходит.\n\n{listing}\n\n"
            f"Ответь только числом."
        )
        out, _ = generate(
            [{"role": "system", "content": "Ты помогаешь подобрать иллюстрацию к уроку. Отвечай одним числом."},
             {"role": "user", "content": msg}],
            build_providers(), max_tokens=6, temperature=0.0,
        )
        m = re.search(r"\d+", out or "")
        if not m:
            return None, None
        idx = int(m.group(0))
        if idx <= 0 or idx > len(candidates[:15]):
            return None, "llm"         # модель сказала «ничего не подходит»
        return candidates[idx - 1], "llm"
    except Exception:
        return None, None


def _similarity(a: str, b: str) -> float:
    """Косинус между двумя строками. 0.0 — если эмбеддинги недоступны (тогда не судим)."""
    client = _embeddings()
    if not client:
        return 0.0
    try:
        from retrieval.embeddings import cosine
        v = client.embed([a, b])
        return cosine(v[0], v[1])
    except Exception:
        return 0.0


def _stems(s: str) -> set:
    """Грубый стем (первые 4 буквы значимых слов) — снимает русскую морфологию."""
    import re
    return {w[:4] for w in re.findall(r"\w+", (s or "").lower())
            if len(w) > 3 and w not in _STOP}


def _clean_query(q: str) -> str:
    import re
    return " ".join(t for t in re.findall(r"\w+", (q or "").lower()) if t not in _STOP)


def find_image(query: str, timeout: float = 8.0, strict: bool = True) -> dict:
    """Ищет свободное фото по теме, отбрасывая нерелевантное и архивное.

    strict=True — заголовок файла обязан пересекаться с темой по смыслу (надёжно, но
    режет англоязычные названия, которых на Викискладе большинство).
    strict=False — принимаем верхний результат выдачи; допустимо только для коротких
    запросов в 1–2 слова, где ранжирование Викисклада само по себе точное.
    → {'url','title','author','license','page'} или {}."""
    q = _clean_query(query)
    if not q:
        return {}
    want = _stems(query)
    try:
        r = requests.get(_API, params={
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": 12,
            "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 900,
        }, headers=_UA, timeout=timeout)
        r.raise_for_status()
        pages = ((r.json() or {}).get("query") or {}).get("pages") or {}
    except Exception:
        return {}

    candidates = _filter_candidates(pages)
    if not candidates:
        return {}

    # 2) смысловой отбор эмбеддингами — работает одинаково для русских и английских названий
    best, score = _semantic_pick(query, candidates)
    if best:
        best["similarity"] = round(score, 3)
        return best
    if score:                          # эмбеддинги отработали, но всё ниже порога
        return {}                      # лучше без картинки, чем не по теме

    # 3) запасной путь, если эмбеддинги недоступны: грубый стем-матч
    for c in candidates:
        has_cyrillic = bool(re.search(r"[А-Яа-яЁё]", c["title"]))
        if want and (strict or has_cyrillic) and not (want & _stems(c["title"])):
            continue
        return c
    return {}


def _filter_candidates(pages: dict) -> list:
    """Жёсткие правила: формат, архивность, год съёмки, имя-код скана. Без семантики."""
    def _m(meta, key):
        return _strip_html((meta.get(key) or {}).get("value") or "")

    candidates = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 99)):
        info = (p.get("imageinfo") or [{}])[0]
        url = info.get("thumburl") or info.get("url") or ""
        if not url.lower().rsplit(".", 1)[-1].startswith(("jpg", "jpeg", "png")):
            continue                   # svg/gif/tiff в Typst не кладём
        title = (p.get("title") or "").replace("File:", "").rsplit(".", 1)[0]
        low = title.lower()
        if any(w in low for w in _ARCHIVAL) or _looks_like_scan_id(title):
            continue                   # обложка журнала 1909 года уроку не иллюстрация
        meta = info.get("extmetadata") or {}
        year = _year_of(meta)
        if year and year < _MIN_YEAR:
            continue                   # только современные материалы
        candidates.append({
            "url": url, "title": title,
            "author": _m(meta, "Artist")[:80],
            "license": _m(meta, "LicenseShortName")[:40],
            "page": info.get("descriptionurl") or "",
        })
    return candidates


def _search_candidates(query: str, timeout: float = 8.0) -> list:
    """Поиск по Викискладу + жёсткие правила. Семантика применяется выше, к общему пулу."""
    q = _clean_query(query)
    if not q:
        return []
    try:
        r = requests.get(_API, params={
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": 12,
            "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 900,
        }, headers=_UA, timeout=timeout)
        r.raise_for_status()
        pages = ((r.json() or {}).get("query") or {}).get("pages") or {}
    except Exception:
        return []
    return _filter_candidates(pages)


def _strip_html(s: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", s or "").strip()


def download(url: str, timeout: float = 10.0) -> str:
    """Качает картинку во временный файл. → путь или "" (вызывающий сам удаляет)."""
    if not url:
        return ""
    try:
        r = requests.get(url, headers=_UA, timeout=timeout, stream=True)
        r.raise_for_status()
        ext = ".png" if url.lower().split("?")[0].endswith(".png") else ".jpg"
        fd, path = tempfile.mkstemp(suffix=ext)
        size = 0
        with os.fdopen(fd, "wb") as f:
            for chunk in r.iter_content(64 * 1024):
                size += len(chunk)
                if size > _MAX_BYTES:
                    break
                f.write(chunk)
        return path if size else ""
    except Exception:
        return ""


def _query_variants(topic: str, subject: str) -> list:
    """От точной темы к отдельным ключевым словам.

    Длинная фраза-вопрос на Викискладе ищется плохо, а какое слово темы окажется
    удачным — заранее неизвестно: в «образовании озёр» работает «озёр», а «образование»
    уводит в школьное образование. Поэтому пробуем каждое значимое слово; за качество
    отвечает семантический отбор, поэтому лишние варианты безопасны."""
    words = [w for w in re.findall(r"\w+", (topic or "").lower())
             if len(w) > 3 and w not in _STOP]
    variants = []
    if topic and topic.strip():
        variants.append(_clean_query(topic))
    if len(words) > 2:
        variants.append(" ".join(words[:2]))
    variants += words[:3]                          # каждое ключевое слово отдельно
    if words and subject:
        variants.append(f"{words[0]} {subject}")
    seen, out = set(), []
    for v in variants:
        v = (v or "").strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out[:5]                                 # хватит; идём параллельно с генерацией


def illustration_for(topic: str, subject: str = "") -> dict:
    """Готовая иллюстрация к теме: качает файл и отдаёт метаданные для подписи.

    Кандидатов собираем по всем вариантам запроса, но ранжируем ОДИН раз и строго
    против исходной темы. Иначе вариант «образование» притягивает «Образование облаков»,
    а «меняет» — «Анжа меняет русло»: совпадение с вариантом ещё не значит совпадение с темой.

    Нет релевантного — возвращает {}: лучше без картинки, чем не по теме.
    → {'path','title','author','license','page','similarity'} или {}."""
    seen, pool = set(), []
    for q in _query_variants(topic, subject):
        for c in _search_candidates(q):
            if c["url"] in seen:
                continue
            seen.add(c["url"])
            pool.append(c)
        if len(pool) >= 20:
            break
    if not pool:
        return {}

    # Два независимых судьи: модель выбирает, эмбеддинги подтверждают. Согласия требуем,
    # потому что поиск по слову-глаголу («меняет») тащит в пул мусор вроде «Виталик меняет
    # лампочку», и модель иногда берёт наименее плохое вместо честного отказа.
    goal = f"{topic} {subject}".strip() or topic
    best, how = _llm_pick(topic, subject, pool)
    score = 0.0
    if how == "llm" and not best:
        return {}                      # модель честно сказала «ничего не подходит»
    if best:
        score = _similarity(goal, best["title"])
        if score and score < _MIN_SIM:
            return {}                  # выбор модели не подтвердился по смыслу
    else:
        best, score = _semantic_pick(goal, pool)
        if not best:
            if score:
                return {}              # эмбеддинги отработали, но всё ниже порога
            best = pool[0]             # ничего не доступно — верхний из выдачи
    path = download(best["url"])
    if not path:
        return {}
    best["path"] = path
    best["similarity"] = round(score, 3)
    return best
