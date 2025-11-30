import pygame
import time
import os
from scene_base import Scene
from menu_scene import MenuScene

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

class CalibrationScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        
        # Load Font
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
        # 1: Follow the Dot (Auto-Calibrate)
        # 2: Verify
        
        self.target_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.target_dir = 1 # 1: Right, -1: Left
        self.target_speed = 8 # Faster
        
        self.start_time = None
        self.duration = 5.0 # 5 seconds of following
        
        # Collected Extremes
        self.min_x_ratio = 1.0
        self.max_x_ratio = 0.0
        
        # Button
        self.start_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 150, 200, 60)
        
        # Skip Button (Top Right)
        self.skip_btn_rect = pygame.Rect(SCREEN_WIDTH - 140, 20, 120, 50)

    def on_enter(self):
        print("Entering Calibration Scene")
        self.step = 0
        self.start_time = None
        self.min_x_ratio = 1.0
        self.max_x_ratio = 0.0

    def update(self):
        # Process Eye Tracking
        gaze = self.manager.eye_tracker.gaze
        
        if self.step == 1:
            if self.start_time is None:
                self.start_time = time.time()
            
            # Move Target (Simple Horizontal Sweep)
            self.target_pos[0] += self.target_speed * self.target_dir
            if self.target_pos[0] > SCREEN_WIDTH - 100:
                self.target_dir = -1
            elif self.target_pos[0] < 100:
                self.target_dir = 1
                
            # Collect Data
            if gaze.pupils_located:
                rx = gaze.horizontal_ratio()
                
                if rx is not None:
                    self.min_x_ratio = min(self.min_x_ratio, rx)
                    self.max_x_ratio = max(self.max_x_ratio, rx)
                    
                    # Auto-Update Calibration Live
                    # Left Edge (Screen 0) -> High Ratio (e.g. 0.85)
                    # Right Edge (Screen W) -> Low Ratio (e.g. 0.15)
                    
                    # We update the tracker with the observed extremes
                    # But we clamp them to reasonable values to avoid glitches
                    
                    # For now, let's just trust the extremes if they are reasonable
                    # or just rely on the user verifying it.
                    
                    # Let's apply it immediately to see effect
                    self.manager.eye_tracker.calibrate(
                        self.max_x_ratio, # Left
                        self.min_x_ratio, # Right
                        0.15, # Top (Default)
                        0.85  # Bottom (Default)
                    )

            # Check Time
            if time.time() - self.start_time > self.duration:
                self.step = 2

    def draw(self, screen):
        # Background is camera (handled by framework)
        
        # Draw Gaze Feedback (Cyan)
        gaze_pos = self.manager.eye_tracker.get_gaze_position()
        if gaze_pos:
            pygame.draw.circle(screen, (0, 255, 255), (int(gaze_pos[0]), int(gaze_pos[1])), 20)
            pygame.draw.circle(screen, (255, 255, 255), (int(gaze_pos[0]), int(gaze_pos[1])), 5)

        # Draw Skip Button
        pygame.draw.rect(screen, (255, 255, 255), self.skip_btn_rect, 2, border_radius=5)
        skip_text = self.font.render("SKIP", True, (255, 255, 255))
        screen.blit(skip_text, (self.skip_btn_rect.centerx - skip_text.get_width()//2, self.skip_btn_rect.centery - skip_text.get_height()//2))

        if self.step == 0:
            self._draw_text_centered(screen, "Calibration Check", -100, self.large_font)
            self._draw_text_centered(screen, "Follow the RED DOT with your eyes.", -40)
            self._draw_text_centered(screen, "The cursor (CYAN) should start following you.", 20)
            self._draw_text_centered(screen, "Press SPACE to start.", 120)
            
        elif self.step == 1:
            # Draw Moving Target
            pygame.draw.circle(screen, (255, 0, 0), (int(self.target_pos[0]), int(self.target_pos[1])), 30)
            self._draw_text_centered(screen, "Follow the Red Dot...", -200)
            
        elif self.step == 2:
            self._draw_text_centered(screen, "Verification", -100, self.large_font)
            self._draw_text_centered(screen, "Look around. Does the cursor follow you?", -40)
            self._draw_text_centered(screen, "It is normal if it follows to the other side!", 20)
            self._draw_text_centered(screen, "If yes, press continue.", 80)
            
            # Draw Start Button
            # pygame.draw.rect(screen, (0, 200, 0), self.start_btn_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.start_btn_rect, 3, border_radius=10)
            
            btn_text = self.font.render("CONTINUE", True, (255, 255, 255))
            text_rect = btn_text.get_rect(center=self.start_btn_rect.center)
            screen.blit(btn_text, text_rect)

    def _draw_text_centered(self, screen, text, y_offset, font=None):
        if font is None:
            font = self.font
        surf = font.render(text, True, (255, 255, 255))
        shadow = font.render(text, True, (0, 0, 0))
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        rect = surf.get_rect(center=(center_x, center_y + y_offset))
        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(surf, rect)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.step == 0:
                        self.step = 1
                    elif self.step == 2:
                        # Go to Menu
                        self.next_scene = MenuScene(self.manager)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.skip_btn_rect.collidepoint(event.pos):
                    self.next_scene = MenuScene(self.manager)
                    return

                if self.step == 2:
                    if self.start_btn_rect.collidepoint(event.pos):
                        # Go to Menu
                        self.next_scene = MenuScene(self.manager)
