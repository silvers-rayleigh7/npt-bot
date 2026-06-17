#!/bin/bash
# Спросить базу знаний НПТ из терминала (метод Карпати: навигация по индексу, без RAG).
# Использование: tools/wiki-query.sh "что мы знаем про закон Бэра?"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
Q="$*"
[ -z "$Q" ] && { echo "Использование: tools/wiki-query.sh \"<вопрос>\""; exit 1; }
command -v claude >/dev/null || { echo "нужен claude CLI"; exit 1; }
claude -p "Ответь по базе знаний в $ROOT/knowledge/. Начни с _home.md и нужного MOC, навигируй по [[ссылкам]], НЕ сканируй всё подряд. Если в базе нет — скажи честно. Вопрос: $Q"
