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
        # Релевантность. Строгий режим — обязательное смысловое пересечение с темой.
        # Мягкий (короткий запрос): русскоязычное название всё равно обязано совпасть —
        # иначе «образование» ловит школьное образование вместо образования озёр.
        # Англоязычному названию доверяем: стем-матч по-русски для него невозможен,
        # а ранжирование Викисклада на коротком запросе точное.
        has_cyrillic = bool(re.search(r"[А-Яа-яЁё]", title))
        if want and (strict or has_cyrillic) and not (want & _stems(title)):
            continue

        def _m(key):
            v = (meta.get(key) or {}).get("value") or ""
            return _strip_html(v)

        return {
            "url": url,
            "title": title,
            "author": _m("Artist")[:80],
            "license": _m("LicenseShortName")[:40],
            "page": info.get("descriptionurl") or "",
        }
    return {}


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
    """От точной темы к ключевым словам: длинная фраза-вопрос на Викискладе ищется плохо,
    а по одному предмету находится случайный плакат — поэтому вариантов несколько,
    и голого предмета среди них нет."""
    import re
    words = [w for w in re.findall(r"\w+", (topic or "").lower())
             if len(w) > 3 and w not in _STOP]
    variants = []
    if topic and topic.strip():
        variants.append(_clean_query(topic))
    if len(words) > 2:
        variants.append(" ".join(words[:2]))       # два ключевых слова
    if words:
        variants.append(words[0])                  # главное слово темы
        if subject:
            variants.append(f"{words[0]} {subject}")
    seen, out = set(), []
    for v in variants:
        v = (v or "").strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def illustration_for(topic: str, subject: str = "") -> dict:
    """Готовая иллюстрация к теме: качает файл и отдаёт метаданные для подписи.
    Нет релевантного — возвращает {}: лучше без картинки, чем не по теме.
    → {'path','title','author','license','page'} или {}."""
    for q in _query_variants(topic, subject):
        # мягкий режим — только для запроса ровно из двух слов: он уже конкретен.
        # Одиночное слово («образование») двусмысленно, длинная фраза ищется плохо.
        found = find_image(q, strict=(len(q.split()) != 2))
        if not found:
            continue
        path = download(found["url"])
        if path:
            found["path"] = path
            return found
    return {}
