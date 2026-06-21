#!/usr/bin/env python3
"""Вставить иконку сюжета по-человечески: чистит фон-прямоугольник (любой цвет)
и кладёт в site/assets/icons/<slug>.svg. Дальше build.py подхватывает по слагу.

Использование:  python3 scripts/add_icon.py <файл.svg> <slug>
Пример:         python3 scripts/add_icon.py ~/Downloads/foo.svg vodorazdel
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "site", "assets", "icons")

# фон во всю канву: <path fill="..." d="M0 0L W 0L W H L0 H L0 0Z"/> (любой fill)
BG = re.compile(r'<path fill="[^"]*" d="M0 0L[\d.]+ 0L[\d.]+ [\d.]+L0 [\d.]+L0 0Z"\s*/>')


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, slug = sys.argv[1], sys.argv[2]
    svg = open(src, encoding="utf-8").read()
    svg, n = BG.subn("", svg, count=1)
    os.makedirs(DST, exist_ok=True)
    out = os.path.join(DST, f"{slug}.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{slug}.svg ← {os.path.basename(src)}  (фон убран: {n})")


if __name__ == "__main__":
    main()
