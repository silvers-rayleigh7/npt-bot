"""Определение места по координатам — чтобы бот рассказывал про ЛЮБУЮ точку, а не только про наши сюжеты.

Источники (оба без ключа):
  • Nominatim (OSM) — обратный геокодинг: что это за место (город/район/регион).
  • Overpass (OSM) — примечательные объекты вокруг: природа, парки, музеи, памятники.

Инвариант: любая ошибка/таймаут гасится, возвращается пустой результат. Бот всё равно ответит —
модель расскажет про местность по названию, а если и его нет — предложит задать тему.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

try:
    from claude_tg.geo_match import haversine_m, nearest_storylines, format_distance
except Exception:  # локальные тесты вне пакета
    from geo_match import haversine_m, nearest_storylines, format_distance

_UA = "TropaBot/1.0 (+https://tropa.fmin.xyz)"


def _get_json(url: str, params: dict = None, data: bytes = None, timeout: float = 8.0):
    """GET/POST + JSON. Только stdlib — в venv бота нет requests."""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, data=data, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

# Наши сюжеты показываем основным ответом только если до них реально дойти/доехать за минуты.
# Дальше — рассказываем про саму местность, где человек стоит.
NEAR_KM = 5.0
# Если наша точка не рядом, но в разумной досягаемости — упоминаем одной строкой как бонус.
MENTION_KM = 30.0

# Что считаем примечательным вокруг (теги OSM). Только именованные объекты и без тяжёлых
# полигональных слоёв (леса/болота) — публичный Overpass на них уходит в таймаут.
_OVERPASS_TPL = """
[out:json][timeout:{t}];
(
  node(around:{r},{lat},{lon})["natural"~"^(peak|water|spring|cave_entrance|beach|volcano)$"]["name"];
  way(around:{r},{lat},{lon})["natural"="water"]["name"];
  node(around:{r},{lat},{lon})["tourism"~"^(museum|attraction|viewpoint|artwork)$"]["name"];
  node(around:{r},{lat},{lon})["historic"]["name"];
  way(around:{r},{lat},{lon})["leisure"="park"]["name"];
);
out center tags {lim};
"""

# Публичные инстансы Overpass по приоритету — первый часто перегружен.
_OVERPASS_HOSTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)

_KIND_RU = {
    # природа
    "peak": "вершина", "water": "водоём", "spring": "родник", "cave_entrance": "пещера",
    "beach": "пляж", "glacier": "ледник", "volcano": "вулкан", "wood": "лес",
    "wetland": "болото", "scrub": "заросли",
    # туризм и отдых
    "museum": "музей", "attraction": "достопримечательность",
    "viewpoint": "смотровая", "artwork": "арт-объект", "park": "парк",
    # историческое
    "memorial": "мемориал", "monument": "памятник", "castle": "крепость",
    "ruins": "руины", "archaeological_site": "археологический памятник",
    "church": "храм", "manor": "усадьба", "tomb": "захоронение",
    "building": "историческое здание", "yes": "исторический объект",
}


# Кэш по округлённым координатам (~100 м): публичные OSM-сервисы троттлят повторные запросы.
_CACHE = {}
_CACHE_MAX = 256


def _cache_key(prefix: str, lat: float, lon: float) -> str:
    return f"{prefix}:{lat:.3f},{lon:.3f}"


def _cached(key: str, produce):
    """Кэшируем ТОЛЬКО успешные ответы: иначе разовый таймаут источника
    навсегда закрепил бы пустой результат для этой точки."""
    if key in _CACHE:
        return _CACHE[key]
    val = produce()
    if val:
        if len(_CACHE) >= _CACHE_MAX:
            _CACHE.clear()
        _CACHE[key] = val
    return val


def reverse_place(lat: float, lon: float, timeout: float = 6.0) -> dict:
    """Что это за место: {'name': 'Иннополис, Татарстан', 'country': 'Россия'} или {}."""
    try:
        d = _get_json(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json",
                    "accept-language": "ru", "zoom": 14},
            timeout=timeout,
        ) or {}
        a = d.get("address", {}) or {}
        parts = [a.get(k) for k in
                 ("hamlet", "village", "town", "city", "suburb", "municipality",
                  "county", "state", "region")]
        name = ", ".join([p for p in parts if p][:3])
        return {"name": name or (d.get("display_name") or "").split(",")[0],
                "country": a.get("country", "")}
    except Exception:
        return {}


def nearby_objects(lat: float, lon: float, radius_m: int = 3000,
                   limit: int = 8, timeout: float = 10.0) -> list:
    """Примечательные объекты вокруг: [{'name','kind','dist_m'}], отсортировано по близости."""
    q = _OVERPASS_TPL.format(t=int(timeout), r=int(radius_m), lat=lat, lon=lon, lim=limit * 4)
    body = urllib.parse.urlencode({"data": q}).encode("utf-8")
    elements = []
    for host in _OVERPASS_HOSTS:          # первый инстанс часто перегружен — пробуем зеркало
        try:
            elements = (_get_json(host, data=body, timeout=timeout) or {}).get("elements", []) or []
            if elements:
                break
        except Exception:
            continue
    if not elements:
        return []

    out, seen = [], set()
    for e in elements:
        tags = e.get("tags", {}) or {}
        nm = tags.get("name:ru") or tags.get("name")
        if not nm or nm in seen:
            continue
        seen.add(nm)
        raw_kind = (tags.get("natural") or tags.get("tourism")
                    or tags.get("historic") or tags.get("leisure") or "")
        c = e.get("center") or {}
        elat, elon = e.get("lat", c.get("lat")), e.get("lon", c.get("lon"))
        dist = haversine_m(lat, lon, elat, elon) if elat and elon else None
        out.append({"name": nm, "kind": _KIND_RU.get(raw_kind, raw_kind), "dist_m": dist})
    out.sort(key=lambda x: x["dist_m"] if x["dist_m"] is not None else 9e9)
    return out[:limit]


def build_geo_prompt(lat: float, lon: float, content_dir: str, near_km: float = NEAR_KM,
                     near: list = None) -> str:
    """Готовый [ГЕО]-промпт для модели. Всегда даёт, о чём говорить: либо наши сюжеты рядом,
    либо сама местность с её объектами.

    `near` (опц.) — заранее посчитанный список ближайших сюжетов (сайт передаёт его из
    geo_index.json, чтобы не сканировать markdown). Без него — сканируем `content_dir`."""
    if near is None:
        try:
            near = nearest_storylines(lat, lon, content_dir, top=3)
        except Exception:
            near = []
    close = [n for n in near if n.get("dist_m", 9e9) <= near_km * 1000]

    # Ветка 1: рядом есть наши верифицированные сюжеты — предлагаем их.
    if close:
        items = "; ".join(f"{i}) {n['title']} ({format_distance(n['dist_m'])})"
                          for i, n in enumerate(close, 1))
        return (
            f"[ГЕО] Пользователь рядом с нашими точками тропы. Полный список ближайших, "
            f"отсортирован по близости, НОМЕР = позиция: {items}. "
            f"Это ВСЕ наши точки поблизости. Других музеев, экспозиций, залов рядом НЕТ — "
            f"НЕ придумывай их, это грубая ошибка. Если просят «ещё» или «другие» — честно "
            f"ответь, что рядом только эти, а весь каталог сюжетов открыт в разделе «Сюжеты» сайта. "
            f"Когда пользователь называет НОМЕР или НАЗВАНИЕ — бери сюжет строго из ЭТОГО "
            f"списка (номер = позиция в нём), НЕ опираясь на списки из прошлых сообщений, "
            f"и расскажи про выбранный. Коротко и живо, показывай расстояния."
        )

    # Ветка 2: наших точек рядом нет — рассказываем про САМУ местность.
    # Оба источника опрашиваем ПАРАЛЛЕЛЬНО (иначе таймауты складываются) и кэшируем.
    # Внешние источники не должны ронять хендлер бота ни при каких обстоятельствах.
    def _safe(fn, key, default):
        try:
            return _cached(key, fn)
        except Exception:
            return default

    place, objs = {}, []
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_place = ex.submit(_safe, lambda: reverse_place(lat, lon),
                                _cache_key("place", lat, lon), {})
            f_objs = ex.submit(_safe, lambda: nearby_objects(lat, lon),
                               _cache_key("objs", lat, lon), [])
            place, objs = f_place.result(), f_objs.result()
    except Exception:
        pass
    where = (place or {}).get("name") or "неизвестная местность"
    if objs:
        obj_line = "; ".join(
            f"{o['name']}" + (f" ({o['kind']})" if o["kind"] else "")
            + (f", {format_distance(o['dist_m'])}" if o["dist_m"] is not None else "")
            for o in objs[:6]
        )
        around = f"Рядом по картам: {obj_line}."
    else:
        around = "Данных об объектах вокруг нет."

    # Наша точка не рядом, но в досягаемости — упомянем одной строкой в конце, не более.
    bonus = ""
    if near and near[0].get("dist_m", 9e9) <= MENTION_KM * 1000:
        n = near[0]
        bonus = (f" В самом конце можешь одной строкой добавить, что в "
                 f"{format_distance(n['dist_m'])} есть наша точка «{n['title']}» — "
                 f"как вариант, если человек готов доехать.")

    return (
        f"[ГЕО] Пользователь прислал геолокацию ({lat:.5f}, {lon:.5f}). "
        f"Это {where}. {around} "
        f"Наших готовых сюжетов рядом нет — НЕ предлагай ехать к далёким точкам и не называй "
        f"расстояния до них. Вместо этого расскажи научно-популярно про ЭТУ местность: "
        f"2–3 интересных факта (природа, геология, вода, климат, история места), "
        f"на что обратить внимание вокруг прямо сейчас, и предложи одно простое наблюдение "
        f"или опыт, который здесь можно провести. Стиль «Кванта»: через первопричину и аналогию. "
        f"Не выдумывай фактов о конкретных объектах, если не уверен — говори о типичном для этой местности."
        f"{bonus}"
    )
