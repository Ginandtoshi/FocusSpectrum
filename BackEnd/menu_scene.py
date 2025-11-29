import pygame
import os
from scene_base import Scene
# Imports are done inside methods to avoid circular imports if necessary, 
# but since we use next_scene class instantiation, we might need them at top or inside.
# Ideally, imports should be at top if no circular dependency. 
# Framework imports scenes, scenes import framework? No, scenes import scene_base.
# Scenes might import each other? Menu imports Game1/2. Game1/2 import Menu? 
# To be safe, I'll import inside the method or use string based imports if I had a factory, 
# but here I'll just import inside the event handler to be safe against circular deps with Framework if any.

class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        
        # Load Algerian Font
        font_path = os.path.join(os.path.dirname(__file__), '..', 'Asset', 'Algerian Regular.ttf')
        try:
            self.font = pygame.font.Font(font_path, 40)
            self.title_font = pygame.font.Font(font_path, 60)
        except:
            print("Font not found, using default")
            self.font = pygame.font.SysFont("Arial", 40)
            self.title_font = pygame.font.SysFont("Arial", 60)
        
        # Button definitions
        self.btn_width = 400
        self.btn_height = 100
        self.spacing = 40  # Reduced spacing slightly to ensure fit
        
        screen_width, screen_height = pygame.display.get_surface().get_size()
        center_x = screen_width // 2
        
        # Calculate total height for 4 buttons to ensure we have space
        # But center based on 3 buttons initially so it looks good before completion
        # We shift it up slightly so the 4th button fits comfortably
        total_btn_height_3 = 3 * self.btn_height + 2 * self.spacing
        
        # Center of the screen minus half the button group height
        # Shift up by 30px to allow room for the 4th button later
        start_y = (screen_height - total_btn_height_3) // 2 - 20
        
        self.btn_game1 = pygame.Rect(center_x - self.btn_width//2, start_y, self.btn_width, self.btn_height)
        self.btn_game2 = pygame.Rect(center_x - self.btn_width//2, start_y + self.btn_height + self.spacing, self.btn_width, self.btn_height)
        self.btn_game3 = pygame.Rect(center_x - self.btn_width//2, start_y + 2*(self.btn_height + self.spacing), self.btn_width, self.btn_height)
        
        # Report Button (Initially hidden or placed below)
        self.btn_report = pygame.Rect(center_x - self.btn_width//2, start_y + 3*(self.btn_height + self.spacing), self.btn_width, self.btn_height)

    def on_enter(self):
        print("Entering Menu Scene")

    def draw(self, screen):
        screen_width = screen.get_width()
        
        # Title
        title = self.title_font.render("Select a Game", True, (255, 255, 255))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 70))
        
        # Check completion status
        completed = self.manager.data.get("completed_games", [])
        
        # Draw Game 1 Button
        self._draw_button(screen, self.btn_game1, "Game 1: Plant", "game1" in completed)
        
        # Draw Game 2 Button
        self._draw_button(screen, self.btn_game2, "Game 2: Metaball", "game2" in completed)

        # Draw Game 3 Button
        self._draw_button(screen, self.btn_game3, "Game 3: Text", "game3" in completed)
        
        # Draw Report Button if all games completed
        if len(completed) >= 3: # Assuming 3 games
             self._draw_button(screen, self.btn_report, "VIEW FINAL REPORT", False, (255, 215, 0))

    def _draw_button(self, screen, rect, text, is_completed, override_color=None):
        # Grey out if completed, but still clickable (or user preference)
        # User said "stays grey".
        if is_completed:
            bg_color = (100, 100, 100)
            border_color = (150, 150, 150)
            text_color = (200, 200, 200)
        elif override_color:
            bg_color = override_color
            border_color = (255, 255, 255)
            text_color = (0, 0, 0)
        else:
            bg_color = (0, 150, 0)
            border_color = (255, 255, 255)
            text_color = (255, 255, 255)
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=15)
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=15)
        
        label = self.font.render(text, True, text_color)
        screen.blit(label, (rect.centerx - label.get_width()//2, rect.centery - label.get_height()//2))

    def handle_events(self, events):
        completed = self.manager.data.get("completed_games", [])
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_game1.collidepoint(event.pos):
                    from game.game1_Plant_MeiLam.Game01_Scene import Game1Scene
                    self.next_scene = Game1Scene(self.manager)
                elif self.btn_game2.collidepoint(event.pos):
                    from game.game2_Park_Yiwen.Game02_Scene import Game2Scene
                    self.next_scene = Game2Scene(self.manager)
                elif self.btn_game3.collidepoint(event.pos):
                    from game.game3_Text_Danyi.Game03_Scene import Game3Scene
                    self.next_scene = Game3Scene(self.manager)
                elif len(completed) >= 3 and self.btn_report.collidepoint(event.pos):
                    from report_scene import ReportScene
                    self.next_scene = ReportScene(self.manager)
