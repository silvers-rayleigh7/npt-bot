---
name: anti-ai-text
description: |
  Detects and rewrites AI-sounding text in both English and Russian.
  Invoke when writing or editing prose that must not read as machine-generated:
  academic papers, blog posts, outbound emails, marketing copy, Telegram posts,
  Habr articles, course materials, dissertation chapters.
  Combines the Wikipedia "Signs of AI writing" catalogs (EN + RU) with
  Russian-specific канцелярит/calque detection and concrete rewrite rules.
triggers:
  - writing text that should sound human
  - editing AI-generated drafts
  - proofreading for AI tells
  - "humanize", "очеловечь", "убери следы ИИ", "sounds like ChatGPT"
  - preparing text for publication (Habr, TG, academic)
---

# Anti-AI Text Skill (EN + RU)

A detection-and-rewrite skill grounded in:
- English: [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- Russian: [Википедия:Признаки сгенерированности текста](https://ru.wikipedia.org/wiki/Википедия:Признаки_сгенерированности_текста)
- Practical rules from the `crimeacs/ai-tells-validator` skill and Russian humanizer research

---

## Workflow: Detect → Flag → Rewrite

### Step 1: DETECT — scan for markers

Read the text and check against all categories below. Count violations.

### Step 2: FLAG — report findings

For each violation, output:
```
[CATEGORY] "offending quote" → explanation
```

### Step 3: REWRITE — eliminate tells

Apply rewrite rules (Section III) to produce clean text that:
- Preserves meaning and factual content
- Sounds like a competent human author
- Passes re-scan with zero flags

---

## I. English AI Tells

### A. Banned Words

| Word | Why it flags |
|------|-------------|
| delve, delving | #1 ChatGPT tell since 2023 |
| tapestry | metaphor overuse |
| intricate, intricacies | false sophistication |
| landscape | vague buzzword |
| meticulous, meticulously | inflation |
| pivotal | drama inflation |
| robust | tech buzzword |
| underscore, underscores | faux-academic |
| showcase, showcasing | promotional |
| testament | dramatic framing |
| enduring | significance inflation |
| fostering, foster | vague causation |
| garner | archaic formality |
| bolster, bolstered | inflation |
| interplay | faux-intellectual |
| leverage, leveraging | SaaS-speak |
| streamline, streamlined | SaaS-speak |
| transformative | hype |
| groundbreaking | hype |
| cutting-edge | hype |
| seamless, seamlessly | SaaS-speak |
| elevate, elevating | SaaS-speak |
| unlock, unlocking | SaaS-speak |
| empower, empowering | SaaS-speak |
| revolutionize | hype |
| paradigm | buzzword |
| synergy | corporate-speak |
| holistic | buzzword |
| vibrant | promotional fluff |

### B. Banned Phrases

- "I hope this email finds you well"
- "circling back" / "touching base" / "just checking in"
- "in conclusion" / "in summary" / "to summarize"
- "it is important to note" / "it's worth noting"
- "in today's fast-paced / rapidly evolving / digital age"
- "plays a vital/crucial/pivotal/key role"
- "navigate the complexities"
- "in the realm of" / "in the world of" / "when it comes to"
- "at its core" / "at its heart"
- "a powerful tool" / "best-in-class" / "world-class"
- "value proposition" / "thought leadership"
- "looking forward to hearing from you"
- "hope this helps"
- "let me know your thoughts"
- "a deep dive" / "a treasure trove" / "a wealth of"

### C. Structural Patterns

| Pattern | Example | Detection |
|---------|---------|-----------|
| Negative parallelism | "Not just X, but Y" | regex: `not (just\|merely\|only) .+ but` |
| Rule of Three | "clear, sourced, and trustworthy" | three comma-separated adjectives |
| Trailing participle | ", ensuring X" / ", driving Y" | comma + gerund at clause end |
| Whether-you're | "Whether you're X or Y..." | opener pattern |
| Excited-to | "Excited to share/announce" | opener pattern |

### D. Punctuation & Formatting

- **Em-dash overuse**: more than 1 per paragraph = flag. Em-dash is the #1 punctuation tell in 2026.
- **Smart/curly quotes**: `""''` instead of straight quotes
- **Thematic breaks**: `---` inside body text
- **Excessive bold**: bolding every key term
- **Emoji as structure**: emoji bullets or separators in professional text

---

## II. Russian AI Tells (Признаки ИИ-текста)

### A. Слова-маркеры (Banned Words)

| Слово/оборот | Почему палит |
|--------------|--------------|
| является | LLM используют 2-3x чаще людей, русский часто обходится без связки |
| данный | канцелярит, уместен только в юр. документах |
| указанный | то же |
| вышеупомянутый | то же |
| обеспечивает | шаблонный глагол поверхностного анализа |
| демонстрирует | то же |
| содействует | то же |
| соответствует | то же |
| подчёркивает | faux-academic |
| символизирует | драматизация |
| выступает (в роли) | канцелярит вместо простого "это" |
| осуществляет | номинализация: "осуществить проверку" вместо "проверить" |
| представляет собой | канцелярит |
| затрагивает | вода |
| способствует | вода |
| погружаться | калька с "delve" |
| гобелен | калька с "tapestry" |
| переплетение | калька с "interplay" |
| нюанс (мн.) | калька с "nuance" |

### B. Фразы-маркеры (Banned Phrases)

**Канцелярит и наукообразие:**
- "В рамках" (данного исследования/проекта/статьи)
- "Важно отметить" / "Стоит отметить" / "Стоит подчеркнуть"
- "Необходимо учитывать"
- "На основании вышеизложенного"
- "В контексте" (чего-либо)
- "Таким образом" (как вводное к выводу)
- "В заключение следует отметить"
- "Представляет собой"
- "Играет важную/ключевую/значительную роль"
- "Оказывает влияние на"
- "Носит характер"

**Рекламный язык:**
- "Может похвастаться"
- "Расположенный в самом сердце"
- "Потрясающая природная красота"
- "Вековое наследие"
- "Богатый, яркий, разнообразный"
- "Уникальный" (без обоснования)

**Ложная глубина:**
- "Это не просто X, это Y"
- "Не только... но и..."
- "Неизгладимый след"
- "Поворотный момент"
- "Служит напоминанием"
- "Свидетельство мастерства/эпохи"

**Диалоговые артефакты:**
- "Конечно!" / "Безусловно!"
- "Я надеюсь, это помогло"
- "Если хотите узнать больше, дайте знать"
- "Сообщите мне"
- "Давайте рассмотрим"

**Ложные кальки с английского:**
- "В конце дня" (at the end of the day)
- "Давайте нырнём" (let's dive in)
- "За пределами коробки" (outside the box)
- "На одной странице" (on the same page)

### C. Структурные паттерны

| Паттерн | Пример | Обнаружение |
|---------|--------|-------------|
| Цепочки родительного падежа | "улучшение качества обслуживания клиентов компании" | 3+ существительных в Р.п. подряд |
| Номинализация | "осуществить проверку" вместо "проверить" | глагол + отглагольное сущ. |
| Деепричастные нагромождения | "являясь ключевым элементом, обеспечивая..." | 2+ деепричастных оборота в одном предложении |
| Правило трёх | "быстрый, удобный и надёжный" | три однородных прилагательных |
| Параллелизм с отрицанием | "Не только X, но и Y" | шаблонная конструкция |
| Меризм (крайности) | "от лёгкого до тяжёлого" | "от X до Y" без конкретики |
| Шаблонные секции | "Проблемы и перспективы" → "Несмотря на... всё же..." | структурный шаблон |
| Принудительный оптимизм | Статья о проблемах заканчивается позитивом | структурный шаблон |
| Однообразие длин | все абзацы ~одинаковой длины | burstiness < порога |

### D. Пунктуация и оформление

- **Тире вместо запятых**: плотность > 5 на 1000 символов = флаг (норма для человека ~2-3)
- **Списки вместо текста**: если >40% текста — маркированные списки
- **Жирный шрифт россыпью**: выделение каждого термина **жирным**
- **Эмодзи как структура**: 🚀 📌 ✅ как маркеры списков в серьёзном тексте
- **Markdown-артефакты**: `##`, `**`, `---` в тексте не предназначенном для рендеринга
- **Заголовки С Большой Буквы Каждого Слова**: калька с Title Case

---

## III. Правила перезаписи (Rewrite Rules)

### Универсальные (EN + RU)

1. **Убить em-dash**: заменить на запятую, точку с запятой, двоеточие, или перестроить предложение
2. **Разбить Rule of Three**: оставить 2 элемента или переформулировать
3. **Убить trailing participle**: сделать отдельным предложением или убрать
4. **Убить negative parallelism**: прямое утверждение вместо "не X, а Y"
5. **Разнообразить длину**: чередовать короткие (5-8 слов) и длинные (15-25 слов) предложения
6. **Убрать вводные-паразиты**: "Важно отметить" → просто написать утверждение

### Русскоязычные

| Что убить | Чем заменить |
|-----------|-------------|
| "является" | убрать связку: "Москва — столица" вместо "Москва является столицей" |
| "данный" | "этот", "такой", или убрать |
| "В рамках" | "В", "При", "Для", или перестроить |
| "осуществить X" | прямой глагол: "проверить" вместо "осуществить проверку" |
| "представляет собой" | тире или ничего |
| "оказывает влияние" | "влияет" |
| "играет роль" | "важен для" или конкретизировать |
| "Таким образом" | убрать или "Итого:" / "Значит," |
| "Стоит отметить" | убрать, написать факт напрямую |
| "В контексте X" | "для X", "при X", или убрать |
| "обеспечивает" | конкретный глагол: "даёт", "создаёт", "позволяет" |
| Цепочка Р.п. | разбить предлогами: "качество обслуживания для клиентов" |
| Деепричастный оборот ×2 | разбить на два предложения |
| Правило трёх | два элемента или абзац с пояснениями |

### Англоязычные

| Что убить | Чем заменить |
|-----------|-------------|
| "delve" | "look at", "examine", "explore" |
| "landscape" | name the specific domain |
| "leverage" | "use" |
| "streamline" | "simplify", "speed up" |
| "transformative" | describe the actual change |
| "seamless" | "smooth", "easy", or describe how |
| "unlock" | "enable", "allow", "open" |
| "robust" | "strong", "reliable", or specify |
| "I hope this finds you well" | cut entirely, start with substance |
| "in conclusion" | just state the conclusion |
| Trailing ", ensuring X" | new sentence: "This ensures X." |
| Em-dash parenthetical | use commas or restructure |

---

## IV. Detection Checklist

Use this checklist when reviewing text:

```
[ ] Banned words (EN): delve, tapestry, leverage, seamless, etc.
[ ] Banned words (RU): является, данный, обеспечивает, осуществляет, etc.
[ ] Banned phrases (EN): "important to note", "plays a key role", etc.
[ ] Banned phrases (RU): "В рамках", "Важно отметить", "Стоит подчеркнуть", etc.
[ ] Structural: Rule of Three present?
[ ] Structural: Trailing participle clauses?
[ ] Structural: Negative parallelism ("not just X, but Y")?
[ ] Structural (RU): Genitive chains (3+ in a row)?
[ ] Structural (RU): Nominalizations instead of verbs?
[ ] Structural (RU): Depricipal clause pileup?
[ ] Punctuation: Em-dash density (>1 per paragraph EN, >5/1000 chars RU)?
[ ] Punctuation: Smart/curly quotes?
[ ] Formatting: Excessive bold, emoji bullets, markdown artifacts?
[ ] Formatting: Title Case headings in Russian?
[ ] Sentence variety: all similar length? (burstiness check)
[ ] Tone: forced optimism at the end?
[ ] Tone: promotional language without substance?
[ ] Dialogue artifacts: "Конечно!", "Let me know", etc.?
[ ] English calques in Russian text?
```

---

## V. Severity Levels

- **CRITICAL** (instant fail): dialogue artifacts ("Конечно, я помогу!"), knowledge-cutoff disclaimers, em-dash density >8/1000, markdown artifacts in non-markdown context, "delve"
- **HIGH** (fix required): "является" density >2 per page, "В рамках" anywhere, banned phrase from top-20 list, Rule of Three + trailing participle in same paragraph
- **MEDIUM** (should fix): single banned word, minor genitive chain, one em-dash too many
- **LOW** (optional): borderline synonym variety, slightly formulaic structure

---

## VI. Context-Specific Presets

### Academic Russian (диссертация, статья)
- Allow: "Таким образом" (1x in conclusions), "В рамках" (1x in intro if specifying scope)
- Strict on: номинализация, цепочки Р.п., деепричастные нагромождения, "является"
- Extra rule: avoid anglicisms, prefer established Russian terminology

### Habr / Tech Blog
- Strict on: em-dash density, listicle structure, bold spam, emoji bullets
- Allow: some informal constructions, code terms
- Extra rule: vary section structures, intersperse personal narrative

### Telegram Post
- Strict on: dialogue artifacts, promotional language, calques
- Allow: short sentences, colloquial tone
- Extra rule: no "Важно отметить" — just say it

### Cold Outbound Email (EN)
- Zero em-dashes allowed
- Zero banned phrases from email category
- Strict on: "I hope this finds you well", "looking forward to hearing"
- Extra rule: first sentence = substance, not pleasantry

### Marketing Copy
- Strict on: all SaaS-speak (leverage, unlock, seamless, synergy)
- Strict on: Rule of Three, trailing participles
- Extra rule: replace every buzzword with a concrete claim

---

## VII. References

1. [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) — English catalog (community-maintained, updated frequently)
2. [Википедия:Признаки сгенерированности текста](https://ru.wikipedia.org/wiki/Википедия:Признаки_сгенерированности_текста) — Russian catalog
3. [crimeacs/ai-tells-validator](https://github.com/crimeacs/ai-tells-validator) — Claude Code skill with live Wikipedia prefetch + regex enforcement
4. [7 метрик AI-хуманизатора (Habr)](https://habr.com/ru/articles/1030384/) — Russian structural metrics: dash density, burstiness, genitive chains
5. [Wikipedia выпустила гайд (Habr)](https://habr.com/ru/articles/987440/) — Russian commentary on the Wikipedia guide

---

## VIII. Usage Examples

### Example 1: Russian academic text

**Before (flagged):**
> В рамках данного исследования важно отметить, что предложенный метод является эффективным инструментом, обеспечивающим существенное улучшение качества обслуживания клиентов компании, демонстрируя при этом устойчивость к различным возмущениям.

**Flags:**
- [PHRASE] "В рамках" → канцелярит
- [WORD] "данного" → канцелярит
- [PHRASE] "важно отметить" → дидактический маркер
- [WORD] "является" → избыточная связка
- [WORD] "обеспечивающим" → шаблонный глагол
- [STRUCTURE] цепочка Р.п. "улучшение качества обслуживания клиентов компании"
- [WORD] "демонстрируя" → шаблонный глагол

**After (clean):**
> Предложенный метод улучшает обслуживание клиентов и устойчив к возмущениям.

### Example 2: English outbound email

**Before (flagged):**
> I hope this finds you well. I wanted to reach out because we've built a transformative, seamless, and robust platform that helps companies leverage AI to unlock growth — driving efficiency across the entire pipeline.

**Flags:**
- [PHRASE] "I hope this finds you well"
- [PHRASE] "wanted to reach out"
- [WORD] "transformative" + "seamless" + "robust" → triple banned word
- [PATTERN] Rule of Three: "transformative, seamless, and robust"
- [WORD] "leverage"
- [WORD] "unlock"
- [PUNCTUATION] em-dash
- [PATTERN] trailing participle: ", driving efficiency"

**After (clean):**
> We built a tool that cuts pipeline review time from 4 hours to 20 minutes. Three teams at [Company] use it today. Worth a 10-min call this week?
