"""Retrieval-слой урока: параллельный сбор опоры из включённых ретриверов.

gather_context() — единственная точка, которую дёргает app.py. Инвариант: НИКОГДА
не бросает наружу и при любой беде возвращает "" (урок не ломается).
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from retrieval.base import RetrievalQuery, Snippet


def _flag(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip() not in ("", "0", "false", "False")


def build_retrievers() -> List:
    """Собирает включённые по флагам ретриверы. Ошибка конструктора одного —
    не мешает остальным (retrieval не должен падать целиком)."""
    retrievers = []
    if _flag("RETRIEVER_STORYLINES", "1"):
        try:
            from retrieval.storyline_retriever import StorylineRetriever
            retrievers.append(StorylineRetriever())
        except Exception:
            pass
    if _flag("RETRIEVER_PROGRAM", "1"):
        try:
            from retrieval.program_retriever import ProgramRetriever
            retrievers.append(ProgramRetriever())
        except Exception:
            pass
    if _flag("RETRIEVER_WEB", "0"):
        try:
            from retrieval.web_retriever import WebRetriever
            wr = WebRetriever()
            if wr.api_key:            # без ключа не добавляем — пустой ретривер не нужен
                retrievers.append(wr)
        except Exception:
            pass
    return retrievers


# Читаемые метки источника для блока опоры.
_LABEL = {"сюжет": "сюжет", "программа": "программа", "веб": "веб"}


def gather_context(
    q: RetrievalQuery,
    retrievers: List = None,
    per_retriever_timeout: float = None,
    char_budget: int = 2500,
    per_retriever_limit: int = 3,
) -> str:
    """Параллельно опрашивает ретриверы, мёржит и форматирует блок «Материалы для опоры».
    Пусто/ошибка → "" (урок генерируется без опоры)."""
    try:
        if retrievers is None:
            retrievers = build_retrievers()
        if not retrievers:
            return ""
        if per_retriever_timeout is None:
            per_retriever_timeout = float(os.environ.get("RETRIEVAL_TIMEOUT", "6"))

        snippets: List[Snippet] = []
        with ThreadPoolExecutor(max_workers=max(1, len(retrievers))) as ex:
            futures = {ex.submit(r.retrieve, q, per_retriever_limit): r for r in retrievers}
            for fut in as_completed(futures, timeout=per_retriever_timeout * len(retrievers) + 1):
                try:
                    res = fut.result(timeout=per_retriever_timeout)
                    if res:
                        snippets.extend(res)
                except Exception:
                    continue          # упавший/зависший ретривер просто не даёт вклада

        if not snippets:
            return ""

        snippets.sort(key=lambda s: s.score, reverse=True)

        lines = ["Материалы для опоры (используй по делу; факты из [веб] приводи с источником):"]
        used = len(lines[0])
        for s in snippets:
            src = _LABEL.get(s.source, s.source)
            tail = f" (источник: {s.url})" if s.source == "веб" and s.url else ""
            line = f"[{src}] {s.title} — {s.text}{tail}".strip()
            if used + len(line) + 1 > char_budget:
                continue
            lines.append(line)
            used += len(line) + 1
        return "\n".join(lines) if len(lines) > 1 else ""
    except Exception:
        return ""
