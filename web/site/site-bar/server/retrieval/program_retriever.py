"""Ретривер по курируемому индексу школьной программы (ФГОС/примерные РП).

Ищет разделы программы под пару (класс, предмет) и ранжирует их
по совпадению слов запроса с темами и ключевыми словами.
"""
from __future__ import annotations

import json
import os
import re
from typing import List

from retrieval.base import RetrievalQuery, Snippet

# Каталог модуля — от него считаем путь к data/ по умолчанию.
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_INDEX = os.path.join(os.path.dirname(_HERE), "data", "programs_index.json")


def _norm_grade(g: str) -> str:
    """Нормализация класса: '6 класс' -> '6', обрезка пробелов."""
    if not g:
        return ""
    m = re.search(r"\d+", str(g))
    return m.group(0) if m else str(g).strip().lower()


def _words(text: str) -> set:
    """Значимые слова (>3 символов, lowercase) для матча."""
    if not text:
        return set()
    toks = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    return {t for t in toks if len(t) > 3}


class ProgramRetriever:
    """Retriever по индексу школьной программы. name='программа'."""

    name = "программа"

    def __init__(self, index_path: str = None):
        # Приоритет: явный путь -> env PROGRAMS_INDEX -> data/programs_index.json.
        path = index_path or os.environ.get("PROGRAMS_INDEX") or _DEFAULT_INDEX
        self.index_path = path
        self._records = self._load(path)

    @staticmethod
    def _load(path: str) -> List[dict]:
        """Загрузка индекса; нет файла или ошибка -> пустой список."""
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def retrieve(self, q: RetrievalQuery, limit: int = 3) -> List[Snippet]:
        try:
            # Без класса или предмета поиск по программе бессмысленен.
            if not q.grade or not q.subject:
                return []

            want_grade = _norm_grade(q.grade)
            want_subject = q.subject.strip().lower()

            # Слова запроса: приоритет topic, затем text и склейка.
            query_words = _words(q.topic) or _words(q.text) or _words(q.joined)
            topic_empty = not (q.topic and q.topic.strip())

            # Сначала собираем все записи пары класс+предмет с числом совпадений.
            matched = []
            for rec in self._records:
                if _norm_grade(rec.get("grade", "")) != want_grade:
                    continue
                if want_subject not in str(rec.get("subject", "")).lower():
                    continue
                themes = rec.get("themes", []) or []
                keywords = rec.get("keywords", []) or []
                bag = _words(" ".join(themes) + " " + " ".join(keywords))
                hits = 0 if topic_empty else len(query_words & bag)
                matched.append((rec, themes, hits))

            if not matched:
                return []

            # Если тема задана, но НИ ОДНА запись не совпала лексически —
            # всё равно отдаём разделы класса+предмета (это релевантный контекст урока),
            # но с пониженным базовым score. Пусто здесь хуже, чем «вот разделы программы».
            any_hit = any(h > 0 for _, _, h in matched)
            denom = max(len(query_words), 1)

            scored = []
            for rec, themes, hits in matched:
                if topic_empty:
                    score = 0.4
                elif not any_hit:
                    score = 0.3                       # тема есть, но лексически не легла
                elif hits == 0:
                    continue                          # есть совпавшие получше — этот пропускаем
                else:
                    score = min(1.0, 0.4 + 0.6 * (hits / denom))
                text = (
                    f"{rec.get('grade', '')} класс, {rec.get('subject', '')}, "
                    f"раздел «{rec.get('section', '')}»: "
                    f"{', '.join(themes[:4])}. {rec.get('note', '')}"
                )
                scored.append(
                    Snippet(source=self.name, title=rec.get("section", ""),
                            text=text, url="", score=round(score, 3))
                )

            scored.sort(key=lambda s: s.score, reverse=True)
            return scored[: max(0, limit)]
        except Exception:
            return []
