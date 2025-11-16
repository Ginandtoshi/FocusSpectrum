"""Lyra game module (Game Three)."""
from __future__ import annotations

import random
import time
from typing import Dict

from eye_tracker import EyeTracker


class LyraGame:
    """Game Three - trail-making style search task (simulated)."""

    def __init__(self, tracker: EyeTracker, targets: int = 10):
        self.tracker = tracker
        self.targets = targets
        self.errors = 0
        self.start_time = 0.0
        self.end_time = 0.0
        self.distraction_glances = 0
        self.distraction_time = 0.0

    def run(self) -> Dict:
        self.tracker.start()
        self.start_time = time.time()
        simulated_time = random.uniform(8.0 + self.targets * 0.8, 20.0 + self.targets * 1.2)
        self.distraction_glances = random.randint(0, 8)
        self.distraction_time = random.uniform(0, 2.0 * self.distraction_glances)
        self.errors = random.randint(0, 3)
        time.sleep(min(1.0, simulated_time))
        self.end_time = self.start_time + simulated_time
        self.tracker.stop()
        return {
            "total_time_s": round(self.end_time - self.start_time, 3),
            "errors": self.errors,
            "distraction_glances": self.distraction_glances,
            "distraction_time_s": round(self.distraction_time, 3),
        }
