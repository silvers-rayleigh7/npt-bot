from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot" / "scripts"))

from poi_match import POIMatcher, haversine_m  # noqa: E402


class POIMatcherTest(unittest.TestCase):
    def test_haversine_zero(self):
        self.assertEqual(haversine_m(55.753681, 48.743252, 55.753681, 48.743252), 0)

    def test_nearest_orders_by_distance(self):
        matcher = POIMatcher(
            poi=[
                {"id": "far", "lat": 55.76, "lon": 48.75},
                {"id": "near", "lat": 55.7537, "lon": 48.7433},
            ],
            state_path=self._state_path(),
        )
        self.assertEqual(matcher.nearest(55.753681, 48.743252, limit=1)[0]["id"], "near")

    def test_step_uses_cooldown_and_hysteresis(self):
        matcher = POIMatcher(
            poi=[{"id": "p1", "lat": 55.753681, "lon": 48.743252, "trigger_radius_m": 30}],
            cooldown_s=900,
            hysteresis_m=10,
            state_path=self._state_path(),
        )
        self.assertIsNotNone(matcher.step(1, 55.753681, 48.743252))
        self.assertIsNone(matcher.step(1, 55.753681, 48.743252))
        self.assertIsNone(matcher.step(1, 55.7545, 48.743252))

    def _state_path(self) -> Path:
        return Path(tempfile.mkdtemp()) / "state.json"


if __name__ == "__main__":
    unittest.main()
