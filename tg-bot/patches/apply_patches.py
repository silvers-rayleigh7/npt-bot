#!/usr/bin/env python3
"""Применяет все правки tropa-bot поверх свежеустановленного claude-tg.

Идемпотентен: повторный запуск ничего не ломает. Запускать после
`uv tool install claude-tg` (или pip) — на любом сервере/аккаунте.

Правки:
  1. stream.py: статус «🎙 Обрабатываю…» вместо «Thinking…»
  2. bot.py _stream_turn: не стримить текст ответа; tool calls только при verbose;
     отслеживать отправку голоса (voice_sent); при неудаче — короткий сигнал, не текст-простыня.
  3. config.py: CLAUDE_TG_MAX_USERS (лимит авто-регистрации).
  4. bot.py: allowlist + авто-регистрация любым сообщением (пока лимит не исчерпан) + динамическая маршрутизация
     в активный chat_id (несколько аккаунтов одного владельца).
  5. mcp_server.py: send_telegram_file шлёт в активный chat (data/current_chat.txt).
  6. mcp_server.py: новый инструмент send_telegram_message — текст (формула) вдогонку к голосу.
  7. media.py: Groq STT language=ru + научный prompt.
"""
import ast
import glob
import os
import shutil
import sys


def find_base() -> str:
    home = os.path.expanduser("~")
    patterns = [
        f"{home}/.local/share/uv/tools/claude-tg/lib/python*/site-packages/claude_tg",
        f"{home}/.local/lib/python*/site-packages/claude_tg",
        "/usr/lib/python*/site-packages/claude_tg",
        "/usr/local/lib/python*/site-packages/claude_tg",
    ]
    for pat in patterns:
        hits = glob.glob(pat)
        if hits:
            return hits[0]
    sys.exit("claude_tg не найден — установи claude-tg сначала")


def patch_stream(base):
    p = os.path.join(base, "stream.py")
    s = open(p).read()
    s = s.replace("⏳ Thinking...", "🎙 Обрабатываю…").replace("⏳ ...", "🎙 Обрабатываю…")
    open(p, "w").write(s)


def patch_bot_stream_turn(base):
    p = os.path.join(base, "bot.py")
    b = open(p).read()
    if "voice_sent = False" in b:
        return  # уже применено
    old = '''    async def _stream_turn(self, events, stream) -> bool:
        """Stream events from a single turn to Telegram. Returns True if RESULT received."""
        response_text = []
        async for event in events:
            if event.type == EventType.TEXT_DELTA:
                response_text.append(event.text)
            elif event.type == EventType.TOOL_USE:
                if self.config.verbose:
                    line = format_tool_call(event.tool_name, event.tool_input)
                    await stream.push_tool_call(line)
            elif event.type == EventType.TOOL_RESULT and self.config.verbose:
                html = format_tool_result(event.text)
                await stream.push_tool_result(html)
            elif event.type == EventType.RESULT:
                self._session_cost += event.cost_usd
                duration = event.duration_ms // 1000
                footer = f"⏱ {duration}s · {event.num_turns} turns"
                await stream.finalize(footer=footer)
                self.conversation_log.log_assistant("".join(response_text))
                return True
        # EOF without RESULT — process died
        self.conversation_log.log_assistant("".join(response_text))
        return False'''
    # Если оригинал уже частично пропатчен (push_text убран вручную) — пробуем мягкий вариант
    new = '''    async def _stream_turn(self, events, stream) -> bool:
        """Stream events from a single turn to Telegram. Returns True if RESULT received."""
        response_text = []
        voice_sent = False
        async for event in events:
            if event.type == EventType.TEXT_DELTA:
                response_text.append(event.text)
            elif event.type == EventType.TOOL_USE:
                if "send_telegram_file" in (event.tool_name or ""):
                    voice_sent = True
                if self.config.verbose:
                    line = format_tool_call(event.tool_name, event.tool_input)
                    await stream.push_tool_call(line)
            elif event.type == EventType.TOOL_RESULT and self.config.verbose:
                html = format_tool_result(event.text)
                await stream.push_tool_result(html)
            elif event.type == EventType.RESULT:
                self._session_cost += event.cost_usd
                duration = event.duration_ms // 1000
                footer = f"⏱ {duration}s · {event.num_turns} turns"
                fallback = "".join(response_text).strip()
                if not voice_sent and fallback:
                    await stream.push_text("🎙 Не удалось озвучить ответ. Пожалуйста, переспросите.")
                    await stream.finalize(footer=footer)
                else:
                    await stream.finalize()
                self.conversation_log.log_assistant("".join(response_text))
                return True
        # EOF without RESULT — process died
        fallback = "".join(response_text).strip()
        if not voice_sent and fallback:
            await stream.push_text("🎙 Не удалось озвучить ответ. Пожалуйста, переспросите.")
        self.conversation_log.log_assistant("".join(response_text))
        return False'''
    if old not in b:
        sys.exit("bot.py _stream_turn: оригинал не найден (версия claude-tg изменилась — обнови патч)")
    open(p, "w").write(b.replace(old, new))


def patch_config(base):
    p = os.path.join(base, "config.py")
    c = open(p).read()
    if "max_users" in c:
        return
    line = '        self.chat_id: int = int(os.environ.get("TELEGRAM_CHAT_ID", "0"))'
    if line not in c:
        sys.exit("config.py: chat_id строка не найдена")
    c = c.replace(line, line + '\n        self.max_users: int = int(os.environ.get("CLAUDE_TG_MAX_USERS", "30"))')
    open(p, "w").write(c)


def patch_bot_multiaccount(base):
    p = os.path.join(base, "bot.py")
    b = open(p).read()
    if "import json" not in b[:1500]:  # allowlist использует json — в PyPI-версии импорта нет
        b = b.replace("import os\n", "import os\nimport json\n", 1)
    if "def cmd_start" not in b:
        old_auth = '''    def _is_authorized(self, update: Update) -> bool:
        return update.effective_chat and update.effective_chat.id == self.config.chat_id'''
        new_auth = '''    def _is_authorized(self, update: Update) -> bool:
        chat = update.effective_chat
        if not chat:
            return False
        allowed = self._load_allowed()
        if chat.id in allowed:
            self._set_active(chat.id)
            return True
        limit = self.config.max_users
        if limit == 0 or len(allowed) < limit:
            allowed.add(chat.id)
            self._save_allowed(allowed)
            self._set_active(chat.id)
            return True
        return False

    def _allowed_path(self) -> str:
        return os.path.join(self.config.work_dir, "data", "allowed_chats.json")

    def _load_allowed(self) -> set:
        ids = {self.config.chat_id}
        p = self._allowed_path()
        if os.path.isfile(p):
            try:
                ids |= {int(x) for x in json.load(open(p))}
            except Exception:
                pass
        return ids

    def _save_allowed(self, ids: set):
        os.makedirs(os.path.dirname(self._allowed_path()), exist_ok=True)
        json.dump(sorted(ids), open(self._allowed_path(), "w"))

    def _allowed_chats(self) -> set:
        return self._load_allowed()

    def _set_active(self, chat_id: int):
        self._active_chat_id = chat_id
        try:
            d = os.path.join(self.config.work_dir, "data")
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "current_chat.txt"), "w").write(str(chat_id))
        except Exception:
            pass

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if not chat:
            return
        cid = chat.id
        allowed = self._load_allowed()
        if cid in allowed:
            self._set_active(cid)
            await update.message.reply_text("С возвращением! Спросите что-нибудь о науке — отвечу голосом.")
            return
        limit = self.config.max_users
        if limit == 0 or len(allowed) < limit:
            allowed.add(cid)
            self._save_allowed(allowed)
            self._set_active(cid)
            await update.message.reply_text("Привет! Я научный гид. Спросите голосом или текстом — расскажу интересно и коротко.")
        else:
            await update.message.reply_text("Извините, доступ сейчас ограничен.")'''
        if old_auth not in b:
            sys.exit("bot.py _is_authorized не найден")
        b = b.replace(old_auth, new_auth)
    # динамический chat_id отправки
    b = b.replace("chat_id=self.config.chat_id,",
                  'chat_id=getattr(self, "_active_chat_id", self.config.chat_id),')
    # /start handler
    if 'CommandHandler("start"' not in b:
        h = '        app.add_handler(CommandHandler("clear", self.cmd_clear))'
        if h not in b:
            sys.exit("bot.py clear-handler не найден")
        b = b.replace(h, '        app.add_handler(CommandHandler("start", self.cmd_start))\n' + h)
    open(p, "w").write(b)


def patch_mcp(base):
    p = os.path.join(base, "mcp_server.py")
    m = open(p).read()
    if "_current_chat_id" in m:
        return
    helper = '''mcp = FastMCP("claude-tg")


def _current_chat_id():
    p = os.path.join(os.environ.get("CLAUDE_WORK_DIR", os.getcwd()), "data", "current_chat.txt")
    try:
        return open(p).read().strip() or os.environ.get("TELEGRAM_CHAT_ID")
    except Exception:
        return os.environ.get("TELEGRAM_CHAT_ID")'''
    m = m.replace('mcp = FastMCP("claude-tg")', helper, 1)
    m = m.replace('    chat_id = os.environ.get("TELEGRAM_CHAT_ID")', '    chat_id = _current_chat_id()', 1)
    # voice-маршрутизация: PyPI-версия шлёт всё документом → .ogg должен идти как send_voice
    if "send_voice" not in m:
        old_send = '''    bot = Bot(token=token)
    async with bot:
        with path.open("rb") as f:
            await bot.send_document(
                chat_id=int(chat_id),
                document=f,
                filename=path.name,
                caption=caption or None,
            )'''
        new_send = '''    ext = path.suffix.lower()
    bot = Bot(token=token)
    async with bot:
        with path.open("rb") as f:
            if ext in {".ogg", ".oga", ".opus"}:
                try:
                    await bot.send_voice(chat_id=int(chat_id), voice=f, caption=caption or None)
                except Exception:
                    f.seek(0)
                    await bot.send_audio(chat_id=int(chat_id), audio=f, caption=caption or None)
            elif ext in {".mp3", ".m4a", ".aac", ".flac", ".wav"}:
                await bot.send_audio(chat_id=int(chat_id), audio=f, caption=caption or None)
            else:
                await bot.send_document(
                    chat_id=int(chat_id),
                    document=f,
                    filename=path.name,
                    caption=caption or None,
                )'''
        if old_send in m:
            m = m.replace(old_send, new_send)
    open(p, "w").write(m)


def patch_mcp_sendmsg(base):
    """MCP-инструмент send_telegram_message — текст (два уровня + формулы) вдогонку к голосу.

    Версия с чисткой markdown: убирает * ` # и длинные тире — / –, чтобы пользователь
    видел чистый текст (Telegram без parse_mode разметку не рендерит).

    Идемпотентно по маркеру `_clean_tg_text`. Если на сервере осталась старая версия
    инструмента (без чистки) — заменяет её на новую; если инструмента не было — вставляет
    после `mcp = FastMCP("claude-tg")` (первая строка helper-блока из patch_mcp)."""
    p = os.path.join(base, "mcp_server.py")
    m = open(p).read()
    if "_clean_tg_text" in m:
        return  # уже новая версия с чисткой

    new_tool = '''@mcp.tool()
async def send_telegram_message(text: str) -> str:
    """Отправить текстовое сообщение (два уровня + формулы) в активный чат Telegram.

    Голос идёт без формул; текст и формулы уходят сюда. Чистит markdown и длинные тире,
    чтобы пользователь не видел символы * ` # и — / –.
    """
    import os as _os
    from telegram import Bot as _Bot

    def _clean_tg_text(t):
        for a, b in (("\\u2014", "-"), ("\\u2013", "-"), ("*", ""), ("`", ""), ("#", "")):
            t = t.replace(a, b)
        return t.strip()

    token = _os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = _current_chat_id()
    if not token or not chat_id:
        return "error: no token or chat_id"
    bot = _Bot(token=token)
    async with bot:
        await bot.send_message(chat_id=int(chat_id), text=_clean_tg_text(text))
    return "sent"'''

    old_tool = '''@mcp.tool()
async def send_telegram_message(text: str) -> str:
    """Отправить текстовое сообщение (например, формулу) в активный чат Telegram.

    Дополнение к голосовому ответу: голос идёт без формул, а формула — этим текстом.
    """
    import os as _os
    from telegram import Bot as _Bot
    token = _os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = _current_chat_id()
    if not token or not chat_id:
        return "error: no token or chat_id"
    bot = _Bot(token=token)
    async with bot:
        await bot.send_message(chat_id=int(chat_id), text=text)
    return "sent"'''

    if old_tool in m:
        open(p, "w").write(m.replace(old_tool, new_tool, 1))
        return

    anchor = 'mcp = FastMCP("claude-tg")'
    if anchor not in m:
        sys.exit("mcp_server.py: anchor `mcp = FastMCP` не найден (запусти patch_mcp раньше)")
    open(p, "w").write(m.replace(anchor, anchor + "\n\n\n" + new_tool, 1))


def patch_media(base):
    """Groq STT: явный русский язык + научный prompt → точнее распознаёт термины."""
    p = os.path.join(base, "media.py")
    m = open(p).read()
    if 'language="ru"' in m:
        return
    marker = 'model="whisper-large-v3",'
    if marker not in m:
        return
    add = (marker
           + '\n                language="ru",'
           + '\n                prompt="Научно-популярный вопрос о физике, астрономии, '
             'химии, биологии, экологии. Термины: рассеяние, гравитация, спектр, '
             'молекула, энергия, частота, орбита, давление.",')
    open(p, "w").write(m.replace(marker, add, 1))


def patch_geolocation(base):
    """Геолокация: handle_location + Haversine-матчинг + кнопка запроса локации.

    Идемпотентно по маркеру `async def handle_location`. Требует, чтобы рядом с bot.py
    лежал модуль geo_match.py (деплоится отдельно). Запускать ПОСЛЕ patch_bot_multiaccount
    (нужны приветствия cmd_start)."""
    p = os.path.join(base, "bot.py")
    b = open(p).read()
    if "async def handle_location" in b:
        return

    # 1) импорт клавиатур
    b = b.replace(
        "from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup",
        "from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, "
        "KeyboardButton, ReplyKeyboardMarkup",
        1,
    )

    # 2) метод handle_location — кладёт [ГЕО]-блок в общий буфер, конвейер переиспользуется
    anchor = "    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):"
    if anchor not in b:
        sys.exit("bot.py: handle_photo не найден (версия claude-tg изменилась)")
    method = (
        "    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):\n"
        "        if not self._is_authorized(update):\n"
        "            return\n"
        "        loc = update.message.location if update.message else None\n"
        "        if not loc:\n"
        "            return\n"
        "        from claude_tg.geo_match import nearest_storylines, format_distance\n"
        "        content_dir = os.path.join(self.config.work_dir, \"content\", \"storylines\")\n"
        "        near = nearest_storylines(loc.latitude, loc.longitude, content_dir, top=3)\n"
        "        if near:\n"
        "            items = \"; \".join(\n"
        "                f\"{i}) {n['title']} — {format_distance(n['dist_m'])}\"\n"
        "                for i, n in enumerate(near, 1)\n"
        "            )\n"
        "        else:\n"
        "            items = \"(поблизости нет точек с координатами)\"\n"
        "        prompt = (\n"
        "            f\"[ГЕО] Пользователь прислал геолокацию ({loc.latitude:.5f}, {loc.longitude:.5f}). \"\n"
        "            f\"Ближайшие точки: {items}. Покажи их списком с расстояниями, дай выбрать номер, \"\n"
        "            f\"затем расскажи про выбранную. Если ближайшая дальше 3 км — честно скажи, \"\n"
        "            f\"что рядом научных точек нет, назови ближайшую и предложи рассказать про неё \"\n"
        "            f\"или задать любую тему.\"\n"
        "        )\n"
        "        self._buffer.append(prompt)\n"
        "        await self._schedule_debounce(context)\n\n"
        "    async def cmd_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):\n"
        "        if not self._is_authorized(update):\n"
        "            return\n"
        "        await update.message.reply_text(\n"
        "            \"Пришли геолокацию — расскажу, что рядом и про тропу.\\n\"\n"
        "            \"📱 На телефоне: нажми кнопку «📍 Что рядом?» ниже.\\n\"\n"
        "            \"💻 На компьютере: 📎 (скрепка) → Геопозиция → выбери точку.\",\n"
        "            reply_markup=ReplyKeyboardMarkup(\n"
        "                [[KeyboardButton(\"📍 Что рядом?\", request_location=True)]],\n"
        "                resize_keyboard=True,\n"
        "            ),\n"
        "        )\n\n"
    )
    b = b.replace(anchor, method + anchor, 1)

    # 3) регистрация LOCATION-хендлера рядом с PHOTO
    reg = "        app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))"
    if reg not in b:
        sys.exit("bot.py: регистрация PHOTO не найдена")
    b = b.replace(
        reg,
        "        app.add_handler(MessageHandler(filters.LOCATION, self.handle_location))\n" + reg,
        1,
    )

    # 3b) команда /location
    creg = '        app.add_handler(CommandHandler("clear", self.cmd_clear))'
    if creg not in b:
        sys.exit("bot.py: регистрация clear-команды не найдена")
    b = b.replace(
        creg,
        creg + '\n        app.add_handler(CommandHandler("location", self.cmd_location))',
        1,
    )

    # 4) кнопка «📍 Что рядом?» (request_location) в приветствиях cmd_start
    kb = (', reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📍 Что рядом?", '
          'request_location=True)]], resize_keyboard=True)')
    for greet in (
        "С возвращением! Спросите что-нибудь о науке — отвечу голосом.",
        "Привет! Я научный гид. Спросите голосом или текстом — расскажу интересно и коротко.",
    ):
        b = b.replace(f'reply_text("{greet}")', f'reply_text("{greet}"{kb})')

    open(p, "w").write(b)


def patch_geo_text_ok(base):
    """Не показывать «не удалось озвучить», если ответ ушёл текстом (send_telegram_message).

    Для гео-ответов (список ближайших) бот отвечает текстом, а не голосом — но страховка
    _stream_turn считала это провалом озвучки и пугала пользователя. Учитываем text-ответ."""
    p = os.path.join(base, "bot.py")
    b = open(p).read()
    if "msg_sent = False" in b:
        return
    if "voice_sent = False" not in b:
        return  # _stream_turn не пропатчен — нечего чинить
    b = b.replace("        voice_sent = False\n",
                  "        voice_sent = False\n        msg_sent = False\n", 1)
    b = b.replace(
        '                if "send_telegram_file" in (event.tool_name or ""):\n'
        '                    voice_sent = True\n',
        '                if "send_telegram_file" in (event.tool_name or ""):\n'
        '                    voice_sent = True\n'
        '                if "send_telegram_message" in (event.tool_name or ""):\n'
        '                    msg_sent = True\n',
        1,
    )
    b = b.replace("if not voice_sent and fallback:",
                  "if not voice_sent and not msg_sent and fallback:")
    open(p, "w").write(b)


def main():
    base = find_base()
    patch_stream(base)
    patch_bot_stream_turn(base)
    patch_config(base)
    patch_bot_multiaccount(base)
    patch_mcp(base)
    patch_mcp_sendmsg(base)
    patch_media(base)
    patch_geolocation(base)
    patch_geo_text_ok(base)
    for f in ("bot.py", "stream.py", "config.py", "mcp_server.py", "media.py"):
        ast.parse(open(os.path.join(base, f)).read())
    shutil.rmtree(os.path.join(base, "__pycache__"), ignore_errors=True)
    print(f"OK: все патчи применены к {base}")


if __name__ == "__main__":
    main()
