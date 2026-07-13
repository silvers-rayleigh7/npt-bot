"""Task 6: gather_context — мёрж, устойчивость к падению ретривера, пустой результат."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval import gather_context                      # noqa: E402
from retrieval.base import RetrievalQuery, Snippet        # noqa: E402


class _Good:
    name = "сюжет"
    def retrieve(self, q, limit=3):
        return [Snippet(source="сюжет", title="Солнечные часы", text="Тень показывает время", url="/s/", score=0.9)]


class _Broken:
    name = "программа"
    def retrieve(self, q, limit=3):
        raise RuntimeError("boom")


class _Empty:
    name = "веб"
    def retrieve(self, q, limit=3):
        return []


def test_merge_and_survive_broken():
    q = RetrievalQuery(topic="время")
    out = gather_context(q, retrievers=[_Good(), _Broken(), _Empty()])
    assert "Материалы для опоры" in out
    assert "Солнечные часы" in out            # рабочий ретривер дал вклад
    assert "boom" not in out                  # падение не протекло


def test_all_empty_returns_blank():
    assert gather_context(RetrievalQuery(topic="x"), retrievers=[_Empty(), _Broken()]) == ""


def test_no_retrievers():
    assert gather_context(RetrievalQuery(topic="x"), retrievers=[]) == ""


def test_char_budget():
    q = RetrievalQuery(topic="t")
    out = gather_context(q, retrievers=[_Good()], char_budget=30)  # заголовок уже длиннее — тело обрежется
    assert out == "" or "Солнечные часы" not in out


if __name__ == "__main__":
    test_merge_and_survive_broken(); test_all_empty_returns_blank()
    test_no_retrievers(); test_char_budget()
    print("OK test_gather_context")
