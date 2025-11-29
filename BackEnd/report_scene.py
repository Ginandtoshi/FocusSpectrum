import pygame
import os
from scene_base import Scene

class ReportScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        
        # Load Fonts
        font_path = os.path.join(os.path.dirname(__file__), '..', 'Asset', 'Algerian Regular.ttf')
        try:
            self.title_font = pygame.font.Font(font_path, 50)
            self.header_font = pygame.font.Font(font_path, 36)
            self.text_font = pygame.font.Font(font_path, 24)
            self.small_font = pygame.font.Font(font_path, 18)
        except:
            self.title_font = pygame.font.SysFont("Arial", 50, bold=True)
            self.header_font = pygame.font.SysFont("Arial", 36, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 24)
            self.small_font = pygame.font.SysFont("Arial", 18)
            
        self.scores = self.manager.data.get("scores", {})
        self.calculate_distraction_scores()
        
        # Calculate background color based on overall distraction
        self.bg_color = self.get_spectrum_color(self.overall_distraction)
        
        self.exit_btn_rect = pygame.Rect(0, 0, 200, 50) # Will position in draw

    def calculate_distraction_scores(self):
        # --- Game 1: Plant (Attention) ---
        # Metric: Accuracy (Bloomed / 12)
        # 12/12 = 0 distraction, 6/12 = 5 distraction, 0/12 = 10 distraction
        g1_data = self.scores.get("game1", {})
        g1_score = g1_data.get("score", 0)
        # Invert score to get distraction (0-10)
        self.g1_distraction = (1.0 - (g1_score / 12.0)) * 10.0
        self.g1_distraction = max(0, min(10, self.g1_distraction))
        
        # --- Game 2: Metaball (Focus/Tracking) ---
        # Metric: Boundary Collisions & Score
        # Assume ~40-50 is a good score. 
        # Let's use collisions as primary distraction metric.
        # 0 collisions = 0 distraction. 10 collisions = 10 distraction.
        g2_data = self.scores.get("game2", {})
        g2_collisions = g2_data.get("collisions", 0)
        self.g2_distraction = min(10.0, g2_collisions * 1.0) 
        
        # --- Game 3: Text (Cognitive) ---
        # Metric: Eye Tracking Distraction % + Errors
        g3_data = self.scores.get("game3", {})
        g3_pct = g3_data.get("distraction_pct", 0)
        g3_errors = g3_data.get("errors", 0)
        
        # Map percentage (0-100) to 0-8 score, add errors
        self.g3_distraction = (g3_pct / 100.0) * 8.0 + (g3_errors * 0.5)
        self.g3_distraction = max(0, min(10, self.g3_distraction))
        
        # --- Overall ---
        self.overall_distraction = (self.g1_distraction + self.g2_distraction + self.g3_distraction) / 3.0

    def get_spectrum_color(self, value):
        """
        Maps 0-10 to Green -> Yellow -> Red
        0: Green (0, 255, 0)
        5: Yellow (255, 255, 0)
        10: Red (255, 0, 0)
        """
        value = max(0, min(10, value))
        
        if value <= 5:
            # Green to Yellow
            ratio = value / 5.0
            r = int(255 * ratio)
            g = 255
            b = 0
        else:
            # Yellow to Red
            ratio = (value - 5.0) / 5.0
            r = 255
            g = int(255 * (1 - ratio))
            b = 0
            
        return (r, g, b)

    def get_distraction_label(self, value):
        if value < 2:
            return "Not Distracted At All"
        elif value < 4:
            return "Mildly Distracted"
        elif value < 7:
            return "Moderately Distracted"
        else:
            return "Highly Distracted"

    def draw(self, screen):
        width, height = screen.get_size()
        
        # Draw Background (Spectrum Color with some transparency over black/camera)
        # Actually user asked for "report background as green... red"
        # Let's make it a solid fill or gradient overlay
        screen.fill(self.bg_color)
        
        # Add a dark overlay to make text readable
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("FOCUS SPECTRUM REPORT", True, (255, 255, 255))
        screen.blit(title, (width//2 - title.get_width()//2, 50))
        
        # Overall Score
        overall_label = self.get_distraction_label(self.overall_distraction)
        score_text = self.header_font.render(f"Overall Distraction Level: {self.overall_distraction:.1f}/10", True, (255, 255, 255))
        label_text = self.title_font.render(overall_label, True, (255, 255, 255))
        
        screen.blit(score_text, (width//2 - score_text.get_width()//2, 130))
        screen.blit(label_text, (width//2 - label_text.get_width()//2, 180))
        
        # Individual Game Panels
        panel_y = 280
        panel_width = 300
        panel_height = 250
        spacing = 50
        total_width = 3 * panel_width + 2 * spacing
        start_x = (width - total_width) // 2
        
        # Game 1 Panel
        self._draw_game_panel(screen, start_x, panel_y, panel_width, panel_height, 
                              "Game 1: Plant", self.g1_distraction, 
                              [f"Score: {self.scores.get('game1', {}).get('score', 0)}/12",
                               f"Misses: {self.scores.get('game1', {}).get('misses', 0)}"])
                               
        # Game 2 Panel
        self._draw_game_panel(screen, start_x + panel_width + spacing, panel_y, panel_width, panel_height,
                              "Game 2: Metaball", self.g2_distraction,
                              [f"Score: {self.scores.get('game2', {}).get('score', 0)}",
                               f"Collisions: {self.scores.get('game2', {}).get('collisions', 0)}"])
                               
        # Game 3 Panel
        self._draw_game_panel(screen, start_x + 2*(panel_width + spacing), panel_y, panel_width, panel_height,
                              "Game 3: Text", self.g3_distraction,
                              [f"Errors: {self.scores.get('game3', {}).get('errors', 0)}",
                               f"Eye Distraction: {self.scores.get('game3', {}).get('distraction_pct', 0):.1f}%"])

        # Exit Button
        self.exit_btn_rect.center = (width//2, height - 80)
        pygame.draw.rect(screen, (255, 255, 255), self.exit_btn_rect, 2, border_radius=10)
        btn_text = self.text_font.render("Back to Menu", True, (255, 255, 255))
        screen.blit(btn_text, (self.exit_btn_rect.centerx - btn_text.get_width()//2, 
                               self.exit_btn_rect.centery - btn_text.get_height()//2))

    def _draw_game_panel(self, screen, x, y, w, h, title, distraction, details):
        # Panel Background
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, (0, 0, 0, 150), rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=15)
        
        # Title
        title_surf = self.header_font.render(title, True, (255, 255, 255))
        screen.blit(title_surf, (x + w//2 - title_surf.get_width()//2, y + 20))
        
        # Distraction Bar
        bar_w = w - 40
        bar_h = 20
        bar_x = x + 20
        bar_y = y + 70
        
        # Draw gradient bar (simulated with segments)
        for i in range(bar_w):
            val = (i / bar_w) * 10
            color = self.get_spectrum_color(val)
            pygame.draw.line(screen, color, (bar_x + i, bar_y), (bar_x + i, bar_y + bar_h))
            
        # Indicator
        ind_x = bar_x + int((distraction / 10.0) * bar_w)
        pygame.draw.rect(screen, (255, 255, 255), (ind_x - 2, bar_y - 5, 4, bar_h + 10))
        
        score_surf = self.text_font.render(f"Distraction: {distraction:.1f}", True, (255, 255, 255))
        screen.blit(score_surf, (x + w//2 - score_surf.get_width()//2, bar_y + 30))
        
        # Details
        start_detail_y = bar_y + 70
        for i, detail in enumerate(details):
            detail_surf = self.small_font.render(detail, True, (200, 200, 200))
            screen.blit(detail_surf, (x + 30, start_detail_y + i * 25))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_btn_rect.collidepoint(event.pos):
                    from menu_scene import MenuScene
                    self.next_scene = MenuScene(self.manager)
