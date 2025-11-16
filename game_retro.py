"""
1-A-2-B 交替排序游戏 - 复古音频设备风格
参考 retro_ui.py 的视觉设计
红色背景 + 黑色面板 + 复古科技感
"""

import pygame
import sys
import random
import math
from typing import List, Tuple

# ==================== 初始化 ====================
pygame.init()
pygame.font.init()

# ==================== 配色方案 (参考 retro_ui.py) ====================
class RetroColors:
    # 主背景和面板
    BG = (217, 44, 10)  # 红色背景 '#d92c0a'
    PANEL_BG = (0, 0, 0)  # 黑色面板 '#000000'
    
    # 文字颜色
    TEXT = (224, 224, 224)  # 米色文字 '#e0e0e0'
    TEXT_DIM = (160, 160, 160)  # 暗淡文字
    
    # 强调色
    ACCENT_RED = (244, 67, 54)  # '#f44336'
    ACCENT_BLUE = (33, 150, 243)  # '#2196F3'
    ACCENT_TAN = (210, 180, 140)  # '#d2b48c'
    
    # 面板元素
    WAVEFORM_BG = (173, 181, 189)  # 波形背景 '#adb5bd'
    WAVEFORM_LINE = (33, 37, 41)  # 波形线条 '#212529'
    GRID = (224, 224, 224, 40)  # 网格线
    
    # 游戏状态颜色
    ACTIVE = (255, 200, 100)  # 当前目标
    COMPLETED = (100, 180, 120)  # 已完成
    DISABLED = (80, 80, 80)  # 未激活

# ==================== 配置 ====================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MAX_TARGET = 10
SNAP_RADIUS = 50

# 面板布局
PANEL_MARGIN = 15
SLOT_PANEL_WIDTH = 280
SLOT_PANEL_X = PANEL_MARGIN
SLOT_PANEL_Y = 80
SLOT_PANEL_HEIGHT = SCREEN_HEIGHT - SLOT_PANEL_Y - PANEL_MARGIN

# 干扰词
DISTRACTOR_WORDS = [
    "apple", "house", "play", "see", "run", "the", "it", "me", "you",
    "sky", "red", "blue", "code", "game", "happy", "sad", "work",
    "time", "day", "night", "sun", "moon", "star", "tree", "river",
    "road", "car", "dog", "cat", "bird", "fish", "walk", "jump"
]

# ==================== 磁铁类 ====================
class Magnet:
    def __init__(self, x: float, y: float, value: str, font: pygame.font.Font):
        self.value = value
        self.pos = pygame.math.Vector2(x, y)
        self.is_locked = False
        self.font = font
        
        text_surf = font.render(value, True, RetroColors.TEXT)
        text_rect = text_surf.get_rect()
        self.width = text_rect.width + 28
        self.height = text_rect.height + 16
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.pos
        
        self.hover_scale = 1.0
        self.glow_alpha = 0
    
    def update(self, mouse_pos: Tuple[int, int], is_selected: bool):
        if not self.is_locked:
            if is_selected:
                target_scale = 1.08
                self.glow_alpha = min(255, self.glow_alpha + 20)
            elif self.contains(mouse_pos):
                target_scale = 1.04
                self.glow_alpha = min(120, self.glow_alpha + 15)
            else:
                target_scale = 1.0
                self.glow_alpha = max(0, self.glow_alpha - 15)
            
            self.hover_scale += (target_scale - self.hover_scale) * 0.2
    
    def draw(self, screen: pygame.Surface, is_selected: bool):
        scaled_rect = self.rect.copy()
        if self.hover_scale != 1.0:
            scaled_rect.width = int(self.width * self.hover_scale)
            scaled_rect.height = int(self.height * self.hover_scale)
            scaled_rect.center = self.rect.center
        
        # 发光效果
        if self.glow_alpha > 0:
            glow_surf = pygame.Surface((scaled_rect.width + 12, scaled_rect.height + 12), pygame.SRCALPHA)
            glow_rect = glow_surf.get_rect()
            pygame.draw.rect(glow_surf, (*RetroColors.ACCENT_TAN, int(self.glow_alpha * 0.4)), 
                           glow_rect, border_radius=3)
            screen.blit(glow_surf, (scaled_rect.x - 6, scaled_rect.y - 6))
        
        # 背景和边框
        if self.is_locked:
            bg_color = RetroColors.PANEL_BG
            border_color = RetroColors.COMPLETED
            text_color = RetroColors.COMPLETED
        elif is_selected:
            bg_color = (40, 40, 40)
            border_color = RetroColors.ACCENT_TAN
            text_color = RetroColors.ACCENT_TAN
        else:
            bg_color = RetroColors.PANEL_BG
            border_color = RetroColors.TEXT_DIM
            text_color = RetroColors.TEXT
        
        pygame.draw.rect(screen, bg_color, scaled_rect, border_radius=3)
        pygame.draw.rect(screen, border_color, scaled_rect, 2, border_radius=3)
        
        # 网格纹理
        if not self.is_locked:
            for i in range(0, scaled_rect.width, 4):
                pygame.draw.line(screen, (border_color[0]//4, border_color[1]//4, border_color[2]//4),
                               (scaled_rect.x + i, scaled_rect.y),
                               (scaled_rect.x + i, scaled_rect.bottom), 1)
        
        # 文字
        text_surf = self.font.render(self.value, True, text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)
    
    def contains(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)
    
    def update_position(self, pos: Tuple[float, float]):
        self.pos = pygame.math.Vector2(pos)
        self.rect.center = self.pos


# ==================== 槽位类 ====================
class TargetSlot:
    def __init__(self, pos: pygame.math.Vector2, value: str, index: int, font: pygame.font.Font):
        self.pos = pos
        self.value = value
        self.index = index
        self.font = font
        
        text_surf = font.render(value, True, RetroColors.TEXT)
        text_rect = text_surf.get_rect()
        self.width = text_rect.width + 32
        self.height = text_rect.height + 18
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = pos
        
        self.pulse = 0
    
    def draw(self, screen: pygame.Surface, current_index: int, time_ms: int):
        if self.index < current_index:
            # 已完成
            bg_color = (10, 35, 10)
            border_color = RetroColors.COMPLETED
            text_color = RetroColors.COMPLETED
        elif self.index == current_index:
            # 当前目标 - 脉冲效果
            pulse = (math.sin(time_ms * 0.004) + 1) / 2
            self.pulse = pulse
            intensity = int(30 + pulse * 40)
            bg_color = (intensity, intensity//2, 0)
            border_color = RetroColors.ACCENT_TAN
            text_color = RetroColors.ACCENT_TAN
        else:
            # 未来
            bg_color = RetroColors.PANEL_BG
            border_color = RetroColors.TEXT_DIM
            text_color = RetroColors.TEXT_DIM
        
        # 背景
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=2)
        
        # 边框
        border_width = 2
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=2)
        
        # 点阵网格（未完成时）
        if self.index >= current_index:
            grid_color = (border_color[0]//3, border_color[1]//3, border_color[2]//3)
            for i in range(self.rect.left + 6, self.rect.right, 6):
                for j in range(self.rect.top + 6, self.rect.bottom, 6):
                    pygame.draw.circle(screen, grid_color, (i, j), 1)
        
        # 目标文字
        text_surf = self.font.render(self.value, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


# ==================== UI 组件 ====================
def draw_panel_border(screen, rect, color, width=2):
    """绘制面板边框 - retro_ui风格"""
    pygame.draw.rect(screen, color, rect, width)


def draw_progress_display(screen, current, total, font, pos):
    """绘制进度显示器（类似计数器）"""
    x, y = pos
    width, height = 200, 60
    rect = pygame.Rect(x, y, width, height)
    
    # 外框
    pygame.draw.rect(screen, RetroColors.PANEL_DARK, rect, border_radius=6)
    pygame.draw.rect(screen, RetroColors.RED_BORDER, rect, 2, border_radius=6)
    
    # 数字显示（LED风格）
    progress_text = f"{current:02d}/{total:02d}"
    text_surf = font.render(progress_text, True, RetroColors.LED_CYAN)
    text_rect = text_surf.get_rect(center=rect.center)
    
    # 数字发光效果
    glow_surf = font.render(progress_text, True, (RetroColors.LED_CYAN[0]//3, 
                                                    RetroColors.LED_CYAN[1]//3, 
                                                    RetroColors.LED_CYAN[2]//3))
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        screen.blit(glow_surf, (text_rect.x + dx, text_rect.y + dy))
    
    screen.blit(text_surf, text_rect)
    
    # 标签
    label = font.render("PROGRESS", True, RetroColors.TEXT_GRAY)
    screen.blit(label, (x + 5, y - 18))


# ==================== 游戏主类 ====================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SEQUENCE SORTER - RETRO EDITION")
        self.clock = pygame.time.Clock()
        
        # 字体 - 使用等宽字体增强科技感
        self.magnet_font = pygame.font.SysFont('Consolas', 18, bold=True)
        self.slot_font = pygame.font.SysFont('Consolas', 20, bold=True)
        self.ui_font = pygame.font.SysFont('Consolas', 16, bold=True)
        self.title_font = pygame.font.SysFont('Consolas', 32, bold=True)
        self.counter_font = pygame.font.SysFont('Consolas', 28, bold=True)
        
        self.running = True
        self.initialize_game()
    
    def initialize_game(self):
        self.magnets = []
        self.slots = []
        self.current_target_index = 0
        self.selected_magnet = None
        self.drag_offset = pygame.math.Vector2(0, 0)
        self.game_won = False
        self.win_time = 0
        
        # 生成目标序列
        target_sequence = []
        for i in range(1, MAX_TARGET + 1):
            target_sequence.append(str(i))
            target_sequence.append(chr(64 + i))  # 'A' 是 65
        
        # 创建槽位 - 调整布局避免挤压
        slot_count = len(target_sequence)
        slot_area_top = 150  # 槽位区域顶部
        slot_area_bottom = SCREEN_HEIGHT - 50  # 槽位区域底部
        available_height = slot_area_bottom - slot_area_top
        slot_spacing = available_height / (slot_count - 1)  # 改为 slot_count - 1
        
        for i, value in enumerate(target_sequence):
            pos = pygame.math.Vector2(130, slot_area_top + i * slot_spacing)
            self.slots.append(TargetSlot(pos, value, i, self.slot_font))
        
        # 创建单词 - 确保包含所有目标单词
        words = target_sequence.copy()  # 包含所有数字和字母
        distractor_count = int(len(target_sequence) * 1.2)
        words.extend(random.choices(DISTRACTOR_WORDS, k=distractor_count))
        random.shuffle(words)
        
        # 磁铁生成区域 - 右侧更宽敞
        spawn_x_range = (SCREEN_WIDTH * 0.30, SCREEN_WIDTH * 0.92)
        spawn_y_range = (150, SCREEN_HEIGHT - 50)
        
        # 使用网格布局避免重叠
        grid_cols = 8
        grid_rows = (len(words) + grid_cols - 1) // grid_cols
        cell_width = (spawn_x_range[1] - spawn_x_range[0]) / grid_cols
        cell_height = (spawn_y_range[1] - spawn_y_range[0]) / grid_rows
        
        positions = []
        for i in range(len(words)):
            col = i % grid_cols
            row = i // grid_cols
            # 在网格单元内随机偏移
            x = spawn_x_range[0] + col * cell_width + random.uniform(10, cell_width - 10)
            y = spawn_y_range[0] + row * cell_height + random.uniform(10, cell_height - 10)
            positions.append((x, y))
        
        # 随机打乱位置
        random.shuffle(positions)
        
        for i, word in enumerate(words):
            x, y = positions[i]
            self.magnets.append(Magnet(x, y, word, self.magnet_font))
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R 键重置
                    self.initialize_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_won:
                    continue
                
                for magnet in reversed(self.magnets):
                    if not magnet.is_locked and magnet.contains(mouse_pos):
                        self.selected_magnet = magnet
                        self.drag_offset = magnet.pos - pygame.math.Vector2(mouse_pos)
                        self.magnets.remove(magnet)
                        self.magnets.append(magnet)
                        break
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.selected_magnet:
                    self.try_snap_magnet()
                    self.selected_magnet = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.selected_magnet:
                    new_pos = pygame.math.Vector2(mouse_pos) + self.drag_offset
                    self.selected_magnet.update_position(new_pos)
    
    def try_snap_magnet(self):
        if not self.selected_magnet or self.current_target_index >= len(self.slots):
            return
        
        current_slot = self.slots[self.current_target_index]
        
        if self.selected_magnet.value != current_slot.value:
            return
        
        distance = self.selected_magnet.pos.distance_to(current_slot.pos)
        if distance < SNAP_RADIUS:
            self.selected_magnet.update_position(current_slot.pos)
            self.selected_magnet.is_locked = True
            self.current_target_index += 1
            
            if self.current_target_index >= len(self.slots):
                self.game_won = True
                self.win_time = pygame.time.get_ticks()
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for magnet in self.magnets:
            magnet.update(mouse_pos, magnet == self.selected_magnet)
        
        if self.game_won:
            elapsed = pygame.time.get_ticks() - self.win_time
            if elapsed > 5000:
                self.initialize_game()
    
    def draw(self):
        # 红色背景 - retro_ui风格
        self.screen.fill(RetroColors.BG)
        
        # 顶部标题面板
        title_panel = pygame.Rect(PANEL_MARGIN, PANEL_MARGIN, 
                                 SCREEN_WIDTH - 2*PANEL_MARGIN, 80)
        pygame.draw.rect(self.screen, RetroColors.PANEL_BG, title_panel)
        draw_panel_border(self.screen, title_panel, RetroColors.ACCENT_RED, 3)
        
        # 标题文字
        title_text = self.title_font.render("SEQUENCE SORTER", True, RetroColors.TEXT)
        title_rect = title_text.get_rect(center=(title_panel.centerx, title_panel.centery - 10))
        self.screen.blit(title_text, title_rect)
        
        subtitle = self.ui_font.render("1-A-2-B-3-C...10-J", True, RetroColors.TEXT_DIM)
        subtitle_rect = subtitle.get_rect(center=(title_panel.centerx, title_panel.centery + 18))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 左侧槽位面板
        slot_panel = pygame.Rect(PANEL_MARGIN, 115, 
                                SLOT_PANEL_WIDTH, SCREEN_HEIGHT - 130)
        pygame.draw.rect(self.screen, RetroColors.PANEL_BG, slot_panel)
        draw_panel_border(self.screen, slot_panel, RetroColors.ACCENT_BLUE, 3)
        
        # 槽位面板标题
        panel_label = self.ui_font.render("TARGET SEQUENCE", True, RetroColors.TEXT)
        self.screen.blit(panel_label, (slot_panel.x + 10, slot_panel.y + 10))
        
        # 进度信息
        progress_text = self.ui_font.render(f"{self.current_target_index}/{len(self.slots)}", 
                                           True, RetroColors.ACCENT_TAN)
        self.screen.blit(progress_text, (slot_panel.right - 70, slot_panel.y + 10))
        
        # 绘制槽位
        current_time = pygame.time.get_ticks()
        for slot in self.slots:
            slot.draw(self.screen, self.current_target_index, current_time)
        
        # 右侧磁铁面板
        magnet_panel = pygame.Rect(SLOT_PANEL_WIDTH + 2*PANEL_MARGIN, 115,
                                   SCREEN_WIDTH - SLOT_PANEL_WIDTH - 3*PANEL_MARGIN,
                                   SCREEN_HEIGHT - 130)
        pygame.draw.rect(self.screen, RetroColors.PANEL_BG, magnet_panel)
        draw_panel_border(self.screen, magnet_panel, RetroColors.ACCENT_TAN, 3)
        
        # 磁铁面板标题
        magnet_label = self.ui_font.render("WORD POOL", True, RetroColors.TEXT)
        self.screen.blit(magnet_label, (magnet_panel.x + 10, magnet_panel.y + 10))
        
        # 绘制磁铁
        for magnet in self.magnets:
            if magnet != self.selected_magnet:
                magnet.draw(self.screen, False)
        
        if self.selected_magnet:
            self.selected_magnet.draw(self.screen, True)
        
        # 胜利画面
        if self.game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            win_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 100, 500, 200)
            pygame.draw.rect(self.screen, RetroColors.PANEL_BG, win_rect)
            draw_panel_border(self.screen, win_rect, RetroColors.COMPLETED, 4)
            
            win_text = self.title_font.render("SEQUENCE COMPLETE", True, RetroColors.COMPLETED)
            win_rect_text = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(win_text, win_rect_text)
            
            instruction = self.ui_font.render("Press R to restart", True, RetroColors.TEXT)
            inst_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            self.screen.blit(instruction, inst_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


# ==================== 主程序 ====================
if __name__ == "__main__":
    game = Game()
    game.run()
