"""Единые контракты retrieval-слоя. От них зависят все ретриверы и gather_context."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol, runtime_checkable


@dataclass
class RetrievalQuery:
    """Запрос на поиск контекста — данные формы учителя."""
    grade: str = ""
    subject: str = ""
    topic: str = ""
    location: str = ""
    season: str = ""
    text: str = ""       # доп. свободный текст

    @property
    def joined(self) -> str:
        """Склейка значимых полей для текстового/семантического матча."""
        parts = [self.topic, self.subject, self.text, self.location, self.season]
        return " ".join(p.strip() for p in parts if p and p.strip()).strip()


@dataclass
class Snippet:
    """Один найденный фрагмент опоры."""
    source: str          # "сюжет" | "программа" | "веб"
    title: str
    text: str
    url: str = ""
    score: float = 0.0   # 0..1


@runtime_checkable
class Retriever(Protocol):
    name: str
    def retrieve(self, q: RetrievalQuery, limit: int = 3) -> List[Snippet]: ...
