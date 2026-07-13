"""WebRetriever: keyless Википедия по умолчанию, Tavily при ключе, устойчивость к ошибкам."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.base import RetrievalQuery        # noqa: E402
from retrieval.web_retriever import WebRetriever  # noqa: E402


def test_disabled_when_no_key_and_no_wiki():
    wr = WebRetriever(api_key=None, use_wikipedia=False)
    assert wr.enabled is False
    assert wr.retrieve(RetrievalQuery(topic="опыление", subject="биология")) == []


def test_enabled_with_wikipedia():
    assert WebRetriever(api_key=None, use_wikipedia=True).enabled is True


def test_default_disabled_without_key():
    # без ключа Tavily и без явной Википедии — веб выключен (Википедия по умолчанию off)
    assert WebRetriever(api_key=None, use_wikipedia=False).enabled is False


def test_tavily_uses_allowlist():
    wr = WebRetriever(api_key="TESTKEY", allowed_domains=["elementy.ru", "nkj.ru"])
    captured = {}
    import retrieval.web_retriever as m
    orig = m.requests.post

    class _R:
        def raise_for_status(self): pass
        def json(self): return {"results": [{"title": "Э", "content": "факт", "url": "https://elementy.ru/x"}]}

    def fake_post(url, json=None, timeout=None):
        captured["domains"] = json.get("include_domains")
        return _R()

    m.requests.post = fake_post
    try:
        res = wr.retrieve(RetrievalQuery(topic="опыление", subject="биология"))
    finally:
        m.requests.post = orig
    assert captured["domains"] == ["elementy.ru", "nkj.ru"]
    assert len(res) == 1 and "elementy.ru" in res[0].url


def test_wikipedia_mock():
    wr = WebRetriever(api_key=None, use_wikipedia=True)
    wr._search = lambda topic, subject: [
        {"title": "Хлорофилл", "content": "Хлорофилл — зелёный пигмент растений.",
         "url": "https://ru.wikipedia.org/wiki/Хлорофилл"}
    ]
    res = wr.retrieve(RetrievalQuery(topic="хлорофилл", subject="биология"))
    assert len(res) == 1 and res[0].source == "веб"
    assert "Хлорофилл" in res[0].title and "wikipedia" in res[0].url


def test_tavily_selected_when_key():
    wr = WebRetriever(api_key="TESTKEY")
    wr._search = lambda topic, subject: [
        {"title": "Пчёлы", "content": "Пчела посещает ~2000 цветков в день", "url": "https://example.org/bees"}
    ]
    res = wr.retrieve(RetrievalQuery(topic="опыление", subject="биология"))
    assert len(res) == 1 and "2000" in res[0].text and res[0].url == "https://example.org/bees"


def test_search_error_returns_empty():
    wr = WebRetriever(api_key="TESTKEY")

    def boom(topic, subject):
        raise RuntimeError("network")

    wr._search = boom
    assert wr.retrieve(RetrievalQuery(topic="x", subject="y")) == []


def test_empty_topic_and_subject():
    wr = WebRetriever(api_key=None, use_wikipedia=True)
    assert wr.retrieve(RetrievalQuery()) == []


if __name__ == "__main__":
    test_disabled_when_no_key_and_no_wiki(); test_enabled_with_wikipedia()
    test_default_disabled_without_key(); test_tavily_uses_allowlist()
    test_wikipedia_mock(); test_tavily_selected_when_key()
    test_search_error_returns_empty(); test_empty_topic_and_subject()
    print("OK test_web_retriever")
