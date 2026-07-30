#!/usr/bin/env python3
"""Скачать шрифты дизайн-системы локально в site/assets/fonts/ + собрать fonts.css.

Зачем локально, а не с Google Fonts: сайт открывают с телефона в поле, и внешняя
зависимость там — это риск получить страницу без заголовочного шрифта. Плюс лишний
сторонний запрос с каждой страницы.

Берём только нужные подмножества (кириллица + латиница) и только используемые
начертания — остальное лишний вес.
"""
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "site", "assets", "fonts")
CSS_PATH = os.path.join(OUT_DIR, "fonts.css")

# UA браузера обязателен: без него Google отдаёт ttf вместо woff2
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
WANT_SUBSETS = ("cyrillic", "latin")
FAMILIES = [
    ("Unbounded", [500, 600]),        # заголовки
    ("Golos Text", [400, 500, 600]),  # основной текст
    ("JetBrains Mono", [400, 500]),   # метки, цифры
]

BLOCK_RE = re.compile(r"/\*\s*([a-z\-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", re.S)


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    faces = []
    for family, weights in FAMILIES:
        fam_q = family.replace(" ", "+")
        css = fetch(f"https://fonts.googleapis.com/css2?family={fam_q}:wght@"
                    f"{';'.join(str(w) for w in weights)}&display=swap").decode()
        for subset, body in BLOCK_RE.findall(css):
            if subset not in WANT_SUBSETS:
                continue
            weight = re.search(r"font-weight:\s*(\d+)", body)
            src = re.search(r"url\((https://[^)]+\.woff2)\)", body)
            rng = re.search(r"unicode-range:\s*([^;]+);", body)
            if not (weight and src):
                continue
            slug = family.lower().replace(" ", "-")
            name = f"{slug}-{weight.group(1)}-{subset}.woff2"
            with open(os.path.join(OUT_DIR, name), "wb") as f:
                f.write(fetch(src.group(1)))
            faces.append(
                f"@font-face{{font-family:'{family}';font-style:normal;"
                f"font-weight:{weight.group(1)};font-display:swap;"
                f"src:url('/assets/fonts/{name}') format('woff2');"
                + (f"unicode-range:{rng.group(1).strip()};" if rng else "")
                + "}"
            )
            print(f"  {name}")

    with open(CSS_PATH, "w", encoding="utf-8") as f:
        f.write("/* Шрифты дизайн-системы — локальные копии, без обращения к Google. */\n")
        f.write("\n".join(faces) + "\n")
    print(f"\nфайлов: {len(faces)} → {CSS_PATH}")


if __name__ == "__main__":
    main()
