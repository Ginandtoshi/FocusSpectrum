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
        self.spacing = 40
        
        screen_width, screen_height = pygame.display.get_surface().get_size()
        center_x = screen_width // 2
        
        # Calculate layout for vertical centering
        # Content: Title (approx 70px) + Gap (50px) + 3 Buttons (3*100 + 2*40 = 380px)
        # Total Height = 70 + 50 + 380 = 500
        
        title_height = 70
        title_btn_gap = 50
        buttons_block_height = 3 * self.btn_height + 2 * self.spacing
        
        total_content_height = title_height + title_btn_gap + buttons_block_height
        
        start_y_offset = (screen_height - total_content_height) // 2
        
        self.title_y = start_y_offset
        btn_start_y = self.title_y + title_height + title_btn_gap
        
        self.btn_game1 = pygame.Rect(center_x - self.btn_width//2, btn_start_y, self.btn_width, self.btn_height)
        self.btn_game2 = pygame.Rect(center_x - self.btn_width//2, btn_start_y + self.btn_height + self.spacing, self.btn_width, self.btn_height)
        self.btn_game3 = pygame.Rect(center_x - self.btn_width//2, btn_start_y + 2*(self.btn_height + self.spacing), self.btn_width, self.btn_height)
        
        # Report Button (Placed below Game 3)
        self.btn_report = pygame.Rect(center_x - self.btn_width//2, btn_start_y + 3*(self.btn_height + self.spacing), self.btn_width, self.btn_height)

        # Sample Report Button (Small button at bottom)
        self.btn_sample = pygame.Rect(center_x - 100, screen_height - 60, 200, 40)

    def on_enter(self):
        print("Entering Menu Scene")

    def draw(self, screen):
        screen_width = screen.get_width()
        
        # Title
        title = self.title_font.render("Select a Game", True, (255, 255, 255))
        screen.blit(title, (screen_width//2 - title.get_width()//2, self.title_y))
        
        # Check completion status
        completed = self.manager.data.get("completed_games", [])
        
        # Draw Game 1 Button
        self._draw_button(screen, self.btn_game1, "Game 1: Blossom", "game1" in completed)
        
        # Draw Game 2 Button
        self._draw_button(screen, self.btn_game2, "Game 2: Metaball", "game2" in completed)

        # Draw Game 3 Button
        self._draw_button(screen, self.btn_game3, "Game 3: Letter", "game3" in completed)
        
        # Draw Report Button if all games completed
        if len(completed) >= 3: # Assuming 3 games
             self._draw_button(screen, self.btn_report, "VIEW FINAL REPORT", False, (255, 215, 0))

        # Draw Sample Report Button
        self._draw_sample_button(screen)

    def _draw_sample_button(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), self.btn_sample, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), self.btn_sample, 2, border_radius=10)
        text = self.font.render("See Sample Report", True, (200, 200, 200))
        # Scale down font for this small button
        small_text = pygame.transform.scale(text, (int(text.get_width() * 0.5), int(text.get_height() * 0.5)))
        screen.blit(small_text, (self.btn_sample.centerx - small_text.get_width()//2, self.btn_sample.centery - small_text.get_height()//2))

    def _draw_button(self, screen, rect, text, is_completed, override_color=None):
        # Grey out if completed, but still clickable (or user preference)
        # User said "stays grey".
        if is_completed:
            bg_color = (100, 100, 100)
            border_color = (150, 150, 150)
            text_color = (200, 200, 200)
            pygame.draw.rect(screen, bg_color, rect, border_radius=15)
        elif override_color:
            # Transparent background, colored border/text
            border_color = override_color
            text_color = override_color
        else:
            # Transparent background, white border/text
            border_color = (255, 255, 255)
            text_color = (255, 255, 255)
        
        # Draw Border
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
                elif self.btn_sample.collidepoint(event.pos):
                    # Define 3 sample datasets for different focus levels
                    samples = [
                        # 1. High Focus (> 70) - "Focus Achieved"
                        {
                            "game1": {"score": 10.5}, # ~87%
                            "game2": {"collisions": 2}, # 90%
                            "game3": {"distraction_pct": 5.0, "errors": 1} # 93%
                        },
                        # 2. Medium Focus (40-70) - "Stay Focused"
                        {
                            "game1": {"score": 6.0}, # 50%
                            "game2": {"collisions": 9}, # 55%
                            "game3": {"distraction_pct": 25.0, "errors": 5} # 65%
                        },
                        # 3. Low Focus (< 40) - "Need Focus"
                        {
                            "game1": {"score": 3.0}, # 25%
                            "game2": {"collisions": 16}, # 20%
                            "game3": {"distraction_pct": 50.0, "errors": 8} # 34%
                        }
                    ]
                    
                    # Get current index, default to 0
                    current_idx = self.manager.data.get("sample_index", 0)
                    
                    # Inject sample based on index
                    self.manager.data["scores"] = samples[current_idx]
                    
                    # Update index for next time (cycle 0 -> 1 -> 2 -> 0)
                    self.manager.data["sample_index"] = (current_idx + 1) % len(samples)
                    
                    from report_scene import ReportScene
                    self.next_scene = ReportScene(self.manager)
