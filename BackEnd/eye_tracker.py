import mediapipe as mp
import numpy as np

class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.facial_detected = False
        self.gaze_pos = None
        
        # Calibration offsets (simple translation for now)
        self.offset_x = 0
        self.offset_y = 0
        self.scale_x = 1.0
        self.scale_y = 1.0

    def process_frame(self, frame_rgb):
        """Process the frame provided by CameraManager"""
        if frame_rgb is None:
            return

        results = self.face_mesh.process(frame_rgb)
        
        if results.multi_face_landmarks:
            self.facial_detected = True
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get eye center landmarks (468 = left eye, 473 = right eye)
            left_eye = face_landmarks.landmark[468]
            right_eye = face_landmarks.landmark[473]
            
            # Average eye position (Normalized 0-1)
            # Note: MediaPipe x is 0 on left, 1 on right of the image.
            # If the camera image is mirrored (flipped horizontally) for display,
            # we need to handle that. Usually CameraManager flips it.
            # If CameraManager flips the frame BEFORE passing it here, then:
            # x=0 is left of screen, x=1 is right of screen.
            
            avg_x = (left_eye.x + right_eye.x) / 2
            avg_y = (left_eye.y + right_eye.y) / 2
            
            # Simple mapping to screen coordinates (assuming 1200x800)
            # We can refine this with calibration later
            screen_x = (avg_x - 0.5) * 1200 * 3 + 600 # Amplify movement
            screen_y = (avg_y - 0.5) * 800 * 3 + 400
            
            # Apply calibration
            screen_x = (screen_x + self.offset_x) * self.scale_x
            screen_y = (screen_y + self.offset_y) * self.scale_y
            
            # Clamp to screen
            # screen_x = max(0, min(1200, screen_x))
            # screen_y = max(0, min(800, screen_y))
            
            self.gaze_pos = (screen_x, screen_y)
        else:
            self.facial_detected = False
            self.gaze_pos = None

    def get_gaze_position(self):
        return self.gaze_pos
    
    def calibrate(self, target_x, target_y, current_gaze_x, current_gaze_y):
        # Very simple 1-point calibration (offset)
        # Or we can do more complex stuff.
        # For now, let's just shift the offset so current gaze matches target
        self.offset_x += (target_x - current_gaze_x)
        self.offset_y += (target_y - current_gaze_y)
