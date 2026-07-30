#!/usr/bin/env python3
"""Заставки сюжетов: плоская векторная графика в языке дизайн-системы.

Прежние заставки были тонким чёрным чертежом на вшитом белом фоне — они
вырезали белый прямоугольник из бумажного фона и выбивались из плоских
цветных схем.

Здесь не 42 уникальных рисунка, а десять геометрических архетипов, каждый
про свой тип явления (огранка, слои, орбиты, колебания, ветвление, сеть,
поток, клетка, градиент, горизонт). Сюжет получает архетип по смыслу и свою
пару акцентов — набор выглядит одной серией, а не сборной солянкой.

Запуск: python3 tools/gen_covers.py [--only slug]
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "assets", "icons")
WORK = os.path.join(ROOT, "content", "figures", "_covers")
FONTS = os.path.join(ROOT, "content", "figures", "fonts")

PAPER = "#FBF8F1"
INK = "#22333C"
ACCENTS = {
    "sky": "#2E9BD6", "grass": "#4EA75D", "terra": "#E9863B",
    "violet": "#7A6FE0", "teal": "#23A79A", "sun": "#F6BB2E", "coral": "#F26B57",
}

# Сюжет → (архетип, основной акцент, дополнительный акцент)
COVERS = {
    "almazy":                ("crystal", "sky", "violet"),
    "yantar":                ("crystal", "sun", "terra"),
    "lenskie-stolby":        ("layers", "terra", "sun"),
    "geo-srez":              ("layers", "terra", "teal"),
    "terrasy-vremeni":       ("layers", "grass", "terra"),
    "batagay":               ("layers", "teal", "sky"),
    "mys-taran":             ("layers", "sky", "sun"),
    "kant-sistema":          ("orbit", "violet", "sun"),
    "solnechnaya-sistema":   ("orbit", "sun", "terra"),
    "bessel":                ("orbit", "sky", "violet"),
    "observatoriya":         ("orbit", "violet", "sky"),
    "sputnik":               ("orbit", "teal", "sky"),
    "solnechnye-chasy":      ("orbit", "sun", "ink"),
    "mayatniki":             ("wave", "sky", "violet"),
    "uslysh-rasstoyanie":    ("wave", "teal", "sky"),
    "seysmograf-viherta":    ("wave", "coral", "ink"),
    "minkovsky":             ("wave", "violet", "sky"),
    "sobolev":               ("wave", "sky", "coral"),
    "dendrohronologiya":     ("branch", "grass", "terra"),
    "staryj-les":            ("branch", "grass", "teal"),
    "tancuyushiy-les":       ("branch", "grass", "sun"),
    "belaya-bereza":         ("branch", "teal", "grass"),
    "fraktalnaya-ramka":     ("branch", "violet", "teal"),
    "russkie-isklyucheniya": ("branch", "coral", "violet"),
    "sem-mostov":            ("grid", "sky", "terra"),
    "most-leonardo":         ("grid", "terra", "ink"),
    "kantorovich":           ("grid", "teal", "sun"),
    "obratnye-zadachi":      ("grid", "violet", "sky"),
    "vhod":                  ("grid", "grass", "sky"),
    "kraevedenie":           ("horizon", "terra", "grass"),
    "skrytaya-matematika":   ("grid", "sun", "grass"),
    "vodorazdel":            ("flow", "sky", "grass"),
    "dvizhushaya-dyuna":     ("flow", "sun", "terra"),
    "vishtynec":             ("flow", "teal", "sky"),
    "klimat-yakutii":        ("thermal", "sky", "coral"),
    "valun-termometr":       ("thermal", "coral", "sky"),
    "mikrobiom":             ("cell", "teal", "grass"),
    "kvadrat-zhizni":        ("cell", "grass", "sun"),
    "belyaev":               ("cell", "coral", "violet"),
    "mamonty":               ("horizon", "sky", "ink"),
    "lavrentyev":            ("flow", "coral", "sun"),
    "kazhetsya-ponimaet":    ("grid", "violet", "coral"),
}

W, H = 440, 200          # под .sg-icon: ширина 80%, высота до 200px
# Подложка во весь лист задаёт канвасу точные границы: без неё cetz сжимает
# холст по содержимому, и фигура уезжает в угол. Координаты внутри считаем
# от низа — так устроен cetz.
HEADER = '''#import "@preview/cetz:0.4.2"
#set page(width: {w}pt, height: {h}pt, margin: 0pt, fill: rgb("{paper}"))
#cetz.canvas(length: 1pt, {{
  import cetz.draw: *
  rect((0, 0), ({w}, {h}), fill: rgb("{paper}"), stroke: none)
'''


def col(name):
    return ACCENTS.get(name, INK)


def crystal(a, b):
    """Огранённый камень: крупные плоские грани, разделённые фоном."""
    cx, cy, r = 220, 96, 66
    return f'''
  merge-path(fill: rgb("{col(a)}"), stroke: none, {{
    line(({cx-r}, {cy+18}), ({cx-r*0.5}, {cy+56}), ({cx+r*0.5}, {cy+56}), ({cx+r}, {cy+18}), close: true) }})
  merge-path(fill: rgb("{col(b)}"), stroke: none, {{
    line(({cx-r*0.5}, {cy+56}), ({cx+r*0.06}, {cy+56}), ({cx-r*0.16}, {cy+18}), close: true) }})
  merge-path(fill: rgb("{INK}"), stroke: none, {{
    line(({cx-r}, {cy+18}), ({cx+r}, {cy+18}), ({cx}, {cy-64}), close: true) }})
  merge-path(fill: rgb("{col(b)}"), stroke: none, {{
    line(({cx-r*0.30}, {cy+18}), ({cx+r*0.30}, {cy+18}), ({cx}, {cy-64}), close: true) }})
  set-style(stroke: (paint: rgb("{PAPER}"), thickness: 3pt))
  line(({cx-r}, {cy+18}), ({cx+r}, {cy+18}))
  line(({cx-r*0.5}, {cy+56}), ({cx-r*0.16}, {cy+18}))
  line(({cx+r*0.5}, {cy+56}), ({cx+r*0.16}, {cy+18}))
'''


def layers(a, b):
    """Слои породы: сплошные пласты, срезанные наклонным сбросом."""
    out, y = [], 30
    bands = ((16, INK), (10, col(a)), (20, col(b)), (8, col(a)), (14, INK), (11, col(b)))
    for th, c in bands:
        # левый блок ровный, правый опущен — разлом читается как одна линия
        # блоки стыкуются вплотную, разлом рисуется одной наклонной линией фона
        out.append(f'  merge-path(fill: rgb("{c}"), stroke: none, {{ '
                   f'line((80, {y}), (236, {y}), (236, {y+th}), (80, {y+th}), close: true) }})')
        out.append(f'  merge-path(fill: rgb("{c}"), stroke: none, {{ '
                   f'line((236, {y-11}), (360, {y-11}), (360, {y+th-11}), (236, {y+th-11}), close: true) }})')
        y += th + 3
    out.append(f'  line((236, 14), (236, 172), stroke: (paint: rgb("{PAPER}"), thickness: 4pt))')
    return "\n".join(out) + "\n"


def orbit(a, b):
    """Орбиты вокруг светила: концентрические дуги и тела на них."""
    cx, cy = 220, 100
    out = [f'  circle(({cx}, {cy}), radius: 17, fill: rgb("{col(a)}"), stroke: none)']
    for i, r in enumerate((44, 68, 92)):
        c = col(b) if i % 2 else INK
        out.append(f'  circle(({cx}, {cy}), radius: {r}, fill: none, '
                   f'stroke: (paint: rgb("{c}"), thickness: 2pt, dash: none))')
    out += [f'  circle(({cx+44}, {cy}), radius: 8, fill: rgb("{INK}"), stroke: none)',
            f'  circle(({cx-48}, {cy+48}), radius: 6.5, fill: rgb("{col(b)}"), stroke: none)',
            f'  circle(({cx+65}, {cy-65}), radius: 5, fill: rgb("{col(a)}"), stroke: none)']
    return "\n".join(out) + "\n"


def wave(a, b):
    """Колебание: затухающая синусоида и её огибающая."""
    pts_a = ", ".join(f"({x}, {100 + 52 * __import__('math').sin(x/26) * (1 - (x-70)/460):.1f})"
                      for x in range(70, 372, 6))
    pts_b = ", ".join(f"({x}, {100 + 52 * (1 - (x-70)/460):.1f})" for x in range(70, 372, 12))
    return f'''
  line({pts_b}, stroke: (paint: rgb("{col(b)}"), thickness: 1.6pt, dash: "dashed"))
  line({pts_a}, stroke: (paint: rgb("{col(a)}"), thickness: 3.4pt))
  line((70, 100), (372, 100), stroke: (paint: rgb("{INK}"), thickness: 1.4pt))
  circle((70, 100), radius: 6, fill: rgb("{INK}"), stroke: none)
'''


def branch(a, b):
    """Ветвление: массивный ствол и расходящиеся ветви — самоподобие роста."""
    out = [f'  line((220, 20), (220, 84), stroke: (paint: rgb("{INK}"), thickness: 9pt))']
    # три уровня ветвления, каждый тоньше и короче предыдущего
    for y, spread, th, c in ((84, 46, 7.0, col(a)), (120, 32, 5.0, col(b)), (148, 20, 3.4, col(a))):
        for sgn in (-1, 1):
            x1, y1 = 220 + sgn * spread, y + 30
            x2, y2 = 220 + sgn * spread * 1.7, y + 50
            out.append(f'  line((220, {y}), ({x1}, {y1}), '
                       f'stroke: (paint: rgb("{c}"), thickness: {th}pt))')
            out.append(f'  line(({x1}, {y1}), ({x2}, {y2}), '
                       f'stroke: (paint: rgb("{c}"), thickness: {th * 0.62:.1f}pt))')
            out.append(f'  circle(({x2}, {y2}), radius: {th * 0.75:.1f}, '
                       f'fill: rgb("{c}"), stroke: none)')
    return "\n".join(out) + "\n"


def grid(a, b):
    """Сеть: узлы и связи — граф, маршрут, зависимость."""
    nodes = [(96, 60), (168, 132), (232, 48), (296, 120), (356, 66), (200, 96)]
    edges = [(0, 5), (1, 5), (2, 5), (3, 5), (4, 3), (2, 4), (0, 1)]
    out = []
    for i, j in edges:
        out.append(f'  line({nodes[i]}, {nodes[j]}, stroke: (paint: rgb("{col(b)}"), thickness: 2pt))')
    for k, n in enumerate(nodes):
        c = col(a) if k == 5 else INK
        r = 13 if k == 5 else 9
        out.append(f'  circle({n}, radius: {r}, fill: rgb("{c}"), stroke: none)')
    return "\n".join(out) + "\n"


def flow(a, b):
    """Поток: русло, сходящиеся струи, направление переноса."""
    out = []
    for i, (y, th) in enumerate(((62, 4), (86, 6.5), (110, 5), (134, 3.5))):
        c = col(a) if i % 2 else col(b)
        pts = ", ".join(f"({x}, {y + 16 * __import__('math').sin((x-80)/54):.1f})"
                        for x in range(80, 368, 8))
        out.append(f'  line({pts}, stroke: (paint: rgb("{c}"), thickness: {th}pt))')
    out.append(f'  merge-path(fill: rgb("{INK}"), stroke: none, {{ '
               f'line((352, 92), (376, 100), (352, 108), close: true) }})')
    return "\n".join(out) + "\n"


def cell(a, b):
    """Клетки: плотная упаковка кругов разного размера — живое сообщество."""
    import math
    out = []
    spots = [(140, 72, 26), (196, 108, 34), (256, 66, 22), (300, 116, 28),
             (170, 136, 18), (246, 138, 15), (330, 62, 13)]
    for i, (x, y, r) in enumerate(spots):
        c = [col(a), col(b), INK][i % 3]
        out.append(f'  circle(({x}, {y}), radius: {r}, fill: rgb("{c}"), stroke: none)')
        if i % 3 == 1:
            out.append(f'  circle(({x}, {y}), radius: {r*0.38:.0f}, fill: rgb("{PAPER}"), stroke: none)')
    return "\n".join(out) + "\n"


def thermal(a, b):
    """Градиент: столбики от холодного к тёплому — перепад температуры."""
    out = []
    x = 96
    for i in range(11):
        t = i / 10
        h = 22 + 96 * (t ** 1.4)
        c = col(a) if t < 0.5 else col(b)
        out.append(f'  rect(({x}, 40), ({x+18}, {40 + h:.0f}), fill: rgb("{c}"), stroke: none)')
        x += 23
    out.append(f'  line((90, 36), (356, 36), stroke: (paint: rgb("{INK}"), thickness: 2.4pt))')
    return "\n".join(out) + "\n"


def horizon(a, b):
    """Горизонт: планы местности уступами и солнце — место и его вид."""
    return f'''
  circle((300, 132), radius: 26, fill: rgb("{col(b)}"), stroke: none)
  merge-path(fill: rgb("{col(a)}"), stroke: none, {{
    line((60, 96), (150, 128), (232, 92), (312, 122), (380, 96), (380, 60), (60, 60), close: true) }})
  merge-path(fill: rgb("{INK}"), stroke: none, {{
    line((60, 62), (128, 88), (208, 56), (288, 84), (380, 54), (380, 24), (60, 24), close: true) }})
'''


SHAPES = {"crystal": crystal, "layers": layers, "orbit": orbit, "wave": wave,
          "branch": branch, "grid": grid, "flow": flow, "cell": cell,
          "thermal": thermal, "horizon": horizon}


def build(slug, kind, a, b):
    body = SHAPES[kind](a, b)
    src = HEADER.format(w=W, h=H, paper=PAPER) + body + "})\n"
    os.makedirs(WORK, exist_ok=True)
    typ = os.path.join(WORK, f"{slug}.typ")
    with open(typ, "w") as f:
        f.write(src)
    svg = os.path.join(OUT, f"{slug}.svg")
    r = subprocess.run(["typst", "compile", "--root", ROOT, "--font-path", FONTS, typ, svg],
                       capture_output=True, timeout=60)
    return r.returncode == 0, (r.stderr or b"").decode()[:160]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    ok = fail = 0
    for slug, (kind, a, b) in COVERS.items():
        if args.only and slug != args.only:
            continue
        good, err = build(slug, kind, a, b)
        if good:
            ok += 1
        else:
            fail += 1
            print(f"  ✗ {slug}: {err}", file=sys.stderr)
    print(f"заставок собрано: {ok}, ошибок: {fail}")


if __name__ == "__main__":
    main()
