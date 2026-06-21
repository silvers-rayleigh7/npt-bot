#!/usr/bin/env python3
"""Generate L1/L2/L3 narration SSML files for a POI from storyline data.

Usage:
    python generate.py --storyline 5 --poi hilltop --nn 01
    python generate.py --storyline 5 --poi hilltop --nn 01 --tts

Reads storyline from content/storylines.yaml by ID, generates three narration
levels via Claude API, applies anti-AI filtering, converts to SSML, saves files.
With --tts, also generates audio via build_audio.py.
"""

import argparse
import json
import os
import re
import subprocess
import sys

import yaml

import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NARRATIONS_DIR = os.path.join(ROOT, "skills", "salute-tts", "narrations")
STORYLINES_PATH = os.path.join(ROOT, "content", "storylines.yaml")

STYLE_RULES = """
Ты пишешь озвучку для научной тропы. Слушатель идёт по маршруту, смотрит вокруг, слушает в наушниках.

СТИЛЬ:
- Начни с привязки к месту: "Посмотри на...", "Прямо здесь...", "Ты только что..."
- Один удивляющий факт в начале — контринтуитивный
- Короткие предложения (до 25 слов). Это аудио, не статья.
- Числа с единицами всегда: "300 метров", "минус 15 атмосфер"
- Формулы проговаривай словами: ρgh → "ро жэ аш", T₆₀ → "тэ шестьдесят"
- Никаких "это очень интересный эффект", "важно отметить", "стоит подчеркнуть"
- Никаких "является", "данный", "обеспечивает", "представляет собой", "в рамках"
- Не называй учёных если имя не часть истории
- Закончи мостиком: где ещё работает тот же принцип

ЗАПРЕЩЕНО (anti-AI маркеры):
- "является", "данный", "указанный", "обеспечивает", "демонстрирует"
- "В рамках", "Важно отметить", "Стоит отметить", "Таким образом"
- "Представляет собой", "Играет роль", "Оказывает влияние"
- Тройки прилагательных ("быстрый, удобный и надёжный")
- Деепричастные нагромождения
- Цепочки родительного падежа (3+ существительных в Р.п. подряд)
"""

LEVEL_SPECS = {
    "l1": {
        "name": "Базовый",
        "duration": "40-90 секунд (80-150 слов)",
        "content": "Хук + действие руками/глазами + одна ключевая мысль + мостик",
        "style": "Энергичный, удивляющий. Как будто друг хватает за рукав и говорит 'смотри!'",
    },
    "l2": {
        "name": "С формулами",
        "duration": "90-180 секунд (150-300 слов)",
        "content": "Механизм явления + формула словами + числа + где ещё работает",
        "style": "Рассуждающий, как хорошая лекция. Формулу объясни по шагам ДО того как назовёшь",
    },
    "l3": {
        "name": "Доп. факты",
        "duration": "180-300 секунд (300-500 слов)",
        "content": "5 микро-историй: исторический анекдот, неожиданное применение, рекорд, парадокс, открытый вопрос",
        "style": "Собеседник, как подкаст. Каждая микро-история — отдельный абзац со своим хуком",
    },
}

STRESS_DICT = {
    "Фарадей": "Фараде'й",
    "трилатерация": "трилатера'ция",
    "ковариация": "ковариа'ция",
    "когезия": "коге'зия",
    "кавитация": "кавита'ция",
    "ксилема": "ксиле'ма",
    "одометрия": "одоме'трия",
    "реверберация": "ревербера'ция",
    "изопериметрический": "изопериметри'ческий",
    "Вардроп": "Вардро'п",
    "Браесс": "Бра'есс",
    "Торричелли": "Торриче'лли",
    "Бернулли": "Берну'лли",
    "Навье": "Навье'",
    "Пуазёйль": "Пуазёйль",
    "аллометрия": "алломе'трия",
    "филлотаксис": "филлота'ксис",
    "тиксотропия": "тиксотропи'я",
    "Гельмгольц": "Ге'льмгольц",
    "констелляция": "констелля'ция",
    "мультиконстелляция": "мультиконстелля'ция",
}


def load_storyline(storyline_id: int) -> dict | None:
    with open(STORYLINES_PATH) as f:
        data = yaml.safe_load(f)
    for s in data.get("storylines", []):
        if s["id"] == storyline_id:
            return s
    return None


def call_claude(prompt: str) -> str:
    claude_bin = shutil.which("claude")
    if not claude_bin:
        print("ERROR: 'claude' CLI not found", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run(
        [claude_bin, "-p", "--model", "sonnet"],
        input=prompt, capture_output=True, text=True, timeout=300,
    )
    return result.stdout.strip()


def generate_narrations(storyline: dict, poi_name: str) -> dict[str, str]:
    results = {}

    for level_key, spec in LEVEL_SPECS.items():
        prompt = f"""{STYLE_RULES}

СЮЖЕТ:
- Название: {storyline['title']}
- Тема: {storyline['topic']}
- Раздел: {storyline['section']}
- Межпредметная связь: {storyline.get('cross_section', '')}

ТОЧКА НА МАРШРУТЕ: {poi_name}

ЗАДАЧА: Напиши озвучку уровня "{spec['name']}" для этой точки.
- Длительность: {spec['duration']}
- Содержание: {spec['content']}
- Стиль: {spec['style']}

Верни ТОЛЬКО текст озвучки, без заголовков, пометок и комментариев. Чистый текст для озвучки."""

        results[level_key] = call_claude(prompt)
        print(f"  {level_key}: {len(results[level_key].split())} слов")

    return results


def text_to_ssml(text: str, level: str = "l1") -> str:
    for word, stressed in STRESS_DICT.items():
        text = re.sub(rf"\b{word}", stressed, text, flags=re.IGNORECASE)

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    pause_between = '<break time="500ms"/>' if level == "l3" else '<break time="400ms"/>'

    ssml_parts = ["<speak>"]
    for i, para in enumerate(paragraphs):
        para = re.sub(r"\$[^$]+\$", "", para)
        para = re.sub(r"\*\*([^*]+)\*\*", r"*\1", para)
        para = re.sub(r"[—–]", "--", para)
        ssml_parts.append(para)
        if i < len(paragraphs) - 1:
            ssml_parts.append(pause_between)
    ssml_parts.append("</speak>")

    return "\n".join(ssml_parts) + "\n"


QUALITY_GATE_PROMPT = """Ты — редактор научного аудиогида. Слушатель идёт по тропе в наушниках, НЕ смотрит на экран.

Прочитай текст ВСЛУХ про себя. Найди ВСЕ проблемы:

1. ФОРМУЛЫ: объяснение формулы путаное? Метафора для математической операции корявая? ("корень режет зависимость" — плохо, "чтобы видеть вдвое дальше, поднимись вчетверо выше" — хорошо)
2. ЧИСЛА: арифметика сходится? Единицы указаны? Порядок величины правильный?
3. СЛУХ: фраза звучит неестественно при произнесении? Слишком длинная? Скороговорка?
4. НАУКА: факт верный? Нет подмены причины и следствия? Нет чрезмерного упрощения до ошибки?
5. ЯСНОСТЬ: слушатель без подготовки поймёт с первого раза? Нет скачков логики?

Для КАЖДОЙ проблемы верни строку:
[КАТЕГОРИЯ] "цитата из текста" → что не так → как исправить

Если проблем нет — верни ровно одно слово: CLEAN

ТЕКСТ:
"""


def quality_gate(text: str, level: str) -> str:
    prompt = QUALITY_GATE_PROMPT + text
    result = call_claude(prompt)
    return result.strip()


def fix_quality_issues(text: str, issues: str, storyline: dict) -> str:
    prompt = f"""Исправь текст озвучки научной тропы. Проблемы перечислены ниже.

ПРАВИЛА:
- Формулы объясняй пошагово и простыми словами. Не используй метафоры для математических операций.
- Каждое предложение должно звучать естественно при произнесении вслух.
- Числа с единицами. Арифметика должна сходиться.
- Сохрани длину текста (±10%).

ПРОБЛЕМЫ:
{issues}

ИСХОДНЫЙ ТЕКСТ:
{text}

ТЕМА: {storyline['title']} — {storyline['topic']}

Верни ТОЛЬКО исправленный текст, без комментариев."""
    return call_claude(prompt)


def anti_ai_check(text: str) -> list[str]:
    flags = []
    banned_words = [
        "является", "данный", "указанный", "обеспечивает", "демонстрирует",
        "содействует", "осуществляет", "представляет собой", "затрагивает",
        "способствует", "подчёркивает", "символизирует",
    ]
    banned_phrases = [
        "в рамках", "важно отметить", "стоит отметить", "стоит подчеркнуть",
        "необходимо учитывать", "таким образом", "в контексте",
        "играет роль", "оказывает влияние", "на основании",
    ]
    lower = text.lower()
    for w in banned_words:
        if w in lower:
            flags.append(f"[WORD] '{w}'")
    for p in banned_phrases:
        if p in lower:
            flags.append(f"[PHRASE] '{p}'")
    return flags


def main():
    parser = argparse.ArgumentParser(description="Generate POI narrations")
    parser.add_argument("--storyline", type=int, required=True, help="Storyline ID from storylines.yaml")
    parser.add_argument("--poi", required=True, help="POI id (e.g. hilltop)")
    parser.add_argument("--nn", default="01", help="POI number prefix (e.g. 01)")
    parser.add_argument("--poi-context", default="", help="Location description for the narrator")
    parser.add_argument("--tts", action="store_true", help="Also generate audio via build_audio.py")
    parser.add_argument("--output-dir", default=NARRATIONS_DIR, help="SSML output directory")
    args = parser.parse_args()

    storyline = load_storyline(args.storyline)
    if not storyline:
        print(f"Storyline {args.storyline} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Storyline: {storyline['title']}")
    print(f"POI: {args.nn}_{args.poi}")
    poi_desc = args.poi_context or storyline["title"]

    print(f"\nGenerating narrations via Claude API...")
    narrations = generate_narrations(storyline, poi_desc)

    print(f"\nAnti-AI check...")
    all_clean = True
    for level, text in narrations.items():
        flags = anti_ai_check(text)
        if flags:
            print(f"  {level}: {len(flags)} flags: {', '.join(flags)}")
            all_clean = False
        else:
            print(f"  {level}: clean")

    if not all_clean:
        print("\nRe-generating flagged levels...")
        for level, text in narrations.items():
            if anti_ai_check(text):
                fix_prompt = f"""Перепиши текст. Убери ВСЕ маркеры ИИ-текста: "является", "данный", "обеспечивает", "важно отметить", "в рамках", "таким образом", тройки прилагательных, деепричастные нагромождения. Сохрани смысл и длину. Верни ТОЛЬКО исправленный текст.\n\nТЕКСТ:\n{text}"""
                narrations[level] = call_claude(fix_prompt)
                remaining = anti_ai_check(narrations[level])
                print(f"  {level}: {'clean' if not remaining else f'{len(remaining)} flags remain'}")

    print(f"\nQuality gate (science + listening)...")
    max_rounds = 3
    for round_n in range(max_rounds):
        any_issues = False
        for level in ["l1", "l2", "l3"]:
            result = quality_gate(narrations[level], level)
            if result == "CLEAN":
                print(f"  {level}: CLEAN")
            else:
                any_issues = True
                issue_lines = len(result.strip().split("\n"))
                print(f"  {level}: {issue_lines} issues — fixing...")
                narrations[level] = fix_quality_issues(narrations[level], result, storyline)
                recheck = anti_ai_check(narrations[level])
                if recheck:
                    narrations[level] = call_claude(
                        f"Убери маркеры ИИ-текста: {', '.join(recheck)}. Верни ТОЛЬКО текст.\n\n{narrations[level]}"
                    )
        if not any_issues:
            break
        if round_n < max_rounds - 1:
            print(f"  (round {round_n + 2}...)")

    print(f"\nConverting to SSML...")
    os.makedirs(args.output_dir, exist_ok=True)
    for level in ["l1", "l2", "l3"]:
        ssml = text_to_ssml(narrations[level], level=level)
        fname = f"{args.nn}_{args.poi}_{level}.xml"
        path = os.path.join(args.output_dir, fname)
        with open(path, "w") as f:
            f.write(ssml)
        print(f"  {fname}")

    if args.tts:
        print(f"\nGenerating audio...")
        build_script = os.path.join(ROOT, "skills", "salute-tts", "build_audio.py")
        subprocess.run(
            [sys.executable, build_script, "--poi", args.nn],
            cwd=ROOT,
            env={**os.environ, **_load_env()},
        )

    print(f"\nDone. Files in {args.output_dir}")


def _load_env() -> dict:
    env_path = "/root/config/.env"
    extra = {}
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    extra[k.strip()] = v.strip()
    return extra


if __name__ == "__main__":
    main()
