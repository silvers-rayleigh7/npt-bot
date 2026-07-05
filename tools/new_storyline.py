#!/usr/bin/env python3
"""Скаффолд НОВОГО сюжета в базе знаний (единый источник).

Создаёт заготовку заметки в `knowledge/10-syuzhety/<Название>.md` по канону НПТ:
frontmatter B + три уровня (Кратко / Как это работает / Глубже) + раздел «## Связи»
+ чек-лист канона (сноски-источники, формулы KaTeX, схема Typst).

Дальше сюжет ПИШЕТСЯ в базе (текст, сноски, формула, схема), а на сайт и в бота он
попадёт ТОЛЬКО через `tools/gen_site_from_vault.py --apply --bot` — прямых правок в
`content/storylines/` и `tg-bot/content/` не делаем. Так база остаётся единым источником.

Использование:
    python3 tools/new_storyline.py "Название сюжета" <site_slug> [код] [--region "Регион"]
Пример:
    python3 tools/new_storyline.py "Почему небо голубое" pochemu-nebo WP099
"""
import os, sys, re

VAULT = os.path.expanduser(os.environ.get("NPT_VAULT", "~/Projects/tropa-bot/knowledge"))
SYU = os.path.join(VAULT, "10-syuzhety")

if len(sys.argv) < 3:
    print(__doc__); sys.exit(1)
title = sys.argv[1]; slug = sys.argv[2]
code = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "WP???"
region = ""
if "--region" in sys.argv:
    region = sys.argv[sys.argv.index("--region") + 1]

path = os.path.join(SYU, f"{title}.md")
if os.path.exists(path):
    print(f"Уже есть: {path}"); sys.exit(1)

fm = ["---", "type: сюжет", f"code: {code}"]
if region: fm.append(f"region: {region}")
fm += [f"site_slug: {slug}", "status: черновик",
       "tags: [ТЕМА1, ТЕМА2]", "routes: []",
       'cross_section: "ОБЩИЙ ПРИНЦИП ОДНОЙ ФРАЗОЙ — что роднит это явление с другими"',
       'related: ["[[СМЕЖНЫЙ СЮЖЕТ]]"]', 'source: ["[[ИСТОЧНИК]]"]',
       'used_in: ["[[Сайт НПТ]]", "[[Чат-бот гид]]"]',
       "levels: [Кратко, Как это работает, Глубже]", "---"]

body = f"""
## Кратко

**Вопрос-крючок, который цепляет читателя?**

Бытовая сцена и наблюдение прямо «здесь». Ответ по сути, без воды. Назвать научный
принцип явления. При схеме — вставить: ![подпись схемы](/assets/figures/{slug}-1.svg)

## Как это работает

**Подзаголовок — механизм**

Разбор механизма через аналогию. Один закон, показанный на двух-трёх разных примерах
(поперечное сечение). Числа и факты — со сноской-источником[^ref].

## Глубже

**Подзаголовок — для продвинутых**

Формула в виде $...$ или $$...$$ (KaTeX). Таблица при необходимости. Метод измерения.

**Открытый вопрос**

Честный нерешённый вопрос по теме.

[^ref]: Автор, «Название». Издание, год ([ссылка](https://...)).

## Связи
- **Принцип (поперечное сечение):** [[СМЕЖНЫЙ СЮЖЕТ]] (чем роднится).
- **Источник:** [[ИСТОЧНИК]] + сноски.
- **Карта:** [[MOC - ТЕМА]].
- **Используется:** [[Сайт НПТ]], [[Чат-бот гид]].
- **Наверх:** [[_home]].
"""
open(path, "w", encoding="utf-8").write("\n".join(fm) + "\n" + body)
print(f"✅ Заготовка: {path}")
print("""
Дальше:
  1. Напиши сюжет в базе (текст, сноски-источники, формулы, схему content/figures/{slug}-1.typ).
  2. Добавь сюжет в подходящий MOC (30-karty), проверь: python3 ~/.claude/skills/obsidian-keeper/keeper_check.py {vault}
  3. Разнеси в продукты: python3 tools/gen_site_from_vault.py --apply --bot
  4. Собери сайт (build.py в репо Даниила, Typst 0.13.1) → закоммить только новые файлы → пуш.
""".replace("{slug}", slug).replace("{vault}", VAULT))
