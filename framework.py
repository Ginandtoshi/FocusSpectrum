"""Top-level orchestrator for the focus-testing game.

This module coordinates the smaller modules in the project and orchestrates
the sequence of steps for the focus-testing game. TODOs are listed below as
inline, code-style comments to make it easier to track implementation tasks.
"""

from __future__ import annotations

from typing import Callable

# TODO checklist (code-style comments)
# TODO[UI]        Implement UI layer (ui.py)
#                 - Use `pygame` for desktop or `p5.js`/`pixi.js` for web
#                 - Draw calibration dot, particles, blossom cores, dynamic boundaries, Lyra grid
#                 - Provide `show_fn(normalized_point: (x,y))` used by Calibration
# TODO[TRACKER]   Implement/Integrate real eye-tracker module (real_eye_tracker.py)
#                 - Desktop: OpenCV + MediaPipe or Pupil Labs SDK
#                 - Web: WebGazer.js client (optionally stream to server via WebSocket/Flask)
#                 - Provide concrete EyeTracker subclass exposing start/stop/get_gaze/calibrate_point
# TODO[RECORDER]  Create recorder.py for session logging
#                 - Record raw gaze samples (timestamped), event logs, clicks, pop-up times
#                 - Support JSON/CSV export for offline analysis
# TODO[PLOTTING]  Add plotting utilities (plot_gaze.py, heatmap.py)
#                 - Gaze trajectory replay (lines + fixation circles)
#                 - Heatmap generator for distraction phases
# TODO[DISTRACTORS]Implement stimuli manager for pop-ups/videos/audio with precise timestamps
# TODO[SYNC]      Ensure consistent timebase across modules (use time.monotonic or LSL)
# TODO[TESTS]     Add unit & integration tests, plus a QA checklist for calibration/sample rate
# TODO[PACKAGE]   Provide packaging & launcher (requirements.txt, run scripts, Flask server if web)
# TODO[OPTIONAL]  Adaptive difficulty, localization, session replay export (PNG/PDF)

from eye_tracker import DummyEyeTracker
from calibration import Calibration
from blossom import BlossomGame
from yiwen import YiwenGame
from lyra import LyraGame
from results import ResultsBuilder


class GameFramework:
    def __init__(self, tracker: DummyEyeTracker, show_fn: Callable[[tuple, tuple], None] = lambda p: None):
        self.tracker = tracker
        self.show_fn = show_fn
        self.results = ResultsBuilder()

    def run_entry(self) -> None:
        print("Step 1: Hello, look at me -> verifying tracker availability")

    def run_calibration(self) -> None:
        print("Step 2: Calibration: follow the dot")
        calib = Calibration(self.tracker, show_fn=self.show_fn)
        res = calib.run()
        print(f"Calibration collected {len(res.samples)} samples")
        self.results.add("calibration", {"samples": len(res.samples)})

    def run_practice(self) -> None:
        print("Practice round: semi-transparent particles -> blow away with gaze")
        # GUI: show particles and reveal start button when gaze moves
        import time

        time.sleep(1.0)

    def run_blossom(self) -> None:
        print("Game One: Blossom")
        g = BlossomGame(self.tracker, spawn_count=8)
        r = g.run(round_time=20.0)
        print(f"Blossom score: {r['score']}")
        self.results.add("blossom", r)

    def run_yiwen(self) -> None:
        print("Game Two: Yiwen")
        g = YiwenGame(self.tracker, duration=15.0)
        r = g.run()
        print(f"Yiwen results: {r}")
        self.results.add("yiwen", r)

    def run_lyra(self) -> None:
        print("Game Three: Lyra")
        g = LyraGame(self.tracker, targets=10)
        r = g.run()
        print(f"Lyra results: {r}")
        self.results.add("lyra", r)

    def run_results(self) -> None:
        print("Step 6: Final Results - building Focus Profile")
        summary = self.results.summarize()
        print("Summary:", summary)

    def run_all(self) -> None:
        self.run_entry()
        self.run_calibration()
        self.run_practice()
        self.run_blossom()
        self.run_yiwen()
        self.run_lyra()
        self.run_results()


def main(dummy_mode: bool = True) -> None:
    if dummy_mode:
        tracker = DummyEyeTracker(mode="random")
    else:
        raise NotImplementedError("Non-dummy trackers must be supplied")

    framework = GameFramework(tracker=tracker, show_fn=lambda p: None)
    framework.run_all()


if __name__ == "__main__":
    main(dummy_mode=True)
