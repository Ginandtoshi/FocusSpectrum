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

# --- Sound Generation Functions ---
def generate_beep_sound(frequency=440, duration=0.1, waveform='sine', envelope='flat'):
    """Generate a beep sound with various waveforms and envelopes"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    
    # Generate waveform
    if waveform == 'sine':
        wave = [math.sin(2 * math.pi * frequency * t / sample_rate) for t in range(n_samples)]
    elif waveform == 'square':
        wave = [1.0 if math.sin(2 * math.pi * frequency * t / sample_rate) > 0 else -1.0 for t in range(n_samples)]
    elif waveform == 'triangle':
        wave = [2 * abs(2 * ((frequency * t / sample_rate) % 1) - 1) - 1 for t in range(n_samples)]
    elif waveform == 'sawtooth':
        wave = [2 * ((frequency * t / sample_rate) % 1) - 1 for t in range(n_samples)]
    elif waveform == 'chirp':  # Frequency sweep
        end_freq = frequency * 1.5
        wave = [math.sin(2 * math.pi * (frequency + (end_freq - frequency) * t / n_samples) * t / sample_rate) 
                for t in range(n_samples)]
    else:
        wave = [math.sin(2 * math.pi * frequency * t / sample_rate) for t in range(n_samples)]
    
    # Apply envelope
    for i in range(n_samples):
        if envelope == 'fade_in':
            wave[i] *= min(1.0, i / (n_samples * 0.3))
        elif envelope == 'fade_out':
            wave[i] *= min(1.0, (n_samples - i) / (n_samples * 0.3))
        elif envelope == 'fade_both':
            fade_in = min(1.0, i / (n_samples * 0.2))
            fade_out = min(1.0, (n_samples - i) / (n_samples * 0.2))
            wave[i] *= fade_in * fade_out
        elif envelope == 'pulse':
            # Create pulsing effect
            pulse_freq = 10
            wave[i] *= 0.5 + 0.5 * abs(math.sin(2 * math.pi * pulse_freq * i / sample_rate))
    
    # Convert to int16 with volume control
    int_wave = [int(32767 * 0.3 * sample) for sample in wave]
    
    # Convert to stereo
    stereo_wave = []
    for sample in int_wave:
        stereo_wave.extend([sample, sample])
    
    # Create sound from array
    sound_array = np.array(stereo_wave, dtype=np.int16)
    sound = pygame.mixer.Sound(sound_array)
    return sound

def generate_voice_sound(sound_type='laugh'):
    """Generate synthesized human/animal sounds"""
    sample_rate = 22050
    
    if sound_type == 'laugh':
        # Ha-ha-ha pattern with varying pitch
        segments = []
        for i in range(3):
            duration = 0.12
            n_samples = int(duration * sample_rate)
            freq = 280 + i * 20
            wave = [math.sin(2 * math.pi * freq * t / sample_rate) * 
                   (1 - abs(t / n_samples - 0.5) * 2) for t in range(n_samples)]
            segments.extend(wave)
            if i < 2:
                segments.extend([0] * int(0.05 * sample_rate))  # Pause
        wave = segments
    
    elif sound_type == 'bird':
        # More realistic chirping with rapid trills - extended
        duration = 1.2
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # Multiple harmonics for richer bird sound with more complex pattern
            freq1 = 2200 + 600 * math.sin(progress * math.pi * 12)
            freq2 = 3400 + 400 * math.sin(progress * math.pi * 18)
            tone1 = math.sin(2 * math.pi * freq1 * t / sample_rate) * 0.45
            tone2 = math.sin(2 * math.pi * freq2 * t / sample_rate) * 0.3
            amplitude = math.sin(progress * math.pi) * (0.7 + 0.15 * random.random())
            wave.append((tone1 + tone2) * amplitude)
    
    elif sound_type == 'dog':
        # More realistic bark - aggressive with harmonics - extended with multiple barks
        segments = []
        # Create 4 barks
        for bark in range(4):
            duration = 0.28
            n_samples = int(duration * sample_rate)
            for t in range(n_samples):
                progress = t / n_samples
                # Fundamental frequency drops sharply
                freq = 600 - 350 * progress
                # Add harmonics for growl quality - reduced intensity
                fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.4
                harmonic2 = math.sin(2 * math.pi * freq * 2 * t / sample_rate) * 0.25
                harmonic3 = math.sin(2 * math.pi * freq * 3 * t / sample_rate) * 0.15
                # Add noise for rough texture - reduced
                noise = random.uniform(-0.3, 0.3)
                amplitude = math.exp(-progress * 6) * (0.8 + 0.1 * abs(math.sin(t * 0.05)))
                segments.append((fundamental + harmonic2 + harmonic3 + noise) * amplitude)
            # Pause between barks
            if bark < 3:
                segments.extend([0] * int(0.2 * sample_rate))
        wave = segments
    
    elif sound_type == 'cat':
        # More realistic meow with vibrato and harmonics - longer meow
        duration = 1.2
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # Rising then holding pitch with vibrato, then falling
            if progress < 0.15:
                base_freq = 350 + 400 * (progress / 0.15)
            elif progress < 0.75:
                base_freq = 750 + 25 * math.sin(t / sample_rate * math.pi * 15)  # Vibrato
            else:
                base_freq = 750 - 250 * ((progress - 0.75) / 0.25)
            
            # Multiple harmonics for cat voice - reduced intensity
            fundamental = math.sin(2 * math.pi * base_freq * t / sample_rate) * 0.5
            harmonic2 = math.sin(2 * math.pi * base_freq * 2.1 * t / sample_rate) * 0.25
            harmonic3 = math.sin(2 * math.pi * base_freq * 3.2 * t / sample_rate) * 0.08
            
            amplitude = math.sin(progress * math.pi) * 0.85
            wave.append((fundamental + harmonic2 + harmonic3) * amplitude)
    
    elif sound_type == 'mosquito':
        # High-pitched buzzing mosquito sound - longer duration, softer
        duration = 3.5
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # Very high frequency with rapid modulation for buzz
            base_freq = 600 + 200 * math.sin(progress * math.pi * 2)
            buzz_mod = 30 * math.sin(t / sample_rate * math.pi * 80)  # Fast modulation
            freq = base_freq + buzz_mod
            
            # Further reduced harmonics for softer buzzing
            fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.2
            harmonic2 = math.sin(2 * math.pi * freq * 1.8 * t / sample_rate) * 0.12
            harmonic3 = math.sin(2 * math.pi * freq * 2.3 * t / sample_rate) * 0.08
            # Add slight random noise for wing flutter
            noise = random.uniform(-0.05, 0.05)
            
            # Softer amplitude to simulate flying closer/farther
            amplitude = 0.3 + 0.2 * math.sin(progress * math.pi * 3)
            wave.append((fundamental + harmonic2 + harmonic3 + noise) * amplitude)
    
    else:
        # Default short beep
        duration = 0.1
        n_samples = int(duration * sample_rate)
        wave = [math.sin(2 * math.pi * 440 * t / sample_rate) for t in range(n_samples)]
    
    # Convert to int16 with volume control (higher volume for voice sounds)
    int_wave = [int(32767 * 0.5 * sample) for sample in wave]
    
    # Convert to stereo
    stereo_wave = []
    for sample in int_wave:
        stereo_wave.extend([sample, sample])
    
    # Create sound from array
    sound_array = np.array(stereo_wave, dtype=np.int16)
    sound = pygame.mixer.Sound(sound_array)
    return sound

# --- Magic Circle (Adapted for non-blocking) ---
class MagicCircle:
    def __init__(self, player_id, center_x=600, center_y=400):
        self.player_id = player_id
        self.center_x = center_x
        self.center_y = center_y
        self.seed = int(time.time() * 1000) % (2**32)
        random.seed(self.seed)
        
        # Core geometric shape
        self.base_shape = random.choice(['circle', 'triangle', 'square', 'pentagon', 'hexagon', 'octagon', 'star'])
        self.shape_sides = {
            'triangle': 3, 'square': 4, 'pentagon': 5, 
            'hexagon': 6, 'octagon': 8, 'star': 5, 'circle': 12
        }[self.base_shape]
        
        # Pattern parameters
        self.num_spokes = random.choice([8, 12, 16])
        self.num_layers = random.randint(4, 6)
        self.base_radius = random.randint(40, 50)
        self.layer_spacing = random.randint(20, 28)
        
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
        
        # Pre-calculate points for aim trainer
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
        
        # Generate points at the outer edge of the pattern
        outer_radius = self.base_radius + (self.num_layers * self.layer_spacing)
        
        for i in range(self.num_spokes):
            angle = i * angle_step + self.rotation_offset
            x = center_x + int(outer_radius * math.cos(math.radians(angle)))
            y = center_y + int(outer_radius * math.sin(math.radians(angle)))
            self.pattern_points.append((x, y))

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
        outer_radius = self.base_radius + (self.num_layers * self.layer_spacing)
        for i in range(self.num_spokes):
            angle = i * angle_step + self.rotation_offset + elapsed * 5
            end_x = center_x + int(outer_radius * math.cos(math.radians(angle)))
            end_y = center_y + int(outer_radius * math.sin(math.radians(angle)))
            pygame.draw.line(screen, self.tertiary_color, (center_x, center_y), (end_x, end_y), 1)

# --- Flower (Using Assets or Procedural) ---
class Flower:
    def __init__(self, x, y, assets=None):
        self.x = x
        self.y = y
        self.assets = assets
        self.bloomed = False
        self.bloom_start_time = 0
        self.core_size = 15
        self.image = random.choice(assets) if assets else None
        
        # Procedural fallback colors
        color_schemes = [
            [(255, 105, 180), (255, 182, 193), (255, 20, 147)], # Pink
            [(186, 85, 211), (221, 160, 221), (147, 112, 219)], # Purple
            [(255, 127, 80), (255, 160, 122), (255, 99, 71)],   # Orange
            [(135, 206, 250), (173, 216, 230), (100, 149, 237)] # Blue
        ]
        self.petal_colors = random.choice(color_schemes)

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
                w = int(self.image.get_width() * scale * 0.5)
                h = int(self.image.get_height() * scale * 0.5)
                if w > 0 and h > 0:
                    scaled_img = pygame.transform.scale(self.image, (w, h))
                    rect = scaled_img.get_rect(center=(self.x, self.y))
                    screen.blit(scaled_img, rect)
            else:
                # Procedural drawing (Layered bloom)
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
        
        # Load Assets
        self.flower_assets = self._load_assets()
        
        # Game State
        self.state = "CALIBRATION" # CALIBRATION, GAME, REPORT
        self.state_timer = time.time()
        
        # Game Logic
        self.flowers = []
        self.current_flower_idx = 0
        self.score = 0
        self.misses = 0
        self.flower_timeout = 1.5 # Seconds per flower
        self.last_flower_spawn_time = 0
        self.reaction_times = []
        
        # Sounds
        self.timeout_sound = generate_beep_sound(200, 0.2)
        self.success_sound = generate_beep_sound(880, 0.1)
        self.disturbance_sounds = [
            generate_voice_sound('bird'),
            generate_voice_sound('dog'),
            generate_voice_sound('cat'),
            generate_voice_sound('mosquito')
        ]
        
        # Exit Button
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
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

    def _load_assets(self):
        assets = []
        base_path = os.path.dirname(os.path.abspath(__file__))
        search_paths = [
            os.path.join(base_path, "assets"),
            base_path,
            os.path.join(base_path, "../../Asset"),
            os.path.join(base_path, "../../../Asset")
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                for f in os.listdir(path):
                    if f.lower().endswith('.png') or f.lower().endswith('.jpg'):
                        try:
                            img = pygame.image.load(os.path.join(path, f)).convert_alpha()
                            assets.append(img)
                        except:
                            pass
        return assets

    def on_enter(self):
        print("Entering Game 1: Plant MeiLam")
        self.state = "CALIBRATION"
        self.state_timer = time.time()
        
        # Initialize flowers positions
        self.flowers = []
        points = self.magic_circle.pattern_points[:]
        random.shuffle(points)
        
        # Ensure we have 12 flowers
        center_x, center_y = self.screen_width // 2, self.screen_height // 2
        for i in range(12):
            if i < len(points):
                x, y = points[i]
            else:
                angle = random.uniform(0, 360)
                radius = random.uniform(50, 200)
                x = center_x + int(radius * math.cos(math.radians(angle)))
                y = center_y + int(radius * math.sin(math.radians(angle)))
            self.flowers.append(Flower(x, y, self.flower_assets))

    def update(self):
        # Update Eye Tracking via Framework
        if hasattr(self.manager, 'eye_tracker') and hasattr(self.manager.camera, 'current_frame'):
            self.manager.eye_tracker.process_frame(self.manager.camera.current_frame)
        
        current_time = time.time()
        
        # State Machine
        if self.state == "CALIBRATION":
            # Show magic circle for 5 seconds
            if current_time - self.state_timer > 5.0:
                self.state = "GAME"
                self.current_flower_idx = 0
                self.last_flower_spawn_time = current_time
                print("Starting Game Phase")

        elif self.state == "GAME":
            if self.current_flower_idx < len(self.flowers):
                # Disturbance sounds logic
                if self.current_flower_idx >= 2 and not (4 <= self.current_flower_idx <= 6):
                     # Simple random chance for disturbance
                     if random.random() < 0.02: # Low chance per frame
                         random.choice(self.disturbance_sounds).play()

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
                self.manager.data["scores"]["game1"] = {
                    "score": self.score,
                    "misses": self.misses,
                    "reaction_times": self.reaction_times
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
        pygame.draw.rect(screen, (200, 50, 50), self.exit_btn_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.exit_btn_rect, 2, border_radius=5)
        exit_text = self.small_font.render("EXIT", True, (255, 255, 255))
        screen.blit(exit_text, (self.exit_btn_rect.centerx - exit_text.get_width()//2, self.exit_btn_rect.centery - exit_text.get_height()//2))
        
        if self.state == "CALIBRATION":
            text = self.font.render("Calibrating... Relax your eyes", True, (255, 255, 255))
            screen.blit(text, (self.screen_width // 2 - text.get_width()//2, 100))
            
        elif self.state == "GAME":
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
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0, 0))
        
        # Draw semi-transparent background for text area on left
        bg_height = self.screen_height - 200
        text_bg = pygame.Surface((400, bg_height))
        text_bg.set_alpha(240)
        text_bg.fill((245, 245, 245))
        screen.blit(text_bg, (20, 100))
        
        # Use class fonts
        font_title = self.font
        font_subtitle = self.small_font
        font_normal = self.small_font
        
        title = font_title.render("YOUR CONCENTRATION ARTWORK", True, (255, 255, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width()//2, 30))
        
        # Stats
        x_left = 40
        y = 130
        
        header = font_subtitle.render("Performance Metrics", True, (44, 62, 80))
        screen.blit(header, (x_left, y))
        y += 50
        
        bloomed_count = self.score
        accuracy_pct = (bloomed_count / 12) * 100
        
        bloomed_label = font_normal.render(f"Flowers Bloomed: {bloomed_count}/12 ({accuracy_pct:.0f}%)", True, (44, 62, 80))
        screen.blit(bloomed_label, (x_left, y))
        y += 40
        
        if self.reaction_times:
            avg_reaction = sum(self.reaction_times) / len(self.reaction_times)
            reaction_label = font_normal.render(f"Avg Reaction Time: {avg_reaction:.3f}s", True, (44, 62, 80))
            screen.blit(reaction_label, (x_left, y))
            y += 40
            
        # Assessment
        if bloomed_count >= 10:
            assessment = "Outstanding!"
            color = (39, 174, 96)
        elif bloomed_count >= 7:
            assessment = "Great Work!"
            color = (52, 152, 219)
        else:
            assessment = "Keep Practicing!"
            color = (231, 76, 60)
            
        assess_text = font_title.render(assessment, True, color)
        screen.blit(assess_text, (x_left, y + 20))
        
        # Instruction to exit
        exit_text = font_normal.render("Press SPACE to return to Menu", True, (200, 200, 200))
        screen.blit(exit_text, (self.screen_width // 2 - exit_text.get_width()//2, self.screen_height - 100))
