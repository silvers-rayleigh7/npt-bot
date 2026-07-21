#!/usr/bin/env python3
"""Приёмка черновиков углубления: то, что я проверял руками, — одной командой.

Каждый прогон вскрывал новый класс ошибок, и каждый становился здесь проверкой:
  • сломанные формулы (тире вместо минуса — типографика залезала внутрь $…$)
  • потерянные ссылки на источники (сюжет теряет бейдж «со ссылками»)
  • дрейф в чужую тему (параллакс уехал в метрику пространства-времени)
  • остатки markdown-мусора (**, ###, лапки)

Запуск:  python3 check_drafts.py
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def formulas(text):
    """Формулы разбираем попарно по долларам: жадная регулярка ловит текст МЕЖДУ ними."""
    out = []
    rest = re.sub(r"\$\$([^$]+)\$\$", lambda m: out.append(m.group(1)) or "", text)
    out += [p for i, p in enumerate(rest.split("$")) if i % 2 == 1]
    return out


def footnotes(text):
    defs = set(re.findall(r"^\[\^([^\]]+)\]:", text, re.M))
    # Определение — только в начале строки. Ссылка в середине текста может стоять
    # перед двоеточием (например, перед таблицей) — это по-прежнему ссылка.
    refs = set(re.findall(r"(?<!\n)\[\^([^\]]+)\]", text)) | \
           set(re.findall(r"(?m)(?<=.)\[\^([^\]]+)\]", text))
    refs -= {k for k in defs if not re.search(r"(?m)[^\n]\[\^%s\]" % re.escape(k), text)}
    return defs, refs


def title_words(slug):
    p = os.path.join(ROOT, "content", "storylines", f"{slug}.md")
    m = re.search(r"^title:\s*(.+)$", open(p, encoding="utf-8").read(), re.M)
    t = m.group(1).strip() if m else slug
    return t, {w[:5].lower() for w in re.findall(r"\w{4,}", t)}


def main():
    problems = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "drafts", "*.md"))):
        slug = os.path.basename(p)[:-3]
        s = open(p, encoding="utf-8").read()
        title, tw = title_words(slug)
        issues = []

        broken = [f for f in formulas(s) if "—" in f]
        if broken:
            issues.append(f"сломанных формул: {len(broken)}")

        old = open(os.path.join(ROOT, "content", "storylines", f"{slug}.md"),
                   encoding="utf-8").read()
        # сравниваем только с уровнем, который переписывается: ссылки прочих уровней
        # остаются в файле нетронутыми, требовать их от черновика — ложная тревога
        old_deep = re.split(r"(?m)^##\s+.+?\s*$",
                            re.split(r"^---\n.*?\n---\n", old, flags=re.S)[1])[-1]
        _, old_refs = footnotes(old_deep)
        _, new_refs = footnotes(s)
        if old_refs - new_refs:
            issues.append("потеряны ссылки: " + ", ".join(sorted(old_refs - new_refs)))

        # углубление обязано наращивать: черновик короче исходного — брак
        cur_deep = re.split(r"(?m)^##\s+.+?\s*$", re.split(r"^---\n.*?\n---\n", old, flags=re.S)[1])[-1]
        cur_len = len(re.sub(r"^\[\^[^\]]+\]:.*$", "", cur_deep, flags=re.M).strip())
        if len(s) < cur_len:
            issues.append(f"стало КОРОЧЕ: {cur_len} → {len(s)}")

        if re.search(r"^#{2,4}\s", s, re.M):
            issues.append("остались решётки-заголовки")
        if '"' in s:
            issues.append("остались лапки")

        # дрейф: слова заголовка должны встречаться в тексте
        body_stems = {w[:5].lower() for w in re.findall(r"\w{4,}", s)}
        if tw and not (tw & body_stems):
            issues.append(f"дрейф: слова темы «{title}» в тексте не встречаются")

        status = "OK" if not issues else "; ".join(issues)
        problems += bool(issues)
        print(f"  {slug:24} {len(s):5} симв  {status}")

    print(f"\nчерновиков с замечаниями: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
