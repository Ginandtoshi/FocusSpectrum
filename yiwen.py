"""Yiwen game module (Game Two)."""
from __future__ import annotations

import random
import time
from typing import Dict, Optional, Tuple

from eye_tracker import EyeTracker

GazePoint = Tuple[float, float]


class YiwenGame:
    """Game Two - control an object with gaze and monitor boundary touches."""

    def __init__(self, tracker: EyeTracker, duration: float = 45.0):
        self.tracker = tracker
        self.duration = duration
        self.boundary_touch_count = 0
        self.total_touch_duration = 0.0

    def run(self) -> Dict:
        self.tracker.start()
        start = time.time()
        in_boundary = True
        touch_start: Optional[float] = None
        while time.time() - start < self.duration:
            cx = 0.5 + 0.08 * random.uniform(-1, 1)
            cy = 0.5 + 0.08 * random.uniform(-1, 1)
            radius = 0.25 + 0.05 * random.uniform(-1, 1)
            g = self.tracker.get_gaze()
            if g:
                dx = g[0] - cx
                dy = g[1] - cy
                dist = (dx * dx + dy * dy) ** 0.5
                currently_in = dist <= radius
                if not currently_in and in_boundary:
                    self.boundary_touch_count += 1
                    touch_start = time.time()
                if currently_in and not in_boundary and touch_start is not None:
                    self.total_touch_duration += time.time() - touch_start
                    touch_start = None
                in_boundary = currently_in

            time.sleep(0.05)

        if touch_start is not None:
            self.total_touch_duration += time.time() - touch_start

        self.tracker.stop()
        return {
            "boundary_touch_count": self.boundary_touch_count,
            "boundary_touch_duration_s": round(self.total_touch_duration, 3),
        }
