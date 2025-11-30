import pygame
import cv2
import mediapipe as mp
import math
import random
import time
import os
import numpy as np
import sys
from datetime import datetime

# Add parent directory to path to allow importing scene_base
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from scene_base import Scene

# --- Sound Generation Functions (Kept as fallback) ---
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    wave = [math.sin(2 * math.pi * frequency * t / sample_rate) for t in range(n_samples)]
    int_wave = [int(32767 * 0.3 * sample) for sample in wave]
    stereo_wave = []
    for sample in int_wave:
        stereo_wave.extend([sample, sample])
    sound_array = np.array(stereo_wave, dtype=np.int16)
    return pygame.mixer.Sound(sound_array)

# --- Magic Circle ---
class MagicCircle:
    def __init__(self, player_id, center_x=600, center_y=400):
        self.player_id = player_id
        self.center_x = center_x
        self.center_y = center_y
        self.seed = int(time.time() * 1000) % (2**32)
        random.seed(self.seed)
        
        # Core geometric shape
        self.base_shape = random.choice(['circle', 'triangle', 'square', 'pentagon', 'hexagon', 'octagon', 'star'])
        
        # Pattern parameters
        self.num_spokes = random.choice([8, 12, 16])
        self.num_layers = random.randint(4, 6)
        self.base_radius = random.randint(40, 50)
        self.layer_spacing = random.randint(20, 28)
        
        # Calculate outer radius for constraints
        self.outer_radius = self.base_radius + (self.num_layers * self.layer_spacing)
        
        # Layer types
        self.layer_types = []
        for i in range(self.num_layers):
            self.layer_types.append(random.choice([
                'circle', 'circle', 'polygon', 'star'
            ]))
        
        self.symmetry_order = random.choice([4, 6, 8])
        self.rotation_offset = random.uniform(0, 360)
        
        # Color scheme
        self.primary_color = self._generate_color()
        self.secondary_color = self._generate_complementary_color()
        self.tertiary_color = self._generate_tertiary_color()
        
        # Animation state
        self.animation_start_time = time.time()
        self.pattern_points = []
        
        # Pre-calculate points
        self._generate_pattern_points()

    def _generate_color(self):
        colors = [
            (74, 144, 226), (155, 89, 182), (230, 126, 34), (26, 188, 156),
            (233, 30, 99), (52, 152, 219), (142, 68, 173), (22, 160, 133),
            (231, 76, 60), (46, 204, 113), (52, 73, 94)
        ]
        return random.choice(colors)
    
    def _generate_complementary_color(self):
        r, g, b = self.primary_color
        return ((r + 128) % 256, (g + 128) % 256, (b + 128) % 256)
    
    def _generate_tertiary_color(self):
        r1, g1, b1 = self.primary_color
        r2, g2, b2 = self.secondary_color
        return ((r1 + r2) // 2, (g1 + g2) // 2, (b1 + b2) // 2)

    def _generate_pattern_points(self):
        center_x, center_y = self.center_x, self.center_y
        angle_step = 360 / self.num_spokes
        
        for i in range(self.num_spokes):
            angle = i * angle_step + self.rotation_offset
            x = center_x + int(self.outer_radius * math.cos(math.radians(angle)))
            y = center_y + int(self.outer_radius * math.sin(math.radians(angle)))
            self.pattern_points.append((x, y))

    def get_random_point_inside(self):
        # Generate random point within the circle
        angle = random.uniform(0, 360)
        # Square root for uniform distribution
        r = math.sqrt(random.random()) * (self.outer_radius - 40) # -40 padding to keep flowers fully inside
        x = self.center_x + int(r * math.cos(math.radians(angle)))
        y = self.center_y + int(r * math.sin(math.radians(angle)))
        return x, y

    def draw(self, screen):
        center_x, center_y = self.center_x, self.center_y
        elapsed = time.time() - self.animation_start_time
        
        # Draw background glow
        glow_surf = pygame.Surface((center_x * 2, center_y * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (20, 20, 30, 100), (center_x, center_y), 300)
        screen.blit(glow_surf, (0, 0))
        
        # Draw rotating layers
        for i in range(self.num_layers):
            radius = self.base_radius + i * self.layer_spacing
            angle_offset = elapsed * (10 if i % 2 == 0 else -10)
            
            color = self.primary_color if i % 2 == 0 else self.secondary_color
            
            # Draw polygon/circle
            points = []
            sides = 6 + i
            for j in range(sides):
                angle = angle_offset + j * (360 / sides)
                x = center_x + int(radius * math.cos(math.radians(angle)))
                y = center_y + int(radius * math.sin(math.radians(angle)))
                points.append((x, y))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points, 2)
                
        # Draw spokes
        angle_step = 360 / self.num_spokes
        for i in range(self.num_spokes):
            angle = i * angle_step + self.rotation_offset + elapsed * 5
            end_x = center_x + int(self.outer_radius * math.cos(math.radians(angle)))
            end_y = center_y + int(self.outer_radius * math.sin(math.radians(angle)))
            pygame.draw.line(screen, self.tertiary_color, (center_x, center_y), (end_x, end_y), 1)

# --- Flower ---
class Flower:
    def __init__(self, x, y, image=None):
        self.x = x
        self.y = y
        self.bloomed = False
        self.bloom_start_time = 0
        self.core_size = 15
        self.image = image
        
        # Fallback colors
        self.petal_colors = [(255, 105, 180), (255, 182, 193), (255, 20, 147)]

    def draw_core(self, screen):
        # Draw the target core
        pygame.draw.circle(screen, (255, 215, 0), (self.x, self.y), self.core_size)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.core_size // 2)

    def bloom(self):
        if not self.bloomed:
            self.bloomed = True
            self.bloom_start_time = time.time()

    def draw(self, screen):
        if self.bloomed:
            elapsed = time.time() - self.bloom_start_time
            scale = min(1.0, elapsed * 2) # Bloom in 0.5 seconds
            
            if self.image:
                # Asset based drawing
                w = int(self.image.get_width() * scale * 0.2)
                h = int(self.image.get_height() * scale * 0.2)
                if w > 0 and h > 0:
                    scaled_img = pygame.transform.scale(self.image, (w, h))
                    rect = scaled_img.get_rect(center=(self.x, self.y))
                    screen.blit(scaled_img, rect)
            else:
                # Procedural drawing (Fallback)
                for i, color in enumerate(self.petal_colors):
                    radius = int((30 - i * 8) * scale)
                    if radius > 0:
                        pygame.draw.circle(screen, color, (self.x, self.y), radius)
                        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), radius, 1)

    def contains_point(self, x, y):
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance <= self.core_size * 2

# --- Main Scene ---
class Game1Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.player_id = manager.data.get("user_id", "Guest")
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        self.magic_circle = MagicCircle(self.player_id, self.screen_width // 2, self.screen_height // 2)
        
        # Load Flower Asset
        asset_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Asset', 'flower.gif')
        try:
            self.flower_img = pygame.image.load(asset_path).convert_alpha()
        except:
            print(f"Failed to load flower asset at {asset_path}")
            self.flower_img = None
            
        # Load Sounds
        self.bg_sounds = []
        sound_files = ['car-honk.mp3', 'dog-bark.mp3', 'running.mp3']
        for sf in sound_files:
            path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Asset', sf)
            try:
                self.bg_sounds.append(pygame.mixer.Sound(path))
            except:
                print(f"Failed to load sound {sf}")
        
        # Game State
        self.state = "GAME" # GAME, REPORT
        self.state_timer = time.time()
        
        # Game Logic
        self.flowers = []
        self.current_flower_idx = 0
        self.score = 0
        self.misses = 0
        self.flower_timeout = 1.5 # Seconds per flower
        self.last_flower_spawn_time = 0
        self.reaction_times = []
        
        # Distraction Tracking
        self.distracted_time = 0
        self.game_start_time = 0
        self.last_frame_time = 0
        self.final_distracted_rate = 0.0 # Store final rate
        
        # Sounds
        self.timeout_sound = generate_beep_sound(200, 0.2)
        self.success_sound = generate_beep_sound(880, 0.1)
        self.active_channels = []
        
        # Exit Button
        self.exit_btn_rect = pygame.Rect(self.screen_width - 120, self.screen_height - 60, 100, 40)
        
        # Load Algerian Font
        font_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Asset', 'Algerian Regular.ttf')
        try:
            self.font = pygame.font.Font(font_path, 40)
            self.small_font = pygame.font.Font(font_path, 24)
        except:
            print("Font not found, using default")
            self.font = pygame.font.SysFont("Arial", 40)
            self.small_font = pygame.font.SysFont("Arial", 24)

    def on_enter(self):
        print("Entering Game 1: Plant MeiLam")
        self.state = "GAME"
        self.state_timer = time.time()
        
        # Initialize flowers positions (20 flowers)
        self.flowers = []
        for _ in range(20):
            x, y = self.magic_circle.get_random_point_inside()
            self.flowers.append(Flower(x, y, self.flower_img))
            
        self.game_start_time = time.time()
        self.last_frame_time = time.time()
        self.last_flower_spawn_time = time.time()
        self.distracted_time = 0
        self.score = 0
        self.misses = 0
        self.reaction_times = []
        self.current_flower_idx = 0
        self.final_distracted_rate = 0.0

    def update(self):
        # Update Eye Tracking via Framework
        if hasattr(self.manager, 'eye_tracker') and hasattr(self.manager.camera, 'current_frame'):
            self.manager.eye_tracker.process_frame(self.manager.camera.current_frame)
        
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # State Machine
        if self.state == "GAME":
            # Distraction Logic (Based on Eye State: Center = Focused)
            is_focused = False
            if hasattr(self.manager, 'eye_tracker') and hasattr(self.manager.eye_tracker, 'gaze'):
                # is_center() returns True only if pupils located AND looking center
                if self.manager.eye_tracker.gaze.is_center():
                    is_focused = True
            
            if not is_focused:
                self.distracted_time += dt

            if self.current_flower_idx < len(self.flowers):
                # Sound Logic (After 6th flower)
                if self.current_flower_idx >= 5 and self.bg_sounds:
                    # Clean up finished channels
                    self.active_channels = [ch for ch in self.active_channels if ch.get_busy()]
                    
                    if len(self.active_channels) < 3:
                        if random.random() < 0.02: # Chance to play sound
                            snd = random.choice(self.bg_sounds)
                            # Only play if this specific sound is not already playing
                            if snd.get_num_channels() == 0:
                                ch = snd.play()
                                if ch:
                                    self.active_channels.append(ch)

                # Check timeout
                if current_time - self.last_flower_spawn_time > self.flower_timeout:
                    self.misses += 1
                    self.timeout_sound.play()
                    self.current_flower_idx += 1
                    self.last_flower_spawn_time = current_time
            else:
                # Game Over
                self.state = "REPORT"
                self.state_timer = current_time
                
                # Stop all sounds
                for s in self.bg_sounds:
                    s.stop()
                self.timeout_sound.stop()
                self.success_sound.stop()
                
                # Calculate Final Distraction Rate
                total_game_time = current_time - self.game_start_time
                if total_game_time > 0:
                    self.final_distracted_rate = (self.distracted_time / total_game_time) * 100
                else:
                    self.final_distracted_rate = 0.0
                
                self.manager.data["scores"]["game1"] = {
                    "score": self.score,
                    "misses": self.misses,
                    "reaction_times": self.reaction_times,
                    "distracted_rate": self.final_distracted_rate
                }

        elif self.state == "REPORT":
            pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check Exit Button
                if self.exit_btn_rect.collidepoint(event.pos):
                    from menu_scene import MenuScene
                    self.next_scene = MenuScene(self.manager)
                    return

                if self.state == "GAME" and self.current_flower_idx < len(self.flowers):
                    flower = self.flowers[self.current_flower_idx]
                    if flower.contains_point(event.pos[0], event.pos[1]):
                        flower.bloom()
                        self.score += 1
                        self.success_sound.play()
                        
                        reaction_time = time.time() - self.last_flower_spawn_time
                        self.reaction_times.append(reaction_time)
                        
                        self.current_flower_idx += 1
                        self.last_flower_spawn_time = time.time()
                    else:
                        self.misses += 1
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.state == "REPORT":
                    # Mark as completed
                    if "completed_games" not in self.manager.data:
                        self.manager.data["completed_games"] = []
                    if "game1" not in self.manager.data["completed_games"]:
                        self.manager.data["completed_games"].append("game1")
                    
                    # Return to Menu
                    from menu_scene import MenuScene
                    self.next_scene = MenuScene(self.manager)

    def draw(self, screen):
        # Background is already drawn by framework (Camera)
        
        # Draw Magic Circle
        self.magic_circle.draw(screen)
        
        # Draw Exit Button
        # pygame.draw.rect(screen, (200, 50, 50), self.exit_btn_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.exit_btn_rect, 2, border_radius=5)
        exit_text = self.small_font.render("EXIT", True, (255, 255, 255))
        screen.blit(exit_text, (self.exit_btn_rect.centerx - exit_text.get_width()//2, self.exit_btn_rect.centery - exit_text.get_height()//2))
        
        if self.state == "GAME":
            # Draw bloomed flowers
            for i in range(self.current_flower_idx):
                if self.flowers[i].bloomed:
                    self.flowers[i].draw(screen)
            
            # Draw current target
            if self.current_flower_idx < len(self.flowers):
                self.flowers[self.current_flower_idx].draw_core(screen)
                
                # Draw timer bar
                elapsed = time.time() - self.last_flower_spawn_time
                remaining = max(0, 1.0 - elapsed / self.flower_timeout)
                bar_width = 100
                pygame.draw.rect(screen, (255, 0, 0), 
                                 (self.flowers[self.current_flower_idx].x - bar_width//2, 
                                  self.flowers[self.current_flower_idx].y + 30, 
                                  bar_width * remaining, 5))

        elif self.state == "REPORT":
            # Draw all flowers
            for f in self.flowers:
                if f.bloomed:
                    f.draw(screen)
            
            # Draw Report Overlay
            self._draw_report(screen)

        # Draw Eye Tracking Gaze (Debug)
        if hasattr(self.manager, 'eye_tracker'):
            gaze = self.manager.eye_tracker.get_gaze_position()
            if gaze:
                pygame.draw.circle(screen, (0, 255, 0), (int(gaze[0]), int(gaze[1])), 10)

    def _draw_report(self, screen):
        # Center Popup
        popup_width = 600
        popup_height = 500
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2
        
        # Draw semi-transparent background
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0, 0))
        
        # Draw Popup Box
        pygame.draw.rect(screen, (245, 245, 245), (popup_x, popup_y, popup_width, popup_height), border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 3, border_radius=15)
        
        # Use class fonts
        font_title = self.font
        font_subtitle = self.small_font
        font_normal = self.small_font
        
        # Title
        title = font_title.render("Game Finished!", True, (44, 62, 80))
        title_rect = title.get_rect(center=(self.screen_width // 2, popup_y + 50))
        screen.blit(title, title_rect)
        
        # Stats
        y = popup_y + 120
        center_x = self.screen_width // 2
        
        # Flowers Bloomed
        bloomed_count = self.score
        accuracy_pct = (bloomed_count / 20) * 100
        bloomed_text = f"Flowers Bloomed: {bloomed_count}/20 ({accuracy_pct:.0f}%)"
        bloomed_surf = font_normal.render(bloomed_text, True, (44, 62, 80))
        screen.blit(bloomed_surf, bloomed_surf.get_rect(center=(center_x, y)))
        y += 50
        
        # Distracted Rate
        distracted_text = f"Distracted Rate: {self.final_distracted_rate:.1f}%"
        distracted_surf = font_normal.render(distracted_text, True, (44, 62, 80))
        screen.blit(distracted_surf, distracted_surf.get_rect(center=(center_x, y)))
        y += 50
        
        # Assessment
        if bloomed_count >= 16:
            assessment = "Outstanding!"
            color = (39, 174, 96)
        elif bloomed_count >= 10:
            assessment = "Great Work!"
            color = (52, 152, 219)
        else:
            assessment = "Keep Practicing!"
            color = (231, 76, 60)
            
        assess_text = font_title.render(assessment, True, color)
        screen.blit(assess_text, assess_text.get_rect(center=(center_x, y + 20)))
        
        # Instruction to exit
        exit_text = font_normal.render("Press SPACE to return to Menu", True, (100, 100, 100))
        screen.blit(exit_text, exit_text.get_rect(center=(center_x, popup_y + popup_height - 50)))
