"""
Game01_pygame.py - Artistic Concentration Game (Pygame Version)
An interactive experience that transforms your focus into personalized artwork.

Part 1: Magic Circle Calibration - Animated symmetrical patterns for focus
Part 2: Flower Aim Trainer - 12 blooming flowers with 1.5s timeout
Part 3: Artistic Report - Your unique artwork combining all elements
"""

import pygame
import random
import math
import time
import cv2
import mediapipe as mp
from datetime import datetime
import os
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (245, 245, 245)


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
    
    elif sound_type == 'hello':
        # "Hello" - rising then falling pitch with stronger formants
        duration = 0.45
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # "Hel-" rising, "-lo" falling
            if progress < 0.4:
                freq = 180 + 120 * (progress / 0.4)
            else:
                freq = 300 - 80 * ((progress - 0.4) / 0.6)
            
            # Add stronger formants (vocal resonances)
            fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.6
            formant1 = math.sin(2 * math.pi * freq * 3 * t / sample_rate) * 0.3
            formant2 = math.sin(2 * math.pi * freq * 5 * t / sample_rate) * 0.2
            
            amplitude = math.sin(progress * math.pi) * 0.95
            wave.append((fundamental + formant1 + formant2) * amplitude)
    
    elif sound_type == 'hey':
        # "Hey!" - quick rising exclamation with stronger presence
        duration = 0.3
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            freq = 200 + 250 * progress
            
            # Stronger formants for "ay" sound
            fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.7
            formant1 = math.sin(2 * math.pi * freq * 4 * t / sample_rate) * 0.3
            formant2 = math.sin(2 * math.pi * freq * 7 * t / sample_rate) * 0.2
            
            amplitude = math.exp(-progress * 2) * 0.95
            wave.append((fundamental + formant1 + formant2) * amplitude)
    
    elif sound_type == 'oh':
        # "Oh!" - surprise sound with stronger presence
        duration = 0.4
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # Quick rise then gradual fall
            if progress < 0.15:
                freq = 150 + 200 * (progress / 0.15)
            else:
                freq = 350 - 100 * ((progress - 0.15) / 0.85)
            
            # Stronger rounded "oh" formants
            fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.7
            formant1 = math.sin(2 * math.pi * freq * 2 * t / sample_rate) * 0.35
            formant2 = math.sin(2 * math.pi * freq * 3.5 * t / sample_rate) * 0.15
            
            amplitude = math.sin(progress * math.pi) * 0.95
            wave.append((fundamental + formant1 + formant2) * amplitude)
    
    elif sound_type == 'wow':
        # "Wow" - two syllables with stronger presence
        duration = 0.5
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # "W-" low, "-ow" high and falling
            if progress < 0.25:
                freq = 160 + 40 * (progress / 0.25)
            elif progress < 0.45:
                freq = 200 + 200 * ((progress - 0.25) / 0.2)
            else:
                freq = 400 - 150 * ((progress - 0.45) / 0.55)
            
            # Stronger formants
            fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.65
            formant1 = math.sin(2 * math.pi * freq * 2.5 * t / sample_rate) * 0.35
            formant2 = math.sin(2 * math.pi * freq * 4 * t / sample_rate) * 0.2
            
            amplitude = 0.85 + 0.15 * math.sin(progress * math.pi)
            wave.append((fundamental + formant1 + formant2) * amplitude * 0.95)
    
    elif sound_type == 'yeah':
        # "Yeah" - affirmative sound with stronger presence
        duration = 0.4
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # Steady with slight rise at end
            freq = 220 + 80 * math.sin(progress * math.pi)
            
            # Stronger formants for "yeah"
            fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.6
            formant1 = math.sin(2 * math.pi * freq * 3.5 * t / sample_rate) * 0.35
            formant2 = math.sin(2 * math.pi * freq * 6 * t / sample_rate) * 0.25
            
            amplitude = math.sin(progress * math.pi) * 0.95
            wave.append((fundamental + formant1 + formant2) * amplitude)
    
    elif sound_type == 'cough':
        # Short burst of noise
        duration = 0.15
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            # Mix of frequencies to create cough-like sound
            noise = random.uniform(-1, 1) * 0.3
            tone = math.sin(2 * math.pi * 180 * t / sample_rate) * 0.7
            amplitude = math.exp(-t / (n_samples * 0.3))
            wave.append((noise + tone) * amplitude)
    
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
    
    elif sound_type == 'owl':
        # More realistic hoot with deeper tone and breath - triple hoot
        duration = 0.8
        n_samples = int(duration * sample_rate)
        wave = []
        for t in range(n_samples):
            progress = t / n_samples
            # Deep hoot with subtle frequency variation
            freq = 200 + 15 * math.sin(t / sample_rate * math.pi * 6)
            # Add harmonics for depth
            fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.7
            harmonic2 = math.sin(2 * math.pi * freq * 2 * t / sample_rate) * 0.2
            # Slight breathiness
            noise = random.uniform(-0.1, 0.1)
            # Triple-hoot pattern
            if progress < 0.28:
                amplitude = math.sin(progress / 0.28 * math.pi)
            elif progress < 0.36:
                amplitude = 0.1
            elif progress < 0.56:
                amplitude = math.sin((progress - 0.36) / 0.2 * math.pi)
            elif progress < 0.64:
                amplitude = 0.1
            else:
                amplitude = math.sin((progress - 0.64) / 0.36 * math.pi)
            
            wave.append((fundamental + harmonic2 + noise) * amplitude * 0.9)
    
    elif sound_type == 'crow':
        # Harsh caw sound - double caw
        segments = []
        for caw in range(2):
            duration = 0.28
            n_samples = int(duration * sample_rate)
            for t in range(n_samples):
                progress = t / n_samples
                freq = 800 - 200 * progress
                # Harsh harmonics for crow
                fundamental = math.sin(2 * math.pi * freq * t / sample_rate) * 0.4
                harmonic2 = math.sin(2 * math.pi * freq * 1.8 * t / sample_rate) * 0.3
                harmonic3 = math.sin(2 * math.pi * freq * 2.5 * t / sample_rate) * 0.2
                noise = random.uniform(-0.4, 0.4)
                amplitude = math.exp(-progress * 3) * (0.9 + 0.1 * math.sin(t * 0.1))
                segments.append((fundamental + harmonic2 + harmonic3 + noise) * amplitude)
            # Pause between caws
            if caw < 1:
                segments.extend([0] * int(0.12 * sample_rate))
        wave = segments
    
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
    
    elif sound_type == 'rooster':
        # Cock-a-doodle-doo pattern
        segments = []
        # Rising "cock-a-"
        for freq_base in [400, 500, 650]:
            duration = 0.08
            n_samples = int(duration * sample_rate)
            for t in range(n_samples):
                progress = t / n_samples
                freq = freq_base + 100 * progress
                tone = math.sin(2 * math.pi * freq * t / sample_rate) * 0.7
                amplitude = math.sin(progress * math.pi)
                segments.append(tone * amplitude)
            segments.extend([0] * int(0.02 * sample_rate))
        
        # Sustained "-doodle-doo"
        duration = 0.15
        n_samples = int(duration * sample_rate)
        for t in range(n_samples):
            progress = t / n_samples
            freq = 900 - 200 * progress
            tone = math.sin(2 * math.pi * freq * t / sample_rate) * 0.8
            amplitude = 0.9
            segments.append(tone * amplitude)
        
        wave = segments
    
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
        self.camera_window_name = 'Eye Tracking'
        
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
            
            # Convert to screen coordinates
            screen_x = avg_x * SCREEN_WIDTH
            screen_y = avg_y * SCREEN_HEIGHT
            
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
                left_eye = face_landmarks.landmark[468]
                left_x, left_y = int(left_eye.x * w), int(left_eye.y * h)
                cv2.circle(frame, (left_x, left_y), 5, (0, 255, 0), -1)
                
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
                
                cv2.putText(frame, 'Tracking Active', (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, 'No Face Detected', (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Resize to small preview (200x150)
            small_frame = cv2.resize(frame, (200, 150))
            
            # Display in window
            cv2.imshow(self.camera_window_name, small_frame)
            cv2.moveWindow(self.camera_window_name, 1000, 50)
            cv2.waitKey(1)
        except Exception as e:
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
        """Calculate overall tracking accuracy"""
        if not self.gaze_data:
            return 0
        
        avg_distance = sum(d['distance'] for d in self.gaze_data) / len(self.gaze_data)
        accuracy = max(0, min(100, (1 - avg_distance / 200) * 100))
        return accuracy
    
    def stop_tracking(self):
        """Stop tracking and release resources"""
        self.tracking_active = False
        if self.cap:
            self.cap.release()
        try:
            cv2.destroyWindow(self.camera_window_name)
        except:
            pass


class MagicCircle:
    """Procedurally generated animated magic circle"""
    
    def __init__(self, player_id):
        """Initialize magic circle with unique seed"""
        self.player_id = player_id
        self.seed = int(time.time() * 1000) % (2**32)
        random.seed(self.seed)
        
        # Core geometric shape - NOT just circles!
        self.base_shape = random.choice(['circle', 'triangle', 'square', 'pentagon', 'hexagon', 'octagon', 'star'])
        self.shape_sides = {
            'triangle': 3, 'square': 4, 'pentagon': 5, 
            'hexagon': 6, 'octagon': 8, 'star': 5, 'circle': 12
        }[self.base_shape]
        
        # Pattern parameters - simplified
        self.num_spokes = random.choice([8, 12, 16])  # Reduced from [8, 12, 16, 20, 24, 32]
        self.num_layers = random.randint(4, 6)  # Reduced from (6, 10)
        self.base_radius = random.randint(40, 50)
        self.layer_spacing = random.randint(20, 28)
        
        # Simpler layer types - more circles, less complex shapes
        self.layer_types = []
        for i in range(self.num_layers):
            self.layer_types.append(random.choice([
                'circle', 'circle', 'polygon', 'star'  # Weighted toward circles
            ]))
        
        # Reduced complexity parameters
        self.has_fractals = False  # Disable fractals
        self.has_nested_shapes = random.choice([True, False])  # Sometimes off
        self.has_overlapping = False  # Disable for simplicity
        self.symmetry_order = random.choice([4, 6, 8])  # Reduced options
        self.rotation_offset = random.uniform(0, 360)
        self.complexity_level = random.choice(['moderate', 'medium', 'balanced'])
        
        # Fewer geometric overlays
        self.overlay_shapes = random.sample(
            ['triangle', 'square', 'hexagon'],
            k=random.randint(1, 2)  # Reduced from (2, 4)
        )
        
        # Symbol layers - simpler options
        self.inner_pattern = random.choice(['seed_of_life', 'mandala', 'flower_of_life'])  # Removed complex ones
        self.middle_pattern = random.choice(['geometric_grid', 'nested_polygons'])
        self.outer_pattern = random.choice(['rays', 'petals', 'waves'])
        
        # Connection and decoration styles - simplified
        self.has_dots = True
        self.has_connecting_lines = True
        self.has_weaving = False  # Disable weaving
        self.connection_style = random.choice(['straight', 'web'])
        self.decoration_density = random.choice(['low', 'medium'])  # Reduced density
        
        # Color scheme - only 2-3 colors
        self.primary_color = self._generate_color()
        self.secondary_color = self._generate_complementary_color()
        self.use_tertiary = random.choice([True, False])
        if self.use_tertiary:
            self.tertiary_color = self._generate_tertiary_color()
        else:
            self.tertiary_color = self.primary_color
        self.pattern_points = []
        
        print(f"✨ Generated sacred geometry for {player_id}")
        print(f"   Base Shape: {self.base_shape} | Layers: {self.num_layers} | Symmetry: {self.symmetry_order}")
        print(f"   Pattern: {self.inner_pattern}/{self.middle_pattern}/{self.outer_pattern}")
        print(f"   Overlays: {', '.join(self.overlay_shapes)}")
        print(f"   Complexity: {self.complexity_level}")
    
    def _generate_color(self):
        """Generate a mystical color"""
        colors = [
            (74, 144, 226), (155, 89, 182), (230, 126, 34), (26, 188, 156),
            (233, 30, 99), (52, 152, 219), (142, 68, 173), (22, 160, 133),
            (231, 76, 60), (46, 204, 113), (52, 73, 94)
        ]
        return random.choice(colors)
    
    def _generate_complementary_color(self):
        """Generate complementary color"""
        r, g, b = self.primary_color
        # Create a complementary color by shifting hue
        return ((r + 128) % 256, (g + 128) % 256, (b + 128) % 256)
    
    def _generate_tertiary_color(self):
        """Generate tertiary color - midpoint between primary and secondary"""
        r1, g1, b1 = self.primary_color
        r2, g2, b2 = self.secondary_color
        return ((r1 + r2) // 2, (g1 + g2) // 2, (b1 + b2) // 2)
    
    def draw_animated(self, screen, eye_tracker):
        """Draw the magic circle with animation and glow effects"""
        print("\n=== Part 1: Magic Circle Calibration ===")
        print("🎯 Watch the magical pattern unfold before your eyes...")
        
        eye_tracker.start_tracking()
        start_time = time.time()
        
        clock = pygame.time.Clock()
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Create darker background for glow effect
        screen.fill((10, 10, 15))
        
        # Draw with glow effect - multiple layers for luminosity
        self._draw_with_glow(screen, center_x, center_y, eye_tracker, start_time)
        
        pygame.display.flip()
        eye_tracker.show_camera_preview()
        
        print("✓ Magic circle complete - A unique masterpiece!")
        print(f"✓ Eye tracking {'successful' if eye_tracker.facial_detected else 'unavailable'}")
        time.sleep(1)
    
    def _draw_with_glow(self, screen, center_x, center_y, eye_tracker, start_time):
        """Draw complex sacred geometry with multiple overlapping patterns"""
        clock = pygame.time.Clock()
        
        # Simplified color palette - only 2-3 colors
        bright_color = self.primary_color
        dim_color = self.secondary_color
        very_dim = self.tertiary_color
        sec_bright = self.secondary_color
        sec_dim = self.tertiary_color
        
        # Layer 1: Draw intricate center pattern (Seed of Life, Metatron's Cube, etc.)
        self._draw_sacred_center(screen, center_x, center_y, bright_color, dim_color, eye_tracker, clock)
        eye_tracker.show_camera_preview()
        
        # Layer 2: Draw base geometric shape (not just circles!)
        self._draw_base_geometry(screen, center_x, center_y, bright_color, dim_color, very_dim, eye_tracker, start_time, clock)
        eye_tracker.show_camera_preview()
        
        # Layer 3: Draw overlapping geometric overlays
        for overlay_shape in self.overlay_shapes:
            self._draw_geometric_overlay(screen, center_x, center_y, overlay_shape, sec_bright, sec_dim)
            pygame.display.flip()
            clock.tick(8)
        
        # Layer 4: Draw intricate web connections
        self._draw_complex_web(screen, center_x, center_y, dim_color, very_dim)
        pygame.display.flip()
        pygame.time.wait(150)
        
        # Layer 5: Draw fractal/recursive patterns
        if self.has_fractals:
            self._draw_fractal_patterns(screen, center_x, center_y, bright_color, dim_color)
            pygame.display.flip()
        
        # Layer 6: Draw nested polygons at all vertices
        self._draw_nested_decorations(screen, center_x, center_y, bright_color, sec_bright, dim_color)
        pygame.display.flip()
        pygame.time.wait(150)
        
        # Layer 7: Extended rays and outer decorations
        self._draw_outer_complexity(screen, center_x, center_y, bright_color, dim_color, sec_bright)
        pygame.display.flip()
        pygame.time.wait(150)
        
        # Layer 8: Brilliant center
        self._draw_brilliant_core(screen, center_x, center_y, bright_color, clock)
        pygame.display.flip()
    
    def _draw_sacred_center(self, screen, cx, cy, bright, dim, eye_tracker, clock):
        """Draw elaborate sacred geometry center"""
        if self.inner_pattern == 'seed_of_life':
            # Seed of Life - 7 overlapping circles, drawn one at a time
            radius = 25
            positions = [(0, 0)]
            for i in range(6):
                angle = i * 60
                x = int(radius * math.cos(math.radians(angle)))
                y = int(radius * math.sin(math.radians(angle)))
                positions.append((x, y))
            
            for px, py in positions:
                for thickness in [4, 3, 2, 1]:
                    glow = tuple(max(0, c - thickness * 20) for c in dim)
                    pygame.draw.circle(screen, glow, (cx + px, cy + py), radius, thickness)
                pygame.draw.circle(screen, bright, (cx + px, cy + py), radius, 1)
                # Update after each circle
                pygame.display.flip()
                clock.tick(12)
        
        elif self.inner_pattern == 'metatron':
            # Metatron's Cube - complex overlapping geometry
            radius = 30
            # Draw 13 circles in Metatron's Cube pattern
            positions = [(0, 0)]
            for ring in [1, 2]:
                r = radius * ring
                for i in range(6):
                    angle = i * 60
                    x = int(r * math.cos(math.radians(angle)))
                    y = int(r * math.sin(math.radians(angle)))
                    positions.append((x, y))
            
            # Draw circles
            for px, py in positions:
                pygame.draw.circle(screen, bright, (cx + px, cy + py), 12, 2)
            
            # Draw connecting lines between all points
            for i, (x1, y1) in enumerate(positions):
                for x2, y2 in positions[i+1:]:
                    pygame.draw.line(screen, dim, (cx + x1, cy + y1), (cx + x2, cy + y2), 1)
        
        elif self.inner_pattern == 'sri_yantra':
            # Sri Yantra - overlapping triangles
            for size in [15, 25, 35, 45]:
                # Upward triangle
                points_up = []
                for i in range(3):
                    angle = -90 + i * 120
                    x = cx + int(size * math.cos(math.radians(angle)))
                    y = cy + int(size * math.sin(math.radians(angle)))
                    points_up.append((x, y))
                pygame.draw.polygon(screen, bright, points_up, 2)
                
                # Downward triangle
                points_down = []
                for i in range(3):
                    angle = 90 + i * 120
                    x = cx + int(size * math.cos(math.radians(angle)))
                    y = cy + int(size * math.sin(math.radians(angle)))
                    points_down.append((x, y))
                pygame.draw.polygon(screen, dim, points_down, 2)
        
        elif self.inner_pattern == 'flower_of_life':
            # Flower of Life pattern, drawn circle by circle
            radius = 22
            rows = 3
            for row in range(-rows, rows + 1):
                cols = 5 if row % 2 == 0 else 4
                offset_x = 0 if row % 2 == 0 else radius * math.sqrt(3) / 2
                for col in range(-cols, cols + 1):
                    x = cx + col * radius * math.sqrt(3) + offset_x
                    y = cy + row * radius * 1.5
                    if math.sqrt((x - cx)**2 + (y - cy)**2) < 80:
                        pygame.draw.circle(screen, bright, (int(x), int(y)), radius, 1)
                        pygame.display.flip()
                        clock.tick(15)
    
    def _draw_base_geometry(self, screen, cx, cy, bright, dim, very_dim, eye_tracker, start_time, clock):
        """Draw base geometric structure (polygons, not just circles)"""
        angle_step = 360 / self.num_spokes
        
        for layer_idx in range(self.num_layers):
            current_radius = self.base_radius + (layer_idx * self.layer_spacing)
            layer_type = self.layer_types[layer_idx]
            
            # Draw layer shape based on type
            if layer_type == 'polygon':
                self._draw_polygon_layer(screen, cx, cy, current_radius, self.shape_sides, bright, dim, very_dim, self.rotation_offset + layer_idx * 15)
            elif layer_type == 'star':
                self._draw_star_layer(screen, cx, cy, current_radius, self.symmetry_order, bright, dim)
            elif layer_type == 'flower':
                self._draw_flower_layer(screen, cx, cy, current_radius, bright, dim)
            elif layer_type == 'gear':
                self._draw_gear_layer(screen, cx, cy, current_radius, bright, dim)
            else:
                # Circle with glow
                for thickness in [5, 3, 2, 1]:
                    glow = tuple(max(0, c - thickness * 20) for c in dim)
                    pygame.draw.circle(screen, glow, (cx, cy), current_radius, thickness)
                pygame.draw.circle(screen, bright, (cx, cy), current_radius, 1)
            
            # Draw radiating spokes from center, one at a time
            for i in range(self.num_spokes):
                angle = i * angle_step + self.rotation_offset
                end_x = cx + int(current_radius * math.cos(math.radians(angle)))
                end_y = cy + int(current_radius * math.sin(math.radians(angle)))
                
                # Multi-layer glow
                for thickness in [4, 2, 1]:
                    glow = tuple(max(0, c - thickness * 30) for c in dim)
                    pygame.draw.line(screen, glow, (cx, cy), (end_x, end_y), thickness)
                pygame.draw.line(screen, bright, (cx, cy), (end_x, end_y), 1)
                
                # Store points for flowers
                self.pattern_points.append((end_x - cx, end_y - cy))
                
                # Decorative nodes
                if layer_idx % 2 == 0:
                    for thickness in [6, 4, 2]:
                        pygame.draw.circle(screen, dim, (end_x, end_y), thickness, 1)
                    pygame.draw.circle(screen, bright, (end_x, end_y), 3, 0)
                
                # Log gaze
                gaze_pos = eye_tracker.get_gaze_position()
                if gaze_pos:
                    eye_tracker.log_gaze((end_x, end_y), gaze_pos, time.time() - start_time)
                
                # Update display after each spoke for continuous animation
                pygame.display.flip()
                clock.tick(8)
    
    def _draw_polygon_layer(self, screen, cx, cy, radius, sides, bright, dim, very_dim, rotation):
        """Draw polygon shape with glow"""
        points = []
        for i in range(sides):
            angle = (360 / sides) * i + rotation
            x = cx + int(radius * math.cos(math.radians(angle)))
            y = cy + int(radius * math.sin(math.radians(angle)))
            points.append((x, y))
        
        # Draw with glow
        if len(points) > 2:
            for thickness in [5, 3, 2]:
                glow = tuple(max(0, c - thickness * 20) for c in dim)
                pygame.draw.polygon(screen, glow, points, thickness)
            pygame.draw.polygon(screen, bright, points, 2)
    
    def _draw_star_layer(self, screen, cx, cy, radius, points_count, bright, dim):
        """Draw star shape"""
        points = []
        for i in range(points_count * 2):
            angle = (360 / (points_count * 2)) * i
            r = radius if i % 2 == 0 else radius * 0.5
            x = cx + int(r * math.cos(math.radians(angle)))
            y = cy + int(r * math.sin(math.radians(angle)))
            points.append((x, y))
        
        if len(points) > 2:
            pygame.draw.polygon(screen, dim, points, 3)
            pygame.draw.polygon(screen, bright, points, 1)
    
    def _draw_flower_layer(self, screen, cx, cy, radius, bright, dim):
        """Draw flower petal layer"""
        for i in range(12):
            angle = i * 30
            petal_cx = cx + int(radius * 0.7 * math.cos(math.radians(angle)))
            petal_cy = cy + int(radius * 0.7 * math.sin(math.radians(angle)))
            pygame.draw.circle(screen, dim, (petal_cx, petal_cy), int(radius * 0.3), 2)
            pygame.draw.circle(screen, bright, (petal_cx, petal_cy), int(radius * 0.3), 1)
    
    def _draw_gear_layer(self, screen, cx, cy, radius, bright, dim):
        """Draw gear-like layer"""
        teeth = 24
        for i in range(teeth):
            angle = (360 / teeth) * i
            if i % 2 == 0:
                r1 = radius
                r2 = radius * 1.1
            else:
                r1 = radius * 1.1
                r2 = radius
            
            x1 = cx + int(r1 * math.cos(math.radians(angle)))
            y1 = cy + int(r1 * math.sin(math.radians(angle)))
            x2 = cx + int(r2 * math.cos(math.radians(angle + 360 / teeth)))
            y2 = cy + int(r2 * math.sin(math.radians(angle + 360 / teeth)))
            
            pygame.draw.line(screen, bright, (x1, y1), (x2, y2), 2)
    
    def _draw_geometric_overlay(self, screen, cx, cy, shape, bright, dim):
        """Draw overlapping geometric shapes"""
        base_radius = self.base_radius + (self.num_layers // 2) * self.layer_spacing
        
        sides_map = {'triangle': 3, 'square': 4, 'pentagon': 5, 'hexagon': 6, 'star': 10}
        sides = sides_map.get(shape, 6)
        
        for scale in [1.2, 1.0, 0.8]:
            radius = base_radius * scale
            points = []
            
            if shape == 'star':
                for i in range(sides):
                    angle = (360 / sides) * i
                    r = radius if i % 2 == 0 else radius * 0.6
                    x = cx + int(r * math.cos(math.radians(angle)))
                    y = cy + int(r * math.sin(math.radians(angle)))
                    points.append((x, y))
            elif shape == 'flower':
                # Draw overlapping circles
                for i in range(8):
                    angle = i * 45
                    x = cx + int(radius * 0.5 * math.cos(math.radians(angle)))
                    y = cy + int(radius * 0.5 * math.sin(math.radians(angle)))
                    pygame.draw.circle(screen, dim, (x, y), int(radius * 0.4), 1)
                continue
            else:
                for i in range(sides):
                    angle = (360 / sides) * i + 15
                    x = cx + int(radius * math.cos(math.radians(angle)))
                    y = cy + int(radius * math.sin(math.radians(angle)))
                    points.append((x, y))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, dim, points, 2)
                pygame.draw.polygon(screen, bright, points, 1)
    
    
    def _draw_complex_web(self, screen, cx, cy, dim, very_dim):
        """Draw intricate web connections"""
        for layer_idx in range(1, self.num_layers, 2):
            radius = self.base_radius + (layer_idx * self.layer_spacing)
            
            # Connect every spoke to multiple other spokes for complex web
            for i in range(self.num_spokes):
                angle1 = i * (360 / self.num_spokes) + self.rotation_offset
                x1 = cx + int(radius * math.cos(math.radians(angle1)))
                y1 = cy + int(radius * math.sin(math.radians(angle1)))
                
                # Connect to non-adjacent spokes
                for skip in [2, 3, self.num_spokes // 2]:
                    j = (i + skip) % self.num_spokes
                    angle2 = j * (360 / self.num_spokes) + self.rotation_offset
                    x2 = cx + int(radius * math.cos(math.radians(angle2)))
                    y2 = cy + int(radius * math.sin(math.radians(angle2)))
                    
                    pygame.draw.line(screen, very_dim, (x1, y1), (x2, y2), 1)
    
    def _draw_fractal_patterns(self, screen, cx, cy, bright, dim):
        """Draw fractal/recursive patterns"""
        # Draw smaller copies of the base shape at key points
        mid_layer = self.num_layers // 2
        radius = self.base_radius + (mid_layer * self.layer_spacing)
        
        for i in range(self.symmetry_order):
            angle = i * (360 / self.symmetry_order)
            fx = cx + int(radius * math.cos(math.radians(angle)))
            fy = cy + int(radius * math.sin(math.radians(angle)))
            
            # Draw mini fractal shape
            for mini_r in [15, 10, 5]:
                points = []
                for j in range(self.shape_sides):
                    mini_angle = (360 / self.shape_sides) * j + angle
                    px = fx + int(mini_r * math.cos(math.radians(mini_angle)))
                    py = fy + int(mini_r * math.sin(math.radians(mini_angle)))
                    points.append((px, py))
                
                if len(points) > 2:
                    pygame.draw.polygon(screen, dim, points, 1)
    
    def _draw_nested_decorations(self, screen, cx, cy, bright, sec_bright, dim):
        """Draw nested polygons at all major vertices"""
        for layer_idx in range(0, self.num_layers, 2):
            radius = self.base_radius + (layer_idx * self.layer_spacing)
            
            for i in range(self.num_spokes):
                angle = i * (360 / self.num_spokes) + self.rotation_offset
                vx = cx + int(radius * math.cos(math.radians(angle)))
                vy = cy + int(radius * math.sin(math.radians(angle)))
                
                # Draw nested shapes at this vertex
                for nest_size in [10, 7, 4]:
                    color = bright if nest_size == 10 else sec_bright if nest_size == 7 else dim
                    
                    if self.base_shape == 'triangle':
                        points = [(vx, vy - nest_size),
                                 (vx - nest_size * 0.866, vy + nest_size * 0.5),
                                 (vx + nest_size * 0.866, vy + nest_size * 0.5)]
                        pygame.draw.polygon(screen, color, points, 1)
                    elif self.base_shape == 'square':
                        pygame.draw.rect(screen, color, 
                                       (vx - nest_size // 2, vy - nest_size // 2, nest_size, nest_size), 1)
                    else:
                        pygame.draw.circle(screen, color, (vx, vy), nest_size, 1)
                    
                    # Glowing center
                    pygame.draw.circle(screen, bright, (vx, vy), 3, 0)
    
    def _draw_outer_complexity(self, screen, cx, cy, bright, dim, sec_bright):
        """Draw elaborate outer decorations"""
        outer_base = self.base_radius + (self.num_layers * self.layer_spacing) + 25
        
        # Multiple outer rings with different shapes
        for i, shape_type in enumerate(['circle', 'polygon', 'star']):
            radius = outer_base + (i * 22)
            
            if shape_type == 'circle':
                for thickness in [6, 4, 2, 1]:
                    glow = tuple(max(0, c - thickness * 18) for c in dim)
                    pygame.draw.circle(screen, glow, (cx, cy), radius, thickness)
                pygame.draw.circle(screen, bright, (cx, cy), radius, 1)
            
            elif shape_type == 'polygon':
                points = []
                for j in range(self.shape_sides):
                    angle = (360 / self.shape_sides) * j + self.rotation_offset
                    x = cx + int(radius * math.cos(math.radians(angle)))
                    y = cy + int(radius * math.sin(math.radians(angle)))
                    points.append((x, y))
                if len(points) > 2:
                    pygame.draw.polygon(screen, sec_bright, points, 2)
            
            elif shape_type == 'star':
                points = []
                for j in range(self.symmetry_order * 2):
                    angle = (360 / (self.symmetry_order * 2)) * j
                    r = radius if j % 2 == 0 else radius * 0.85
                    x = cx + int(r * math.cos(math.radians(angle)))
                    y = cy + int(r * math.sin(math.radians(angle)))
                    points.append((x, y))
                if len(points) > 2:
                    pygame.draw.polygon(screen, bright, points, 1)
        
        # Extended rays with elaborate decorations
        max_radius = outer_base + 85
        ray_count = self.num_spokes * 2
        
        for i in range(ray_count):
            angle = i * (360 / ray_count)
            ray_length = max_radius if i % 2 == 0 else max_radius * 0.75
            end_x = cx + int(ray_length * math.cos(math.radians(angle)))
            end_y = cy + int(ray_length * math.sin(math.radians(angle)))
            
            # Multi-layer glow rays
            for thickness in [5, 3, 1]:
                glow = tuple(max(0, c - thickness * 25) for c in dim)
                pygame.draw.line(screen, glow, (cx, cy), (end_x, end_y), thickness)
            pygame.draw.line(screen, bright, (cx, cy), (end_x, end_y), 1)
            
            # Decorative elements at intervals along rays
            for dist_mult in [0.7, 0.85, 0.95]:
                dec_x = cx + int(ray_length * dist_mult * math.cos(math.radians(angle)))
                dec_y = cy + int(ray_length * dist_mult * math.sin(math.radians(angle)))
                
                if self.outer_pattern == 'flames':
                    # Draw flame-like decoration
                    for flicker in range(3):
                        fx = dec_x + random.randint(-3, 3)
                        fy = dec_y + random.randint(-3, 3)
                        pygame.draw.circle(screen, bright, (fx, fy), 2, 0)
                elif self.outer_pattern == 'spikes':
                    # Sharp spikes
                    spike_len = 8
                    spike_x = dec_x + int(spike_len * math.cos(math.radians(angle)))
                    spike_y = dec_y + int(spike_len * math.sin(math.radians(angle)))
                    pygame.draw.line(screen, bright, (dec_x, dec_y), (spike_x, spike_y), 2)
                    pygame.draw.circle(screen, bright, (spike_x, spike_y), 3, 0)
                else:
                    # Glowing nodes
                    for size in [6, 4, 2]:
                        pygame.draw.circle(screen, dim, (dec_x, dec_y), size, 1)
                    pygame.draw.circle(screen, bright, (dec_x, dec_y), 2, 0)
    
    def _draw_brilliant_core(self, screen, cx, cy, bright, clock):
        """Draw brilliant glowing center with smooth animation"""
        # Multiple layers of increasing brightness - smaller core, drawn one at a time
        for size in [12, 10, 8, 6, 4]:
            intensity = int(255 * (size / 12))
            core_color = tuple(min(255, int(c * (intensity / 255) + 255 * (1 - intensity / 255))) for c in bright)
            pygame.draw.circle(screen, core_color, (cx, cy), size, 0)
            pygame.display.flip()
            pygame.time.wait(200)  # 200ms pause between each layer for slower animation
        
        # Pure white center
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 2, 0)
        pygame.display.flip()
        pygame.time.wait(200)
        
        # Glowing halo rings - smaller, drawn one at a time slowly
        for halo_r in [15, 18, 22]:
            for thickness in range(1, 3):
                alpha_val = 255 - (halo_r - 15) * 20 - thickness * 20
                glow = tuple(max(0, int(c * alpha_val / 255)) for c in bright)
                pygame.draw.circle(screen, glow, (cx, cy), halo_r, thickness)
            pygame.display.flip()
            pygame.time.wait(250)  # Longer pause for halo rings
    
    
    def _draw_symbol_at_point(self, screen, x, y, layer_idx, angle):
        """Draw symbol at spoke end (legacy method - kept for compatibility)"""
        pass


class Flower:
    """Flower that blooms when targeted"""
    
    def __init__(self, x, y, core_size=8):
        """Initialize flower at position"""
        self.x = x
        self.y = y
        self.core_size = core_size
        self.bloomed = False
        
        # Choose a random color scheme for variety
        color_schemes = [
            # Pink/Rose
            [(255, 105, 180), (255, 182, 193), (255, 20, 147), (219, 112, 147),
             (255, 192, 203), (255, 133, 192), (255, 110, 180), (255, 79, 163)],
            # Purple/Lavender
            [(186, 85, 211), (221, 160, 221), (147, 112, 219), (216, 191, 216),
             (238, 130, 238), (218, 112, 214), (199, 21, 133), (208, 155, 218)],
            # Orange/Coral
            [(255, 127, 80), (255, 160, 122), (255, 99, 71), (255, 140, 105),
             (255, 165, 0), (255, 140, 0), (255, 120, 90), (255, 180, 140)],
            # Blue/Cyan
            [(135, 206, 250), (173, 216, 230), (100, 149, 237), (176, 224, 230),
             (135, 206, 235), (70, 130, 180), (120, 180, 220), (140, 200, 240)],
            # Red/Crimson
            [(220, 20, 60), (255, 99, 132), (255, 69, 0), (255, 105, 97),
             (240, 52, 52), (255, 82, 82), (255, 118, 117), (255, 56, 79)]
        ]
        
        self.petal_colors = random.choice(color_schemes)
        # Only use layered bloom style
        self.bloom_style = 'layered'
    
    def draw_core(self, screen):
        """Draw flower core (target)"""
        pygame.draw.circle(screen, (255, 215, 0), (self.x, self.y), self.core_size)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.core_size // 2)
    
    def bloom(self, screen):
        """Animate flower blooming with artistic variations"""
        if self.bloom_style == 'classic':
            self._bloom_classic(screen)
        elif self.bloom_style == 'spiral':
            self._bloom_spiral(screen)
        elif self.bloom_style == 'layered':
            self._bloom_layered(screen)
        elif self.bloom_style == 'star':
            self._bloom_star(screen)
        
        self.bloomed = True
    
    def _bloom_classic(self, screen):
        """Classic curved petal bloom"""
        for petal_idx in range(8):
            petal_angle = petal_idx * 45
            color = self.petal_colors[petal_idx]
            
            for size in range(5, 14, 2):
                points = [(self.x, self.y)]
                base_angle = math.radians(petal_angle)
                perp_angle = base_angle + math.pi / 2
                
                for arc_angle in range(0, 181, 15):
                    angle_rad = perp_angle + math.radians(arc_angle - 90)
                    px = self.x + int(size * math.cos(base_angle)) + int(size * 0.5 * math.cos(angle_rad))
                    py = self.y + int(size * math.sin(base_angle)) + int(size * 0.5 * math.sin(angle_rad))
                    points.append((px, py))
                
                points.append((self.x, self.y))
                if len(points) > 2:
                    pygame.draw.polygon(screen, color, points, 0)
            
            pygame.display.flip()
            pygame.time.wait(15)
    
    def _bloom_spiral(self, screen):
        """Spiral outward bloom - petals stay visible"""
        angles_drawn = []
        for rotation in range(0, 180, 15):
            for petal_idx in range(8):
                petal_angle = petal_idx * 45 + rotation
                color_idx = petal_idx % len(self.petal_colors)
                color = self.petal_colors[color_idx]
                
                size = 10 + (rotation // 20)
                base_angle = math.radians(petal_angle)
                
                # Draw oval petal
                points = []
                for t in range(0, 360, 30):
                    angle_rad = base_angle + math.radians(t)
                    rx = size * 0.8
                    ry = size * 0.4
                    px = self.x + int(rx * math.cos(angle_rad) * math.cos(math.radians(t)))
                    py = self.y + int(rx * math.sin(angle_rad) * math.cos(math.radians(t))) + int(ry * math.sin(math.radians(t)))
                    points.append((px, py))
                
                if len(points) > 2:
                    pygame.draw.polygon(screen, color, points, 0)
                angles_drawn.append((petal_angle, color, size))
            
            pygame.display.flip()
            pygame.time.wait(20)
    
    def _bloom_layered(self, screen):
        """Layered lotus-like bloom with visible petals"""
        # Outer layer - 8 large petals
        for petal_idx in range(8):
            petal_angle = petal_idx * 45
            color = self.petal_colors[petal_idx]
            base_angle = math.radians(petal_angle)
            
            # Draw rounded petal
            points = [(self.x, self.y)]
            for angle_offset in range(-30, 31, 8):
                angle_rad = base_angle + math.radians(angle_offset)
                radius = 16 - abs(angle_offset) * 0.25
                px = self.x + int(radius * math.cos(angle_rad))
                py = self.y + int(radius * math.sin(angle_rad))
                points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points, 0)
                pygame.draw.polygon(screen, (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)), points, 1)
        
        pygame.display.flip()
        pygame.time.wait(30)
        
        # Middle layer - 8 medium petals offset
        for petal_idx in range(8):
            petal_angle = petal_idx * 45 + 22.5
            color = self.petal_colors[(petal_idx + 4) % len(self.petal_colors)]
            base_angle = math.radians(petal_angle)
            
            points = [(self.x, self.y)]
            for angle_offset in range(-25, 26, 8):
                angle_rad = base_angle + math.radians(angle_offset)
                radius = 11 - abs(angle_offset) * 0.2
                px = self.x + int(radius * math.cos(angle_rad))
                py = self.y + int(radius * math.sin(angle_rad))
                points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points, 0)
        
        pygame.display.flip()
        pygame.time.wait(30)
        
        # Inner layer - small center petals
        for petal_idx in range(6):
            petal_angle = petal_idx * 60
            color = (255, 200, 220)
            base_angle = math.radians(petal_angle)
            
            points = [(self.x, self.y)]
            for angle_offset in range(-20, 21, 10):
                angle_rad = base_angle + math.radians(angle_offset)
                radius = 6 - abs(angle_offset) * 0.15
                px = self.x + int(radius * math.cos(angle_rad))
                py = self.y + int(radius * math.sin(angle_rad))
                points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points, 0)
        
        pygame.display.flip()
    
    def _bloom_star(self, screen):
        """Geometric star burst with defined petals"""
        # Draw 5 pointed star petals
        for petal_idx in range(5):
            petal_angle = petal_idx * 72
            color = self.petal_colors[petal_idx]
            base_angle = math.radians(petal_angle)
            
            # Outer point
            outer_x = self.x + int(18 * math.cos(base_angle))
            outer_y = self.y + int(18 * math.sin(base_angle))
            
            # Inner points
            left_angle = base_angle - math.radians(30)
            right_angle = base_angle + math.radians(30)
            
            left_x = self.x + int(8 * math.cos(left_angle))
            left_y = self.y + int(8 * math.sin(left_angle))
            
            right_x = self.x + int(8 * math.cos(right_angle))
            right_y = self.y + int(8 * math.sin(right_angle))
            
            # Draw petal triangle
            points = [(self.x, self.y), (left_x, left_y), (outer_x, outer_y), (right_x, right_y)]
            pygame.draw.polygon(screen, color, points, 0)
            pygame.draw.polygon(screen, (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50)), points, 1)
            
            pygame.display.flip()
            pygame.time.wait(30)
        
        # Add secondary smaller points between
        for petal_idx in range(5):
            petal_angle = petal_idx * 72 + 36
            color = self.petal_colors[(petal_idx + 3) % len(self.petal_colors)]
            base_angle = math.radians(petal_angle)
            
            outer_x = self.x + int(12 * math.cos(base_angle))
            outer_y = self.y + int(12 * math.sin(base_angle))
            
            left_angle = base_angle - math.radians(25)
            right_angle = base_angle + math.radians(25)
            
            left_x = self.x + int(6 * math.cos(left_angle))
            left_y = self.y + int(6 * math.sin(left_angle))
            
            right_x = self.x + int(6 * math.cos(right_angle))
            right_y = self.y + int(6 * math.sin(right_angle))
            
            points = [(self.x, self.y), (left_x, left_y), (outer_x, outer_y), (right_x, right_y)]
            pygame.draw.polygon(screen, color, points, 0)
            
            pygame.display.flip()
            pygame.time.wait(30)

    
    def contains_point(self, x, y):
        """Check if point is inside flower core"""
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
        self.spawn_time = 0
        self.last_disturbance = 0
        
        # Generate sounds
        self.timeout_sound = generate_beep_sound(200, 0.2, 'sine', 'fade_both')  # Low timeout with fade
        # Animal sounds for distraction
        self.disturbance_sounds = [
            generate_voice_sound('bird'),
            generate_voice_sound('dog'),
            generate_voice_sound('cat'),
            generate_voice_sound('mosquito')
        ]
        
        self._generate_flower_positions()
    
    def _generate_flower_positions(self):
        """Generate 12 flower positions"""
        available_points = self.magic_circle_points.copy()
        random.shuffle(available_points)
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        for i in range(12):
            if i < len(available_points):
                x, y = available_points[i]
                x += center_x
                y += center_y
            else:
                angle = random.uniform(0, 360)
                radius = random.uniform(50, 200)
                x = center_x + int(radius * math.cos(math.radians(angle)))
                y = center_y + int(radius * math.sin(math.radians(angle)))
            
            self.flowers.append(Flower(x, y))
    
    def play(self, screen):
        """Run the flower aim trainer"""
        print("\n=== Part 2: Flower Aim Trainer ===")
        print("🌸 Click on flower cores to make them bloom!")
        print(f"   Target: 12 flowers")
        print("   ⏱️  Each flower lasts 1 second!\n")
        
        # Close camera preview
        try:
            cv2.destroyWindow('Eye Tracking')
        except:
            pass
        
        clock = pygame.time.Clock()
        self._spawn_next_flower(screen)
        
        while not self.game_complete:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event.pos, screen)
            
            # Check timeout (changed to 1 second)
            if self.current_flower_index < len(self.flowers) and time.time() - self.spawn_time > 1.0:
                self._handle_timeout(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
        
        self.eye_tracker.stop_tracking()
    
    def _spawn_next_flower(self, screen):
        """Spawn the next flower core"""
        # Only play disturbance sounds after 2nd flower, but skip 5th-7th flowers
        # Allow sounds to play simultaneously with spawn for flowers 10-12
        should_play_sound = self.current_flower_index >= 2 and not (4 <= self.current_flower_index <= 6)
        is_final_flowers = self.current_flower_index >= 9  # Flowers 10-12 (index 9-11)
        
        if should_play_sound and not is_final_flowers:
            # Play 1 misleading disturbance sound at random interval before spawning
            num_fake_sounds = random.randint(1, 1)  # Reduced to just 1 sound
            for _ in range(num_fake_sounds):
                pygame.time.wait(random.randint(400, 800))  # Longer intervals
                random.choice(self.disturbance_sounds).play()
            
            # Longer delay then spawn the actual flower
            pygame.time.wait(random.randint(300, 700))  # Longer delay
        
        self.spawn_time = time.time()
        flower = self.flowers[self.current_flower_index]
        
        # Save the background area where the flower core will be drawn
        core_area_size = flower.core_size * 4
        self.core_rect = pygame.Rect(
            flower.x - core_area_size // 2,
            flower.y - core_area_size // 2,
            core_area_size,
            core_area_size
        )
        self.saved_background = screen.subsurface(self.core_rect).copy()
        
        flower.draw_core(screen)
        pygame.display.flip()
        
        # For final flowers (10-12), play sound at the same time as spawn
        if should_play_sound and is_final_flowers:
            random.choice(self.disturbance_sounds).play()
        
        # Skip after-spawn sound to reduce frequency
        # (Removed the after-spawn sound to make sounds less frequent)
    
    def _handle_click(self, pos, screen):
        """Handle click events"""
        if self.game_complete:
            return
        
        current_flower = self.flowers[self.current_flower_index]
        
        if current_flower.contains_point(pos[0], pos[1]):
            # Hit!
            reaction_time = time.time() - self.spawn_time
            self.reaction_times.append(reaction_time)
            self.hits += 1
            
            print(f"✓ Flower {self.current_flower_index + 1}/12 bloomed! ({reaction_time:.3f}s)")
            
            current_flower.bloom(screen)
            
            self.current_flower_index += 1
            if self.current_flower_index < 12:
                self._spawn_next_flower(screen)
            else:
                self.game_complete = True
                print("\n🎉 All 12 flowers bloomed! Game complete!")
        else:
            self.misses += 1
            print(f"✗ Miss! Try again...")
    
    def _handle_timeout(self, screen):
        """Handle flower timeout"""
        current_flower = self.flowers[self.current_flower_index]
        self.misses += 1
        
        # Play timeout sound
        self.timeout_sound.play()
        
        print(f"⏱️  Timeout! Flower {self.current_flower_index + 1}/12 disappeared")
        
        # Restore the saved background to make the flower core disappear
        if hasattr(self, 'saved_background') and hasattr(self, 'core_rect'):
            screen.blit(self.saved_background, self.core_rect)
        
        pygame.display.flip()
        
        self.current_flower_index += 1
        if self.current_flower_index < 12:
            self._spawn_next_flower(screen)
        else:
            self.game_complete = True
            print("\n🎮 Game complete!")


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
    
    def generate(self, screen):
        """Generate the artistic report"""
        print("\n=== Part 3: Your Personalized Artwork ===")
        
        # Don't clear screen - keep the magic circle and flowers visible
        # Just add statistics overlay on the left side
        
        # Draw semi-transparent background for text area on left
        text_bg = pygame.Surface((400, 600))
        text_bg.set_alpha(240)
        text_bg.fill(GRAY)
        screen.blit(text_bg, (20, 100))
        
        # Title at top center
        font_title = pygame.font.Font(None, 44)
        font_subtitle = pygame.font.Font(None, 28)
        font_normal = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 18)
        
        title = font_title.render("YOUR CONCENTRATION ARTWORK", True, (44, 62, 80))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title, title_rect)
        
        player = font_small.render(f"Created by: {self.player_id}", True, (52, 73, 94))
        player_rect = player.get_rect(center=(SCREEN_WIDTH // 2, 65))
        screen.blit(player, player_rect)
        
        date = font_tiny.render(datetime.now().strftime('%B %d, %Y at %H:%M'), True, (127, 140, 141))
        date_rect = date.get_rect(center=(SCREEN_WIDTH // 2, 88))
        screen.blit(date, date_rect)
        
        # Draw statistics on left side
        self._draw_statistics(screen, font_subtitle, font_normal, font_small, font_tiny)
        
        pygame.display.flip()
        print("✓ Artwork generated successfully!")
    
    def _draw_statistics(self, screen, font_subtitle, font_normal, font_small, font_tiny):
        """Draw performance statistics"""
        x_left = 40
        y = 130
        
        # Header
        header = font_subtitle.render("Performance Metrics", True, (44, 62, 80))
        screen.blit(header, (x_left, y))
        y += 35
        
        # Separator line
        pygame.draw.line(screen, (149, 165, 166), (x_left, y), (x_left + 340, y), 2)
        y += 25
        
        # Part 1: Eye Tracking
        part1_title = font_normal.render("✦ PART 1: CALIBRATION", True, (52, 152, 219))
        screen.blit(part1_title, (x_left, y))
        y += 30
        
        accuracy_label = font_small.render("Eye Tracking Accuracy:", True, (44, 62, 80))
        screen.blit(accuracy_label, (x_left, y))
        y += 25
        
        # Color based on accuracy
        if self.tracking_accuracy >= 70:
            acc_color = (39, 174, 96)
        elif self.tracking_accuracy >= 50:
            acc_color = (243, 156, 18)
        else:
            acc_color = (231, 76, 60)
        
        accuracy_value = font_subtitle.render(f"{self.tracking_accuracy:.1f}%", True, acc_color)
        screen.blit(accuracy_value, (x_left, y))
        y += 35
        
        pattern_info = font_tiny.render(
            f"Pattern: {self.magic_circle.num_spokes} spokes, {self.magic_circle.num_layers} layers",
            True, (44, 62, 80)
        )
        screen.blit(pattern_info, (x_left, y))
        y += 40
        
        # Part 2: Aim Trainer
        part2_title = font_normal.render("✦ PART 2: FLOWER BLOOMS", True, (233, 30, 99))
        screen.blit(part2_title, (x_left, y))
        y += 30
        
        bloomed_count = sum(1 for f in self.flowers if f.bloomed)
        accuracy_pct = (bloomed_count / 12) * 100
        
        bloomed_label = font_small.render("Flowers Bloomed:", True, (44, 62, 80))
        screen.blit(bloomed_label, (x_left, y))
        y += 25
        
        # Color based on bloomed count
        if bloomed_count == 12:
            bloom_color = (39, 174, 96)
        elif bloomed_count >= 9:
            bloom_color = (243, 156, 18)
        else:
            bloom_color = (231, 76, 60)
        
        bloomed_value = font_subtitle.render(f"{bloomed_count}/12 ({accuracy_pct:.0f}%)", True, bloom_color)
        screen.blit(bloomed_value, (x_left, y))
        y += 35
        
        # Reaction times
        if self.reaction_times:
            avg_reaction = sum(self.reaction_times) / len(self.reaction_times)
            best_reaction = min(self.reaction_times)
            
            reaction_label = font_small.render("Avg Reaction Time:", True, (44, 62, 80))
            screen.blit(reaction_label, (x_left, y))
            y += 25
            
            if avg_reaction < 0.5:
                reaction_color = (39, 174, 96)
            elif avg_reaction < 0.8:
                reaction_color = (243, 156, 18)
            else:
                reaction_color = (231, 76, 60)
            
            reaction_value = font_subtitle.render(f"{avg_reaction:.3f}s", True, reaction_color)
            screen.blit(reaction_value, (x_left, y))
            y += 30
            
            best_label = font_tiny.render(f"Best: {best_reaction:.3f}s", True, (127, 140, 141))
            screen.blit(best_label, (x_left, y))
            y += 25
        
        # Overall assessment
        y += 15
        pygame.draw.line(screen, (149, 165, 166), (x_left, y), (x_left + 340, y), 1)
        y += 20
        
        assessment_title = font_normal.render("Overall Assessment:", True, (44, 62, 80))
        screen.blit(assessment_title, (x_left, y))
        y += 30
        
        # Determine assessment
        if bloomed_count == 12 and self.tracking_accuracy >= 70:
            assessment = "Outstanding!"
            assess_color = (39, 174, 96)
        elif bloomed_count >= 9 and self.tracking_accuracy >= 50:
            assessment = "Great Work!"
            assess_color = (52, 152, 219)
        elif bloomed_count >= 6:
            assessment = "Good Effort!"
            assess_color = (243, 156, 18)
        else:
            assessment = "Keep Practicing!"
            assess_color = (231, 76, 60)
        
        assessment_text = font_normal.render(assessment, True, assess_color)
        screen.blit(assessment_text, (x_left, y))


class ConcentrationArtGame:
    """Main game controller"""
    
    def __init__(self, player_id):
        """Initialize game"""
        self.player_id = player_id
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Concentration Art Game")
        self.eye_tracker = EyeTracker()
        
    def run(self):
        """Run the complete game"""
        print("=" * 60)
        print("🎨 CONCENTRATION ART GAME 🎨")
        print("=" * 60)
        print("Transform your focus into personalized artwork!")
        print()
        
        self.screen.fill(WHITE)
        
        # Part 1: Magic Circle
        self.magic_circle = MagicCircle(self.player_id)
        self.magic_circle.draw_animated(self.screen, self.eye_tracker)
        
        # Part 2: Flower Aim Trainer (flowers appear ON the magic circle)
        self.aim_trainer = FlowerAimTrainer(self.magic_circle.pattern_points, self.eye_tracker)
        self.aim_trainer.play(self.screen)
        
        # Part 3: Artistic Report
        self.report = ArtisticReport(
            self.player_id,
            self.magic_circle,
            self.aim_trainer.flowers,
            self.aim_trainer.reaction_times,
            self.eye_tracker
        )
        self.report.generate(self.screen)
        
        print("\n" + "=" * 60)
        print("Thank you for creating art with us! 🎨✨")
        print("=" * 60)
        
        # Keep window open
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
        pygame.quit()


def main():
    """Main entry point"""
    player_name = "Artist"
    game = ConcentrationArtGame(player_name)
    game.run()


if __name__ == "__main__":
    main()
