import pygame
import sys
import os
from camera_manager import CameraManager
from scene_base import Scene
from eye_tracker import EyeTracker
from calibration_scene import CalibrationScene

# Import your game scenes here
from game.game1_Plant_MeiLam.Game01_Scene import Game1Scene
from game.game2_Park_Yiwen.Game02_Scene import Game2Scene
from game.game3_Text_Danyi.Game03_Scene import Game3Scene

# --- Configuration ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

class Framework:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Focus Spectrum")
        self.clock = pygame.time.Clock()
        
        # Initialize Camera
        print("Initializing Camera...")
        self.camera = CameraManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize Eye Tracker
        print("Initializing Eye Tracker...")
        self.eye_tracker = EyeTracker()
        
        # Shared Data (Score, User Profile)
        self.data = {
            "user_id": "guest",
            "scores": {},
            "completed_games": []
        }
        
        # Start with Onboarding Scene
        self.current_scene = OnboardingScene(self)

    def run(self):
        running = True
        while running:
            # 1. Event Handling
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            
            # 2. Camera Background
            # We draw the camera frame FIRST, so it's the background
            # Update Eye Tracker with current frame to get annotated frame
            current_frame = self.camera.get_frame()
            if current_frame is not None:
                self.eye_tracker.process_frame(current_frame)
                
                # Get annotated frame for visualization
                annotated_frame = self.eye_tracker.get_annotated_frame()
                if annotated_frame is not None:
                    # Convert to Pygame surface
                    cam_surface = pygame.image.frombuffer(annotated_frame.tobytes(), (annotated_frame.shape[1], annotated_frame.shape[0]), "RGB")
                else:
                    cam_surface = self.camera.get_pygame_surface()
            else:
                cam_surface = None

            if cam_surface:
                self.screen.blit(cam_surface, (0, 0))
            else:
                self.screen.fill((0, 0, 0)) # Fallback if camera fails

            # 3. Scene Logic
            if self.current_scene:
                self.current_scene.handle_events(events)
                self.current_scene.update()
                self.current_scene.draw(self.screen)
                
                # Check for scene switch
                if self.current_scene.next_scene:
                    old_scene = self.current_scene
                    old_scene.on_exit()
                    self.current_scene = self.current_scene.next_scene
                    self.current_scene.on_enter()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        self.camera.release()
        pygame.quit()
        sys.exit()

# --- Simple Onboarding Scene (Example) ---
class OnboardingScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        
        # Load Algerian Font
        font_path = os.path.join(os.path.dirname(__file__), '..', 'Asset', 'Algerian Regular.ttf')
        try:
            self.font = pygame.font.Font(font_path, 48)
            self.small_font = pygame.font.Font(font_path, 24)
        except:
            print("Font not found, using default")
            self.font = pygame.font.SysFont("Arial", 48)
            self.small_font = pygame.font.SysFont("Arial", 24)
            
        self.start_time = pygame.time.get_ticks()

    def draw(self, screen):
        # Draw semi-transparent overlay so text is readable over camera
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)) # Black with alpha 100
        screen.blit(overlay, (0, 0))

        # Draw Text
        text = self.font.render("Focus Spectrum", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        sub = self.small_font.render("Press SPACE to Start Calibration", True, (200, 200, 200))
        screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 + 20))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Switch to Calibration Scene
                    print("Switching to Calibration...")
                    self.next_scene = CalibrationScene(self.manager)


if __name__ == "__main__":
    app = Framework()
    app.run()
