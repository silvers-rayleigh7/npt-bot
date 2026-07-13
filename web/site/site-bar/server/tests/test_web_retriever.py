"""Тесты веб-ретривера. Без реальной сети — метод _search мокается."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.base import RetrievalQuery       # noqa: E402
from retrieval.web_retriever import WebRetriever  # noqa: E402


def test_disabled_without_key():
    # без ключа ретривер выключен — всегда []
    r = WebRetriever(api_key=None)
    assert r.retrieve(RetrievalQuery(topic="опыление", subject="биология")) == []


def test_with_key_returns_snippet():
    r = WebRetriever(api_key="TESTKEY")
    # подменяем сеть заглушкой
    r._search = lambda query: [
        {
            "title": "Пчёлы",
            "content": "Пчела посещает ~2000 цветков в день",
            "url": "https://example.org/bees",
        }
    ]
    snippets = r.retrieve(RetrievalQuery(topic="опыление", subject="биология"))
    assert len(snippets) == 1
    s = snippets[0]
    assert s.source == "веб"
    assert s.url == "https://example.org/bees"
    assert "2000" in s.text


def test_search_error_returns_empty():
    r = WebRetriever(api_key="TESTKEY")

    def boom(query):
        raise RuntimeError("network down")

    r._search = boom
    assert r.retrieve(RetrievalQuery(topic="опыление", subject="биология")) == []


def test_empty_topic_and_subject():
    # ключ есть, но тема и предмет пусты → []
    r = WebRetriever(api_key="TESTKEY")
    r._search = lambda query: [{"title": "x", "content": "y", "url": "z"}]
    assert r.retrieve(RetrievalQuery(topic="", subject="")) == []


if __name__ == "__main__":
    test_disabled_without_key()
    test_with_key_returns_snippet()
    test_search_error_returns_empty()
    test_empty_topic_and_subject()
    print("OK test_web_retriever")
