#!/usr/bin/env bash
# Развёртывание tropa-bot на свежем Ubuntu-сервере.
# Запуск: bash setup.sh   (под root)
set -euo pipefail

echo "==> Системные пакеты"
apt update && apt -y install ffmpeg python3 python3-pip git curl

echo "==> Node.js 20 (для Claude Code CLI)"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt -y install nodejs

echo "==> uv (для claude-tg)"
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "==> Claude Code CLI + claude-tg + python-зависимости"
npm install -g @anthropic-ai/claude-code
uv tool install claude-tg
pip3 install requests

echo "==> Применяю патчи claude-tg (голос-only, Обрабатываю, multi-account)"
python3 patches/apply_patches.py

echo ""
echo "==> Базовая установка готова. Осталось вручную:"
echo "  1. claude setup-token   (на машине с браузером) → CLAUDE_CODE_OAUTH_TOKEN"
echo "  2. cp .env.example .env  и заполнить все ключи (chmod 600 .env)"
echo "  3. cp -r skills/scipop-answer ~/.claude/skills/"
echo "  4. установить systemd-сервис (см. README.md) и: systemctl enable --now claude-tg"
