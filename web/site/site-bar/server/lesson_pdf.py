"""Рендер методички урока: markdown → Typst → PDF (bytes).

Фирменный стиль сайта (как PDF сюжетов): сериф, оливковые заголовки, блок «ОПЫТ».
Требует бинарь typst на сервере (env TYPST_BIN) и шрифт с кириллицей (env TYPST_FONT_PATH).
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile

TYPST_BIN = os.environ.get("TYPST_BIN", "typst")
TYPST_FONT_PATH = os.environ.get("TYPST_FONT_PATH", "")
# Список шрифтов по приоритету: фирменный Libertinus → кириллические фолбэки Linux.
TEXT_FONT = os.environ.get("TYPST_TEXT_FONT", 'Libertinus Serif", "DejaVu Serif", "Liberation Serif')


class PdfError(Exception):
    pass


# ─────────────────────────── парсинг markdown ───────────────────────────
def parse_lesson(md: str) -> dict:
    title, meta = "", ""
    sections = []
    cur = None
    for line in md.splitlines():
        s = line.rstrip()
        if s.startswith("## Урок:"):
            title = s.split(":", 1)[1].strip()
        elif s.startswith("## ") and not title:
            title = s[3:].strip()
        elif s.startswith("**Класс:**") or (s.startswith("**") and "Класс" in s):
            meta = re.sub(r"\*\*", "", s).strip()
        elif s.startswith("### "):
            # blocks сохраняет исходный порядок абзацев и пунктов (важно для логики методички)
            cur = {"h": s[4:].strip(), "blocks": []}
            sections.append(cur)
        elif s.strip() and cur is not None:
            ls = s.lstrip()
            num = re.match(r"^\d+[.)]\s+(.+)$", ls)   # «1. …» / «2) …» — нумерованный пункт
            if ls.startswith(("- ", "* ", "• ")):
                cur["blocks"].append(("li", ls[2:].strip()))
            elif num:
                cur["blocks"].append(("li", num.group(1).strip()))
            else:
                cur["blocks"].append(("p", s.strip()))
    return {"title": title or "Урок", "meta": meta, "sections": sections}


# ─────────────────────────── экранирование Typst ───────────────────────────
_SPECIAL = ["\\", "#", "$", "*", "_", "`", "[", "]", "@", "<", ">", "~"]


def _esc(s: str) -> str:
    for ch in _SPECIAL:
        s = s.replace(ch, "\\" + ch)
    return s


def _inline(s: str) -> str:
    """Markdown **жирный** → Typst #strong[...], остальное экранируется."""
    parts = re.split(r"\*\*(.+?)\*\*", s)
    out = []
    for i, part in enumerate(parts):
        e = _esc(part)
        out.append(f"#strong[{e}]" if i % 2 == 1 else e)
    return "".join(out)


def _bold_colon(it: str) -> str:
    """«Ключ: текст» → ключ жирным."""
    m = re.match(r"^(.+?):\s*(.+)$", it)
    if m:
        return f"#strong[{_esc(m.group(1))}:] {_inline(m.group(2))}"
    return _inline(it)


# ─────────────────────────── генерация Typst ───────────────────────────
def to_typst(doc: dict) -> str:
    t = []
    t.append('#set page(width: 21cm, height: 29.7cm, margin: (x: 2.9cm, top: 1.9cm, bottom: 2.1cm), fill: white,')
    t.append('  footer: align(center, text(size: 7.5pt, fill: rgb("#A29B8C"), tracking: 1.6pt)[tropa.fmin.xyz · Научная тропа Иннополиса]))')
    t.append(f'#set text(font: ("{TEXT_FONT}"), size: 11.5pt, fill: rgb("#1A1A18"), lang: "ru", hyphenate: true)')
    t.append('#set par(justify: true, leading: 0.72em, spacing: 0.85em)')
    t.append('#show heading: set text(fill: rgb("#7C7F6A"), weight: "semibold")')
    t.append('#align(center, text(size: 8.5pt, fill: rgb("#7C7F6A"), tracking: 3pt)[НАУЧНАЯ ТРОПА ИННОПОЛИСА · МЕТОДИЧКА УРОКА])')
    t.append('#v(0.2cm)')
    t.append(f'#align(center, text(size: 24pt, weight: "bold", fill: rgb("#3E4038"))[{_esc(doc["title"])}])')
    if doc["meta"]:
        t.append('#v(0.12cm)')
        t.append(f'#align(center, text(size: 10.5pt, fill: rgb("#7C7F6A"))[{_esc(doc["meta"])}])')
    t.append('#v(0.32cm)')
    t.append('#line(length: 100%, stroke: 0.6pt + rgb("#E2DACE"))')
    t.append('#v(0.5cm)')

    for sec in doc["sections"]:
        h = sec["h"]
        low = h.lower()
        is_opyt = "опыт" in low or "🔬" in h
        hclean = h.replace("🔬", "").strip()
        if is_opyt:
            t.append('#block(fill: rgb("#F4F2EE"), inset: 13pt, radius: 6pt, width: 100%, breakable: false)[')
            t.append(f'  #text(size: 13pt, weight: "bold", fill: rgb("#7C7F6A"))[ОПЫТ · {_esc(hclean.replace("Проведи опыт", "").strip() or "Проведи опыт")}]')
            t.append('  #v(0.2cm)')
            for kind, txt in sec["blocks"]:
                inner = _inline(txt) if kind == "p" else f"• {_inline(txt)}"
                t.append(f'  #par(text(size: 11pt)[{inner}])')
            t.append(']')
            t.append('#v(0.4cm)')
        else:
            t.append(f'#text(size: 14pt, weight: "semibold", fill: rgb("#7C7F6A"))[{_esc(hclean)}]')
            t.append('#v(0.22cm)')
            for kind, txt in sec["blocks"]:
                if kind == "p":
                    t.append(f'#par[{_inline(txt)}]')
                else:
                    t.append(f'#par[#text(fill: rgb("#7C7F6A"))[•] {_bold_colon(txt)}]')
            t.append('#v(0.42cm)')
    return "\n".join(t)


# ─────────────────────────── компиляция в PDF ───────────────────────────
def render_lesson_pdf(md: str) -> bytes:
    """markdown методички → PDF bytes. Бросает PdfError при проблеме."""
    doc = parse_lesson(md)
    typ = to_typst(doc)
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "lesson.typ")
        out = os.path.join(tmp, "lesson.pdf")
        with open(src, "w", encoding="utf-8") as f:
            f.write(typ)
        cmd = [TYPST_BIN, "compile", src, out]
        if TYPST_FONT_PATH:
            cmd += ["--font-path", TYPST_FONT_PATH]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=25)
        except Exception as exc:
            raise PdfError(f"typst не запустился: {exc}") from exc
        if r.returncode != 0:
            raise PdfError(f"typst error: {r.stderr.decode('utf-8', 'ignore')[:400]}")
        with open(out, "rb") as f:
            return f.read()
