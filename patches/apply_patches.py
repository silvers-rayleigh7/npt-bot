#!/usr/bin/env python3
"""Применяет все правки tropa-bot поверх свежеустановленного claude-tg.

Идемпотентен: повторный запуск ничего не ломает. Запускать после
`uv tool install claude-tg` (или pip) — на любом сервере/аккаунте.

Правки:
  1. stream.py: статус «🎙 Обрабатываю…» вместо «Thinking…»
  2. bot.py _stream_turn: не стримить текст ответа; tool calls только при verbose;
     отслеживать отправку голоса (voice_sent); при неудаче — короткий сигнал, не текст-простыня.
  3. config.py: CLAUDE_TG_MAX_USERS (лимит авто-регистрации).
  4. bot.py: allowlist + авто-регистрация по /start + динамическая маршрутизация ответа
     в активный chat_id (несколько аккаунтов одного владельца).
  5. mcp_server.py: send_telegram_file шлёт в активный chat (data/current_chat.txt).
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
    c = c.replace(line, line + '\n        self.max_users: int = int(os.environ.get("CLAUDE_TG_MAX_USERS", "8"))')
    open(p, "w").write(c)


def patch_bot_multiaccount(base):
    p = os.path.join(base, "bot.py")
    b = open(p).read()
    if "def cmd_start" not in b:
        old_auth = '''    def _is_authorized(self, update: Update) -> bool:
        return update.effective_chat and update.effective_chat.id == self.config.chat_id'''
        new_auth = '''    def _is_authorized(self, update: Update) -> bool:
        chat = update.effective_chat
        if not chat:
            return False
        if chat.id in self._allowed_chats():
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
    open(p, "w").write(m)


def main():
    base = find_base()
    patch_stream(base)
    patch_bot_stream_turn(base)
    patch_config(base)
    patch_bot_multiaccount(base)
    patch_mcp(base)
    for f in ("bot.py", "stream.py", "config.py", "mcp_server.py"):
        ast.parse(open(os.path.join(base, f)).read())
    shutil.rmtree(os.path.join(base, "__pycache__"), ignore_errors=True)
    print(f"OK: все патчи применены к {base}")


if __name__ == "__main__":
    main()
