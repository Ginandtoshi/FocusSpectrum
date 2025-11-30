from __future__ import annotations

import math
import random
import sys
import os
from typing import Dict, Iterable, List, Optional, Tuple

import pygame
try:
    from noise import pnoise3
except ImportError:
    # Fallback if noise is not installed (e.g. Windows without C++ compiler)
    from perlin_noise import PerlinNoise
    _noise_cache = {}
    def pnoise3(x, y, z, octaves=1, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, repeatz=1024, base=0.0):
        key = (octaves, 1)
        if key not in _noise_cache:
            _noise_cache[key] = PerlinNoise(octaves=octaves, seed=1)
        return _noise_cache[key]([x, y, z]) * 2.0

from scene_base import Scene

# -- Configuration defaults -------------------------------------------------

FRAME_RATE = 60 # Increased for smoother animation in game loop

# Unicode block characters matching the reference image style
ASCII_CHARS_CALM: list[str] = [
    " ", "·", ".", ":", "∙", "░", "▒", "▓",
    "─", "│", "┌", "┐", "└", "┘", "├", "┤",
    "┬", "┴", "┼", "╱", "╲", "╳",
    "▏", "▎", "▍", "▌", "▋", "▊", "▉",
    "⠁", "⠃", "⠇", "⠏", "⠟", "⠿",
]

ASCII_CHARS_CHAOTIC: list[str] = [
    "█", "▓", "▒", "░", "▄", "▀", "▌", "▐",
    "▖", "▗", "▘", "▙", "▚", "▛", "▜", "▝", "▞", "▟",
    "▂", "▃", "▄", "▅", "▆", "▇", "█",
    "┃", "━", "╳", "╱", "╲",
    "⣿", "⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯",
    "⠿", "⡿", "⣿",
]

FONT_CHOICES = ["consolas", "couriernew", "lucidaconsole", "dejavusansmono", "monospace"]

# -- Rorschach Blob Configuration -------------------------------------------

CRYSTAL_COLORS = [
    '#086788',  # Deep Blue - Most Focused
    '#57aab4',  # Cyan
    '#a6ece0',  # Light Cyan
    '#d2dde9',  # Pale Blue
    '#fecef1',  # Pale Pink
    '#ffc3bc',  # Light Coral
    '#ffb787',  # Apricot
    '#ff9f1c',  # Orange Yellow - Transition
    '#e9564c',  # Coral Red
    '#d30c7b',  # Deep Pink - Most Distracted
]

# -- Utility functions ------------------------------------------------------

def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def lerp_color(color_a: tuple[int, int, int], color_b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(ca, cb, t)) for ca, cb in zip(color_a, color_b))

def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))

def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if in_max == in_min:
        return out_min
    return out_min + (out_max - out_min) * ((value - in_min) / (in_max - in_min))

# =============================================================================
# Rorschach Blob Visualizer
# =============================================================================

class RorschachBlob:
    """
    Dynamic Biological Rorschach Inkblot Renderer.
    """
    
    def __init__(
        self,
        surface: pygame.Surface,
        center_x: float,
        center_y: float,
        size: float,
        focus_score: float = 75.0,
        distraction_count: int = 5,
        error_count: int = 0,
    ):
        self.surface = surface
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        
        # User Data
        self.focus_score = clamp(focus_score, 0.0, 100.0)
        self.distraction_count = distraction_count
        self.error_count = error_count
        
        # Derived Parameters
        self.focus_ratio = self.focus_score / 100.0
        self.is_focused = self.focus_score > 50
        
        # Visual Parameters
        self.max_radius = 6
        self.noise_octaves = 3
        self.frame_count = 0
        
        # Apply Data Mapping
        self._apply_data_mapping()
        
        # Create fade surface for trails
        self.fade_surface = pygame.Surface(
            (int(self.size * 2.5), int(self.size * 2.5)),
            pygame.SRCALPHA
        )
        # Lower alpha for longer trails to fill gaps from fewer particles
        fade_alpha = int(map_range(self.focus_ratio, 0.0, 1.0, 5, 12))
        self.fade_surface.fill((245, 243, 240, fade_alpha))
        
        # Draw Rect
        self.draw_rect = pygame.Rect(
            int(self.center_x - self.size * 1.25),
            int(self.center_y - self.size * 1.25),
            int(self.size * 2.5),
            int(self.size * 2.5)
        )
        
        # Buffer
        self.buffer = pygame.Surface(
            (int(self.size * 2.5), int(self.size * 2.5)),
            pygame.SRCALPHA
        )
        self.buffer.fill((0, 0, 0, 0))
        
        # Mask
        self._create_circular_mask()
    
    def _create_circular_mask(self):
        w, h = self.buffer.get_size()
        self.mask_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.mask_surface.fill((0, 0, 0, 0))
        
        center = (w // 2, h // 2)
        radius = min(w, h) // 2 - 10
        pygame.draw.circle(self.mask_surface, (255, 255, 255, 255), center, radius)
    
    def _apply_data_mapping(self):
        # 1. Speed
        base_speed = 0.003
        self.speed = base_speed + (self.distraction_count * 0.0015)
        self.speed = min(self.speed, 0.025)
        
        # 2. Scale
        self.scale = 0.005 + ((100 - self.focus_score) / 100) * 0.008
        
        # 3. Spread
        base_spread = 1.2
        error_factor = min(self.error_count * 0.08, 0.6)
        self.spread = base_spread + error_factor
        
        # 4. Particle Count
        # Reduced count to improve performance with pure-Python noise library
        self.n_plotters = int(map_range(self.focus_ratio, 0.0, 1.0, 150, 300))
        
        # 5. Radius
        # Increased radius to compensate for fewer particles
        self.max_radius = map_range(self.focus_ratio, 0.0, 1.0, 8, 16)
        
        # 6. Octaves
        self.noise_octaves = int(map_range(self.focus_ratio, 0.0, 1.0, 5, 2))
        
        # 7. Palette
        self._build_color_palette()
    
    def _build_color_palette(self):
        crystal_palette = [hex_to_rgb(c) for c in CRYSTAL_COLORS]
        
        extended_palette = {
            "deep_blue": (6, 82, 110),
            "blue": crystal_palette[0],
            "cyan": crystal_palette[1],
            "light_cyan": crystal_palette[2],
            "pale_blue": crystal_palette[3],
            "pale_pink": crystal_palette[4],
            "coral_light": crystal_palette[5],
            "apricot": crystal_palette[6],
            "orange": crystal_palette[7],
            "coral_red": crystal_palette[8],
            "deep_pink": crystal_palette[9],
            "magenta": (180, 8, 100),
        }
        
        if self.focus_ratio >= 0.8:
            self.primary_colors = [extended_palette["deep_blue"], extended_palette["blue"], extended_palette["cyan"]]
            self.secondary_colors = [extended_palette["blue"], extended_palette["cyan"], extended_palette["light_cyan"]]
        elif self.focus_ratio >= 0.65:
            self.primary_colors = [extended_palette["cyan"], extended_palette["light_cyan"], extended_palette["blue"]]
            self.secondary_colors = [extended_palette["light_cyan"], extended_palette["pale_blue"], extended_palette["cyan"]]
        elif self.focus_ratio >= 0.5:
            self.primary_colors = [extended_palette["light_cyan"], extended_palette["pale_blue"], extended_palette["pale_pink"]]
            self.secondary_colors = [extended_palette["pale_blue"], extended_palette["pale_pink"], extended_palette["coral_light"]]
        elif self.focus_ratio >= 0.35:
            self.primary_colors = [extended_palette["apricot"], extended_palette["orange"], extended_palette["coral_light"]]
            self.secondary_colors = [extended_palette["coral_light"], extended_palette["apricot"], extended_palette["pale_pink"]]
        elif self.focus_ratio >= 0.2:
            self.primary_colors = [extended_palette["coral_red"], extended_palette["orange"], extended_palette["apricot"]]
            self.secondary_colors = [extended_palette["orange"], extended_palette["coral_red"], extended_palette["deep_pink"]]
        else:
            self.primary_colors = [extended_palette["deep_pink"], extended_palette["magenta"], extended_palette["coral_red"]]
            self.secondary_colors = [extended_palette["magenta"], extended_palette["deep_pink"], extended_palette["coral_red"]]

    def _get_color_palette(self, noise_value: float) -> Tuple[Tuple[int, int, int, int], float]:
        base_alpha = int(map_range(self.focus_ratio, 0.0, 1.0, 180, 220))
        
        primary_idx = int(noise_value * (len(self.primary_colors) - 1))
        primary_idx = max(0, min(primary_idx, len(self.primary_colors) - 1))
        primary = self.primary_colors[primary_idx] + (base_alpha,)
        
        secondary_idx = int(noise_value * (len(self.secondary_colors) - 1))
        secondary_idx = max(0, min(secondary_idx, len(self.secondary_colors) - 1))
        secondary = self.secondary_colors[secondary_idx] + (base_alpha - 20,)
        
        colors = [primary, secondary, primary, secondary, primary, primary, secondary, primary, secondary, primary]
        
        n = len(colors)
        segment_size = 1.0 / n
        index = int(noise_value / segment_size)
        index = max(0, min(index, n - 1))
        
        position_in_segment = (noise_value - (index * segment_size)) / segment_size
        
        center = 0.5
        sharpness = map_range(self.focus_ratio, 0.0, 1.0, 0.3, 0.5)
        radius_scale = 2.0 * (sharpness + (center - sharpness) - abs(position_in_segment - center))
        radius_scale = clamp(radius_scale, 0.0, 1.0)
        radius = self.max_radius * radius_scale
        
        return colors[index], radius
    
    def _rotate_point(self, x: float, y: float, angle: float) -> Tuple[float, float]:
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
    
    def update_and_draw(self):
        self.buffer.blit(self.fade_surface, (0, 0))
        
        buffer_center_x = self.buffer.get_width() / 2
        buffer_center_y = self.buffer.get_height() * 0.55
        
        for _ in range(self.n_plotters):
            seed_a = random.random() * 100
            seed_b = random.random() * 100
            
            n1 = pnoise3(seed_a, seed_b, 0, octaves=self.noise_octaves)
            n2 = pnoise3(seed_b, seed_a, 0, octaves=self.noise_octaves)
            
            x0 = n1 * self.size * self.spread
            y0 = n2 * self.size * self.spread
            
            rotation_angle = -3 * math.pi / 4
            x, y = self._rotate_point(x0, y0, rotation_angle)
            
            noise_val = pnoise3(
                x * self.scale,
                y * self.scale,
                self.frame_count * self.speed,
                octaves=self.noise_octaves,
                persistence=0.5
            )
            noise_val = (noise_val + 1.0) / 2.0
            noise_val = clamp(noise_val, 0.0, 1.0)
            
            color, radius = self._get_color_palette(noise_val)
            
            if radius > 0.5:
                screen_x = int(x + buffer_center_x)
                screen_y = int(y + buffer_center_y)
                
                if 0 <= screen_x < self.buffer.get_width() and 0 <= screen_y < self.buffer.get_height():
                    pygame.draw.circle(
                        self.buffer,
                        color[:3],
                        (screen_x, screen_y),
                        int(radius)
                    )
        
        output = pygame.Surface(self.buffer.get_size(), pygame.SRCALPHA)
        output.fill((0, 0, 0, 0))
        output.blit(self.buffer, (0, 0))
        output.blit(self.mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        self.surface.blit(output, self.draw_rect.topleft)
        self.frame_count += 1
    
    def reset(self):
        self.frame_count = 0
        self.buffer.fill((255, 255, 255, 255))

# =============================================================================
# Report Scene
# =============================================================================

class ReportScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        
        # 1. Calculate Data
        self.scores = self.manager.data.get("scores", {})
        self.calculate_metrics()
        
        # 2. Initialize Fonts
        self.init_fonts()
        
        # 3. Colors
        self.bg_color = (245, 243, 240)
        self.text_color = (60, 60, 65)
        self.light_text = (160, 160, 165)
        self.accent_color = (200, 195, 190)
        
        # 4. Rorschach State
        self.rorschach = None
        self.rorschach_initialized = False
        self.circle_center = (0, 0)
        self.circle_radius = 0
        
        # 5. Layout State
        self.nav_height = 50
        self.left_col_width = 0
        self.right_col_width = 0

    def calculate_metrics(self):
        g1_score = 0
        g2_collisions = 0
        g3_distraction = 0
        g3_errors = 0
        
        has_data = False
        
        # Game 1: Plant (Attention)
        if "game1" in self.scores:
            has_data = True
            g1_data = self.scores["game1"]
            g1_raw = g1_data.get("score", 0)
            self.g1_focus = (g1_raw / 12.0) * 100.0
        else:
            self.g1_focus = 50.0

        # Game 2: Metaball (Focus/Tracking)
        if "game2" in self.scores:
            has_data = True
            g2_data = self.scores["game2"]
            g2_collisions = g2_data.get("collisions", 0)
            self.g2_focus = max(0, 100 - (g2_collisions * 5))
        else:
            self.g2_focus = 50.0
            
        # Game 3: Text (Cognitive)
        if "game3" in self.scores:
            has_data = True
            g3_data = self.scores["game3"]
            g3_distraction = g3_data.get("distraction_pct", 0)
            g3_errors = g3_data.get("errors", 0)
            self.g3_focus = max(0, 100 - g3_distraction - (g3_errors * 2))
        else:
            self.g3_focus = 50.0

        if not has_data:
            # Default "Medium" state
            self.focus_score = 50.0
            self.distraction_count = 5
            self.error_count = 0
            self.metrics_text = {"Duration": "N/A"}
        else:
            self.focus_score = (self.g1_focus + self.g2_focus + self.g3_focus) / 3.0
            self.distraction_count = int(g2_collisions + g3_errors)
            self.error_count = int(g3_errors)
            self.metrics_text = {
                "G1 Focus": f"{int(self.g1_focus)}%",
                "G2 Focus": f"{int(self.g2_focus)}%",
                "G3 Focus": f"{int(self.g3_focus)}%"
            }
            
        self.focus_ratio = self.focus_score / 100.0

    def init_fonts(self):
        self.hero_font = pygame.font.SysFont(["georgia", "times", "serif"], 58, bold=False)
        self.title_font = pygame.font.SysFont(["georgia", "times", "serif"], 42, bold=False)
        self.score_font = pygame.font.SysFont(FONT_CHOICES, 120, bold=True)
        self.nav_font = pygame.font.SysFont(FONT_CHOICES, 14)
        self.body_font = pygame.font.SysFont(["georgia", "times", "serif"], 15)
        self.small_font = pygame.font.SysFont(FONT_CHOICES, 12)
        self.watermark_font = pygame.font.SysFont(["arial", "helvetica", "sans-serif"], 180, bold=True)

    def _init_rorschach(self, screen):
        w, h = screen.get_size()
        
        self.left_col_width = w * 0.33
        self.right_col_width = w - self.left_col_width
        
        blob_size = min(self.right_col_width * 0.75, h * 0.8)
        
        center_x = self.left_col_width + self.right_col_width / 2
        center_y = h / 2
        
        self.rorschach = RorschachBlob(
            surface=screen,
            center_x=center_x,
            center_y=center_y,
            size=blob_size,
            focus_score=self.focus_score,
            distraction_count=self.distraction_count,
            error_count=self.error_count,
        )
        
        self.circle_center = (int(center_x), int(center_y))
        self.circle_radius = int(blob_size * 0.95)
        self.rorschach_initialized = True

    def _draw_nav_bar(self, screen, w, h):
        nav_y = self.nav_height
        
        nav_items_left = ["FocusSpectrum", "Report"]
        x = 30
        for item in nav_items_left:
            text = self.nav_font.render(item, True, self.text_color)
            screen.blit(text, (x, (nav_y - text.get_height()) // 2))
            x += text.get_width() + 25
        
        right_text = self.nav_font.render("USER SESSION 01", True, self.light_text)
        screen.blit(right_text, (w - right_text.get_width() - 30, (nav_y - right_text.get_height()) // 2))
        
        pygame.draw.line(screen, self.accent_color, (0, nav_y), (w, nav_y), 1)

    def _draw_left_content(self, screen, w, h):
        content_x = 30
        content_y = h * 0.25
        
        if self.focus_ratio > 0.7:
            line1 = "Focus"
            line2 = "Achieved."
        elif self.focus_ratio > 0.4:
            line1 = "Stay"
            line2 = "Focused."
        else:
            line1 = "Need"
            line2 = "Focus."
        
        title1 = self.hero_font.render(line1, True, self.text_color)
        screen.blit(title1, (content_x, content_y))
        
        title2 = self.hero_font.render(line2, True, self.text_color)
        screen.blit(title2, (content_x, content_y + title1.get_height() + 5))
        
        line_y = content_y + title1.get_height() * 2 + 40
        pygame.draw.line(screen, self.accent_color, (content_x, line_y), (self.left_col_width - 20, line_y), 1)
        
        desc_y = line_y + 30
        
        # --- Description Title ---
        if self.focus_ratio > 0.7:
            desc_title = "Excellent concentration achieved."
        elif self.focus_ratio > 0.4:
            desc_title = "Good focus with room to improve."
        else:
            desc_title = "Focus needs improvement."
        
        title_surf = self.body_font.render(desc_title, True, self.text_color)
        screen.blit(title_surf, (content_x, desc_y))
        desc_y += 30

        # --- Overall Stats ---
        desc_lines = [
            f"Overall Score: {self.focus_score:.0f}/100",
            f"Distractions: {self.distraction_count}",
            f"Errors: {self.error_count}",
        ]
        
        for line in desc_lines:
            line_surf = self.small_font.render(line, True, self.light_text)
            screen.blit(line_surf, (content_x, desc_y))
            desc_y += 22
            
        desc_y += 10

        # --- Per-Game Metrics ---
        for key, val in self.metrics_text.items():
            line_surf = self.small_font.render(f"{key}: {val}", True, self.light_text)
            screen.blit(line_surf, (content_x, desc_y))
            desc_y += 22

        desc_y += 30
        link_text = self.small_font.render("Press SPACE to Return to Menu", True, self.text_color)
        screen.blit(link_text, (content_x, desc_y))

    def _draw_circle_background(self, screen):
        circle_color = (215, 212, 208)
        pygame.draw.circle(screen, circle_color, self.circle_center, self.circle_radius)

    def _draw_bottom_watermark(self, screen, w, h):
        watermark = "FOCUS"
        watermark_surf = self.watermark_font.render(watermark, True, self.accent_color)
        watermark_x = w // 2 - watermark_surf.get_width() // 2
        watermark_y = h - watermark_surf.get_height() // 2 - 20
        screen.blit(watermark_surf, (watermark_x, watermark_y))

    def _draw_score_display(self, screen):
        score_warm = hex_to_rgb("#d30c7b")
        score_cool = hex_to_rgb("#086788")
        score_color = lerp_color(score_warm, score_cool, self.focus_ratio)
        
        score_text = self.score_font.render(f"{self.focus_score:.0f}", True, score_color)
        score_rect = score_text.get_rect(center=self.circle_center)
        screen.blit(score_text, score_rect)

    def _draw_grid_lines(self, screen, w, h):
        pygame.draw.line(screen, (230, 228, 225), 
                        (self.left_col_width, 0), 
                        (self.left_col_width, h), 1)

    def draw(self, screen):
        if not self.rorschach_initialized:
            self._init_rorschach(screen)
            
        w, h = screen.get_size()
        
        # 1. Background
        screen.fill(self.bg_color)
        
        # 2. Grid Lines
        self._draw_grid_lines(screen, w, h)
        
        # 3. Watermark
        self._draw_bottom_watermark(screen, w, h)
        
        # 4. Circle Background
        self._draw_circle_background(screen)
        
        # 5. Rorschach Blob
        if self.rorschach:
            self.rorschach.update_and_draw()
            
        # 6. Score Overlay
        # self._draw_score_display(screen)
            
        # 7. Nav Bar
        self._draw_nav_bar(screen, w, h)
        
        # 8. Left Content
        self._draw_left_content(screen, w, h)
        
        # 9. Right Description (Merged into Left Content)
        # self._draw_right_description(screen, w, h)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    from menu_scene import MenuScene
                    self.next_scene = MenuScene(self.manager)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.rorschach:
                    self.rorschach.reset()

    def update(self):
        pass
