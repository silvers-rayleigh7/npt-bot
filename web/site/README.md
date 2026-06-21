<div align="center">

# Тропа

**Научный аудиогид, который сам знает, когда рассказывать**

Telegram-бот отслеживает Live Location и запускает голосовой рассказ,
когда вы подошли к научной точке маршрута.
Три уровня глубины: от бытовой аналогии до формул.

[Сайт](https://tropa.fmin.xyz) · [Попробовать бота](#быстрый-старт) · [Маршрут Иннополиса](#маршрут)

</div>

---

## Идея

Таблички с QR-кодами на тропах никто не сканирует.
**Тропа** работает наоборот: бот сам замечает, что вы подошли к точке,
и присылает 30-90 секунд голосового рассказа прямо в Telegram.

Каждая точка привязана к тому, что видно прямо сейчас: стена, от которой отражается звук, развилка дорог с парадоксом Браесса, дата-центр, греющий воздух.

### Три уровня

| Уровень | Для кого | Что внутри |
|---|---|---|
| **L1** | Любой прохожий | Бытовая аналогия, 80-150 слов |
| **L2** | Студент / инженер | Формулы, численная оценка |
| **L3** | Любопытный | Историческая байка, смежные области |

L1 приходит голосом автоматически. L2 и L3 по команде.

## Сюжеты

67 научных сюжетов прошли тройной фильтр:

1. **Школьная мастерская** — собирается из дерева, проволоки, магнитов. Без станков.
2. **Без обслуживания** — никаких расходников: ни мыла, ни воды, ни бумаги. Поставил и забыл.
3. **Любая погода** — металл, дерево, камень. Работает в дождь, мороз, жару.

Средний бюджет ~500 руб на точку. Полный каталог с фильтрами: [tropa.fmin.xyz/storylines](https://tropa.fmin.xyz/storylines/)

## Маршрут

Первый маршрут: **Университет Иннополис**, 1.8 км, 8 точек, ~45 мин.

| # | Точка | Наука | Интерактив |
|:---:|---|---|---|
| 1 | Главный вход | GPS/ГЛОНАСС, трилатерация | Магнитный трилатератор |
| 2 | Атриум | Акустика, реверберация | Эхо-хлопок |
| 3 | Дорожка роботов | SLAM, лидар | Карта неопределённости |
| 4 | Точка Теслы | Электромагнитная индукция | Катушка + магнит |
| 5 | Развилка | Равновесие Нэша-Вардропа | Доска парадокса Браесса |
| 6 | Спортзона | Число Фруда, биомеханика | Маятниковая нога |
| 7 | Зелёная зона | Вода в деревьях | Шкала давления |
| 8 | ИТ-парк | Тепло дата-центров, энтропия | «Тёплый бит» |

Карта и аудио: [tropa.fmin.xyz/innopolis](https://tropa.fmin.xyz/innopolis/)

## Структура проекта

```
site/                              — статический сайт (tropa.fmin.xyz)
  index.html                       — главная
  innopolis/                       — маршрут с картой и аудиоплеером
  storylines/                      — 67 сюжетов с фильтрами
  skills/                          — документация скиллов
  audio/                           — MP3: 8 POI × 3 уровня = 24 файла

content/
  storylines.yaml                  — банк сюжетов (67 активных из 139)
  routes/innopolis.yaml            — конфиг маршрута

bot/
  config/poi.innopolis.yaml        — координаты и радиусы 8 точек
  config/style.md                  — системный промпт (tone of voice)
  scripts/bot.py                   — Telegram-бот
  scripts/narrate.py               — генерация текста через LLM
  scripts/poi_match.py             — геоматчинг (Haversine + cooldown)
  scripts/tts.py, stt.py           — озвучка и распознавание

skills/
  salute-tts/SKILL.md              — TTS-озвучка (Salute Speech / Edge TTS)
  salute-tts/build_audio.py        — генератор аудио
  salute-tts/narrations/*.xml      — SSML-исходники
  anti-ai-text/SKILL.md            — детектор ИИ-текста
  poi-gen/SKILL.md                 — генерация новых POI
  narration-gen/SKILL.md           — пайплайн storyline → L1/L2/L3 → SSML → аудио
  outdoor-scipop-architect/SKILL.md — проектирование научпоп-экспонатов (8 фильтров)
  storyline-proofread/SKILL.md     — quality-gate вычитки сюжета до издательского качества
```

## Скиллы

Скилл — это Markdown-файл с инструкциями для Claude Code. Агент подключает нужный скилл автоматически или по явному запросу.

| Скилл | Что делает | Статус |
|---|---|---|
| `salute-tts` | Озвучка через Salute Speech, fallback на Edge TTS | ready |
| `anti-ai-text` | Детекция и переписывание ИИ-звучащего текста | ready |
| `narration-gen` | Пайплайн storyline → L1/L2/L3 → anti-AI → SSML → аудио | ready |
| `outdoor-scipop-architect` | Проектирование и верификация научпоп-экспонатов по манифесту (8 фильтров, метод сечения, уровни А/Б/В) | ready |
| `storyline-proofread` | Quality-gate вычитки сюжета до издательского качества: панель адверсариальных критиков + цикл правок | ready |
| `poi-gen` | Генерация POI: от сюжета до аудио | planned |

### Как добавить маршрут

Один файл — один маршрут. Сайт собирается автоматически.

1. Создать `content/routes/{id}.yaml` по образцу `innopolis.yaml`
2. Запустить `python3 build.py`

Всё. Скрипт найдёт YAML, сгенерирует страницу маршрута с картой Leaflet и аудиоплеером, добавит карточку на главную.

**Формат YAML:**
```yaml
id: sviyazh                         # ID = папка site/{id}/
name: Свияжские холмы
city: Татарстан
distance_km: 3.2
points: 6
time_min: 60
status: draft                       # draft | ready
map_center: [55.77, 48.66]
map_zoom: 15
poi:
  - id: hilltop
    n: 1
    name: Вершина холма
    topic: Расстояние до горизонта
    lat: 55.7701
    lon: 48.6612
    tags: [геометрия, физика]
    interactive: "Металлическая пластина с формулой d=√(2Rh)"
    audio:
      l1: audio/01_hilltop_l1.mp3
      l2: audio/01_hilltop_l2.mp3
      l3: audio/01_hilltop_l3.mp3
    pdf:
      l1: cards/01_hilltop_l1.pdf
    l1: "<p>Текст базового уровня...</p>"
    l2: "<p>Текст с формулами...</p>"
    l3: "<p>Текст с историями...</p>"
```

**Бот:** скопировать конфиг точек в `bot/config/poi.{id}.yaml`, добавить маршрут в `bot.yaml`.

### Как добавить сюжет

1. Дописать в `content/storylines.yaml`
2. Проверить три фильтра: мастерская, без расходников, любая погода
3. Написать 3 уровня текста, прогнать через anti-ai скилл
4. Положить SSML в `skills/salute-tts/narrations/`, запустить:

```bash
python3 skills/salute-tts/build_audio.py --poi 01
# Сам выберет: Salute Speech (если есть SALUTE_AUTH_DATA) или Edge TTS
```

## Быстрый старт

```bash
git clone https://github.com/MerkulovDaniil/tropa.git
cd tropa/bot

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp config/bot.example.yaml config/bot.yaml
# Заполните токены:
export TELEGRAM_BOT_TOKEN=...      # @BotFather
export OPENROUTER_API_KEY=...      # openrouter.ai (бесплатно)
export GROQ_API_KEY=...            # groq.com (бесплатно)

python scripts/bot.py --config config/bot.yaml
```

В Telegram: `/start` → поделиться Live Location → идти по маршруту.

| Команда | Что делает |
|---|---|
| `/start` | Запуск и инструкция |
| `/poi` | Список точек маршрута |
| `/here` | Рассказ про ближайшую точку |
| `/level2`, `/level3` | Формулы / байки |
| голосовое | Вопрос — ответ голосом |

## Стек

| Компонент | Технология | Стоимость |
|---|---|---|
| Бот | `python-telegram-bot` (async) | — |
| LLM | OpenRouter (авто-выбор free моделей) | $0 |
| TTS | Salute Speech / Edge TTS | $0 |
| STT | Groq Whisper Large v3 | $0 |
| Сайт | Статический HTML + KaTeX + Leaflet | — |

## Лицензия

MIT
