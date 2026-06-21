# Dev notes — сборка (читать перед `python3 build.py`)

## ✅ Версия Typst: РОВНО 0.13.x (используй 0.13.1)

`build.py` монолитный: собирает всё, включая `build_figures()` (Typst→SVG) и
`build_pdf()` (Typst→PDF). Узкое окно совместимости версий Typst:

- `mitex 0.2.4` (в TYPST_TPL) ломается на Typst **0.14+**: `error: unknown variable: kai`.
- `first-line-indent: (amount:.., all:..)` в build.py требует Typst **0.13+**
  (на 0.12 → `error: expected length, found dictionary`).
- **Пересечение = 0.13.x.** Проверено: **Typst 0.13.1 собирает все 48 PDF чисто.**

Рабочий бинарь лежит в `.tools/typst` (= 0.13.1, в .gitignore). Запуск полной сборки:
```
PATH="$PWD/.tools:$PATH" python3 build.py
```
С системным Typst 0.14+/0.15 PDF НЕ соберутся (затрёт кнопки PDF → `TROPA_PDFS=[null,...]`).

### Правила
- `site/` **закоммичен** (деплой отдаёт его).
- Полная сборка с 0.13.1 герметична → можно коммитить. НО figures/PDF могут дать
  мелкий байтовый шум vs версия автора — при добавлении НОВОГО сюжета коммить только
  его файлы, существующие откатывай: `git checkout -- <чужие изменённые пути>`.
- Быстрая итерация по **гидам** (без Typst): `python3 build.py --guides-only`.

## Раздел «Гиды» (новый тип контента)
- Источник: `content/guides/<slug>.yaml`. Сборка: `load_guides()` + `build_guides()`.
- Ассеты: `site/assets/guides/<slug>/` (map + portrait + points). Резолвер `_resolve_asset`
  подставляет существующий файл (yaml хранит «идеальный» путь .png, плейсхолдеры .svg).
- Генератор плейсхолдеров/карты: `python3 scripts/gen_guide_assets.py <slug>`.

## Генерация картинок
Ключи в `~/.kwork.env`. Состояние на 20.06.2026:
- **`GEMINI_API_KEY` — РАБОЧИЙ путь.** Достучался напрямую с машины (не гео-блок).
  Модель `gemini-3.1-flash-image` = **Nano Banana**, синхронный `generateContent`,
  отдаёт base64 inlineData (jpeg). Стиль точно ложится в палитру сайта. Скрипт:
  `python3 scripts/gen_guide_images.py <slug> [--map]`.
- `POLZA_API_KEY` — **пустой баланс** (−8 ₽), не использовать пока не пополнят.
- `OPENAI_API_KEY` — пустое значение в env.
Картинки сжимать под веб: `sips -Z 400` (точки) / `-Z 1280` (карты) — Gemini отдаёт ~1 МБ.

## site-bar — виджет-гид сайта (этап 3/B, 21.06.2026)
Текстовый чат-гид в правом-нижнем углу всех страниц («Чем помочь?»). Отвечает по тексту
открытого сюжета (читает `h1`, `.sg-kicker`, `.sg-deck`, все `.body.lvl` из DOM — включая
скрытые табы). Тон — как у TG-бота, но кратко (2–5 предложений).
- Фронт: `site/assets/site-bar/bot.{css,js}`, подключён в `templates/base.html`
  (CSS в head, `bot.js` defer перед `</body>`). Эндпоинт по умолчанию `/api/chat`
  (тот же origin), можно переопределить `<body data-bot-api="...">`.
- Бэкенд: `site-bar/server/` — FastAPI-прокси. **GigaChat-2-Max → OpenRouter/DeepSeek fallback.**
  `providers.py` (OAuth-кэш токена GigaChat, OpenAI-совместимый chat), `app.py` (POST /api/chat,
  history[-8], page_context[:6000]), `system_prompt.md`. `.env` — **GITIGNORED**, секреты не в git.
- **Грабли:** `app.py` обязан звать `load_dotenv()` ДО `from providers import` — иначе
  `build_providers()` падает при импорте (env пуст). GigaChat TLS: локально `verify=False`,
  на сервере `GIGACHAT_CA=<путь к Russian Trusted Root CA>`.
- Деплой: `site-bar/deploy/` (systemd unit + nginx snippet + README). Сервер 144.124.250.77,
  uvicorn на 127.0.0.1:8000, наружу только через nginx `/api/`.
- Локальный тест: `/tmp/sitebar_serve.py` (статика+прокси) + `/tmp/sitebar_test.py` (Playwright).
