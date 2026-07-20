"""Погода для урока на природе — Open-Meteo (без ключа).

Зачем прогноз, а не «сейчас»: учитель готовится вечером к завтрашнему уроку, значит
погода нужна на час занятия. Отдаём короткую строку для промпта; любая ошибка → "".
"""
from __future__ import annotations

from datetime import datetime, timedelta

import requests

_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FC_URL = "https://api.open-meteo.com/v1/forecast"

# Коды погоды WMO → человеческое описание.
_WMO = {
    0: "ясно", 1: "почти ясно", 2: "переменная облачность", 3: "пасмурно",
    45: "туман", 48: "изморозь",
    51: "морось", 53: "морось", 55: "сильная морось",
    56: "ледяная морось", 57: "ледяная морось",
    61: "небольшой дождь", 63: "дождь", 65: "сильный дождь",
    66: "ледяной дождь", 67: "ледяной дождь",
    71: "небольшой снег", 73: "снег", 75: "сильный снег", 77: "снежная крупа",
    80: "ливень", 81: "ливень", 82: "сильный ливень",
    85: "снегопад", 86: "сильный снегопад",
    95: "гроза", 96: "гроза с градом", 99: "гроза с градом",
}

# Варианты поля «Когда урок» → (сдвиг дней, час).
WHEN_CHOICES = {
    "": (0, None),                      # не указано → текущая погода
    "сейчас": (0, None),
    "сегодня днём": (0, 13),
    "сегодня вечером": (0, 17),
    "завтра утром": (1, 9),
    "завтра днём": (1, 13),
    "завтра вечером": (1, 17),
}


def geocode(city: str, timeout: float = 6.0):
    """Название города → (lat, lon) или None."""
    if not city or not city.strip():
        return None
    try:
        r = requests.get(_GEO_URL, params={"name": city.strip(), "count": 1,
                                           "language": "ru", "format": "json"},
                         timeout=timeout)
        r.raise_for_status()
        res = (r.json() or {}).get("results") or []
        if not res:
            return None
        return float(res[0]["latitude"]), float(res[0]["longitude"])
    except Exception:
        return None


def _fmt(code, temp, wind, when_label: str) -> str:
    desc = _WMO.get(int(code), "") if code is not None else ""
    parts = []
    if temp is not None:
        parts.append(f"{round(float(temp)):+d} °C".replace("+-", "-"))
    if desc:
        parts.append(desc)
    if wind is not None:
        parts.append(f"ветер {round(float(wind))} м/с")
    if not parts:
        return ""
    return f"{when_label}: " + ", ".join(parts) if when_label else ", ".join(parts)


def weather_for(city: str, when: str = "", timeout: float = 6.0) -> str:
    """Короткая строка погоды на час урока, напр. «завтра утром: +14 °C, переменная
    облачность, ветер 3 м/с». Нет города/сбой → ""."""
    coords = geocode(city, timeout=timeout)
    if not coords:
        return ""
    lat, lon = coords
    day_off, hour = WHEN_CHOICES.get((when or "").strip().lower(), (0, None))
    try:
        params = {"latitude": lat, "longitude": lon, "timezone": "auto",
                  "wind_speed_unit": "ms"}
        if hour is None:
            params["current"] = "temperature_2m,weather_code,wind_speed_10m"
        else:
            params["hourly"] = "temperature_2m,weather_code,wind_speed_10m"
            params["forecast_days"] = day_off + 2
        r = requests.get(_FC_URL, params=params, timeout=timeout)
        r.raise_for_status()
        d = r.json() or {}

        if hour is None:
            c = d.get("current") or {}
            return _fmt(c.get("weather_code"), c.get("temperature_2m"),
                        c.get("wind_speed_10m"), "сейчас")

        h = d.get("hourly") or {}
        times = h.get("time") or []
        target = (datetime.now() + timedelta(days=day_off)).strftime("%Y-%m-%d") + f"T{hour:02d}:00"
        if target not in times:
            return ""
        i = times.index(target)
        return _fmt((h.get("weather_code") or [None])[i],
                    (h.get("temperature_2m") or [None])[i],
                    (h.get("wind_speed_10m") or [None])[i],
                    (when or "").strip().lower())
    except Exception:
        return ""
