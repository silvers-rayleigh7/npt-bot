#!/usr/bin/env python3
"""Углубление уровня «Глубже» в сюжетах.

Разбор 13.07: «если глубже — то глубже, надо по-нормальному объяснять». Инструмент
расширяет последний уровень сюжета: механизм до первопричины, формулы с расшифровкой,
количественная сторона, привязка к самому объекту.

Безопасность: опубликованный текст НЕ перезаписывается. Результат кладётся в
drafts/<slug>.md на ревью — применять вручную после вычитки.

Запуск:
    python3 deepen_storyline.py --slug vishtynec        # один сюжет
    python3 deepen_storyline.py --thinnest 10           # десять самых тонких
    python3 deepen_storyline.py --apply vishtynec       # вклеить готовый черновик
"""
import argparse
import glob
import os
import re
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(ROOT, "site-bar", "server")
DRAFTS = os.path.join(ROOT, "drafts")
load_dotenv(os.path.join(SERVER, ".env"))
sys.path.insert(0, SERVER)
from providers import build_providers, generate  # noqa: E402

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)

PROMPT = """Ты — научный редактор проекта «Тропа»: научно-популярные сюжеты о конкретных местах
в каноне «Кванта» и «Науки и жизни» — через первопричину и наглядную аналогию.

Тебе дан сюжет целиком. Перепиши ТОЛЬКО последний уровень («Глубже»), сделав его
по-настоящему глубоким. Требования:

1. ОБЪЁМ: 3500–5000 знаков. Сейчас этот уровень слишком краток — читатель уходит
   раззадоренным, но без объяснения.
2. МЕХАНИЗМ до первопричины: не «так происходит», а почему именно так, шаг за шагом.
   Что стоит за явлением на уровне физики/химии/биологии.
3. ФОРМУЛЫ обязательны, если тема их допускает: в LaTeX между $…$ (в строке) или
   $$…$$ (отдельной строкой). КАЖДОЕ обозначение расшифруй словами. Формула без
   расшифровки — брак.
4. КОЛИЧЕСТВЕННАЯ сторона: порядки величин, характерные числа, оценки. Каждое число
   должно быть проверяемым; при неуверенности пиши «примерно», «порядка».
5. ПРИВЯЗКА К ОБЪЕКТУ: общее явление должно объяснять, почему ИМЕННО ЭТОТ объект
   такой. Не пересказ общей физики, а причинная связь с конкретным местом.
6. Сохрани всё ценное из текущего текста — дополняй, а не выбрасывай.
7. Сохрани сноски вида [^метка] на источники и добавь новые для новых чисел.
   Определения сносок ([^метка]: текст) выноси в самый конец.
8. В конце оставь подраздел «**Открытый вопрос**» — живой нерешённый вопрос по теме.

ТИПОГРАФИКА: кавычки «ёлочки», длинное тире —, буква ё везде, где она есть
(лёд, объём, растёт, чёрный). Подзаголовки внутри уровня — жирной строкой, не решётками.

ДЕРЖИСЬ ТЕМЫ СЮЖЕТА. Углубляй именно её, не уходи в соседние: у «Расстояния до звезды»
тема — параллакс и как его измеряют, а не метрика пространства-времени. Если тянет
рассказать смежное — вернись к заявленному объекту.

НЕ ВЫДУМЫВАЙ фактов. Если данных не хватает — рассуждай о механизме, а не сочиняй числа.

Верни ТОЛЬКО текст уровня «Глубже» в markdown, без заголовка «## Глубже» и без пояснений.
"""


def load_one(slug):
    p = os.path.join(ROOT, "content", "storylines", f"{slug}.md")
    raw = open(p, encoding="utf-8").read()
    m = FM_RE.match(raw)
    fm, body = m.group(1), m.group(2)
    parts = re.split(r"(?m)^##\s+(.+?)\s*$", body)
    levels = [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
    title = (re.search(r"^title:\s*(.+)$", fm, re.M) or re.match("", "")).group(1).strip()
    return {"path": p, "raw": raw, "fm": fm, "body": body, "levels": levels, "title": title}


def facts_for(title, providers):
    """Проверенные факты об объекте — из наших доверенных источников."""
    try:
        from retrieval import build_retrievers, gather_context
        from retrieval.base import RetrievalQuery
        os.environ.setdefault("RETRIEVER_WEB", "1")
        return gather_context(RetrievalQuery(topic=title, text=title),
                              retrievers=build_retrievers())
    except Exception:
        return ""


VERIFY_PROMPT = """Ты — придирчивый научный рецензент. Перед тобой черновик уровня «Глубже»
научно-популярного сюжета и список проверенных фактов из источников.

Твоя задача — вычистить недостоверное. Действуй так:

1. Найди КАЖДОЕ число и КАЖДУЮ формулу в тексте.
2. Для каждого спроси: это подтверждается фактами из источников, либо это стандартное
   школьное/учебниковое соотношение, известное всем? Если ни то, ни другое — оно выдумано.
3. Выдуманные коэффициенты («K ≈ 0.01 для песчаников»), сочинённые «эмпирические формулы»
   и игрушечные расчёты, которые тут же опровергаются, — УДАЛИ. Замени качественным
   объяснением механизма: как влияет, от чего зависит, в какую сторону меняется.
3а. РАЗМЕРНОСТИ: проверь каждую формулу на согласованность единиц. Классическая ошибка —
   метрика Минковского без c² при dt². Формула с несходящимися размерностями — брак,
   исправь её или убери.
4. Стандартные физические соотношения (закон сохранения, определение плотности, формулы
   школьного курса) оставляй — они не требуют источника.
5. Числа из блока проверенных фактов — сохрани и по возможности используй шире.
6. Не сокращай текст ради сокращения: убрав недостоверное, разверни объяснение механизма,
   чтобы объём остался прежним.

7. СНОСКИ [^метка] в тексте не удаляй — они указывают на источники утверждений.
   Если убираешь утверждение целиком, ссылку убирай вместе с ним; в остальных случаях сохраняй.

Верни ТОЛЬКО исправленный текст в markdown, без заголовков уровня и без комментариев.
"""


def verify(draft, facts, providers):
    """Второй проход: вычищает выдуманные числа и формулы.

    Первая версия инструмента сочиняла коэффициенты и «эмпирические формулы» — выглядит
    убедительно, но это брак: сюжеты читает математик. Дешевле проверить, чем краснеть.
    """
    try:
        out, _ = generate(
            [{"role": "system", "content": VERIFY_PROMPT},
             {"role": "user", "content": (f"{facts}\n\n" if facts else "")
              + f"Черновик:\n\n{draft}"}],
            providers, max_tokens=4000, temperature=0.0,
        )
        return (out or "").strip() or draft
    except Exception:
        return draft


def deepen(slug, providers):
    it = load_one(slug)
    facts = facts_for(it["title"], providers)
    body_txt = "\n\n".join(f"## {n}\n{t.strip()}" for n, t in it["levels"])

    # Сноски перечисляем явно и требуем сохранить: без этого модель систематически
    # теряет их при переписывании, и сюжет лишается бейджа «со ссылками на источники».
    # Ссылки берём из ПЕРЕПИСЫВАЕМОГО уровня. Раньше брал из всего сюжета — и требовал
    # от «Глубже» ссылки, которые живут в «Как это работает»: инструмент рапортовал
    # потери там, где ничего не терялось.
    old_defs, _ = _footnotes(it["raw"])
    _, old_refs = _footnotes(it["levels"][-1][1])
    keep = ""
    if old_refs:
        listing = "\n".join(f"[^{k}] — {old_defs.get(k, '')[:120]}" for k in sorted(old_refs))
        keep = ("\n\nОБЯЗАТЕЛЬНО сохрани в новом тексте ссылки на эти источники "
                "(каждую поставь там, где утверждение на неё опирается):\n" + listing + "\n")

    user = (f"Сюжет «{it['title']}».\n\n"
            + (f"{facts}\n\n" if facts else "")
            + f"Текущий текст сюжета:\n\n{body_txt}{keep}")
    out, _ = generate(
        [{"role": "system", "content": PROMPT}, {"role": "user", "content": user}],
        providers, max_tokens=4000, temperature=0.45,
    )
    draft = (out or "").strip()
    draft = verify(draft, facts, providers)          # вычищаем выдуманное
    draft, restored = reattach_footnotes(draft, old_defs, old_refs, it["levels"][-1][1])
    if restored:
        print("      вернул ссылки: " + ", ".join(sorted(restored)))
    draft = polish(draft)
    return it, draft


def reattach_footnotes(draft, old_defs, old_refs, old_body=""):
    """Возвращает потерянные ссылки на источники в текст — кодом, а не просьбой к модели.

    Явное требование в промпте не помогло: 12 черновиков из 12 всё равно теряли ссылки.
    Поэтому ищем сами: берём значимые слова из определения сноски и ставим ссылку в конец
    того абзаца, который сильнее всего с ними пересекается. Не нашли подходящего — значит
    утверждения в тексте больше нет, и ссылку возвращать некуда.
    """
    _, have = _footnotes(draft)
    lost = old_refs - have
    if not lost:
        return draft, set()

    paras = [p for p in draft.split("\n\n")]
    ok_idx = [i for i, p in enumerate(paras)
              if not p.lstrip().startswith("[^") and not p.strip().startswith("$$")
              and len(p.strip()) > 80]
    if not ok_idx:
        return draft, set()

    # Ориентир — СТАРЫЙ абзац, который ссылался на источник, а не описание источника.
    # Словарное совпадение здесь ошибается: у мамонтов ссылка на радиоуглеродный анализ
    # встала на утверждение про уран-свинцовый метод — общие слова «датирование», «возраст»
    # совпали, а смысл нет. Сравниваем смыслы эмбеддингами.
    anchors = {}
    for key in sorted(lost):
        m = re.search(rf"[^\n]*\[\^{re.escape(key)}\](?!:)[^\n]*", old_body or "")
        if m:
            anchors[key] = m.group(0)

    if not anchors:
        return draft, set()

    try:
        from retrieval.embeddings import EmbeddingsClient, cosine
        client = EmbeddingsClient(auth_key=os.environ["GIGACHAT_AUTH_KEY"],
                                  scope=os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_CORP"))
        keys = list(anchors)
        vecs = client.embed([anchors[k] for k in keys] + [paras[i] for i in ok_idx])
    except Exception:
        return draft, set()                   # без эмбеддингов не гадаем

    restored = set()
    av, pv = vecs[:len(keys)], vecs[len(keys):]
    for key, a in zip(keys, av):
        scored = sorted(((cosine(a, v), i) for v, i in zip(pv, ok_idx)), reverse=True)
        score, idx = scored[0]
        # Порог намеренно высокий. Пробовал 0.72 — радиоуглеродная ссылка встала на
        # утверждение про уран-свинцовый метод: для эмбеддингов это близкие темы,
        # а для читателя — ссылка на источник, который ничего не подтверждает.
        # Привязка источника к утверждению остаётся редакторским решением.
        if score < 0.88:
            continue
        paras[idx] = re.sub(r"([.!?])(\s*)$", rf"[^{key}]\1\2", paras[idx].rstrip(), count=1)
        restored.add(key)
    return "\n\n".join(paras), restored


def polish(text: str) -> str:
    """Приводит черновик к типографике проекта: «ёлочки», тире, подзаголовки жирным.

    Механические огрехи модели чинятся кодом, а не повторным запросом — надёжнее и дешевле.
    """
    # заголовок уровня модель добавляет вопреки инструкции
    text = re.sub(r"^#{2,4}\s*Глубже\s*$", "", text, flags=re.M)
    # подзаголовки внутри уровня в проекте — жирной строкой, а не ###
    text = re.sub(r"^#{3,4}\s*(.+?)\s*$", r"**\1**", text, flags=re.M)
    # Формулы выводим из-под типографики: внутри $…$ дефис — это минус, и замена
    # его на тире ломает математику (поймано на регрессионной модели дендрохронологии).
    guard = []

    def _stash(m):
        guard.append(m.group(0))
        return f"\x00{len(guard) - 1}\x00"

    text = re.sub(r"\$\$[^$]+\$\$|\$[^$\n]+\$", _stash, text)

    # лапки → ёлочки
    text = re.sub(r'"([^"\n]{1,80})"', r"«\1»", text)
    # дефис как тире между словами → длинное тире; маркер списка в начале строки не трогаем
    text = re.sub(r"(?<!^)(?<!\n)(\S)\s+-\s+(\S)", r"\1 — \2", text, flags=re.M)
    # среднее тире – модель ставит вместо длинного —
    text = re.sub(r"(?<=[а-яё])\s+–\s+", " — ", text)
    # ****жирный**** — модель дублирует маркеры, в вёрстке остаются лишние звёздочки
    text = re.sub(r"\*{3,}", "**", text)
    # голые --- как разделитель: в наших сюжетах горизонтальных линеек нет
    text = re.sub(r"(?m)^\s*-{3,}\s*$\n?", "", text)

    for i, frag in enumerate(guard):          # возвращаем формулы как были
        text = text.replace(f"\x00{i}\x00", frag)
    # буква ё: только однозначные слова, где замена не меняет смысл
    for a, b in (("лед", "лёд"), ("Лед", "Лёд"), ("льда", "льда"), ("объем", "объём"),
                 ("Объем", "Объём"), ("растет", "растёт"), ("тает", "тает"),
                 ("темпера", "темпера"), ("черн", "чёрн"), ("Черн", "Чёрн"),
                 ("теплот", "теплот"), ("плотн", "плотн"), ("зелен", "зелён"),
                 ("подъем", "подъём"), ("нагрев", "нагрев")):
        if a != b:
            text = re.sub(rf"\b{a}", b, text)
    return text.strip()


def write_draft(it, slug, new_deep):
    os.makedirs(DRAFTS, exist_ok=True)
    dst = os.path.join(DRAFTS, f"{slug}.md")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(new_deep + "\n")
    old = len(it["levels"][-1][1].strip())

    # Предупреждаем сразу: если новый текст перестал ссылаться на источники, которые
    # были в сюжете, он потеряет бейдж «со ссылками» — это заметно только при вычитке.
    _, old_refs = _footnotes(it["raw"])
    _, new_refs = _footnotes(new_deep)
    dropped = old_refs - new_refs
    warn = f"  ⚠️ перестал ссылаться на: {', '.join(sorted(dropped))}" if dropped else ""
    print(f"  {slug:26} «Глубже» {old} → {len(new_deep)} симв  → drafts/{slug}.md{warn}")
    return dst


def _footnotes(text):
    """({метка: определение}, {метки-ссылки})."""
    defs = dict(re.findall(r"^\[\^([^\]]+)\]:\s*(.+)$", text, re.M))
    # Определение — только в начале строки. Ссылка в середине текста может стоять
    # перед двоеточием (например, перед таблицей) — это по-прежнему ссылка.
    refs = set(re.findall(r"(?<!\n)\[\^([^\]]+)\]", text)) | \
           set(re.findall(r"(?m)(?<=.)\[\^([^\]]+)\]", text))
    refs -= {k for k in defs if not re.search(r"(?m)[^\n]\[\^%s\]" % re.escape(k), text)}
    return defs, refs


def apply_draft(slug):
    """Вклеивает вычитанный черновик вместо последнего уровня сюжета.

    Определения сносок лежат в конце файла — то есть ПОСЛЕ последнего уровня, но
    относятся ко всем уровням сразу. Наивная замена хвоста уничтожала источники
    предыдущих уровней (поймано на Батагайском провале: ссылка осталась, определение
    исчезло, читатель молча потерял источник). Поэтому определения переносим.
    """
    it = load_one(slug)
    draft = open(os.path.join(DRAFTS, f"{slug}.md"), encoding="utf-8").read().strip()
    last_name = it["levels"][-1][0]

    old_defs, _ = _footnotes(it["raw"])
    draft_defs, _ = _footnotes(draft)
    body = re.sub(r"^\[\^[^\]]+\]:.*$", "", draft, flags=re.M).strip()

    head, _sep, _tail = it["raw"].rpartition(f"## {last_name}")
    merged = {**old_defs, **draft_defs}                 # новые определения важнее старых
    _, refs = _footnotes(f"{head}## {last_name}\n\n{body}")
    used = {k: v for k, v in merged.items() if k in refs}
    tail = "\n\n".join(f"[^{k}]: {v}" for k, v in used.items())
    new = f"{head}## {last_name}\n\n{body}\n\n{tail}\n" if tail else \
          f"{head}## {last_name}\n\n{body}\n"
    open(it["path"], "w", encoding="utf-8").write(new)

    # контроль целостности: висячих ссылок быть не должно
    defs2, refs2 = _footnotes(new)
    dangling = refs2 - set(defs2)
    lost = set(old_defs) - set(defs2) - (set(old_defs) - refs2)
    status = "OK" if not dangling and not lost else f"⚠️ висячие={dangling} утрачены={lost}"
    print(f"  применено: {slug} («{last_name}») — сносок {len(used)}, {status}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--thinnest", type=int)
    ap.add_argument("--apply")
    a = ap.parse_args()

    if a.apply:
        apply_draft(a.apply)
        return

    slugs = []
    if a.slug:
        slugs = [a.slug]
    elif a.thinnest:
        rows = []
        for p in sorted(glob.glob(os.path.join(ROOT, "content", "storylines", "*.md"))):
            s = os.path.basename(p)[:-3]
            try:
                it = load_one(s)
                rows.append((len(it["levels"][-1][1].strip()), s))
            except Exception:
                continue
        rows.sort()
        slugs = [s for _n, s in rows[: a.thinnest]]
    else:
        ap.error("укажи --slug, --thinnest N или --apply")

    providers = build_providers()
    for s in slugs:
        try:
            it, new_deep = deepen(s, providers)
            write_draft(it, s, new_deep)
        except Exception as e:
            print(f"  {s:26} ОШИБКА: {str(e)[:70]}")


if __name__ == "__main__":
    main()
