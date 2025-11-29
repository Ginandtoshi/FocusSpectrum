import cv2
import pygame
import numpy as np

class CameraManager:
    def __init__(self, width=1200, height=800):
        self.cap = cv2.VideoCapture(0)
        self.width = width
        self.height = height
        self.current_frame = None # Store the current frame (RGB)
        
        # Try to set camera resolution to match window, or close to it
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Mirror the frame (optional, usually feels better for user)
        frame = cv2.flip(frame, 1)
        
        # Resize to fit screen exactly if needed
        frame = cv2.resize(frame, (self.width, self.height))
        
        # Convert BGR (OpenCV) to RGB (Pygame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Store for other uses (e.g. MediaPipe)
        self.current_frame = frame
        
        # Rotate if needed (Pygame surfaces are (width, height), numpy is (height, width, depth))
        # Usually numpy -> pygame image needs a transpose if we want to do it manually, 
        # but pygame.image.frombuffer handles it.
        
        return frame

    def get_pygame_surface(self):
        frame = self.get_frame()
        if frame is None:
            return None
            
        # Create Pygame Surface
        # frame.shape[1] is width, frame.shape[0] is height
        return pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")

    def release(self):
        self.cap.release()
