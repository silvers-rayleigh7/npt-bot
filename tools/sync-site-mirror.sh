#!/usr/bin/env bash
# Синхронизация зеркала-бэкапа сайта Даниила в наш монорепо.
#
# Назначение: web/site/ — независимая копия репо MerkulovDaniil/tropa на текущем коммите.
# Страховка на случай, если репо Даниила исчезнет. Источник правды — репо Даниила;
# здесь только read-only зеркало (руками web/site/ НЕ редактируем).
#
# Когда запускать: КАЖДЫЙ РАЗ после push в репо Даниила — чтобы наш бэкап был актуален.
# Скрипт сам делает commit + push в наш npt-bot.
#
# Использование:  bash tools/sync-site-mirror.sh
set -euo pipefail

SRC="${TROPA_SRC:-$HOME/Projects/tropa}"        # клон репо Даниила
DST_REPO="${NPT_REPO:-$HOME/Projects/tropa-bot}" # наш монорепо
DST="$DST_REPO/web/site"

[ -d "$SRC/.git" ] || { echo "Нет клона репо Даниила: $SRC"; exit 1; }

# Берём ровно tracked-файлы на HEAD (без .venv/.tools/.env — .env у Даниила gitignored).
COMMIT=$(git -C "$SRC" rev-parse --short HEAD)
COMMIT_FULL=$(git -C "$SRC" rev-parse HEAD)
echo "Источник: MerkulovDaniil/tropa @ $COMMIT"

rm -rf "$DST"; mkdir -p "$DST"
git -C "$SRC" archive HEAD | tar -x -C "$DST"

# Метка происхождения зеркала
cat > "$DST/.MIRROR_INFO" <<EOF
Зеркало-бэкап репозитория MerkulovDaniil/tropa (сайт tropa.fmin.xyz).
Источник правды — репо Даниила; здесь read-only копия, руками не редактировать.
Обновляется скриптом tools/sync-site-mirror.sh после каждого push к Даниилу.

source_repo: https://github.com/MerkulovDaniil/tropa
mirror_commit: $COMMIT_FULL
EOF

cd "$DST_REPO"
git add web/site
if git diff --cached --quiet; then
  echo "Зеркало уже актуально — изменений нет."
  exit 0
fi
git commit -q -m "chore(web): синхронизация зеркала сайта (MerkulovDaniil/tropa @ $COMMIT)

Read-only бэкап репо Даниила. Источник правды — у Даниила, здесь страховочная копия.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
git push origin main
echo "Зеркало обновлено и запушено в npt-bot (источник @ $COMMIT)."
