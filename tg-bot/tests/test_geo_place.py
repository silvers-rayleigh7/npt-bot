"""geo_place: ветка «наши сюжеты рядом» vs «рассказать про саму местность», устойчивость к сбоям."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import geo_place  # noqa: E402
from geo_place import build_geo_prompt  # noqa: E402


def _content_dir_with(lat, lon, title="Тестовый сюжет"):
    """Временный content-каталог с одним сюжетом в заданной точке."""
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "test-syuzhet.md"), "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {title}\ngeo:\n- {lat}\n- {lon}\n---\n\n## Уровень\nТекст.\n")
    return d


def test_near_branch_lists_our_storylines():
    # сюжет ровно в точке пользователя → ветка «наши точки рядом»
    d = _content_dir_with(55.7519, 48.7440)
    p = build_geo_prompt(55.7519, 48.7440, d)
    assert "Рядом наши научные точки" in p
    assert "Тестовый сюжет" in p


def test_far_branch_describes_place(monkeypatch=None):
    # сюжет за 500 км → ветка «расскажи про саму местность»
    d = _content_dir_with(60.0, 30.0)
    geo_place.reverse_place = lambda lat, lon, timeout=6.0: {"name": "Тестовое село, Область"}
    geo_place.nearby_objects = lambda lat, lon, **kw: [
        {"name": "Озеро Тест", "kind": "водоём", "dist_m": 800.0}
    ]
    p = build_geo_prompt(55.0, 37.0, d)
    assert "Тестовое село" in p
    assert "Озеро Тест" in p
    assert "НЕ предлагай ехать к далёким точкам" in p
    assert "Тестовый сюжет" not in p          # далёкий сюжет не упоминается


def test_far_branch_survives_source_failure():
    # оба внешних источника падают → промпт всё равно собирается
    d = _content_dir_with(60.0, 30.0)

    def boom(*a, **kw):
        raise RuntimeError("network")

    geo_place.reverse_place = boom
    geo_place.nearby_objects = boom
    try:
        p = build_geo_prompt(55.0, 37.0, d)
    except Exception as e:
        raise AssertionError(f"build_geo_prompt бросил наружу: {e}")
    assert "[ГЕО]" in p


if __name__ == "__main__":
    test_near_branch_lists_our_storylines()
    test_far_branch_describes_place()
    test_far_branch_survives_source_failure()
    print("OK test_geo_place")
