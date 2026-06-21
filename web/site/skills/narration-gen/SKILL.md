---
name: narration-gen
description: Use when generating narration texts (L1/L2/L3) and SSML audio files for POI points on a scientific trail. Covers the full pipeline from storyline to finished audio.
---

# Narration Generation

Full pipeline: storyline → L1/L2/L3 text → anti-AI → SSML → audio.

## Quick start

```bash
# Generate narrations + SSML for storyline #5, POI "hilltop", prefix 01
python3 skills/narration-gen/generate.py --storyline 5 --poi hilltop --nn 01

# Same + generate audio
python3 skills/narration-gen/generate.py --storyline 5 --poi hilltop --nn 01 --tts
```

Output: `skills/salute-tts/narrations/{nn}_{poi}_{l1,l2,l3}.xml`

## Manual generation (Claude Code agent)

When generating narrations directly (without the script), follow this exact structure.

### Step 1: Read the storyline

From `content/storylines.yaml`, grab:
- `title` — the hook question
- `topic` — scientific domain
- `cross_section` — where else this principle appears
- `section` — category

### Step 2: Write L1 (40-90 sec, 80-150 words)

Structure:
1. **Local binding** (1 sentence) — "Посмотри на...", "Прямо здесь..."
2. **Baffling claim** (1 sentence) — counter-intuitive, makes listener stop
3. **Action** (1-2 sentences) — what to do right now (look, touch, listen, count)
4. **Explanation** (2-3 sentences) — how it works, with one number+unit
5. **Bridge** (1 sentence) — where else this works

Example (GPS point):
> Открой бот — он уже знает, что ты у главного входа. Но ни один спутник тебя не видел. Ни камеры, ни луча, ни фотографии.
> Спутники не ищут тебя. Каждый передаёт одно: сейчас такое-то время, я в такой-то точке. Телефон ловит сигналы и замеряет задержку. Один спутник — расстояние. Три спутника — три сферы. Точка пересечения — ты.
> Ошибка в миллионную долю секунды сдвигает на 300 метров. Поэтому на орбите — атомные часы. Так же охотится летучая мышь: крик, задержка, расстояние.

### Step 3: Write L2 (90-180 sec, 150-300 words)

Structure:
1. Recap mechanism from L1 (1-2 sentences, don't repeat verbatim)
2. **Formula step-by-step**: explain what each symbol means BEFORE writing the formula
3. **Numerical estimate**: plug in real numbers, get a result with units
4. **Cross-section**: same math in another domain (1-2 sentences)

Formula rule: explain THEN name. "Расстояние равно скорости, умноженной на время задержки... записывается как ро равно цэ умножить на дельта тэ."

### Step 4: Write L3 (180-300 sec, 300-500 words)

Five micro-stories, each 2-4 sentences:
1. **Historical anecdote** — who discovered this and how
2. **Surprising application** — where else this principle works (unexpected domain)
3. **Record/extreme** — biggest, smallest, fastest example
4. **Paradox or failure** — when it breaks or gives counter-intuitive result
5. **Open question** — what we still don't know

Each micro-story starts with a bold hook. Separate with pauses.

### Step 5: Anti-AI check

Scan EVERY generated text. Kill on sight:

| Kill | Replace with |
|---|---|
| "является" | тире or nothing |
| "данный" | "этот" or remove |
| "обеспечивает" | "даёт", "создаёт" |
| "В рамках" | "В", "При", "Для" |
| "Важно отметить" | just state the fact |
| "Таким образом" | remove or "Итого:" |
| "представляет собой" | тире |
| triple adjectives | keep two or rephrase |
| trailing ", обеспечивая X" | new sentence |

If ANY flag remains after one rewrite pass, rewrite again. Zero tolerance.

### Step 6: Convert to SSML

Wrap in `<speak>` tags. Rules:

```xml
<speak>
First paragraph text.
<break time="400ms"/>
Second paragraph. Use *emphasis before key words.
<break time="400ms"/>
Third paragraph.
</speak>
```

- `<break time="400ms"/>` between paragraphs
- `<break time="500ms"/>` before dramatic reveal in L3
- `*` before emphasized words (no space: `*триста метров`)
- Stress marks: apostrophe after stressed vowel for tricky words

Stress dictionary (always apply):
```
трилатерация → трилатера'ция
реверберация → ревербера'ция
ковариация → ковариа'ция
когезия → коге'зия
кавитация → кавита'ция
ксилема → ксиле'ма
Фарадей → Фараде'й
Торричелли → Торриче'лли
Бернулли → Берну'лли
Вардроп → Вардро'п
Браесс → Бра'есс
```

Numbers as words: "300 м" → "триста метров", "10⁻³" → "десять в минус третьей", "ρgh" → "ро же аш".

### Step 7: Save and build

```
skills/salute-tts/narrations/{nn}_{poi_id}_l1.xml
skills/salute-tts/narrations/{nn}_{poi_id}_l2.xml
skills/salute-tts/narrations/{nn}_{poi_id}_l3.xml
```

Then:
```bash
python3 skills/salute-tts/build_audio.py --poi {nn}
```

## Validation

Before committing:
- [ ] L1: 80-150 words, no formulas, one number+unit
- [ ] L2: has formula explained step-by-step, numerical estimate
- [ ] L3: 5 distinct micro-stories, each with own hook
- [ ] Anti-AI: 0 flags on all three levels
- [ ] SSML: stress marks on all tricky words
- [ ] Listens well without looking at screen
- [ ] No "посмотри на график" or "как показано на схеме"
