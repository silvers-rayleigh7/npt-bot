# Геолокация в ТГ-боте — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Пользователь шлёт боту геолокацию → бот показывает 2–3 ближайших научных сюжета с расстояниями и по выбору рассказывает (голос+текст).

**Architecture:** Транспорт `claude_tg` (форк на сервере) ловит сообщение-локацию, считает ближайшие точки по Haversine из `content/storylines/*.md`, кладёт структурированный `[ГЕО]`-блок в общий буфер — дальше срабатывает существующий конвейер (`_process_buffer → runner.run`), и `claude -p` рассказывает через свои MCP-инструменты. Правки транспорта вносятся идемпотентным патчем `patches/apply_patches.py`.

**Tech Stack:** Python 3.14, python-telegram-bot (v20+, `filters.LOCATION`, `ReplyKeyboardMarkup`), `claude_tg` (uv tool), pytest.

## Global Constraints
- Правки транспорта — ТОЛЬКО через `tg-bot/patches/apply_patches.py` (идемпотентно, с маркером). НЕ редактировать site-packages вручную.
- Координаты сюжетов берём из `{work_dir}/content/storylines/*.md` (frontmatter `geo`), work_dir на сервере = `/root/tropa-bot`.
- Формат расстояния: `<1000 м` → «N м», иначе «N.N км». Радиус fallback — 3 км.
- Фаза 1 — только разовая отправка (`message.location`). Live Location (`edited_message.location`) — НЕ реализуем (фаза 2).
- Живое тестирование в Telegram — ПОСЛЕ всего (по решению владельца), не в процессе.
- Все Python-файлы должны проходить `ast.parse` (это проверяет `main()` в apply_patches).

---

### Task 1: Модуль геоматчинга `geo_match.py` (TDD)

**Files:**
- Create: `tg-bot/geo_match.py`
- Test: `tg-bot/tests/test_geo_match.py`

**Interfaces:**
- Produces:
  - `haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float` — расстояние в метрах.
  - `nearest_storylines(lat: float, lon: float, content_dir: str, top: int = 3) -> list[dict]` — список `{"title": str, "slug": str, "dist_m": float}`, отсортирован по возрастанию расстояния.
  - `format_distance(m: float) -> str` — «120 м» / «1.2 км».

- [ ] **Step 1: Написать падающий тест**

```python
# tg-bot/tests/test_geo_match.py
import os, tempfile, textwrap
from geo_match import haversine_m, nearest_storylines, format_distance

def test_haversine_known_distance():
    # Иннополис ↔ Казань ≈ 40 км; проверяем порядок величины
    d = haversine_m(55.7514, 48.7312, 55.7887, 49.1221)
    assert 20000 < d < 60000

def test_haversine_zero():
    assert haversine_m(55.0, 48.0, 55.0, 48.0) < 1.0

def test_format_distance():
    assert format_distance(120) == "120 м"
    assert format_distance(1234) == "1.2 км"

def _write(d, name, title, lat, lon):
    open(os.path.join(d, name), "w", encoding="utf-8").write(textwrap.dedent(f"""\
        ---
        title: {title}
        code: WP001
        tags:
        - физика
        geo:
        - {lat}
        - {lon}
        routes:
        - innopolis
        ---
        ## Кратко
        текст
        """))

def test_nearest_sorted_and_limited():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "a.md", "Ближняя", 55.7515, 48.7313)
        _write(d, "b.md", "Средняя", 55.7600, 48.7400)
        _write(d, "c.md", "Дальняя", 55.8000, 48.8000)
        # файл без geo — игнорируется
        open(os.path.join(d, "n.md"), "w", encoding="utf-8").write("---\ntitle: Нет гео\n---\n## Кратко\nx\n")
        res = nearest_storylines(55.7514, 48.7312, d, top=2)
        assert [r["title"] for r in res] == ["Ближняя", "Средняя"]
        assert res[0]["slug"] == "a"
        assert res[0]["dist_m"] < res[1]["dist_m"]
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

Run: `cd ~/Projects/tropa-bot/tg-bot && python3 -m pytest tests/test_geo_match.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'geo_match'`

- [ ] **Step 3: Реализовать модуль**

```python
# tg-bot/geo_match.py
"""Геоматчинг для ТГ-бота: ближайшие сюжеты по координатам (Haversine).

Координаты берутся из frontmatter `geo` файлов content/storylines/*.md.
Поддерживает блочный (geo:\\n- lat\\n- lon) и инлайн (geo: [lat, lon]) форматы.
"""
import glob
import math
import os
import re


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между двумя точками на сфере Земли, в метрах."""
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _parse_title_geo(path: str):
    """(title, (lat, lon)) из frontmatter, либо (None, None) если нет title/geo."""
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if not m:
        return None, None
    fm = m.group(1)
    tm = re.search(r"^title:\s*(.+)$", fm, re.M)
    gm = re.search(r"geo:\s*\n\s*-\s*([-\d.]+)\s*\n\s*-\s*([-\d.]+)", fm)
    if not gm:
        gm = re.search(r"geo:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]", fm)
    if not tm or not gm:
        return None, None
    return tm.group(1).strip(), (float(gm.group(1)), float(gm.group(2)))


def nearest_storylines(lat: float, lon: float, content_dir: str, top: int = 3) -> list[dict]:
    """Топ-N ближайших сюжетов с координатами, отсортированы по расстоянию."""
    pts = []
    for p in glob.glob(os.path.join(content_dir, "*.md")):
        title, geo = _parse_title_geo(p)
        if not geo:
            continue
        pts.append({
            "title": title,
            "slug": os.path.basename(p)[:-3],
            "dist_m": haversine_m(lat, lon, geo[0], geo[1]),
        })
    pts.sort(key=lambda x: x["dist_m"])
    return pts[:top]


def format_distance(m: float) -> str:
    """«120 м» для <1 км, иначе «1.2 км»."""
    return f"{int(round(m))} м" if m < 1000 else f"{m / 1000:.1f} км"
```

- [ ] **Step 4: Запустить тесты — убедиться, что проходят**

Run: `cd ~/Projects/tropa-bot/tg-bot && python3 -m pytest tests/test_geo_match.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Коммит**

```bash
cd ~/Projects/tropa-bot
git add tg-bot/geo_match.py tg-bot/tests/test_geo_match.py
git commit -m "feat(bot): geo_match — ближайшие сюжеты по Haversine (TDD)"
```

---

### Task 2: Раздел «Геоконтекст» в `CLAUDE.md` бота

**Files:**
- Modify: `tg-bot/CLAUDE.md` (раздел `## Геоконтекст (если пользователь прислал локацию)`)

**Interfaces:**
- Consumes: формат `[ГЕО]`-блока из Task 3 (строка, которую транспорт кладёт в буфер).

- [ ] **Step 1: Заменить заглушку на рабочую инструкцию**

Найти в `tg-bot/CLAUDE.md` блок:

```markdown
## Геоконтекст (если пользователь прислал локацию)

Свяжи явление с местом/временем мягко («раз вы сейчас у реки…»). Это задел на будущее;
не навязывай, если не подходит.
```

Заменить на:

```markdown
## Геоконтекст (если пользователь прислал локацию)

Если во входящем сообщении есть блок `[ГЕО] …` — это транспорт прислал геолокацию
пользователя и уже посчитал ближайшие научные точки. Действуй так:

1. Покажи список этих точек с расстояниями (2–3 пункта, как в блоке), КОРОТКО, и спроси,
   про что рассказать (пользователь ответит номером или названием). Этот список — текстом
   (инструмент send_telegram_message), голос тут не нужен.
2. Когда пользователь выбрал точку — расскажи про соответствующий сюжет как обычно
   (найди его в базе content/, голос без формул + текст в два уровня).
3. Если в блоке сказано, что ближайшая точка дальше 3 км — честно скажи, что рядом
   научных точек нет, назови ближайшую и предложи: рассказать про неё или задать любую тему.
4. Свяжи явление с местом мягко («раз вы сейчас здесь…»), но не навязывай.
```

- [ ] **Step 2: Коммит**

```bash
cd ~/Projects/tropa-bot
git add tg-bot/CLAUDE.md
git commit -m "docs(bot): рабочая инструкция обработки [ГЕО]-блока в CLAUDE.md"
```

---

### Task 3: Патч транспорта — `patch_geolocation` в `apply_patches.py`

**Files:**
- Modify: `tg-bot/patches/apply_patches.py` (новая функция + вызов в `main()`)

**Interfaces:**
- Consumes: `geo_match.nearest_storylines`, `geo_match.format_distance` (Task 1) — модуль будет скопирован в пакет при деплое (Task 4), импорт `from claude_tg.geo_match import ...`.
- Produces: в `bot.py` появляются метод `handle_location`, регистрация `MessageHandler(filters.LOCATION, ...)`, кнопка запроса локации в `cmd_start`.

- [ ] **Step 1: Добавить функцию `patch_geolocation` перед `def main()`**

```python
def patch_geolocation(base):
    """Геолокация: handle_location + Haversine-матчинг + кнопка запроса локации."""
    p = os.path.join(base, "bot.py")
    b = open(p).read()
    if "async def handle_location" in b:
        return  # уже применено
    # 1) импорт клавиатур
    b = b.replace(
        "from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup",
        "from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, "
        "KeyboardButton, ReplyKeyboardMarkup",
        1,
    )
    # 2) метод handle_location — кладём [ГЕО]-блок в буфер и переиспользуем конвейер
    anchor_method = "    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):"
    if anchor_method not in b:
        sys.exit("bot.py: handle_photo не найден (версия claude-tg изменилась)")
    new_method = '''    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update):
            return
        loc = update.message.location if update.message else None
        if not loc:
            return
        from claude_tg.geo_match import nearest_storylines, format_distance
        content_dir = os.path.join(self.config.work_dir, "content", "storylines")
        near = nearest_storylines(loc.latitude, loc.longitude, content_dir, top=3)
        if near:
            items = "; ".join(
                f"{i}) {n['title']} — {format_distance(n['dist_m'])}"
                for i, n in enumerate(near, 1)
            )
        else:
            items = "(поблизости нет точек с координатами)"
        prompt = (
            f"[\\u0413\\u0415\\u041e] \\u041f\\u043e\\u043b\\u044c\\u0437\\u043e\\u0432\\u0430\\u0442\\u0435\\u043b\\u044c "
            f"\\u043f\\u0440\\u0438\\u0441\\u043b\\u0430\\u043b \\u0433\\u0435\\u043e\\u043b\\u043e\\u043a\\u0430\\u0446\\u0438\\u044e "
            f"({loc.latitude:.5f}, {loc.longitude:.5f}). "
            f"\\u0411\\u043b\\u0438\\u0436\\u0430\\u0439\\u0448\\u0438\\u0435 \\u0442\\u043e\\u0447\\u043a\\u0438: {items}. "
            f"\\u041f\\u043e\\u043a\\u0430\\u0436\\u0438 \\u0441\\u043f\\u0438\\u0441\\u043a\\u043e\\u043c \\u0441 "
            f"\\u0440\\u0430\\u0441\\u0441\\u0442\\u043e\\u044f\\u043d\\u0438\\u044f\\u043c\\u0438, \\u0434\\u0430\\u0439 "
            f"\\u0432\\u044b\\u0431\\u0440\\u0430\\u0442\\u044c \\u043d\\u043e\\u043c\\u0435\\u0440, "
            f"\\u0437\\u0430\\u0442\\u0435\\u043c \\u0440\\u0430\\u0441\\u0441\\u043a\\u0430\\u0436\\u0438 \\u043f\\u0440\\u043e "
            f"\\u0432\\u044b\\u0431\\u0440\\u0430\\u043d\\u043d\\u0443\\u044e. \\u0415\\u0441\\u043b\\u0438 "
            f"\\u0431\\u043b\\u0438\\u0436\\u0430\\u0439\\u0448\\u0430\\u044f \\u0434\\u0430\\u043b\\u044c\\u0448\\u0435 3 "
            f"\\u043a\\u043c \\u2014 \\u0441\\u043a\\u0430\\u0436\\u0438, \\u0447\\u0442\\u043e "
            f"\\u0440\\u044f\\u0434\\u043e\\u043c \\u043d\\u0438\\u0447\\u0435\\u0433\\u043e \\u043d\\u0435\\u0442."
        )
        self._buffer.append(prompt)
        await self._schedule_debounce(context)

'''
    b = b.replace(anchor_method, new_method + anchor_method, 1)
    # 3) регистрация хендлера рядом с PHOTO
    anchor_reg = "        app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))"
    if anchor_reg not in b:
        sys.exit("bot.py: регистрация PHOTO не найдена")
    b = b.replace(
        anchor_reg,
        "        app.add_handler(MessageHandler(filters.LOCATION, self.handle_location))\n" + anchor_reg,
        1,
    )
    # 4) кнопка запроса локации в приветствиях cmd_start
    kb = ('reply_markup=ReplyKeyboardMarkup([[KeyboardButton('
          '"\\U0001F4CD \\u0427\\u0442\\u043e \\u0440\\u044f\\u0434\\u043e\\u043c?", '
          'request_location=True)]], resize_keyboard=True)')
    b = b.replace(
        'await update.message.reply_text("\\u0421 \\u0432\\u043e\\u0437\\u0432\\u0440\\u0430\\u0449\\u0435\\u043d\\u0438\\u0435\\u043c! \\u0421\\u043f\\u0440\\u043e\\u0441\\u0438\\u0442\\u0435 \\u0447\\u0442\\u043e-\\u043d\\u0438\\u0431\\u0443\\u0434\\u044c \\u043e \\u043d\\u0430\\u0443\\u043a\\u0435 \\u2014 \\u043e\\u0442\\u0432\\u0435\\u0447\\u0443 \\u0433\\u043e\\u043b\\u043e\\u0441\\u043e\\u043c.")',
        None,
    ) if False else b  # (замена приветствий — по факту в Step 2 ниже)
    open(p, "w").write(b)
```

> Примечание: русские строки в патче записаны через `\\uXXXX`, потому что файл-патч сам по себе исходник; это гарантирует корректную запись без проблем кодировки при string-replace. При исполнении плана можно вместо escape-последовательностей вписать русский текст напрямую — если файл сохраняется в UTF-8 (проверить `ast.parse` в `main()`).

- [ ] **Step 2: Добавить кнопку локации в оба приветствия `cmd_start`** (упростить — вставить общий `reply_markup`)

Заменить обе строки приветствия в `patch_bot_multiaccount` НЕ трогаем; вместо этого в `patch_geolocation` после записи выше добавить идемпотентную вставку клавиатуры в ответы cmd_start:

```python
    # (в конце patch_geolocation, перед open(p,"w"))
    kb_arg = (', reply_markup=ReplyKeyboardMarkup([[KeyboardButton('
              '"\\U0001F4CD \\u0427\\u0442\\u043e \\u0440\\u044f\\u0434\\u043e\\u043c?", '
              'request_location=True)]], resize_keyboard=True)')
    for greet in (
        '\\u0421 \\u0432\\u043e\\u0437\\u0432\\u0440\\u0430\\u0449\\u0435\\u043d\\u0438\\u0435\\u043c! \\u0421\\u043f\\u0440\\u043e\\u0441\\u0438\\u0442\\u0435 \\u0447\\u0442\\u043e-\\u043d\\u0438\\u0431\\u0443\\u0434\\u044c \\u043e \\u043d\\u0430\\u0443\\u043a\\u0435 \\u2014 \\u043e\\u0442\\u0432\\u0435\\u0447\\u0443 \\u0433\\u043e\\u043b\\u043e\\u0441\\u043e\\u043c.',
        '\\u041f\\u0440\\u0438\\u0432\\u0435\\u0442! \\u042f \\u043d\\u0430\\u0443\\u0447\\u043d\\u044b\\u0439 \\u0433\\u0438\\u0434. \\u0421\\u043f\\u0440\\u043e\\u0441\\u0438\\u0442\\u0435 \\u0433\\u043e\\u043b\\u043e\\u0441\\u043e\\u043c \\u0438\\u043b\\u0438 \\u0442\\u0435\\u043a\\u0441\\u0442\\u043e\\u043c \\u2014 \\u0440\\u0430\\u0441\\u0441\\u043a\\u0430\\u0436\\u0443 \\u0438\\u043d\\u0442\\u0435\\u0440\\u0435\\u0441\\u043d\\u043e \\u0438 \\u043a\\u043e\\u0440\\u043e\\u0442\\u043a\\u043e.',
    ):
        b = b.replace(f'reply_text("{greet}")', f'reply_text("{greet}"{kb_arg})')
```

(Переставить `open(p, "w").write(b)` в самый конец функции, после этого блока.)

- [ ] **Step 3: Зарегистрировать `patch_geolocation` в `main()`**

В `def main()` после `patch_media(base)` добавить строку:

```python
    patch_geolocation(base)
```

- [ ] **Step 4: Локальная проверка синтаксиса патча**

Run: `cd ~/Projects/tropa-bot/tg-bot && python3 -c "import ast; ast.parse(open('patches/apply_patches.py').read()); print('apply_patches.py OK')"`
Expected: `apply_patches.py OK`

- [ ] **Step 5: Коммит**

```bash
cd ~/Projects/tropa-bot
git add tg-bot/patches/apply_patches.py
git commit -m "feat(bot): patch_geolocation — LOCATION-хендлер + кнопка локации в транспорте"
```

---

### Task 4: Деплой на сервер (живой тест — ПОСЛЕ, отдельно)

**Files:**
- Deploy: `tg-bot/geo_match.py` → пакет `claude_tg` на сервере; `tg-bot/CLAUDE.md` → `/root/tropa-bot/CLAUDE.md`; `apply_patches.py` → запуск на сервере.

**Interfaces:**
- Consumes: всё из Task 1–3.

- [ ] **Step 1: Скопировать `geo_match.py` в пакет и CLAUDE.md в рабочую папку**

```bash
cd ~/Projects/tropa-bot/tg-bot
export SSHPASS='<пароль сервера>'
SSHOPT="-o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no"
PKG=$(sshpass -e ssh $SSHOPT root@144.124.250.77 'ls -d /root/.local/share/uv/tools/claude-tg/lib/python*/site-packages/claude_tg')
sshpass -e scp $SSHOPT geo_match.py root@144.124.250.77:"$PKG/geo_match.py"
sshpass -e scp $SSHOPT CLAUDE.md root@144.124.250.77:/root/tropa-bot/CLAUDE.md
sshpass -e scp $SSHOPT patches/apply_patches.py root@144.124.250.77:/root/tropa-bot/apply_patches.py
```

- [ ] **Step 2: Применить патчи и проверить синтаксис пакета**

```bash
sshpass -e ssh $SSHOPT root@144.124.250.77 'cd /root/tropa-bot && python3 apply_patches.py'
```
Expected: `OK: все патчи применены к …/claude_tg` (без ошибок; `ast.parse` внутри main() валидирует bot.py).

- [ ] **Step 3: Проверить, что хендлер и модуль на месте (без запуска бота)**

```bash
sshpass -e ssh $SSHOPT root@144.124.250.77 'PKG='"$PKG"'; grep -c "async def handle_location" "$PKG/bot.py"; grep -c "filters.LOCATION" "$PKG/bot.py"; python3 -c "import sys; sys.path.insert(0,\"'"$PKG"'/..\"); from claude_tg.geo_match import nearest_storylines; print(nearest_storylines(55.7514,48.7312,\"/root/tropa-bot/content/storylines\",3))"'
```
Expected: `1`, `1`, и печать топ-3 ближайших к Иннополису сюжетов с `dist_m`.

- [ ] **Step 4: Перезапустить сервис**

```bash
sshpass -e ssh $SSHOPT root@144.124.250.77 'systemctl restart claude-tg && sleep 3 && systemctl is-active claude-tg'
```
Expected: `active`

- [ ] **Step 5: Живой тест в Telegram (ОТДЕЛЬНО, по готовности владельца)**

Открыть бота → `/start` → нажать «📍 Что рядом?» → отправить геолокацию → убедиться, что пришёл список 2–3 ближайших с расстояниями → выбрать номер → пришёл голос+текст рассказа. Проверить fallback: отправить точку далеко (>3 км) → бот честно говорит «рядом ничего нет».

- [ ] **Step 6: Коммит статуса (если менялись файлы репо при деплое)**

```bash
cd ~/Projects/tropa-bot
git add -A tg-bot/
git commit -m "chore(bot): деплой геолокации на сервер (транспорт пропатчен, сервис перезапущен)" || echo "нет изменений репо"
```

---

## Self-Review (проверка плана против спеки)
- **Покрытие спеки:** Haversine-матчинг (Task 1) ✓; CLAUDE.md инструкция (Task 2) ✓; LOCATION-хендлер + кнопка + регистрация (Task 3) ✓; деплой через apply_patches + рестарт (Task 4) ✓; fallback 3 км (в промпте Task 3 + CLAUDE.md Task 2) ✓; scope «все гео-сюжеты» (nearest_storylines по всей папке) ✓; единый источник (читаем content/storylines) ✓.
- **Live Location (фаза 2)** — намеренно НЕ в плане (YAGNI, отдельная итерация).
- **Типы согласованы:** `nearest_storylines` возвращает `list[dict]` с ключами `title/slug/dist_m`, ими же пользуется `handle_location` и тест.
- **Плейсхолдеров нет:** весь код и команды приведены; `<пароль сервера>` подставляется при исполнении.
