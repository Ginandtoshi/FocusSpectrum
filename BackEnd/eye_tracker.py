import cv2
import numpy as np
from gaze_tracking import GazeTracking

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

class EyeTracker:
    def __init__(self):
        self.gaze = GazeTracking()
        self.gaze_x = SCREEN_WIDTH / 2
        self.gaze_y = SCREEN_HEIGHT / 2
        
        # Smoothing (Exponential Moving Average)
        self.alpha = 0.15 # Smoothing factor (0.0 - 1.0). Lower = Smoother but laggier.
        
        self.last_annotated_frame = None
        
        # Calibration Parameters (Ratios)
        # Horizontal: 1.0 is Left, 0.0 is Right (from GazeTracking library)
        # We want to map these to Screen X (0 to Width)
        self.calib_left = 0.40  # Ratio when looking at Left Edge
        self.calib_right = 0.60 # Ratio when looking at Right Edge
        
        # Vertical: 0.0 is Top, 1.0 is Bottom (from GazeTracking library)
        self.calib_top = 0.60    # Ratio when looking at Top Edge
        self.calib_bottom = 0.40 # Ratio when looking at Bottom Edge

    def calibrate(self, left_ratio, right_ratio, top_ratio, bottom_ratio):
        self.calib_left = left_ratio
        self.calib_right = right_ratio
        self.calib_top = top_ratio
        self.calib_bottom = bottom_ratio
        print(f"Calibration Updated: L={left_ratio:.2f}, R={right_ratio:.2f}, T={top_ratio:.2f}, B={bottom_ratio:.2f}")

    def process_frame(self, frame):
        """
        Process the frame (RGB) to update gaze position.
        """
        # Convert RGB to BGR for GazeTracking
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        self.gaze.refresh(frame_bgr)
        
        # Store annotated frame (BGR) -> Convert back to RGB for Pygame
        annotated_bgr = self.gaze.annotated_frame()
        
        # Draw Ratio
        ratio_x = self.gaze.horizontal_ratio()
        ratio_y = self.gaze.vertical_ratio()

        # Add debug text (Bottom Left with Background)
        lines = []
        if self.gaze.is_blinking():
            lines.append("Blinking")
        elif ratio_x is not None:
            if ratio_x <= 0.53:
                lines.append("Looking left")
            elif ratio_x < 0.59:
                lines.append("Looking center")
            else:
                lines.append("Looking right")
        
        left_pupil = self.gaze.pupil_left_coords()
        right_pupil = self.gaze.pupil_right_coords()
        lines.append("Left pupil:  " + str(left_pupil))
        lines.append("Right pupil: " + str(right_pupil))
        
        if ratio_x is not None:
            lines.append(f"Ratio X: {ratio_x:.2f}")
            
        # Draw Text at Bottom Left
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 1
        text_color = (255, 255, 255)
        bg_color = (0, 0, 0)
        line_height = 25
        padding = 10
        
        # Calculate max text width
        max_text_width = 0
        for line in lines:
            (w, h), _ = cv2.getTextSize(line, font, font_scale, font_thickness)
            if w > max_text_width:
                max_text_width = w
        
        # Ensure minimum width to reduce jitter, but expand if needed
        box_width = max(350, max_text_width + 2 * padding)
        
        fixed_lines_count = 4
        
        total_height = fixed_lines_count * line_height
        start_y = SCREEN_HEIGHT - total_height - 20
        
        # Draw Background Rectangle
        cv2.rectangle(annotated_bgr, (10, start_y - 20), (10 + box_width, SCREEN_HEIGHT - 10), bg_color, -1)
        
        # Draw Lines
        for i, line in enumerate(lines):
            y = start_y + i * line_height
            cv2.putText(annotated_bgr, line, (20, y), font, font_scale, text_color, font_thickness)
        
        self.last_annotated_frame = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
        
        if self.gaze.pupils_located:
            if ratio_x is not None and ratio_y is not None:
                # Map Ratios to Screen Coordinates using Calibration
                
                # Horizontal Mapping
                if abs(self.calib_right - self.calib_left) > 0.01:
                    norm_x = (ratio_x - self.calib_left) / (self.calib_right - self.calib_left)
                else:
                    norm_x = 0.5
                
                # Clamp
                norm_x = max(0.0, min(1.0, norm_x))
                target_x = norm_x * SCREEN_WIDTH
                
                # Vertical Mapping
                if abs(self.calib_bottom - self.calib_top) > 0.01:
                    norm_y = (ratio_y - self.calib_top) / (self.calib_bottom - self.calib_top)
                else:
                    norm_y = 0.5
                    
                # Clamp
                norm_y = max(0.0, min(1.0, norm_y))
                target_y = norm_y * SCREEN_HEIGHT
                
                # Exponential Moving Average (EMA) Smoothing
                self.gaze_x = self.alpha * target_x + (1 - self.alpha) * self.gaze_x
                self.gaze_y = self.alpha * target_y + (1 - self.alpha) * self.gaze_y
                
                return (self.gaze_x, self.gaze_y)
        
        return None

    def get_gaze_position(self):
        return (self.gaze_x, self.gaze_y)
        
    def get_annotated_frame(self):
        return self.last_annotated_frame
