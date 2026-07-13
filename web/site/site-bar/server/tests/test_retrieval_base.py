"""Task 1: контракты + косинус."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.base import RetrievalQuery, Snippet  # noqa: E402
from retrieval.embeddings import cosine             # noqa: E402


def test_query_joined():
    q = RetrievalQuery(grade="6", subject="биология", topic="опыление")
    assert "опыление" in q.joined and "биология" in q.joined


def test_snippet_defaults():
    s = Snippet(source="сюжет", title="T", text="B")
    assert s.url == "" and s.score == 0.0


def test_cosine():
    assert cosine([1, 0], [1, 0]) == 1.0
    assert cosine([1, 0], [0, 1]) == 0.0
    assert cosine([], [1]) == 0.0
    assert cosine([0, 0], [0, 0]) == 0.0


if __name__ == "__main__":
    test_query_joined(); test_snippet_defaults(); test_cosine()
    print("OK test_retrieval_base")
