#!/usr/bin/env python3
"""Сборка сайта Тропа из единого источника content/storylines/*.md + templates/.

Модель: одна сущность — сюжет (content/storylines/<slug>.md, frontmatter + уровни-табы).
Сюжет с `geo` → POI. Маршрут (content/routes/*.yaml) = сюжеты по членству `routes`,
порядок — TSP, линия — реальные пешие тропы. Всё выводится программно, без хардкода.
"""
import hashlib
import json
import math
import os
import re
import urllib.parse
import urllib.request

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
TEMPLATES = os.path.join(ROOT, "templates")
OUT = os.path.join(ROOT, "site")
CACHE = os.path.join(CONTENT, "cache")

MD_EXT = ["extra", "sane_lists"]
LEVEL_ROLE = {"Кратко": "a", "Как это работает": "b", "Глубже": "c"}


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def md(text):
    return markdown.markdown(text.strip(), extensions=MD_EXT)


_FORMULA = re.compile(r"^[\wα-ωΑ-Ωа-яёА-ЯЁ]{1,8}\s*[=≈]\s")


# короткие предлоги/союзы, которые нельзя оставлять висеть в конце строки
_SHORT = ("а|и|о|у|я|в|к|с|на|по|за|до|из|от|об|во|со|не|ни|но|да|то|ко|про|"
          "под|над|при|для|без|или|изо")
# слово из списка как самостоятельное (перед ним — не буква), за ним пробел(ы) и слово
_NBSP_RE = re.compile(r"(?<![А-Яа-яЁёA-Za-z])(" + _SHORT + r")[ \t]+(?=\S)", re.IGNORECASE)


def _typo(t):
    """Микротипографика: длинное тире, неразрывные пробелы у коротких предлогов.
    Математику ($…$ и $$…$$) НЕ трогаем: иначе минус « - » в формуле
    превращается в тире (баг 2026-06-02: R = P - I - E - T → P — I — E — T)."""
    def _apply(s):
        s = re.sub(r"(?<=\S)\s[-–]\s(?=\S)", " — ", s)
        s = s.replace(" -- ", " — ")
        s = s.replace(" — ", " — ")
        s = _NBSP_RE.sub(lambda m: m.group(1) + " ", s)
        return s
    return "".join(
        part if (part.startswith("$") and part.endswith("$") and len(part) > 1)
        else _apply(part)
        for part in re.split(r"(\$\$[^$]*\$\$|\$[^$]+\$)", t))


def _fig_wrap(m):
    """<p><img alt=cap src=path></p> → <figure> с подписью (серифный курсив)."""
    tag = m.group(0)
    alt = re.search(r'alt="([^"]*)"', tag)
    src = re.search(r'src="([^"]+)"', tag)
    if not src:
        return tag
    cap = alt.group(1) if alt else ""
    figcap = '<figcaption>%s</figcaption>' % cap if cap else ""
    return '<figure class="fig"><img src="%s" alt="%s">%s</figure>' % (src.group(1), cap, figcap)


def md_levels(text, all_defs=None):
    """MD → HTML с центрированием отдельных строк-формул (где это формула, не предложение).
    all_defs — file-wide определения сносок: убираем локальные def, дописываем определения
    ровно для использованных в этом уровне ссылок (чинит пустую сноску в L1 и сироту в L3)."""
    if all_defs is not None:
        body = _FN_DEF_RE.sub("", text)
        seen, refs = set(), []
        for k in _FN_REF_RE.findall(body):
            if k in all_defs and k not in seen:
                seen.add(k); refs.append(k)
        if refs:
            body = body.rstrip() + "\n\n" + "\n".join("[^%s]: %s" % (k, all_defs[k]) for k in refs)
        text = body
    def repl(m):
        inner = m.group(1)
        txt = re.sub(r"<[^>]+>", "", inner).strip()
        if (len(txt) < 70 and _FORMULA.match(txt)
                and re.search(r"[·×√≈≤≥πΩφλβα°²³^/]", txt)):
            return '<p class="formula">%s</p>' % inner
        return m.group(0)
    html = md(_typo(text))
    # картинка-врезка → <figure> с подписью
    html = re.sub(r"<p>\s*<img[^>]*>\s*</p>", _fig_wrap, html)
    # одиночная жирная строка = подзаголовок
    html = re.sub(r"<p><strong>([^<]{1,80}?)</strong></p>", r"<h3>\1</h3>", html)
    return re.sub(r"<p>(.*?)</p>", repl, html, flags=re.S)


# ───────────────────────── маршрут: TSP + реальные пешие тропы ───────────────
def _haversine(a, b):
    R = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def tsp_order(coords, start=0):
    """Замкнутый тур (обход с возвратом): nearest-neighbour + 2-opt. Без хардкода."""
    n = len(coords)
    if n <= 2:
        return list(range(n))
    d = [[_haversine(coords[i], coords[j]) for j in range(n)] for i in range(n)]
    unvis = set(range(n)) - {start}
    tour = [start]
    while unvis:
        last = tour[-1]
        nxt = min(unvis, key=lambda j: d[last][j])
        tour.append(nxt)
        unvis.discard(nxt)
    # 2-opt для ЦИКЛА: рёбра считаем по кругу (включая возврат в начало)
    improved = True
    while improved:
        improved = False
        for i in range(n):
            for k in range(i + 1, n):
                a, b = tour[i - 1], tour[i]
                c, e = tour[k], tour[(k + 1) % n]
                if a == c or b == e:
                    continue
                if d[a][c] + d[b][e] + 1e-9 < d[a][b] + d[c][e]:
                    tour[i:k + 1] = reversed(tour[i:k + 1])
                    improved = True
    si = tour.index(start)
    return tour[si:] + tour[:si]


def _decode_polyline6(s):
    coords, idx, lat, lon = [], 0, 0, 0
    while idx < len(s):
        for is_lon in (False, True):
            shift, result = 0, 0
            while True:
                b = ord(s[idx]) - 63
                idx += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dval = ~(result >> 1) if result & 1 else (result >> 1)
            if is_lon:
                lon += dval
            else:
                lat += dval
        coords.append([lat / 1e6, lon / 1e6])
    return coords


def _valhalla_walk(a, b):
    body = {"locations": [{"lat": a[0], "lon": a[1]}, {"lat": b[0], "lon": b[1]}],
            "costing": "pedestrian", "directions_options": {"units": "kilometers"}}
    req = urllib.request.Request(
        "https://valhalla1.openstreetmap.de/route", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "tropa-build/1.0"})
    r = json.load(urllib.request.urlopen(req, timeout=25))
    leg = r["trip"]["legs"][0]
    return _decode_polyline6(leg["shape"]), r["trip"]["summary"]["length"]


def walking_path(route_id, ordered_coords):
    key = hashlib.md5(json.dumps(ordered_coords).encode()).hexdigest()[:12]
    cache_file = os.path.join(CACHE, f"{route_id}_{key}.json")
    if os.path.exists(cache_file):
        return load_yaml(cache_file)
    path, total, ok = [], 0.0, True
    for a, b in zip(ordered_coords, ordered_coords[1:]):
        try:
            seg, ln = _valhalla_walk(a, b)
            path.extend(seg)
            total += ln
        except Exception as e:
            print(f"    [walking_path] fallback straight ({e})")
            path.extend([a, b])
            total += _haversine(a, b) / 1000
            ok = False
    result = {"path": path, "length_km": round(total, 2), "routed": ok}
    if ok:
        os.makedirs(CACHE, exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump(result, f, ensure_ascii=False)
    return result


# ───────────────────────── сущность: сюжет ──────────────────────────────────
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def load_storylines():
    """Единый источник: content/storylines/<slug>.md → список сюжетов с уровнями-табами."""
    d = os.path.join(CONTENT, "storylines")
    items = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(d, fn), encoding="utf-8").read()
        m = FM_RE.match(raw)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        all_defs = {k: v.strip() for k, v in _FN_DEF_RE.findall(m.group(2))}  # сноски всего файла
        parts = re.split(r"(?m)^##\s+(.+?)\s*$", m.group(2))
        levels = []
        for i in range(1, len(parts), 2):
            label = parts[i].strip()
            body = parts[i + 1].strip()
            if body:
                deck, rest = _split_deck(body)   # вопрос-хук уровня → отдельно
                levels.append({"role": LEVEL_ROLE.get(label, "a"), "label": label,
                               "deck": deck, "html": md_levels(rest if deck else body, all_defs),
                               "md": body})
        slug = fn[:-3]
        icon = None
        for ext in (".svg", ".png", ".jpg", ".jpeg", ".webp"):
            cand = f"assets/icons/{slug}{ext}"
            if os.path.exists(os.path.join(OUT, cand)):
                icon = cand
                break
        items.append({
            "slug": slug, "title": fm.get("title", slug), "code": fm.get("code"),
            "icon": icon, "tags": fm.get("tags", []), "geo": fm.get("geo"),
            "routes": fm.get("routes", []) or [], "topic": fm.get("topic", ""),
            "region": fm.get("region"),  # напр. «Калининградская область»; пусто → тропа Иннополиса
            "levels": levels, "fndefs": all_defs,
        })
    return items


def map_link(geo):
    return f"https://yandex.ru/maps/?pt={geo[1]},{geo[0]}&z=17&l=map"


# ───────────────────────── PDF уровня (Typst — самый быстрый) ────────────────
import subprocess  # noqa: E402

TYPST_TPL = """#import "@preview/droplet:0.3.1": dropcap
#import "@preview/mitex:0.2.4": mi, mitex
#set page(width: 21cm, height: 29.7cm, margin: (x: 3.5cm, top: 1.7cm, bottom: 2.4cm), fill: white,
  footer: align(center)[
    #image("/site/assets/glyphs/divider.svg", width: 4.3cm)
    #v(1pt)
    #text(size: 7.5pt, fill: rgb("#A29B8C"), tracking: 1.6pt)[%URL%]
  ])
#set text(font: "Libertinus Serif", size: 11pt, fill: rgb("#1A1A18"), lang: "ru", hyphenate: true)
#set par(justify: true, leading: 0.8em, spacing: 0.8em, first-line-indent: (amount: 1.2em, all: false), linebreaks: "optimized")
#show heading: set text(font: "Libertinus Serif", fill: rgb("#7C7F6A"), weight: "semibold", size: 12pt)
#show heading: set block(above: 1.7em, below: 0.7em)
#show heading: set align(center)
#align(center, %MASTIMG%)
#v(0.4cm)
#align(center, text(size: 8.5pt, fill: rgb("#7C7F6A"), tracking: 3pt)[НАУЧНАЯ ТРОПА ИННОПОЛИСА])
#v(0.16cm)
#align(center, text(size: 27pt, weight: "bold")[%TITLE%])
%DECK%
#v(0.55cm)
#line(length: 100%, stroke: 0.5pt + rgb("#E2DACE"))
#v(0.6cm)
%BODY%
"""


def _clean(s):
    s = s.replace("**", "").replace("*", "")        # снять md-эмфазис
    for ch in "\\#$@<>~`_=":
        s = s.replace(ch, "\\" + ch)
    s = s.replace("//", "\\/\\/")                    # // — это комментарий в Typst-разметке
    return s


def _latex_to_typst(s):
    """Математика LaTeX (как для KaTeX на вебе) → синтаксис Typst-math.
    Покрывает реальные конструкции сюжетов: дроби (\\frac/\\dfrac/\\tfrac), корни,
    суб/суп-скрипты в {…}, \\text{…} с кириллицей, десятичную запятую {,}, градусы,
    пробелы (\\, \\quad …), \\lim/\\ln/\\log/\\sum, \\sim/\\to/\\varepsilon/\\varphi и
    греческие/операторы, чьё имя совпадает с Typst."""
    s = s.replace("{,}", '","')                       # десятичная запятая 0{,}5 → плотная
    s = re.sub(r"\\(?:text|mathrm|operatorname)\s*\{([^{}]*)\}", r'"\1"', s)
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    for _ in range(6):                                # дроби/корни/скобочные индексы — до устойчивости (вложенность)
        s2 = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", s)
        s2 = re.sub(r"\\sqrt\s*\{([^{}]+)\}", r"sqrt(\1)", s2)
        s2 = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", s2)
        s2 = re.sub(r"_\{([^{}]+)\}", r"_(\1)", s2)
        if s2 == s:
            break
        s = s2
    s = s.replace("^\\circ", " degree ").replace("°", " degree ")
    for a, b in (("\\qquad", " quad quad "), ("\\quad", " quad "),
                 ("\\,", " thin "), ("\\;", " thick "), ("\\:", " med "), ("\\ ", " ")):
        s = s.replace(a, b)
    for a, b in (("\\varepsilon", "epsilon.alt"), ("\\varphi", "phi.alt"),
                 ("\\sim", " tilde.op "), ("\\to", " -> "), ("\\cdot", " dot.op "),
                 ("\\times", " times "), ("\\leq", " <= "), ("\\le", " <= "),
                 ("\\geq", " >= "), ("\\ge", " >= "), ("\\neq", " != "),
                 ("\\pm", " plus.minus "), ("\\infty", " infinity "),
                 ("\\approx", " approx "), ("\\ll", " << "), ("\\gg", " >> ")):
        s = s.replace(a, b)
    s = re.sub(r"\\([a-zA-Z]+)", r"\1", s)           # \alpha, \pi, \lim, \ln, \sum … → имя без слеша
    return s


def _mitex_inline(latex):
    """Инлайн-формула LaTeX → #mi(`…`) (mitex рендерит настоящий LaTeX, как KaTeX на вебе)."""
    return "#mi(`" + re.sub(r"\s+", " ", latex).strip() + "`)"


def _mitex_block(latex):
    """Display-формула LaTeX → #mitex(`…`) (центрированное уравнение)."""
    return "#mitex(`" + re.sub(r"\s+", " ", latex).strip() + "`)"


def _clean_math(text):
    """Как _clean, но сегменты $…$ рендерятся через mitex, а не экранируются."""
    out = []
    for part in re.split(r"(\$[^$]+\$)", text):
        if len(part) > 2 and part[0] == "$" and part[-1] == "$":
            out.append(_mitex_inline(part[1:-1]))
        else:
            out.append(_clean(part))
    return "".join(out)


def _split_deck(text):
    """Если уровень открывается заголовком — вынести его как дек (подзаголовок под
    названием), чтобы тело начиналось буквицей без конкурирующего заголовка."""
    blocks = re.split(r"\n\s*\n", _typo(text).strip())
    if not blocks:
        return None, text
    first = blocks[0].strip()
    h = re.match(r"^#{2,6}\s+(.+)$", first)
    bold = re.match(r"^\*\*(.+?)\*\*[.:]?\s*$", first)
    if h:
        deck = h.group(1).strip()
    elif bold and len(bold.group(1)) < 80:
        deck = bold.group(1).strip()
    else:
        return None, text
    return deck, "\n\n".join(blocks[1:])


# ── сноски-ссылки (markdown footnotes → Typst #footnote) ─────────────────────
_FN_DEF_RE = re.compile(r"(?m)^\[\^([\w-]+)\]:[ \t]*(.+?)\s*$")
_FN_REF_RE = re.compile(r"\[\^([\w-]+)\]")


def _fn_text_to_typst(s):
    """Текст сноски (markdown-ссылки) → Typst; кириллические URL percent-кодируются."""
    out, last = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", s):
        out.append(_clean_math(s[last:m.start()]))   # текст сноски может содержать $…$
        url = urllib.parse.quote(m.group(2), safe="/:?#[]@!$&'()*+,;=~._-%")
        out.append('#link("%s")[%s]' % (url, _clean(m.group(1))))
        last = m.end()
    out.append(_clean_math(s[last:]))
    return "".join(out)


def _fig_size_directive(tp):
    """Сайзинг фигуры в PDF: квадратные/высокие (w/h < 1.3) — по высоте,
    чтобы не съедали страницу; широкие — 78% ширины колонки."""
    real = os.path.join(ROOT, tp.lstrip("/"))
    try:
        with open(real, encoding="utf-8") as fh:
            head = fh.read(600)
        m = re.search(r'width="([0-9.]+)(?:pt)?"\s+height="([0-9.]+)(?:pt)?"', head)
        if m:
            w, h = float(m.group(1)), float(m.group(2))
            if h > 0 and (w / h) < 1.3:
                return "height: 7.6cm"
    except Exception:
        pass
    return "width: 78%"


def _md_table_to_typst(lines):
    """markdown-таблица → Typst #table в книжном (booktabs) стиле."""
    rows = []
    for ln in lines:
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if cells and all(re.match(r"^:?-{2,}:?$", c) for c in cells if c != ""):
            continue  # строка-разделитель |---|---|
        rows.append(cells)
    if len(rows) < 2:
        return None
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    header, body = rows[0], rows[1:]

    def cell(c, bold=False):
        # неразрывность: разряды числа (20 000) и число+единица (20 000 км, 7 м/с) не рвём
        c = re.sub(r"(\d)[   ](?=\d)", "\\1 ", c)
        c = re.sub(r"(\d)[ ](?=[A-Za-zА-ЯЁа-яё°/])", "\\1 ", c)
        c = _clean_math(c)
        return "[*%s*]" % c if bold else "[%s]" % c

    out = ["#align(center, block(breakable: false, text(hyphenate: false, table("]  # без переносов в ячейках; короткие таблицы не рвём
    out.append("  columns: %d," % ncol)
    out.append("  stroke: none,")
    out.append("  inset: (x: 7pt, y: 4.5pt),")
    out.append("  align: (left,) + (left,) * %d," % (ncol - 1))
    out.append("  table.hline(stroke: 0.8pt),")
    out.append("  table.header(%s)," % ", ".join(cell(c, True) for c in header))
    out.append("  table.hline(stroke: 0.5pt),")
    for r in body:
        out.append("  " + ", ".join(cell(c) for c in r) + ",")
    out.append("  table.hline(stroke: 0.8pt),")
    out.append("))))")
    return "\n".join(out)


def _md_to_typst(text, base_fndefs=None):
    text = _typo(text).strip()
    fndefs = dict(base_fndefs or {})          # file-wide определения: ссылка в одном уровне, def в другом

    def _grab(m):
        fndefs[m.group(1)] = m.group(2).strip()
        return ""
    text = _FN_DEF_RE.sub(_grab, text)        # вынуть определения сносок из тела

    out = []
    drop_done = False
    blocks = 0  # сколько содержательных блоков уже вышло
    for block in re.split(r"\n\s*\n", text):
        if not block.strip():
            continue
        lines = block.splitlines()
        # картинка-врезка → #figure(image(...), caption)
        img = re.match(r"^!\[(.*?)\]\((.+?)\)$", block.strip())
        if img:
            cap, path = img.group(1), img.group(2)
            tp = path if path.startswith("/site") else ("/site" + path if path.startswith("/") else "/site/" + path)
            cap_typ = (", caption: [%s]" % _clean_math(cap)) if cap else ""
            out.append('#figure(image("%s", %s)%s)' % (tp, _fig_size_directive(tp), cap_typ))
            blocks += 1
            continue
        # display-формула $$…$$ на своей строке → блочное (центрированное) уравнение Typst
        dm = re.match(r"^\$\$(.+?)\$\$$", block.strip(), re.S)
        if dm:
            out.append(_mitex_block(dm.group(1).strip()))
            blocks += 1
            continue
        if all(ln.lstrip().startswith("|") for ln in lines) and len(lines) >= 2:
            tbl = _md_table_to_typst(lines)
            if tbl:
                out.append(tbl)
                blocks += 1
                continue
        h = re.match(r"^#{2,6}\s+(.+)$", lines[0])
        if h and len(lines) == 1:
            out.append("== " + _clean_math(h.group(1).strip()))
            blocks += 1
            continue
        # одиночная жирная строка = подзаголовок
        bold = re.match(r"^\*\*(.+?)\*\*[.:]?\s*$", block.strip()) if len(lines) == 1 else None
        if bold and len(bold.group(1)) < 80:
            out.append("== " + _clean_math(bold.group(1).strip()))
            blocks += 1
            continue
        if all(re.match(r"^\s*[-*]\s+", ln) for ln in lines):
            for ln in lines:
                item = _clean_math(re.sub(r"^\s*[-*]\s+", "", ln))
                item = _FN_REF_RE.sub(
                    lambda m: "#footnote[" + _fn_text_to_typst(fndefs.get(m.group(1), "")) + "]", item)
                out.append("- " + item)
            blocks += 1
            continue
        para = _clean_math(" ".join(lines))
        para = _FN_REF_RE.sub(
            lambda m: "#footnote[" + _fn_text_to_typst(fndefs.get(m.group(1), "")) + "]", para)
        # буквица — только если это настоящее открытие (первые блоки) и абзац существенный
        if (not drop_done and blocks <= 1 and len(para) > 80
                and re.match(r"^[A-Za-zА-ЯЁа-яё]", para)):
            out.append('#dropcap(height: 2, gap: 6pt, fill: rgb("#7C7F6A"))[' + para + "]")
            drop_done = True
        else:
            out.append(para)
        blocks += 1
    return "\n\n".join(out)


def build_pdf(out_dir, slug, role, label, title, body_md, tags, url, icon=None, base_fndefs=None):
    """Сгенерировать красивый PDF уровня через Typst. Возвращает имя файла или None."""
    if icon:
        mastimg = 'image("/site/%s", width: 7cm)' % icon
    else:
        mastimg = 'image("/site/assets/glyphs/mountains.png", width: 2.4cm)'
    deck, rest = _split_deck(body_md)
    deck_typ = ('#v(0.22cm)\n#align(center, text(size: 12.5pt, style: "italic", '
                'fill: rgb("#6E7163"))[' + _clean_math(deck) + "])") if deck else ""
    typ = (TYPST_TPL.replace("%URL%", _clean(url.upper()))
           .replace("%MASTIMG%", mastimg)
           .replace("%TITLE%", _clean(title))
           .replace("%DECK%", deck_typ)
           .replace("%BODY%", _md_to_typst(rest, base_fndefs)))
    src = os.path.join(out_dir, f".{role}.typ")
    pdf = os.path.join(out_dir, f"{role}.pdf")
    with open(src, "w", encoding="utf-8") as f:
        f.write(typ)
    try:
        subprocess.run(["typst", "compile", "--root", ROOT, src, pdf],
                       check=True, capture_output=True, timeout=60)
        os.remove(src)
        return f"{role}.pdf"
    except Exception as e:
        print(f"    [pdf] {slug}/{role} failed: {getattr(e,'stderr',e)}")
        if os.path.exists(src):
            os.remove(src)
        return None


# ───────────────────────── фигуры (CeTZ → SVG) ──────────────────────────────
def build_figures():
    """Компилировать content/figures/*.typ → site/assets/figures/*.svg.
    Файлы с префиксом _ (преамбула) пропускаются — они импортируются."""
    src = os.path.join(CONTENT, "figures")
    if not os.path.isdir(src):
        return
    out = os.path.join(OUT, "assets", "figures")
    os.makedirs(out, exist_ok=True)
    n = 0
    for fn in sorted(os.listdir(src)):
        if not fn.endswith(".typ") or fn.startswith("_"):
            continue
        svg = os.path.join(out, fn[:-4] + ".svg")
        try:
            subprocess.run(["typst", "compile", "--root", ROOT, os.path.join(src, fn), svg],
                           check=True, capture_output=True, timeout=60)
            n += 1
        except Exception as e:
            print(f"  [fig] {fn} failed: {getattr(e, 'stderr', e)}")
    print(f"  figures: {n} svg")


# ───────────────────────── сборка ────────────────────────────────────────────
def build():
    os.makedirs(CACHE, exist_ok=True)
    build_figures()
    site = load_yaml(os.path.join(CONTENT, "site.yaml"))
    # URL сайта — из переменной окружения (генератор подставляет), затем site.yaml, затем дефолт
    site["url"] = os.environ.get("TROPA_URL") or site.get("url") or "tropa.fmin.xyz"
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=False)
    storylines = load_storylines()
    by_slug = {s["slug"]: s for s in storylines}

    # routes (минимальный реестр; POI выводятся из сюжетов с geo)
    routes = []
    routes_dir = os.path.join(CONTENT, "routes")
    for fn in sorted(os.listdir(routes_dir)):
        if fn.endswith(".yaml"):
            routes.append(load_yaml(os.path.join(routes_dir, fn)))

    # ── главная
    cards = []
    for r in routes:
        poi = [s for s in storylines if r["id"] in s["routes"] and s["geo"]]
        cards.append({**r, "points": len(poi)})
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(env.get_template("index.html").render(site=site, routes=cards))
    print(f"  index.html ({len(cards)} routes)")

    # ── отдельная вкладка «Маршруты» (карточки всех маршрутов)
    routes_out = os.path.join(OUT, "routes")
    os.makedirs(routes_out, exist_ok=True)
    with open(os.path.join(routes_out, "index.html"), "w") as f:
        f.write(env.get_template("routes.html").render(site=site, routes=cards))
    print(f"  routes/index.html ({len(cards)} routes)")

    # ── маршруты: POI = сюжеты с geo + членством, порядок TSP, линия по тропам
    route_tpl = env.get_template("route.html")
    for r in routes:
        poi = [s for s in storylines if r["id"] in s["routes"] and s["geo"]]
        if not poi:  # маршрут без сюжетов с geo — карточка есть, страницу-карту не строим
            print(f"  {r['id']}/ — 0 POI, страница пропущена")
            continue
        coords = [s["geo"] for s in poi]
        start = next((i for i, s in enumerate(poi) if s.get("code") == "WP001"), 0)
        order = tsp_order(coords, start)
        ordered = [poi[i] for i in order]
        ordered_coords = [s["geo"] for s in ordered]
        cycle = ordered_coords + [ordered_coords[0]]  # замкнутый обход с возвратом
        wp = walking_path(r["id"], cycle)
        view = []
        for n, s in enumerate(ordered, 1):
            view.append({"n": n, "slug": s["slug"], "name": s["title"],
                         "topic": s["topic"] or (", ".join(s["tags"][:2])),
                         "lat": s["geo"][0], "lon": s["geo"][1],
                         "levels": s["levels"], "location": map_link(s["geo"])})
        rd = {**r, "distance_km": wp["length_km"] or r.get("distance_km"),
              "points": len(view), "poi": view}
        poi_json = json.dumps([{"n": p["n"], "lat": p["lat"], "lon": p["lon"],
                                "name": p["name"]} for p in view], ensure_ascii=False)
        out = os.path.join(OUT, r["id"])
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w") as f:
            f.write(route_tpl.render(site=site, route=rd, poi_json=poi_json,
                                     path_json=json.dumps(wp["path"], ensure_ascii=False)))
        print(f"  {r['id']}/index.html ({len(view)} POI, {wp['length_km']} км)")

    # ── Сюжеты: список + отдельная страница каждого с табами
    out = os.path.join(OUT, "storylines")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(env.get_template("storylines.html").render(site=site, storylines=storylines))
    page = env.get_template("storyline.html")
    npdf = 0
    for s in storylines:
        d = os.path.join(out, s["slug"])
        os.makedirs(d, exist_ok=True)
        loc = map_link(s["geo"]) if s["geo"] else None
        pdfs, pdf_by_i = {}, []
        for lv in s["levels"]:
            fn = build_pdf(d, s["slug"], lv["role"], lv["label"], s["title"], lv["md"],
                           s["tags"], site["url"], s.get("icon"), s.get("fndefs"))
            pdf_by_i.append(fn)
            if fn:
                pdfs[lv["role"]] = fn
                npdf += 1
        s["pdfs"] = pdfs
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(page.render(site=site, s=s, location=loc,
                                pdfs_json=json.dumps(pdf_by_i, ensure_ascii=False),
                                decks_json=json.dumps([lv.get("deck") for lv in s["levels"]],
                                                      ensure_ascii=False)))
    print(f"  storylines/index.html + {len(storylines)} pages ({npdf} PDFs)")

    # ── гиды (отдельный тип контента: авторские маршруты с интерактивной картой)
    build_guides(env, site)
    # ── скиллы — АРХИВИРОВАНО (13.07.2026): вкладка и страница скрыты по просьбе.
    # Шаблон в archive/skills.html; данные в site.yaml (skills:). Чтобы вернуть —
    # раскомментировать строку ниже и вернуть archive/skills.html → templates/.
    # build_skills(env, site)
    # ── бот
    bd = _mk(os.path.join(OUT, "bot"))
    with open(bd, "w") as f:
        f.write(env.get_template("bot.html").render(site=site))
    print("  bot/index.html")
    print(f"Done → {OUT}/ ({len(storylines)} storylines, {len(routes)} route(s))")


def _mk(d):
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "index.html")


def build_skills(env, site):
    skills = []
    gh = site["links"]["github"].rstrip("/")
    for sk in site.get("skills", []):
        item = dict(sk)
        fpath = os.path.join(ROOT, sk["file"])
        if os.path.exists(fpath):
            raw = re.sub(r"^---\n.*?\n---\n", "", open(fpath, encoding="utf-8").read(), count=1, flags=re.S)
            item["content"] = md(raw)
            item["raw_url"] = f"{gh}/blob/main/{sk['file']}"
        skills.append(item)
    with open(_mk(os.path.join(OUT, "skills")), "w") as f:
        f.write(env.get_template("skills.html").render(site=site, skills=skills))
    print(f"  skills/index.html ({len(skills)} skills)")


def _resolve_asset(path):
    """Путь к существующему ассету: пробуем как есть, иначе ту же базу с другим
    расширением. Так yaml хранит «идеальный» путь (.png), а сборка подставит
    .svg-плейсхолдер сейчас и реальный .png/.jpg позже — без правок yaml."""
    if not path:
        return path
    if os.path.exists(os.path.join(OUT, path)):
        return path
    base = os.path.splitext(path)[0]
    for alt in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
        if os.path.exists(os.path.join(OUT, base + alt)):
            return base + alt
    return path  # не нашли — оставляем как есть (404 заметен на превью)


def load_guides():
    """Гиды — отдельный тип контента (content/guides/<slug>.yaml). Авторский маршрут
    гида рендерится интерактивной рисованной картой, а не научным сюжетом."""
    d = os.path.join(CONTENT, "guides")
    if not os.path.isdir(d):
        return []
    items = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".yaml"):
            continue
        g = load_yaml(os.path.join(d, fn))
        g["slug"] = g.get("slug") or fn[:-5]
        g["bio_html"] = md(g["bio_md"]) if g.get("bio_md") else ""
        g["portrait"] = _resolve_asset(g.get("portrait"))
        if g.get("route"):
            g["route"]["map_image"] = _resolve_asset(g["route"].get("map_image"))
            for p in g["route"].get("points", []):
                if p.get("image"):
                    p["image"] = _resolve_asset(p["image"])
        items.append(g)
    return items


def build_guides(env, site):
    """Раздел «Гиды»: сетка карточек + персональная страница каждого гида."""
    guides = load_guides()
    if not guides:
        return
    out = os.path.join(OUT, "guides")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(env.get_template("guides.html").render(site=site, guides=guides))
    page = env.get_template("guide.html")
    for g in guides:
        d = os.path.join(out, g["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(page.render(site=site, g=g))
    print(f"  guides/index.html + {len(guides)} pages")


# ── helpers used by scripts/migrate_storylines.py (one-time migration) ────────
STOP_RE = re.compile(
    r"(Безопасн|Эксплуатац|Обслуживан|Круглогодичн|Всесезонн|Что требует|Что изменил|"
    r"Что усилен|Что убрано|Карта прохожд|Карта фильтр|Проверка перед|Образовательн|"
    r"Сезонн|Автономн|Целевая аудит|Масштабные параметр|Техническая карточк|Build Card|"
    r"Слабые места|Уличн|Практическое задание|Графика панели|Размещение|Внутренний стенд)")
HEADER_RE = re.compile(r"^#{1,6}\s")
STRAY_RE = re.compile(r"^\*{1,3}\s*$")


def _exhibit_file(code):
    base = os.path.join(CONTENT, "exhibits")
    for cand in (f"{code}.md", f"{code}-1.md"):
        p = os.path.join(base, cand)
        if os.path.exists(p):
            return p
    return None


if __name__ == "__main__":
    import sys
    if "--guides-only" in sys.argv:
        # Изолированная сборка ТОЛЬКО гидов: не трогает сюжеты/figures/PDF.
        # Нужна, пока PDF-путь сюжетов несовместим с локальной версией Typst.
        _site = load_yaml(os.path.join(CONTENT, "site.yaml"))
        _site["url"] = os.environ.get("TROPA_URL") or _site.get("url") or "tropa.fmin.xyz"
        _env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=False)
        build_guides(_env, _site)
        print("Done (guides-only)")
    else:
        build()
