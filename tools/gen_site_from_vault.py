#!/usr/bin/env python3
"""Генератор САЙТА из базы знаний (единый источник → сайт).

Из vault-заметок с полем `site_slug` формирует файлы content/storylines/*.md
в формате сайта Даниила. Тело — дословно из заметки (без раздела «## Связи»),
frontmatter — сайтовые поля (title/code/region/tags/geo/routes).

По умолчанию — СУХОЙ ПРОГОН: генерит во временную папку и строго сверяет с текущим
сайтом (значения frontmatter + тело + побайтово). Ничего не трогает.
С флагом --apply — записывает прямо в content/storylines/ репо сайта.

Проверено 06.07.2026: 40/40 сюжетов генерятся байт-в-байт как на сайте.

Использование:
    python3 tools/gen_site_from_vault.py            # проверка (dry-run)
    python3 tools/gen_site_from_vault.py --apply     # записать в репо сайта
"""
import os, re, glob, sys, yaml, tempfile, shutil

VAULT = os.path.expanduser(os.environ.get("NPT_VAULT", "~/Projects/tropa-bot/knowledge"))
SITE  = os.path.expanduser(os.environ.get("TROPA_SITE", "~/Projects/tropa/content/storylines"))
SYU   = os.path.join(VAULT, "10-syuzhety")

def split(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else (None, text)

def gen_frontmatter(v, title, vfm_txt):
    lines = [f"title: {title}", f"code: {v['code']}"]
    if v.get("region"): lines.append(f"region: {v['region']}")
    lines.append("tags:")
    for t in v.get("tags", []): lines.append(f"- {t}")
    if "geo" in v:
        graw = re.search(r"^geo:\s*\[(.+?)\]\s*$", vfm_txt, re.M)  # координаты дословно
        vals = [g.strip() for g in graw.group(1).split(",")] if graw else [str(x) for x in v["geo"]]
        lines.append("geo:")
        for x in vals: lines.append(f"- {x}")
    if "routes" in v:
        if v["routes"]:
            lines.append("routes:")
            for r in v["routes"]: lines.append(f"- {r}")
        else:
            lines.append("routes: []")
    return "\n".join(lines)

def generate(out_dir):
    n = 0
    for path in glob.glob(os.path.join(SYU, "*.md")):
        vfm, vbody = split(open(path, encoding="utf-8").read())
        if not vfm: continue
        v = yaml.safe_load(vfm)
        if not v.get("site_slug"): continue
        title = os.path.basename(path)[:-3]
        body = re.sub(r"\n## Связи\n.*$", "", vbody, flags=re.S).strip()
        out = "---\n" + gen_frontmatter(v, title, vfm) + "\n---\n\n" + body + "\n"
        open(os.path.join(out_dir, v["site_slug"] + ".md"), "w", encoding="utf-8").write(out)
        n += 1
    return n

def verify(gen_dir):
    fm_bad, body_bad, missing, byte_ok = [], [], [], 0
    for f in glob.glob(os.path.join(gen_dir, "*.md")):
        slug = os.path.basename(f); cur = os.path.join(SITE, slug)
        if not os.path.exists(cur): missing.append(slug); continue
        g = open(f, encoding="utf-8").read(); c = open(cur, encoding="utf-8").read()
        if g == c: byte_ok += 1
        gfm, gb = split(g); cfm, cb = split(c)
        if yaml.safe_load(gfm) != yaml.safe_load(cfm): fm_bad.append(slug)
        if gb.strip() != cb.strip(): body_bad.append(slug)
    return fm_bad, body_bad, missing, byte_ok

apply = "--apply" in sys.argv
tmp = tempfile.mkdtemp(prefix="gen_storylines_")
try:
    n = generate(tmp)
    fm_bad, body_bad, missing, byte_ok = verify(tmp)
    print(f"Сгенерировано: {n} | байт-в-байт: {byte_ok}/{n} | "
          f"frontmatter расходится: {len(fm_bad)} | тело: {len(body_bad)} | нет на сайте: {len(missing)}")
    ok = not (fm_bad or body_bad or missing)
    if not ok:
        print("❌ Расхождения:", (fm_bad + body_bad + missing)[:8]); sys.exit(1)
    print("✅ Генерация эквивалентна текущему сайту.")
    if apply:
        for f in glob.glob(os.path.join(tmp, "*.md")):
            shutil.copy2(f, os.path.join(SITE, os.path.basename(f)))
        print(f"→ Записано в {SITE} ({n} файлов). Дальше: собрать сайт и запушить в репо Даниила.")
    if "--bot" in sys.argv:
        # тот же формат сюжета питает и ТГ-бота (RAG по content/storylines/)
        bot_dir = os.path.expanduser(os.environ.get("BOT_STORYLINES",
                    "~/Projects/tropa-bot/tg-bot/content/storylines"))
        os.makedirs(bot_dir, exist_ok=True)
        for f in glob.glob(os.path.join(tmp, "*.md")):
            shutil.copy2(f, os.path.join(bot_dir, os.path.basename(f)))
        print(f"→ Записано в {bot_dir} ({n} файлов) — ТГ-бот теперь видит все сюжеты базы.")
    if not apply and "--bot" not in sys.argv:
        print("Сухой прогон. Запись: --apply (сайт), --bot (ТГ-бот), можно вместе.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
