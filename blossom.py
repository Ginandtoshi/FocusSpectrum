"""Blossom game module (Game One)."""
from __future__ import annotations

import random
import time
from typing import Dict, Tuple

from eye_tracker import EyeTracker

GazePoint = Tuple[float, float]


class BlossomGame:
    """Game One - spawn flower cores and detect 'shots' via gaze proximity."""

    def __init__(self, tracker: EyeTracker, spawn_count: int = 10):
        self.tracker = tracker
        self.spawn_count = spawn_count
        self.score = 0

    def run(self, round_time: float = 30.0) -> Dict:
        self.score = 0
        self.tracker.start()
        start = time.time()
        spawns = self.spawn_count
        while time.time() - start < round_time and spawns > 0:
            core_pos = (random.uniform(0.1, 0.9), random.uniform(0.1, 0.9))
            lifetime = random.uniform(3.0, 5.0)
            t0 = time.time()
            hit = False
            while time.time() - t0 < lifetime:
                g = self.tracker.get_gaze()
                if g:
                    dx = g[0] - core_pos[0]
                    dy = g[1] - core_pos[1]
                    if (dx * dx + dy * dy) ** 0.5 < 0.08:
                        hit = True
                        self.score += 1
                        break
                time.sleep(0.02)

            spawns -= 1
            time.sleep(0.3)

        self.tracker.stop()
        return {"score": self.score}
