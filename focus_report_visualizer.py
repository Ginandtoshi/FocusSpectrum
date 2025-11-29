"""Focus score visualizer that transforms distraction metrics into an animated
Perlin-noise ASCII mosaic and a dynamic Rorschach-style biological visualization.

Run this as a stand-alone script or import ``FocusReportVisualizer`` and call
``run()`` after the distraction test finishes.

Visual styles:
1. ASCII Mosaic: Perlin-noise driven character grid
2. Rorschach Blob: Symmetric biological/organic particle system

- High distraction (low focus score): Red/warm tones, chaotic noise, fast animation
- Low distraction (high focus score): Blue/cool tones, calm patterns, slow animation
"""

from __future__ import annotations

import math
import random
import sys
from typing import Dict, Iterable, List, Optional, Tuple

import pygame
from noise import pnoise3

# -- Configuration defaults -------------------------------------------------

DEFAULT_WINDOW_WIDTH = 960
DEFAULT_WINDOW_HEIGHT = 720
FRAME_RATE = 12

# Unicode block characters matching the reference image style
# Ordered from light/sparse to dense/heavy
ASCII_CHARS_CALM: list[str] = [
    " ", "·", ".", ":", "∙", "░", "▒", "▓",
    "─", "│", "┌", "┐", "└", "┘", "├", "┤",
    "┬", "┴", "┼", "╱", "╲", "╳",
    "▏", "▎", "▍", "▌", "▋", "▊", "▉",
    "⠁", "⠃", "⠇", "⠏", "⠟", "⠿",
]

ASCII_CHARS_CHAOTIC: list[str] = [
    "█", "▓", "▒", "░", "▄", "▀", "▌", "▐",
    "▖", "▗", "▘", "▙", "▚", "▛", "▜", "▝", "▞", "▟",
    "▂", "▃", "▄", "▅", "▆", "▇", "█",
    "┃", "━", "╳", "╱", "╲",
    "⣿", "⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯",
    "⠿", "⡿", "⣿",
]

# Gradient color palettes - 水晶色板
# 基于参考代码: ['#d30c7b','#e9564c','#ff9f1c','#ffb787','#ffc3bc','#fecef1','#d2dde9','#a6ece0','#57aab4','#086788']

# 专注状态：冷色调（青-蓝-绿）- 圆滑、平静
CALM_GRADIENT = [
    "#a6ece0",  # 浅青绿
    "#8de4d8",  # 青绿
    "#74dcd0",  # 中青绿
    "#5bc8c0",  # 青
    "#57aab4",  # 青蓝
    "#4a9aaa",  # 中青蓝
    "#3d8a9f",  # 深青
    "#2f7994",  # 深青蓝
    "#086788",  # 最深青蓝
    "#055570",  # 暗青蓝
]

# 分心状态：暖色调（红-粉-橙）- 尖锐、躁动
CHAOTIC_GRADIENT = [
    "#ffc3bc",  # 淡珊瑚
    "#ffb0a5",  # 浅珊瑚
    "#ff9d8e",  # 珊瑚
    "#f98775",  # 深珊瑚
    "#e9564c",  # 珊瑚红
    "#e04050",  # 红
    "#d72f60",  # 深红粉
    "#d01c70",  # 粉红
    "#d30c7b",  # 深粉红
    "#b5086a",  # 最深粉红
]

# 中间过渡色（黄-橙-杏）
NEUTRAL_GRADIENT = [
    "#fecef1",  # 浅粉
    "#ffd9e8",  # 淡粉
    "#ffc3bc",  # 淡珊瑚
    "#ffb787",  # 杏色
    "#ffab6b",  # 深杏
    "#ff9f1c",  # 橙黄（核心过渡色）
    "#f5940f",  # 深橙
    "#e88a08",  # 橙
    "#d2dde9",  # 浅灰蓝
    "#c0d0e0",  # 灰蓝
]

FONT_CHOICES = ["consolas", "couriernew", "lucidaconsole", "dejavusansmono", "monospace"]


# -- Rorschach Blob Configuration -------------------------------------------

# 水晶色板 (Crystal Palette) - 基于参考代码的颜色
# 从专注(蓝/青)到分心(红/粉)的渐变
CRYSTAL_COLORS = [
    '#086788',  # 深青蓝 - 最专注
    '#57aab4',  # 青色
    '#a6ece0',  # 浅青绿
    '#d2dde9',  # 浅灰蓝
    '#fecef1',  # 浅粉
    '#ffc3bc',  # 淡珊瑚
    '#ffb787',  # 杏色
    '#ff9f1c',  # 橙黄 - 过渡色
    '#e9564c',  # 珊瑚红
    '#d30c7b',  # 深粉红 - 最分心
]

# 罗夏墨迹图的颜色配置 (更新为水晶色)
RORSCHACH_COLORS = {
    # 专注状态：冷色调
    "calm_primary": (8, 103, 136),       # #086788 深青蓝
    "calm_secondary": (87, 170, 180),    # #57aab4 青色
    "calm_tertiary": (166, 236, 224),    # #a6ece0 浅青绿
    # 过渡状态：暖黄色
    "neutral_primary": (255, 159, 28),   # #ff9f1c 橙黄
    "neutral_secondary": (255, 183, 135),# #ffb787 杏色
    # 分心状态：暖红色
    "anxious_primary": (211, 12, 123),   # #d30c7b 深粉红
    "anxious_secondary": (233, 86, 76),  # #e9564c 珊瑚红
    "anxious_tertiary": (255, 195, 188), # #ffc3bc 淡珊瑚
    # 通用
    "black": (15, 15, 20),
    "white": (245, 241, 228),             # #f5f1e4 蛋壳白（参考代码背景色）
}


# -- Utility functions ------------------------------------------------------

def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(color_a: tuple[int, int, int], color_b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(ca, cb, t)) for ca, cb in zip(color_a, color_b))


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if in_max == in_min:
        return out_min
    return out_min + (out_max - out_min) * ((value - in_min) / (in_max - in_min))


# -- Visualizer -------------------------------------------------------------

class FocusReportVisualizer:
    def __init__(
        self,
        score: float,
        metrics: Optional[Dict[str, float | str]] = None,
        title: str = "Focus Report",
        surface_size: tuple[int, int] = (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT),
    ) -> None:
        self.score = clamp(score, 0.0, 100.0)
        self.focus_ratio = self.score / 100.0  # 1.0 = fully focused, 0.0 = fully distracted
        self.distraction_ratio = 1.0 - self.focus_ratio
        self.metrics = metrics or {}
        self.title = title
        self.surface_size = surface_size

        # Build gradient palette based on focus level
        # High focus = calm blue tones, Low focus = chaotic red/orange tones
        self.calm_palette = [hex_to_rgb(c) for c in CALM_GRADIENT]
        self.chaotic_palette = [hex_to_rgb(c) for c in CHAOTIC_GRADIENT]
        self.neutral_palette = [hex_to_rgb(c) for c in NEUTRAL_GRADIENT]
        self.active_palette = self._build_gradient_palette()

        # Build character set based on focus level
        self.ascii_chars = self._build_char_set()

        # Visual parameters that change with focus level
        # Distracted: larger cells, faster animation, more chaotic noise
        # Focused: smaller cells, slower animation, calmer noise
        self.cell_size = int(map_range(self.distraction_ratio, 0.0, 1.0, 12, 18))
        self.noise_scale = map_range(self.distraction_ratio, 0.0, 1.0, 0.08, 0.18)
        self.z_increment = map_range(self.distraction_ratio, 0.0, 1.0, 0.008, 0.04)
        self.noise_octaves = int(map_range(self.distraction_ratio, 0.0, 1.0, 2, 6))
        self.noise_persistence = map_range(self.distraction_ratio, 0.0, 1.0, 0.3, 0.7)

        pygame.init()
        self.screen = pygame.display.set_mode(self.surface_size, pygame.RESIZABLE)
        pygame.display.set_caption(self.title)

        self.grid_font = pygame.font.SysFont(FONT_CHOICES, self.cell_size)
        overlay_size = max(16, self.cell_size - 2)
        self.overlay_font = pygame.font.SysFont(FONT_CHOICES, overlay_size, bold=True)
        self.body_font = pygame.font.SysFont(FONT_CHOICES, overlay_size - 2)

        self.char_cache = self._create_char_cache(self.grid_font, self.active_palette)

        self.clock = pygame.time.Clock()
        self.frame_count = 0
        self.z_offset = 0.0

    def _build_gradient_palette(self) -> List[Tuple[int, int, int]]:
        """Build a color palette that transitions from calm (blue) to chaotic (red)."""
        palette_size = 12
        palette: List[Tuple[int, int, int]] = []
        
        for i in range(palette_size):
            t = i / (palette_size - 1)  # 0.0 to 1.0
            
            # Get base colors from calm and chaotic palettes
            calm_idx = int(t * (len(self.calm_palette) - 1))
            chaotic_idx = int(t * (len(self.chaotic_palette) - 1))
            neutral_idx = int(t * (len(self.neutral_palette) - 1))
            
            calm_color = self.calm_palette[calm_idx]
            chaotic_color = self.chaotic_palette[chaotic_idx]
            neutral_color = self.neutral_palette[neutral_idx]
            
            # Blend based on distraction level
            # Low distraction (high focus) -> more calm colors
            # High distraction -> more chaotic colors
            if self.distraction_ratio < 0.3:
                # Mostly calm with slight neutral
                color = lerp_color(calm_color, neutral_color, self.distraction_ratio * 2)
            elif self.distraction_ratio < 0.6:
                # Transition through neutral
                blend = (self.distraction_ratio - 0.3) / 0.3
                color = lerp_color(neutral_color, chaotic_color, blend * 0.5)
            else:
                # Mostly chaotic
                blend = (self.distraction_ratio - 0.6) / 0.4
                color = lerp_color(
                    lerp_color(neutral_color, chaotic_color, 0.5),
                    chaotic_color,
                    blend
                )
            
            palette.append(color)
        
        return palette

    def _build_char_set(self) -> List[str]:
        """Build character set that transitions from calm to chaotic."""
        if self.distraction_ratio < 0.3:
            # Mostly calm characters
            return ASCII_CHARS_CALM
        elif self.distraction_ratio < 0.6:
            # Mix of both
            mixed = ASCII_CHARS_CALM[::2] + ASCII_CHARS_CHAOTIC[::2]
            return mixed
        else:
            # Mostly chaotic characters
            return ASCII_CHARS_CHAOTIC

    def _build_blended_palette(self, count: int) -> list[tuple[int, int, int]]:
        palette: list[tuple[int, int, int]] = []
        for i in range(count):
            base_a = self.chaotic_palette[i % len(self.chaotic_palette)]
            base_b = self.calm_palette[i % len(self.calm_palette)]
            palette.append(lerp_color(base_a, base_b, self.focus_ratio))
        return palette

    def _create_char_cache(
        self,
        font: pygame.font.Font,
        palette: Iterable[tuple[int, int, int]],
    ) -> dict[int, dict[int, pygame.Surface]]:
        cache: dict[int, dict[int, pygame.Surface]] = {}
        colors = list(palette)
        for char_index, char in enumerate(self.ascii_chars):
            cache[char_index] = {}
            for color_index, rgb in enumerate(colors):
                cache[char_index][color_index] = font.render(char, True, rgb)
        return cache

    def _select_char_index(self, value: float) -> int:
        # Add some chaos for high distraction
        chaos_factor = self.distraction_ratio * 0.3
        adjusted = clamp(value + chaos_factor * (value - 0.5), 0.0, 1.0)
        return min(int(adjusted * (len(self.ascii_chars) - 1)), len(self.ascii_chars) - 1)

    def _select_color_index(self, value: float) -> int:
        return min(int(value * (len(self.active_palette) - 1)), len(self.active_palette) - 1)

    def _draw_overlay(self, width: int, height: int) -> None:
        padding = 18
        panel_height = int(height * 0.18)
        panel_rect = pygame.Rect(0, 0, width, panel_height)

        overlay_bg = lerp_color((20, 20, 25), (240, 245, 250), self.focus_ratio)
        overlay_bg = tuple(clamp(channel, 0, 255) for channel in overlay_bg)
        pygame.draw.rect(self.screen, overlay_bg, panel_rect)

        border_color = lerp_color((180, 90, 60), (60, 120, 140), self.focus_ratio)
        pygame.draw.rect(self.screen, border_color, panel_rect, 2)

        title_text = self.overlay_font.render(f"{self.title}", True, border_color)
        self.screen.blit(title_text, (padding, padding))

        score_color = lerp_color((200, 60, 40), (60, 190, 120), self.focus_ratio)
        score_text = self.overlay_font.render(f"Focus Score: {self.score:.1f}", True, score_color)
        self.screen.blit(score_text, (padding, padding + title_text.get_height() + 4))

        metrics_y = padding + title_text.get_height() + score_text.get_height() + 10
        for label, value in self.metrics.items():
            line = f"{label}: {value}"
            line_surface = self.body_font.render(line, True, border_color)
            self.screen.blit(line_surface, (padding, metrics_y))
            metrics_y += line_surface.get_height() + 2

        instructions = "Press ESC or close window to exit"
        instr_surface = self.body_font.render(instructions, True, border_color)
        instr_rect = instr_surface.get_rect()
        instr_rect.bottomright = (width - padding, panel_height - padding // 2)
        self.screen.blit(instr_surface, instr_rect)

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            width, height = self.screen.get_size()
            grid_width = width * 0.76
            grid_height = height * 0.68
            pad_left = (width - grid_width) / 2
            pad_top = height - grid_height - height * 0.08

            cols = max(1, int(grid_width // self.cell_size))
            rows = max(1, int(grid_height // self.cell_size))

            background_color = lerp_color((12, 12, 16), (245, 245, 248), self.focus_ratio)
            self.screen.fill(background_color)

            x_start = self.frame_count * self.noise_scale * 0.35
            y_start = self.frame_count * self.noise_scale * 0.25

            for grid_y in range(rows):
                y_offset = y_start + grid_y * self.noise_scale
                for grid_x in range(cols):
                    x_offset = x_start + grid_x * self.noise_scale
                    noise_value = pnoise3(
                        x_offset, y_offset, self.z_offset,
                        octaves=self.noise_octaves,
                        persistence=self.noise_persistence,
                        lacunarity=2.0
                    )
                    normalized = clamp(map_range(noise_value, -1.0, 1.0, 0.0, 1.0), 0.0, 1.0)

                    char_idx = self._select_char_index(normalized)
                    color_idx = self._select_color_index(normalized)
                    glyph = self.char_cache[char_idx][color_idx]

                    pos_x = pad_left + grid_x * self.cell_size + self.cell_size / 2
                    pos_y = pad_top + grid_y * self.cell_size + self.cell_size / 2
                    glyph_rect = glyph.get_rect(center=(pos_x, pos_y))
                    self.screen.blit(glyph, glyph_rect)

            self._draw_overlay(width, height)

            self.z_offset += self.z_increment
            self.frame_count += 1

            pygame.display.flip()
            self.clock.tick(FRAME_RATE)

        pygame.quit()
        sys.exit()


def run_visual_report(score: float, metrics: Optional[Dict[str, float | str]] = None) -> None:
    """Convenience wrapper for quick launches."""
    visualizer = FocusReportVisualizer(score=score, metrics=metrics)
    visualizer.run()


# =============================================================================
# Rorschach Blob Visualizer - 动态生物罗夏墨迹图
# =============================================================================

class RorschachBlob:
    """
    动态生物罗夏墨迹图渲染器。
    
    创建一个关于Y轴对称的、由粒子组成的有机形态，
    视觉效果类似于心理学测试中的墨迹图或显微镜下的细胞。
    
    关键特性：
    - 垂直对称：图形严格关于中线对称
    - 粒子系统：由数千个微小圆点组成
    - 拖尾效果：使用半透明覆盖层产生烟雾般的消散效果
    - 噪声驱动：Perlin噪声控制粒子分布和颜色变化
    """
    
    def __init__(
        self,
        surface: pygame.Surface,
        center_x: float,
        center_y: float,
        size: float,
        focus_score: float = 75.0,
        distraction_count: int = 5,
        error_count: int = 0,
    ):
        """
        初始化罗夏墨迹图渲染器。
        
        Args:
            surface: 要绘制到的 pygame Surface
            center_x: 图形中心 X 坐标
            center_y: 图形中心 Y 坐标  
            size: 图形的基础尺寸
            focus_score: 专注分数 (0-100)，影响颜色倾向
            distraction_count: 分心次数，影响流动速度
            error_count: 错误次数，影响粒子扩散程度
        """
        self.surface = surface
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        
        # 用户数据
        self.focus_score = clamp(focus_score, 0.0, 100.0)
        self.distraction_count = distraction_count
        self.error_count = error_count
        
        # 计算衍生参数
        self.focus_ratio = self.focus_score / 100.0
        self.is_focused = self.focus_score > 50
        
        # 视觉参数
        self.max_radius = 6
        self.noise_octaves = 3
        self.frame_count = 0
        
        # 应用用户数据映射
        self._apply_data_mapping()
        
        # 创建拖尾效果的半透明表面 - 使用透明背景
        self.fade_surface = pygame.Surface(
            (int(self.size * 2.5), int(self.size * 2.5)),
            pygame.SRCALPHA
        )
        # 透明度决定拖尾长度：值越小，拖尾越长
        fade_alpha = int(map_range(self.focus_ratio, 0.0, 1.0, 8, 18))
        # 使用透明色作为拖尾（让背景透出）
        self.fade_surface.fill((245, 243, 240, fade_alpha))
        
        # 计算绘制区域
        self.draw_rect = pygame.Rect(
            int(self.center_x - self.size * 1.25),
            int(self.center_y - self.size * 1.25),
            int(self.size * 2.5),
            int(self.size * 2.5)
        )
        
        # 创建独立的绘制缓冲区 - 透明背景
        self.buffer = pygame.Surface(
            (int(self.size * 2.5), int(self.size * 2.5)),
            pygame.SRCALPHA
        )
        # 透明背景初始化
        self.buffer.fill((0, 0, 0, 0))
        
        # 创建圆形遮罩
        self._create_circular_mask()
    
    def _create_circular_mask(self):
        """创建圆形遮罩 - 匹配参考图中的灰色圆形"""
        w, h = self.buffer.get_size()
        self.mask_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.mask_surface.fill((0, 0, 0, 0))
        
        # 绘制圆形作为遮罩
        center = (w // 2, h // 2)
        radius = min(w, h) // 2 - 10
        pygame.draw.circle(self.mask_surface, (255, 255, 255, 255), center, radius)
    
    def _apply_data_mapping(self):
        """将用户测试数据映射为视觉参数"""
        
        # 1. 流动速度 (Speed): 分心次数越多，流动越快、越混乱
        base_speed = 0.003
        self.speed = base_speed + (self.distraction_count * 0.0015)
        self.speed = min(self.speed, 0.025)  # 限制最大速度
        
        # 2. 噪声尺度 (Scale): 分数越低，噪点越密集（更破碎/尖锐）
        # 高分 = 更平滑的形态；低分 = 更碎片化/尖锐
        self.scale = 0.005 + ((100 - self.focus_score) / 100) * 0.008
        
        # 3. 粒子扩散度: 错误越多，形态越发散
        base_spread = 1.2
        error_factor = min(self.error_count * 0.08, 0.6)
        self.spread = base_spread + error_factor
        
        # 4. 粒子数量: 根据性能和效果平衡
        self.n_plotters = int(map_range(self.focus_ratio, 0.0, 1.0, 1800, 2200))
        
        # 5. 粒子最大半径: 专注时更大更圆润，分心时更小更尖锐
        self.max_radius = map_range(self.focus_ratio, 0.0, 1.0, 4, 8)
        
        # 6. 噪声复杂度 (octaves): 分心时更多层次 = 更尖锐碎片化
        self.noise_octaves = int(map_range(self.focus_ratio, 0.0, 1.0, 5, 2))
        
        # 7. 构建颜色调色板 (基于水晶色板)
        self._build_color_palette()
    
    def _build_color_palette(self):
        """
        基于专注度构建动态颜色调色板 - 6个分段，更丰富的颜色过渡。
        
        分数段:
        - 0-20:   深红/粉红 (非常分心)
        - 20-35:  珊瑚红/橙红 (较分心)
        - 35-50:  橙色/杏色 (中低)
        - 50-65:  黄绿/浅青 (中高)
        - 65-80:  青色/青蓝 (较专注)
        - 80-100: 深青蓝/蓝 (非常专注)
        """
        # 水晶色板 - 从专注到分心的完整渐变
        crystal_palette = [
            hex_to_rgb(c) for c in CRYSTAL_COLORS
        ]
        
        # 扩展色板 - 添加更多中间色
        extended_palette = {
            "deep_blue": (6, 82, 110),       # 最深青蓝
            "blue": crystal_palette[0],       # #086788 深青蓝
            "cyan": crystal_palette[1],       # #57aab4 青色
            "light_cyan": crystal_palette[2], # #a6ece0 浅青绿
            "pale_blue": crystal_palette[3],  # #d2dde9 浅灰蓝
            "pale_pink": crystal_palette[4],  # #fecef1 浅粉
            "coral_light": crystal_palette[5],# #ffc3bc 淡珊瑚
            "apricot": crystal_palette[6],    # #ffb787 杏色
            "orange": crystal_palette[7],     # #ff9f1c 橙黄
            "coral_red": crystal_palette[8],  # #e9564c 珊瑚红
            "deep_pink": crystal_palette[9],  # #d30c7b 深粉红
            "magenta": (180, 8, 100),         # 洋红
        }
        
        # 根据专注度选择调色板区间 - 6个分段
        if self.focus_ratio >= 0.8:
            # 80-100: 非常专注 - 深青蓝色调
            self.primary_colors = [
                extended_palette["deep_blue"],
                extended_palette["blue"],
                extended_palette["cyan"],
            ]
            self.secondary_colors = [
                extended_palette["blue"],
                extended_palette["cyan"],
                extended_palette["light_cyan"],
            ]
        elif self.focus_ratio >= 0.65:
            # 65-80: 较专注 - 青色调
            self.primary_colors = [
                extended_palette["cyan"],
                extended_palette["light_cyan"],
                extended_palette["blue"],
            ]
            self.secondary_colors = [
                extended_palette["light_cyan"],
                extended_palette["pale_blue"],
                extended_palette["cyan"],
            ]
        elif self.focus_ratio >= 0.5:
            # 50-65: 中高 - 浅青/黄绿过渡
            self.primary_colors = [
                extended_palette["light_cyan"],
                extended_palette["pale_blue"],
                extended_palette["pale_pink"],
            ]
            self.secondary_colors = [
                extended_palette["pale_blue"],
                extended_palette["pale_pink"],
                extended_palette["coral_light"],
            ]
        elif self.focus_ratio >= 0.35:
            # 35-50: 中低 - 橙色/杏色
            self.primary_colors = [
                extended_palette["apricot"],
                extended_palette["orange"],
                extended_palette["coral_light"],
            ]
            self.secondary_colors = [
                extended_palette["coral_light"],
                extended_palette["apricot"],
                extended_palette["pale_pink"],
            ]
        elif self.focus_ratio >= 0.2:
            # 20-35: 较分心 - 珊瑚红/橙红
            self.primary_colors = [
                extended_palette["coral_red"],
                extended_palette["orange"],
                extended_palette["apricot"],
            ]
            self.secondary_colors = [
                extended_palette["orange"],
                extended_palette["coral_red"],
                extended_palette["deep_pink"],
            ]
        else:
            # 0-20: 非常分心 - 深红/粉红
            self.primary_colors = [
                extended_palette["deep_pink"],
                extended_palette["magenta"],
                extended_palette["coral_red"],
            ]
            self.secondary_colors = [
                extended_palette["magenta"],
                extended_palette["deep_pink"],
                extended_palette["coral_red"],
            ]

    def _get_color_palette(self, noise_value: float) -> Tuple[Tuple[int, int, int, int], float]:
        """
        根据噪声值返回颜色和粒子半径。
        
        使用水晶色板，根据专注度动态选择颜色范围：
        - 专注: 青蓝色调，圆润形态
        - 分心: 红粉色调，尖锐形态
        - 过渡: 黄橙色调
        
        Args:
            noise_value: 0.0 到 1.0 之间的噪声值
            
        Returns:
            (颜色RGBA元组, 粒子半径)
        """
        # 基础透明度 - 更高的透明度使颜色更明显
        base_alpha = int(map_range(self.focus_ratio, 0.0, 1.0, 180, 220))
        
        # 从当前调色板选择颜色
        primary_idx = int(noise_value * (len(self.primary_colors) - 1))
        primary_idx = max(0, min(primary_idx, len(self.primary_colors) - 1))
        primary = self.primary_colors[primary_idx] + (base_alpha,)
        
        secondary_idx = int(noise_value * (len(self.secondary_colors) - 1))
        secondary_idx = max(0, min(secondary_idx, len(self.secondary_colors) - 1))
        secondary = self.secondary_colors[secondary_idx] + (base_alpha - 20,)
        
        # 颜色映射表 - 减少白色，增加主题色占比
        colors = [
            primary,
            secondary,
            primary,
            secondary,
            primary,
            primary,
            secondary,
            primary,
            secondary,
            primary,
        ]
        
        n = len(colors)
        segment_size = 1.0 / n
        index = int(noise_value / segment_size)
        index = max(0, min(index, n - 1))
        
        # 计算在当前区间的相对位置
        position_in_segment = (noise_value - (index * segment_size)) / segment_size
        
        # 半径变化：
        # - 专注时: 更大更圆润的粒子
        # - 分心时: 更小更尖锐的粒子（通过更大的变化幅度）
        center = 0.5
        sharpness = map_range(self.focus_ratio, 0.0, 1.0, 0.3, 0.5)  # 分心时更陡峭
        radius_scale = 2.0 * (sharpness + (center - sharpness) - abs(position_in_segment - center))
        radius_scale = clamp(radius_scale, 0.0, 1.0)
        radius = self.max_radius * radius_scale
        
        return colors[index], radius
    
    def _rotate_point(self, x: float, y: float, angle: float) -> Tuple[float, float]:
        """二维旋转变换"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
    
    def update_and_draw(self):
        """更新并绘制一帧罗夏墨迹图"""
        
        # 1. 拖尾效果：覆盖半透明白色层
        self.buffer.blit(self.fade_surface, (0, 0))
        
        buffer_center_x = self.buffer.get_width() / 2
        buffer_center_y = self.buffer.get_height() * 0.55  # 稍微偏下，更像罗夏图
        
        # 2. 粒子系统
        for _ in range(self.n_plotters):
            # 生成随机种子用于噪声采样
            seed_a = random.random() * 100
            seed_b = random.random() * 100
            
            # 使用 Perlin 噪声生成对称坐标
            # noise(a, b) 和 noise(b, a) 产生关于对角线对称的点
            n1 = pnoise3(seed_a, seed_b, 0, octaves=self.noise_octaves)
            n2 = pnoise3(seed_b, seed_a, 0, octaves=self.noise_octaves)
            
            # 映射到画布尺寸并应用扩散系数
            x0 = n1 * self.size * self.spread
            y0 = n2 * self.size * self.spread
            
            # 旋转坐标：将对角线对称转换为垂直轴对称 (-135度)
            rotation_angle = -3 * math.pi / 4
            x, y = self._rotate_point(x0, y0, rotation_angle)
            
            # 基于位置和时间采样噪声场，决定颜色
            # 分心时使用更多octaves产生更尖锐的噪声
            noise_val = pnoise3(
                x * self.scale,
                y * self.scale,
                self.frame_count * self.speed,
                octaves=self.noise_octaves,
                persistence=0.5
            )
            # 归一化到 0-1
            noise_val = (noise_val + 1.0) / 2.0
            noise_val = clamp(noise_val, 0.0, 1.0)
            
            color, radius = self._get_color_palette(noise_val)
            
            # 只绘制有效半径的粒子
            if radius > 0.5:
                screen_x = int(x + buffer_center_x)
                screen_y = int(y + buffer_center_y)
                
                # 确保在缓冲区范围内
                if 0 <= screen_x < self.buffer.get_width() and 0 <= screen_y < self.buffer.get_height():
                    pygame.draw.circle(
                        self.buffer,
                        color[:3],  # RGB (不含alpha，直接绘制)
                        (screen_x, screen_y),
                        int(radius)
                    )
        
        # 3. 应用圆角遮罩并绘制到主表面
        # 创建输出表面
        output = pygame.Surface(self.buffer.get_size(), pygame.SRCALPHA)
        output.fill((0, 0, 0, 0))
        
        # 使用遮罩裁剪缓冲区
        output.blit(self.buffer, (0, 0))
        output.blit(self.mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        self.surface.blit(output, self.draw_rect.topleft)
        
        self.frame_count += 1
    
    def reset(self):
        """重置渲染状态"""
        self.frame_count = 0
        self.buffer.fill((255, 255, 255, 255))


# =============================================================================
# Combined Focus Report Visualizer - 整合版本
# =============================================================================

class FocusReportWithRorschach:
    """
    整合罗夏墨迹图的完整报告可视化器。
    
    网格布局（参考 Lorem Ipsum 设计）：
    - 浅灰白色背景
    - 顶部：导航栏
    - 左侧：大标题文字区域
    - 右上：圆形可视化区域（罗夏墨迹图）
    - 右下：描述文字区域
    - 底部：大字母装饰
    """
    
    def __init__(
        self,
        focus_score: float,
        distraction_count: int = 5,
        error_count: int = 0,
        metrics: Optional[Dict[str, float | str]] = None,
        title: str = "Focus Report",
        window_size: Tuple[int, int] = (1280, 720),  # 横屏 16:9 比例
    ):
        self.focus_score = clamp(focus_score, 0.0, 100.0)
        self.focus_ratio = self.focus_score / 100.0
        self.distraction_count = distraction_count
        self.error_count = error_count
        self.metrics = metrics or {}
        self.title = title
        self.window_size = window_size
        
        pygame.init()
        self.screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # 字体 - 参考图片使用大号衬线字体
        self.hero_font = pygame.font.SysFont(["georgia", "times", "serif"], 58, bold=False)
        self.title_font = pygame.font.SysFont(["georgia", "times", "serif"], 42, bold=False)
        self.score_font = pygame.font.SysFont(FONT_CHOICES, 120, bold=True)
        self.nav_font = pygame.font.SysFont(FONT_CHOICES, 14)
        self.body_font = pygame.font.SysFont(["georgia", "times", "serif"], 15)
        self.small_font = pygame.font.SysFont(FONT_CHOICES, 12)
        self.watermark_font = pygame.font.SysFont(["arial", "helvetica", "sans-serif"], 180, bold=True)
        
        # 颜色配置 - 参考图片的浅灰白色调
        self.bg_color = (245, 243, 240)  # 浅灰白背景
        self.text_color = (60, 60, 65)   # 深灰文字
        self.light_text = (160, 160, 165) # 浅灰文字
        self.accent_color = (200, 195, 190) # 装饰色
        
        # 初始化罗夏图渲染器
        self._init_rorschach()
    
    def _init_rorschach(self):
        """初始化罗夏墨迹图渲染器 - 放置在右侧中间位置，占画面2/3"""
        w, h = self.screen.get_size()
        
        # 网格布局计算
        self.nav_height = 50
        self.left_col_width = w * 0.33  # 左侧文字区域占1/3
        self.right_col_width = w - self.left_col_width  # 右侧可视化区域占2/3
        
        # 圆形可视化区域 - 居中于右侧区域（垂直居中）
        blob_size = min(self.right_col_width * 0.75, h * 0.8)
        
        # 圆心位置 - 右侧区域的中心
        center_x = self.left_col_width + self.right_col_width / 2
        center_y = h / 2
        
        self.rorschach = RorschachBlob(
            surface=self.screen,
            center_x=center_x,
            center_y=center_y,
            size=blob_size,
            focus_score=self.focus_score,
            distraction_count=self.distraction_count,
            error_count=self.error_count,
        )
        
        # 保存圆形区域信息用于绘制背景圆
        self.circle_center = (int(center_x), int(center_y))
        self.circle_radius = int(blob_size * 0.95)
    
    def _draw_nav_bar(self, w, h):
        """绘制顶部导航栏 - 参考图片风格"""
        # 导航栏背景（与主背景同色，通过分隔线区分）
        nav_y = self.nav_height
        
        # 左侧导航文字
        nav_items_left = ["Lorem Ipsum", "dolor"]
        x = 30
        for item in nav_items_left:
            text = self.nav_font.render(item, True, self.text_color)
            self.screen.blit(text, (x, (nav_y - text.get_height()) // 2))
            x += text.get_width() + 25
        
        # 中间导航文字
        nav_items_center = ["Lorem", "Cotohl", "Losole", "Conloh"]
        total_width = sum(self.nav_font.size(item)[0] for item in nav_items_center) + 60
        x = w // 2 - total_width // 2
        for item in nav_items_center:
            text = self.nav_font.render(item, True, self.light_text)
            self.screen.blit(text, (x, (nav_y - text.get_height()) // 2))
            x += text.get_width() + 20
        
        # 右侧导航文字
        right_text = self.nav_font.render("DNIO VCIO foro", True, self.light_text)
        self.screen.blit(right_text, (w - right_text.get_width() - 30, (nav_y - right_text.get_height()) // 2))
        
        # 底部分隔线
        pygame.draw.line(self.screen, self.accent_color, (0, nav_y), (w, nav_y), 1)
    
    def _draw_left_content(self, w, h):
        """绘制左侧大标题区域 - 参考图片的 Lorem Ipsum 风格"""
        content_x = 30
        content_y = h * 0.25  # 垂直居中偏上
        
        # 根据专注度选择标题
        if self.focus_ratio > 0.7:
            line1 = "Focus"
            line2 = "Achieved."
        elif self.focus_ratio > 0.4:
            line1 = "Stay"
            line2 = "Focused."
        else:
            line1 = "Need"
            line2 = "Focus."
        
        # 第一行大标题
        title1 = self.hero_font.render(line1, True, self.text_color)
        self.screen.blit(title1, (content_x, content_y))
        
        # 第二行大标题（带点缀）
        title2 = self.hero_font.render(line2, True, self.text_color)
        self.screen.blit(title2, (content_x, content_y + title1.get_height() + 5))
        
        # 分隔线
        line_y = content_y + title1.get_height() * 2 + 40
        pygame.draw.line(self.screen, self.accent_color, (content_x, line_y), (self.left_col_width - 20, line_y), 1)
        
        # 左侧底部描述区域
        desc_y = line_y + 30
        
        # 描述文字
        desc_lines = [
            f"Score: {self.focus_score:.0f}/100",
            f"Duration: {self.metrics.get('Duration', '00:00')}",
            f"Distractions: {self.distraction_count}",
        ]
        
        for line in desc_lines:
            line_surf = self.small_font.render(line, True, self.light_text)
            self.screen.blit(line_surf, (content_x, desc_y))
            desc_y += 22
        
        # 底部提示
        desc_y += 20
        link_text = self.small_font.render("Press ESC to close", True, self.light_text)
        self.screen.blit(link_text, (content_x, desc_y))
    
    def _draw_right_description(self, w, h):
        """绘制右下角描述文字区域"""
        # 描述区域位置（圆形下方）
        desc_x = self.left_col_width + 40
        desc_y = h * 0.6
        desc_width = self.right_col_width - 80
        
        # 标题
        if self.focus_ratio > 0.7:
            desc_title = "Excellent concentration achieved."
        elif self.focus_ratio > 0.4:
            desc_title = "Good focus with room to improve."
        else:
            desc_title = "Focus needs improvement."
        
        title_surf = self.body_font.render(desc_title, True, self.text_color)
        self.screen.blit(title_surf, (desc_x, desc_y))
        
        # 描述文字（多行）
        desc_lines = [
            f"Score: {self.focus_score:.0f}/100",
            f"Duration: {self.metrics.get('Duration', '00:00')}",
            f"Distractions: {self.distraction_count}",
        ]
        
        y = desc_y + 30
        for line in desc_lines:
            line_surf = self.small_font.render(line, True, self.light_text)
            self.screen.blit(line_surf, (desc_x, y))
            y += 22
        
        # 底部链接风格文字
        link_text = self.small_font.render("Press ESC to close", True, self.light_text)
        self.screen.blit(link_text, (desc_x, y + 15))
    
    def _draw_circle_background(self, w, h):
        """绘制灰色圆形背景（可视化动态的容器）"""
        # 浅灰色圆形背景
        circle_color = (215, 212, 208)  # 参考图片中的灰色圆
        pygame.draw.circle(self.screen, circle_color, self.circle_center, self.circle_radius)
    
    def _draw_bottom_watermark(self, w, h):
        """绘制底部大字母水印 - 参考图片的 IPSUM 风格"""
        # 水印文字
        watermark = "FOCUS"
        watermark_surf = self.watermark_font.render(watermark, True, self.accent_color)
        
        # 位置：底部居中，部分超出屏幕
        watermark_x = w // 2 - watermark_surf.get_width() // 2
        watermark_y = h - watermark_surf.get_height() // 2 - 20
        
        self.screen.blit(watermark_surf, (watermark_x, watermark_y))
    
    def _draw_score_display(self, w, h):
        """绘制分数显示 - 放在圆形内部中心"""
        # 分数颜色渐变
        score_warm = hex_to_rgb("#d30c7b")
        score_cool = hex_to_rgb("#086788")
        score_color = lerp_color(score_warm, score_cool, self.focus_ratio)
        
        # 大分数
        score_text = self.score_font.render(f"{self.focus_score:.0f}", True, score_color)
        score_rect = score_text.get_rect(center=self.circle_center)
        self.screen.blit(score_text, score_rect)
    
    def _draw_grid_lines(self, w, h):
        """绘制网格参考线 - 左侧1/3和右侧2/3的分隔"""
        # 垂直分隔线 - 在左侧1/3位置
        pygame.draw.line(self.screen, (230, 228, 225), 
                        (self.left_col_width, 0), 
                        (self.left_col_width, h), 1)
    
    def run(self):
        """运行可视化主循环"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 点击重置罗夏图
                    self.rorschach.reset()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self._init_rorschach()
            
            w, h = self.screen.get_size()
            
            # 1. 绘制浅灰白色背景
            self.screen.fill(self.bg_color)
            
            # 2. 绘制网格分隔线
            self._draw_grid_lines(w, h)
            
            # 3. 绘制底部大字母水印（在其他内容之下）
            self._draw_bottom_watermark(w, h)
            
            # 4. 绘制灰色圆形背景
            self._draw_circle_background(w, h)
            
            # 5. 绘制罗夏墨迹图（透明背景，叠加在灰色圆上）
            self.rorschach.update_and_draw()
            
            # 6. 绘制导航栏
            self._draw_nav_bar(w, h)
            
            # 7. 绘制左侧大标题和描述
            self._draw_left_content(w, h)
            
            pygame.display.flip()
            self.clock.tick(FRAME_RATE)
        
        pygame.quit()


def run_rorschach_report(
    focus_score: float,
    distraction_count: int = 5,
    error_count: int = 0,
    metrics: Optional[Dict[str, float | str]] = None,
) -> None:
    """
    便捷函数：启动带有罗夏墨迹图的专注力报告。
    
    Args:
        focus_score: 专注分数 (0-100)
        distraction_count: 分心次数
        error_count: 错误次数
        metrics: 其他要显示的指标
    """
    visualizer = FocusReportWithRorschach(
        focus_score=focus_score,
        distraction_count=distraction_count,
        error_count=error_count,
        metrics=metrics,
    )
    visualizer.run()


if __name__ == "__main__":
    # 从命令行参数获取分数，默认为 50
    import sys
    
    if len(sys.argv) > 1:
        try:
            focus_score = float(sys.argv[1])
        except ValueError:
            focus_score = 50.0
    else:
        focus_score = 50.0
    
    sample_metrics = {
        "Duration": "02:35",
        "Errors": 3,
        "Distractions": 7,
    }
    
    # 使用命令行传入的分数
    print(f"Running with focus_score = {focus_score}")
    
    run_rorschach_report(
        focus_score=focus_score,
        distraction_count=int(7 * (1 - focus_score/100)),  # 根据分数动态调整
        error_count=int(5 * (1 - focus_score/100)),        # 根据分数动态调整
        metrics=sample_metrics,
    )
