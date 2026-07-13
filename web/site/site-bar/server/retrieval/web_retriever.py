"""Веб-ретривер: 1-2 проверенных научпоп-факта по теме урока с источником.

Работает строго за флагом: без API-ключа полностью выключен (retrieve → []),
чтобы отсутствие веб-поиска НИКОГДА не роняло генерацию урока.
Наружу исключения не бросает — любая ошибка сети/парсинга гасится в [].
"""
from __future__ import annotations

import os
from typing import List, Optional

import requests

from .base import RetrievalQuery, Snippet


class WebRetriever:
    name = "веб"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        # ключ из аргумента или из env; без него ретривер выключен
        self.api_key = api_key if api_key is not None else os.environ.get("WEB_SEARCH_API_KEY")
        self.timeout = timeout

    def _search(self, query: str) -> List[dict]:
        """Tavily-совместимый REST-поиск. Отдельный метод — чтобы мокать в тесте.

        При любой ошибке пробрасывает исключение (его ловит retrieve).
        """
        r = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": self.api_key,
                "query": query,
                "max_results": 2,
                "search_depth": "basic",
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json().get("results", [])

    def retrieve(self, q: RetrievalQuery, limit: int = 2) -> List[Snippet]:
        if not self.api_key:
            return []  # выключен без ключа
        # склейка непустых полей без лишних пробелов
        parts = [p for p in (q.topic, q.subject) if p and p.strip()]
        if not parts:
            return []
        query = f"{' '.join(parts)} для детей научно-популярно"
        try:
            results = self._search(query)[:limit]
            return [
                Snippet(
                    source="веб",
                    title=res.get("title", ""),
                    text=(res.get("content", "") or "")[:220],
                    url=res.get("url", ""),
                    score=0.5,
                )
                for res in results
            ]
        except Exception:
            return []
