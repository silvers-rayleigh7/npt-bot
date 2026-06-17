#!/bin/bash
# SessionStart-хук НПТ («вспоминалка» по методу Карпати).
# При старте сессии из репозитория НПТ выводит состояние базы знаний в контекст,
# чтобы Claude не сканировал файлы с нуля. Проектный хук — срабатывает только здесь.
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
VAULT="$ROOT/knowledge"
[ -d "$VAULT" ] || exit 0

echo "🧠 НПТ — база знаний (вспоминалка). Прочитай это прежде, чем лезть в файлы."
echo "Вход: knowledge/_home.md · правила: knowledge/90-meta/Конвенция связей.md · смотритель: скил obsidian-keeper · журнал: knowledge/90-meta/LOG.md"
echo ""
echo "=== _home (карты тем / организация / люди / проекты) ==="
sed -n '6,80p' "$VAULT/_home.md" 2>/dev/null
echo ""
echo "=== последняя запись журнала (что делали в прошлый раз) ==="
awk 'BEGIN{c=0} /^## /{c++} c>=1 && c<2 {print} c>=2 {exit}' "$VAULT/90-meta/LOG.md" 2>/dev/null | head -45
echo ""
echo "=== состояние базы (линтер obsidian-keeper) ==="
python3 "$HOME/.claude/skills/obsidian-keeper/keeper_check.py" "$VAULT" 2>/dev/null | head -3
exit 0
