#!/usr/bin/env python3
"""Синхронизатор СЮЖЕТОВ из базы знаний в сайт и ТГ-бот (единый источник).

База `knowledge/` — единственный источник правды. Этот скрипт разносит её в оба продукта:
  • сайт  — `~/Projects/tropa/content/storylines/*.md` (+ схемы `content/figures/*.typ`)
  • ТГ-бот — `~/Projects/tropa-bot/tg-bot/content/storylines/*.md` (RAG)

Обрабатывает ДОБАВЛЕНИЕ / ИЗМЕНЕНИЕ / УДАЛЕНИЕ сюжетов: что удалили из базы — удаляется
и из продуктов. Из vault берутся заметки с полем `site_slug`; тело — без раздела «## Связи».

По умолчанию — СУХОЙ ПРОГОН (показывает, что изменится, ничего не трогает).
    python3 tools/gen_site_from_vault.py            # что изменится
    python3 tools/gen_site_from_vault.py --apply     # применить к сайту
    python3 tools/gen_site_from_vault.py --apply --bot   # + к ТГ-боту
    python3 tools/gen_site_from_vault.py --check     # строгая сверка (для миграции): всё ли байт-в-байт

После --apply: собрать сайт (`build.py` в репо Даниила) и запушить; ТГ-бот — задеплоить (scp).
"""
import os, re, glob, sys, yaml, shutil

VAULT = os.path.expanduser(os.environ.get("NPT_VAULT", "~/Projects/tropa-bot/knowledge"))
SITE  = os.path.expanduser(os.environ.get("TROPA_SITE", "~/Projects/tropa/content/storylines"))
SITE_FIG = os.path.expanduser(os.environ.get("TROPA_FIG", "~/Projects/tropa/content/figures"))
BOT   = os.path.expanduser(os.environ.get("BOT_STORYLINES", "~/Projects/tropa-bot/tg-bot/content/storylines"))
SYU   = os.path.join(VAULT, "10-syuzhety")
VFIG  = os.path.join(VAULT, "assets", "figures")

def split(t):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    return (m.group(1), m.group(2)) if m else (None, t)

def gen_fm(v, title, vfm_txt):
    L = [f"title: {title}", f"code: {v['code']}"]
    if v.get("region"): L.append(f"region: {v['region']}")
    L.append("tags:")
    for t in v.get("tags", []): L.append(f"- {t}")
    if "geo" in v:
        g = re.search(r"^geo:\s*\[(.+?)\]\s*$", vfm_txt, re.M)   # координаты дословно
        vals = [x.strip() for x in g.group(1).split(",")] if g else [str(x) for x in v["geo"]]
        L.append("geo:"); L += [f"- {x}" for x in vals]
    if "routes" in v:
        if v["routes"]:
            L.append("routes:"); L += [f"- {r}" for r in v["routes"]]
        else:
            L.append("routes: []")
    return "\n".join(L)

# ── собрать желаемое состояние из базы ──────────────────────────
desired = {}   # site_slug -> текст файла сайта
for path in glob.glob(os.path.join(SYU, "*.md")):
    vfm, vbody = split(open(path, encoding="utf-8").read())
    if not vfm: continue
    v = yaml.safe_load(vfm)
    slug = v.get("site_slug")
    if not slug: continue
    title = os.path.basename(path)[:-3]
    body = re.sub(r"\n## Связи\n.*$", "", vbody, flags=re.S).strip()
    desired[slug] = "---\n" + gen_fm(v, title, vfm) + "\n---\n\n" + body + "\n"

if not desired:
    print("В базе нет сюжетов с site_slug — отказ (защита от случайного удаления всего)."); sys.exit(1)

def classify(target_dir):
    cur = {os.path.basename(f)[:-3]: open(f, encoding="utf-8").read()
           for f in glob.glob(os.path.join(target_dir, "*.md"))}
    new     = [s for s in desired if s not in cur]
    changed = [s for s in desired if s in cur and desired[s] != cur[s]]
    removed = [s for s in cur if s not in desired]
    return new, changed, removed

apply = "--apply" in sys.argv
do_bot = "--bot" in sys.argv
check = "--check" in sys.argv

targets = [("САЙТ", SITE, True)] + ([("ТГ-БОТ", BOT, False)] if do_bot else [])
for name, tdir, is_site in targets:
    os.makedirs(tdir, exist_ok=True)
    new, changed, removed = classify(tdir)
    print(f"\n=== {name} ({tdir}) ===")
    print(f"  новых: {len(new)} {new}")
    print(f"  изменённых: {len(changed)} {changed}")
    print(f"  на удаление: {len(removed)} {removed}")
    if check:
        byte_ok = sum(1 for s in desired
                      if os.path.exists(os.path.join(tdir, s + ".md"))
                      and open(os.path.join(tdir, s + ".md"), encoding="utf-8").read() == desired[s])
        print(f"  байт-в-байт совпадает: {byte_ok}/{len(desired)}")
    if apply:
        for s in new + changed:
            open(os.path.join(tdir, s + ".md"), "w", encoding="utf-8").write(desired[s])
        for s in removed:
            os.remove(os.path.join(tdir, s + ".md"))
        # схемы (только для сайта): синк .typ из базы
        if is_site and os.path.isdir(VFIG):
            for f in glob.glob(os.path.join(VFIG, "*.typ")):
                shutil.copy2(f, os.path.join(SITE_FIG, os.path.basename(f)))
        print(f"  → применено (записано {len(new)+len(changed)}, удалено {len(removed)}).")

if not apply:
    print("\nСухой прогон. Применить: --apply (сайт), добавить --bot (ТГ-бот).")
