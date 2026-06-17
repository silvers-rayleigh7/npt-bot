#!/bin/bash
# Показать непрокомпилированное сырьё из 00-raw и подсказать запуск компиляции (метод Карпати).
# Использование: tools/compile-raw.sh
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="$ROOT/knowledge"
echo "=== Непрокомпилированный RAW (📥 = ещё не превращён в вики) ==="
python3 "$HOME/.claude/skills/obsidian-keeper/keeper_check.py" "$VAULT" 2>/dev/null | grep '📥' || echo "  (нет — всё сырьё скомпилировано)"
echo ""
echo "Чтобы скомпилировать: открой Claude в $ROOT и попроси"
echo "  «скомпилируй новое сырьё из 00-raw в вики»"
echo "Скил obsidian-keeper опишет процесс (обновить существующее, отметить противоречия, не плодить дубли)."
