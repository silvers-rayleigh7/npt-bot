#!/usr/bin/env python3
"""Миграция golden/trail-станций в единую модель content/storylines/<slug>.md.

Текст уровней режется из content/exhibits/*.md по маркерам content/trail_levels.yaml,
фактура НЕ переписывается — только реструктурируется в ## Кратко / ## Как это работает /
## Глубже + чистятся артефакты экспорта. Минимум YAML-полей.
"""
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build  # noqa: E402  (STOP_RE, HEADER_RE, _exhibit_file, STRAY_RE)

CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(CONTENT, "storylines")

# координаты trail-станций (резолв геопривязок Яндекс-карт)
GEO = {
    "WP001": [55.74755, 48.73783], "WP003": [55.75375, 48.72934],
    "WP004": [55.74795, 48.73433], "WP007": [55.75755, 48.72968],
    "WP008": [55.752738, 48.741585], "WP010": [55.7563, 48.73723],
    "WP012": [55.75809, 48.73229], "WP013": [55.75827, 48.73484],
    "WP014": [55.75756, 48.72975], "WP016": [55.76006, 48.72993],
    "WP017": [55.75141, 48.73125], "WP018": [55.76429, 48.71851],
}

META = {
    "WP001":   ("Входной стенд", ["навигация", "методология"]),
    "WP001-3": ("Валун-термометр", ["физика", "тепло"]),
    "WP003":   ("Услышь расстояние", ["акустика", "физика"]),
    "WP004":   ("Маятниковая роща", ["физика", "колебания"]),
    "WP007":   ("Геологический срез", ["геология", "время"]),
    "WP008":   ("Солнечная система", ["астрономия", "масштаб"]),
    "WP010":   ("Квадрат жизни", ["биология", "экология"]),
    "WP011":   ("Обсерватория", ["астрономия", "геометрия"]),
    "WP012":   ("Террасы времени", ["геология", "рельеф"]),
    "WP013":   ("Краеведческий стенд", ["история", "место"]),
    "WP014":   ("Мост Леонардо", ["инженерия", "геометрия"]),
    "WP016":   ("Водораздел", ["гидрология", "геоморфология"]),
    "WP017":   ("Белая берёза", ["биология", "оптика"]),
    "WP018":   ("Фрактальная рамка", ["математика", "фракталы"]),
    "WP020":   ("Солнечные часы", ["астрономия", "время"]),
    "WP026":   ("Спутниковая навигация", ["навигация", "геометрия"]),
}
LEVEL_HEADERS = {"a": "## Кратко", "b": "## Как это работает", "c": "## Глубже"}


def clean(text):
    """Снять артефакты экспорта Google Docs, не трогая смысл."""
    text = re.sub(r"\\([*<>_#`\[\]])", r"\1", text)            # \* \< \> → * < >
    text = re.sub(r"\]\(https?://[^)]+\)\]\((https?://[^)]+)\)", r"](\1)", text)  # дубль ссылок
    text = re.sub(r"<(https?://[^>]+)>", r"\1", text)          # <url> → url
    text = re.sub(r"#{4,}\s*", "", text)                        # #### в теле уровня → текст
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def slice_levels(code, cfg):
    path = build._exhibit_file(code)
    lines = open(path, encoding="utf-8").read().splitlines()

    def find(sub, start=0):
        for i in range(start, len(lines)):
            if build.HEADER_RE.match(lines[i]) and sub in lines[i]:
                return i
        return None

    a = find(cfg["a"])
    b = find(cfg["b"], a + 1) if cfg.get("b") else None
    c = find(cfg["c"], (b or a) + 1) if cfg.get("c") else None
    if cfg.get("stop"):
        end = find(cfg["stop"], (c or b or a) + 1)
    else:
        last = c or b or a
        end = len(lines)
        for i in range(last + 1, len(lines)):
            if build.HEADER_RE.match(lines[i]) and build.STOP_RE.search(lines[i]):
                end = i
                break

    spans = []
    if a is not None:
        spans.append(("a", a, b or c or end))
    if b is not None:
        spans.append(("b", b, c or end))
    if c is not None:
        spans.append(("c", c, end))

    out = []
    for role, s, e in spans:
        chunk = [ln for ln in lines[s + 1:e] if not build.STRAY_RE.match(ln)]
        body = clean("\n".join(chunk))
        if body:
            out.append((role, body))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    levels_cfg = yaml.safe_load(open(os.path.join(CONTENT, "trail_levels.yaml")))
    n = 0
    for code, (title, tags) in META.items():
        cfg = levels_cfg.get(code)
        if not cfg:
            print("skip (no markers):", code); continue
        levels = slice_levels(code, cfg)
        if not levels:
            print("skip (no text):", code); continue
        fm = {"title": title, "tags": tags}
        if code in GEO:
            fm["geo"] = GEO[code]
            fm["routes"] = ["innopolis"]
        slug = code.lower()
        front = yaml.dump(fm, allow_unicode=True, sort_keys=False).strip()
        body = "\n\n".join(f"{LEVEL_HEADERS[r]}\n\n{txt}" for r, txt in levels)
        with open(os.path.join(OUT, f"{slug}.md"), "w", encoding="utf-8") as f:
            f.write(f"---\n{front}\n---\n\n{body}\n")
        n += 1
        print(f"  {slug}.md  levels={[r for r,_ in levels]}")
    print(f"Done. {n} storylines → {OUT}/")


if __name__ == "__main__":
    main()
