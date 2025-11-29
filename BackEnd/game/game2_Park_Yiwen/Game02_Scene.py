import pygame
import cv2
import numpy as np
import time
import collections
import math
import mediapipe as mp
import random
import sys
import os

# Add parent directory to path to allow importing scene_base
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from scene_base import Scene

# --- Helper Functions ---
def hsv_to_rgb(h, s, v):
    """HSV颜色空间转RGB"""
    h = max(0.0, min(1.0, h)) % 1.0
    s = max(0.0, min(1.0, s))
    v = max(0.0, min(1.0, v))
    
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    
    if i == 0:
        r, g, b = int(v * 255), int(t * 255), int(p * 255)
    elif i == 1:
        r, g, b = int(q * 255), int(v * 255), int(p * 255)
    elif i == 2:
        r, g, b = int(p * 255), int(v * 255), int(t * 255)
    elif i == 3:
        r, g, b = int(p * 255), int(q * 255), int(v * 255)
    elif i == 4:
        r, g, b = int(t * 255), int(p * 255), int(v * 255)
    else:
        r, g, b = int(v * 255), int(p * 255), int(q * 255)
    
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def draw_pupil_eye(screen, x, y, radius, time_factor=0):
    """绘制瞳孔样式的眼睛"""
    center_x, center_y = int(x), int(y)
    pupil_radius = max(3, int(radius * 0.3))
    iris_radius = int(radius)
    
    for r in range(iris_radius, pupil_radius, -1):
        distance_ratio = (r - pupil_radius) / (iris_radius - pupil_radius)
        hue = (0.1 + distance_ratio * 0.2 + time_factor * 0.1) % 1.0
        saturation = 0.6 + distance_ratio * 0.3
        brightness = 0.4 + distance_ratio * 0.5
        color = hsv_to_rgb(hue, saturation, brightness)
        pygame.draw.circle(screen, color, (center_x, center_y), r)
    
    num_rays = 48
    for i in range(num_rays):
        angle = (i / num_rays) * 2 * math.pi + time_factor * 0.3
        inner_r = pupil_radius + 2
        outer_r = iris_radius - 2
        ray_hue = (0.15 + (i % 8) * 0.02 + time_factor * 0.05) % 1.0
        ray_brightness = 0.3 + (i % 3) * 0.2
        ray_color = hsv_to_rgb(ray_hue, 0.8, ray_brightness)
        
        for j in range(3):
            offset_angle = angle + (j - 1) * 0.02
            start_x = center_x + inner_r * math.cos(offset_angle)
            start_y = center_y + inner_r * math.sin(offset_angle)
            end_x = center_x + outer_r * math.cos(offset_angle)
            end_y = center_y + outer_r * math.sin(offset_angle)
            
            line_width = max(1, int(radius * 0.03))
            if j == 1:
                pygame.draw.line(screen, ray_color, (start_x, start_y), (end_x, end_y), line_width)
            else:
                darker_color = tuple(int(c * 0.7) for c in ray_color)
                pygame.draw.line(screen, darker_color, (start_x, start_y), (end_x, end_y), max(1, line_width // 2))
    
    for ring in range(3):
        ring_radius = pupil_radius + (iris_radius - pupil_radius) * (0.3 + ring * 0.25)
        ring_color = hsv_to_rgb((0.12 + ring * 0.03 + time_factor * 0.02) % 1.0, 0.7, 0.6 - ring * 0.1)
        
        for segment in range(0, 360, 15):
            if (segment + int(time_factor * 10)) % 45 < 30:
                start_angle = math.radians(segment)
                points = []
                for a in range(segment, segment + 10, 2):
                    rad = math.radians(a)
                    px = center_x + ring_radius * math.cos(rad)
                    py = center_y + ring_radius * math.sin(rad)
                    points.append((px, py))
                
                if len(points) > 1:
                    pygame.draw.lines(screen, ring_color, False, points, max(1, int(radius * 0.02)))
    
    pygame.draw.circle(screen, (20, 20, 25), (center_x, center_y), pupil_radius)
    highlight_x = center_x - pupil_radius // 3
    highlight_y = center_y - pupil_radius // 3
    highlight_radius = max(1, pupil_radius // 4)
    pygame.draw.circle(screen, (180, 180, 200), (highlight_x, highlight_y), highlight_radius)
    pygame.draw.circle(screen, (100, 80, 60), (center_x, center_y), iris_radius, 2)

# --- Classes ---
class InterferenceRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.wave_sources = []
        self.noise_points = []
        self.last_update = 0
        self.update_interval = 0.08
        
    def update_interference(self, current_time, metaball_renderer):
        if current_time - self.last_update < self.update_interval:
            return
        self.wave_sources = []
        self.noise_points = []
        
        num_wave_sources = random.randint(8, 12)
        for _ in range(num_wave_sources):
            x = random.randint(30, self.width - 30)
            y = random.randint(30, self.height - 30)
            if not metaball_renderer.is_point_in_focus_area(x, y):
                intensity = random.uniform(0.6, 1.5)
                frequency = random.uniform(0.8, 3.0)
                wave_type = random.choice(['radial', 'spiral', 'flow', 'burst', 'web', 'chaos'])
                color_hue = random.uniform(0.0, 1.0)
                scale = random.uniform(0.8, 2.5)
                self.wave_sources.append({
                    'x': x, 'y': y, 'intensity': intensity, 
                    'frequency': frequency, 'type': wave_type,
                    'hue': color_hue, 'phase': random.uniform(0, 6.28),
                    'scale': scale, 'rotation': random.uniform(0, 6.28)
                })
        
        num_noise = random.randint(60, 100)
        for _ in range(num_noise):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            if not metaball_renderer.is_point_in_focus_area(x, y):
                size = random.randint(1, 5)
                alpha = random.uniform(0.3, 0.9)
                color = (random.randint(80, 255), random.randint(80, 255), random.randint(100, 255))
                effect_type = random.choice(['dot', 'cross', 'star'])
                self.noise_points.append({
                    'x': x, 'y': y, 'size': size, 
                    'color': color, 'alpha': alpha, 'type': effect_type
                })
        self.last_update = current_time
    
    def render_wave_patterns(self, screen, current_time):
        for source in self.wave_sources:
            if source['type'] == 'radial': self.draw_radial_waves(screen, source, current_time)
            elif source['type'] == 'spiral': self.draw_spiral_waves(screen, source, current_time)
            elif source['type'] == 'flow': self.draw_flow_lines(screen, source, current_time)
            elif source['type'] == 'burst': self.draw_burst_pattern(screen, source, current_time)
            elif source['type'] == 'web': self.draw_web_pattern(screen, source, current_time)
            elif source['type'] == 'chaos': self.draw_chaos_lines(screen, source, current_time)
    
    def draw_radial_waves(self, screen, source, current_time):
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        rotation = source['rotation'] + current_time * 0.5
        for layer in range(3):
            layer_offset = layer * 0.4
            for angle in range(0, 360, 6):
                rad = math.radians(angle + rotation * 25)
                intensity_variation = math.sin(phase + angle * 0.05 + layer_offset) * 0.5 + 0.8
                base_length = 50 + layer * 25
                length = base_length + intensity_variation * 80 * source['scale']
                end_x = center_x + length * math.cos(rad)
                end_y = center_y + length * math.sin(rad)
                color_intensity = source['intensity'] * intensity_variation * (1 - layer * 0.2)
                hue = (source['hue'] + angle * 0.008 + layer * 0.15) % 1.0
                color = hsv_to_rgb(hue, 0.8, min(1.0, color_intensity))
                if (0 <= end_x <= self.width and 0 <= end_y <= self.height):
                    line_width = max(1, 3 - layer)
                    pygame.draw.line(screen, color, (center_x, center_y), (end_x, end_y), line_width)

    def draw_burst_pattern(self, screen, source, current_time):
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        for burst in range(5):
            burst_phase = phase + burst * 1.2
            burst_radius = 25 + burst * 35 + math.sin(burst_phase) * 20
            points = []
            for angle in range(0, 360, 12):
                rad = math.radians(angle)
                variation = math.sin(burst_phase + angle * 0.1) * 0.5 + 1.0
                r = burst_radius * variation * source['scale']
                x = center_x + r * math.cos(rad)
                y = center_y + r * math.sin(rad)
                if 0 <= x <= self.width and 0 <= y <= self.height:
                    points.append((x, y))
            if len(points) > 2:
                color = hsv_to_rgb((source['hue'] + burst * 0.15) % 1.0, 0.9, source['intensity'] * (1 - burst * 0.15))
                try: pygame.draw.lines(screen, color, True, points, max(1, 3 - burst))
                except: pass

    def draw_web_pattern(self, screen, source, current_time):
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        web_points = []
        for ring in range(1, 6):
            ring_radius = ring * 30 * source['scale']
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                noise = math.sin(phase + angle * 0.05 + ring * 0.3) * 10
                r = ring_radius + noise
                x = center_x + r * math.cos(rad)
                y = center_y + r * math.sin(rad)
                web_points.append((x, y, ring, angle))
        for i, (x1, y1, ring1, angle1) in enumerate(web_points):
            if 0 <= x1 <= self.width and 0 <= y1 <= self.height:
                for x2, y2, ring2, angle2 in web_points[i+1:]:
                    if (abs(ring1 - ring2) <= 1 or abs(angle1 - angle2) <= 60) and 0 <= x2 <= self.width and 0 <= y2 <= self.height:
                        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                        if distance < 100:
                            alpha = max(0.15, 1 - distance / 100)
                            color = hsv_to_rgb(source['hue'], 0.7, source['intensity'] * alpha)
                            pygame.draw.line(screen, color, (x1, y1), (x2, y2), max(1, int(2 - distance / 50)))

    def draw_chaos_lines(self, screen, source, current_time):
        start_x, start_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        for path in range(6):
            points = [(start_x, start_y)]
            current_x, current_y = start_x, start_y
            path_phase = phase + path * 0.8
            for step in range(30):
                chaos_x = math.sin(current_x * 0.025 + path_phase) * math.cos(step * 0.15) * 25
                chaos_y = math.cos(current_y * 0.02 + path_phase * 1.2) * math.sin(step * 0.12) * 25
                current_x += chaos_x * source['scale']
                current_y += chaos_y * source['scale']
                if 0 <= current_x <= self.width and 0 <= current_y <= self.height:
                    points.append((current_x, current_y))
                else: break
            if len(points) > 3:
                color = hsv_to_rgb((source['hue'] + path * 0.12) % 1.0, 0.8, source['intensity'] * 0.9)
                try: pygame.draw.lines(screen, color, False, points, max(1, 2 - path // 3))
                except: pass

    def draw_spiral_waves(self, screen, source, current_time):
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        points = []
        for i in range(0, 100, 2):
            angle = i * 0.2 + phase
            radius = i * 0.8 + math.sin(angle * 0.5 + phase) * 10
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            if 0 <= x <= self.width and 0 <= y <= self.height:
                points.append((x, y))
        if len(points) > 3:
            color = hsv_to_rgb(source['hue'], 0.6, source['intensity'])
            try: pygame.draw.lines(screen, color, False, points, 1)
            except: pass

    def draw_flow_lines(self, screen, source, current_time):
        start_x, start_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        points = [(start_x, start_y)]
        current_x, current_y = start_x, start_y
        for step in range(20):
            noise_x = math.sin(current_x * 0.02 + phase) + math.cos(current_y * 0.03 + phase * 0.7)
            noise_y = math.cos(current_x * 0.025 + phase * 1.3) + math.sin(current_y * 0.02 + phase)
            current_x += noise_x * 8
            current_y += noise_y * 8
            if 0 <= current_x <= self.width and 0 <= current_y <= self.height:
                points.append((current_x, current_y))
            else: break
        if len(points) > 2:
            color = hsv_to_rgb((source['hue'] + step * 0.02) % 1.0, 0.5, source['intensity'])
            try: pygame.draw.lines(screen, color, False, points, 1)
            except: pass

    def render_noise_points(self, screen):
        for point in self.noise_points:
            if point['type'] == 'dot':
                surf = pygame.Surface((point['size'] * 2, point['size'] * 2))
                surf.set_alpha(int(point['alpha'] * 255))
                surf.fill(point['color'])
                screen.blit(surf, (point['x'] - point['size'], point['y'] - point['size']))
            elif point['type'] == 'cross':
                x, y, size = point['x'], point['y'], point['size']
                pygame.draw.line(screen, point['color'], (x-size, y), (x+size, y), 2)
                pygame.draw.line(screen, point['color'], (x, y-size), (x, y+size), 2)
            elif point['type'] == 'star':
                x, y, size = point['x'], point['y'], point['size']
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    end_x = x + size * math.cos(rad)
                    end_y = y + size * math.sin(rad)
                    pygame.draw.line(screen, point['color'], (x, y), (end_x, end_y), 1)

    def render(self, screen, metaball_renderer):
        current_time = time.time()
        self.update_interference(current_time, metaball_renderer)
        self.render_wave_patterns(screen, current_time)
        self.render_noise_points(screen)

class Metaball:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        size = random.random() ** 1.2
        self.radius = 80 * size + 60
        speed = 3.5 * (1 - size) + 1.5
        angle = random.random() * 2 * math.pi
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        self.pos_x = width / 2 + random.randint(-80, 80)
        self.pos_y = height / 2 + random.randint(-60, 60)
    
    def update(self):
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        if self.pos_x < self.radius or self.pos_x > self.width - self.radius: self.vel_x *= -1
        if self.pos_y < self.radius or self.pos_y > self.height - self.radius: self.vel_y *= -1
        self.pos_x = max(self.radius, min(self.width - self.radius, self.pos_x))
        self.pos_y = max(self.radius, min(self.height - self.radius, self.pos_y))

class MetaballRenderer:
    def __init__(self, width, height, num_balls=2):
        self.width = width
        self.height = height
        self.metaballs = [Metaball(width, height) for _ in range(num_balls)]
        self.boundary_points = []
        self.boundary_colors = []
        self.last_update_time = 0
        self.update_interval = 0.05
    
    def update_size(self, width, height):
        old_width, old_height = self.width, self.height
        self.width = width
        self.height = height
        for ball in self.metaballs:
            ball.width = width
            ball.height = height
            ball.pos_x = ball.pos_x * width / old_width
            ball.pos_y = ball.pos_y * height / old_height
    
    def compute_metaball_value(self, x, y):
        v = 0.0
        for ball in self.metaballs:
            dx = ball.pos_x - x
            dy = ball.pos_y - y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0: v += (ball.radius * ball.radius) / dist_sq
        return v
    
    def update_boundary(self):
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval: return
        for ball in self.metaballs: ball.update()
        self.boundary_points = []
        self.boundary_colors = []
        step = 4
        threshold_min, threshold_max = 0.6, 0.8
        for x in range(0, self.width, step):
            for y in range(0, self.height, step):
                v = self.compute_metaball_value(x, y)
                if threshold_min < v < threshold_max:
                    a = (v - threshold_min) / (threshold_max - threshold_min)
                    hue = (a + current_time * 0.2) % 1.0
                    self.boundary_points.append((x, y))
                    self.boundary_colors.append(hsv_to_rgb(hue, 1.0, 1.0))
        self.last_update_time = current_time
    
    def is_point_in_focus_area(self, x, y):
        return self.compute_metaball_value(x, y) >= 0.7
    
    def render(self, screen):
        self.update_boundary()
        for i, point in enumerate(self.boundary_points):
            pygame.draw.circle(screen, self.boundary_colors[i], point, 2)

class GazeProvider:
    def __init__(self, screen_width, screen_height):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.position_history = collections.deque(maxlen=10)
        self.initial_radius = 15
        self.current_radius = self.initial_radius
        self.max_radius = 60
        self.growth_rate = 1.0
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-2, 2)
        self.max_speed = 3.0
        self.friction = 0.99
        self.auto_movement = False
        self.boundary_collision_count = 0
        self.last_in_focus = True
        self.last_touching_boundary = False

    def get_position(self): return (self.x, self.y)
    def get_radius(self): return self.current_radius
    def get_boundary_collisions(self): return self.boundary_collision_count
    
    def check_focus_boundary_collision(self, metaball_renderer):
        center_x, center_y = self.x, self.y
        radius = self.current_radius
        points_in_focus = 0
        angles = [i * 45 for i in range(8)]
        for angle in angles:
            rad = math.radians(angle)
            if metaball_renderer.is_point_in_focus_area(center_x + radius * math.cos(rad), center_y + radius * math.sin(rad)):
                points_in_focus += 1
        currently_touching_boundary = 0 < points_in_focus < len(angles)
        if not self.last_touching_boundary and currently_touching_boundary:
            self.boundary_collision_count += 1
        self.last_touching_boundary = currently_touching_boundary
        return metaball_renderer.is_point_in_focus_area(center_x, center_y)
    
    def update_ball_size(self, elapsed_time):
        target_radius = min(self.initial_radius + elapsed_time * self.growth_rate, self.max_radius)
        self.current_radius = self.current_radius * 0.98 + target_radius * 0.02
        return self.current_radius
    
    def reset_position(self, width, height):
        self.x, self.y = width // 2, height // 2
        self.position_history.clear()
        self.current_radius = self.initial_radius
        self.velocity_x, self.velocity_y = random.uniform(-2, 2), random.uniform(-2, 2)
        self.boundary_collision_count = 0
        self.last_in_focus = True
        self.last_touching_boundary = False
    
    def update(self, width, height):
        if self.auto_movement:
            self.x += self.velocity_x
            self.y += self.velocity_y
            if self.x <= self.current_radius or self.x >= width - self.current_radius:
                self.velocity_x *= -0.8
                self.x = max(self.current_radius, min(width - self.current_radius, self.x))
            if self.y <= self.current_radius or self.y >= height - self.current_radius:
                self.velocity_y *= -0.8
                self.y = max(self.current_radius, min(height - self.current_radius, self.y))
            self.velocity_x += random.uniform(-0.1, 0.1)
            self.velocity_y += random.uniform(-0.1, 0.1)
            speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            if speed > self.max_speed:
                self.velocity_x = self.velocity_x / speed * self.max_speed
                self.velocity_y = self.velocity_y / speed * self.max_speed
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction
        
        boundary_margin = 30
        if (self.x < -boundary_margin or self.x > width + boundary_margin or 
            self.y < -boundary_margin or self.y > height + boundary_margin):
            self.x, self.y = width // 2, height // 2
            self.velocity_x, self.velocity_y = random.uniform(-2, 2), random.uniform(-2, 2)
        return (self.x, self.y)

class HandGazeProvider(GazeProvider):
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.finger_history = collections.deque(maxlen=5)
        self.current_finger_pos = None
        self.calibration_points = []
        self.screen_points = []
        self.transform = None
        self.calibrated = False

    def process_frame(self, frame_rgb):
        """Process frame from framework camera"""
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            finger_tip = hand_landmarks.landmark[8]
            h, w, _ = frame_rgb.shape
            finger_x = int(finger_tip.x * w)
            finger_y = int(finger_tip.y * h)
            self.finger_history.append((finger_x, finger_y))
            if len(self.finger_history) >= 3:
                recent = list(self.finger_history)[-3:]
                avg_x = sum(pos[0] for pos in recent) / len(recent)
                avg_y = sum(pos[1] for pos in recent) / len(recent)
                self.current_finger_pos = (avg_x, avg_y)
            else:
                self.current_finger_pos = (finger_x, finger_y)
        else:
            # No hand detected
            pass

    def get_finger_position(self):
        return self.current_finger_pos
    
    def update(self, width, height):
        if self.auto_movement:
            super().update(width, height)
            return (self.x, self.y)
        
        boundary_margin = 20
        if (self.x < -boundary_margin or self.x > width + boundary_margin or 
            self.y < -boundary_margin or self.y > height + boundary_margin):
            self.x, self.y = width // 2, height // 2
            return (self.x, self.y)
        
        finger_pos = self.get_finger_position()
        if finger_pos is None: return (self.x, self.y)
        
        if self.calibrated and self.transform is not None:
            src = np.array([ [finger_pos[0], finger_pos[1], 1.0] ], dtype=np.float32)
            M = np.vstack([self.transform, [0,0,1]])
            res = (M @ src.T).T[0]
            target_x, target_y = float(res[0]), float(res[1])
            
            finger_dx = target_x - self.x
            finger_dy = target_y - self.y
            finger_distance = math.sqrt(finger_dx*finger_dx + finger_dy*finger_dy)
            
            if finger_distance < 10.0: return (self.x, self.y)
            
            base_response = 0.12
            if finger_distance < 25.0: response_factor = base_response * 1.3
            elif finger_distance < 60.0: response_factor = base_response
            else: response_factor = base_response * 0.85
            
            move_x = -finger_dx * response_factor
            move_y = -finger_dy * response_factor
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            self.position_history.append((new_x, new_y))
            if len(self.position_history) >= 3:
                recent = list(self.position_history)[-3:]
                weights = [0.15, 0.25, 0.6]
                avg_x = sum(pos[0] * w for pos, w in zip(recent, weights))
                avg_y = sum(pos[1] * w for pos, w in zip(recent, weights))
                self.x = self.x * 0.75 + avg_x * 0.25
                self.y = self.y * 0.75 + avg_y * 0.25
            else:
                self.x, self.y = new_x, new_y
            
            ball_radius = self.current_radius
            self.x = max(ball_radius, min(width - ball_radius, self.x))
            self.y = max(ball_radius, min(height - ball_radius, self.y))
        else:
            # Fallback if not calibrated: Direct mapping (mirrored)
            # Assuming camera is mirrored, moving hand right moves finger_pos right.
            # We want to map finger_pos to screen.
            self.x = finger_pos[0]
            self.y = finger_pos[1]

        return (self.x, self.y)

# --- Main Scene ---
class Game2Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.width, self.height = pygame.display.get_surface().get_size()
        
        self.metaball_renderer = MetaballRenderer(self.width, self.height, num_balls=2)
        self.interference_renderer = InterferenceRenderer(self.width, self.height)
        self.hand_provider = HandGazeProvider(self.width, self.height)
        
        self.game_active = False
        self.game_over = False
        self.game_start_time = None
        self.game_duration = 45.0
        self.score = 0
        
        # Load Font
        try:
            font_path = os.path.join(os.path.dirname(__file__), "../../../Asset/Algerian Regular.ttf")
            self.font = pygame.font.Font(font_path, 24)
            self.large_font = pygame.font.Font(font_path, 48)
        except:
            self.font = pygame.font.SysFont("Arial", 24)
            self.large_font = pygame.font.SysFont("Arial", 48)
            
        self.exit_btn_rect = pygame.Rect(self.width - 120, self.height - 60, 100, 40)

    def on_enter(self):
        print("Entering Game 2: Metaball Hand Tracking")
        self.hand_provider.reset_position(self.width, self.height)
        self.game_active = False
        self.game_over = False
        self.score = 0

    def update(self):
        # Process Camera Frame
        if hasattr(self.manager.camera, 'current_frame') and self.manager.camera.current_frame is not None:
            self.hand_provider.process_frame(self.manager.camera.current_frame)
        
        # Game Logic
        time_left = 0
        if self.game_active:
            if self.game_start_time:
                elapsed = time.time() - self.game_start_time
                time_left = max(0, self.game_duration - elapsed)
                
                if time_left <= 0:
                    self.game_active = False
                    self.game_over = True
                    # Game Over Logic here
        
        # Update Position
        self.hand_provider.update(self.width, self.height)
        
        # Update Size
        if self.game_active and self.game_start_time:
            elapsed = time.time() - self.game_start_time
            self.hand_provider.update_ball_size(elapsed)
            
        # Check Collisions
        ball_x, ball_y = self.hand_provider.get_position()
        if self.game_active:
            self.hand_provider.check_focus_boundary_collision(self.metaball_renderer)
            if self.metaball_renderer.is_point_in_focus_area(ball_x, ball_y):
                self.score += 1

    def draw(self, screen):
        # Background is already drawn by framework (Camera)
        # We can add a semi-transparent dark overlay to make the game elements pop
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 5, 15, 100)) # Dark blue tint with transparency
        screen.blit(overlay, (0, 0))
        
        # Render Interference
        self.interference_renderer.render(screen, self.metaball_renderer)
        
        # Render Metaballs
        self.metaball_renderer.render(screen)
        
        # Render Pupil
        ball_x, ball_y = self.hand_provider.get_position()
        current_radius = self.hand_provider.get_radius()
        current_time_factor = time.time() * 0.5
        draw_pupil_eye(screen, ball_x, ball_y, current_radius, current_time_factor)
        
        # HUD
        self._draw_hud(screen)
        
        # Draw Exit Button
        pygame.draw.rect(screen, (200, 50, 50), self.exit_btn_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.exit_btn_rect, 2, border_radius=5)
        exit_text = self.font.render("EXIT", True, (255, 255, 255))
        screen.blit(exit_text, (self.exit_btn_rect.centerx - exit_text.get_width() // 2, self.exit_btn_rect.centery - exit_text.get_height() // 2))
        
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            msg = self.large_font.render("Game Over!", True, (255, 255, 255))
            screen.blit(msg, (self.width // 2 - msg.get_width()//2, self.height // 2 - 100))
            
            score_msg = self.large_font.render(f"Final Score: {self.score}", True, (255, 255, 0))
            screen.blit(score_msg, (self.width // 2 - score_msg.get_width()//2, self.height // 2 - 40))
            
            exit_msg = self.font.render("Press SPACE to return to Menu", True, (200, 200, 200))
            screen.blit(exit_msg, (self.width // 2 - exit_msg.get_width()//2, self.height // 2 + 50))

    def _draw_hud(self, screen):
        ball_x, ball_y = self.hand_provider.get_position()
        current_radius = self.hand_provider.get_radius()
        difficulty_factor = current_radius / self.hand_provider.initial_radius
        collision_count = self.hand_provider.get_boundary_collisions()
        
        time_left = 0
        if self.game_active and self.game_start_time:
            time_left = max(0, self.game_duration - (time.time() - self.game_start_time))
            
        info_lines = [
            f'Time: {time_left:.1f}s' if self.game_active else 'Press SPACE to start',
            f'Score: {self.score}',
            f'Pupil Size: {current_radius:.1f}px (x{difficulty_factor:.1f})',
            f'Boundary Hits: {collision_count}',
            f'Hand: {"Detected" if self.hand_provider.get_finger_position() else "No Hand"}',
            f'Pos: ({ball_x:.0f}, {ball_y:.0f})',
        ]
        
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (200, 200, 200))
            screen.blit(text, (10, 10 + i * 25))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_btn_rect.collidepoint(event.pos):
                    from menu_scene import MenuScene
                    self.next_scene = MenuScene(self.manager)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        # Save detailed stats
                        self.manager.data["scores"]["game2"] = {
                            "score": self.score,
                            "collisions": self.hand_provider.get_boundary_collisions(),
                            "max_radius": self.hand_provider.max_radius,
                            "final_radius": self.hand_provider.get_radius()
                        }

                        # Mark as completed
                        if "completed_games" not in self.manager.data:
                            self.manager.data["completed_games"] = []
                        if "game2" not in self.manager.data["completed_games"]:
                            self.manager.data["completed_games"].append("game2")
                        
                        # Return to Menu
                        from menu_scene import MenuScene
                        self.next_scene = MenuScene(self.manager)
                    elif not self.game_active:
                        self.game_active = True
                        self.game_start_time = time.time()
                        self.score = 0
                        self.hand_provider.reset_position(self.width, self.height)
                elif event.key == pygame.K_r:
                    self.hand_provider.reset_position(self.width, self.height)
