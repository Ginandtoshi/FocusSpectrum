import pygame
import time
import math
import os
from scene_base import Scene

class CalibrationScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        
        # Load Algerian Font
        font_path = os.path.join(os.path.dirname(__file__), '..', 'Asset', 'Algerian Regular.ttf')
        try:
            self.font = pygame.font.Font(font_path, 30)
            self.large_font = pygame.font.Font(font_path, 50)
        except:
            print("Font not found, using default")
            self.font = pygame.font.SysFont("Arial", 30)
            self.large_font = pygame.font.SysFont("Arial", 50)
        
        # Calibration State
        self.step = 0 
        # 0: Intro
        # 1: Look Left
        # 2: Look Right
        # 3: Look Top
        # 4: Look Bottom
        # 5: Center / Verify
        # 6: Complete
        
        self.calibration_points = {
            "left": (100, 400),
            "right": (1100, 400),
            "top": (600, 100),
            "bottom": (600, 700),
            "center": (600, 400)
        }
        
        self.timer = 0
        self.hold_duration = 2.0 # Seconds to hold gaze
        self.start_hold_time = None
        
        self.left_verified = False
        self.right_verified = False
        
        # Button
        self.start_btn_rect = pygame.Rect(500, 600, 200, 60)

    def on_enter(self):
        print("Entering Calibration Scene")
        self.step = 0
        self.left_verified = False
        self.right_verified = False

    def update(self):
        # Process Eye Tracking
        if hasattr(self.manager, 'eye_tracker') and hasattr(self.manager.camera, 'current_frame'):
            self.manager.eye_tracker.process_frame(self.manager.camera.current_frame)
        
        gaze = self.manager.eye_tracker.get_gaze_position()
        
        if self.step == 0:
            # Intro
            pass
            
        elif self.step == 1: # Verify Left
            if gaze and gaze[0] < 400: # Looked leftish
                if self.start_hold_time is None:
                    self.start_hold_time = time.time()
                elif time.time() - self.start_hold_time > 1.0:
                    self.left_verified = True
                    self.step = 2 # Go to Right
                    self.start_hold_time = None
            else:
                self.start_hold_time = None
                
        elif self.step == 2: # Verify Right
            if gaze and gaze[0] > 800: # Looked rightish
                if self.start_hold_time is None:
                    self.start_hold_time = time.time()
                elif time.time() - self.start_hold_time > 1.0:
                    self.right_verified = True
                    self.step = 3 # Done
                    self.start_hold_time = None
            else:
                self.start_hold_time = None

    def draw(self, screen):
        # Background (Camera is already drawn by framework)
        
        # Draw Gaze Feedback (Trackball)
        gaze = self.manager.eye_tracker.get_gaze_position()
        if gaze:
            pygame.draw.circle(screen, (0, 255, 255), (int(gaze[0]), int(gaze[1])), 20)
            pygame.draw.circle(screen, (255, 255, 255), (int(gaze[0]), int(gaze[1])), 5)
        else:
            text = self.font.render("No Face Detected", True, (255, 0, 0))
            screen.blit(text, (10, 10))

        # Draw Instructions based on step
        if self.step == 0:
            self._draw_text_centered(screen, "Calibration Check", -100, self.large_font)
            self._draw_text_centered(screen, "Follow the instructions to verify eye tracking.", -40)
            self._draw_text_centered(screen, "Press SPACE to start.", 20)
            
        elif self.step == 1:
            self._draw_text_centered(screen, "Look at the LEFT side", -200, self.large_font)
            # Draw target area
            pygame.draw.circle(screen, (255, 0, 0, 100), self.calibration_points["left"], 50, 5)
            if self.start_hold_time:
                progress = (time.time() - self.start_hold_time) / 1.0
                pygame.draw.circle(screen, (0, 255, 0), self.calibration_points["left"], int(50 * progress))

        elif self.step == 2:
            self._draw_text_centered(screen, "Look at the RIGHT side", -200, self.large_font)
            # Draw target area
            pygame.draw.circle(screen, (255, 0, 0, 100), self.calibration_points["right"], 50, 5)
            if self.start_hold_time:
                progress = (time.time() - self.start_hold_time) / 1.0
                pygame.draw.circle(screen, (0, 255, 0), self.calibration_points["right"], int(50 * progress))

        elif self.step == 3:
            self._draw_text_centered(screen, "Calibration Complete!", -100, self.large_font)
            self._draw_text_centered(screen, "Press SPACE to continue to Menu", -40)
            
            # Draw Start Button
            pygame.draw.rect(screen, (0, 200, 0), self.start_btn_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.start_btn_rect, 3, border_radius=10)
            
            btn_text = self.font.render("CONTINUE", True, (255, 255, 255))
            text_rect = btn_text.get_rect(center=self.start_btn_rect.center)
            screen.blit(btn_text, text_rect)

    def _draw_text_centered(self, screen, text, y_offset, font=None):
        if font is None:
            font = self.font
        surf = font.render(text, True, (255, 255, 255))
        # Add shadow
        shadow = font.render(text, True, (0, 0, 0))
        
        center_x = 1200 // 2
        center_y = 800 // 2
        
        rect = surf.get_rect(center=(center_x, center_y + y_offset))
        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(surf, rect)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.step == 0:
                        self.step = 1
                    elif self.step == 3:
                        # Go to Menu
                        from menu_scene import MenuScene
                        self.next_scene = MenuScene(self.manager)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.step == 3:
                    if self.start_btn_rect.collidepoint(event.pos):
                        # Go to Menu
                        from menu_scene import MenuScene
                        self.next_scene = MenuScene(self.manager)
