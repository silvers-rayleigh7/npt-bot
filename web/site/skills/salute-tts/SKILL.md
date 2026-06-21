---
name: salute-tts
description: Use when generating or regenerating TTS audio for POI narrations in the Тропа project. Covers Salute Speech API authentication, SSML markup for natural narration, voice selection, and batch generation pipeline.
---

# Salute Speech TTS Generation

## Overview

Generate natural-sounding Russian narration audio for scientific trail POIs using Sber Salute Speech API with SSML markup for pauses, emphasis, and prosody control.

## Engine Selection (auto)

Before generating audio, the build script checks Salute Speech credentials:

1. **Salute Speech available** (`SALUTE_AUTH_DATA` in env → token request succeeds): use Salute Speech API (Bys_24000 voice, best quality, SSML support)
2. **Salute Speech unavailable** (no creds or auth fails): fallback to **Microsoft Edge TTS** (`edge-tts` CLI, voice `ru-RU-DmitryNeural`, free, no API key)

The script prints which engine is active at startup. Both engines produce MP3 output.

## Quick Reference

| Parameter | Value |
|---|---|
| Auth endpoint | `https://ngw.devices.sberbank.ru:9443/api/v2/oauth` |
| Synth endpoint | `https://smartspeech.sber.ru/rest/v1/text:synthesize` |
| Default voice | `Bys_24000` (Борис, мужской) |
| Credentials | `SALUTE_AUTH_DATA` in `/root/config/.env` (base64 of client_id:client_secret) |
| Free tier | 200 000 символов/мес |
| Max per request | 4000 символов including SSML tags |
| Output | WAV 24kHz → convert to MP3 128kbps via ffmpeg |
| Output dir | `/root/tropa/site/audio/` |

## Available Voices

| ID | Name | Gender |
|---|---|---|
| `Nec_24000` | Наталья | Ж |
| `Bys_24000` | Борис | М |
| `May_24000` | Марфа | Ж |
| `Tur_24000` | Тарас | М |
| `Ost_24000` | Александра | Ж |
| `Pon_24000` | Сергей | М |

## Authentication

Token lives 30 min. Always get fresh before batch.

```python
import requests, uuid, os

AUTH_DATA = os.environ.get('SALUTE_AUTH_DATA')  # from /root/config/.env
resp = requests.post(
    'https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
    headers={
        'Authorization': f'Basic {AUTH_DATA}',
        'RqUID': str(uuid.uuid4()),
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    data='scope=SALUTE_SPEECH_PERS',
    verify=False, timeout=10
)
token = resp.json()['access_token']
```

## Synthesis

```python
resp = requests.post(
    'https://smartspeech.sber.ru/rest/v1/text:synthesize',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/ssml'  # or 'application/text' for plain
    },
    params={'voice': 'Bys_24000'},
    data=ssml_text.encode('utf-8'),
    verify=False, timeout=20
)
# resp.content = WAV audio bytes
```

## SSML Best Practices for Scientific Narration

### Structure

Always wrap in `<speak>` root tag:
```xml
<speak>
First paragraph text.
<break time="400ms"/>
Second paragraph text.
</speak>
```

### Pauses

| Context | Tag | Duration |
|---|---|---|
| Between paragraphs | `<break time="400ms"/>` | 300-500ms |
| After question | `<break time="300ms"/>` | 200-400ms |
| Dramatic pause | `<break time="500ms"/>` | 500-700ms |
| Comma-level | `<break time="200ms"/>` | 100-200ms |
| Between sentences | natural, no tag needed | — |

### Emphasis

Asterisk directly before word (no space):
```xml
<speak>Ошибка в *одну миллионную долю секунды</speak>
```

### Stress Marks (Russian) — CRITICAL

TTS часто ошибается в ударениях научных и редких слов. Апостроф после ударной гласной:

```xml
<speak>Закон Фараде'я. Ковариа'нция. Трилатера'ция.</speak>
```

**Обязательно проверять и размечать:**

| Слово | Разметка | Почему |
|---|---|---|
| Фарадей | `Фараде'я` | TTS ставит на первый слог |
| трилатерация | `трилатера'ция` | Редкое слово |
| ковариация | `ковариа'ция` | Мат. термин |
| когезия | `коге'зия` | Физ. термин |
| кавитация | `кавита'ция` | Физ. термин |
| ксилема | `ксиле'ма` | Биол. термин |
| одометрия | `одоме'трия` | Техн. термин |
| реверберация | `ревербера'ция` | Акустический термин |
| изопериметрический | `изопериметри'ческий` | Мат. термин |
| Вардроп | `Вардро'п` | Фамилия |
| Браесс | `Бра'есс` | Фамилия |
| Хаген-Пуазёйль | `Хаге'н-Пуазёйль` | Двойная фамилия |
| Торричелли | `Торриче'лли` | Фамилия |

**Правило:** перед генерацией прослушать тестовый фрагмент с каждым непростым словом. Если ударение неправильное — добавить апостроф. Лучше поставить лишний апостроф, чем пропустить ошибку.

### Prosody Control

```xml
<paint pitch="4" speed="3" loudness="4">важная фраза</paint>
```
Attributes: `pitch` (1-5), `speed` (1-5), `loudness` (1-5).

### Emotions

```xml
<voice mode="happy">радостная фраза</voice>
```
Modes: `sad`, `annoyed`, `happy`, `whisper`.

### Numbers and Formulas — Always as Words

| Source | SSML text |
|---|---|
| `300 м` | `триста метров` |
| `7.5 км/ч` | `семь с половиной километров в час` |
| `10⁻³` | `десять в минус третьей` |
| `ρgh` | `ро же аш` |
| `T₆₀` | `тэ шестьдесят` |
| `≈` | `примерно` |
| `ω²` | `омега в квадрате` |
| `μ` | `мю` |
| `Δt` | `дельта тэ` |

### Special Content

```xml
<say-as interpret-as="cardinal">42</say-as>
<say-as interpret-as="date" detail="d.m.y">25.01.2000</say-as>
<sub alias="мартэновских">мартеновских</sub>
```

## Narration Writing Rules (Gasnikov Style)

### Cardinal Rule: Eyes-Free

All narrations MUST be fully comprehensible without looking at a screen, card, or stend. The listener is walking, looking around, not reading. This means:
- Formulas are spoken as words: $\rho g h$ → "ро жэ аш", $T_{60} \approx 1.6$ → "тэ шестьдесят — примерно одна и шесть"
- Visual references ("посмотри на график", "как показано на схеме") are FORBIDDEN
- Spatial references are OK if they point to the physical world: "посмотри на деревья вокруг", "хлопни в ладоши здесь"
- Structure conveyed by voice: pauses between sections, prosody changes for key points
- Each level is a self-contained audio experience, not a supplement to a card

### Three Levels of Audio

| Level | Duration | Content | Style |
|---|---|---|---|
| L1 (базовый) | 40–90 sec | Hook + action + one thought + anchor | Энергичный, удивляющий |
| L2 (с формулами) | 90–180 sec | Mechanism + formula as words + cross-section | Рассуждающий, как лекция |
| L3 (доп. факты) | 180–300 sec | 5 micro-stories, history, open question | Собеседник, как подкаст |

### Style Rules

1. Start with local binding: "Посмотри на...", "Ты только что..."
2. One baffling opener per POI
3. Numbers as words, formulas as speech
4. Short sentences for audio (max 25 words)
5. Pause after questions and before key reveals
6. End with bridge to next concept
7. L2: formula explained step by step BEFORE stating it — "расстояние равно скорости, умноженной на время задержки... записывается как ро равно цэ умножить на дельта тэ"
8. L3: each micro-story has its own intro pause (500ms) and slightly different energy

## Pipeline: Anti-AI → SSML → TTS

Audio production is a TWO-SKILL pipeline. Skipping the first skill produces robotic, AI-sounding narrations.

### Step 1: Anti-AI Check (MANDATORY before TTS)

Before converting any text to SSML, run it through the `anti-ai-text` skill (`/root/tropa/skills/anti-ai-text/SKILL.md`). This catches:
- Канцелярит: "является", "представляет собой", "обеспечивает"
- AI patterns: "важно отметить", "в рамках данного", "таким образом"
- Faux-academic filler: "демонстрирует", "содействует", "подчёркивает"
- Structural tells: rule-of-three adjectives, trailing participles

**Process:** Take the l1/l2/l3 text from YAML → scan with anti-ai-text rules → rewrite flagged phrases → THEN convert to SSML.

A narration that passes TTS but fails anti-ai is worse than no narration — the listener will hear "AI voice reading AI text" and tune out.

### Step 2: SSML Conversion

Convert cleaned text to SSML with stress marks, breaks, emphasis, numbers-as-words per rules above.

### Step 3: TTS Generation

See `build_audio.py` in this directory for the complete pipeline script.

### Validation Checklist

Before committing audio:
- [ ] Source text passed anti-ai scan (0 flags)
- [ ] All formulas spoken as words (no symbols read as-is)
- [ ] All scientific terms have stress marks
- [ ] Narration makes sense without looking at screen
- [ ] Duration within level range (L1: 40-90s, L2: 90-180s, L3: 180-300s)

Usage:
```bash
cd /root/tropa
python skills/salute-tts/build_audio.py                    # all POIs
python skills/salute-tts/build_audio.py --poi 01 05        # specific POIs
python skills/salute-tts/build_audio.py --voice Nec_24000  # different voice
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Sending LaTeX/unicode math | Write as Russian words |
| No `<speak>` wrapper | SSML requires `<speak>` root |
| `Content-Type: application/text` with SSML | Use `application/ssml` |
| Token expired (30 min) | Fresh token before each batch |
| Text > 4000 chars | Split into segments |
| `&` in text | Escape as `&amp;` |
| Missing `verify=False` | Sber API requires it |
