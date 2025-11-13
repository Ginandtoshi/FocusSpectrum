#!/usr/bin/env python3

"""
Concentration Test Game with Eye Tracking
Part 1: Eye/Face Tracking Calibration with Magic Pattern
Part 2: Aim Trainer - Flower Version
Part 3: Personalized Report
"""

import turtle
import random
import time
import math
from datetime import datetime
import cv2
import mediapipe as mp
import os
from PIL import Image, ImageTk
import tkinter as tk


class EyeTracker:
    """Face and eye tracking using Mediapipe"""
    
    def __init__(self):
        """Initialize Mediapipe face mesh and webcam"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Warning: Cannot open webcam. Eye tracking disabled.")
            self.enabled = False
        else:
            self.enabled = True
            print("Eye tracker initialized successfully")
        
        self.gaze_data = []
        self.tracking_active = False
        self.screen_width = 900
        self.screen_height = 700
    
    def start_tracking(self):
        """Start eye tracking"""
        self.tracking_active = True
        self.gaze_data = []
        print("Eye tracking started")
    
    def stop_tracking(self):
        """Stop eye tracking"""
        self.tracking_active = False
        print("Eye tracking stopped")
    
    def get_gaze_position(self):
        """
        Get current gaze position using Mediapipe
        Returns (x, y) in screen coordinates
        """
        if not self.enabled or not self.tracking_active:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get eye landmarks (average of both eyes)
            # Left eye center: landmark 468
            # Right eye center: landmark 473
            left_eye = face_landmarks.landmark[468]
            right_eye = face_landmarks.landmark[473]
            
            # Average eye position
            avg_x = (left_eye.x + right_eye.x) / 2
            avg_y = (left_eye.y + right_eye.y) / 2
            
            # Convert to screen coordinates
            screen_x = (avg_x - 0.5) * self.screen_width
            screen_y = -(avg_y - 0.5) * self.screen_height
            
            return (screen_x, screen_y)
        
        return None
    
    def log_gaze(self, turtle_pos, gaze_pos, timestamp):
        """Log gaze data for analysis"""
        if gaze_pos is None:
            return
        
        distance = math.sqrt((turtle_pos[0] - gaze_pos[0])**2 + 
                           (turtle_pos[1] - gaze_pos[1])**2)
        
        self.gaze_data.append({
            'timestamp': timestamp,
            'turtle_pos': turtle_pos,
            'gaze_pos': gaze_pos,
            'distance': distance
        })
    
    def analyze_tracking_accuracy(self, threshold=100):
        """
        Analyze tracking accuracy
        Returns percentage of time gaze was within threshold distance
        """
        if not self.gaze_data:
            return 0
        
        accurate_samples = sum(1 for data in self.gaze_data 
                              if data['distance'] <= threshold)
        accuracy = (accurate_samples / len(self.gaze_data)) * 100
        
        return accuracy
    
    def cleanup(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


class MagicPattern:
    """Procedurally generated magic pattern"""
    
    def __init__(self, player_id):
        """Initialize pattern with unique seed"""
        self.player_id = player_id
        # Use current timestamp to make pattern different every run
        import time as t_module
        self.seed = int(t_module.time() * 1000) % (2**32)
        random.seed(self.seed)
        
        # Pattern parameters - Doctor Strange style
        self.num_spokes = random.choice([8, 12, 16, 24])  # Symmetrical divisions
        self.num_rings = random.randint(3, 5)
        self.base_radius = random.randint(60, 90)
        self.ring_spacing = random.randint(50, 70)
        self.has_runes = random.choice([True, False])
        self.rune_type = random.choice(['circle', 'triangle', 'square', 'hexagon', 'star'])
        self.color = self._generate_color()
        self.pattern_points = []  # Store for report
        
        print(f"Generated unique Doctor Strange pattern for {player_id}")
        print(f"Seed: {self.seed}, Spokes: {self.num_spokes}, Rings: {self.num_rings}, Runes: {self.rune_type if self.has_runes else 'None'}")
    
    def _generate_color(self):
        """Generate a single calming color"""
        colors = ["#4A90E2", "#50C878", "#9B59B6", "#E67E22", "#1ABC9C"]
        return random.choice(colors)
    
    def _draw_rune(self, t, x, y, size, rune_type):
        """Draw mystical runes at specific positions"""
        t.goto(x, y)
        
        if rune_type == 'circle':
            t.circle(size)
            t.goto(x, y)
        elif rune_type == 'triangle':
            for _ in range(3):
                t.forward(size * 2)
                t.left(120)
        elif rune_type == 'square':
            for _ in range(4):
                t.forward(size * 1.5)
                t.left(90)
        elif rune_type == 'hexagon':
            for _ in range(6):
                t.forward(size * 1.2)
                t.left(60)
        elif rune_type == 'star':
            for _ in range(5):
                t.forward(size * 2)
                t.right(144)
    
    def draw(self, t, screen, eye_tracker):
        """Draw Doctor Strange style magic spell ring"""
        print("\n=== Part 1: Eye Tracking Calibration ===")
        print("Focus on the center and follow the pattern with your eyes")
        
        screen.tracer(0)  # Disable animation for faster drawing
        t.speed(0)  # Fastest speed
        t.hideturtle()
        
        time.sleep(1)
        
        # Start tracking
        eye_tracker.start_tracking()
        start_time = time.time()
        
        # Set single color for ENTIRE pattern
        t.color(self.color)
        t.pensize(2)
        
        angle_step = 360 / self.num_spokes
        
        # ONE PERFECTLY SYMMETRICAL DOCTOR STRANGE SPELL RING
        # Start at center
        t.penup()
        t.goto(0, 0)
        t.setheading(0)  # Always start from 0 for perfect symmetry
        t.pendown()  # Pen stays down for entire pattern
        
        # Draw center mystic symbol (focal point)
        center_size = 15
        for i in range(3):
            t.circle(center_size + i * 8)
            t.goto(0, 0)
            t.setheading(0)
        
        # Draw radial spokes and rings - Doctor Strange style
        for ring_idx in range(self.num_rings):
            current_radius = self.base_radius + (ring_idx * self.ring_spacing)
            
            # Draw spokes from center to ring
            for i in range(self.num_spokes):
                angle = i * angle_step
                
                # Return to center
                t.goto(0, 0)
                t.setheading(angle)
                
                # Draw spoke line
                end_x = current_radius * math.cos(math.radians(angle))
                end_y = current_radius * math.sin(math.radians(angle))
                t.goto(end_x, end_y)
                
                # Draw mystical runes at spoke endpoints (if enabled)
                if self.has_runes:
                    current_heading = t.heading()
                    self._draw_rune(t, end_x, end_y, 8 + ring_idx * 2, self.rune_type)
                    t.setheading(current_heading)
                    t.goto(end_x, end_y)
                
                self.pattern_points.append((end_x, end_y))
                
                # Track gaze
                gaze_pos = eye_tracker.get_gaze_position()
                if gaze_pos:
                    eye_tracker.log_gaze((end_x, end_y), gaze_pos, time.time() - start_time)
            
            # Draw connecting circle at this radius
            t.goto(0, 0)
            t.goto(0, -current_radius)
            t.setheading(0)
            t.circle(current_radius)
        
        # Draw outer decorative rings (like Doctor Strange's spell layers)
        num_outer_rings = random.randint(2, 4)
        outer_start = self.base_radius + (self.num_rings * self.ring_spacing) + 20
        
        for i in range(num_outer_rings):
            ring_radius = outer_start + (i * 30)
            t.goto(0, 0)
            t.goto(0, -ring_radius)
            t.setheading(0)
            t.circle(ring_radius)
        
        # Add mystical cross lines through center (rotating mandalas effect)
        t.pensize(1)
        num_cross_lines = self.num_spokes * 2
        for i in range(num_cross_lines):
            angle = i * (360 / num_cross_lines)
            t.goto(0, 0)
            t.setheading(angle)
            max_radius = outer_start + (num_outer_rings * 30) + 20
            t.forward(max_radius)
        
        # Return to center to complete the perfect stroke
        t.goto(0, 0)
        t.penup()  # Only now lift the pen!
        
        screen.update()  # Show the completed pattern
        eye_tracker.stop_tracking()
        
        screen.update()
        eye_tracker.stop_tracking()
        
        # Show calibration results
        accuracy = eye_tracker.analyze_tracking_accuracy()
        print(f"\nCalibration Complete!")
        print(f"Tracking Accuracy: {accuracy:.2f}%")
        
        return accuracy


class Flower:
    """Flower target for aim trainer"""
    
    def __init__(self, x, y, color, size=20):
        """Initialize flower at position"""
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.bloomed = False
        self.click_time = None
    
    def draw_core(self, t):
        """Draw flower core (target)"""
        t.penup()
        t.goto(self.x, self.y)
        t.pendown()
        t.dot(self.size, self.color)
        
        # Draw outer ring
        t.penup()
        t.goto(self.x, self.y)
        t.pendown()
        t.color("black")
        t.pensize(2)
        for _ in range(2):
            t.circle(self.size // 2)
    
    def bloom(self, t, screen):
        """Animate flower blooming"""
        self.bloomed = True
        t.speed(5)
        
        # Draw petals
        petal_colors = ["#FF69B4", "#FFB6C1", "#FFC0CB", "#FF1493"]
        num_petals = 8
        
        for i in range(num_petals):
            angle = i * (360 / num_petals)
            t.penup()
            t.goto(self.x, self.y)
            t.setheading(angle)
            t.forward(self.size // 2)
            
            # Draw petal
            t.pendown()
            t.fillcolor(random.choice(petal_colors))
            t.begin_fill()
            t.circle(self.size // 2, 60)
            t.left(120)
            t.circle(self.size // 2, 60)
            t.end_fill()
        
        # Redraw center
        t.penup()
        t.goto(self.x, self.y)
        t.dot(self.size // 2, "yellow")
        
        screen.update()
    
    def is_hit(self, click_x, click_y):
        """Check if click is within flower core"""
        distance = math.sqrt((click_x - self.x)**2 + (click_y - self.y)**2)
        return distance <= self.size


class AimTrainer:
    """Aim trainer game with flowers"""
    
    def __init__(self, pattern_points, num_targets=12):
        """Initialize aim trainer"""
        self.pattern_points = pattern_points
        self.num_targets = num_targets
        self.flowers = []
        self.current_flower_idx = 0
        self.start_time = None
        self.reaction_times = []
        self.game_complete = False
    
    def generate_flower_positions(self):
        """Generate random positions on the pattern"""
        positions = []
        
        # Use pattern points and add some random positions
        sample_size = min(self.num_targets, len(self.pattern_points))
        if self.pattern_points:
            sampled = random.sample(self.pattern_points, sample_size)
            positions.extend(sampled)
        
        # Fill remaining with random positions
        while len(positions) < self.num_targets:
            angle = random.uniform(0, 360)
            radius = random.uniform(50, 250)
            x = radius * math.cos(math.radians(angle))
            y = radius * math.sin(math.radians(angle))
            positions.append((x, y))
        
        return positions
    
    def setup(self, t, screen):
        """Setup aim trainer"""
        print("\n=== Part 2: Aim Trainer - Flower Version ===")
        print(f"Click on {self.num_targets} flower cores to make them bloom!")
        
        positions = self.generate_flower_positions()
        flower_colors = ["#FF4500", "#FF6347", "#DC143C", "#C71585"]
        
        for x, y in positions:
            color = random.choice(flower_colors)
            self.flowers.append(Flower(x, y, color))
        
        self.start_time = time.time()
        self.draw_current_flower(t, screen)
    
    def draw_current_flower(self, t, screen):
        """Draw the current flower core"""
        if self.current_flower_idx < len(self.flowers):
            flower = self.flowers[self.current_flower_idx]
            flower.draw_core(t)
            screen.update()
            print(f"Flower {self.current_flower_idx + 1}/{self.num_targets} spawned")
    
    def handle_click(self, x, y, t, screen):
        """Handle mouse click"""
        if self.game_complete:
            return
        
        if self.current_flower_idx < len(self.flowers):
            flower = self.flowers[self.current_flower_idx]
            
            if flower.is_hit(x, y):
                # Record reaction time
                click_time = time.time()
                if self.current_flower_idx == 0:
                    reaction_time = click_time - self.start_time
                else:
                    prev_flower = self.flowers[self.current_flower_idx - 1]
                    reaction_time = click_time - prev_flower.click_time
                
                flower.click_time = click_time
                self.reaction_times.append(reaction_time)
                
                print(f"Hit! Reaction time: {reaction_time:.3f}s")
                
                # Bloom the flower
                flower.bloom(t, screen)
                
                # Move to next flower
                self.current_flower_idx += 1
                
                if self.current_flower_idx < len(self.flowers):
                    self.draw_current_flower(t, screen)
                else:
                    self.game_complete = True
                    print("\n🎉 All flowers bloomed! Game complete!")


class PersonalizedReport:
    """Generate personalized report"""
    
    def __init__(self, player_id, pattern, flowers, reaction_times, tracking_accuracy, pattern_image_path=None):
        """Initialize report"""
        self.player_id = player_id
        self.pattern = pattern
        self.flowers = flowers
        self.reaction_times = reaction_times
        self.tracking_accuracy = tracking_accuracy
        self.pattern_image_path = pattern_image_path
    
    def generate(self, t, screen):
        """Generate visual report"""
        print("\n=== Part 3: Personalized Report ===")
        
        screen.clear()
        t.clear()
        screen.bgcolor("white")
        t.penup()
        t.hideturtle()
        
        # Title
        t.goto(0, 320)
        t.color("black")
        t.write("CONCENTRATION TEST REPORT", align="center", 
                font=("Arial", 20, "bold"))
        
        # Player info
        t.goto(0, 285)
        t.write(f"Player: {self.player_id}", align="center", 
                font=("Arial", 14, "normal"))
        
        t.goto(0, 260)
        t.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                align="center", font=("Arial", 12, "normal"))
        
        # Redraw the magic pattern on the right side
        t.goto(0, 230)
        t.write("Your Magic Pattern with Flower Blooms:", 
                align="center", font=("Arial", 12, "bold"))
        
        # Draw the pattern on the right side (scaled down)
        original_pos = t.position()
        scale = 0.7  # Scale down the pattern to fit
        offset_x = 300  # Move to right side
        offset_y = -50  # Move down a bit
        
        # Redraw the magic spell ring
        t.penup()
        t.goto(offset_x, offset_y)
        t.color(self.pattern.color)
        t.pensize(1)
        t.pendown()
        
        # Draw center spiral
        center_size = 15 * scale
        for i in range(3):
            t.circle((center_size + i * 8) * scale)
            t.goto(offset_x, offset_y)
        
        angle_step = 360 / self.pattern.num_spokes
        
        # Draw radial spokes and rings
        for ring_idx in range(self.pattern.num_rings):
            current_radius = (self.pattern.base_radius + (ring_idx * self.pattern.ring_spacing)) * scale
            
            for i in range(self.pattern.num_spokes):
                angle = i * angle_step
                t.goto(offset_x, offset_y)
                
                end_x = offset_x + current_radius * math.cos(math.radians(angle))
                end_y = offset_y + current_radius * math.sin(math.radians(angle))
                t.goto(end_x, end_y)
                
                # Draw runes if pattern has them
                if self.pattern.has_runes:
                    rune_size = (8 + ring_idx * 2) * scale
                    if self.pattern.rune_type == 'circle':
                        t.circle(rune_size)
                        t.goto(end_x, end_y)
            
            # Draw connecting circle
            t.goto(offset_x, offset_y)
            t.goto(offset_x, offset_y - current_radius)
            t.setheading(0)
            t.circle(current_radius)
        
        # Draw outer decorative rings
        num_outer_rings = 3
        outer_start = (self.pattern.base_radius + (self.pattern.num_rings * self.pattern.ring_spacing) + 20) * scale
        
        for i in range(num_outer_rings):
            ring_radius = outer_start + (i * 30 * scale)
            t.goto(offset_x, offset_y)
            t.goto(offset_x, offset_y - ring_radius)
            t.setheading(0)
            t.circle(ring_radius)
        
        t.penup()
        
        # Draw the bloomed flowers on the pattern
        for flower in self.flowers:
            if flower.bloomed:
                flower_x = offset_x + (flower.x * scale)
                flower_y = offset_y + (flower.y * scale)
                
                # Draw petals
                for petal_angle in range(0, 360, 45):
                    t.goto(flower_x, flower_y)
                    t.setheading(petal_angle)
                    t.color(flower.petal_colors[petal_angle // 45])
                    t.pendown()
                    t.circle(10 * scale, 180)
                    t.penup()
                
                # Draw center
                t.goto(flower_x, flower_y)
                t.color("#FFD700")
                t.dot(8 * scale)
        
        # Performance stats - left side layout
        t.penup()
        t.goto(-350, 200)
        t.color("black")
        t.write("Performance Summary", align="left", font=("Arial", 14, "bold"))
        
        t.goto(-350, 175)
        t.write("═" * 40, align="left", font=("Arial", 10, "normal"))
        
        # PART 1: Eye Tracking Results
        t.goto(-350, 150)
        t.color("#2E86AB")
        t.write("PART 1: Eye Tracking Calibration", align="left", font=("Arial", 12, "bold"))
        
        t.goto(-350, 130)
        t.color("black")
        t.write(f"Tracking Accuracy:", align="left", font=("Arial", 11, "normal"))
        t.goto(-350, 110)
        if self.tracking_accuracy >= 70:
            t.color("#27AE60")  # Green
        elif self.tracking_accuracy >= 50:
            t.color("#F39C12")  # Orange
        else:
            t.color("#E74C3C")  # Red
        t.write(f"{self.tracking_accuracy:.1f}%", align="left", font=("Arial", 14, "bold"))
        
        t.color("black")
        t.goto(-350, 85)
        t.write(f"Pattern Complexity:", align="left", font=("Arial", 11, "normal"))
        t.goto(-350, 65)
        t.write(f"{self.pattern.num_spokes} spokes, {self.pattern.num_rings} rings", 
                align="left", font=("Arial", 10, "normal"))
        
        # PART 2: Aim Trainer Results
        t.goto(-350, 35)
        t.color("#A23B72")
        t.write("PART 2: Aim Trainer - Flowers", align="left", font=("Arial", 12, "bold"))
        
        # Reaction times
        if self.reaction_times:
            avg_reaction = sum(self.reaction_times) / len(self.reaction_times)
            best_reaction = min(self.reaction_times)
            accuracy = (len(self.reaction_times) / 12) * 100
            
            t.goto(-350, 15)
            t.color("black")
            t.write(f"Flowers Hit:", align="left", font=("Arial", 11, "normal"))
            t.goto(-350, -5)
            if len(self.reaction_times) == 12:
                t.color("#27AE60")
            elif len(self.reaction_times) >= 9:
                t.color("#F39C12")
            else:
                t.color("#E74C3C")
            t.write(f"{len(self.reaction_times)}/12 ({accuracy:.0f}%)", align="left", font=("Arial", 12, "bold"))
            
            t.goto(-350, -30)
            t.color("black")
            t.write(f"Average Reaction:", align="left", font=("Arial", 11, "normal"))
            t.goto(-350, -50)
            if avg_reaction < 0.5:
                t.color("#27AE60")
            elif avg_reaction < 0.8:
                t.color("#F39C12")
            else:
                t.color("#E74C3C")
            t.write(f"{avg_reaction:.3f}s", align="left", font=("Arial", 12, "bold"))
            
            t.goto(-350, -75)
            t.color("black")
            t.write(f"Best Reaction:", align="left", font=("Arial", 11, "normal"))
            t.goto(-350, -95)
            t.color("#27AE60")
            t.write(f"{best_reaction:.3f}s", align="left", font=("Arial", 12, "bold"))
        
        # Performance rating
        t.goto(-350, -125)
        t.color("black")
        t.write("═" * 40, align="left", font=("Arial", 10, "normal"))
        
        t.goto(-350, -150)
        t.write("Overall Performance Rating:", align="left", font=("Arial", 12, "bold"))
        
        t.goto(-350, -175)
        rating = self._calculate_rating()
        if rating in ["Excellent!", "Great Job!"]:
            t.color("#27AE60")
        elif rating in ["Good", "Fair"]:
            t.color("#F39C12")
        else:
            t.color("#E74C3C")
        t.write(f"★ {rating} ★", align="left", font=("Arial", 16, "bold"))
        
        screen.update()
        print("\nReport generated successfully!")
        print(f"Overall Rating: {rating}")
    
    def _calculate_rating(self):
        """Calculate overall performance rating"""
        if not self.reaction_times:
            return "Incomplete"
        
        avg_reaction = sum(self.reaction_times) / len(self.reaction_times)
        
        # Combined score
        score = 0
        
        # Tracking score (40%)
        if self.tracking_accuracy >= 70:
            score += 40
        elif self.tracking_accuracy >= 50:
            score += 30
        elif self.tracking_accuracy >= 30:
            score += 20
        else:
            score += 10
        
        # Reaction time score (40%)
        if avg_reaction < 0.5:
            score += 40
        elif avg_reaction < 1.0:
            score += 30
        elif avg_reaction < 1.5:
            score += 20
        else:
            score += 10
        
        # Completion score (20%)
        completion_rate = len(self.reaction_times) / 12
        score += completion_rate * 20
        
        # Return rating
        if score >= 90:
            return "⭐⭐⭐⭐⭐ Excellent"
        elif score >= 75:
            return "⭐⭐⭐⭐ Great"
        elif score >= 60:
            return "⭐⭐⭐ Good"
        elif score >= 45:
            return "⭐⭐ Fair"
        else:
            return "⭐ Needs Practice"


class ConcentrationGame:
    """Main game controller"""
    
    def __init__(self, player_id):
        """Initialize game"""
        self.player_id = player_id
        print("\n" + "=" * 60)
        print("CONCENTRATION TEST GAME")
        print("=" * 60)
        print(f"Player: {player_id}")
        print("=" * 60)
        
        # Setup turtle screen
        self.screen = turtle.Screen()
        self.screen.setup(width=900, height=700)
        self.screen.bgcolor("white")
        self.screen.title(f"Concentration Test - {player_id}")
        
        self.t = turtle.Turtle()
        self.t.hideturtle()
        
        # Initialize components
        self.eye_tracker = EyeTracker()
        self.pattern = MagicPattern(player_id)
        self.aim_trainer = None
        self.tracking_accuracy = 0
        self.pattern_image_path = None
    
    def save_pattern_image(self):
        """Save the current screen as an image"""
        try:
            # Create images directory if it doesn't exist
            if not os.path.exists("pattern_images"):
                os.makedirs("pattern_images")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            eps_file = f"pattern_images/{self.player_id}_{timestamp}.eps"
            png_file = f"pattern_images/{self.player_id}_{timestamp}.png"
            
            # Save the canvas as EPS
            ts = self.screen.getcanvas()
            ts.postscript(file=eps_file)
            
            # Convert EPS to PNG for better compatibility
            try:
                # Try to convert using PIL/Pillow
                from PIL import Image
                img = Image.open(eps_file)
                img.save(png_file, 'PNG')
                self.pattern_image_path = png_file
                print(f"Pattern saved to: {png_file}")
            except Exception as e:
                # If conversion fails, keep the EPS file
                self.pattern_image_path = eps_file
                print(f"Pattern saved to: {eps_file}")
            
        except Exception as e:
            print(f"Could not save pattern image: {e}")
            self.pattern_image_path = None
    
    def run(self):
        """Run the complete game"""
        try:
            # Part 1: Calibration
            self.tracking_accuracy = self.pattern.draw(self.t, self.screen, self.eye_tracker)
            time.sleep(2)
            
            # Part 2: Aim Trainer
            self.aim_trainer = AimTrainer(self.pattern.pattern_points)
            self.aim_trainer.setup(self.t, self.screen)
            
            # Setup click handler
            def click_handler(x, y):
                self.aim_trainer.handle_click(x, y, self.t, self.screen)
                
                # Check if game complete
                if self.aim_trainer.game_complete:
                    # Save the pattern with flowers as image
                    self.save_pattern_image()
                    time.sleep(2)
                    self.show_report()
            
            self.screen.onclick(click_handler)
            
            # Wait for game to complete
            self.screen.mainloop()
            
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        finally:
            self.cleanup()
    
    def show_report(self):
        """Show personalized report"""
        report = PersonalizedReport(
            self.player_id,
            self.pattern,
            self.aim_trainer.flowers,
            self.aim_trainer.reaction_times,
            self.tracking_accuracy,
            self.pattern_image_path
        )
        report.generate(self.t, self.screen)
        
        print("\nClick anywhere to exit...")
        
        def exit_handler(x, y):
            self.cleanup()
        
        self.screen.onclick(exit_handler)
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")
        self.eye_tracker.cleanup()
        try:
            self.screen.bye()
        except:
            pass


def main():
    """Main entry point"""
    print("\n🎮 Welcome to the Concentration Test Game! 🎮\n")
    
    # Generate random player ID automatically
    player_id = f"Player_{random.randint(1000, 9999)}"
    
    print(f"Your Player ID: {player_id}")
    print("\n📋 Game Instructions:")
    print("Part 1: Follow the magic pattern with your eyes")
    print("Part 2: Click on flower cores to make them bloom (12 flowers)")
    print("Part 3: View your personalized performance report")
    print("\nStarting game...\n")
    
    game = ConcentrationGame(player_id)
    game.run()


if __name__ == "__main__":
    main()
