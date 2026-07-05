#!/usr/bin/env python3
"""Синхронизация база ← сайт (сверка/подтягивание правок, сделанных на сайте).

Обычно единый источник — база, и правки идут в ней. Но если кто-то поправил сюжет
прямо в репо сайта, этот скрипт подтянет свежий текст в базу БЕЗ ПОТЕРЬ:
тело — дословно с сайта (со схемами /assets/*.svg), + geo/routes/site_slug,
а связи заметки (cross_section/related/source/used_in/## Связи) сохраняются.

Сайт НЕ трогает. Сюжеты, которых нет в базе, — сообщает, но не создаёт вслепую
(создание новых — через отдельный разбор, чтобы проставить связи и MOC).

Использование:  python3 tools/vault_sync_from_site.py
"""
import os, re, glob, yaml

SITE = os.path.expanduser(os.environ.get("TROPA_SITE", "~/Projects/tropa/content/storylines"))
SYU  = os.path.expanduser(os.environ.get("NPT_VAULT", "~/Projects/tropa-bot/knowledge")) + "/10-syuzhety"

def split(t):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    return (m.group(1), m.group(2)) if m else (None, t)

def raw(fm, name):
    r = re.search(rf"^{name}:\s*(.+)$", fm, re.M)
    return r.group(1).strip() if r else None

updated, missing = [], []
for path in glob.glob(os.path.join(SITE, "*.md")):
    slug = os.path.basename(path)[:-3]
    sfm, sbody = split(open(path, encoding="utf-8").read())
    if not sfm: continue
    s = yaml.safe_load(sfm)
    vpath = os.path.join(SYU, s["title"] + ".md")
    if not os.path.exists(vpath): missing.append(s["title"]); continue

    vfm, vbody = split(open(vpath, encoding="utf-8").read())
    cross = (raw(vfm, "cross_section") or "").strip().strip('"').strip()
    related = raw(vfm, "related") or "[]"; source = raw(vfm, "source") or "[]"
    used_in = raw(vfm, "used_in") or '["[[Сайт НПТ]]", "[[Чат-бот гид]]"]'
    status = raw(vfm, "status") or "готов"; vtype = raw(vfm, "type") or "сюжет"
    m = re.search(r"\n## Связи\n(.*)$", vbody, re.S)
    svz = "\n## Связи\n" + m.group(1).strip() + "\n" if m else ""

    fm = ["---", f"type: {vtype}", f"code: {s['code']}"]
    if s.get("region"): fm.append(f"region: {s['region']}")
    fm.append(f"site_slug: {slug}"); fm.append(f"status: {status}")
    fm.append(f"tags: [{', '.join(s.get('tags', []))}]")
    if "geo" in s:
        graw = re.findall(r"^-\s*(.+)$", re.search(r"geo:\s*\n((?:\s*-\s*.+\n?)+)", sfm).group(1), re.M)
        fm.append(f"geo: [{', '.join(g.strip() for g in graw)}]")
    if "routes" in s: fm.append(f"routes: [{', '.join(s['routes'])}]")
    fm += [f'cross_section: "{cross}"', f"related: {related}", f"source: {source}",
           f"used_in: {used_in}", "levels: [Кратко, Как это работает, Глубже]", "---"]
    note = "\n".join(fm) + "\n\n" + sbody.strip() + "\n" + svz
    if note != open(vpath, encoding="utf-8").read():
        open(vpath, "w", encoding="utf-8").write(note); updated.append(s["title"])

print(f"Обновлено в базе: {len(updated)}")
if missing: print(f"На сайте есть, в базе нет ({len(missing)}): {missing}")
