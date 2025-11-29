"""
Card Report Module - Dark gradient design with glowing waveform
"""

import pygame
import random
import math
from datetime import datetime


class CardReport:
    """Generate and display card-based reports with dark gradient and waveform"""
    
    def __init__(self, width=800, height=600, score=0):
        """Initialize the card report"""
        self.width = width
        self.height = height
        self.cards = []
        self.wave_offset = 0
        self.score = score
        self.button_rect = None
        self.button_hovered = False
        self.card_surface_for_save = None
        self.base_card_surface = None  # Cache static card elements
        
        # Generate random card number (001-999)
        self.card_number = str(random.randint(1, 999)).zfill(3)
        
        # Determine wave color based on score first
        self.wave_color = self._get_wave_color_by_score(score)
        
        # Choose random gradient colors for the card, avoiding colors similar to wave
        gradient_options = [
            # Grand Canyon - Orange to dark red
            [(255, 100, 50), (180, 60, 30), (100, 40, 20)],
            # Ocean - Blue to dark blue
            [(100, 180, 255), (50, 120, 200), (20, 60, 120)],
            # Purple - Light purple to dark purple
            [(200, 120, 255), (150, 80, 200), (100, 40, 150)],
            # Green - Light green to dark green
            [(120, 255, 150), (60, 180, 100), (30, 100, 60)],
            # Sunset - Pink to purple
            [(255, 150, 180), (200, 100, 150), (150, 50, 100)],
            # Amber - Yellow-orange to brown
            [(255, 200, 100), (200, 140, 60), (120, 80, 30)],
            # Teal - Cyan to dark teal
            [(100, 255, 220), (60, 180, 160), (30, 100, 100)],
            # Magenta - Bright pink to dark magenta
            [(255, 100, 200), (200, 60, 150), (120, 30, 90)],
        ]
        
        # Filter out gradients that are too similar to wave color
        if score < 20:
            # Wave is red - avoid red, orange, pink colors
            safe_gradients = [
                gradient_options[1],  # Ocean - Blue
                gradient_options[2],  # Purple
                gradient_options[3],  # Green
                gradient_options[6],  # Teal
            ]
        elif score < 40:
            # Wave is red-yellow - avoid red, orange colors
            safe_gradients = [
                gradient_options[1],  # Ocean - Blue
                gradient_options[2],  # Purple
                gradient_options[3],  # Green
                gradient_options[6],  # Teal
            ]
        elif score < 60:
            # Wave is yellow - avoid yellow, orange colors
            safe_gradients = [
                gradient_options[0],  # Grand Canyon - Orange/red
                gradient_options[1],  # Ocean - Blue
                gradient_options[2],  # Purple
                gradient_options[6],  # Teal
                gradient_options[7],  # Magenta
            ]
        elif score < 80:
            # Wave is yellow-green - avoid green, yellow colors
            safe_gradients = [
                gradient_options[0],  # Grand Canyon - Orange/red
                gradient_options[1],  # Ocean - Blue
                gradient_options[2],  # Purple
                gradient_options[4],  # Sunset - Pink
                gradient_options[7],  # Magenta
            ]
        else:
            # Wave is green - avoid green colors
            safe_gradients = [
                gradient_options[0],  # Grand Canyon - Orange/red
                gradient_options[1],  # Ocean - Blue
                gradient_options[2],  # Purple
                gradient_options[4],  # Sunset - Pink
                gradient_options[5],  # Amber
                gradient_options[7],  # Magenta
            ]
        
        self.gradient_colors = random.choice(safe_gradients)
        
        # Choose random geometric pattern
        self.pattern_type = random.choice([
            'diagonal_stripes',
            'vertical_bars', 
            'chevron',
            'cross',
            'zigzag',
            'triangles',
            'waves',
            'grid'
        ])
    
    def _get_wave_color_by_score(self, score):
        """Get wave color gradient based on score (0-100)"""
        if score == 100:
            # Perfect score - Bright green gradient (very strong contrast)
            return [(230, 255, 230), (100, 255, 100), (30, 150, 30)]
        elif score >= 80:
            # High score - Green gradient
            return [(220, 255, 200), (120, 255, 120), (40, 180, 40)]
        elif score >= 60:
            # Medium-high score - Yellow to Green gradient
            return [(255, 255, 150), (200, 255, 100), (80, 200, 50)]
        elif score >= 40:
            # Medium score - Yellow gradient
            return [(255, 255, 200), (255, 255, 100), (180, 180, 40)]
        elif score >= 20:
            # Low-medium score - Red to Yellow gradient
            return [(255, 255, 150), (255, 200, 80), (255, 80, 40)]
        else:
            # Low score - Red gradient
            return [(255, 200, 200), (255, 100, 100), (180, 30, 30)]
    
    def add_card(self, title, content, color=(255, 255, 255)):
        """Add a card to the report"""
        card = {
            'title': title,
            'content': content,
            'color': color
        }
        self.cards.append(card)
    
    def draw_gradient_background(self, screen):
        """Draw simple dark background"""
        screen.fill((15, 20, 40))  # Dark navy blue
    
    def draw_waveform(self, screen):
        """Placeholder - waveform removed"""
        pass
    
    def _draw_geometric_pattern(self, width, height, base_color):
        """Draw unique geometric pattern on card surface"""
        # Create pattern surface with transparency
        pattern_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Get lighter version of base color for pattern
        pattern_color = tuple(min(255, int(c * 1.2)) for c in base_color[:3]) + (40,)
        
        if self.pattern_type == 'diagonal_stripes':
            # Diagonal stripes from top-left to bottom-right
            stripe_width = 40
            for i in range(-height, width, stripe_width * 2):
                points = [(i, 0), (i + stripe_width, 0), 
                         (i + stripe_width + height, height), (i + height, height)]
                pygame.draw.polygon(pattern_surface, pattern_color, points)
        
        elif self.pattern_type == 'vertical_bars':
            # Vertical bars of varying widths
            x = 0
            while x < width:
                bar_width = random.randint(30, 80)
                pygame.draw.rect(pattern_surface, pattern_color, 
                               (x, 0, bar_width, height))
                x += bar_width + random.randint(20, 60)
        
        elif self.pattern_type == 'chevron':
            # Chevron/arrow pattern pointing down
            chevron_height = 60
            y = -30
            while y < height:
                points = [
                    (0, y), (width//2, y + chevron_height),
                    (width, y), (width, y - 20),
                    (width//2, y + chevron_height - 20), (0, y - 20)
                ]
                pygame.draw.polygon(pattern_surface, pattern_color, points)
                y += chevron_height
        
        elif self.pattern_type == 'cross':
            # Cross/plus pattern
            bar_width = 60
            # Vertical bars
            for x in range(bar_width, width, bar_width * 3):
                pygame.draw.rect(pattern_surface, pattern_color,
                               (x, 0, bar_width, height))
            # Horizontal bars
            for y in range(bar_width, height, bar_width * 3):
                pygame.draw.rect(pattern_surface, pattern_color,
                               (0, y, width, bar_width))
        
        elif self.pattern_type == 'zigzag':
            # Zigzag vertical lines
            line_spacing = 50
            zigzag_width = 30
            for x in range(0, width, line_spacing):
                points = []
                y = 0
                direction = 1
                while y < height:
                    points.append((x + direction * zigzag_width, y))
                    y += 40
                    direction *= -1
                if len(points) > 1:
                    pygame.draw.lines(pattern_surface, pattern_color, False, points, 15)
        
        elif self.pattern_type == 'triangles':
            # Triangular pattern
            tri_size = 80
            for y in range(0, height + tri_size, tri_size):
                for x in range(0, width + tri_size, tri_size):
                    if random.random() > 0.5:
                        points = [(x, y), (x + tri_size, y), (x + tri_size//2, y + tri_size)]
                    else:
                        points = [(x, y + tri_size), (x + tri_size, y + tri_size), (x + tri_size//2, y)]
                    pygame.draw.polygon(pattern_surface, pattern_color, points)
        
        elif self.pattern_type == 'waves':
            # Wavy horizontal lines
            wave_count = 8
            for i in range(wave_count):
                y_base = (height // wave_count) * i + 30
                points = []
                for x in range(0, width + 10, 10):
                    y = y_base + math.sin(x * 0.05 + i) * 20
                    points.append((x, y))
                if len(points) > 1:
                    pygame.draw.lines(pattern_surface, pattern_color, False, points, 12)
        
        elif self.pattern_type == 'grid':
            # Grid pattern with varying opacity
            grid_size = 50
            for x in range(0, width, grid_size):
                pygame.draw.line(pattern_surface, pattern_color, 
                               (x, 0), (x, height), 3)
            for y in range(0, height, grid_size):
                pygame.draw.line(pattern_surface, pattern_color,
                               (0, y), (width, y), 3)
        
        return pattern_surface
    
    def _create_base_card(self, card_width, card_height):
        """Create the static base card with gradient and pattern (called once)"""
        # Create card surface with gradient background
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        
        # Create a temporary surface for the gradient with black background
        gradient_surface = pygame.Surface((card_width, card_height))
        gradient_surface.fill((0, 0, 0))  # Fill with black
        
        # Vertical gradient: Use random colors
        gradient_colors = self.gradient_colors
        for y in range(card_height):
            progress = y / card_height
            if progress < 0.5:
                t = progress * 2
                color = tuple(int(gradient_colors[0][j] * (1-t) + gradient_colors[1][j] * t) for j in range(3))
            else:
                t = (progress - 0.5) * 2
                color = tuple(int(gradient_colors[1][j] * (1-t) + gradient_colors[2][j] * t) for j in range(3))
            pygame.draw.line(gradient_surface, color, (0, y), (card_width, y))
        
        # Create a mask with rounded corners
        mask_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), 
                        (0, 0, card_width, card_height),
                        border_radius=20)
        
        # Apply the gradient to card surface with rounded corners
        gradient_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        card_surface.blit(gradient_surface, (0, 0))
        
        # Add unique geometric pattern overlay
        pattern_overlay = self._draw_geometric_pattern(card_width, card_height, gradient_colors[1])
        card_surface.blit(pattern_overlay, (0, 0))
        
        return card_surface
    
    def draw(self, screen):
        """Draw all cards on the screen"""
        # Draw simple dark background
        screen.fill((0, 0, 0))  # Black background
        
        # Get current screen dimensions (in case of window resize)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Draw single large vertical card in center
        card_width = 350
        card_height = 500
        
        # Center the card on screen - force center positioning
        card_x = (screen_width - card_width) // 2
        card_y = (screen_height - card_height) // 2
        
        # Create base card once and cache it
        if self.base_card_surface is None:
            self.base_card_surface = self._create_base_card(card_width, card_height)
        
        # Copy the static base card
        card_surface = self.base_card_surface.copy()
        
        # Add waveform visualization in center of card
        waveform_center_x = card_width // 2
        waveform_center_y = card_height // 2
        
        # Get wave color gradient based on score
        wave_gradient = self.wave_color
        
        # Draw glowing waveform with smooth wave pattern
        # Create many vertical bars that create a smooth sine wave
        num_bars = 25
        bars = []
        
        for i in range(num_bars):
            # Position bars evenly across width
            x_pos = -120 + (i * 240 // (num_bars - 1))
            
            # Calculate wave height based on position (sine wave)
            wave_position = (i / num_bars) * 2 * math.pi
            base_height = 30 + abs(math.sin(wave_position)) * 40
            
            # Width based on distance from edges
            center_distance = abs(x_pos) / 120
            base_width = 50 - (center_distance * 25)
            
            # Create gradient colors across the wave
            # Edges use first color, center uses transition to third color
            position_ratio = (i / (num_bars - 1))  # 0 to 1 from left to right
            
            if position_ratio < 0.25:
                # Far left - use first color (edge)
                color = wave_gradient[0]
            elif position_ratio < 0.5:
                # Left to center - blend from color[0] to color[1]
                t = (position_ratio - 0.25) / 0.25
                color = tuple(
                    int(wave_gradient[0][j] * (1-t) + wave_gradient[1][j] * t) 
                    for j in range(3)
                )
            elif position_ratio < 0.75:
                # Center to right - blend from color[1] to color[2]
                t = (position_ratio - 0.5) / 0.25
                color = tuple(
                    int(wave_gradient[1][j] * (1-t) + wave_gradient[2][j] * t) 
                    for j in range(3)
                )
            else:
                # Far right - use third color (edge)
                color = wave_gradient[2]
            
            alpha_mult = 0.7 + (1 - center_distance) * 0.3
            phase = i * 360 // num_bars
            
            bars.append((x_pos, base_width, base_height, color, alpha_mult, phase))
        
        # Animate bars with wave offset
        for x_base, w_base, h_base, color, alpha_mult, phase in bars:
            # Calculate animated dimensions with traveling wave
            angle = (self.wave_offset + phase) % 360
            w = w_base + abs(math.sin(math.radians(angle))) * 8
            h = h_base + math.sin(math.radians(angle)) * 25
            
            # Vertical position follows wave
            y_offset = math.sin(math.radians(angle)) * 5
            
            # Draw bars with glow
            for glow in range(3, 0, -1):
                alpha = int((200 - glow * 50) * alpha_mult)
                glow_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                
                # Create vertical bar
                bar_rect = pygame.Rect(
                    waveform_center_x + x_base - (w * glow * 0.6) // 2,
                    waveform_center_y + y_offset - (h * glow) // 2,
                    w * glow * 0.6,
                    max(h * glow, 10)
                )
                
                glow_color = (*color, alpha)
                pygame.draw.ellipse(glow_surface, glow_color, bar_rect)
                card_surface.blit(glow_surface, (0, 0))
        
        # Update wave animation
        self.wave_offset = (self.wave_offset + 5) % 360
        
        # === FONT SETUP - Use consistent font for all numbers ===
        number_font_large = pygame.font.Font(None, 72)  # For score value
        number_font_medium = pygame.font.Font(None, 40)  # For card number
        number_font_small = pygame.font.Font(None, 32)   # For date numbers
        label_font = pygame.font.Font(None, 24)          # For labels
        
        # === TOP SECTION: Score and Number ===
        # Draw score in top left with label
        score_label = label_font.render("SCORE", True, (200, 200, 200, 180))
        card_surface.blit(score_label, (25, 25))
        
        score_value = number_font_large.render(str(self.score), True, (255, 255, 255, 220))
        card_surface.blit(score_value, (25, 45))
        
        # Draw card number in top right
        number_label = pygame.font.Font(None, 20).render("No.", True, (200, 200, 200, 180))
        card_surface.blit(number_label, (card_width - 65, 25))
        
        number_text = number_font_medium.render(self.card_number, True, (255, 255, 255, 200))
        card_surface.blit(number_text, (card_width - 75, 45))
        
        # === BOTTOM SECTION: Date and Time ===
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")  # e.g., "November 29, 2025"
        time_str = now.strftime("%I:%M %p")    # e.g., "02:30 PM"
        
        # Draw date
        date_text = number_font_small.render(date_str, True, (220, 220, 220))
        date_rect = date_text.get_rect()
        date_rect.left = 35
        date_rect.top = card_height - 70
        card_surface.blit(date_text, date_rect)
        
        # Draw time
        time_text = pygame.font.Font(None, 28).render(time_str, True, (180, 180, 180, 200))
        time_rect = time_text.get_rect()
        time_rect.left = 35
        time_rect.top = card_height - 35
        card_surface.blit(time_text, time_rect)
        
        # Draw rounded border
        pygame.draw.rect(card_surface, (255, 255, 255, 100), 
                       (0, 0, card_width, card_height),
                       width=3, border_radius=20)
        
        screen.blit(card_surface, (card_x, card_y))
        
        # Store card surface for downloading
        self.card_surface_for_save = card_surface.copy()
        
        # Draw modern download button below the card
        button_width = 280
        button_height = 70
        button_margin = 40
        button_x = (screen_width - button_width) // 2
        button_y = card_y + card_height + button_margin
        
        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Modern glass-morphism button design
        if self.button_hovered:
            # Hover state - glass effect with glow
            bg_alpha = 180
            border_alpha = 220
            glow_radius = 25
            text_color = (255, 255, 255)
            icon_scale = 1.1
        else:
            # Normal state - subtle glass
            bg_alpha = 140
            border_alpha = 180
            glow_radius = 15
            text_color = (245, 245, 245)
            icon_scale = 1.0
        
        # Draw outer glow effect
        for i in range(glow_radius, 0, -2):
            alpha = int((bg_alpha * 0.3) * (1 - i / glow_radius))
            glow_surface = pygame.Surface((button_width + i*2, button_height + i*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (80, 160, 255, alpha), 
                           (0, 0, button_width + i*2, button_height + i*2), 
                           border_radius=20)
            screen.blit(glow_surface, (button_x - i, button_y - i))
        
        # Main button surface with frosted glass effect
        button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        
        # Background with gradient
        for i in range(button_height):
            progress = i / button_height
            # Subtle gradient from lighter to darker
            color_top = (70, 150, 250, bg_alpha)
            color_bottom = (50, 120, 220, bg_alpha)
            r = int(color_top[0] * (1-progress) + color_bottom[0] * progress)
            g = int(color_top[1] * (1-progress) + color_bottom[1] * progress)
            b = int(color_top[2] * (1-progress) + color_bottom[2] * progress)
            a = int(color_top[3] * (1-progress) + color_bottom[3] * progress)
            pygame.draw.line(button_surface, (r, g, b, a), (0, i), (button_width, i))
        
        # Add frosted glass shine at top
        shine_height = button_height // 2
        for i in range(shine_height):
            alpha = int(50 * (1 - i / shine_height))
            pygame.draw.line(button_surface, (255, 255, 255, alpha), 
                           (10, i + 5), (button_width - 10, i + 5))
        
        # Rounded corners mask
        mask = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, button_width, button_height), border_radius=20)
        button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Multi-layer border for depth
        # Outer bright border
        pygame.draw.rect(button_surface, (150, 210, 255, border_alpha), 
                        (0, 0, button_width, button_height), width=3, border_radius=20)
        # Inner subtle border
        pygame.draw.rect(button_surface, (255, 255, 255, 100), 
                        (2, 2, button_width-4, button_height-4), width=1, border_radius=18)
        
        screen.blit(button_surface, (button_x, button_y))
        
        # Draw text and icon with clean styling
        text_size = 36
        text_font = pygame.font.Font(None, text_size)
        
        # Render "DOWNLOAD" text
        text_string = "DOWNLOAD"
        text = text_font.render(text_string, True, text_color)
        text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        
        # Add subtle text shadow for depth
        text_shadow = text_font.render(text_string, True, (0, 0, 0, 80))
        screen.blit(text_shadow, (text_rect.x + 1, text_rect.y + 2))
        screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def save_card(self):
        """Save the card as a PNG image"""
        if self.card_surface_for_save:
            # Create saves directory if it doesn't exist
            import os
            save_dir = "card_saves"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Generate filename with timestamp and card number
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{save_dir}/card_{self.card_number}_{timestamp}.png"
            
            # Save the card surface
            pygame.image.save(self.card_surface_for_save, filename)
            print(f"Card saved as: {filename}")
            return filename
        return None
    
    def run(self, screen):
        """Run the card report display"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Check mouse hover
            mouse_pos = pygame.mouse.get_pos()
            if self.button_rect and self.button_rect.collidepoint(mouse_pos):
                self.button_hovered = True
            else:
                self.button_hovered = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.button_rect and self.button_rect.collidepoint(event.pos):
                            saved_file = self.save_card()
                            if saved_file:
                                print(f"✓ Card downloaded successfully!")
            
            self.draw(screen)
            clock.tick(60)


if __name__ == '__main__':
    # Example usage - Cycle through different scores to see all colors
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Card Report - Heritage of the Earth")
    
    # Get actual screen dimensions
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Test different scores to see all wave colors
    test_scores = [
        (100, "Perfect - Bright Green"),
        (85, "High Score - Green"),
        (65, "Medium-High - Yellow-Green"),
        (45, "Medium - Yellow"),
        (25, "Low-Medium - Orange"),
        (10, "Low - Red")
    ]
    
    for score, description in test_scores:
        print(f"\n{'='*50}")
        print(f"Score: {score} - {description}")
        
        report = CardReport(width=screen_width, height=screen_height, score=score)
        report.add_card("Park", "Grand Canyon")
        print(f"Wave color RGB: {report.wave_color}")
        print("Close the window to see the next color...")
        
        report.run(screen)
    
    pygame.quit()
    print("\nAll colors tested!")
