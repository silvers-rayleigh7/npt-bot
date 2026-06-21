#!/usr/bin/env python3
"""Генерация ассетов гида в нативном стиле сайта (векторный SVG, палитра Тропы).

Создаёт по data из content/guides/<slug>.yaml:
  - map.svg     — карта-серпантин: дорога через все точки маршрута + узлы + море
  - portrait.svg (если нет реального фото) — плейсхолдер с инициалами
  - points/NN.svg (если нет реальной картинки) — плейсхолдер миниатюры точки

Кладёт в site/assets/guides/<slug>/. Реальные картинки (Nano Banana / фото)
позже просто заменяют одноимённые файлы — менять yaml не нужно.

Использование:  python3 scripts/gen_guide_assets.py zernova
"""
import os
import sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# палитра дизайн-системы Тропы
SAND, SAGE, OLIVE, CHAR, INK, BD = "#DBD4C7", "#B8B5A6", "#7C7F6A", "#3E4038", "#1A1A18", "#EAE7E0"
W, H = 1000, 560  # холст карты


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_map(points):
    """Серпантин-дорога через точки (x,y в % → координаты холста) + море сверху."""
    pts = [(p["x"] / 100 * W, p["y"] / 100 * H) for p in points]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    # узлы под HTML-пинами (бледные кружки — пины лягут поверх)
    nodes = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#fff" stroke="{OLIVE}" stroke-width="2"/>'
        f'<text x="{x:.1f}" y="{y+4:.1f}" font-family="Georgia,serif" font-size="12" '
        f'font-weight="700" fill="{OLIVE}" text-anchor="middle">{p["n"]}</text>'
        for (x, y), p in zip(pts, points))
    sx, sy = pts[0]
    ex, ey = pts[-1]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif">
  <rect width="{W}" height="{H}" fill="{SAND}"/>
  <!-- море сверху -->
  <rect width="{W}" height="64" fill="{SAGE}" opacity="0.55"/>
  <text x="{W-18}" y="40" font-size="22" fill="{CHAR}" text-anchor="end" font-style="italic" opacity="0.8">Балтийское море</text>
  <!-- дорога-серпантин -->
  <polyline points="{poly}" fill="none" stroke="{OLIVE}" stroke-width="4"
            stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="2 9" opacity="0.9"/>
  {nodes}
  <text x="{sx:.0f}" y="{sy+34:.0f}" font-size="15" fill="{CHAR}" text-anchor="middle">старт · вокзал</text>
  <text x="{ex:.0f}" y="{ey-22:.0f}" font-size="15" fill="{CHAR}" text-anchor="middle">клифы</text>
</svg>'''


def build_portrait(name):
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500">
  <rect width="400" height="500" fill="{SAND}"/>
  <text x="200" y="270" font-family="Cormorant Garamond,Georgia,serif" font-size="150"
        font-weight="600" fill="{OLIVE}" text-anchor="middle">{initials}</text>
  <text x="200" y="330" font-family="Georgia,serif" font-size="18" fill="{CHAR}"
        text-anchor="middle" opacity="0.7">фото гида</text>
</svg>'''


def build_point(p):
    bg = SAND if p["n"] % 2 else SAGE
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 120">
  <rect width="160" height="120" fill="{bg}" opacity="0.5"/>
  <text x="80" y="58" font-family="Cormorant Garamond,Georgia,serif" font-size="44"
        font-weight="600" fill="{OLIVE}" text-anchor="middle">{p["n"]}</text>
  <text x="80" y="86" font-family="Georgia,serif" font-size="11" fill="{CHAR}"
        text-anchor="middle" opacity="0.6">иллюстрация</text>
</svg>'''


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    slug = sys.argv[1]
    g = yaml.safe_load(open(os.path.join(ROOT, "content", "guides", f"{slug}.yaml"), encoding="utf-8"))
    out = os.path.join(ROOT, "site", "assets", "guides", slug)
    os.makedirs(os.path.join(out, "points"), exist_ok=True)
    points = g["route"]["points"]

    with open(os.path.join(out, "map.svg"), "w", encoding="utf-8") as f:
        f.write(build_map(points))
    print(f"  map.svg ({len(points)} точек)")

    pj = os.path.join(out, "portrait.jpg")
    if not os.path.exists(pj):
        with open(os.path.join(out, "portrait.svg"), "w", encoding="utf-8") as f:
            f.write(build_portrait(g["name"]))
        print("  portrait.svg (плейсхолдер — заменить реальным фото)")

    n = 0
    for p in points:
        real = os.path.join(out, "points", f"{p['n']:02d}.png")
        if os.path.exists(real):
            continue
        with open(os.path.join(out, "points", f"{p['n']:02d}.svg"), "w", encoding="utf-8") as f:
            f.write(build_point(p))
        n += 1
    print(f"  points/*.svg ({n} плейсхолдеров)")


if __name__ == "__main__":
    main()
