"""Веб-ретривер: 1-2 проверенных факта по теме урока с источником.

Два источника (по приоритету):
  1. Tavily — если задан WEB_SEARCH_API_KEY (широкий веб).
  2. Русская Википедия — keyless, авторитетно для школы, есть цитируемый URL (по умолчанию вкл).

Наружу исключения не бросает — любая ошибка сети/парсинга гасится в []. Если оба источника
выключены (нет ключа и WEB_WIKIPEDIA=0) — retrieve() возвращает [], урок не страдает.
"""
from __future__ import annotations

import os
import re
from typing import List, Optional
from urllib.parse import urlparse

import requests

from .base import RetrievalQuery, Snippet

_UA = {"User-Agent": "TropaLessonBot/1.0 (+https://tropa.fmin.xyz)"}
# Вопросительные и служебные слова — выкидываем из запроса.
_STOP = {"почему", "как", "что", "такое", "зачем", "какой", "какие", "какая", "где", "когда",
         "для", "детей", "чем", "это", "при", "или", "если", "чтобы"}
# Белый список авторитетных научпоп/энциклопедических источников (правится через WEB_ALLOWED_DOMAINS).
_DEFAULT_ALLOWED = [
    "elementy.ru", "nkj.ru", "postnauka.ru", "nplus1.ru", "bigenc.ru",
    "naked-science.ru", "scientificrussia.ru", "arzamas.academy",
]


def _flag(name: str, default: str) -> bool:
    return os.environ.get(name, default).strip() not in ("", "0", "false", "False")


def _toks(s: str) -> List[str]:
    return [w for w in re.findall(r"\w+", s.lower()) if len(w) > 3 and w not in _STOP]


def _stems(s: str) -> set:
    """Грубый стем: первые 4 буквы значимых слов (снимает русскую морфологию)."""
    return {w[:4] for w in _toks(s)}


def _clean_query(q: str) -> str:
    return " ".join(t for t in re.findall(r"\w+", q.lower()) if t not in _STOP)


class WebRetriever:
    name = "веб"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0,
                 use_wikipedia: Optional[bool] = None, allowed_domains: Optional[List[str]] = None):
        self.api_key = api_key if api_key is not None else os.environ.get("WEB_SEARCH_API_KEY")
        # Википедия по умолчанию ВЫКЛючена (краудсорс — слабый источник для образования).
        self.use_wikipedia = _flag("WEB_WIKIPEDIA", "0") if use_wikipedia is None else use_wikipedia
        env_domains = os.environ.get("WEB_ALLOWED_DOMAINS", "")
        self.allowed_domains = allowed_domains if allowed_domains is not None else (
            [d.strip() for d in env_domains.split(",") if d.strip()] or list(_DEFAULT_ALLOWED)
        )
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key) or self.use_wikipedia

    def _host_allowed(self, url: str) -> bool:
        """Хост URL входит в allowlist (сам домен или его поддомен). Пустой allowlist → всё разрешено."""
        if not self.allowed_domains:
            return True
        try:
            host = urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
        except Exception:
            return False
        return any(host == d or host.endswith("." + d) for d in self.allowed_domains)

    # ── провайдеры поиска (каждый может бросить — ловит retrieve) ──
    def _search_tavily(self, topic: str, subject: str) -> List[dict]:
        query = " ".join(p for p in (topic, subject) if p).strip() + " для детей научно-популярно"
        payload = {"api_key": self.api_key, "query": query, "max_results": 8, "search_depth": "basic"}
        if self.allowed_domains:                       # просим Tavily ограничиться доверенными…
            payload["include_domains"] = self.allowed_domains
        r = requests.post("https://api.tavily.com/search", json=payload, timeout=self.timeout)
        r.raise_for_status()
        # …но include_domains у Tavily — мягкое пожелание: при отсутствии контента в доверенных
        # доменах он молча отдаёт общий веб (ловили kinogo.ec/wikipedia на «перемещении дюн»).
        # Поэтому ЖЁСТКО фильтруем по хосту на своей стороне — гарантия, а не надежда.
        return [
            {"title": x.get("title", ""), "content": (x.get("content", "") or ""), "url": x.get("url", "")}
            for x in r.json().get("results", [])
            if self._host_allowed(x.get("url", ""))
        ]

    def _search_wikipedia(self, topic: str, subject: str) -> List[dict]:
        base = topic or subject
        query = (_clean_query(topic) + " " + subject).strip() or base
        r = requests.get(
            "https://ru.wikipedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": query, "gsrlimit": 6, "prop": "extracts",
                "exintro": 1, "explaintext": 1, "exchars": 500, "redirects": 1,
            },
            headers=_UA, timeout=self.timeout,
        )
        r.raise_for_status()
        pages = ((r.json().get("query") or {}).get("pages") or {})
        want = _stems(base)               # релевантность считаем по теме (предмет слишком общий)
        scored = []
        for p in pages.values():
            extract = (p.get("extract", "") or "").strip()
            title = p.get("title", "")
            if not extract or not title:
                continue
            overlap = len(want & _stems(title + " " + extract)) if want else 0
            if want and overlap == 0:     # нерелевантное не берём — лучше ничего, чем «Лук-порей»
                continue
            scored.append((overlap, p.get("index", 99), {
                "title": title,
                "content": extract,
                "url": "https://ru.wikipedia.org/wiki/" + title.replace(" ", "_"),
            }))
        # больше совпадений выше; при равенстве — по позиции в выдаче
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [item for _, _, item in scored]

    def _search(self, topic: str, subject: str) -> List[dict]:
        """Диспетчер источника (отдельный метод — чтобы мокать в тесте)."""
        if self.api_key:
            return self._search_tavily(topic, subject)
        if self.use_wikipedia:
            return self._search_wikipedia(topic, subject)
        return []

    def retrieve(self, q: RetrievalQuery, limit: int = 2) -> List[Snippet]:
        if not self.enabled:
            return []
        topic = (q.topic or "").strip()
        subject = (q.subject or "").strip()
        if not topic and not subject:
            return []
        try:
            results = self._search(topic, subject)[:limit]
            return [
                Snippet(source="веб", title=r.get("title", ""),
                        text=(r.get("content", "") or "")[:240], url=r.get("url", ""), score=0.5)
                for r in results if r.get("content")
            ]
        except Exception:
            return []
