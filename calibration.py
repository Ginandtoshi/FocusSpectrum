"""Calibration routine module."""
from __future__ import annotations

import time
from typing import Callable, List, Tuple

from eye_tracker import EyeTracker

GazePoint = Tuple[float, float]


class CalibrationResult:
    def __init__(self, samples: List[Tuple[GazePoint, GazePoint]]):
        self.samples = samples


class Calibration:
    """Calibration routine.

    Shows a dot at fixed points and records average gaze for each point.
    """

    def __init__(self, tracker: EyeTracker, show_fn: Callable[[GazePoint], None]):
        self.tracker = tracker
        self.show_fn = show_fn
        self.samples: List[Tuple[GazePoint, GazePoint]] = []

    def run(self, duration_per_point: float = 1.2) -> CalibrationResult:
        points = [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95), (0.5, 0.5)]
        self.tracker.start()
        for p in points:
            self.show_fn(p)
            t0 = time.time()
            collected = []
            while time.time() - t0 < duration_per_point:
                g = self.tracker.get_gaze()
                if g:
                    collected.append(g)
                time.sleep(0.02)

            if collected:
                avg_x = sum(g[0] for g in collected) / len(collected)
                avg_y = sum(g[1] for g in collected) / len(collected)
                measured = (avg_x, avg_y)
                self.tracker.calibrate_point(p)
                self.samples.append((measured, p))

        self.tracker.stop()
        return CalibrationResult(self.samples)
