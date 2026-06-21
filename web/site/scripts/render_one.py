#!/usr/bin/env python3
"""Отрендерить ОДИН сюжет для вычитки: фигуры→SVG+PNG, уровни→PDF+PNG, HTML.

Выход — в /root/tropa/.render/<slug>/ (внутри project root, чтобы Typst не ругался).
Использование: python3 scripts/render_one.py <slug>
Критик читает PNG-страницы и PNG-фигуры из выходной папки.
"""
import os
import subprocess
import sys

ROOT = "/root/tropa"
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import build  # noqa: E402


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    slug = sys.argv[1]
    out = os.path.join(ROOT, ".render", slug)
    os.makedirs(out, exist_ok=True)

    # ── фигуры (если есть): SVG в сайт + PNG в out для просмотра
    figdir = os.path.join(ROOT, "content", "figures")
    figs = sorted(f for f in os.listdir(figdir)
                  if f.startswith(slug + "-") and f.endswith(".typ"))
    for f in figs:
        base = f[:-4]
        svg = os.path.join(ROOT, "site", "assets", "figures", base + ".svg")
        png = os.path.join(out, base + ".png")
        run(["typst", "compile", "--root", ROOT, os.path.join(figdir, f), svg])
        run(["typst", "compile", "--root", ROOT, os.path.join(figdir, f), png, "--ppi", "170"])

    # ── уровни: PDF (книжная планка) + PNG страниц + HTML
    s = next((x for x in build.load_storylines() if x["slug"] == slug), None)
    if s is None:
        print("ERROR: storyline not found:", slug)
        return
    for lv in s["levels"]:
        pdf = build.build_pdf(out, slug, lv["role"], lv["label"], s["title"],
                              lv["md"], s["tags"], "tropa.fmin.xyz", s.get("icon"))
        if pdf:
            run(["pdftoppm", "-png", "-r", "130",
                 os.path.join(out, f"{lv['role']}.pdf"),
                 os.path.join(out, f"{lv['role']}page")])
        with open(os.path.join(out, f"{lv['role']}.html"), "w", encoding="utf-8") as fh:
            fh.write(build.md_levels(lv["md"]))

    pages = sorted(f for f in os.listdir(out) if f.endswith(".png"))
    print("OUT:", out)
    print("figures:", figs)
    print("levels:", [lv["role"] for lv in s["levels"]])
    print("pngs:", pages)


if __name__ == "__main__":
    main()
