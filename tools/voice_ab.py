#!/usr/bin/env python3
"""A/B-подбор голоса: один и тот же научный абзац в духе Капицы разными голосами Yandex v1.

Зачем: на слух выбрать тембр, наиболее близкий к «светлому чёткому баритону» Капицы,
и подобрать размеренный темп (его манера). Голос/скорость потом фиксируются в .env
(YANDEX_VOICE, YANDEX_SPEED) — движок не меняем, остаёмся на надёжном v1.

Запуск на сервере (где есть ключи Yandex в окружении):
    cd /root/tropa-bot
    set -a; . ./.env; set +a
    python3 tools/voice_ab.py                # голоса filipp/zahar/ermil на speed 1.0
    python3 tools/voice_ab.py filipp 0.9 1.0 1.15   # один голос, разные темпы (сравнить пейс)

Результат: ./voice_samples/<voice>_<speed>.ogg — разослать в Telegram и выбрать на слух.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tts

# Абзац-эталон: размеренная подача Капицы, назван научный принцип, есть пауза перед термином.
SAMPLE = (
    "Добрый день. Посмотрите на закат. Днём небо голубое, а к вечеру оно краснеет — "
    "и это не случайность. Солнечный свет идёт к нам сквозь толщу воздуха, и воздух "
    "рассеивает короткие, синие лучи сильнее длинных, красных. Днём путь света короткий, "
    "и до нас доходит рассеянная синева. На закате путь длинный, синее теряется по дороге, "
    "и остаётся красное. У этого явления есть имя. Это рэлеевское рассеяние. "
    "Тот же принцип красит и голубизну неба, и синеву далёких гор."
)

# По умолчанию — три мужских нейронных голоса на размеренной скорости.
DEFAULT_VOICES = ["filipp", "zahar", "ermil"]
DEFAULT_SPEEDS = ["1.0"]


def main():
    args = sys.argv[1:]
    voices = [args[0]] if args else DEFAULT_VOICES
    speeds = args[1:] if len(args) > 1 else DEFAULT_SPEEDS

    out_dir = os.path.join(os.path.dirname(__file__), "..", "voice_samples")
    os.makedirs(out_dir, exist_ok=True)

    # tts.synthesize читает голос/скорость из окружения — переопределяем на каждый прогон.
    saved = {k: os.environ.get(k) for k in ("YANDEX_VOICE", "YANDEX_SPEED")}
    try:
        for voice in voices:
            for speed in speeds:
                os.environ["YANDEX_VOICE"] = voice
                os.environ["YANDEX_SPEED"] = str(speed)
                out = os.path.join(out_dir, f"{voice}_{speed}.ogg")
                try:
                    tts.synthesize(SAMPLE, out)
                    print(f"OK  {voice} speed={speed} -> {out}")
                except Exception as e:
                    print(f"ERR {voice} speed={speed}: {e}")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    print(f"\nГотово. Файлы в {os.path.abspath(out_dir)} — прослушать и выбрать голос/темп.")


if __name__ == "__main__":
    main()
