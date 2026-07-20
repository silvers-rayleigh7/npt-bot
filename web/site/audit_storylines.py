#!/usr/bin/env python3
"""Аудит сюжетов: соответствует ли содержание обещанию заголовка и достаточна ли глубина.

Проверяет две претензии с разбора 13.07:
  1. «пафос сюжета не соответствует содержанию» — заголовок про конкретный объект,
     а внутри общее явление, применимое к чему угодно;
  2. уровень «Глубже» не глубже — «будоражит, но не объясняет».

Запуск:  python3 audit_storylines.py [--limit N]
Результат: docs/audit-storylines.md + сводка в консоль.
"""
import glob
import json
import os
import re
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(ROOT, "site-bar", "server")
load_dotenv(os.path.join(SERVER, ".env"))
sys.path.insert(0, SERVER)
from providers import build_providers, generate  # noqa: E402

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)

PROMPT = """Ты — научный редактор проекта научно-популярных сюжетов о конкретных местах.

Оцени сюжет по двум критериям и верни СТРОГО JSON без пояснений:
{"specificity": 1-5, "depth": 1-5, "issue": "одна фраза о главной проблеме", "fix": "одна фраза что добавить"}

specificity — насколько содержание про ИМЕННО ЭТОТ объект из заголовка, а не про общее явление.
  5 — раскрыт именно этот объект: происхождение, история, чем отличается от похожих, что здесь уникально.
  3 — общее явление объяснено хорошо, но про сам объект — одна-две фразы вскользь.
  1 — заголовок обещает конкретное место, а внутри общая физика/биология, верная для любого объекта.
depth — насколько уровень «Глубже» действительно объясняет механизм до первопричины.
  5 — механизм разобран, видно откуда что берётся, есть количественная сторона.
  1 — заявлено интересное, но объяснения нет: «будоражит и бросает».

БУДЬ СТРОГИМ. Эталон калибровки, оценённый экспертом:
Сюжет «Озеро Виштынец» рассказывает про термоклин, аномалию плотности воды при +4 °C и
сезонные перевороты. Всё это верно для ЛЮБОГО глубокого озера умеренных широт; про сам
Виштынец сказано лишь, что он олиготрофный и его зовут «Балтийским Байкалом». Нет ни
ледникового происхождения, ни эндемиков, ни запасов пресной воды, ни того, чем он
отличается от соседних озёр. Эксперт оценил это как НЕДОСТАТОЧНУЮ конкретность:
specificity = 2. Ориентируйся на эту планку — оценку 5 ставь только если объект раскрыт
по-настоящему, а не упомянут.
"""


def load():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content", "storylines", "*.md"))):
        raw = open(p, encoding="utf-8").read()
        m = FM_RE.match(raw)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)
        tm = re.search(r"^title:\s*(.+)$", fm, re.M)
        parts = re.split(r"(?m)^##\s+(.+?)\s*$", body)
        levels = {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts), 2)}
        out.append({
            "slug": os.path.basename(p)[:-3],
            "title": tm.group(1).strip() if tm else os.path.basename(p)[:-3],
            "levels": levels,
            "deep_len": len(list(levels.values())[-1]) if levels else 0,
        })
    return out


def audit(item, providers):
    body = "\n\n".join(f"## {k}\n{v}" for k, v in item["levels"].items())[:6000]
    try:
        out, _ = generate(
            [{"role": "system", "content": PROMPT},
             {"role": "user", "content": f"Заголовок: {item['title']}\n\n{body}"}],
            providers, max_tokens=220, temperature=0.0,
        )
        m = re.search(r"\{.*\}", out or "", re.S)
        return json.loads(m.group(0)) if m else {}
    except Exception as e:
        return {"error": str(e)[:80]}


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    items = load()[:limit]
    providers = build_providers()
    rows = []
    for i, it in enumerate(items, 1):
        r = audit(it, providers)
        rows.append({**it, **r})
        print(f"  [{i}/{len(items)}] {it['title'][:38]:40} "
              f"конкретность={r.get('specificity','?')} глубина={r.get('depth','?')}")

    rows.sort(key=lambda x: (x.get("specificity", 9), x.get("depth", 9)))
    dst = os.path.join(ROOT, "docs", "audit-storylines.md")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("# Аудит сюжетов: конкретность и глубина\n\n")
        f.write("Критерии с разбора 13.07: содержание должно быть про заявленный объект "
                "(не про общее явление), а уровень «Глубже» — действительно объяснять механизм.\n\n")
        f.write("| Сюжет | Конкретность | Глубина | Знаков в «Глубже» | Проблема | Что добавить |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['title']} | {r.get('specificity','—')} | {r.get('depth','—')} | "
                    f"{r['deep_len']} | {r.get('issue','')} | {r.get('fix','')} |\n")
    print(f"\n→ {dst}")

    low = [r for r in rows if (r.get("specificity") or 9) <= 2 or (r.get("depth") or 9) <= 2]
    print(f"требуют доработки (оценка ≤2): {len(low)} из {len(rows)}")


if __name__ == "__main__":
    main()
