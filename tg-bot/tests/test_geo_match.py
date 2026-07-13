import os
import sys
import tempfile
import textwrap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from geo_match import haversine_m, nearest_storylines, format_distance


def test_haversine_known_distance():
    # Иннополис ↔ Казань ≈ 40 км; проверяем порядок величины
    d = haversine_m(55.7514, 48.7312, 55.7887, 49.1221)
    assert 20000 < d < 60000


def test_haversine_zero():
    assert haversine_m(55.0, 48.0, 55.0, 48.0) < 1.0


def test_format_distance():
    assert format_distance(120) == "120 м"
    assert format_distance(1234) == "1.2 км"


def _write(d, name, title, lat, lon):
    open(os.path.join(d, name), "w", encoding="utf-8").write(textwrap.dedent(f"""\
        ---
        title: {title}
        code: WP001
        tags:
        - физика
        geo:
        - {lat}
        - {lon}
        routes:
        - innopolis
        ---
        ## Кратко
        текст
        """))


def test_nearest_sorted_and_limited():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "a.md", "Ближняя", 55.7515, 48.7313)
        _write(d, "b.md", "Средняя", 55.7600, 48.7400)
        _write(d, "c.md", "Дальняя", 55.8000, 48.8000)
        # файл без geo — игнорируется
        open(os.path.join(d, "n.md"), "w", encoding="utf-8").write(
            "---\ntitle: Нет гео\n---\n## Кратко\nx\n"
        )
        res = nearest_storylines(55.7514, 48.7312, d, top=2)
        assert [r["title"] for r in res] == ["Ближняя", "Средняя"]
        assert res[0]["slug"] == "a"
        assert res[0]["dist_m"] < res[1]["dist_m"]
