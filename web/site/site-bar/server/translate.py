"""Пайплайн перевода: DeepL → наш стилевой агент.

Схема:
    translate()  — точный перевод (DeepL, при отсутствии ключа — GigaChat)
    stylize()    — приведение к нашему голосу («Квант» / «Наука и жизнь»)
    localize()   — перевод + стиль одной операцией, для готового текста

Для поискового запроса стиль не нужен — там достаточно translate().
Любая ошибка возвращает исходный текст: перевод не должен ломать пайплайн урока.
"""
from __future__ import annotations

import os

import requests

# Бесплатный тариф DeepL живёт на api-free, платный — на api. Определяем по суффиксу ключа.
_DEEPL_FREE = "https://api-free.deepl.com/v2/translate"
_DEEPL_PRO = "https://api.deepl.com/v2/translate"

STYLE_PROMPT = (
    "Ты — редактор научно-популярного проекта «Тропа». Приведи текст к нашему голосу: "
    "канон «Кванта» и «Науки и жизни» — через первопричину и наглядную аналогию, живо и точно, "
    "без канцелярита и без выхода за школьный курс. Не добавляй фактов, которых нет в исходнике, "
    "и не выбрасывай существенное. Верни только переработанный текст, без пояснений."
)


def _deepl_url(key: str) -> str:
    return _DEEPL_FREE if key.strip().endswith(":fx") else _DEEPL_PRO


def translate(text: str, target: str = "EN", source: str = None, timeout: float = 8.0) -> str:
    """Точный перевод. DeepL при наличии ключа, иначе GigaChat. Сбой → исходный текст."""
    text = (text or "").strip()
    if not text:
        return ""

    key = os.environ.get("DEEPL_API_KEY", "").strip()
    if key:
        try:
            data = {"text": [text], "target_lang": target.upper()}
            if source:
                data["source_lang"] = source.upper()
            r = requests.post(_deepl_url(key), json=data, timeout=timeout,
                              headers={"Authorization": f"DeepL-Auth-Key {key}"})
            r.raise_for_status()
            out = ((r.json() or {}).get("translations") or [{}])[0].get("text", "")
            if out.strip():
                return out.strip()
        except Exception:
            pass                       # молча падаем на запасной переводчик

    return _translate_gigachat(text, target, timeout)


def _translate_gigachat(text: str, target: str, timeout: float = 8.0) -> str:
    """Запасной переводчик — уже подключённая модель. Ключей не требует."""
    lang = {"EN": "английский", "RU": "русский"}.get(target.upper(), target)
    try:
        from providers import build_providers, generate
        out, _ = generate(
            [{"role": "system", "content":
              f"Ты переводчик. Переведи текст на {lang} язык. "
              f"Верни ТОЛЬКО перевод, без пояснений и кавычек."},
             {"role": "user", "content": text}],
            build_providers(), max_tokens=300, temperature=0.0,
        )
        return (out or "").strip().strip('"') or text
    except Exception:
        return text


def stylize(text: str, timeout: float = 20.0) -> str:
    """Приводит текст к нашему голосу. Сбой → исходный текст."""
    text = (text or "").strip()
    if not text:
        return ""
    try:
        from providers import build_providers, generate
        out, _ = generate(
            [{"role": "system", "content": STYLE_PROMPT},
             {"role": "user", "content": text}],
            build_providers(), max_tokens=1200, temperature=0.4,
        )
        return (out or "").strip() or text
    except Exception:
        return text


def localize(text: str, target: str = "RU") -> str:
    """Полный пайплайн для готового текста: точный перевод, затем наш стиль."""
    return stylize(translate(text, target=target))


def _has_cyrillic(s: str) -> bool:
    import re
    return bool(re.search(r"[А-Яа-яЁё]", s or ""))


def shape_query(text_en: str, timeout: float = 10.0) -> str:
    """Наш агент формует из перевода поисковую фразу: 2–3 слова, существительные.

    Дословный перевод «Why does a shadow change its length» для поиска картинок бесполезен —
    нужен предметный термин вроде `tree shadow`. Это работа стилевого слоя, только цель
    не читабельность, а попадание в термины фотобанка.
    """
    text_en = (text_en or "").strip()
    if not text_en:
        return ""
    try:
        from providers import build_providers, generate
        out, _ = generate(
            [{"role": "system", "content":
              "You turn a school lesson topic into a short English image-search query. "
              "Reply with 2-3 words, a concrete noun phrase naming the OBJECT or PHENOMENON "
              "to photograph. No questions, no verbs, no articles, no explanation. "
              "Examples: 'lake formation' -> 'mountain lake'; "
              "'why does a shadow change length' -> 'tree shadow'; "
              "'pollination of flowers' -> 'bee pollinating flower'."},
             {"role": "user", "content": text_en}],
            build_providers(), max_tokens=16, temperature=0.0,
        )
        q = (out or "").strip().strip('".,:;!?')
        words = [w for w in q.split() if w.strip()]
        return " ".join(words[:3]) if words else text_en
    except Exception:
        return text_en


def search_query_en(topic: str, subject: str = "") -> str:
    """Тема урока → английский поисковый запрос: DeepL переводит, наш агент формует.

    Викисклад почти весь англоязычный: названия, описания, категории. «образование озёр»
    как русская фраза даёт архивные журналы, а `mountain lake` — реальные озёра.
    """
    src = " ".join(p for p in (topic, subject) if p and p.strip()).strip()
    if not src:
        return ""
    en = translate(src, target="EN")
    if _has_cyrillic(en):              # переводчик не справился — формуем из оригинала
        en = src
    q = shape_query(en)
    return "" if _has_cyrillic(q) else q
