#!/usr/bin/env bash
# Деплой статики сайта Тропа на боевой сервер (nginx: /var/www/tropa/site).
#
# Источник правды по коду — репо Даниила (MerkulovDaniil/tropa); здесь только выкладка
# уже собранного site/. Секрет НЕ в этом файле — берётся из ~/.tropa-deploy.env (chmod 600,
# в $HOME, вне git). Так пароль переживает компактификацию и не утекает в публичный репо.
#
# Полный цикл выкладки страницы:
#   cd ~/Projects/tropa && PATH="$PWD/.tools:$PATH" python3 build.py   # пересобрать site/
#   git checkout -- $(git status --short | grep '\.pdf$' | awk '{print $2}')  # убрать PDF-шум
#   bash ~/Projects/tropa-bot/tools/deploy-site.sh                     # залить *.html
#
# Использование:
#   bash tools/deploy-site.sh          # читает ~/.tropa-deploy.env
#   bash tools/deploy-site.sh --all    # залить всё (ассеты/pdf/css/js), не только html
set -euo pipefail

CREDS="${TROPA_CREDS:-$HOME/.tropa-deploy.env}"
[ -f "$CREDS" ] || { echo "Нет файла кред: $CREDS  (TROPA_HOST/TROPA_USER/SERVER_PASS)"; exit 1; }
# shellcheck disable=SC1090
source "$CREDS"

HOST="${TROPA_HOST:?}"; USER="${TROPA_USER:?}"; PASS="${SERVER_PASS:?}"
DEST="${TROPA_DEST:-/var/www/tropa/site/}"
SRC="${TROPA_SRC:-$HOME/Projects/tropa}/site/"
[ -d "$SRC" ] || { echo "Нет собранного сайта: $SRC — запусти build.py"; exit 1; }

SSH_OPTS="-o StrictHostKeyChecking=no"
if [ "${1:-}" = "--all" ]; then
  FILTERS=()                                  # всё
else
  FILTERS=(--include='*/' --include='*.html' --exclude='*')  # только страницы
fi

sshpass -p "$PASS" rsync -rzc "${FILTERS[@]}" -e "ssh $SSH_OPTS" "$SRC" "$USER@$HOST:$DEST"

echo "✓ Залито. Проверка боевого домена:"
curl -s -o /dev/null -w "  /teacher/ → HTTP %{http_code}\n" https://tropa.fmin.xyz/teacher/
curl -s -o /dev/null -w "  /         → HTTP %{http_code}\n" https://tropa.fmin.xyz/
