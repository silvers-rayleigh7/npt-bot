# tropa-bot — голосовой ИИ-гид «Путеводитель по научной тропе»

Telegram-бот: научный вопрос **голосом или текстом** → **голосовой ответ** «профессорским»
голосом в каноне Перельмана / Ливанова, а следом — **текстовый разбор в два уровня**.
Прототип для А. В. Гасникова (научные тропы), демонстрация на ПМЭФ. Личное некоммерческое использование.

Построен поверх [claude-tg](https://github.com/MerkulovDaniil/claude-tg) (Telegram ↔ Claude Code
OAuth + голос-ввод Groq + память диалога). Наш слой: личность (`CLAUDE.md`), озвучка (`tts.py`),
контент-база (`content/`), методология (`skills/scipop-answer`), воспроизводимые правки каркаса (`patches/`).

## Что делает

- **Голос всегда** — лаконичная устная речь без формул, подстроенная под уровень собеседника
  (новичок / любознательный / знаток), в размеренной манере С. Капицы.
- **Текст всегда следом** — разбор в два уровня: 🔹 *для любознательных* (без формул) и
  🔸 *для продвинутых* (механизм, термины, числовая оценка и **формула** Юникодом).
- **Обязательно называет научный принцип** явления (рэлеевское рассеяние, параметрический резонанс…).
- **Опора на выверенную базу** `content/` (RAG) против галлюцинаций; честные числа или порядок величины.

## Архитектура

```
Telegram (голос/текст)
  → Groq Whisper STT (ru)
  → claude-tg (Python, systemd, VPS)
  → claude -p (OAuth, модель opus; читает CLAUDE.md + RAG по content/)
  → tts.py → Yandex SpeechKit v1 (голос filipp) → oggopus
  → MCP send_telegram_file  → 🔊 голосовое
  + MCP send_telegram_message → 📝 текст в два уровня (формулы только в 🔸 Уровне 2)
```

Латентность ~20–40 с (opus + RAG) — осознанный trade-off качество ↔ скорость.
Подробности, решения и история — в [PROJECT.md](PROJECT.md).

## Структура проекта

| Путь | Назначение |
|------|-----------|
| `CLAUDE.md` | личность бота (системный промпт: уровни, манера Капицы, два уровня текста, обязательный термин) |
| `tts.py` | озвучка Yandex SpeechKit v1 → oggopus; `normalize_for_tts`; retry 3× |
| `content/storylines/` | 16 сюжетов-эталонов (из проекта tropa) |
| `content/storylines.yaml` | банк «поперечных сечений» |
| `content/topics/` | curated demo-темы (закат, приливы, радуга) |
| `content/livanov/` | справки-первооснова (анти-галлюцинации) |
| `skills/scipop-answer/` | методология А/Б/В, канон Перельмана/Ливанова |
| `patches/apply_patches.py` | идемпотентные правки claude-tg (голос, мультиаккаунт, `send_telegram_message`, STT) |
| `tools/voice_ab.py` | A/B-подбор голоса Yandex (filipp / zahar / ermil) |
| `tools/build_report.py` | генератор PDF-отчёта по проекту |
| `tests/` | тест `tts.py` (мок, без расхода токенов) |
| `PROJECT.md` | полная техническая выжимка: архитектура, решения, баги, эксплуатация |

## Развёртывание на новом сервере (в т.ч. перенос Max → Pro)

```bash
git clone <этот-репозиторий> tropa-bot && cd tropa-bot
bash setup.sh                          # системные пакеты, node, claude-tg, deps, apply_patches
claude setup-token                     # на машине с браузером, под нужным аккаунтом (Max/Pro)
cp .env.example .env && nano .env      # заполнить ключи + CLAUDE_CODE_OAUTH_TOKEN; chmod 600 .env
cp -r skills/scipop-answer ~/.claude/skills/
systemctl enable --now claude-tg
```

OAuth работает одинаково на Max и Pro — отличаются только лимиты. Сменить модель, голос,
скорость или аккаунт = правка `.env` + `systemctl restart claude-tg`.

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

## Тесты

```bash
python3 -m pytest tests/ -v
```

> Секреты (API-ключи, токены, пароли) в репозитории не хранятся — только в `.env` на сервере.
