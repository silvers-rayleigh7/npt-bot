# Retrieval-Augmented Lesson — Implementation Plan

> **For agentic workers:** реализация по задачам. Общие модули и интеграцию делает главный агент;
> три ретривера (Task 3/4/5) пишутся параллельными субагентами по общим контрактам из Task 1.

**Goal:** GigaChat перед генерацией урока опирается на источники (сюжеты / программа / веб), не ломая MVP.

**Architecture:** три ретривера по единому контракту → `gather_context()` (параллельно, с таймаутом) →
блок «Материалы для опоры» в промпт урока. Всё в site-bar бэкенде. Мастер-флаг + инвариант «не блокирует».

**Tech Stack:** Python 3.9 (сервер), FastAPI, requests, GigaChat Embeddings, ThreadPoolExecutor.

## Global Constraints

- Никаких новых сервисов — только `site-bar/server/`. Деплой: `scp app.py + retrieval/` → `systemctl restart tropa-bot-api`.
- Инвариант регресса: `/api/lesson` при `RETRIEVAL_ENABLED=0` == текущее поведение байт-в-байт по логике.
- Каждый ретривер при любой ошибке/таймауте возвращает `[]`, НЕ бросает исключение наружу.
- Единые контракты из `base.py` — не менять сигнатуры между задачами.
- Python 3.9: без `str | None` в рантайме без `from __future__ import annotations`; dataclasses ок.

---

### Task 1: Контракты + клиент эмбеддингов (foundation, главный агент)

**Files:**
- Create: `site-bar/server/retrieval/__init__.py` (пустой пока, заполнится в Task 6)
- Create: `site-bar/server/retrieval/base.py`
- Create: `site-bar/server/retrieval/embeddings.py`
- Test: `site-bar/server/tests/test_retrieval_base.py`

**Produces:** `RetrievalQuery`, `Snippet`, `Retriever` (Protocol), `EmbeddingsClient.embed()`, `cosine()`.

- [ ] base.py: `RetrievalQuery`, `Snippet` (dataclasses), `Retriever` Protocol (`name`, `retrieve(q, limit)->list[Snippet]`).
- [ ] embeddings.py: `EmbeddingsClient(auth_key, scope)` с `embed(texts:list[str])->list[list[float]]` через GigaChat `/embeddings` (переиспользует токен-логику GigaChatProvider), `cosine(a,b)->float`. При ошибке — `RuntimeError` (ловится ретривером).
- [ ] Тест: Snippet/Query создаются; `cosine([1,0],[1,0])==1.0`, `cosine([1,0],[0,1])==0.0`.
- [ ] Commit.

### Task 2: Индекс сюжетов (data, главный агент)

**Files:**
- Create: `build_indexes.py` (корень репо, рядом с build.py)
- Create: `site-bar/server/data/storylines_index.json` (генерится)

**Consumes:** `EmbeddingsClient` (Task 1), `content/storylines/*`.

- [ ] `build_indexes.py`: читает сюжеты (title, summary/first-para, tags, region, slug), считает эмбеддинг по «title + summary + tags», пишет `[{slug,title,summary,tags,region,url,embedding}]` в json.
- [ ] Прогон: сгенерить `storylines_index.json` (42 записи). Проверить: длина эмбеддинга > 0, 42 записи.
- [ ] Commit (json + скрипт).

### Task 3: StorylineRetriever (параллельный агент A)

**Files:**
- Create: `site-bar/server/retrieval/storyline_retriever.py`
- Test: `site-bar/server/tests/test_storyline_retriever.py`

**Consumes:** `base.py` контракты, `EmbeddingsClient`, `data/storylines_index.json`.
**Produces:** `StorylineRetriever` (name="storylines").

- [ ] Загружает индекс при инициализации. `retrieve(q, limit=3)`: эмбеддит `q.text`, косинус к индексу, топ-limit со score>порог → Snippet(source="сюжет", url=slug). Fallback: keyword-матч по tags/title если эмбеддинги недоступны. При ошибке → `[]`.
- [ ] Тест на мок-индексе (2 записи, фиктивные эмбеддинги): релевантная запись возвращается первой; при пустом индексе → `[]`.
- [ ] Commit.

### Task 4: ProgramRetriever + сид индекса программы (параллельный агент B)

**Files:**
- Create: `site-bar/server/retrieval/program_retriever.py`
- Create: `site-bar/server/data/programs_index.json` (курируемый сид)
- Test: `site-bar/server/tests/test_program_retriever.py`

**Consumes:** `base.py` контракты.
**Produces:** `ProgramRetriever` (name="программа").

- [ ] `programs_index.json`: массив `{grade, subject, section, themes:[...], keywords:[...], note}` — стартовый набор по предметам формы (физика/биология/география/химия/математика/экология/астрономия/окружающий мир/история) для 1–11, темы из открытых ФГОС/примерных программ и учебников (структура, ключевые термины). Сид — покрыть хотя бы по 3–5 тем на предмет×ступень.
- [ ] `ProgramRetriever.retrieve(q)`: матч по grade+subject, ранжирование тем по совпадению `q.topic`/`q.text` с themes/keywords → Snippet(source="программа", text=«N класс, <предмет>, раздел …; тема …»). Без grade+subject → `[]`.
- [ ] Тест: запрос (6, биология, «опыление») → сниппет с разделом жизнедеятельности растений; неизвестный предмет → `[]`.
- [ ] Commit.

### Task 5: WebRetriever (параллельный агент C)

**Files:**
- Create: `site-bar/server/retrieval/web_retriever.py`
- Test: `site-bar/server/tests/test_web_retriever.py`

**Consumes:** `base.py` контракты, env `WEB_SEARCH_API_KEY`.
**Produces:** `WebRetriever` (name="веб").

- [ ] `WebRetriever(api_key)`: если ключ пуст → `retrieve()` всегда `[]` (выключен). Иначе поиск по «<topic> <subject> для детей научпоп», берёт 1–2 результата → Snippet(source="веб", title, text=сниппет, url). Таймаут запроса ≤ 5с; при ошибке → `[]`. Провайдер поиска — через абстракцию `_search(query)->list[dict]` (реализация под доступный API; по умолчанию Tavily-совместимый REST).
- [ ] Тест: без ключа → `[]`; с мок-`_search` → корректные Snippet с url.
- [ ] Commit.

### Task 6: gather_context — сборка (интеграция, главный агент)

**Files:**
- Modify: `site-bar/server/retrieval/__init__.py`
- Test: `site-bar/server/tests/test_gather_context.py`

**Consumes:** все ретриверы, флаги env.
**Produces:** `build_retrievers()`, `gather_context(query, timeout, char_budget)->str`.

- [ ] `build_retrievers()`: собирает включённые по флагам (`RETRIEVER_STORYLINES/PROGRAM/WEB`). `gather_context()`: ThreadPoolExecutor, на каждый ретривер `RETRIEVAL_TIMEOUT`, собирает Snippet-ы, сортирует по score, режет по `char_budget`, форматирует markdown-блок «Материалы для опоры». Всё пусто → "".
- [ ] Тест: два мок-ретривера (один падает) → блок содержит сниппеты рабочего; все пустые → "".
- [ ] Commit.

### Task 7: Интеграция в пайплайн урока (интеграция, главный агент)

**Files:**
- Modify: `site-bar/server/app.py:lesson()`
- Modify: `site-bar/server/lesson_prompt.md`

**Consumes:** `gather_context`, `RETRIEVAL_ENABLED`.

- [ ] app.py: в `lesson()` если `RETRIEVAL_ENABLED` → `ctx = gather_context(RetrievalQuery(...))`; при непустом — добавить в user-сообщение блоком перед «Данные формы». Обёрнуто в try/except (retrieval не роняет урок). `LessonOut` дополнить полем `sources: list[str]` (заголовки/url для показа под уроком, опц.).
- [ ] lesson_prompt.md: добавить правило — «если дан блок „Материалы для опоры“ — опирайся на него; факты из „[веб]“ приводи с источником; ничего не выдумывай сверх материалов, но и не ограничивайся ими».
- [ ] Тест локально: `RETRIEVAL_ENABLED=0` → урок как раньше; `=1` c мок-контекстом → урок использует опору.
- [ ] Commit.

### Task 8: Деплой по инкрементам + верификация (главный агент)

- [ ] scp `app.py`, `lesson_prompt.md`, `retrieval/`, `data/` → сервер; `pip install`-зависимостей нет новых. Прописать флаги в `.env` c `RETRIEVAL_ENABLED=0`. Restart. Проверить `/api/lesson` == прежнее.
- [ ] Включить `RETRIEVER_STORYLINES=1` + `RETRIEVAL_ENABLED=1`. Проверить урок (тень/солнечные часы → подтянулся наш сюжет). Тройная верификация.
- [ ] Включить `RETRIEVER_PROGRAM=1`. Проверить привязку к разделу программы.
- [ ] Веб — только если задан `WEB_SEARCH_API_KEY` (уточнить у заказчика провайдер/ключ). Иначе оставить выключенным.
- [ ] Коммит + пуш в репо Даниила + зеркало.
