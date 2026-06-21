---
name: poi-gen
description: Use when creating, editing, or reviewing POI (point of interest) content for Тропа routes. Covers storyline selection, physical interactive design, feasibility checks, text generation for three levels, and the full pipeline from idea to deployable POI.
---

# POI Generation Skill

## What is a POI

A POI (Point of Interest) is a single station on a scientific trail. Each POI has:
- A scientific storyline tied to a physical location
- Three levels of narration (L1 basic, L2 formulas, L3 deep facts)
- A physical interactive — something visitors build, touch, or measure
- Audio narration generated via TTS
- A PDF card for print

## Pipeline

```
Storyline candidate → GROUND ON REAL POI → Critical-visitor test → Feasibility check →
   Text (3 levels) → Anti-AI scan → SSML → TTS → Audio (MP3)
                                                ↘ Typst → PDF card
```

### Step 0: GROUND ON REAL POI (mandatory — fail-fast filter)

**The single biggest mistake**: extracting a "cool idea" from a lecture/book and adding it to the bank without first checking it lands on a real POI on a real route. A storyline without a place to live on the trail is **useless** — the bank is not a museum catalog, it is a deployment queue.

**Two routes currently exist:**
- `bot/config/poi.innopolis.yaml` — Innopolis University, 8 POIs (entrance, atrium, robot path, Tesla marker, boulevard fork, sports zone, forest edge, data-center view)
- `bot/config/poi.skolkovo.yaml` — Skolkovo Big Boulevard, 7 POIs (MCD station, Tehnopark, World Class, central square, Hypercube, Matrex, Skoltech)

**For each candidate storyline, BEFORE anything else, answer:**

1. **Which existing POI does this refine or extend?** Open both YAMLs. Find a point with a visible physical object that anchors the story. Cite the POI `id`.
2. **If no existing POI fits — does this justify a new POI on one of these routes?** Propose specific GPS coordinates. If the only honest answer is "would need a hypothetical site that doesn't exist on either route" → **archive, do not add to bank**.
3. **Critical-visitor test**: imagine you are a sceptical, time-pressed walker passing this point. *Would you stop and listen?* If the honest answer is "only if I'm already into the topic" — **archive**. The trail is for the random kid, not for fans.

**Common failure modes that trigger archive:**
- Pure abstract algorithm / pure game theory without a physical object on the route (e.g. tit-for-tat, Gale–Shapley, Arrow's theorem, Conway's Life, HyperLogLog, k-means).
- Politics, voting systems, sociological models.
- "Cool number trick" that needs paper/pencil and a quiet desk (Karatsuba, Newton division, Schwarz triangle).
- Anything requiring a TV/screen/keyboard/touch device on the trail.
- Anything where the only interactive is "read this text and think about it".

**Common passes:**
- A story that uses a real lake, tree, rock, sky, building, fork in the path, bridge, statue as its anchor.
- An abstract idea that has a *bodily* demo on a small stand (coin rotation paradox, Platonic-solid sculptures, Fermat-Torricelli weighted strings, complex number = rotation on a clock face).

### Step 1: Select storyline from bank

Source: `content/storylines.yaml`.

Pick by:
- Route location (what's physically visible at the point)
- Section variety (don't cluster 5 geometry POIs in a row)
- Feasibility rating (prefer "easy", avoid "hard")
- Budget (aim for <500₽ per POI on average)

### Step 2: Feasibility check (three gates)

Every POI must pass ALL three gates:

**Gate 1 — School workshop:**

| Criterion | Required |
|---|---|
| **Basic tools only** | Wood, wire, string, magnets, metal — no CNC, no 3D printing |
| **No electricity** | No batteries, no power outlets, no electronics on the trail |
| **No safety hazard** | No chemicals, no fire, no sharp edges at child height |
| **Portable** | Fits in a car. Nothing heavier than 15 kg |

**Gate 2 — Budget-accounted, non-exotic:**

| Criterion | Required |
|---|---|
| **Any material OK** | Stones, boards, planks, metal, plastic, paint, magnets, springs — whatever fits. Found and bought materials both fine. |
| **Budget must include all costs** | The realistic budget tier (300/600/1000/1500+ ₽) has to actually cover the listed parts, including installation. Don't list a "разметка площадки" and tag it «до 300₽». |
| **Avoid exotic** | Prefer common shop / Авито / Леруа / Чип-и-Дип / AliExpress parts. Don't require CNC-3D-printed-laser-cut-on-Mars unless that's the only way. |
| **Consumables OK if sourced** | If a part is consumable (replacement markers, sample cards, fresh paint), say *where to buy and how often to replace* in «Как сделать». |

**Still fails Gate 2:** food, soap, fresh paper that gets wet daily, anything that can't be re-bought from a known shop.

**Gate 3 — Any weather outdoors:**

| Criterion | Required |
|---|---|
| **Rain** | Metal/wood/stone survive. Paper → laminate or metal engraving |
| **Frost** | No water, no rubber seals, no LCD screens |
| **Wind** | Loose parts chained/bolted. Nothing lighter than 200g free-standing |
| **Sun** | UV-resistant. No foam, no fabric, no food |
| **Self-explanatory** | Works without a guide. 20 seconds to understand |

**Adaptation rule:** If an idea is great but fails Gate 2/3, try: paper → metal engraving, cardboard → welded wire, loose objects → chained/mounted, flashlight → sunlight, water → dry alternative. If no viable adaptation exists → remove.

If a storyline fails any gate and can't be adapted → remove.

### Step 3: Write three narration levels

All narrations follow the Gasnikov style (see `bot/config/style.md`):

| Level | Duration | Content | Style |
|---|---|---|---|
| L1 (базовый) | 40-90 sec | Hook + action + one key idea | Energetic, surprising |
| L2 (формулы) | 90-180 sec | Mechanism + formula as words + cross-section | Analytical, like a lecture |
| L3 (факты) | 180-300 sec | 5 micro-stories, history, open question | Conversational, like a podcast |

**Rules:**
1. Start with local binding: "Посмотри на...", "Прямо здесь..."
2. One baffling opener per POI — a counter-intuitive claim
3. Numbers always with units. Formulas spoken as words in audio.
4. Short sentences (max 25 words for audio)
5. No filler: "очень интересный эффект" = forbidden
6. Eyes-free: narration must work without looking at a screen
7. Focus on ideas, not names — don't name-drop scientists unless the name IS the story

### Step 4: Anti-AI check (MANDATORY)

Before converting to SSML, run text through `skills/anti-ai-text/SKILL.md`.

Kill: "является", "данный", "важно отметить", "представляет собой", "обеспечивает", trailing participles, rule-of-three adjectives.

A narration that passes TTS but fails anti-AI is worse than no narration.

### Step 5: SSML + TTS

Use `skills/salute-tts/SKILL.md` for the full TTS pipeline.

The build script auto-selects engine:
- **Salute Speech** if `SALUTE_AUTH_DATA` available (best quality, SSML support)
- **Edge TTS** as fallback (free, no API key, `ru-RU-DmitryNeural` voice)

```bash
# Generate all levels for specific POIs
python3 skills/salute-tts/build_audio.py --poi 01 05

# Generate everything
python3 skills/salute-tts/build_audio.py
```

SSML files go in `skills/salute-tts/narrations/` as `{nn}_{poi_id}_{level}.xml`.
Audio output: `site/audio/{nn}_{poi_id}_{level}.mp3`.

### Step 6: Physical interactive design

Each POI needs a hands-on element. Design principles from `docs/physical-interactives.md`:

**Do:**
- One effect, large parts, no fragile electronics
- Materials: plywood, metal, acrylic, rope, magnets, anti-vandal fasteners
- Understandable in 20 seconds without instructions
- Works in rain, wind, direct sun

**Don't:**
- Touchscreens, small removable parts, long instructions
- Anything dependent on power supply
- Decoration without an experiment

### Step 7: Budget estimation

| Material | Typical cost |
|---|---|
| Found materials (sticks, rocks, water) | 0₽ |
| Basic hardware (wire, magnets, springs) | 200-500₽ |
| Wood/plywood cuts | 500-1500₽ |
| Metal fabrication | 1500-3000₽ |
| Specialty items (prism, lens, tuning fork) | 1000-3000₽ |

Target: **average 500₽ per POI**, max 2000₽ for complex items.

Budget categories on the site:
- до 300₽ — found/basic materials
- до 600₽ — hardware store
- до 1000₽ — wood workshop
- свыше 1000₽ — specialty items

## POI YAML format

```yaml
- id: 1
  name: "university_entrance"
  lat: 55.7527
  lon: 48.7440
  trigger_radius_m: 30
  topic: "GPS/ГЛОНАСС, трилатерация"
  scenario_brief: "One-sentence hook"
  level1_seed: "L1 narration text"
  level2_seed: "L2 narration with formulas"
  level3_seed: "L3 narration with stories"
  physical_interactive: "Description of hands-on element"
  sources: ["source1", "source2"]
  verified: false
  budget_rub: 500
```

## Quality checklist

Before marking a POI as done:

- [ ] Tied to a real visible object at the location
- [ ] Has a number with units in every level
- [ ] Has a formula (spoken as words) in L2
- [ ] Physical interactive works without power
- [ ] Budget estimated and reasonable (<2000₽)
- [ ] Anti-AI scan passed (0 flags)
- [ ] Audio generated for all 3 levels
- [ ] Audio comprehensible without looking at screen
- [ ] Duration within range (L1: 40-90s, L2: 90-180s, L3: 180-300s)
- [ ] Cross-section link to another field of science
