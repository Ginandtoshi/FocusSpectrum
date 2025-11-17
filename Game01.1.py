"""
Test02.py - Artistic Concentration Game
An interactive experience that transforms your focus into personalized artwork.

Part 1: Magic Circle Calibration - Animated symmetrical patterns for focus
Part 2: Flower Aim Trainer - 20 blooming flowers overlay on magic circle
Part 3: Artistic Report - Your unique artwork combining all elements
"""

import turtle
import random
import math
import time
import cv2
import mediapipe as mp
from datetime import datetime
import os
from PIL import Image, ImageTk


class EyeTracker:
    """Eye tracking using Mediapipe Face Mesh"""
    
    def __init__(self):
        """Initialize MediaPipe face mesh"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
        self.tracking_active = False
        self.gaze_data = []
        self.facial_detected = False
        
    def start_tracking(self):
        """Start webcam and tracking"""
        print("Starting eye tracking...")
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Warning: Could not open webcam. Tracking disabled.")
                return False
            self.tracking_active = True
            print("✓ Eye tracking initialized successfully!")
            return True
        except Exception as e:
            print(f"Warning: Eye tracking unavailable ({e})")
            return False
    
    def get_gaze_position(self):
        """Get current gaze position"""
        if not self.tracking_active or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Store frame for display
        self.current_frame = frame.copy()
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        # Store results for visualization
        self.current_results = results
        
        if results.multi_face_landmarks:
            self.facial_detected = True
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get eye center landmarks (468 = left eye, 473 = right eye)
            left_eye = face_landmarks.landmark[468]
            right_eye = face_landmarks.landmark[473]
            
            # Average eye position
            avg_x = (left_eye.x + right_eye.x) / 2
            avg_y = (left_eye.y + right_eye.y) / 2
            
            # Convert to screen coordinates (-400 to 400, -300 to 300)
            screen_x = (avg_x - 0.5) * 1600
            screen_y = (0.5 - avg_y) * 1200
            
            return (screen_x, screen_y)
        
        return None
    
    def show_camera_preview(self):
        """Display small camera preview window with face and eye tracking visualization"""
        if not self.tracking_active or not self.cap:
            return
        
        try:
            # Get fresh frame
            ret, frame = self.cap.read()
            if not ret:
                return
            
            # Convert to RGB for processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            # Draw face and eye tracking if detected
            if results.multi_face_landmarks:
                self.facial_detected = True
                face_landmarks = results.multi_face_landmarks[0]
                h, w, _ = frame.shape
                
                # Draw eye tracking points
                # Left eye center (landmark 468)
                left_eye = face_landmarks.landmark[468]
                left_x, left_y = int(left_eye.x * w), int(left_eye.y * h)
                cv2.circle(frame, (left_x, left_y), 5, (0, 255, 0), -1)
                
                # Right eye center (landmark 473)
                right_eye = face_landmarks.landmark[473]
                right_x, right_y = int(right_eye.x * w), int(right_eye.y * h)
                cv2.circle(frame, (right_x, right_y), 5, (0, 255, 0), -1)
                
                # Draw face oval outline
                face_oval_points = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                                   397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                                   172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
                for i in range(len(face_oval_points) - 1):
                    pt1 = face_landmarks.landmark[face_oval_points[i]]
                    pt2 = face_landmarks.landmark[face_oval_points[i + 1]]
                    cv2.line(frame, (int(pt1.x * w), int(pt1.y * h)), 
                            (int(pt2.x * w), int(pt2.y * h)), (255, 0, 0), 1)
                
                # Add status text
                cv2.putText(frame, 'Tracking Active', (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, 'No Face Detected', (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Resize to small preview (200x150)
            small_frame = cv2.resize(frame, (200, 150))
            
            # Display in window
            cv2.imshow('Eye Tracking', small_frame)
            cv2.moveWindow('Eye Tracking', 1000, 50)  # Position at top right
            cv2.waitKey(1)
        except Exception as e:
            # Silently handle any camera errors to prevent crashes
            pass
    
    def log_gaze(self, target_pos, gaze_pos, timestamp):
        """Log gaze data for analysis"""
        if gaze_pos:
            distance = math.sqrt(
                (target_pos[0] - gaze_pos[0])**2 + 
                (target_pos[1] - gaze_pos[1])**2
            )
            self.gaze_data.append({
                'timestamp': timestamp,
                'target': target_pos,
                'gaze': gaze_pos,
                'distance': distance
            })
    
    def calculate_accuracy(self):
        """Calculate tracking accuracy"""
        if not self.gaze_data:
            return 0.0
        
        # Calculate average distance from targets
        avg_distance = sum(d['distance'] for d in self.gaze_data) / len(self.gaze_data)
        
        # Convert to accuracy percentage (closer = higher accuracy)
        # Assume 200px is baseline, 0px is perfect
        accuracy = max(0, min(100, (1 - avg_distance / 200) * 100))
        return accuracy
    
    def stop_tracking(self):
        """Stop tracking and release resources"""
        self.tracking_active = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


class MagicCircle:
    """Procedurally generated animated magic circle"""
    
    def __init__(self, player_id):
        """Initialize magic circle with unique seed"""
        self.player_id = player_id
        # Use timestamp for random patterns each time
        self.seed = int(time.time() * 1000) % (2**32)
        random.seed(self.seed)
        
        # Pattern parameters - more artistic variety
        self.num_spokes = random.choice([8, 12, 16, 20])  # Fewer spoke options
        self.num_rings = random.randint(4, 6)  # Fewer rings
        self.base_radius = random.randint(25, 35)  # Smaller base
        self.ring_spacing = random.randint(20, 30)  # Tighter spacing
        
        # Multiple symbol layers for complexity
        self.inner_symbol = random.choice(['circle', 'star', 'triangle', 'flower'])
        self.middle_symbol = random.choice(['square', 'diamond', 'hexagon', 'petal'])
        self.outer_symbol = random.choice(['triangle', 'star', 'wave', 'arc'])
        
        # Pattern style variations - more decorative elements
        self.has_dots = random.choice([True, True, False])  # Higher chance
        self.has_arcs = random.choice([True, True, False])  # Higher chance
        self.has_weaving = random.choice([True, True, False])  # Higher chance
        self.has_inner_mandala = True  # Always show complex center
        self.has_cross_rays = True  # Always show rays
        self.num_outer_rings = random.randint(4, 6)  # More outer rings
        
        # Color scheme
        self.primary_color = self._generate_color()
        self.secondary_color = self._generate_secondary_color(self.primary_color)
        
        self.pattern_points = []  # Store positions for flowers
        
        print(f"✨ Generated magic circle for {player_id}")
        print(f"   Spokes: {self.num_spokes} | Rings: {self.num_rings}")
        print(f"   Inner: {self.inner_symbol} | Middle: {self.middle_symbol} | Outer: {self.outer_symbol}")
    
    def _generate_color(self):
        """Generate a mystical color with more variety"""
        colors = [
            "#4A90E2", "#9B59B6", "#E67E22", "#1ABC9C", "#E91E63", "#3498DB",
            "#8E44AD", "#16A085", "#C0392B", "#2980B9", "#D35400", "#27AE60",
            "#2C3E50", "#F39C12", "#8E44AD", "#16A085"
        ]
        return random.choice(colors)
    
    def _generate_secondary_color(self, primary):
        """Generate complementary secondary color"""
        secondary_colors = {
            "#4A90E2": "#E29B4A",  # Blue → Orange
            "#9B59B6": "#59B68E",  # Purple → Teal
            "#E67E22": "#2291E6",  # Orange → Blue
            "#1ABC9C": "#BC1A49",  # Teal → Pink
            "#E91E63": "#1EE98C",  # Pink → Green
            "#3498DB": "#DB8434",  # Blue → Orange
            "#8E44AD": "#ADAD44",  # Purple → Yellow
            "#16A085": "#A01685",  # Teal → Magenta
            "#C0392B": "#2BC092",  # Red → Cyan
            "#2980B9": "#B99029",  # Blue → Gold
            "#D35400": "#00D38C",  # Orange → Teal
            "#27AE60": "#AE2773",  # Green → Pink
        }
        return secondary_colors.get(primary, "#95A5A6")
    
    def _draw_flower_symbol(self, t, x, y, size):
        """Draw flower-like symbol"""
        t.penup()
        t.goto(x, y)
        for angle in range(0, 360, 60):
            t.setheading(angle)
            t.pendown()
            t.circle(size, 120)
            t.penup()
            t.goto(x, y)
    
    def _draw_arc_decoration(self, t, x1, y1, x2, y2):
        """Draw decorative arc between two points"""
        t.penup()
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        t.goto(x1, y1)
        t.pendown()
        t.goto(mid_x, mid_y + 10)
        t.goto(x2, y2)
        t.penup()
    
    def _draw_wave_symbol(self, t, x, y, size):
        """Draw wave-like symbol"""
        t.penup()
        t.goto(x - size, y)
        t.pendown()
        for i in range(3):
            t.circle(size/2, 180)
            t.circle(-size/2, 180)
        t.penup()
    
    def _draw_hexagon(self, t, x, y, size):
        """Draw hexagon"""
        t.penup()
        t.goto(x, y)
        t.setheading(0)
        t.pendown()
        for _ in range(6):
            t.forward(size)
            t.left(60)
        t.penup()
    
    def draw_animated(self, t, screen, eye_tracker):
        """Draw beautiful artistic magic circle"""
        print("\n=== Part 1: Magic Circle Calibration ===")
        print("🎯 Watch the magical pattern unfold before your eyes...")
        
        screen.tracer(1)  # Smooth animation - update every frame
        t.speed(0)  # Maximum speed - fastest possible
        t.hideturtle()
        
        time.sleep(1)
        
        # Start eye tracking
        eye_tracker.start_tracking()
        start_time = time.time()
        
        angle_step = 360 / self.num_spokes
        
        print("✨ Creating your unique magic circle...")
        
        # Step 1: Draw ornate center
        t.color(self.primary_color)
        t.pensize(2)
        t.penup()
        t.goto(0, 0)
        
        # Center mandala with multiple layers
        radii = [4, 8, 13, 19, 26, 34]  # Non-uniform spacing for variety
        for radius in radii:
            t.goto(0, -radius)
            t.setheading(0)
            t.pendown()
            t.circle(radius)
            t.penup()
        
        # Add decorative dots in center - only 6 points
        for i in range(6):
            angle = i * 60
            x = 18 * math.cos(math.radians(angle))
            y = 18 * math.sin(math.radians(angle))
            t.goto(x, y)
            t.dot(5)
            t.penup()
        
        # Center star or flower
        if self.inner_symbol == 'star':
            for i in range(8):
                angle = i * 45
                t.goto(0, 0)
                t.setheading(angle)
                t.pendown()
                t.forward(30)
                t.penup()
        elif self.inner_symbol == 'flower':
            self._draw_flower_symbol(t, 0, 0, 12)
        
        screen.update()
        eye_tracker.show_camera_preview()
        
        # Step 2: Draw radial spokes with artistic elements
        t.color(self.primary_color)
        t.pensize(2)
        
        for ring_idx in range(self.num_rings):
            current_radius = self.base_radius + (ring_idx * self.ring_spacing)
            
            # Draw main ring
            t.penup()
            t.goto(0, -current_radius)
            t.setheading(0)
            t.pendown()
            t.circle(current_radius)
            t.penup()
            
            # Update camera preview periodically (every 2 rings)
            if ring_idx % 2 == 0:
                eye_tracker.show_camera_preview()
            
            # Draw spokes with decorative elements
            for i in range(self.num_spokes):
                angle = i * angle_step
                
                # Draw spoke from center
                t.goto(0, 0)
                t.setheading(angle)
                t.pendown()
                t.forward(current_radius)
                spoke_end_x = current_radius * math.cos(math.radians(angle))
                spoke_end_y = current_radius * math.sin(math.radians(angle))
                t.penup()
                
                # Choose symbol based on ring layer
                symbol_x = spoke_end_x
                symbol_y = spoke_end_y
                
                t.color(self.primary_color)  # USE SAME COLOR THROUGHOUT
                
                if ring_idx == 0:  # Inner ring
                    if self.inner_symbol == 'circle':
                        t.goto(symbol_x, symbol_y)
                        t.dot(10)
                    elif self.inner_symbol == 'triangle':
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle)
                        t.pendown()
                        for _ in range(3):
                            t.forward(12)
                            t.left(120)
                        t.penup()
                    elif self.inner_symbol == 'star':
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle)
                        t.pendown()
                        for _ in range(5):
                            t.forward(10)
                            t.right(144)
                        t.penup()
                
                elif ring_idx == 1 or ring_idx == 2:  # Middle rings
                    if self.middle_symbol == 'square':
                        t.goto(symbol_x - 6, symbol_y - 6)
                        t.setheading(0)
                        t.pendown()
                        for _ in range(4):
                            t.forward(12)
                            t.left(90)
                        t.penup()
                    elif self.middle_symbol == 'diamond':
                        t.goto(symbol_x, symbol_y - 8)
                        t.setheading(45)
                        t.pendown()
                        for _ in range(4):
                            t.forward(10)
                            t.left(90)
                        t.penup()
                    elif self.middle_symbol == 'hexagon':
                        self._draw_hexagon(t, symbol_x, symbol_y, 6)
                    elif self.middle_symbol == 'petal':
                        self._draw_flower_symbol(t, symbol_x, symbol_y, 6)
                
                else:  # Outer rings
                    if self.outer_symbol == 'triangle':
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle + 90)
                        t.pendown()
                        for _ in range(3):
                            t.forward(14)
                            t.left(120)
                        t.penup()
                    elif self.outer_symbol == 'star':
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle)
                        t.pendown()
                        for _ in range(5):
                            t.forward(12)
                            t.right(144)
                        t.penup()
                    elif self.outer_symbol == 'wave':
                        self._draw_wave_symbol(t, symbol_x, symbol_y, 5)
                    elif self.outer_symbol == 'arc':
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle + 45)
                        t.pendown()
                        t.circle(10, 90)
                        t.penup()
                
                # Add decorative dots
                if self.has_dots:
                    t.color(self.primary_color)  # USE SAME COLOR
                    mid_x = (current_radius * 0.7) * math.cos(math.radians(angle))
                    mid_y = (current_radius * 0.7) * math.sin(math.radians(angle))
                    t.goto(mid_x, mid_y)
                    t.dot(5)
                
                # Store point for flowers
                self.pattern_points.append((spoke_end_x, spoke_end_y))
                
                # Track gaze
                gaze_pos = eye_tracker.get_gaze_position()
                if gaze_pos:
                    eye_tracker.log_gaze((spoke_end_x, spoke_end_y), gaze_pos, time.time() - start_time)
        
        screen.update()
        
        # Step 3: Add weaving pattern between spokes
        if self.has_weaving:
            t.color(self.primary_color)  # USE SAME COLOR
            t.pensize(1)
            middle_radius = self.base_radius + (self.num_rings // 2) * self.ring_spacing
            
            for i in range(self.num_spokes):
                angle1 = i * angle_step
                angle2 = ((i + 1) % self.num_spokes) * angle_step
                
                x1 = middle_radius * math.cos(math.radians(angle1))
                y1 = middle_radius * math.sin(math.radians(angle1))
                x2 = middle_radius * math.cos(math.radians(angle2))
                y2 = middle_radius * math.sin(math.radians(angle2))
                
                if self.has_arcs:
                    self._draw_arc_decoration(t, x1, y1, x2, y2)
                else:
                    t.penup()
                    t.goto(x1, y1)
                    t.pendown()
                    t.goto(x2, y2)
                    t.penup()
        
        screen.update()
        eye_tracker.show_camera_preview()
        
        # Step 4: Add outer decorative rings
        t.color(self.primary_color)
        t.pensize(2)
        outer_base = self.base_radius + (self.num_rings * self.ring_spacing) + 15
        
        for i in range(2):  # Reduced to 2 rings
            radius = outer_base + (i * 25)
            t.penup()
            t.goto(0, -radius)
            t.setheading(0)
            t.pendown()
            t.circle(radius)
            t.penup()
            
            # Add dots only on outermost ring
            if i == 1:
                for j in range(self.num_spokes):
                    angle = j * (360 / self.num_spokes)
                    x = radius * math.cos(math.radians(angle))
                    y = radius * math.sin(math.radians(angle))
                    t.goto(x, y)
                    t.dot(5)
        
        screen.update()
        eye_tracker.show_camera_preview()
        
        # Step 5: Add mystical cross rays
        t.color(self.primary_color)  # USE SAME COLOR
        t.pensize(1)
        max_radius = outer_base + 70
        
        for i in range(self.num_spokes * 2):  # Back to 2x, less repetitive
            angle = i * (360 / (self.num_spokes * 2))
            t.penup()
            t.goto(0, 0)
            t.setheading(angle)
            t.pendown()
            # Alternate long and short rays
            ray_length = max_radius if i % 2 == 0 else max_radius * 0.75
            t.forward(ray_length)
            t.penup()
            
            # Add triangles only on main cardinal directions (every 4th ray)
            if i % 4 == 0:
                t.goto(ray_length * 0.88 * math.cos(math.radians(angle)),
                       ray_length * 0.88 * math.sin(math.radians(angle)))
                t.setheading(angle)
                t.pendown()
                for _ in range(3):
                    t.forward(6)
                    t.left(120)
                t.penup()
        
        screen.update()
        eye_tracker.show_camera_preview()
        time.sleep(0.5)  # Brief pause to show final preview
        
        print("✓ Magic circle complete - A unique masterpiece!")
        print(f"✓ Eye tracking {'successful' if eye_tracker.facial_detected else 'unavailable'}")
        time.sleep(1)


class Flower:
    """Flower that blooms when targeted"""
    
    def __init__(self, x, y, core_size=8):
        """Initialize flower at position"""
        self.x = x
        self.y = y
        self.core_size = core_size
        self.bloomed = False
        self.petal_colors = [
            "#FF69B4", "#FFB6C1", "#FF1493", "#DB7093",
            "#FFC0CB", "#FF85C0", "#FF6EB4", "#FF4FA3"
        ]
    
    def draw_core(self, t):
        """Draw flower core (target)"""
        t.penup()
        t.goto(self.x, self.y)
        t.color("#FFD700")  # Gold core
        t.dot(self.core_size * 2)
        
        # Pulsing effect
        t.color("#FFFFFF")
        t.dot(self.core_size)
    
    def bloom(self, t, screen):
        """Animate flower blooming"""
        screen.tracer(0)
        
        # Draw petals
        for petal_angle in range(0, 360, 45):
            t.penup()
            t.goto(self.x, self.y)
            t.setheading(petal_angle)
            t.color(self.petal_colors[petal_angle // 45])
            t.pendown()
            
            # Petal shape
            for size in range(5, 15, 2):
                t.circle(size, 180)
                t.goto(self.x, self.y)
                t.setheading(petal_angle)
                screen.update()
                time.sleep(0.02)
        
        # Draw glowing center
        t.penup()
        t.goto(self.x, self.y)
        for size in [15, 12, 9, 6]:
            t.color("#FFD700" if size % 2 == 0 else "#FFEC8B")
            t.dot(size)
            screen.update()
            time.sleep(0.03)
        
        self.bloomed = True
        screen.update()
    
    def contains_point(self, x, y):
        """Check if point is within flower core"""
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance <= self.core_size * 2


class FlowerAimTrainer:
    """Aim trainer with 12 blooming flowers"""
    
    def __init__(self, magic_circle_points, eye_tracker):
        """Initialize with positions from magic circle"""
        self.magic_circle_points = magic_circle_points
        self.eye_tracker = eye_tracker
        self.flowers = []
        self.current_flower_index = 0
        self.reaction_times = []
        self.hits = 0
        self.misses = 0
        self.game_complete = False
        
        # Generate 12 flower positions using magic circle points
        self._generate_flower_positions()
    
    def _generate_flower_positions(self):
        """Generate 12 flower positions on the magic circle"""
        # Use all available points and add some random variations
        available_points = self.magic_circle_points.copy()
        random.shuffle(available_points)
        
        for i in range(12):
            if i < len(available_points):
                # Use exact magic circle point
                x, y = available_points[i]
            else:
                # Generate additional points if needed
                angle = random.uniform(0, 360)
                radius = random.uniform(50, 200)
                x = radius * math.cos(math.radians(angle))
                y = radius * math.sin(math.radians(angle))
            
            self.flowers.append(Flower(x, y))
    
    def play(self, t, screen):
        """Run the flower aim trainer"""
        print("\n=== Part 2: Flower Aim Trainer ===")
        print("🌸 Click on flower cores to make them bloom!")
        print(f"   Target: 12 flowers")
        print("   ⏱️  Each flower lasts 1.5 seconds!\n")
        
        # Close camera preview window but keep tracking active
        try:
            cv2.destroyWindow('Eye Tracking')
        except:
            pass  # Window might not exist
        
        screen.tracer(1)
        
        def on_click(x, y):
            """Handle click events"""
            if self.game_complete:
                return
            
            current_flower = self.flowers[self.current_flower_index]
            
            if current_flower.contains_point(x, y):
                # Hit!
                reaction_time = time.time() - self.spawn_time
                self.reaction_times.append(reaction_time)
                self.hits += 1
                
                print(f"✓ Flower {self.current_flower_index + 1}/12 bloomed! ({reaction_time:.3f}s)")
                
                # Bloom animation
                current_flower.bloom(t, screen)
                
                # Spawn next flower
                self.current_flower_index += 1
                if self.current_flower_index < 12:
                    self._spawn_next_flower(t, screen)
                else:
                    self.game_complete = True
                    print("\n🎉 All 12 flowers bloomed! Game complete!")
            else:
                # Miss
                self.misses += 1
                print(f"✗ Miss! Try again...")
        
        # Bind click event
        screen.onclick(on_click)
        
        # Spawn first flower
        self._spawn_next_flower(t, screen)
        
        # Wait for completion with timeout check
        while not self.game_complete:
            screen.update()
            
            # Check if 1.5 seconds have passed without clicking
            if self.current_flower_index < len(self.flowers) and time.time() - self.spawn_time > 1.5:
                # Timeout - erase flower and spawn next
                current_flower = self.flowers[self.current_flower_index]
                self.misses += 1
                print(f"⏱️  Timeout! Flower {self.current_flower_index + 1}/12 disappeared")
                
                # Erase the flower core
                t.penup()
                t.goto(current_flower.x, current_flower.y)
                t.color("#FFFFFF")  # White to erase
                t.dot(current_flower.core_size * 3)
                screen.update()
                
                # Move to next flower
                self.current_flower_index += 1
                if self.current_flower_index < 12:
                    self._spawn_next_flower(t, screen)
                else:
                    self.game_complete = True
                    print("\n🎮 Game complete!")
            
            time.sleep(0.1)
        
        # Stop tracking after Part 2 completes
        self.eye_tracker.stop_tracking()
        
        screen.onclick(None)  # Unbind
    
    def _spawn_next_flower(self, t, screen):
        """Spawn the next flower core"""
        self.spawn_time = time.time()
        flower = self.flowers[self.current_flower_index]
        flower.draw_core(t)
        screen.update()


class ArtisticReport:
    """Generate personalized artistic report"""
    
    def __init__(self, player_id, magic_circle, flowers, reaction_times, eye_tracker):
        """Initialize report"""
        self.player_id = player_id
        self.magic_circle = magic_circle
        self.flowers = flowers
        self.reaction_times = reaction_times
        self.eye_tracker = eye_tracker
        self.tracking_accuracy = eye_tracker.calculate_accuracy()
    
    def generate(self, t, screen):
        """Generate the artistic report"""
        print("\n=== Part 3: Your Personalized Artwork ===")
        
        screen.clear()
        t.clear()
        screen.bgcolor("#F5F5F5")
        t.hideturtle()
        
        # Title
        t.penup()
        t.goto(0, 320)
        t.color("#2C3E50")
        t.write("YOUR CONCENTRATION ARTWORK", align="center", 
                font=("Arial", 22, "bold"))
        
        t.goto(0, 285)
        t.color("#34495E")
        t.write(f"Created by: {self.player_id}", align="center", 
                font=("Arial", 14, "normal"))
        
        t.goto(0, 260)
        t.write(f"{datetime.now().strftime('%B %d, %Y at %H:%M')}", 
                align="center", font=("Arial", 11, "italic"))
        
        # Summary stats at top
        bloomed_count = sum(1 for f in self.flowers if f.bloomed)
        t.goto(0, 230)
        t.color("#27AE60" if bloomed_count == 12 else "#F39C12")
        t.write(f"✨ {bloomed_count}/12 Flowers Bloomed | Accuracy: {self.tracking_accuracy:.0f}% ✨", 
                align="center", font=("Arial", 12, "bold"))
        
        # Redraw the complete artwork on right side
        offset_x = 280
        offset_y = -30
        scale = 0.65
        
        t.goto(offset_x - 50, 210)
        t.color("#7F8C8D")
        t.write("Your Unique Pattern", align="center", font=("Arial", 11, "bold"))
        
        # Redraw magic circle
        self._redraw_magic_circle(t, screen, offset_x, offset_y, scale)
        
        # Redraw all bloomed flowers
        self._redraw_flowers(t, screen, offset_x, offset_y, scale)
        
        # Statistics on left side
        self._draw_statistics(t, screen)
        
        # Save as image
        self._save_artwork(screen)
        
        screen.update()
        print("✓ Artwork generated successfully!")
    
    def _redraw_magic_circle(self, t, screen, offset_x, offset_y, scale):
        """Instantly display the magic circle matching Part 1 exactly"""
        screen.tracer(0)  # Disable animation for instant display
        t.pensize(1)
        
        angle_step = 360 / self.magic_circle.num_spokes
        
        # Step 1: Center mandala with multiple layers
        t.color(self.magic_circle.primary_color)
        radii = [6, 14, 24, 36]  # Reduced to 4 circles
        for radius in radii:
            t.penup()
            t.goto(offset_x, offset_y - (radius * scale))
            t.setheading(0)
            t.pendown()
            t.circle(radius * scale)
        
        # Add decorative dots in center - only 6 points
        for i in range(6):
            angle = i * 60
            x = offset_x + (18 * scale) * math.cos(math.radians(angle))
            y = offset_y + (18 * scale) * math.sin(math.radians(angle))
            t.penup()
            t.goto(x, y)
            t.dot(int(5 * scale))
        
        # Center star or flower
        if self.magic_circle.inner_symbol == 'star':
            for i in range(8):
                angle = i * 45
                t.penup()
                t.goto(offset_x, offset_y)
                t.setheading(angle)
                t.pendown()
                t.forward(30 * scale)
        elif self.magic_circle.inner_symbol == 'flower':
            t.penup()
            for angle in range(0, 360, 60):
                t.goto(offset_x, offset_y)
                t.setheading(angle)
                t.pendown()
                t.circle(12 * scale, 120)
                t.penup()
        
        # Step 2: Draw radial spokes with decorative elements
        for ring_idx in range(self.magic_circle.num_rings):
            current_radius = (self.magic_circle.base_radius + 
                            (ring_idx * self.magic_circle.ring_spacing)) * scale
            
            # Main ring
            t.color(self.magic_circle.primary_color)
            t.penup()
            t.goto(offset_x, offset_y - current_radius)
            t.setheading(0)
            t.pendown()
            t.circle(current_radius)
            t.penup()
            
            # Spokes with symbols
            for i in range(self.magic_circle.num_spokes):
                angle = i * angle_step
                
                spoke_end_x = offset_x + current_radius * math.cos(math.radians(angle))
                spoke_end_y = offset_y + current_radius * math.sin(math.radians(angle))
                
                # Draw spoke - USE PRIMARY COLOR ONLY
                t.color(self.magic_circle.primary_color)
                t.penup()
                t.goto(offset_x, offset_y)
                t.setheading(angle)
                t.pendown()
                t.goto(spoke_end_x, spoke_end_y)
                t.penup()
                
                # Draw decorative elements at spoke ends - USE PRIMARY COLOR ONLY
                symbol_x = spoke_end_x
                symbol_y = spoke_end_y
                
                t.color(self.magic_circle.primary_color)
                
                if ring_idx == 0:  # Inner ring - same symbols as Part 1
                    if self.magic_circle.inner_symbol == 'circle':
                        t.goto(symbol_x, symbol_y)
                        t.dot(int(10 * scale))
                    elif self.magic_circle.inner_symbol == 'triangle':
                        t.penup()
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle)
                        t.pendown()
                        for _ in range(3):
                            t.forward(12 * scale)
                            t.left(120)
                        t.penup()
                    elif self.magic_circle.inner_symbol == 'star':
                        t.penup()
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle)
                        t.pendown()
                        for _ in range(5):
                            t.forward(10 * scale)
                            t.right(144)
                        t.penup()
                    elif self.magic_circle.inner_symbol == 'flower':
                        t.penup()
                        for petal_angle in range(0, 360, 60):
                            t.goto(symbol_x, symbol_y)
                            t.setheading(petal_angle)
                            t.pendown()
                            t.circle(6 * scale, 120)
                            t.penup()
                
                elif ring_idx in [1, 2]:  # Middle rings - same symbols as Part 1
                    if self.magic_circle.middle_symbol == 'square':
                        t.penup()
                        t.goto(symbol_x - (6 * scale), symbol_y - (6 * scale))
                        t.setheading(0)
                        t.pendown()
                        for _ in range(4):
                            t.forward(12 * scale)
                            t.left(90)
                        t.penup()
                    elif self.magic_circle.middle_symbol == 'diamond':
                        t.penup()
                        t.goto(symbol_x, symbol_y - (8 * scale))
                        t.setheading(45)
                        t.pendown()
                        for _ in range(4):
                            t.forward(10 * scale)
                            t.left(90)
                        t.penup()
                    elif self.magic_circle.middle_symbol == 'hexagon':
                        t.penup()
                        t.goto(symbol_x, symbol_y)
                        t.setheading(0)
                        t.pendown()
                        for _ in range(6):
                            t.forward(6 * scale)
                            t.left(60)
                        t.penup()
                    elif self.magic_circle.middle_symbol == 'petal':
                        t.penup()
                        for petal_angle in range(0, 360, 60):
                            t.goto(symbol_x, symbol_y)
                            t.setheading(petal_angle)
                            t.pendown()
                            t.circle(6 * scale, 120)
                            t.penup()
                
                else:  # Outer rings - same symbols as Part 1
                    if self.magic_circle.outer_symbol == 'triangle':
                        t.penup()
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle + 90)
                        t.pendown()
                        for _ in range(3):
                            t.forward(14 * scale)
                            t.left(120)
                        t.penup()
                    elif self.magic_circle.outer_symbol == 'star':
                        t.penup()
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle)
                        t.pendown()
                        for _ in range(5):
                            t.forward(12 * scale)
                            t.right(144)
                        t.penup()
                    elif self.magic_circle.outer_symbol == 'wave':
                        # Wave symbol
                        t.penup()
                        t.goto(symbol_x - (5 * scale), symbol_y)
                        t.pendown()
                        for i in range(3):
                            t.circle((5 * scale)/2, 180)
                            t.circle(-(5 * scale)/2, 180)
                        t.penup()
                    elif self.magic_circle.outer_symbol == 'arc':
                        t.penup()
                        t.goto(symbol_x, symbol_y)
                        t.setheading(angle + 45)
                        t.pendown()
                        t.circle(10 * scale, 90)
                        t.penup()
                
                # Add decorative dots if enabled - USE PRIMARY COLOR ONLY
                if self.magic_circle.has_dots:
                    t.color(self.magic_circle.primary_color)
                    mid_x = offset_x + (current_radius * 0.7) * math.cos(math.radians(angle))
                    mid_y = offset_y + (current_radius * 0.7) * math.sin(math.radians(angle))
                    t.goto(mid_x, mid_y)
                    t.dot(int(5 * scale))
        
        # Step 3: Weaving pattern between spokes - USE PRIMARY COLOR ONLY
        if self.magic_circle.has_weaving:
            t.color(self.magic_circle.primary_color)
            middle_radius = (self.magic_circle.base_radius + 
                           (self.magic_circle.num_rings // 2) * self.magic_circle.ring_spacing) * scale
            
            for i in range(self.magic_circle.num_spokes):
                angle1 = i * angle_step
                angle2 = ((i + 1) % self.magic_circle.num_spokes) * angle_step
                
                x1 = offset_x + middle_radius * math.cos(math.radians(angle1))
                y1 = offset_y + middle_radius * math.sin(math.radians(angle1))
                x2 = offset_x + middle_radius * math.cos(math.radians(angle2))
                y2 = offset_y + middle_radius * math.sin(math.radians(angle2))
                
                t.penup()
                t.goto(x1, y1)
                t.pendown()
                if self.magic_circle.has_arcs:
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    t.goto(mid_x, mid_y + (10 * scale))
                t.goto(x2, y2)
                t.penup()
        
        # Step 4: Outer decorative rings
        t.color(self.magic_circle.primary_color)
        outer_base = (self.magic_circle.base_radius + 
                     (self.magic_circle.num_rings * self.magic_circle.ring_spacing) + 15) * scale
        
        for i in range(2):  # Reduced to 2 rings
            radius = outer_base + (i * 25 * scale)
            t.penup()
            t.goto(offset_x, offset_y - radius)
            t.setheading(0)
            t.pendown()
            t.circle(radius)
            t.penup()
            
            # Add dots only on outermost ring
            if i == 1:
                for j in range(self.magic_circle.num_spokes):
                    angle = j * (360 / self.magic_circle.num_spokes)
                    x = offset_x + radius * math.cos(math.radians(angle))
                    y = offset_y + radius * math.sin(math.radians(angle))
                    t.goto(x, y)
                    t.dot(int(5 * scale))
        
        # Step 5: Cross rays - USE PRIMARY COLOR ONLY
        t.color(self.magic_circle.primary_color)
        max_radius = outer_base + (70 * scale)
        
        for i in range(self.magic_circle.num_spokes * 2):  # Back to 2x
            angle = i * (360 / (self.magic_circle.num_spokes * 2))
            t.penup()
            t.goto(offset_x, offset_y)
            t.setheading(angle)
            t.pendown()
            # Alternate long and short rays
            ray_length = max_radius if i % 2 == 0 else max_radius * 0.75
            t.forward(ray_length)
            t.penup()
            
            # Add triangles only on main cardinal directions (every 4th ray)
            if i % 4 == 0:
                tri_x = offset_x + ray_length * 0.88 * math.cos(math.radians(angle))
                tri_y = offset_y + ray_length * 0.88 * math.sin(math.radians(angle))
                t.goto(tri_x, tri_y)
                t.setheading(angle)
                t.pendown()
                for _ in range(3):
                    t.forward(6 * scale)
                    t.left(120)
                t.penup()
    
    def _redraw_flowers(self, t, screen, offset_x, offset_y, scale):
        """Instantly display all bloomed flowers"""
        screen.tracer(0)  # Instant display
        
        for flower in self.flowers:
            if flower.bloomed:
                flower_x = offset_x + (flower.x * scale)
                flower_y = offset_y + (flower.y * scale)
                
                # Draw petals - bigger and more visible
                for petal_angle in range(0, 360, 45):
                    t.penup()
                    t.goto(flower_x, flower_y)
                    t.setheading(petal_angle)
                    t.color(flower.petal_colors[petal_angle // 45])
                    t.pendown()
                    t.pensize(2)  # Thicker petals
                    t.circle(12 * scale, 180)  # Bigger petals
                    t.penup()
                
                # Draw center - bigger and more visible
                t.goto(flower_x, flower_y)
                t.color("#FFD700")
                t.dot(int(12 * scale))  # Bigger center
        
        screen.tracer(1)
        screen.update()
    
    def _draw_statistics(self, t, screen):
        """Draw performance statistics"""
        t.penup()
        
        # Header
        t.goto(-350, 200)
        t.color("#2C3E50")
        t.write("Performance Metrics", align="left", font=("Arial", 15, "bold"))
        
        t.goto(-350, 175)
        t.color("#95A5A6")
        t.write("━" * 35, align="left", font=("Arial", 10, "normal"))
        
        # Part 1: Eye Tracking
        t.goto(-350, 145)
        t.color("#3498DB")
        t.write("✦ PART 1: CALIBRATION", align="left", font=("Arial", 12, "bold"))
        
        t.goto(-350, 120)
        t.color("#2C3E50")
        t.write(f"Eye Tracking Accuracy:", align="left", font=("Arial", 10, "normal"))
        
        t.goto(-350, 100)
        if self.tracking_accuracy >= 70:
            t.color("#27AE60")
        elif self.tracking_accuracy >= 50:
            t.color("#F39C12")
        else:
            t.color("#E74C3C")
        t.write(f"{self.tracking_accuracy:.1f}%", align="left", font=("Arial", 14, "bold"))
        
        t.goto(-350, 75)
        t.color("#2C3E50")
        t.write(f"Pattern: {self.magic_circle.num_spokes} spokes, {self.magic_circle.num_rings} rings", 
                align="left", font=("Arial", 9, "normal"))
        
        # Part 2: Aim Trainer
        t.goto(-350, 40)
        t.color("#E91E63")
        t.write("✦ PART 2: FLOWER BLOOMS", align="left", font=("Arial", 12, "bold"))
        
        bloomed_count = sum(1 for f in self.flowers if f.bloomed)
        accuracy = (bloomed_count / 12) * 100
        
        t.goto(-350, 15)
        t.color("#2C3E50")
        t.write(f"Flowers Bloomed:", align="left", font=("Arial", 10, "normal"))
        
        t.goto(-350, -5)
        if bloomed_count == 12:
            t.color("#27AE60")
        elif bloomed_count >= 9:
            t.color("#F39C12")
        else:
            t.color("#E74C3C")
        t.write(f"{bloomed_count}/12 ({accuracy:.0f}%)", align="left", font=("Arial", 14, "bold"))
        
        if self.reaction_times:
            avg_reaction = sum(self.reaction_times) / len(self.reaction_times)
            best_reaction = min(self.reaction_times)
            
            t.goto(-350, -30)
            t.color("#2C3E50")
            t.write(f"Avg Reaction Time:", align="left", font=("Arial", 10, "normal"))
            
            t.goto(-350, -50)
            if avg_reaction < 0.5:
                t.color("#27AE60")
            elif avg_reaction < 0.8:
                t.color("#F39C12")
            else:
                t.color("#E74C3C")
            t.write(f"{avg_reaction:.3f}s", align="left", font=("Arial", 12, "bold"))
            
            t.goto(-350, -75)
            t.color("#2C3E50")
            t.write(f"Best Time: {best_reaction:.3f}s", align="left", font=("Arial", 9, "normal"))
        
        # Overall Rating
        t.goto(-350, -110)
        t.color("#95A5A6")
        t.write("━" * 35, align="left", font=("Arial", 10, "normal"))
        
        t.goto(-350, -135)
        t.color("#2C3E50")
        t.write("Artistic Rating:", align="left", font=("Arial", 11, "normal"))
        
        t.goto(-350, -160)
        rating = self._calculate_rating()
        if rating in ["Masterpiece!", "Excellent"]:
            t.color("#27AE60")
        elif rating in ["Very Good", "Good"]:
            t.color("#F39C12")
        else:
            t.color("#E74C3C")
        t.write(f"★ {rating} ★", align="left", font=("Arial", 14, "bold"))
    
    def _calculate_rating(self):
        """Calculate artistic rating"""
        bloomed = sum(1 for f in self.flowers if f.bloomed)
        
        if bloomed == 12 and self.tracking_accuracy >= 70:
            return "Masterpiece!"
        elif bloomed >= 10 and self.tracking_accuracy >= 60:
            return "Excellent"
        elif bloomed >= 8 and self.tracking_accuracy >= 50:
            return "Very Good"
        elif bloomed >= 6:
            return "Good"
        else:
            return "Keep Practicing"
    
    def _save_artwork(self, screen):
        """Save artwork as image"""
        try:
            # Create directory
            os.makedirs("artworks", exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"artworks/artwork_{self.player_id}_{timestamp}"
            
            # Save as EPS
            eps_file = f"{filename}.eps"
            screen.getcanvas().postscript(file=eps_file)
            
            # Convert to PNG
            png_file = f"{filename}.png"
            img = Image.open(eps_file)
            img.save(png_file, "PNG")
            
            print(f"✓ Artwork saved: {png_file}")
            
        except Exception as e:
            print(f"✗ Could not save artwork: {e}")


class ConcentrationArtGame:
    """Main game controller"""
    
    def __init__(self, player_id="Artist"):
        """Initialize game"""
        self.player_id = player_id
        self.screen = None
        self.turtle = None
        self.eye_tracker = EyeTracker()
        self.magic_circle = None
        self.aim_trainer = None
        self.report = None
    
    def setup(self):
        """Setup turtle graphics"""
        self.screen = turtle.Screen()
        self.screen.setup(width=900, height=700)
        self.screen.bgcolor("white")
        self.screen.title("Concentration Art Game")
        
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
    
    def run(self):
        """Run the complete game"""
        print("=" * 60)
        print("🎨 CONCENTRATION ART GAME 🎨")
        print("=" * 60)
        print("Transform your focus into personalized artwork!")
        print()
        
        self.setup()
        
        # Part 1: Magic Circle Calibration
        self.magic_circle = MagicCircle(self.player_id)
        self.magic_circle.draw_animated(self.turtle, self.screen, self.eye_tracker)
        
        # Part 2: Flower Aim Trainer
        self.aim_trainer = FlowerAimTrainer(self.magic_circle.pattern_points, self.eye_tracker)
        self.aim_trainer.play(self.turtle, self.screen)
        
        # Part 3: Artistic Report
        self.report = ArtisticReport(
            self.player_id,
            self.magic_circle,
            self.aim_trainer.flowers,
            self.aim_trainer.reaction_times,
            self.eye_tracker
        )
        self.report.generate(self.turtle, self.screen)
        
        print("\n" + "=" * 60)
        print("Thank you for creating art with us! 🎨✨")
        print("=" * 60)
        
        # Keep window open
        self.screen.mainloop()


def main():
    """Main entry point"""
    # Use default player name
    player_name = "Artist"
    
    # Run game
    game = ConcentrationArtGame(player_name)
    game.run()


if __name__ == "__main__":
    main()
