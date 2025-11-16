"""Eye tracker abstractions and dummy simulator."""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Optional, Tuple

# Normalized gaze point
GazePoint = Tuple[float, float]


class EyeTracker(ABC):
    """Abstract interface for an eye tracker."""

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_gaze(self) -> Optional[GazePoint]:
        raise NotImplementedError

    @abstractmethod
    def calibrate_point(self, screen_point: GazePoint) -> None:
        raise NotImplementedError


class DummyEyeTracker(EyeTracker):
    """A simple simulator used for development and testing."""

    def __init__(self, noise: float = 0.02, mode: str = "random"):
        self.running = False
        self.noise = noise
        self.mode = mode
        self._last: Optional[GazePoint] = None

    def start(self) -> None:
        self.running = True
        self._last = (0.5, 0.5)

    def stop(self) -> None:
        self.running = False

    def get_gaze(self) -> Optional[GazePoint]:
        if not self.running:
            return None
        x, y = self._last or (0.5, 0.5)
        if self.mode == "focused":
            x += random.gauss(0, self.noise)
            y += random.gauss(0, self.noise)
        else:
            x += random.uniform(-0.05, 0.05)
            y += random.uniform(-0.05, 0.05)
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        self._last = (x, y)
        return self._last

    def calibrate_point(self, screen_point: GazePoint) -> None:
        if self._last is None:
            self._last = screen_point
            return
        self._last = (self._last[0] * 0.8 + screen_point[0] * 0.2, self._last[1] * 0.8 + screen_point[1] * 0.2)
