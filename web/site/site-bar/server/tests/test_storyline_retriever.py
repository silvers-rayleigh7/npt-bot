"""Task: StorylineRetriever — keyword-фолбэк без сети (auth_key=None)."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.base import RetrievalQuery          # noqa: E402
from retrieval.storyline_retriever import StorylineRetriever  # noqa: E402


def _tmp_index():
    """Мини-индекс из 2 фейковых записей → временный json, возвращает путь."""
    items = [
        {"slug": "reka", "title": "Тайна реки", "topic": "гидрология",
         "tags": ["география"], "summary": "Как течёт вода.",
         "url": "/storylines/reka/", "embedding": [0.0] * 4},
        {"slug": "les", "title": "Загадка леса", "topic": "экология",
         "tags": ["биология"], "summary": "Почему шумит лес.",
         "url": "/storylines/les/", "embedding": [0.0] * 4},
    ]
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)
    return path


def test_keyword_hit():
    path = _tmp_index()
    try:
        r = StorylineRetriever(index_path=path, auth_key=None)  # форсим фолбэк
        # "тайна" — слово из title первой записи → она должна быть первой
        res = r.retrieve(RetrievalQuery(topic="тайна"))
        assert res and res[0].title == "Тайна реки"
        assert res[0].source == "сюжет" and res[0].score > 0
    finally:
        os.remove(path)


def test_no_match():
    path = _tmp_index()
    try:
        r = StorylineRetriever(index_path=path, auth_key=None)
        assert r.retrieve(RetrievalQuery(topic="космос")) == []
    finally:
        os.remove(path)


def test_empty_index():
    # несуществующий путь → пустой индекс → []
    r = StorylineRetriever(index_path="/nope/missing.json", auth_key=None)
    assert r.retrieve(RetrievalQuery(topic="тайна")) == []


if __name__ == "__main__":
    test_keyword_hit(); test_no_match(); test_empty_index()
    print("OK test_storyline_retriever")
