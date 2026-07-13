"""Ретривер по сюжетам научной тропы.

Основной путь — семантический поиск через эмбеддинги GigaChat по заранее
собранному индексу (data/storylines_index.json). Если ключа нет или эмбеддинги
недоступны — падаем на keyword-фолбэк по словам title/topic/tags.
Наружу исключения не бросает: при любой ошибке возвращает [] или фолбэк.
"""
from __future__ import annotations

import json
import os
from typing import List, Optional

from .base import RetrievalQuery, Snippet
from .embeddings import EmbeddingsClient, EmbeddingsError, cosine

# порог семантической близости и предельный score фолбэка
_MIN_COS = 0.35
_FALLBACK_CAP = 0.34


def _default_index_path() -> str:
    """Путь к индексу: env STORYLINES_INDEX или data/storylines_index.json рядом с модулем."""
    env = os.environ.get("STORYLINES_INDEX")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "data", "storylines_index.json")


def _words(text: str) -> set:
    """Слова длиннее 3 символов в нижнем регистре — для keyword-матча."""
    return {w for w in text.lower().split() if len(w) > 3}


class StorylineRetriever:
    name = "storylines"

    def __init__(
        self,
        index_path: Optional[str] = None,
        auth_key: Optional[str] = None,
        scope: str = "GIGACHAT_API_CORP",
    ):
        self.index_path = index_path or _default_index_path()
        self.auth_key = auth_key if auth_key is not None else os.environ.get("GIGACHAT_AUTH_KEY")
        self.scope = scope
        self.items = self._load_index()
        self._client: Optional[EmbeddingsClient] = None  # ленивый клиент эмбеддингов

    def _load_index(self) -> List[dict]:
        """Загружает индекс в память. Нет файла / битый JSON → пустой список."""
        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _ensure_client(self) -> EmbeddingsClient:
        if self._client is None:
            self._client = EmbeddingsClient(self.auth_key, scope=self.scope)
        return self._client

    def _snippet(self, item: dict, score: float) -> Snippet:
        return Snippet(
            source="сюжет",
            title=item.get("title", ""),
            text=str(item.get("summary", ""))[:220],
            url=item.get("url", ""),
            score=round(score, 3),
        )

    def retrieve(self, q: RetrievalQuery, limit: int = 3) -> List[Snippet]:
        if not self.items:
            return []
        # основной путь — семантика; при отсутствии ключа или ошибке → фолбэк
        if self.auth_key:
            try:
                return self._semantic(q, limit)
            except EmbeddingsError:
                return self._keyword(q, limit)
            except Exception:
                return self._keyword(q, limit)
        return self._keyword(q, limit)

    def _semantic(self, q: RetrievalQuery, limit: int) -> List[Snippet]:
        vec = self._ensure_client().embed([q.joined])[0]
        scored = []
        for item in self.items:
            emb = item.get("embedding") or []
            cos = cosine(vec, emb)
            if cos >= _MIN_COS:
                scored.append((cos, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [self._snippet(item, cos) for cos, item in scored[:limit]]

    def _keyword(self, q: RetrievalQuery, limit: int) -> List[Snippet]:
        qwords = _words(q.joined)
        if not qwords:
            return []
        scored = []
        for item in self.items:
            bag = _words(
                " ".join([
                    item.get("title", ""),
                    item.get("topic", ""),
                    " ".join(item.get("tags", []) or []),
                ])
            )
            hits = len(qwords & bag)
            if hits:
                scored.append((min(_FALLBACK_CAP, 0.08 * hits), item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [self._snippet(item, score) for score, item in scored[:limit]]
