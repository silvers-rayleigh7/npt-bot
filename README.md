# tropa-bot — голосовой ИИ-гид «Путеводитель по научной тропе»

Telegram-бот: голосовой вопрос о науке → лаконичный голосовой ответ «профессорским»
голосом в каноне Перельмана/Ливанова. Личное некоммерческое использование.

Построен поверх [claude-tg](https://github.com/MerkulovDaniil/claude-tg) (Telegram↔Claude
Code OAuth + голос-ввод Groq + память). Наш слой: личность (`CLAUDE.md`), озвучка (`tts.py`),
контент-база (`content/`), методология (`skills/scipop-answer`).

## Архитектура

```
Telegram → claude-tg → Groq Whisper (STT) → claude -p (OAuth, читает CLAUDE.md + content/)
        → tts.py (ElevenLabs → opus) → send_telegram_file → 🔊 голосовое
```

## Развёртывание на новом сервере (в т.ч. перенос Max → Pro)

```bash
git clone <этот-репозиторий> tropa-bot && cd tropa-bot
bash setup.sh                          # системные пакеты, node, claude-tg, deps
claude setup-token                     # на машине с браузером, под нужным аккаунтом (Max/Pro)
cp .env.example .env && nano .env      # заполнить ключи + CLAUDE_CODE_OAUTH_TOKEN; chmod 600 .env
cp -r skills/scipop-answer ~/.claude/skills/
# systemd (см. ниже) и запуск:
systemctl enable --now claude-tg
```

OAuth работает одинаково на Max и Pro — отличаются только лимиты использования.

## systemd

```ini
# /etc/systemd/system/claude-tg.service
[Unit]
Description=Tropa Voice Science Guide Bot
After=network-online.target
[Service]
Type=simple
EnvironmentFile=/root/tropa-bot/.env
Environment=PATH=/root/.local/bin:/usr/local/bin:/usr/bin
WorkingDirectory=/root/tropa-bot
ExecStart=/root/.local/bin/claude-tg --work-dir /root/tropa-bot
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
```

## Структура

| Путь | Назначение |
|------|-----------|
| `CLAUDE.md` | личность бота (системный промпт: канон, уровни А/Б, анти-галлюцинации) |
| `tts.py` | озвучка ElevenLabs → opus ogg (Telegram voice) |
| `content/storylines/` | 16 сюжетов-эталонов (из проекта tropa) |
| `content/storylines.yaml` | банк 139 «поперечных сечений» |
| `content/topics/` | curated demo-темы (выверенный текст уровня А) |
| `content/livanov/` | справки-первооснова (анти-галлюцинации) |
| `skills/scipop-answer/` | методология А/Б/В, канон Перельмана/Ливанова |
| `tests/` | тест tts.py |

## Тесты

```bash
python3 -m pytest tests/ -v
```
