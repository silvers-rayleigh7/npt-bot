#!/usr/bin/env bash
# Унификация гео-логики сайт↔бот.
#
# Канон гео-кода — у бота (tg-bot/geo_place.py, geo_match.py). Сайту нужна идентичная
# копия, чтобы «что рядом» на сайте и в боте отвечалось одинаково. Скрипт:
#   1) копирует канон → site-bar/server/geo/  (байт-в-байт, сверяет cmp)
#   2) генерирует лёгкий geo_index.json из frontmatter сюжетов сайта
#      (бэкенду сайта не нужны markdown-файлы — только координаты+slug+title)
#
# Запуск:  bash ~/Projects/tropa-bot/tools/sync-geo.sh

set -euo pipefail
BOT="${NPT_BOT_REPO:-$HOME/Projects/tropa-bot}/tg-bot"
SITE_GEO="${TROPA_REPO:-$HOME/Projects/tropa}/site-bar/server/geo"
STORYLINES="${TROPA_REPO:-$HOME/Projects/tropa}/content/storylines"

mkdir -p "$SITE_GEO"

for f in geo_place.py geo_match.py; do
  cp "$BOT/$f" "$SITE_GEO/$f"
  if cmp -s "$BOT/$f" "$SITE_GEO/$f"; then
    echo "✓ $f синхронизирован (байт-в-байт с каноном)"
  else
    echo "✗ $f: копии разошлись после cp — прерываю" >&2
    exit 1
  fi
done

# geo_index.json: [{slug, title, lat, lon}] из frontmatter — переиспользуем парсер канона.
python3 - "$STORYLINES" "$SITE_GEO/geo_index.json" <<'PY'
import sys, os, glob, json
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[2])))  # site-bar/server/geo на path
from geo_match import _parse_title_geo

storylines, out = sys.argv[1], sys.argv[2]
idx = []
for p in sorted(glob.glob(os.path.join(storylines, "*.md"))):
    title, geo = _parse_title_geo(p)
    if not geo:
        continue
    idx.append({"slug": os.path.basename(p)[:-3], "title": title,
                "lat": geo[0], "lon": geo[1]})
json.dump(idx, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"✓ geo_index.json: {len(idx)} сюжетов с координатами")
PY
