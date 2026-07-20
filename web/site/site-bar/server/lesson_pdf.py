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
    in_math, math_buf = False, []      # состояние «забора» блочной формулы $$…$$
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
            # блочная формула $$...$$ — может быть на одной строке или в «заборе» из трёх
            one = re.match(r"^\$\$(.+?)\$\$$", ls)
            if one:
                cur["blocks"].append(("math", one.group(1).strip()))
                continue
            if ls == "$$":
                in_math = not in_math
                if not in_math and math_buf:
                    cur["blocks"].append(("math", " ".join(math_buf).strip()))
                    math_buf = []
                continue
            if in_math:
                math_buf.append(ls)
                continue
            num = re.match(r"^\d+[.)]\s+(.+)$", ls)   # «1. …» / «2) …» — нумерованный пункт
            if ls.startswith(("- ", "* ", "• ")):
                cur["blocks"].append(("li", ls[2:].strip()))
            elif num:
                cur["blocks"].append(("li", num.group(1).strip()))
            else:
                cur["blocks"].append(("p", s.strip()))
    return {"title": title or "Урок", "meta": meta, "sections": sections}


# ─────── подача текста в Typst СТРОКОВЫМ ЛИТЕРАЛОМ (без markup-интерпретации) ───────
# Так произвольный текст модели/Википедии не сломает компиляцию: экранируем лишь \ и ".
def _tystr(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _esc(s: str) -> str:
    """Строковый рендер для заголовков: #(...) вставляет текст как есть."""
    return f"#({_tystr(s)})"


def _run(s: str, bold: bool = False) -> str:
    if not s:
        return ""
    body = f"#({_tystr(s)})"
    return f"#strong[{body}]" if bold else body


_FORMULA_RE = re.compile(r"\$([^$\n]+)\$")   # LaTeX между долларами: $v = s/t$


def has_math(md: str) -> bool:
    return bool(_FORMULA_RE.search(md or ""))


def _inline_bold(s: str) -> str:
    parts = re.split(r"\*\*(.+?)\*\*", s)
    return "".join(_run(p, bold=(i % 2 == 1)) for i, p in enumerate(parts) if p)


def _inline(s: str, math: bool = True) -> str:
    """**жирный** → #strong[…]; $формула$ → #mi("…") (mitex). Текст — строковыми литералами.
    При math=False формула печатается как обычный текст (запасной путь сборки)."""
    if not math:
        s = _FORMULA_RE.sub(lambda m: m.group(1), s)
        return _inline_bold(s) or '#("")'
    out, pos = [], 0
    for m in _FORMULA_RE.finditer(s):
        out.append(_inline_bold(s[pos:m.start()]))
        out.append(f"#mi({_tystr(m.group(1))})")
        pos = m.end()
    out.append(_inline_bold(s[pos:]))
    return "".join(x for x in out if x) or '#("")'


def _math_block(latex: str, math: bool = True) -> str:
    """Блочная формула $$…$$ — по центру отдельной строкой."""
    if not math:
        return f'#align(center, text(style: "italic")[{_run(latex)}])'
    return f'#v(0.15cm)\n#align(center, mitex({_tystr(latex)}))\n#v(0.15cm)'


def _bold_colon(it: str, math: bool = True) -> str:
    """«Ключ: текст» → ключ жирным."""
    m = re.match(r"^(.+?):\s*(.+)$", it)
    if m:
        return f"{_run(m.group(1) + ':', bold=True)} {_inline(m.group(2), math)}"
    return _inline(it, math)


# ─────────────────────────── генерация Typst ───────────────────────────
def to_typst(doc: dict, math: bool = True) -> str:
    t = []
    if math:
        # mitex подключаем только когда формулы есть — лишняя зависимость документу не нужна
        t.append('#import "@preview/mitex:0.2.4": mi, mitex')
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
                if kind == "math":
                    t.append(f'  {_math_block(txt, math)}')
                    continue
                inner = _inline(txt, math) if kind == "p" else f"• {_inline(txt, math)}"
                t.append(f'  #par(text(size: 11pt)[{inner}])')
            t.append(']')
            t.append('#v(0.4cm)')
        else:
            t.append(f'#text(size: 14pt, weight: "semibold", fill: rgb("#7C7F6A"))[{_esc(hclean)}]')
            t.append('#v(0.22cm)')
            for kind, txt in sec["blocks"]:
                if kind == "math":
                    t.append(_math_block(txt, math))
                elif kind == "p":
                    t.append(f'#par[{_inline(txt, math)}]')
                else:
                    t.append(f'#par[#text(fill: rgb("#7C7F6A"))[•] {_bold_colon(txt, math)}]')
            t.append('#v(0.42cm)')
    return "\n".join(t)


# ─────────────────────────── компиляция в PDF ───────────────────────────
def render_lesson_pdf(md: str) -> bytes:
    """markdown методички → PDF bytes.

    Сначала пробуем с формулами (mitex). Если сборка сорвалась — например, пакет
    недоступен или модель выдала кривой LaTeX — пересобираем без математики,
    чтобы учитель в любом случае получил документ.
    """
    doc = parse_lesson(md)
    if has_math(md):
        try:
            return _compile(to_typst(doc, math=True))
        except PdfError:
            pass                      # формулы не собрались — отдаём без них
    return _compile(to_typst(doc, math=False))


def _compile(typ: str) -> bytes:
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
