"""TG-бот «Научный Гид»: live location + голосовые ответы в стиле Гасникова.

Запуск из каталога bot/:
    python scripts/bot.py --config config/bot.yaml

Зависимости:
    pip install python-telegram-bot[ext] openai pyyaml torch torchaudio edge-tts
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import urllib.request
from pathlib import Path

import yaml
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from narrate import Narrator
from poi_match import POIMatcher, haversine_m, load_poi
from stt import GroqSTT
from tts import make_tts

log = logging.getLogger("cnpt_bot")

NARRATIVE_KEYS = ("title_intriguing", "title_scientific", "L1", "L2", "L3", "narration_short")


def expand_env(obj):
    """Рекурсивно подменяет ${VAR} → os.environ[VAR]."""
    if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        return os.environ.get(obj[2:-1], "")
    if isinstance(obj, dict):
        return {k: expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_env(v) for v in obj]
    return obj


def load_config(path: str | Path) -> dict:
    config_path = Path(path).expanduser().resolve()
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = expand_env(yaml.safe_load(f))
    cfg["_config_dir"] = str(config_path.parent)
    return cfg


def resolve_path(cfg: dict, value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (Path(cfg["_config_dir"]) / path).resolve()


def resolve_llm_models(llm_cfg: dict) -> tuple[str, list[str]]:
    source_url = llm_cfg.get("model_source_url")
    if source_url:
        request = urllib.request.Request(
            source_url,
            headers={"User-Agent": "tropa-bot/1.0"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        models = [item["id"] for item in data.get("models", []) if item.get("id")]
        if not models:
            raise RuntimeError(f"No models in {source_url}")
        fallback = data.get("fallback", {}).get("id")
        fallbacks = models[1:3]
        if fallback and fallback not in fallbacks:
            fallbacks.append(fallback)
        log.info("selected OpenRouter model from %s: %s", source_url, models[0])
        return models[0], fallbacks
    return llm_cfg.get("model", "openrouter/free"), llm_cfg.get("fallback_models") or []


class BotApp:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.allowed = set(cfg["telegram"].get("allowed_users") or [])
        self.log_dir = resolve_path(cfg, cfg["logging"]["dir"])
        poi_file = resolve_path(cfg, cfg["scenarios"]["poi_file"])
        style_file = resolve_path(cfg, cfg["scenarios"]["style_file"])
        tts_cfg = dict(cfg["tts"])
        tts_cfg["silero"] = dict(tts_cfg.get("silero", {}))
        if "cache_dir" in tts_cfg["silero"]:
            tts_cfg["silero"]["cache_dir"] = str(resolve_path(cfg, tts_cfg["silero"]["cache_dir"]))
        self.poi_matcher = POIMatcher(
            poi=load_poi(poi_file),
            default_radius_m=cfg["location"]["default_trigger_radius_m"],
            cooldown_s=cfg["location"]["cooldown_seconds"],
            hysteresis_m=cfg["location"]["hysteresis_m"],
            state_path=self.log_dir / "poi_state.json",
        )
        self.narrator = Narrator(
            api_key=cfg["llm"]["api_key"],
            model=cfg["llm"]["model"],
            style_file=style_file,
            max_tokens=cfg["llm"].get("max_tokens", 2000),
            temperature=cfg["llm"].get("temperature", 0.4),
            base_url=cfg["llm"].get("base_url", "https://openrouter.ai/api/v1"),
            fallback_models=cfg["llm"].get("fallback_models") or ["openrouter/free"],
            app_title=cfg["llm"].get("app_title", "Innopolis Science Trail"),
            site_url=cfg["llm"].get("site_url"),
            timeout_seconds=cfg["llm"].get("timeout_seconds", 25),
        )
        self.tts = make_tts(tts_cfg)
        self.stt = GroqSTT(
            api_key=cfg["stt"]["api_key"],
            model=cfg["stt"]["model"],
            language=cfg["stt"]["language"],
        )
        self.min_accuracy = cfg["location"]["min_accuracy_m"]
        self.here_max_distance = cfg["location"].get("here_max_distance_m", 400)
        self.voice_answer_timeout = cfg["llm"].get("voice_answer_timeout_seconds", 7)
        self.narrative_cache: dict[str, dict] = {}

    def _allowed(self, user_id: int) -> bool:
        return not self.allowed or user_id in self.allowed

    def _route_context(self, poi: dict) -> dict:
        items = self.poi_matcher.poi
        for idx, current in enumerate(items):
            if current["id"] != poi["id"]:
                continue
            if idx + 1 >= len(items):
                return {}
            next_poi = items[idx + 1]
            return {
                "next_poi": next_poi["name"],
                "next_distance_m": round(
                    haversine_m(poi["lat"], poi["lon"], next_poi["lat"], next_poi["lon"])
                ),
            }
        return {}

    def _cached_narrative(self, poi: dict) -> dict:
        poi_id = poi["id"]
        if poi_id not in self.narrative_cache:
            if not self.cfg["llm"].get("generate_poi_narratives", False):
                self.narrative_cache[poi_id] = self._fallback_narrative(poi)
                return self.narrative_cache[poi_id]
            try:
                narrative = self.narrator.narrate(poi, self._route_context(poi))
                missing = [key for key in NARRATIVE_KEYS if not narrative.get(key)]
                if missing:
                    raise ValueError(f"invalid narrative, missing {missing}")
            except Exception:
                log.exception("LLM narrative failed for poi=%s; using YAML fallback", poi_id)
                narrative = self._fallback_narrative(poi)
            self.narrative_cache[poi_id] = narrative
        return self.narrative_cache[poi_id]

    def _fallback_narrative(self, poi: dict) -> dict:
        sources = poi.get("sources") or []
        source_text = "; ".join(sources[:2]) if sources else "источник будет добавлен после фактчека"
        l1 = poi.get("level1_seed") or poi["topic"]
        l2 = poi.get("level2_seed") or poi.get("scenario_brief") or poi["topic"]
        l3 = (
            f"Эксперт для проверки: {poi.get('expert', 'TBD')}. "
            f"Источники: {source_text}."
        )
        return {
            "title_intriguing": poi["topic"],
            "title_scientific": poi["topic"],
            "L1": l1,
            "L2": l2,
            "L3": l3,
            "narration_short": l1,
        }

    def _speechify(self, text: str) -> str:
        replacements = {
            "≈": " примерно ",
            "·": " умножить на ",
            "→": " приводит к ",
            "≥": " больше или равно ",
            "≤": " меньше или равно ",
            "μ": " мю ",
            "ρ": " ро ",
            "Δ": " дельта ",
            "⁻": " в минус ",
            "³": " третьей ",
            "²": " второй ",
            "_rail": " для рельса ",
            "_road": " для дороги ",
            "vs": " против ",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return " ".join(text.split())

    def _last_location(self, ctx: ContextTypes.DEFAULT_TYPE) -> tuple[float, float] | None:
        loc = ctx.user_data.get("last_location")
        if not loc:
            return None
        return loc["lat"], loc["lon"]

    def _nearest_from_context(
        self, ctx: ContextTypes.DEFAULT_TYPE, limit: int = 1
    ) -> list[dict]:
        last = self._last_location(ctx)
        if not last:
            return []
        return self.poi_matcher.nearest(last[0], last[1], limit=limit)

    # ----- handlers -----

    async def start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Привет! Я научный гид.\n\n"
            "Включи Live Location (📎 → Location → Share Live Location) "
            "и иди по маршруту. Я буду присылать голосовые рассказы, "
            "когда ты будешь рядом с интересными местами.\n\n"
            "Команды:\n"
            "/poi — список точек\n"
            "/here — рассказать про ближайшую точку\n"
            "/level2 <poi_id> — углублённая версия с формулами\n"
            "/level3 <poi_id> — доп. факты и связки\n"
            "/sources <poi_id> — источники сюжета\n\n"
            "Live Location расходует батарею. Для полевого теста лучше иметь запас зарядки."
        )

    async def poi_list(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        lines = ["📍 Точки маршрута:"]
        for p in self.poi_matcher.poi:
            lines.append(f"• `{p['id']}` — {p['name']}: {p['topic']}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    async def here(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        nearest = self._nearest_from_context(ctx, limit=1)
        if not nearest:
            await update.message.reply_text(
                "Пришли геолокацию или включи Live Location, и я найду ближайшую точку."
            )
            return
        poi = nearest[0]
        if poi["distance_m"] > self.here_max_distance:
            await update.message.reply_text(
                f"Ближайшая точка — {poi['name']} примерно в {poi['distance_m']:.0f} м. "
                "Подойди ближе или увеличь here_max_distance_m в конфиге."
            )
            return
        await self._deliver_poi(update.message, poi)

    async def level2(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._send_level(update, ctx, "L2", "title_scientific")

    async def level3(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._send_level(update, ctx, "L3", "title_intriguing")

    async def sources(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        poi = await self._poi_from_args_or_nearest(update, ctx)
        if not poi:
            return
        sources = poi.get("sources") or []
        if not sources:
            await update.message.reply_text(f"Для `{poi['id']}` источники пока не указаны.", parse_mode="Markdown")
            return
        lines = [f"Источники для {poi['name']}:"]
        lines.extend(f"• {source}" for source in sources)
        await update.message.reply_text("\n".join(lines))

    async def location(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = update.edited_message or update.message
        if not msg or not msg.location:
            return
        user_id = msg.from_user.id
        if not self._allowed(user_id):
            return
        loc = msg.location
        acc = float(loc.horizontal_accuracy or 0.0)
        if acc and acc > self.min_accuracy:
            log.info("skip low-accuracy location: %.0fm", acc)
            return
        ctx.user_data["last_location"] = {"lat": loc.latitude, "lon": loc.longitude}
        hit = self.poi_matcher.step(user_id, loc.latitude, loc.longitude, acc)
        if hit:
            log.info("poi hit user=%s poi=%s distance=%.1fm", user_id, hit["id"], hit["distance_m"])
            await self._deliver_poi(msg, hit)

    async def voice(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Принимаем голосовое — STT → reply."""
        msg = update.message
        try:
            f = await msg.voice.get_file()
            tmp = self.log_dir / f"in_{msg.message_id}.ogg"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            await f.download_to_drive(str(tmp))
            text = await asyncio.to_thread(self.stt.transcribe, tmp)
        except Exception:
            log.exception("voice STT failed")
            await msg.reply_text(
                "Не смог распознать голос. Я уже залогировал ошибку; попробуй ещё раз "
                "или напиши вопрос текстом."
            )
            return
        nearest = self._nearest_from_context(ctx, limit=1)
        if not nearest:
            await msg.reply_text(
                f"🎤 Распознано: _{text}_\n\n"
                "Чтобы ответ был привязан к месту, пришли геолокацию или включи Live Location.",
                parse_mode="Markdown",
            )
            return
        poi = nearest[0]
        await msg.chat.send_action(ChatAction.RECORD_VOICE)
        try:
            answer = await asyncio.wait_for(
                asyncio.to_thread(
                    self.narrator.answer_question, poi, text, self._route_context(poi)
                ),
                timeout=self.voice_answer_timeout,
            )
        except asyncio.TimeoutError:
            log.warning("voice answer timeout for poi=%s", poi["id"])
            answer = self._voice_fallback_answer(poi, text)
        except Exception:
            log.exception("voice answer failed for poi=%s", poi["id"])
            answer = self._voice_fallback_answer(poi, text)
        await self._send_voice_or_text(msg, answer, f"🎤 {text}\n\n📍 {poi['name']}\n{answer}")

    def _voice_fallback_answer(self, poi: dict, question: str) -> str:
        narrative = self._cached_narrative(poi)
        return (
            f"Я распознал вопрос: {question}. "
            f"Быстрый ответ у этой точки: {narrative['L1']} "
            f"Если хочешь глубже по теме, нажми /level2 {poi['id']}."
        )

    async def _deliver_poi(self, msg, poi: dict):
        try:
            await msg.chat.send_action(ChatAction.RECORD_VOICE)
            narrative = await asyncio.to_thread(self._cached_narrative, poi)
            caption = (
                f"📍 {poi['name']}\n"
                f"{narrative['title_intriguing']}\n\n"
                f"{narrative['L1']}\n\n"
                f"Хочешь глубже? /level2 {poi['id']}"
            )
            await self._send_voice_or_text(msg, self._speechify(narrative["narration_short"]), caption)
            self._log_narrative(msg.from_user.id, poi["id"], narrative)
        except Exception:
            log.exception("deliver poi failed poi=%s", poi.get("id"))
            await msg.reply_text(
                f"Рядом точка: {poi['name']}.\n\n"
                f"{poi.get('level1_seed') or poi['topic']}\n\n"
                f"Глубже: /level2 {poi['id']}"
            )

    async def _send_voice_or_text(self, msg, voice_text: str, caption: str):
        try:
            audio = await asyncio.to_thread(self.tts.synth, voice_text)
        except Exception:
            log.exception("TTS failed; falling back to text")
            await msg.reply_text(caption[:4096])
            return

        if audio.suffix.lower() != ".ogg":
            try:
                with open(audio, "rb") as fh:
                    await msg.reply_audio(audio=fh, caption=caption[:1024])
            except Exception:
                log.exception("audio send failed; falling back to text")
                await msg.reply_text(caption[:4096])
            return

        try:
            with open(audio, "rb") as fh:
                await msg.reply_voice(voice=fh, caption=caption[:1024])
        except Exception:
            log.exception("voice send failed; trying audio")
            try:
                with open(audio, "rb") as fh:
                    await msg.reply_audio(audio=fh, caption=caption[:1024])
            except Exception:
                log.exception("audio send failed; falling back to text")
                await msg.reply_text(caption[:4096])

    def _log_narrative(self, user_id: int, poi_id: str, narrative: dict):
        log_dir = self.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"narratives_{user_id}.jsonl"
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write(json.dumps({"poi_id": poi_id, "narrative": narrative}, ensure_ascii=False) + "\n")

    async def _poi_from_args_or_nearest(
        self, update: Update, ctx: ContextTypes.DEFAULT_TYPE
    ) -> dict | None:
        if ctx.args:
            poi = self.poi_matcher.by_id(ctx.args[0])
            if poi:
                return poi
            await update.message.reply_text(
                f"Не знаю точку `{ctx.args[0]}`. Посмотри /poi.",
                parse_mode="Markdown",
            )
            return None
        nearest = self._nearest_from_context(ctx, limit=1)
        if nearest:
            return nearest[0]
        await update.message.reply_text(
            "Укажи poi_id: например `/level2 university_entrance`.",
            parse_mode="Markdown",
        )
        return None

    async def _send_level(
        self,
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        level_key: str,
        title_key: str,
    ):
        poi = await self._poi_from_args_or_nearest(update, ctx)
        if not poi:
            return
        await update.message.chat.send_action(ChatAction.RECORD_VOICE)
        narrative = await asyncio.to_thread(self._cached_narrative, poi)
        text = (
            f"{poi['name']}\n"
            f"{narrative.get(title_key, poi['topic'])}\n\n"
            f"{narrative[level_key]}"
        )
        await self._send_voice_or_text(update.message, self._speechify(narrative[level_key]), text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/bot.yaml")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    cfg = load_config(args.config)
    model, fallback_models = resolve_llm_models(cfg["llm"])
    cfg["llm"]["model"] = model
    cfg["llm"]["fallback_models"] = fallback_models
    app = BotApp(cfg)

    application = (
        Application.builder().token(cfg["telegram"]["bot_token"]).build()
    )
    application.add_handler(CommandHandler("start", app.start))
    application.add_handler(CommandHandler("poi", app.poi_list))
    application.add_handler(CommandHandler("here", app.here))
    application.add_handler(CommandHandler("level2", app.level2))
    application.add_handler(CommandHandler("level3", app.level3))
    application.add_handler(CommandHandler("sources", app.sources))
    application.add_handler(MessageHandler(filters.LOCATION, app.location))
    application.add_handler(
        MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.LOCATION, app.location)
    )
    application.add_handler(MessageHandler(filters.VOICE, app.voice))
    log.info("Started.")
    application.run_polling(allowed_updates=["message", "edited_message"])


if __name__ == "__main__":
    main()
