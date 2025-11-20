# Game Two — Eye Gaze Focus Demo (Python / Pygame)

This is a Python prototype of the Step 4 game (Yiwen) implemented with `pygame`.

Features
- 45s single round
- Mouse fallback control (treated as gaze). The code provides a placeholder where an OpenCV-based gaze provider can be plugged in.
- Waveform focus boundary modulated by moving distractor blobs
- Scoring: counts of times the controlled object touches the boundary and cumulative touch duration (seconds)

Requirements
- Python 3.8+
- Install dependencies:

```bash
python3 -m pip install -r game2-py/requirements.txt
```

Run

```bash
python3 game2-py/main.py
```

Controls
- Left-click or press SPACE to start the 45s round.
- **Eye tracking only**: The glowing ball is controlled only by your eye movements (no mouse control).
- Press `C` to run eye tracking calibration (required for eye control). During calibration you will see targets; look at each target until collection finishes.

Notes about gaze (required)
- The demo requires camera-based eye tracking. It uses OpenCV to detect eye regions and then finds a dark pupil contour. This is intentionally simple and may fail under strong lighting, eyeglasses, or side-facing head poses.
- **Calibration is required**: The ball will only move after you press `C` to run calibration. The calibration shows a sequence of 5 targets (center + corners); look steadily at each target while data is collected. The app fits an affine mapping from pupil coords to screen coords.
- **No mouse fallback**: Unlike typical demos, this version has no mouse control - only eye tracking controls the ball position.
- Accuracy limits: this approach is a prototype. For reliable gaze tracking you should use a proper eye-tracking SDK or improve the detector (infrared illumination, pupil models, per-user calibration).

Output
- After a round completes, the app prints and displays: touch count and total touch time (seconds).

License: MIT (demo)
