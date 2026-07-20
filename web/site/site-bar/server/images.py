"""Иллюстрация к уроку — Викисклад (Wikimedia Commons).

Почему именно он: свободные лицензии (CC/PD), открытый API без ключа, есть автор и
ссылка на страницу файла — иллюстрацию можно законно вложить в методичку и корректно
атрибутировать. Случайные картинки из поиска для образовательного документа не годятся.

Любая ошибка → None: документ соберётся без фото.
"""
from __future__ import annotations

import os
import tempfile

import requests

_API = "https://commons.wikimedia.org/w/api.php"
_UA = {"User-Agent": "TropaLessonBot/1.0 (+https://tropa.fmin.xyz)"}
_MAX_BYTES = 4 * 1024 * 1024          # не тащим гигантские файлы в PDF


def find_image(query: str, timeout: float = 8.0) -> dict:
    """Ищет свободное фото по теме. → {'url','title','author','license','page'} или {}."""
    q = (query or "").strip()
    if not q:
        return {}
    try:
        r = requests.get(_API, params={
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": 6,
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
        meta = info.get("extmetadata") or {}

        def _m(key):
            v = (meta.get(key) or {}).get("value") or ""
            return _strip_html(v)

        return {
            "url": url,
            "title": (p.get("title") or "").replace("File:", "").rsplit(".", 1)[0],
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


def illustration_for(topic: str, subject: str = "") -> dict:
    """Готовая иллюстрация к теме: качает файл и отдаёт метаданные для подписи.
    → {'path','title','author','license','page'} или {}."""
    for q in [t for t in (topic, f"{topic} {subject}".strip(), subject) if t and t.strip()]:
        found = find_image(q)
        if not found:
            continue
        path = download(found["url"])
        if path:
            found["path"] = path
            return found
    return {}
