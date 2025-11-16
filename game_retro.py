"""
1-A-2-B 交替排序游戏 - 复古音频设备风格
参考 retro_ui.py 的视觉设计
红色背景 + 黑色面板 + 复古科技感
"""

import pygame
import sys
import random
import math
from typing import List, Tuple, Optional
import cv2
import mediapipe as mp
import numpy as np

# ==================== 初始化 ====================
pygame.init()
pygame.font.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# ==================== 声音生成函数 ====================
def generate_notification_sound():
    """生成消息提示音（简单的双音调）"""
    import numpy as np
    
    sample_rate = 22050
    duration = 0.15  # 150毫秒
    
    # 生成两个音调的正弦波（类似"叮咚"声）
    t1 = np.linspace(0, duration/2, int(sample_rate * duration/2))
    t2 = np.linspace(0, duration/2, int(sample_rate * duration/2))
    
    freq1 = 800  # 第一个音调频率（Hz）
    freq2 = 600  # 第二个音调频率（Hz）
    
    # 生成音调并添加淡出效果
    wave1 = np.sin(2 * np.pi * freq1 * t1) * np.linspace(1, 0.3, len(t1))
    wave2 = np.sin(2 * np.pi * freq2 * t2) * np.linspace(0.3, 0, len(t2))
    
    # 合并两个音调
    wave = np.concatenate([wave1, wave2])
    
    # 转换为16位整数
    wave = np.int16(wave * 32767)
    
    # 创建立体声（复制到两个声道）
    stereo_wave = np.column_stack((wave, wave))
    
    # 创建pygame Sound对象
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

def generate_dancer_appear_sound():
    """生成像素人出现的音效（弹跳声）"""
    import numpy as np
    
    sample_rate = 22050
    duration = 0.2
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 使用下降的频率模拟弹跳声
    freq_start = 600
    freq_end = 200
    freq = np.linspace(freq_start, freq_end, len(t))
    
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 8)  # 指数衰减
    wave = np.int16(wave * 32767 * 0.3)  # 30%音量
    
    stereo_wave = np.column_stack((wave, wave))
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

def generate_dancer_dance_sound():
    """生成像素人跳舞的循环音效（轻快的节拍）"""
    import numpy as np
    
    sample_rate = 22050
    duration = 0.1  # 短促的节拍声
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 简单的打击乐音效
    freq = 300
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 30)
    wave = np.int16(wave * 32767 * 0.15)  # 15%音量（很轻）
    
    stereo_wave = np.column_stack((wave, wave))
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

def generate_phone_ring_sound():
    """生成来电铃声音效（经典铃声）"""
    import numpy as np
    
    sample_rate = 22050
    duration = 1.5  # 1.5秒的铃声
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 双音多频（类似经典电话铃声）
    freq1 = 440  # A4
    freq2 = 554  # C#5
    
    # 创建铃声模式：响 - 停 - 响 - 停
    ring_pattern = np.zeros(len(t))
    ring_duration = int(sample_rate * 0.3)  # 每次响0.3秒
    pause_duration = int(sample_rate * 0.15)  # 停0.15秒
    
    for i in range(3):  # 3次铃响
        start = i * (ring_duration + pause_duration)
        end = start + ring_duration
        if end < len(ring_pattern):
            ring_pattern[start:end] = 1
    
    # 生成铃声波形
    wave = (np.sin(2 * np.pi * freq1 * t) + np.sin(2 * np.pi * freq2 * t)) / 2
    wave = wave * ring_pattern * 0.4  # 40%音量
    
    wave = np.int16(wave * 32767)
    stereo_wave = np.column_stack((wave, wave))
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

def generate_system_warning_sound():
    """生成系统警告音效（严肃的警报声）"""
    import numpy as np
    
    sample_rate = 22050
    duration = 1.0  # 1秒的警告声
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 使用三音调警报（紧急感）
    freq1 = 800
    freq2 = 600
    freq3 = 700
    
    # 创建三段式警报：高-低-中
    segment_len = len(t) // 3
    wave = np.zeros(len(t))
    
    # 第一段：高音
    wave[:segment_len] = np.sin(2 * np.pi * freq1 * t[:segment_len])
    # 第二段：低音
    wave[segment_len:2*segment_len] = np.sin(2 * np.pi * freq2 * t[segment_len:2*segment_len])
    # 第三段：中音
    wave[2*segment_len:] = np.sin(2 * np.pi * freq3 * t[2*segment_len:])
    
    # 添加紧迫感的调制
    modulation = np.sin(2 * np.pi * 8 * t)  # 8Hz调制
    wave = wave * (0.7 + 0.3 * modulation)
    
    # 音量渐强
    envelope = np.linspace(0.3, 0.6, len(t))
    wave = wave * envelope
    
    wave = np.int16(wave * 32767)
    stereo_wave = np.column_stack((wave, wave))
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

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
    ERROR = (255, 50, 50)  # 错误标记

# ==================== 配置 ====================
BORDER_SIZE = 150  # 2cm 边框 (约 75 像素/cm)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GAME_WIDTH = SCREEN_WIDTH - 2 * BORDER_SIZE  # 游戏区域宽度
GAME_HEIGHT = SCREEN_HEIGHT - 2 * BORDER_SIZE  # 游戏区域高度
GAME_OFFSET_X = BORDER_SIZE  # 游戏区域X偏移
GAME_OFFSET_Y = BORDER_SIZE  # 游戏区域Y偏移
MAX_TARGET = 8  # 从10减少到8（减少4个项：2个数字+2个字母）
SNAP_RADIUS = 50

# 面板布局
PANEL_MARGIN = 15
BOTTOM_BAR_HEIGHT = 100  # 底部序列条高度
BOTTOM_BAR_Y = GAME_OFFSET_Y + GAME_HEIGHT - BOTTOM_BAR_HEIGHT - PANEL_MARGIN  # 底部条Y位置

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
        self.is_error = False
        self.error_time = 0
        
        text_surf = font.render(value, True, RetroColors.TEXT)
        text_rect = text_surf.get_rect()
        self.width = text_rect.width + 28
        self.height = text_rect.height + 16
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.pos
        
        self.hover_scale = 1.0
        self.glow_alpha = 0
        
        # 生成独特的撕碎边缘形状（每个纸条不同）
        self.torn_edges = self._generate_torn_edges()
    
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
    
    def _generate_torn_edges(self):
        """生成不规则的撕碎边缘形状"""
        # 为每条边生成随机的撕裂点
        edges = {
            'top': [],
            'right': [],
            'bottom': [],
            'left': []
        }
        
        # 顶边 - 不规则撕裂
        steps = random.randint(8, 15)
        for i in range(steps):
            ratio = i / (steps - 1)
            x = ratio
            # 更大的随机偏移创造不规则效果
            y = random.uniform(-0.15, 0.05)
            edges['top'].append((x, y))
        
        # 右边 - 不规则撕裂
        steps = random.randint(8, 15)
        for i in range(steps):
            ratio = i / (steps - 1)
            x = random.uniform(0.95, 1.15)
            y = ratio
            edges['right'].append((x, y))
        
        # 底边 - 不规则撕裂
        steps = random.randint(8, 15)
        for i in range(steps):
            ratio = i / (steps - 1)
            x = 1 - ratio
            y = random.uniform(0.95, 1.15)
            edges['bottom'].append((x, y))
        
        # 左边 - 不规则撕裂
        steps = random.randint(8, 15)
        for i in range(steps):
            ratio = i / (steps - 1)
            x = random.uniform(-0.15, 0.05)
            y = 1 - ratio
            edges['left'].append((x, y))
        
        return edges
    
    def _get_torn_polygon(self, width, height):
        """根据撕碎边缘生成多边形点"""
        points = []
        
        # 顶边
        for x_ratio, y_ratio in self.torn_edges['top']:
            x = max(0, min(width, x_ratio * width))
            y = max(0, y_ratio * height)
            points.append((x, y))
        
        # 右边
        for x_ratio, y_ratio in self.torn_edges['right']:
            x = min(width, x_ratio * width)
            y = max(0, min(height, y_ratio * height))
            points.append((x, y))
        
        # 底边
        for x_ratio, y_ratio in self.torn_edges['bottom']:
            x = max(0, min(width, x_ratio * width))
            y = min(height, y_ratio * height)
            points.append((x, y))
        
        # 左边
        for x_ratio, y_ratio in self.torn_edges['left']:
            x = max(0, x_ratio * width)
            y = max(0, min(height, y_ratio * height))
            points.append((x, y))
        
        return points
    
    def draw(self, screen: pygame.Surface, is_selected: bool):
        scaled_rect = self.rect.copy()
        if self.hover_scale != 1.0:
            scaled_rect.width = int(self.width * self.hover_scale)
            scaled_rect.height = int(self.height * self.hover_scale)
            scaled_rect.center = self.rect.center
        
        # 阴影效果（撕碎纸条）
        shadow_offset = 4
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        
        # 绘制阴影（半透明黑色，使用不规则形状）
        shadow_surf = pygame.Surface((shadow_rect.width + 20, shadow_rect.height + 20), pygame.SRCALPHA)
        shadow_points = self._get_torn_polygon(shadow_rect.width, shadow_rect.height)
        
        if len(shadow_points) > 2:
            # 偏移阴影点以匹配阴影位置
            shadow_points_offset = [(p[0] + 10, p[1] + 10) for p in shadow_points]
            pygame.draw.polygon(shadow_surf, (0, 0, 0, 80), shadow_points_offset)
        screen.blit(shadow_surf, (shadow_rect.x - 10, shadow_rect.y - 10))
        
        # 发光效果（选中时）
        if self.glow_alpha > 0 and is_selected:
            glow_surf = pygame.Surface((scaled_rect.width + 20, scaled_rect.height + 20), pygame.SRCALPHA)
            glow_points = self._get_torn_polygon(scaled_rect.width, scaled_rect.height)
            if len(glow_points) > 2:
                glow_points_offset = [(p[0] + 10, p[1] + 10) for p in glow_points]
                # 绘制多层发光
                for i in range(3):
                    offset = 4 + i * 2
                    glow_layer = [(p[0] + offset - 4, p[1] + offset - 4) for p in glow_points_offset]
                    alpha = int(self.glow_alpha * 0.3 / (i + 1))
                    pygame.draw.polygon(glow_surf, (255, 200, 100, alpha), glow_layer)
            screen.blit(glow_surf, (scaled_rect.x - 10, scaled_rect.y - 10))
        
        # 纸条背景（白色）
        if self.is_locked:
            bg_color = (220, 220, 220)  # 已锁定 - 灰白色
            text_color = (100, 100, 100)  # 灰色文字
        elif self.is_error:
            # 错误状态 - 白底红字
            bg_color = (255, 240, 240)
            text_color = RetroColors.ERROR
        elif is_selected:
            bg_color = (255, 255, 240)  # 选中 - 微黄色
            text_color = (50, 50, 50)
        else:
            bg_color = (255, 255, 255)  # 白色纸条
            text_color = (30, 30, 30)  # 黑色文字
        
        # 绘制纸条背景（不规则撕裂边缘）
        paper_surf = pygame.Surface((scaled_rect.width + 20, scaled_rect.height + 20), pygame.SRCALPHA)
        paper_points = self._get_torn_polygon(scaled_rect.width, scaled_rect.height)
        
        if len(paper_points) > 2:
            # 偏移点以留出边距
            paper_points_offset = [(p[0] + 10, p[1] + 10) for p in paper_points]
            pygame.draw.polygon(paper_surf, bg_color, paper_points_offset)
            
            # 添加细微的纸张纹理线条（在不规则形状内）
            for i in range(3):
                line_y = random.randint(15, scaled_rect.height - 5)
                line_x_start = random.randint(10, 20)
                line_x_end = scaled_rect.width - random.randint(10, 20)
                line_color = (max(0, bg_color[0] - 15), max(0, bg_color[1] - 15), max(0, bg_color[2] - 15))
                pygame.draw.line(paper_surf, line_color, 
                               (line_x_start, line_y), (line_x_end, line_y), 1)
            
            # 添加一些随机的褶皱线
            for i in range(2):
                fold_x = random.randint(15, scaled_rect.width - 5)
                fold_y_start = random.randint(10, 15)
                fold_y_end = scaled_rect.height - random.randint(10, 15)
                fold_color = (max(0, bg_color[0] - 10), max(0, bg_color[1] - 10), max(0, bg_color[2] - 10))
                pygame.draw.line(paper_surf, fold_color, 
                               (fold_x, fold_y_start), (fold_x + random.randint(-5, 5), fold_y_end), 1)
        
        screen.blit(paper_surf, (scaled_rect.x - 10, scaled_rect.y - 10))
        
        # 文字（黑色）
        text_surf = self.font.render(self.value, True, text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)
        
        # 错误标记 "X"
        if self.is_error:
            x_font = pygame.font.SysFont('Consolas', 36, bold=True)
            x_surf = x_font.render('X', True, RetroColors.ERROR)
            x_rect = x_surf.get_rect(center=scaled_rect.center)
            screen.blit(x_surf, x_rect)
    
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


# ==================== 聊天弹窗类 ====================
class ChatNotification:
    def __init__(self, x: int, y: int, font: pygame.font.Font):
        self.x = x
        self.y = y
        self.width = 280
        self.height = 80
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.font = font
        self.visible = False
        self.appear_time = 0
        self.notification_type = "message"  # "message" 或 "call"
        
        # 生成提示音
        try:
            self.notification_sound = generate_notification_sound()
            self.notification_sound.set_volume(0.3)  # 设置音量为30%
            self.phone_ring_sound = generate_phone_ring_sound()
            self.phone_ring_sound.set_volume(0.4)  # 设置音量为40%
        except:
            self.notification_sound = None
            self.phone_ring_sound = None
        
        self.messages = [
            ("Alice", "Hey! Can u help?"),
            ("Boss", "Work tomorrow?"),
            ("Mom", "Did you eat?"),
            ("Jack", "Send me the file"),
            ("Sarah", "Free to chat?"),
            ("Tom", "Call me back!"),
            ("Lisa", "Check this out!"),
        ]
        
        self.phone_calls = [
            ("Mom", "Incoming Call..."),
            ("Boss", "Calling..."),
            ("Unknown", "Incoming Call..."),
            ("Dad", "Calling..."),
            ("Friend", "Incoming Call..."),
        ]
        
        self.border_colors = [
            (100, 200, 100),  # 绿色 (微信风格)
            (0, 150, 255),    # 蓝色 (Facebook风格)
            (255, 100, 150),  # 粉色 (Instagram风格)
            (150, 100, 255),  # 紫色 (Discord风格)
            (255, 200, 50),   # 黄色 (Snapchat风格)
        ]
        
        self.call_color = (50, 205, 50)  # 绿色来电
        
        self.current_message = random.choice(self.messages)
        self.current_border_color = random.choice(self.border_colors)
    
    def show(self, current_time: int):
        self.visible = True
        self.appear_time = current_time
        
        # 50%概率显示来电，50%显示消息
        if random.random() > 0.5:
            self.notification_type = "call"
            self.current_message = random.choice(self.phone_calls)
            self.current_border_color = self.call_color
            # 播放来电铃声
            if self.phone_ring_sound:
                try:
                    self.phone_ring_sound.play()
                except:
                    pass
        else:
            self.notification_type = "message"
            self.current_message = random.choice(self.messages)
            self.current_border_color = random.choice(self.border_colors)
            # 播放消息提示音
            if self.notification_sound:
                try:
                    self.notification_sound.play()
                except:
                    pass
    
    def update(self, current_time: int):
        # 显示5秒后消失
        if self.visible and current_time - self.appear_time > 5000:
            self.visible = False
    
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        
        # 半透明背景
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surf.fill((40, 40, 40, 230))
        screen.blit(bg_surf, (self.x, self.y))
        
        # 彩色边框（随机颜色）
        pygame.draw.rect(screen, self.current_border_color, self.rect, 2, border_radius=5)
        
        if self.notification_type == "call":
            # 来电显示样式
            # 电话图标（简化的电话符号）
            phone_icon_x = self.x + 20
            phone_icon_y = self.y + 25
            
            # 绘制电话听筒形状
            pygame.draw.arc(screen, self.current_border_color, 
                          (phone_icon_x - 8, phone_icon_y - 8, 16, 16), 
                          math.pi * 0.2, math.pi * 0.8, 3)
            pygame.draw.arc(screen, self.current_border_color, 
                          (phone_icon_x - 8, phone_icon_y + 8, 16, 16), 
                          math.pi * 1.2, math.pi * 1.8, 3)
            
            # 文字
            sender, message = self.current_message
            
            # 闪烁效果（来电时）
            blink = int((pygame.time.get_ticks() - self.appear_time) / 500) % 2
            text_color = (255, 255, 255) if blink else (200, 255, 200)
            
            sender_surf = self.font.render(sender, True, text_color)
            message_surf = self.font.render(message, True, self.current_border_color)
            
            screen.blit(sender_surf, (self.x + 45, self.y + 15))
            screen.blit(message_surf, (self.x + 45, self.y + 45))
            
            # 来电按钮图标
            accept_x = self.x + self.width - 60
            decline_x = self.x + self.width - 30
            button_y = self.y + self.height // 2
            
            # 接听按钮（绿色）
            pygame.draw.circle(screen, (50, 205, 50), (accept_x, button_y), 8)
            # 挂断按钮（红色）
            pygame.draw.circle(screen, (255, 50, 50), (decline_x, button_y), 8)
        else:
            # 原来的消息样式
            # 应用图标（圆点，颜色与边框匹配）
            pygame.draw.circle(screen, self.current_border_color, (self.x + 20, self.y + 25), 12)
            
            # 文字（英文）
            sender, message = self.current_message
            sender_surf = self.font.render(sender, True, (255, 255, 255))
            message_surf = self.font.render(message, True, (200, 200, 200))
            
            screen.blit(sender_surf, (self.x + 40, self.y + 15))
            screen.blit(message_surf, (self.x + 40, self.y + 45))


# ==================== 系统警告类 ====================
class SystemWarning:
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.title_font = pygame.font.SysFont('Consolas', 24, bold=True)
        self.visible = False
        self.appear_time = 0
        self.width = 450
        self.height = 200
        
        # 生成警告音
        try:
            self.warning_sound = generate_system_warning_sound()
            self.warning_sound.set_volume(0.5)
        except:
            self.warning_sound = None
        
        self.warnings = [
            ("SYSTEM ERROR", "Critical system failure detected!", "Please restart immediately"),
            ("SECURITY ALERT", "Unauthorized access detected!", "System will lock in 30 seconds"),
            ("LOW MEMORY", "System memory critically low!", "Close applications now"),
            ("DISK ERROR", "Hard drive failure imminent!", "Backup your data immediately"),
            ("VIRUS DETECTED", "Malware found in system!", "Run antivirus scan now"),
            ("UPDATE REQUIRED", "Critical security update!", "Install update to continue"),
        ]
        
        self.current_warning = random.choice(self.warnings)
    
    def show(self, current_time: int):
        self.visible = True
        self.appear_time = current_time
        self.current_warning = random.choice(self.warnings)
        
        # 播放警告音
        if self.warning_sound:
            try:
                self.warning_sound.play()
            except:
                pass
    
    def update(self, current_time: int):
        # 显示4秒后消失
        if self.visible and current_time - self.appear_time > 4000:
            self.visible = False
    
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        
        # 计算中心位置
        center_x = GAME_OFFSET_X + GAME_WIDTH // 2
        center_y = GAME_OFFSET_Y + GAME_HEIGHT // 2
        
        x = center_x - self.width // 2
        y = center_y - self.height // 2
        
        rect = pygame.Rect(x, y, self.width, self.height)
        
        # 闪烁效果
        blink = int((pygame.time.get_ticks() - self.appear_time) / 300) % 2
        
        # 半透明红色背景
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if blink:
            bg_surf.fill((150, 20, 20, 240))
        else:
            bg_surf.fill((120, 10, 10, 240))
        screen.blit(bg_surf, (x, y))
        
        # 红色警告边框
        border_color = (255, 50, 50) if blink else (200, 30, 30)
        pygame.draw.rect(screen, border_color, rect, 4, border_radius=5)
        
        # 警告图标（三角形感叹号）
        icon_x = x + 30
        icon_y = y + self.height // 2
        icon_size = 35
        
        # 三角形
        triangle_points = [
            (icon_x, icon_y - icon_size // 2),
            (icon_x - icon_size // 2, icon_y + icon_size // 2),
            (icon_x + icon_size // 2, icon_y + icon_size // 2)
        ]
        pygame.draw.polygon(screen, (255, 200, 0), triangle_points)
        pygame.draw.polygon(screen, (255, 255, 255), triangle_points, 3)
        
        # 感叹号
        exclaim_font = pygame.font.SysFont('Consolas', 28, bold=True)
        exclaim_surf = exclaim_font.render("!", True, (0, 0, 0))
        exclaim_rect = exclaim_surf.get_rect(center=(icon_x, icon_y))
        screen.blit(exclaim_surf, exclaim_rect)
        
        # 警告文字
        title, message1, message2 = self.current_warning
        
        # 标题（闪烁白色/黄色）
        title_color = (255, 255, 255) if blink else (255, 255, 0)
        title_surf = self.title_font.render(title, True, title_color)
        screen.blit(title_surf, (x + 80, y + 30))
        
        # 消息内容
        msg1_surf = self.font.render(message1, True, (255, 220, 220))
        screen.blit(msg1_surf, (x + 80, y + 70))
        
        msg2_surf = self.font.render(message2, True, (255, 220, 220))
        screen.blit(msg2_surf, (x + 80, y + 100))
        
        # 假的按钮
        button_y = y + self.height - 50
        button_width = 80
        button_height = 30
        
        # OK 按钮
        ok_rect = pygame.Rect(x + self.width - button_width - 100, button_y, button_width, button_height)
        pygame.draw.rect(screen, (80, 80, 80), ok_rect, border_radius=3)
        pygame.draw.rect(screen, (200, 200, 200), ok_rect, 2, border_radius=3)
        ok_text = self.font.render("OK", True, (255, 255, 255))
        ok_text_rect = ok_text.get_rect(center=ok_rect.center)
        screen.blit(ok_text, ok_text_rect)
        
        # Cancel 按钮
        cancel_rect = pygame.Rect(x + self.width - button_width - 20, button_y, button_width, button_height)
        pygame.draw.rect(screen, (80, 80, 80), cancel_rect, border_radius=3)
        pygame.draw.rect(screen, (200, 200, 200), cancel_rect, 2, border_radius=3)
        cancel_text = self.font.render("Cancel", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        screen.blit(cancel_text, cancel_text_rect)


# ==================== 像素小人跳舞干扰类 ====================
class PixelDancer:
    # 类级别的声音对象（所有实例共享）
    appear_sound = None
    dance_sound = None
    
    @classmethod
    def initialize_sounds(cls):
        """初始化类级别的声音（只调用一次）"""
        if cls.appear_sound is None:
            try:
                cls.appear_sound = generate_dancer_appear_sound()
                cls.appear_sound.set_volume(0.4)
                cls.dance_sound = generate_dancer_dance_sound()
                cls.dance_sound.set_volume(0.2)
            except:
                cls.appear_sound = None
                cls.dance_sound = None
    
    def __init__(self, base_x, base_y):
        # 基础属性
        self.start_time = pygame.time.get_ticks()
        self.base_pos = pygame.Vector2(base_x, base_y)
        
        # 随机颜色（模拟短视频风格的彩色像素人）
        self.skin_color = random.choice([
            (255, 200, 150), (255, 180, 120), (200, 150, 100),
            (255, 100, 150), (100, 200, 255), (150, 255, 100)  # 加入彩色变体
        ])
        self.outfit_color = (random.randint(100, 255), random.randint(50, 200), random.randint(50, 200))
        
        # 动画参数
        self.scale = random.uniform(1.5, 2.5)  # 随机大小
        self.dance_speed = random.uniform(0.008, 0.015)  # 跳舞速度
        self.dance_style = random.randint(0, 2)  # 0=左右摇摆, 1=上下跳跃, 2=旋转
        
        # 生命周期
        self.lifetime = random.randint(5000, 10000)  # 5到10秒
        
        # 声音相关
        self.sound_played = False
        self.last_dance_sound_time = 0
        self.dance_sound_interval = random.randint(800, 1500)  # 跳舞音效间隔（毫秒）
        
        # 播放出现音效
        if PixelDancer.appear_sound and not self.sound_played:
            try:
                PixelDancer.appear_sound.play()
                self.sound_played = True
            except:
                pass
    
    def is_alive(self, current_time):
        """检查是否存活"""
        return (current_time - self.start_time) < self.lifetime
    
    def _draw_pixel_person(self, surface: pygame.Surface, x: int, y: int, 
                           arm_angle_left: float, arm_angle_right: float, 
                           leg_offset: int, body_tilt: float):
        """绘制像素小人（使用矩形拼接）"""
        pixel_size = int(4 * self.scale)
        
        # 身体倾斜效果
        tilt_x = int(body_tilt * 3)
        
        # 头部（圆形，像素风格）
        head_y = y - int(18 * self.scale)
        pygame.draw.rect(surface, self.skin_color, 
                        (x - pixel_size, head_y - pixel_size, pixel_size * 2, pixel_size * 2))
        pygame.draw.rect(surface, self.skin_color, 
                        (x - pixel_size * 2, head_y, pixel_size, pixel_size))
        pygame.draw.rect(surface, self.skin_color, 
                        (x + pixel_size, head_y, pixel_size, pixel_size))
        
        # 眼睛
        pygame.draw.rect(surface, (50, 50, 50), 
                        (x - pixel_size//2, head_y, pixel_size//2, pixel_size//2))
        pygame.draw.rect(surface, (50, 50, 50), 
                        (x + pixel_size//4, head_y, pixel_size//2, pixel_size//2))
        
        # 身体
        body_y = y - int(10 * self.scale)
        body_height = int(10 * self.scale)
        pygame.draw.rect(surface, self.outfit_color, 
                        (x - pixel_size + tilt_x, body_y, pixel_size * 2, body_height))
        
        # 左臂（根据角度摆动）
        arm_len = int(8 * self.scale)
        left_arm_x = x - pixel_size + tilt_x + int(math.cos(arm_angle_left) * arm_len)
        left_arm_y = body_y + int(math.sin(arm_angle_left) * arm_len)
        pygame.draw.line(surface, self.skin_color, 
                        (x - pixel_size + tilt_x, body_y + pixel_size), 
                        (left_arm_x, left_arm_y), int(2 * self.scale))
        
        # 右臂
        right_arm_x = x + pixel_size + tilt_x + int(math.cos(arm_angle_right) * arm_len)
        right_arm_y = body_y + int(math.sin(arm_angle_right) * arm_len)
        pygame.draw.line(surface, self.skin_color, 
                        (x + pixel_size + tilt_x, body_y + pixel_size), 
                        (right_arm_x, right_arm_y), int(2 * self.scale))
        
        # 腿部
        leg_y = y
        left_leg_x = x - pixel_size//2 + tilt_x
        right_leg_x = x + pixel_size//2 + tilt_x
        
        # 左腿（带动画偏移）
        pygame.draw.rect(surface, self.outfit_color, 
                        (left_leg_x - leg_offset, leg_y, pixel_size, int(10 * self.scale)))
        
        # 右腿
        pygame.draw.rect(surface, self.outfit_color, 
                        (right_leg_x + leg_offset, leg_y, pixel_size, int(10 * self.scale)))
    
    def draw(self, surface: pygame.Surface, current_time: int):
        """绘制跳舞的像素小人"""
        age = current_time - self.start_time
        
        # 播放跳舞音效（间隔播放）
        if PixelDancer.dance_sound and current_time - self.last_dance_sound_time > self.dance_sound_interval:
            try:
                PixelDancer.dance_sound.play()
                self.last_dance_sound_time = current_time
            except:
                pass
        
        # 根据舞蹈风格计算动画参数
        if self.dance_style == 0:  # 左右摇摆
            sway = math.sin(age * self.dance_speed) * 15
            arm_left = math.sin(age * self.dance_speed) * 0.8 + math.pi * 0.3
            arm_right = -math.sin(age * self.dance_speed) * 0.8 + math.pi * 0.7
            leg_offset = int(abs(math.sin(age * self.dance_speed * 2)) * 3)
            body_tilt = math.sin(age * self.dance_speed) * 0.5
            pos = self.base_pos + pygame.Vector2(sway, 0)
            
        elif self.dance_style == 1:  # 上下跳跃
            bounce = abs(math.sin(age * self.dance_speed * 1.5)) * 20
            arm_left = math.pi * 0.2 if bounce > 10 else math.pi * 0.4
            arm_right = math.pi * 0.8 if bounce > 10 else math.pi * 0.6
            leg_offset = 0 if bounce > 10 else 3
            body_tilt = 0
            pos = self.base_pos + pygame.Vector2(0, -bounce)
            
        else:  # 旋转舞蹈
            rotation = age * self.dance_speed * 0.5
            radius = 8
            offset_x = math.cos(rotation) * radius
            offset_y = math.sin(rotation) * radius * 0.3
            arm_left = rotation
            arm_right = rotation + math.pi
            leg_offset = int(abs(math.sin(rotation * 2)) * 3)
            body_tilt = math.sin(rotation) * 0.3
            pos = self.base_pos + pygame.Vector2(offset_x, offset_y)
        
        # 绘制小人
        self._draw_pixel_person(surface, int(pos.x), int(pos.y), 
                               arm_left, arm_right, leg_offset, body_tilt)


# ==================== 游走像素人类（会走入游戏区域） ====================
class WanderingDancer(PixelDancer):
    def __init__(self, start_x, start_y, target_area):
        super().__init__(start_x, start_y)
        self.target_area = target_area  # 目标游走区域
        self.lifetime = random.randint(8000, 15000)  # 8-15秒的生命周期
        
        # 随机选择一个目标点（在游戏区域内）
        self.target_x = random.randint(target_area.x + 50, target_area.right - 50)
        self.target_y = random.randint(target_area.y + 80, target_area.bottom - 80)
        
        # 移动速度
        self.move_speed = random.uniform(0.5, 1.2)
        
        # 计算移动方向
        dx = self.target_x - self.base_pos.x
        dy = self.target_y - self.base_pos.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            self.velocity = pygame.Vector2(dx / distance * self.move_speed, 
                                          dy / distance * self.move_speed)
        else:
            self.velocity = pygame.Vector2(0, 0)
        
        self.has_reached = False
    
    def update(self, current_time: int):
        """更新位置，向目标移动"""
        if not self.has_reached:
            # 移动向目标
            self.base_pos += self.velocity
            
            # 检查是否到达目标
            dist_to_target = math.sqrt((self.target_x - self.base_pos.x) ** 2 + 
                                      (self.target_y - self.base_pos.y) ** 2)
            if dist_to_target < 10:
                self.has_reached = True
                # 到达后在附近游走
                self.target_x = self.base_pos.x + random.randint(-30, 30)
                self.target_y = self.base_pos.y + random.randint(-30, 30)
        else:
            # 在目标区域附近随机游走
            if random.random() > 0.98:
                self.target_x = random.randint(max(self.target_area.x + 50, int(self.base_pos.x) - 50),
                                              min(self.target_area.right - 50, int(self.base_pos.x) + 50))
                self.target_y = random.randint(max(self.target_area.y + 80, int(self.base_pos.y) - 50),
                                              min(self.target_area.bottom - 80, int(self.base_pos.y) + 50))
                
                dx = self.target_x - self.base_pos.x
                dy = self.target_y - self.base_pos.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance > 0:
                    self.velocity = pygame.Vector2(dx / distance * self.move_speed * 0.3,
                                                  dy / distance * self.move_speed * 0.3)
            
            self.base_pos += self.velocity


# ==================== 边框干扰管理器 ====================
class BorderDistraction:
    def __init__(self):
        self.dancers = []  # 边框区固定的跳舞小人
        self.wandering_dancers = []  # 游走到游戏区的小人
        self.max_dancers = 7  # 边框固定的最多7个
        self.max_wandering = 3  # 游走的最多3个
        
        # 干扰延迟控制
        self.distraction_enabled = False
        self.distraction_start_time = None
        self.distraction_delay = 3000  # 3秒延迟（毫秒）
        
        # 定义边框区域的六个干扰区
        self.distraction_areas = [
            pygame.Rect(20, 20, BORDER_SIZE - 40, 200),  # 左上角
            pygame.Rect(SCREEN_WIDTH - BORDER_SIZE + 20, 20, BORDER_SIZE - 40, 200),  # 右上角
            pygame.Rect(20, SCREEN_HEIGHT - 220, BORDER_SIZE - 40, 200),  # 左下角
            pygame.Rect(SCREEN_WIDTH - BORDER_SIZE + 20, SCREEN_HEIGHT - 220, BORDER_SIZE - 40, 200),  # 右下角
            pygame.Rect(SCREEN_WIDTH // 2 - 75, 10, 150, BORDER_SIZE - 20),  # 上边中间
            pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - BORDER_SIZE + 10, 150, BORDER_SIZE - 20),  # 下边中间
        ]
        
        # 游戏区域（供游走小人使用）
        self.game_area = pygame.Rect(GAME_OFFSET_X, GAME_OFFSET_Y, GAME_WIDTH, GAME_HEIGHT)
    
    def update(self, current_time: int, game_started: bool, game_start_time: Optional[int]):
        # 检查是否应该启动干扰（游戏开始后23秒）
        if game_started and game_start_time is not None:
            if not self.distraction_enabled:
                if current_time - game_start_time >= self.distraction_delay:
                    self.distraction_enabled = True
                    self.distraction_start_time = current_time
        else:
            # 游戏未开始，重置干扰状态
            self.distraction_enabled = False
            self.distraction_start_time = None
        
        # 移除"死亡"的跳舞小人
        self.dancers = [d for d in self.dancers if d.is_alive(current_time)]
        self.wandering_dancers = [d for d in self.wandering_dancers if d.is_alive(current_time)]
        
        # 只有在干扰启用后才添加新的跳舞小人
        if not self.distraction_enabled:
            return
        
        # 随机添加新的边框跳舞小人
        if len(self.dancers) < self.max_dancers and random.random() > 0.98:
            area = random.choice(self.distraction_areas)
            spawn_x = area.x + random.randint(40, max(41, area.width - 40))
            spawn_y = area.y + random.randint(60, max(61, area.height - 40))
            self.dancers.append(PixelDancer(spawn_x, spawn_y))
        
        # 随机添加游走小人（从边框走入游戏区）
        if len(self.wandering_dancers) < self.max_wandering and random.random() > 0.985:
            # 从边框区随机位置开始
            spawn_side = random.choice(['left', 'right', 'top', 'bottom'])
            if spawn_side == 'left':
                spawn_x = random.randint(20, 60)
                spawn_y = random.randint(GAME_OFFSET_Y + 100, GAME_OFFSET_Y + GAME_HEIGHT - 100)
            elif spawn_side == 'right':
                spawn_x = random.randint(SCREEN_WIDTH - 60, SCREEN_WIDTH - 20)
                spawn_y = random.randint(GAME_OFFSET_Y + 100, GAME_OFFSET_Y + GAME_HEIGHT - 100)
            elif spawn_side == 'top':
                spawn_x = random.randint(GAME_OFFSET_X + 100, GAME_OFFSET_X + GAME_WIDTH - 100)
                spawn_y = random.randint(20, 60)
            else:  # bottom
                spawn_x = random.randint(GAME_OFFSET_X + 100, GAME_OFFSET_X + GAME_WIDTH - 100)
                spawn_y = random.randint(SCREEN_HEIGHT - 60, SCREEN_HEIGHT - 20)
            
            self.wandering_dancers.append(WanderingDancer(spawn_x, spawn_y, self.game_area))
        
        # 更新游走小人的位置
        for dancer in self.wandering_dancers:
            dancer.update(current_time)
    
    def draw(self, surface: pygame.Surface, current_time: int):
        # 绘制所有跳舞的像素小人（边框和游走）
        for dancer in self.dancers:
            dancer.draw(surface, current_time)
        for dancer in self.wandering_dancers:
            dancer.draw(surface, current_time)


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


# ==================== 眼动追踪类 ====================
class EyeTracker:
    def __init__(self):
        # 初始化 MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        
        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # 虹膜关键点索引（用于获取瞳孔中心）
        self.LEFT_IRIS = [468, 469, 470, 471, 472]
        self.RIGHT_IRIS = [473, 474, 475, 476, 477]
        
        # 瞳孔历史追踪
        self.left_pupil_history = []
        self.right_pupil_history = []
        self.max_history = 10
        
        # 凝视点坐标（屏幕坐标系）
        self.gaze_x = SCREEN_WIDTH // 2
        self.gaze_y = SCREEN_HEIGHT // 2
        self.gaze_valid = False
        
        # 瞳孔初始基准位置（归一化坐标 0-1）
        self.baseline_pupil_x = None
        self.baseline_pupil_y = None
        self.baseline_frames = 0
        self.baseline_required_frames = 30  # 需要30帧来建立基准
        
        # 分心阈值（归一化坐标偏移）
        self.distraction_threshold = 0.02
        self.is_distracted = False
        
        self.camera_available = self.cap.isOpened()
    
    def update(self):
        """更新眼动追踪，返回凝视点坐标"""
        if not self.camera_available:
            return False
        
        success, image = self.cap.read()
        if not success:
            self.gaze_valid = False
            return False
        
        # 获取图像尺寸
        image_h, image_w, _ = image.shape
        
        # 转换为RGB并翻转（自拍视角）
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb = cv2.flip(image_rgb, 1)
        
        # 处理面部关键点
        results = self.face_mesh.process(image_rgb)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # 获取左右眼瞳孔中心点（虹膜landmark的中心点：468和473）
            left_pupil_x = face_landmarks.landmark[468].x
            left_pupil_y = face_landmarks.landmark[468].y
            
            right_pupil_x = face_landmarks.landmark[473].x
            right_pupil_y = face_landmarks.landmark[473].y
            
            # 平均两只眼睛的瞳孔位置（归一化坐标）
            avg_pupil_x = (left_pupil_x + right_pupil_x) / 2
            avg_pupil_y = (left_pupil_y + right_pupil_y) / 2
            
            # 建立基准位置（前30帧的平均值）
            if self.baseline_pupil_x is None:
                self.baseline_pupil_x = avg_pupil_x
                self.baseline_pupil_y = avg_pupil_y
                self.baseline_frames = 1
            elif self.baseline_frames < self.baseline_required_frames:
                # 累积平均
                self.baseline_pupil_x = (self.baseline_pupil_x * self.baseline_frames + avg_pupil_x) / (self.baseline_frames + 1)
                self.baseline_pupil_y = (self.baseline_pupil_y * self.baseline_frames + avg_pupil_y) / (self.baseline_frames + 1)
                self.baseline_frames += 1
            
            # 计算与基准位置的偏移（归一化坐标）
            if self.baseline_frames >= self.baseline_required_frames:
                offset_x = abs(avg_pupil_x - self.baseline_pupil_x)
                offset_y = abs(avg_pupil_y - self.baseline_pupil_y)
                total_offset = (offset_x ** 2 + offset_y ** 2) ** 0.5
                
                # 判断是否分心（偏离超过阈值）
                self.is_distracted = total_offset > self.distraction_threshold
            else:
                self.is_distracted = False
            
            # 将归一化坐标映射到屏幕坐标（翻转x轴以匹配自拍视角）
            self.gaze_x = int((1.0 - avg_pupil_x) * SCREEN_WIDTH)
            self.gaze_y = int(avg_pupil_y * SCREEN_HEIGHT)
            
            # 限制范围
            self.gaze_x = max(0, min(SCREEN_WIDTH, self.gaze_x))
            self.gaze_y = max(0, min(SCREEN_HEIGHT, self.gaze_y))
            
            self.gaze_valid = True
            return True
        else:
            self.gaze_valid = False
            return False
    
    def get_gaze_position(self) -> tuple[int, int]:
        """获取当前凝视点坐标"""
        return (self.gaze_x, self.gaze_y)
    
    def is_gaze_valid(self) -> bool:
        """检查凝视点是否有效"""
        return self.gaze_valid
    
    def is_pupil_distracted(self) -> bool:
        """检查瞳孔是否偏离基准位置（分心）"""
        return self.is_distracted and self.baseline_frames >= self.baseline_required_frames
    
    def get_baseline_status(self) -> str:
        """获取基准建立状态"""
        if self.baseline_frames < self.baseline_required_frames:
            return f"Calibrating... {self.baseline_frames}/{self.baseline_required_frames}"
        else:
            return "Tracking"
    
    def close(self):
        """释放资源"""
        if self.cap:
            self.cap.release()
        if self.face_mesh:
            self.face_mesh.close()


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
        self.distraction_font = pygame.font.SysFont('Consolas', 14, bold=True)
        
        # 初始化像素人声音
        PixelDancer.initialize_sounds()
        
        # 干扰元素
        self.chat_notification = ChatNotification(
            SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100, self.distraction_font
        )
        self.border_distraction = BorderDistraction()
        self.next_chat_time = None  # 延迟到游戏开始后23秒
        
        # 系统警告
        self.system_warning = SystemWarning(self.distraction_font)
        self.next_warning_time = None  # 延迟到游戏中后期
        
        # 眼动追踪
        self.eye_tracker = EyeTracker()
        
        # 分心统计
        self.total_frames = 0
        self.gaze_on_chat_frames = 0
        self.gaze_on_dancer_frames = 0
        self.distraction_percentage = 0.0
        
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
        
        # 计时器和错误计数
        self.start_time = None
        self.end_time = None
        self.error_count = 0
        self.game_started = False
        
        # 重置分心统计
        self.total_frames = 0
        self.gaze_on_chat_frames = 0
        self.gaze_on_dancer_frames = 0
        self.distraction_percentage = 0.0
        
        # 重置聊天通知时间
        self.next_chat_time = None
        
        # 重置系统警告时间
        self.next_warning_time = None
        
        # 生成目标序列
        target_sequence = []
        for i in range(1, MAX_TARGET + 1):
            target_sequence.append(str(i))
            target_sequence.append(chr(64 + i))  # 'A' 是 65
        
        # 创建槽位 - 底部横向排列
        slot_count = len(target_sequence)
        bottom_bar_left = GAME_OFFSET_X + PANEL_MARGIN + 40  # 增加左边距
        bottom_bar_right = GAME_OFFSET_X + GAME_WIDTH - PANEL_MARGIN - 40  # 增加右边距
        available_width = bottom_bar_right - bottom_bar_left
        slot_spacing = available_width / (slot_count - 1) if slot_count > 1 else 0
        
        slot_y = BOTTOM_BAR_Y + BOTTOM_BAR_HEIGHT // 2
        
        for i, value in enumerate(target_sequence):
            x = bottom_bar_left + i * slot_spacing
            pos = pygame.math.Vector2(x, slot_y)
            self.slots.append(TargetSlot(pos, value, i, self.slot_font))
        
        # 创建单词 - 确保包含所有目标单词
        words = target_sequence.copy()  # 包含所有数字和字母
        distractor_count = int(len(target_sequence) * 1.2)
        words.extend(random.choices(DISTRACTOR_WORDS, k=distractor_count))
        random.shuffle(words)
        
        # 磁铁生成区域 - 使用整个游戏区域（底部序列条上方）
        spawn_x_range = (GAME_OFFSET_X + 50, GAME_OFFSET_X + GAME_WIDTH - 50)
        spawn_y_range = (GAME_OFFSET_Y + 120, BOTTOM_BAR_Y - 20)
        
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
        
        # 开始计时（首次点击目标时）
        if not self.game_started:
            self.game_started = True
            self.start_time = pygame.time.get_ticks()
        
        # 检查是否为正确目标
        if self.selected_magnet.value != current_slot.value:
            # 错误 - 标记并计数
            self.selected_magnet.is_error = True
            self.selected_magnet.error_time = pygame.time.get_ticks()
            self.error_count += 1
            # TODO: 播放错误音效
            return
        
        distance = self.selected_magnet.pos.distance_to(current_slot.pos)
        if distance < SNAP_RADIUS:
            self.selected_magnet.update_position(current_slot.pos)
            self.selected_magnet.is_locked = True
            self.current_target_index += 1
            
            if self.current_target_index >= len(self.slots):
                self.game_won = True
                self.end_time = pygame.time.get_ticks()
                self.win_time = self.end_time
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()
        
        # 更新眼动追踪
        self.eye_tracker.update()
        
        # 基于瞳孔偏移检测分心
        if self.eye_tracker.is_gaze_valid() and self.game_started and not self.game_won:
            self.total_frames += 1
            
            # 检查瞳孔是否偏离基准位置（0.02阈值）
            if self.eye_tracker.is_pupil_distracted():
                # 瞳孔偏离基准位置，计为分心
                self.gaze_on_chat_frames += 1
            
            # 计算分心百分比
            if self.total_frames > 0:
                self.distraction_percentage = (self.gaze_on_chat_frames / self.total_frames) * 100
        
        for magnet in self.magnets:
            magnet.update(mouse_pos, magnet == self.selected_magnet)
            
            # 清除错误状态（显示1秒后）
            if magnet.is_error and current_time - magnet.error_time > 1000:
                magnet.is_error = False
        
        # 更新干扰元素（传递游戏状态）
        self.border_distraction.update(current_time, self.game_started, self.start_time)
        self.chat_notification.update(current_time)
        self.system_warning.update(current_time)
        
        # 初始化聊天弹窗时间（游戏开始后3秒）
        if self.game_started and self.next_chat_time is None:
            self.next_chat_time = self.start_time + 3000 + random.randint(2000, 5000)  # 3秒 + 2-5秒随机延迟
        
        # 初始化系统警告时间（游戏进行到中后期，50%进度后）
        if self.game_started and self.next_warning_time is None and len(self.slots) > 0:
            # 当完成度达到40%时，设置警告时间
            if self.current_target_index >= len(self.slots) * 0.4:
                self.next_warning_time = current_time + random.randint(5000, 10000)  # 5-10秒后出现
        
        # 定期显示聊天弹窗（只在游戏开始且干扰启用后）
        if self.game_started and self.next_chat_time is not None:
            if current_time >= self.next_chat_time and not self.chat_notification.visible:
                self.chat_notification.show(current_time)
                self.next_chat_time = current_time + random.randint(8000, 15000)  # 8-15秒后再次弹出
        
        # 显示系统警告（游戏中后期）
        if self.game_started and self.next_warning_time is not None:
            if current_time >= self.next_warning_time and not self.system_warning.visible:
                self.system_warning.show(current_time)
                # 下次警告间隔更长
                self.next_warning_time = current_time + random.randint(20000, 30000)  # 20-30秒后再次出现
        
        if self.game_won:
            elapsed = current_time - self.win_time
            if elapsed > 5000:
                self.initialize_game()
    
    def draw(self):
        # 红色背景 - retro_ui风格（全屏）
        self.screen.fill(RetroColors.BG)
        
        # 绘制游戏区域边框（深色内嵌效果）
        game_area = pygame.Rect(GAME_OFFSET_X, GAME_OFFSET_Y, GAME_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(self.screen, (50, 50, 50), game_area)
        pygame.draw.rect(self.screen, (100, 100, 100), game_area, 3)
        
        # 绘制边框区域的干扰元素
        current_time = pygame.time.get_ticks()
        self.border_distraction.draw(self.screen, current_time)
        self.chat_notification.draw(self.screen)
        
        # 系统警告绘制在最上层（覆盖所有元素）
        self.system_warning.draw(self.screen)
        
        # 顶部标题面板（在游戏区域内）- 音频波形风格
        title_panel = pygame.Rect(GAME_OFFSET_X + PANEL_MARGIN, GAME_OFFSET_Y + PANEL_MARGIN, 
                                 GAME_WIDTH - 2*PANEL_MARGIN, 70)
        
        # 米黄色背景
        beige_bg = (215, 205, 180)
        pygame.draw.rect(self.screen, beige_bg, title_panel)
        
        # 深色边框
        border_color = (60, 50, 40)
        pygame.draw.rect(self.screen, border_color, title_panel, 4)
        
        # 左侧橙棕色竖条
        left_stripe_width = 20
        stripe_color = (180, 120, 70)
        pygame.draw.rect(self.screen, stripe_color, 
                        (title_panel.x, title_panel.y, left_stripe_width, title_panel.height))
        
        # 右侧灰色竖条
        right_stripe_width = 25
        right_stripe_color = (140, 140, 140)
        pygame.draw.rect(self.screen, right_stripe_color,
                        (title_panel.right - right_stripe_width, title_panel.y, right_stripe_width, title_panel.height))
        
        # 分成上下两个通道区域（L 和 R）
        channel_height = (title_panel.height - 6) // 2
        channel_margin = 3
        
        # L 通道（上半部分）
        l_channel_rect = pygame.Rect(title_panel.x + left_stripe_width + 10, title_panel.y + channel_margin,
                                     title_panel.width - left_stripe_width - right_stripe_width - 20, channel_height)
        
        # R 通道（下半部分）
        r_channel_rect = pygame.Rect(title_panel.x + left_stripe_width + 10, 
                                     title_panel.y + channel_margin + channel_height + channel_margin,
                                     title_panel.width - left_stripe_width - right_stripe_width - 20, channel_height)
        
        # 绘制中间分隔线
        pygame.draw.line(self.screen, border_color,
                        (title_panel.x + left_stripe_width, title_panel.centery),
                        (title_panel.right - right_stripe_width, title_panel.centery), 2)
        
        # 绘制 L 和 R 标签
        label_font = pygame.font.SysFont('Arial', 20, bold=True)
        l_text = label_font.render("L", True, (80, 80, 80))
        r_text = label_font.render("R", True, (80, 80, 80))
        
        # L 在最左边（左侧橙棕色条内）
        self.screen.blit(l_text, (title_panel.x + (left_stripe_width - l_text.get_width()) // 2, 
                                  l_channel_rect.centery - l_text.get_height() // 2))
        # R 在最右边（右侧灰色条内）
        self.screen.blit(r_text, (title_panel.right - right_stripe_width + (right_stripe_width - r_text.get_width()) // 2,
                                  r_channel_rect.centery - r_text.get_height() // 2))
        
        # 绘制基线
        baseline_color = (120, 110, 100)
        l_baseline_y = l_channel_rect.centery
        r_baseline_y = r_channel_rect.centery
        pygame.draw.line(self.screen, baseline_color, 
                        (l_channel_rect.x, l_baseline_y), (l_channel_rect.right, l_baseline_y), 1)
        pygame.draw.line(self.screen, baseline_color,
                        (r_channel_rect.x, r_baseline_y), (r_channel_rect.right, r_baseline_y), 1)
        
        # 标题和规则文字
        text_color = (40, 40, 40)
        title_font_text = pygame.font.SysFont('Arial', 18, bold=True)
        rule_font_text = pygame.font.SysFont('Arial', 14)
        
        # L 通道 - 标题
        title_text = title_font_text.render("SEQUENCE SORTER", True, text_color)
        title_x = l_channel_rect.x + 10
        self.screen.blit(title_text, (title_x, l_channel_rect.centery - title_text.get_height() // 2))
        
        # R 通道 - 游戏规则
        last_num = MAX_TARGET
        last_letter = chr(64 + MAX_TARGET)
        rule_text = rule_font_text.render(f"Sort the sequence: 1-A-2-B-3-C...{last_num}-{last_letter}", True, text_color)
        rule_x = r_channel_rect.x + 10
        self.screen.blit(rule_text, (rule_x, r_channel_rect.centery - rule_text.get_height() // 2))
        
        # 底部序列条面板
        bottom_bar = pygame.Rect(GAME_OFFSET_X + PANEL_MARGIN, BOTTOM_BAR_Y, 
                                GAME_WIDTH - 2 * PANEL_MARGIN, BOTTOM_BAR_HEIGHT)
        pygame.draw.rect(self.screen, RetroColors.PANEL_BG, bottom_bar)
        draw_panel_border(self.screen, bottom_bar, RetroColors.ACCENT_BLUE, 3)
        
        # 底部面板标题
        panel_label = self.ui_font.render("TARGET SEQUENCE", True, RetroColors.TEXT)
        self.screen.blit(panel_label, (bottom_bar.x + 10, bottom_bar.y + 10))
        
        # 进度信息（右上角）
        progress_text = self.ui_font.render(f"{self.current_target_index}/{len(self.slots)}", 
                                           True, RetroColors.ACCENT_TAN)
        self.screen.blit(progress_text, (bottom_bar.right - 70, bottom_bar.y + 10))
        
        # ==================== 边框UI - 复古磁带风格 ====================
        
        # 顶部边框 - 磁带卷轴和计时器
        reel_center_y = 70
        reel_left_x = 60
        reel_right_x = SCREEN_WIDTH - 60
        reel_radius = 35
        
        # 左侧卷轴（计时器）
        if self.game_started and not self.game_won:
            elapsed_ms = pygame.time.get_ticks() - self.start_time
        elif self.game_won:
            elapsed_ms = self.end_time - self.start_time
        else:
            elapsed_ms = 0
        
        elapsed_sec = elapsed_ms / 1000.0
        
        # 绘制左侧卷轴
        pygame.draw.circle(self.screen, (40, 40, 40), (reel_left_x, reel_center_y), reel_radius)
        pygame.draw.circle(self.screen, (80, 80, 80), (reel_left_x, reel_center_y), reel_radius, 3)
        pygame.draw.circle(self.screen, (60, 60, 60), (reel_left_x, reel_center_y), reel_radius - 10)
        pygame.draw.circle(self.screen, (100, 100, 100), (reel_left_x, reel_center_y), reel_radius - 10, 2)
        
        # 卷轴旋转效果（基于时间）
        rotation = (elapsed_sec * 2) % (math.pi * 2)
        for i in range(6):
            angle = rotation + i * (math.pi / 3)
            line_start = (reel_left_x + math.cos(angle) * 10, reel_center_y + math.sin(angle) * 10)
            line_end = (reel_left_x + math.cos(angle) * (reel_radius - 12), reel_center_y + math.sin(angle) * (reel_radius - 12))
            pygame.draw.line(self.screen, (120, 120, 120), line_start, line_end, 2)
        
        # 时间文字
        time_text = self.ui_font.render(f"{elapsed_sec:.1f}s", True, RetroColors.TEXT)
        time_rect = time_text.get_rect(center=(reel_left_x, reel_center_y))
        self.screen.blit(time_text, time_rect)
        
        # 右侧卷轴（错误计数）
        pygame.draw.circle(self.screen, (40, 40, 40), (reel_right_x, reel_center_y), reel_radius)
        pygame.draw.circle(self.screen, (80, 80, 80), (reel_right_x, reel_center_y), reel_radius, 3)
        pygame.draw.circle(self.screen, (60, 60, 60), (reel_right_x, reel_center_y), reel_radius - 10)
        pygame.draw.circle(self.screen, (100, 100, 100), (reel_right_x, reel_center_y), reel_radius - 10, 2)
        
        # 错误数字
        error_text = self.counter_font.render(str(self.error_count), True, RetroColors.ERROR)
        error_rect = error_text.get_rect(center=(reel_right_x, reel_center_y))
        self.screen.blit(error_text, error_rect)
        
        # 标签
        label_font = pygame.font.SysFont('Consolas', 12, bold=True)
        time_label = label_font.render("TIME", True, RetroColors.TEXT_DIM)
        self.screen.blit(time_label, (reel_left_x - time_label.get_width() // 2, reel_center_y + reel_radius + 5))
        
        error_label = label_font.render("ERRORS", True, RetroColors.TEXT_DIM)
        self.screen.blit(error_label, (reel_right_x - error_label.get_width() // 2, reel_center_y + reel_radius + 5))
        
        # 中间进度条和分心指示器
        progress_bar_y = reel_center_y
        progress_bar_left = reel_left_x + reel_radius + 30
        progress_bar_right = reel_right_x - reel_radius - 30
        progress_bar_width = progress_bar_right - progress_bar_left
        
        # 进度条背景（磁带）
        tape_height = 8
        pygame.draw.rect(self.screen, (30, 30, 30), 
                        (progress_bar_left, progress_bar_y - tape_height // 2, progress_bar_width, tape_height))
        pygame.draw.rect(self.screen, (80, 80, 80), 
                        (progress_bar_left, progress_bar_y - tape_height // 2, progress_bar_width, tape_height), 1)
        
        # 进度填充
        if len(self.slots) > 0:
            progress = self.current_target_index / len(self.slots)
            progress_width = int(progress_bar_width * progress)
            pygame.draw.rect(self.screen, RetroColors.ACCENT_TAN, 
                            (progress_bar_left, progress_bar_y - tape_height // 2, progress_width, tape_height))
        
        # 分心指示器（在进度条下方）
        if self.game_started and self.total_frames > 30:
            distract_y = progress_bar_y + 20
            
            # 根据分心程度改变颜色
            if self.distraction_percentage > 30:
                indicator_color = RetroColors.ERROR
                status = "HIGH"
            elif self.distraction_percentage > 15:
                indicator_color = (255, 165, 0)
                status = "MED"
            else:
                indicator_color = RetroColors.COMPLETED
                status = "LOW"
            
            # 指示灯
            indicator_radius = 8
            indicator_x = (progress_bar_left + progress_bar_right) // 2
            pygame.draw.circle(self.screen, indicator_color, (indicator_x, distract_y), indicator_radius)
            pygame.draw.circle(self.screen, (200, 200, 200), (indicator_x, distract_y), indicator_radius, 2)
            
            # 文字
            distract_text = label_font.render(f"DISTRACTION: {status} ({self.distraction_percentage:.0f}%)", 
                                             True, RetroColors.TEXT_DIM)
            distract_rect = distract_text.get_rect(center=(indicator_x, distract_y + indicator_radius + 12))
            self.screen.blit(distract_text, distract_rect)
        
        # 绘制槽位（在底部序列条中）
        current_time = pygame.time.get_ticks()
        for slot in self.slots:
            slot.draw(self.screen, self.current_target_index, current_time)
        
        # 绘制磁铁
        for magnet in self.magnets:
            if magnet != self.selected_magnet:
                magnet.draw(self.screen, False)
        
        if self.selected_magnet:
            self.selected_magnet.draw(self.screen, True)
        
        # 绘制凝视点光标（如果眼动追踪激活）
        if self.eye_tracker.is_gaze_valid():
            gaze_x, gaze_y = self.eye_tracker.get_gaze_position()
            
            # 根据瞳孔偏移状态改变颜色
            if self.eye_tracker.is_pupil_distracted():
                # 分心状态 - 红色
                gaze_color = (255, 50, 50, 150)
                outer_color = (255, 50, 50, 80)
            else:
                # 专注状态 - 青色
                gaze_color = (0, 255, 255, 150)
                outer_color = (0, 255, 255, 80)
            
            gaze_size = 15
            
            # 创建半透明 surface
            gaze_surf = pygame.Surface((gaze_size * 2, gaze_size * 2), pygame.SRCALPHA)
            
            # 外圈
            pygame.draw.circle(gaze_surf, outer_color, (gaze_size, gaze_size), gaze_size)
            # 内圈
            pygame.draw.circle(gaze_surf, gaze_color, (gaze_size, gaze_size), gaze_size // 2)
            # 十字线
            pygame.draw.line(gaze_surf, gaze_color, (0, gaze_size), (gaze_size * 2, gaze_size), 2)
            pygame.draw.line(gaze_surf, gaze_color, (gaze_size, 0), (gaze_size, gaze_size * 2), 2)
            
            self.screen.blit(gaze_surf, (gaze_x - gaze_size, gaze_y - gaze_size))
            
            # 显示校准状态
            status_text = self.distraction_font.render(self.eye_tracker.get_baseline_status(), 
                                                      True, RetroColors.TEXT_DIM)
            self.screen.blit(status_text, (GAME_OFFSET_X + PANEL_MARGIN + 20, 
                                          GAME_OFFSET_Y + GAME_HEIGHT - 30))
        
        # 胜利画面
        if self.game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            win_rect = pygame.Rect(GAME_OFFSET_X + GAME_WIDTH//2 - 250, 
                                  GAME_OFFSET_Y + GAME_HEIGHT//2 - 100, 500, 200)
            pygame.draw.rect(self.screen, RetroColors.PANEL_BG, win_rect)
            draw_panel_border(self.screen, win_rect, RetroColors.COMPLETED, 4)
            
            win_text = self.title_font.render("SEQUENCE COMPLETE", True, RetroColors.COMPLETED)
            win_center_x = GAME_OFFSET_X + GAME_WIDTH//2
            win_center_y = GAME_OFFSET_Y + GAME_HEIGHT//2
            win_rect_text = win_text.get_rect(center=(win_center_x, win_center_y - 50))
            self.screen.blit(win_text, win_rect_text)
            
            # 显示最终统计
            total_time = (self.end_time - self.start_time) / 1000.0
            stats_text = self.ui_font.render(f"Time: {total_time:.1f}s  |  Errors: {self.error_count}", 
                                            True, RetroColors.ACCENT_TAN)
            stats_rect = stats_text.get_rect(center=(win_center_x, win_center_y))
            self.screen.blit(stats_text, stats_rect)
            
            instruction = self.ui_font.render("Press R to restart", True, RetroColors.TEXT)
            inst_rect = instruction.get_rect(center=(win_center_x, win_center_y + 40))
            self.screen.blit(instruction, inst_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        # 释放眼动追踪资源
        self.eye_tracker.close()
        
        pygame.quit()
        sys.exit()


# ==================== 主程序 ====================
if __name__ == "__main__":
    game = Game()
    game.run()
