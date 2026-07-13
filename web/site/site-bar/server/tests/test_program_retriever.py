"""Тесты ретривера школьной программы. Без сети, на реальном индексе data/."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.base import RetrievalQuery, Snippet          # noqa: E402
from retrieval.program_retriever import ProgramRetriever     # noqa: E402


def test_hit_grade6_biology():
    r = ProgramRetriever()
    res = r.retrieve(RetrievalQuery(grade="6", subject="биология", topic="опыление"))
    assert res, "ожидался непустой список"
    top = res[0]
    assert isinstance(top, Snippet)
    assert top.source == "программа"
    assert "6 класс" in top.text and "биология" in top.text
    assert 0.0 <= top.score <= 1.0


def test_unknown_subject_empty():
    r = ProgramRetriever()
    res = r.retrieve(RetrievalQuery(grade="6", subject="несуществующийпредмет", topic="x"))
    assert res == []


def test_no_grade_empty():
    r = ProgramRetriever()
    res = r.retrieve(RetrievalQuery(subject="биология"))
    assert res == []


def test_grade_normalization():
    # '6 класс' должен матчиться так же, как '6'.
    r = ProgramRetriever()
    res = r.retrieve(RetrievalQuery(grade="6 класс", subject="биология", topic="фотосинтез"))
    assert res and res[0].source == "программа"


def test_empty_topic_base_score():
    # Без темы — разделы пары с базовым score 0.4.
    r = ProgramRetriever()
    res = r.retrieve(RetrievalQuery(grade="6", subject="биология"))
    assert res
    assert all(abs(s.score - 0.4) < 1e-9 for s in res)


if __name__ == "__main__":
    test_hit_grade6_biology()
    test_unknown_subject_empty()
    test_no_grade_empty()
    test_grade_normalization()
    test_empty_topic_base_score()
    print("OK test_program_retriever")
