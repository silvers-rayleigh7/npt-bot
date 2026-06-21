#!/usr/bin/env python3
"""Split the two vetted Innopolis-team Google Docs into per-item markdown files.

Source of truth (verbatim, fact-checked round-2 by Сафиуллова/Фишман):
  storylines_library.md  → 40 QR storylines  → content/qr/storylines/ST-NN.md
  exhibits.md            → physical stands    → content/exhibits/<code>.md

We never re-type the vetted text; we only slice it on heading boundaries and
strip trailing whitespace. A summary is printed for manual verification.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.abspath(os.path.join(HERE, "..", ".."))

ST_OUT = os.path.join(CONTENT, "qr", "storylines")
EX_OUT = os.path.join(CONTENT, "exhibits")


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read().splitlines()


def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = "\n".join(lines).rstrip() + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------- storylines
ST_HEAD = re.compile(r"^#\s+\*{0,2}ST\s*-?\s*0*(\d+)\b")


def split_storylines():
    lines = read("storylines_library.md")
    # find first header line per distinct ST number
    starts = []  # (lineidx, num)
    seen = set()
    for i, ln in enumerate(lines):
        m = ST_HEAD.match(ln)
        if m:
            num = int(m.group(1))
            if num not in seen:
                seen.add(num)
                starts.append((i, num))
    starts.sort()
    results = []
    for k, (idx, num) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        block = lines[idx:end]
        # title = the bold restate header if present, else the plain one
        title = ""
        for ln in block[:4]:
            m = ST_HEAD.match(ln)
            if m:
                t = re.sub(r"^#\s+", "", ln).strip().strip("*").strip()
                if "**" in ln or len(t) > len(title):
                    title = t
        path = os.path.join(ST_OUT, f"ST-{num:02d}.md")
        write(path, block)
        results.append((f"ST-{num:02d}", title, len(block), os.path.relpath(path, CONTENT)))
    return results


# ------------------------------------------------------------------ exhibits
# Primary exhibit headers (the non-bold "title" line of each exhibit).
EX_HEAD = re.compile(r"^#\s+(✅|➕|WP\d|\d+\s*[—«]|Вкладка)")
CODE_RE = re.compile(r"(WP\d+(?:-[0-9а-яёА-ЯЁ]+)?|ЭК-\d+|ST-\d+)")
SKIP_HEAD = re.compile(r"^#\s+Вкладка")


def slug_code(header):
    """Extract a stable filename code from an exhibit header."""
    h = re.sub(r"^#\s+", "", header).strip().strip("*").strip()
    m = CODE_RE.search(h)
    if m:
        code = m.group(1).replace(" ", "")
        return code, h
    # fallbacks: "33 — ...", "37 «...»", "Вкладка 42"
    m = re.match(r"^(✅|➕)?\s*(\d+)\s*[—«]", h)
    if m:
        return f"N{m.group(2)}", h
    m = re.match(r"^Вкладка\s+(\d+)", h)
    if m:
        return f"vkladka-{m.group(1)}", h
    return None, h


def split_exhibits():
    lines = read("exhibits.md")
    starts = []
    for i, ln in enumerate(lines):
        if EX_HEAD.match(ln) and not SKIP_HEAD.match(ln):
            code, h = slug_code(ln)
            starts.append((i, code, h))
    # merge consecutive boundaries that share the same code (title + bold restate)
    merged = []
    for s in starts:
        if merged and s[1] is not None and s[1] == merged[-1][1]:
            continue  # same code → fold into previous block (don't start new file)
        merged.append(s)
    results = []
    for k, (idx, code, h) in enumerate(merged):
        end = merged[k + 1][0] if k + 1 < len(merged) else len(lines)
        # but stop the block before any trailing Вкладка placeholders
        block = lines[idx:end]
        if code is None:
            code = f"unknown-{idx}"
        path = os.path.join(EX_OUT, f"{code}.md")
        write(path, block)
        results.append((code, h, len(block), os.path.relpath(path, CONTENT)))
    return results


def main():
    st = split_storylines()
    ex = split_exhibits()
    print(f"=== STORYLINES: {len(st)} files ===")
    for code, title, n, rel in st:
        print(f"  {code:7} {n:4}L  {title[:70]}")
    print(f"\n=== EXHIBITS: {len(ex)} files ===")
    for code, title, n, rel in ex:
        print(f"  {code:14} {n:4}L  {title[:60]}")


if __name__ == "__main__":
    main()
