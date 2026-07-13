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

import requests

from .base import RetrievalQuery, Snippet

_UA = {"User-Agent": "TropaLessonBot/1.0 (+https://tropa.fmin.xyz)"}
# Вопросительные и служебные слова — выкидываем из запроса к Википедии.
_STOP = {"почему", "как", "что", "такое", "зачем", "какой", "какие", "какая", "где", "когда",
         "для", "детей", "чем", "это", "при", "или", "если", "чтобы"}


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
                 use_wikipedia: Optional[bool] = None):
        self.api_key = api_key if api_key is not None else os.environ.get("WEB_SEARCH_API_KEY")
        self.use_wikipedia = _flag("WEB_WIKIPEDIA", "1") if use_wikipedia is None else use_wikipedia
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key) or self.use_wikipedia

    # ── провайдеры поиска (каждый может бросить — ловит retrieve) ──
    def _search_tavily(self, topic: str, subject: str) -> List[dict]:
        query = " ".join(p for p in (topic, subject) if p).strip() + " для детей научно-популярно"
        r = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": self.api_key, "query": query, "max_results": 2, "search_depth": "basic"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return [
            {"title": x.get("title", ""), "content": (x.get("content", "") or ""), "url": x.get("url", "")}
            for x in r.json().get("results", [])
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
