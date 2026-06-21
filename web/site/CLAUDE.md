# Тропа — Project Instructions

## Project Structure
```
bot/config/     — POI YAML configs, style.md (LLM system prompt), bot config
site/           — Landing page + knowledge base (tropa.fmin.xyz)
site/audio/     — TTS audio files (Salute Speech, Boris voice)
site/cards/     — Typst-generated PDF cards per POI per level
site/typst/     — Typst template + build script for PDF cards
skills/         — Project skills for Claude Code
docs/           — Route docs, content model, physical interactives spec
BRIEF.md        — Full project brief (89 storylines, tone of voice, architecture)
```

## Skills

### `skills/salute-tts/`
TTS generation via Sber Salute Speech API. SSML markup, stress marks for scientific terms, batch generation pipeline.
- `SKILL.md` — full reference (API, SSML tags, stress table, narration rules)
- `build_audio.py` — batch generator: `python3 skills/salute-tts/build_audio.py`

## Key Conventions

- **Voice**: Борис (`Bys_24000`) — default for all narrations
- **POI content source of truth**: `bot/config/poi.innopolis.yaml` for metadata, site JS config for rich L1/L2/L3 text
- **Formulas**: KaTeX on site (`$...$`), Typst in PDFs, words in TTS
- **Stress marks**: apostrophe after stressed vowel in SSML (`трилатера'ция`, `Фараде'я`)
- **Audio format**: WAV 24kHz from API → MP3 128kbps via ffmpeg
- **PDF generation**: `python3 site/typst/build.py` (requires typst CLI)
- **Credentials**: `SALUTE_AUTH_DATA` in `/root/config/.env`

## Tone of Voice (Gasnikov)

Full spec in `bot/config/style.md` and `BRIEF.md` section 2. Key rules:
1. Local binding ("посмотри на...", "прямо здесь...")
2. Baffling opener → counter-intuitive turn → numerical estimate
3. Formulas in L2, anecdotes in L3
4. Numbers with units always
5. No "это очень интересный эффект" — empty filler forbidden
