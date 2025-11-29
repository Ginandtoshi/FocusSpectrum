import pygame

class Scene:
    def __init__(self, manager):
        self.manager = manager
        self.next_scene = None # If set, manager will switch to this

    def handle_events(self, events):
        """Process pygame events (clicks, keys)"""
        pass

    def update(self):
        """Update game logic (movement, timers)"""
        pass

    def draw(self, screen):
        """Draw game elements. Background (camera) is already drawn."""
        pass

    def on_enter(self):
        """Called when scene becomes active"""
        pass

    def on_exit(self):
        """Called when scene is removed"""
        pass
