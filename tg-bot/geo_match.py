"""Геоматчинг для ТГ-бота: ближайшие сюжеты по координатам (Haversine).

Координаты берутся из frontmatter `geo` файлов content/storylines/*.md.
Поддерживает блочный (geo:\\n- lat\\n- lon) и инлайн (geo: [lat, lon]) форматы.
"""
import glob
import math
import os
import re


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между двумя точками на сфере Земли, в метрах."""
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _parse_title_geo(path: str):
    """(title, (lat, lon)) из frontmatter, либо (None, None) если нет title/geo."""
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if not m:
        return None, None
    fm = m.group(1)
    tm = re.search(r"^title:\s*(.+)$", fm, re.M)
    gm = re.search(r"geo:\s*\n\s*-\s*([-\d.]+)\s*\n\s*-\s*([-\d.]+)", fm)
    if not gm:
        gm = re.search(r"geo:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]", fm)
    if not tm or not gm:
        return None, None
    return tm.group(1).strip(), (float(gm.group(1)), float(gm.group(2)))


def nearest_storylines(lat: float, lon: float, content_dir: str, top: int = 3) -> list[dict]:
    """Топ-N ближайших сюжетов с координатами, отсортированы по расстоянию."""
    pts = []
    for p in glob.glob(os.path.join(content_dir, "*.md")):
        title, geo = _parse_title_geo(p)
        if not geo:
            continue
        pts.append({
            "title": title,
            "slug": os.path.basename(p)[:-3],
            "dist_m": haversine_m(lat, lon, geo[0], geo[1]),
        })
    pts.sort(key=lambda x: x["dist_m"])
    return pts[:top]


def format_distance(m: float) -> str:
    """«120 м» для <1 км, иначе «1.2 км»."""
    return f"{int(round(m))} м" if m < 1000 else f"{m / 1000:.1f} км"
