#!/usr/bin/env bash
# Гард «единого источника» проекта «Тропа».
#
# Правило (README-edinyj-istochnik.md): сюжеты создаются/правятся/удаляются ТОЛЬКО в
# базе knowledge/, затем разносятся скриптом gen_site_from_vault.py на сайт и бота.
# Прямые правки content/storylines/ (сайт) и tg-bot/content/ (бот) затираются при
# следующем разносе — поэтому они запрещены.
#
# Зачем скрипт: 21.07.2026 весь сеанс сюжеты правились прямо в content/storylines/
# ИЗ ЧУЖОГО воркдерева — проектный хук в tropa/.claude/ такое не ловит, т.к. cwd другой.
# Вывод: защита должна срабатывать ГЛОБАЛЬНО и по ПУТИ редактируемого файла, а не по cwd.
#
# Режимы:
#   session — SessionStart: если сессия относится к «Тропе», печатает правило и сверяет
#             базу с сайтом (расхождение = сайт правили напрямую в обход базы).
#   edit    — PreToolUse(Edit|Write): блокирует правку сгенерированного продукта.
#
# Скрипт живёт в базе (npt-bot) — единый источник и для правил тоже.

BOTREPO="${NPT_BOT_REPO:-$HOME/Projects/tropa-bot}"
GEN="$BOTREPO/tools/gen_site_from_vault.py"

RULE='⛔ ЕДИНЫЙ ИСТОЧНИК «Тропа»: сюжеты — только в базе knowledge/10-syuzhety/, затем
   python3 ~/Projects/tropa-bot/tools/gen_site_from_vault.py --apply [--bot]
   Прямые правки content/storylines/ и tg-bot/content/ ЗАПРЕЩЕНЫ — затрутся при разносе.
   Если сайт уже правили напрямую — верни правки в базу: tools/vault_sync_from_site.py'

case "${1:-session}" in
  session)
    # Самогейтинг: молчим, если сессия не про «Тропу» (глобальный хук, но шумим только по делу).
    remote="$(git remote get-url origin 2>/dev/null || true)"
    case "$PWD:$remote" in
      *tropa*|*npt-bot*) : ;;                # относится к «Тропе» — продолжаем
      *) exit 0 ;;                            # чужой проект — тишина
    esac
    echo "$RULE"
    if [ -f "$GEN" ]; then
      out="$(cd "$BOTREPO" && python3 tools/gen_site_from_vault.py 2>/dev/null \
             | sed -n '/=== САЙТ/,/====/p' || true)"
      n="$(printf '%s' "$out" | sed -n 's/.*новых: \([0-9][0-9]*\).*/\1/p' | head -1)"
      c="$(printf '%s' "$out" | sed -n 's/.*изменённых: \([0-9][0-9]*\).*/\1/p' | head -1)"
      r="$(printf '%s' "$out" | sed -n 's/.*на удаление: \([0-9][0-9]*\).*/\1/p' | head -1)"
      if [ "${n:-0}${c:-0}${r:-0}" = "000" ]; then
        echo "✅ база и сайт синхронны."
      else
        echo "⚠ РАСХОЖДЕНИЕ база↔сайт: новых ${n:-?}, изменённых ${c:-?}, удалить ${r:-?}."
        echo "  Правил базу → разнеси (--apply). Правил сайт напрямую → верни (vault_sync_from_site.py)."
      fi
    fi
    ;;

  edit)
    fp="$(python3 -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)"
    case "$fp" in
      */content/storylines/*.md|*/tg-bot/content/*.md)
        {
          echo "ЗАБЛОКИРОВАНО гардом единого источника «Тропа»."
          echo "Файл — СГЕНЕРИРОВАННЫЙ продукт, правка затрётся при следующем разносе:"
          echo "  $fp"
          echo
          echo "Правь сюжет в базе:  ~/Projects/tropa-bot/knowledge/10-syuzhety/<Название>.md"
          echo "Затем разнеси:       python3 ~/Projects/tropa-bot/tools/gen_site_from_vault.py --apply --bot"
          echo "Если правка уже на сайте — верни в базу: tools/vault_sync_from_site.py"
        } >&2
        exit 2
        ;;
    esac
    ;;
esac
exit 0
