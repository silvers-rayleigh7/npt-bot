"""POI matching: учитывает кулдаун, гистерезис, точность."""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Iterable

EARTH_R = 6_371_000.0  # m


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между двумя точками на сфере, метры."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(a))


class POIMatcher:
    """Отслеживает кулдаун и гистерезис на POI per-user."""

    def __init__(
        self,
        poi: list[dict],
        default_radius_m: float = 80.0,
        cooldown_s: float = 900.0,
        hysteresis_m: float = 30.0,
        state_path: str | Path = "logs/poi_state.json",
    ):
        self.poi = poi
        self.default_radius = default_radius_m
        self.cooldown = cooldown_s
        self.hysteresis = hysteresis_m
        self.state_path = Path(state_path)
        self.state: dict = self._load()

    def _load(self) -> dict:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {}

    def _save(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2))

    def step(
        self, user_id: int, lat: float, lon: float, accuracy_m: float = 0.0
    ) -> dict | None:
        """Принимает одну точку live-location. Возвращает POI dict, если триггеримся."""
        u = self.state.setdefault(str(user_id), {"last_trigger": {}, "inside": {}})
        now = time.time()

        for p in self.poi:
            d = haversine_m(lat, lon, p["lat"], p["lon"])
            radius = float(p.get("trigger_radius_m", self.default_radius))
            pid = p["id"]
            was_inside = u["inside"].get(pid, False)
            last = u["last_trigger"].get(pid, 0)

            # Внутри радиуса
            if d <= radius:
                if not was_inside and (now - last) > self.cooldown:
                    u["inside"][pid] = True
                    u["last_trigger"][pid] = now
                    self._save()
                    return {**p, "distance_m": round(d, 1), "accuracy_m": accuracy_m}
                # уже внутри — не повторяем
                u["inside"][pid] = True

            # Снаружи радиуса + гистерезис — освобождаем триггер
            elif d > radius + self.hysteresis and was_inside:
                u["inside"][pid] = False

        self._save()
        return None

    def nearest(self, lat: float, lon: float, limit: int = 3) -> list[dict]:
        """Возвращает ближайшие POI с расстоянием в метрах."""
        ranked = []
        for p in self.poi:
            d = haversine_m(lat, lon, p["lat"], p["lon"])
            ranked.append({**p, "distance_m": round(d, 1)})
        ranked.sort(key=lambda item: item["distance_m"])
        return ranked[:limit]

    def by_id(self, poi_id: str) -> dict | None:
        """Ищет POI по стабильному id."""
        for p in self.poi:
            if p["id"] == poi_id:
                return p
        return None


def load_poi(path: str | Path) -> list[dict]:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg["poi"]
