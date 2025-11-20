import pygame
import cv2
import numpy as np
import threading
import time
import collections
import math
import mediapipe as mp
import random


def draw_pupil_eye(screen, x, y, radius, time_factor=0):
    """绘制瞳孔样式的眼睛"""
    center_x, center_y = int(x), int(y)
    
    # 瞳孔大小（中心黑色部分）
    pupil_radius = max(3, int(radius * 0.3))
    
    # 虹膜外圈
    iris_radius = int(radius)
    
    # 绘制虹膜背景渐变
    for r in range(iris_radius, pupil_radius, -1):
        # 计算距离比例
        distance_ratio = (r - pupil_radius) / (iris_radius - pupil_radius)
        
        # 基础颜色 - 从外到内的渐变
        hue = (0.1 + distance_ratio * 0.2 + time_factor * 0.1) % 1.0  # 棕色到浅棕色
        saturation = 0.6 + distance_ratio * 0.3
        brightness = 0.4 + distance_ratio * 0.5
        
        color = hsv_to_rgb(hue, saturation, brightness)
        pygame.draw.circle(screen, color, (center_x, center_y), r)
    
    # 绘制放射状虹膜纹理
    num_rays = 48  # 增加射线数量获得更细致效果
    for i in range(num_rays):
        angle = (i / num_rays) * 2 * math.pi + time_factor * 0.3
        
        # 计算射线的起点和终点
        inner_r = pupil_radius + 2
        outer_r = iris_radius - 2
        
        # 射线的颜色变化
        ray_hue = (0.15 + (i % 8) * 0.02 + time_factor * 0.05) % 1.0
        ray_brightness = 0.3 + (i % 3) * 0.2
        ray_color = hsv_to_rgb(ray_hue, 0.8, ray_brightness)
        
        # 绘制多条细射线形成纤维效果
        for j in range(3):
            offset_angle = angle + (j - 1) * 0.02
            
            start_x = center_x + inner_r * math.cos(offset_angle)
            start_y = center_y + inner_r * math.sin(offset_angle)
            end_x = center_x + outer_r * math.cos(offset_angle)
            end_y = center_y + outer_r * math.sin(offset_angle)
            
            # 绘制射线（使用线条粗细变化）
            line_width = max(1, int(radius * 0.03))
            if j == 1:  # 中间线条更亮
                pygame.draw.line(screen, ray_color, (start_x, start_y), (end_x, end_y), line_width)
            else:  # 侧边线条较暗
                darker_color = tuple(int(c * 0.7) for c in ray_color)
                pygame.draw.line(screen, darker_color, (start_x, start_y), (end_x, end_y), max(1, line_width // 2))
    
    # 绘制虹膜环状纹理
    for ring in range(3):
        ring_radius = pupil_radius + (iris_radius - pupil_radius) * (0.3 + ring * 0.25)
        ring_color = hsv_to_rgb((0.12 + ring * 0.03 + time_factor * 0.02) % 1.0, 0.7, 0.6 - ring * 0.1)
        
        # 绘制不完整的圆环（创造自然的纹理）
        for segment in range(0, 360, 15):
            if (segment + int(time_factor * 10)) % 45 < 30:  # 创造间断效果
                start_angle = math.radians(segment)
                end_angle = math.radians(segment + 10)
                
                points = []
                for a in range(segment, segment + 10, 2):
                    rad = math.radians(a)
                    px = center_x + ring_radius * math.cos(rad)
                    py = center_y + ring_radius * math.sin(rad)
                    points.append((px, py))
                
                if len(points) > 1:
                    pygame.draw.lines(screen, ring_color, False, points, max(1, int(radius * 0.02)))
    
    # 绘制瞳孔（黑色中心）
    pygame.draw.circle(screen, (20, 20, 25), (center_x, center_y), pupil_radius)
    
    # 瞳孔高光
    highlight_x = center_x - pupil_radius // 3
    highlight_y = center_y - pupil_radius // 3
    highlight_radius = max(1, pupil_radius // 4)
    pygame.draw.circle(screen, (180, 180, 200), (highlight_x, highlight_y), highlight_radius)
    
    # 虹膜外圈边界
    pygame.draw.circle(screen, (100, 80, 60), (center_x, center_y), iris_radius, 2)


class InterferenceRenderer:
    """干扰区渲染器 - 在焦点区域外生成随机波形噪点"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.wave_sources = []  # 波形源点
        self.noise_points = []  # 噪点
        self.last_update = 0
        self.update_interval = 0.08  # 减少到80ms，增强动态感
        
    def update_interference(self, current_time, metaball_renderer):
        """更新干扰效果"""
        if current_time - self.last_update < self.update_interval:
            return
            
        # 清空之前的干扰
        self.wave_sources = []
        self.noise_points = []
        
        # 随机生成波形源点（增强视觉效果）
        num_wave_sources = random.randint(8, 12)  # 增加数量提升视觉张力
        for _ in range(num_wave_sources):
            x = random.randint(30, self.width - 30)
            y = random.randint(30, self.height - 30)
            
            # 检查是否在焦点区域外
            if not metaball_renderer.is_point_in_focus_area(x, y):
                intensity = random.uniform(0.6, 1.5)  # 增强强度范围
                frequency = random.uniform(0.8, 3.0)  # 增加频率范围
                wave_type = random.choice(['radial', 'spiral', 'flow', 'burst', 'web', 'chaos'])
                color_hue = random.uniform(0.0, 1.0)
                scale = random.uniform(0.8, 2.5)  # 增大尺度变化范围
                
                self.wave_sources.append({
                    'x': x, 'y': y, 'intensity': intensity, 
                    'frequency': frequency, 'type': wave_type,
                    'hue': color_hue, 'phase': random.uniform(0, 6.28),
                    'scale': scale, 'rotation': random.uniform(0, 6.28)
                })
        
        # 随机生成单个噪点（增强密度）
        num_noise = random.randint(60, 100)  # 增加噪点数量
        for _ in range(num_noise):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            
            # 只在焦点区域外生成噪点
            if not metaball_renderer.is_point_in_focus_area(x, y):
                size = random.randint(1, 5)  # 增大尺寸范围
                alpha = random.uniform(0.3, 0.9)  # 增强透明度
                color = (random.randint(80, 255), random.randint(80, 255), random.randint(100, 255))
                effect_type = random.choice(['dot', 'cross', 'star'])  # 添加不同类型
                
                self.noise_points.append({
                    'x': x, 'y': y, 'size': size, 
                    'color': color, 'alpha': alpha, 'type': effect_type
                })
                
        self.last_update = current_time
    
    def render_wave_patterns(self, screen, current_time):
        """渲染波形图案"""
        for source in self.wave_sources:
            if source['type'] == 'radial':
                self.draw_radial_waves(screen, source, current_time)
            elif source['type'] == 'spiral':
                self.draw_spiral_waves(screen, source, current_time)
            elif source['type'] == 'flow':
                self.draw_flow_lines(screen, source, current_time)
            elif source['type'] == 'burst':
                self.draw_burst_pattern(screen, source, current_time)
            elif source['type'] == 'web':
                self.draw_web_pattern(screen, source, current_time)
            elif source['type'] == 'chaos':
                self.draw_chaos_lines(screen, source, current_time)
    
    def draw_radial_waves(self, screen, source, current_time):
        """绘制增强的放射状波形"""
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        rotation = source['rotation'] + current_time * 0.5
        
        # 增加到3层效果
        for layer in range(3):
            layer_offset = layer * 0.4
            for angle in range(0, 360, 6):  # 增加密度到6度
                rad = math.radians(angle + rotation * 25)
                intensity_variation = math.sin(phase + angle * 0.05 + layer_offset) * 0.5 + 0.8
                base_length = 50 + layer * 25  # 增大基础长度
                length = base_length + intensity_variation * 80 * source['scale']  # 增大波动幅度
                
                end_x = center_x + length * math.cos(rad)
                end_y = center_y + length * math.sin(rad)
                
                # 计算颜色
                color_intensity = source['intensity'] * intensity_variation * (1 - layer * 0.2)
                hue = (source['hue'] + angle * 0.008 + layer * 0.15) % 1.0
                color = hsv_to_rgb(hue, 0.8, min(1.0, color_intensity))
                
                # 绘制更粗的线条
                if (0 <= end_x <= self.width and 0 <= end_y <= self.height):
                    line_width = max(1, 3 - layer)
                    pygame.draw.line(screen, color, (center_x, center_y), (end_x, end_y), line_width)
    
    def draw_burst_pattern(self, screen, source, current_time):
        """绘制增强的爆发式图案"""
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        
        # 增加到5个爆发效果
        for burst in range(5):
            burst_phase = phase + burst * 1.2
            burst_radius = 25 + burst * 35 + math.sin(burst_phase) * 20  # 增大半径
            
            points = []
            for angle in range(0, 360, 12):  # 增加密度
                rad = math.radians(angle)
                variation = math.sin(burst_phase + angle * 0.1) * 0.5 + 1.0
                r = burst_radius * variation * source['scale']
                
                x = center_x + r * math.cos(rad)
                y = center_y + r * math.sin(rad)
                
                if 0 <= x <= self.width and 0 <= y <= self.height:
                    points.append((x, y))
            
            if len(points) > 2:
                color = hsv_to_rgb((source['hue'] + burst * 0.15) % 1.0, 0.9, 
                                  source['intensity'] * (1 - burst * 0.15))
                try:
                    line_width = max(1, 3 - burst)
                    pygame.draw.lines(screen, color, True, points, line_width)
                except:
                    pass
    
    def draw_web_pattern(self, screen, source, current_time):
        """绘制增强的网状图案"""
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        
        # 增大网格结构
        web_points = []
        for ring in range(1, 6):  # 增加到5圈
            ring_radius = ring * 30 * source['scale']  # 增大半径
            for angle in range(0, 360, 30):  # 增加密度
                rad = math.radians(angle)
                noise = math.sin(phase + angle * 0.05 + ring * 0.3) * 10  # 增大噪声
                r = ring_radius + noise
                
                x = center_x + r * math.cos(rad)
                y = center_y + r * math.sin(rad)
                web_points.append((x, y, ring, angle))
        
        # 绘制更多连接线
        for i, (x1, y1, ring1, angle1) in enumerate(web_points):
            if 0 <= x1 <= self.width and 0 <= y1 <= self.height:
                for x2, y2, ring2, angle2 in web_points[i+1:]:
                    if (abs(ring1 - ring2) <= 1 or abs(angle1 - angle2) <= 60) and \
                       0 <= x2 <= self.width and 0 <= y2 <= self.height:
                        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                        if distance < 100:  # 增大连接距离
                            alpha = max(0.15, 1 - distance / 100)
                            color_val = source['intensity'] * alpha
                            color = hsv_to_rgb(source['hue'], 0.7, color_val)
                            line_width = max(1, int(2 - distance / 50))
                            pygame.draw.line(screen, color, (x1, y1), (x2, y2), line_width)
    
    def draw_chaos_lines(self, screen, source, current_time):
        """绘制增强的混沌线条"""
        start_x, start_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        
        # 增加混沌路径数量
        for path in range(6):  # 增加到6条
            points = [(start_x, start_y)]
            current_x, current_y = start_x, start_y
            path_phase = phase + path * 0.8
            
            for step in range(30):  # 增加到30步
                # 增强的噪声函数
                chaos_x = math.sin(current_x * 0.025 + path_phase) * math.cos(step * 0.15) * 25
                chaos_y = math.cos(current_y * 0.02 + path_phase * 1.2) * math.sin(step * 0.12) * 25
                
                current_x += chaos_x * source['scale']
                current_y += chaos_y * source['scale']
                
                if 0 <= current_x <= self.width and 0 <= current_y <= self.height:
                    points.append((current_x, current_y))
                else:
                    break
            
            if len(points) > 3:
                color = hsv_to_rgb((source['hue'] + path * 0.12) % 1.0, 
                                  0.8, source['intensity'] * 0.9)
                try:
                    line_width = max(1, 2 - path // 3)
                    pygame.draw.lines(screen, color, False, points, line_width)
                except:
                    pass

    def draw_spiral_waves(self, screen, source, current_time):
        """绘制螺旋波形（模仿第一个图）"""
        center_x, center_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        
        points = []
        for i in range(0, 100, 2):
            angle = i * 0.2 + phase
            radius = i * 0.8 + math.sin(angle * 0.5 + phase) * 10
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            if 0 <= x <= self.width and 0 <= y <= self.height:
                points.append((x, y))
        
        if len(points) > 3:
            color = hsv_to_rgb(source['hue'], 0.6, source['intensity'])
            try:
                pygame.draw.lines(screen, color, False, points, 1)
            except:
                pass
    
    def draw_flow_lines(self, screen, source, current_time):
        """绘制流动线条（模仿流体效果）"""
        start_x, start_y = source['x'], source['y']
        phase = source['phase'] + current_time * source['frequency']
        
        # 生成流动路径
        points = [(start_x, start_y)]
        current_x, current_y = start_x, start_y
        
        for step in range(20):
            # 根据噪声函数计算下一个点
            noise_x = math.sin(current_x * 0.02 + phase) + math.cos(current_y * 0.03 + phase * 0.7)
            noise_y = math.cos(current_x * 0.025 + phase * 1.3) + math.sin(current_y * 0.02 + phase)
            
            current_x += noise_x * 8
            current_y += noise_y * 8
            
            if 0 <= current_x <= self.width and 0 <= current_y <= self.height:
                points.append((current_x, current_y))
            else:
                break
        
        if len(points) > 2:
            color = hsv_to_rgb((source['hue'] + step * 0.02) % 1.0, 0.5, source['intensity'])
            try:
                pygame.draw.lines(screen, color, False, points, 1)
            except:
                pass
    
    def render_noise_points(self, screen):
        """渲染增强的噪点效果"""
        for point in self.noise_points:
            if point['type'] == 'dot':
                # 普通圆点
                surf = pygame.Surface((point['size'] * 2, point['size'] * 2))
                surf.set_alpha(int(point['alpha'] * 255))
                surf.fill(point['color'])
                screen.blit(surf, (point['x'] - point['size'], point['y'] - point['size']))
                
            elif point['type'] == 'cross':
                # 十字形
                color = (*point['color'], int(point['alpha'] * 255))
                size = point['size']
                x, y = point['x'], point['y']
                
                # 横线
                pygame.draw.line(screen, point['color'], (x-size, y), (x+size, y), 2)
                # 竖线  
                pygame.draw.line(screen, point['color'], (x, y-size), (x, y+size), 2)
                
            elif point['type'] == 'star':
                # 星形
                size = point['size']
                x, y = point['x'], point['y']
                
                # 8方向的星形
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    end_x = x + size * math.cos(rad)
                    end_y = y + size * math.sin(rad)
                    pygame.draw.line(screen, point['color'], (x, y), (end_x, end_y), 1)
    
    def render(self, screen, metaball_renderer):
        """渲染干扰效果"""
        current_time = time.time()
        self.update_interference(current_time, metaball_renderer)
        
        # 渲染波形图案
        self.render_wave_patterns(screen, current_time)
        
        # 渲染噪点
        self.render_noise_points(screen)


def hsv_to_rgb(h, s, v):
    """HSV颜色空间转RGB"""
    # 确保输入值在有效范围内
    h = max(0.0, min(1.0, h)) % 1.0
    s = max(0.0, min(1.0, s))
    v = max(0.0, min(1.0, v))
    
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    
    if i == 0:
        r, g, b = int(v * 255), int(t * 255), int(p * 255)
    elif i == 1:
        r, g, b = int(q * 255), int(v * 255), int(p * 255)
    elif i == 2:
        r, g, b = int(p * 255), int(v * 255), int(t * 255)
    elif i == 3:
        r, g, b = int(p * 255), int(q * 255), int(v * 255)
    elif i == 4:
        r, g, b = int(t * 255), int(p * 255), int(v * 255)
    else:
        r, g, b = int(v * 255), int(p * 255), int(q * 255)
    
    # 确保RGB值在0-255范围内
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


class Metaball:
    """元球类 - 创建流动的有机形状"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # 小半径范围，创建局部焦点区域
        size = random.random() ** 1.2  # 调整分布，更多中大尺寸
        self.radius = 80 * size + 60   # 小半径范围：60-140
        
        # 更大的速度范围，让边界变化更动感
        speed = 3.5 * (1 - size) + 1.5  # 进一步增大速度范围
        angle = random.random() * 2 * math.pi
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        
        # 初始位置在屏幕中心小范围，创建局部焦点区域
        self.pos_x = width / 2 + random.randint(-80, 80)
        self.pos_y = height / 2 + random.randint(-60, 60)
    
    def update(self):
        """更新元球位置"""
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        
        # 边界碰撞反弹
        if self.pos_x < self.radius or self.pos_x > self.width - self.radius:
            self.vel_x *= -1
        if self.pos_y < self.radius or self.pos_y > self.height - self.radius:
            self.vel_y *= -1
        
        # 确保位置在边界内
        self.pos_x = max(self.radius, min(self.width - self.radius, self.pos_x))
        self.pos_y = max(self.radius, min(self.height - self.radius, self.pos_y))


class MetaballRenderer:
    """元球渲染器 - 生成流动的彩虹边界"""
    
    def __init__(self, width, height, num_balls=2):  # 减少到2个元球创建局部区域
        self.width = width
        self.height = height
        self.num_balls = num_balls
        self.metaballs = []
        
        # 创建元球
        for _ in range(num_balls):
            self.metaballs.append(Metaball(width, height))
        
        # 用于缓存边界点
        self.boundary_points = []
        self.boundary_colors = []
        self.last_update_time = 0
        self.update_interval = 0.05  # 每50ms更新一次边界
    
    def update_size(self, width, height):
        """更新渲染器尺寸"""
        old_width, old_height = self.width, self.height
        self.width = width
        self.height = height
        
        # 按比例调整元球位置
        for ball in self.metaballs:
            ball.width = width
            ball.height = height
            ball.pos_x = ball.pos_x * width / old_width
            ball.pos_y = ball.pos_y * height / old_height
    
    def compute_metaball_value(self, x, y):
        """计算某点的元球值"""
        v = 0.0
        for ball in self.metaballs:
            dx = ball.pos_x - x
            dy = ball.pos_y - y
            r_squared = ball.radius * ball.radius
            distance_squared = dx * dx + dy * dy
            
            if distance_squared > 0:
                v += r_squared / distance_squared
        return v
    
    def update_boundary(self):
        """更新边界点（优化版本）"""
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return
        
        # 更新元球位置
        for ball in self.metaballs:
            ball.update()
        
        self.boundary_points = []
        self.boundary_colors = []
        
        # 采样密度和阈值设置
        step = 4  # 精细采样获得清晰边界
        threshold_min = 0.6    # 较高阈值创建明确的局部区域
        threshold_max = 0.8    # 高阈值范围，创建紧凑的焦点区域
        
        for x in range(0, self.width, step):
            for y in range(0, self.height, step):
                v = self.compute_metaball_value(x, y)
                
                if threshold_min < v < threshold_max:
                    # 计算彩虹颜色
                    a = (v - threshold_min) / (threshold_max - threshold_min)
                    hue = (a + current_time * 0.2) % 1.0  # 时间驱动的色彩变化
                    color = hsv_to_rgb(hue, 1.0, 1.0)
                    
                    self.boundary_points.append((x, y))
                    self.boundary_colors.append(color)
        
        self.last_update_time = current_time
    
    def is_point_in_focus_area(self, x, y):
        """检查点是否在焦点区域内"""
        v = self.compute_metaball_value(x, y)
        return v >= 0.7  # 高阈值创建局部焦点区域
    
    def render(self, screen):
        """渲染元球边界"""
        self.update_boundary()
        
        # 绘制边界点
        for i, point in enumerate(self.boundary_points):
            color = self.boundary_colors[i]
            # 绘制更小的点使边界更细致，但仍然可见
            pygame.draw.circle(screen, color, point, 2)  # 减小到2像素


class GazeProvider:
    """凝视位置提供者基类"""
    
    def __init__(self, screen_width, screen_height):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.position_history = collections.deque(maxlen=10)
        
        # 小球大小相关属性
        self.initial_radius = 15  # 增大初始半径到15px，让瞳孔更明显
        self.current_radius = self.initial_radius
        self.max_radius = 60  # 相应增大最大半径到60px
        self.growth_rate = 1.0  # 增大每秒增长速度到1.0像素
        
        # 自动运动相关属性
        self.velocity_x = random.uniform(-2, 2)  # X方向速度
        self.velocity_y = random.uniform(-2, 2)  # Y方向速度
        self.max_speed = 3.0  # 最大速度
        self.friction = 0.99  # 摩擦系数
        self.auto_movement = False  # 禁用自动运动，启用手指控制
        
        # 边界碰撞计数
        self.boundary_collision_count = 0
        self.last_in_focus = True  # 上一帧是否在焦点区域内
        
    def get_position(self):
        return (self.x, self.y)
    
    def get_radius(self):
        """获取当前小球半径"""
        return self.current_radius
    
    def get_boundary_collisions(self):
        """获取边界碰撞次数"""
        return self.boundary_collision_count
    
    def check_focus_boundary_collision(self, metaball_renderer):
        """检查小球是否碰到焦点区域边界（内外边界）"""
        # 检测小球边缘上的多个点是否在焦点区域内
        center_x, center_y = self.x, self.y
        radius = self.current_radius
        
        # 在小球周围检查8个点
        angles = [i * 45 for i in range(8)]  # 0, 45, 90, 135, 180, 225, 270, 315度
        
        points_in_focus = 0
        total_points = len(angles)
        
        for angle in angles:
            rad = math.radians(angle)
            check_x = center_x + radius * math.cos(rad)
            check_y = center_y + radius * math.sin(rad)
            
            if metaball_renderer.is_point_in_focus_area(check_x, check_y):
                points_in_focus += 1
        
        # 如果部分点在区域内，部分点在区域外，则认为碰到边界
        currently_touching_boundary = 0 < points_in_focus < total_points
        
        # 如果从不碰边界变成碰边界，计数
        if not hasattr(self, 'last_touching_boundary'):
            self.last_touching_boundary = False
            
        if not self.last_touching_boundary and currently_touching_boundary:
            self.boundary_collision_count += 1
            print(f"小球碰到焦点边界！第 {self.boundary_collision_count} 次 (部分边缘超出区域)")
        
        self.last_touching_boundary = currently_touching_boundary
        
        # 返回中心点是否在焦点区域内（用于得分）
        return metaball_renderer.is_point_in_focus_area(center_x, center_y)
    
    def update_ball_size(self, elapsed_time):
        """根据游戏时间更新小球大小"""
        # 计算当前应有的半径
        target_radius = min(self.initial_radius + elapsed_time * self.growth_rate, self.max_radius)
        # 平滑过渡到目标半径
        self.current_radius = self.current_radius * 0.98 + target_radius * 0.02
        return self.current_radius
    
    def reset_position(self, width, height):
        """重置小球到屏幕中心（焦点区域中心）"""
        # 确保初始位置在屏幕中心，在焦点区域内
        self.x = width // 2
        self.y = height // 2
        self.position_history.clear()
        self.current_radius = self.initial_radius  # 重置小球大小
        # 重置速度为随机方向
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-2, 2)
        # 重置碰撞计数
        self.boundary_collision_count = 0
        self.last_in_focus = True
        self.last_touching_boundary = False  # 重置边界磨到状态
        print(f"小球重置到焦点区域中心: ({self.x}, {self.y})，大小重置为 {self.initial_radius}，新速度: ({self.velocity_x:.1f}, {self.velocity_y:.1f})，碰撞计数重置")
    
    def update(self, width, height):
        if self.auto_movement:
            # 自动物理运动
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            # 边界碰撞反弹
            if self.x <= self.current_radius or self.x >= width - self.current_radius:
                self.velocity_x *= -0.8  # 反弹时损失一些能量
                self.x = max(self.current_radius, min(width - self.current_radius, self.x))
            
            if self.y <= self.current_radius or self.y >= height - self.current_radius:
                self.velocity_y *= -0.8
                self.y = max(self.current_radius, min(height - self.current_radius, self.y))
            
            # 添加一点随机扰动让运动更有趣
            self.velocity_x += random.uniform(-0.1, 0.1)
            self.velocity_y += random.uniform(-0.1, 0.1)
            
            # 限制最大速度
            speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            if speed > self.max_speed:
                self.velocity_x = self.velocity_x / speed * self.max_speed
                self.velocity_y = self.velocity_y / speed * self.max_speed
            
            # 应用摩擦力
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction
        
        # 严格边界检查和紧急重置
        boundary_margin = 30
        if (self.x < -boundary_margin or self.x > width + boundary_margin or 
            self.y < -boundary_margin or self.y > height + boundary_margin):
            print(f"边界紧急重置: 位置({self.x:.1f}, {self.y:.1f}) -> 中心")
            self.x = width // 2
            self.y = height // 2
            # 重置速度
            self.velocity_x = random.uniform(-2, 2)
            self.velocity_y = random.uniform(-2, 2)
            return (self.x, self.y)
        
        return (self.x, self.y)


class HandGazeProvider(GazeProvider):
    """使用MediaPipe检测手指位置来控制小球移动"""
    
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.camera = None
        self.camera_thread = None
        self.running = False
        
        # MediaPipe手部检测初始化 - 提高精度
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,  # 提高检测置信度
            min_tracking_confidence=0.8   # 提高追踪置信度
        )
        
        # 手指位置历史记录
        self.finger_history = collections.deque(maxlen=5)  # 减少到5帧提高响应性
        self.current_finger_pos = None
        
        # 校准相关
        self.calibration_points = []
        self.screen_points = []
        self.transform = None
        self.calibrated = False
    
    def start_camera(self):
        """启动摄像头，只使用电脑内置摄像头"""
        # 只尝试连接电脑内置摄像头（索引0）
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret and frame is not None:
                print(f"成功连接到电脑内置摄像头（索引0）")
            else:
                self.camera.release()
                self.camera = None
                raise Exception("电脑内置摄像头无法正常工作")
        else:
            self.camera = None
            raise Exception("无法连接到电脑内置摄像头")
        
        self.running = True
        self.camera_thread = threading.Thread(target=self.camera_thread_func)
        self.camera_thread.start()
    
    def stop_camera(self):
        """停止摄像头"""
        self.running = False
        if self.camera_thread:
            self.camera_thread.join()
        if self.camera:
            self.camera.release()
    
    def camera_thread_func(self):
        """摄像头线程：检测手指位置"""
        while self.running:
            if self.camera is None:
                time.sleep(0.1)
                continue
                
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                finger_tip = hand_landmarks.landmark[8]
                
                h, w, _ = frame.shape
                finger_x = int(finger_tip.x * w)
                finger_y = int(finger_tip.y * h)
                
                self.finger_history.append((finger_x, finger_y))
                
                if len(self.finger_history) >= 3:
                    recent = list(self.finger_history)[-3:]  # 使用更少帧提高响应
                    avg_x = sum(pos[0] for pos in recent) / len(recent)
                    avg_y = sum(pos[1] for pos in recent) / len(recent)
                    self.current_finger_pos = (avg_x, avg_y)
                else:
                    self.current_finger_pos = (finger_x, finger_y)
            
            time.sleep(1/30)
    
    def get_finger_position(self):
        """获取当前检测到的手指位置"""
        return self.current_finger_pos
    
    def start_calibration(self, screen, calib_points, collection_seconds=2.0):
        """开始手指位置校准"""
        print('开始手指校准...')
        
        self.calibration_points = []
        self.screen_points = []
        
        for i, pt in enumerate(calib_points):
            px, py = pt
            screen.fill((8,12,22))
            
            # 显示校准目标
            pygame.draw.circle(screen, (255,255,255), (int(px), int(py)), 15)
            pygame.draw.circle(screen, (100,200,255), (int(px), int(py)), 8)
            pygame.draw.circle(screen, (255,255,255), (int(px), int(py)), 3)
            pygame.display.flip()
            
            time.sleep(0.5)
            
            # 收集手指位置样本
            t0 = time.time()
            collected = []
            while (time.time() - t0) < collection_seconds:
                finger_pos = self.get_finger_position()
                if finger_pos is not None:
                    collected.append(finger_pos)
                time.sleep(0.1)
            
            if len(collected) > 5:
                avg_x = sum(p[0] for p in collected) / len(collected)
                avg_y = sum(p[1] for p in collected) / len(collected)
                self.calibration_points.append((avg_x, avg_y))
                self.screen_points.append((px, py))
                print(f'校准点 {i+1}: 手指位置=({avg_x:.1f}, {avg_y:.1f}), 屏幕位置=({px}, {py})')
            else:
                print(f'校准点 {i+1} 失败: 无法检测到手指')
                return False
        
        # 计算变换矩阵
        if len(self.calibration_points) >= 3:
            finger_pts = np.array(self.calibration_points, dtype=np.float32)
            screen_pts = np.array(self.screen_points, dtype=np.float32)
            
            try:
                self.transform = cv2.getAffineTransform(finger_pts[:3], screen_pts[:3])
                self.calibrated = True
                print('手指校准成功！')
                return True
            except Exception as e:
                print(f'校准失败: {e}')
                return False
        
        return False
    
    def update(self, width, height, boundary_margin=30):
        """更新小球位置基于手指检测"""
        # 首先调用父类的物理更新（如果启用自动移动）
        if self.auto_movement:
            super().update(width, height)
            return (self.x, self.y)
        
        # 手指控制模式 - 严格限制在屏幕内
        boundary_margin = 20  # 减小边界容忍度
        if (self.x < -boundary_margin or self.x > width + boundary_margin or 
            self.y < -boundary_margin or self.y > height + boundary_margin):
            print(f"边界紧急重置: 位置({self.x:.1f}, {self.y:.1f}) -> 中心")
            self.x = width // 2
            self.y = height // 2
            return (self.x, self.y)
        
        finger_pos = self.get_finger_position()
        if finger_pos is None:
            return (self.x, self.y)
        
        if self.calibrated and self.transform is not None:
            src = np.array([ [finger_pos[0], finger_pos[1], 1.0] ], dtype=np.float32)
            M = np.vstack([self.transform, [0,0,1]])
            res = (M @ src.T).T[0]
            target_x, target_y = float(res[0]), float(res[1])
            
            finger_dx = target_x - self.x
            finger_dy = target_y - self.y
            finger_distance = math.sqrt(finger_dx*finger_dx + finger_dy*finger_dy)
            
            if finger_distance < 10.0:  # 缩小死区提高响应性
                return (self.x, self.y)
            
            base_response = 0.12  # 提高响应系数获得更精准跟随
            
            if finger_distance < 25.0:
                response_factor = base_response * 1.3  # 小距离增强响应
            elif finger_distance < 60.0:
                response_factor = base_response  # 中等距离正常
            else:
                response_factor = base_response * 0.85  # 大距离稍微减缓
            
            # 修复方向相反问题：反转移动向量
            move_x = -finger_dx * response_factor  # 添加负号反转X方向
            move_y = -finger_dy * response_factor  # 添加负号反转Y方向
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            self.position_history.append((new_x, new_y))
            
            if len(self.position_history) >= 3:
                recent = list(self.position_history)[-3:]
                weights = [0.15, 0.25, 0.6]  # 更高的实时权重
                
                avg_x = sum(pos[0] * w for pos, w in zip(recent, weights))
                avg_y = sum(pos[1] * w for pos, w in zip(recent, weights))
                
                # 调整平滑权重获得更好的跟随性
                self.x = self.x * 0.75 + avg_x * 0.25
                self.y = self.y * 0.75 + avg_y * 0.25
            else:
                self.x = new_x
                self.y = new_y
            
            # 严格限制瞳孔在屏幕内，防止消失
            ball_radius = self.current_radius  # 使用当前瞳孔半径
            self.x = max(ball_radius, min(width - ball_radius, self.x))
            self.y = max(ball_radius, min(height - ball_radius, self.y))
        
        return (self.x, self.y)


def main():
    pygame.init()
    
    width = 1000
    height = 700
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption('Pupil Eye Tracking - Local Focus Area')
    
    clock = pygame.time.Clock()
    
    # 创建元球渲染器 - 2个元球避免过度分裂
    metaball_renderer = MetaballRenderer(width, height, num_balls=2)
    
    # 创建干扰区渲染器
    interference_renderer = InterferenceRenderer(width, height)
    
    # 创建凝视提供者
    gaze_provider = GazeProvider(width, height)
    
    # 初始化手指追踪
    hand_provider = None
    try:
        hand_provider = HandGazeProvider(width, height)
        hand_provider.start_camera()
        print('手指追踪已启动，按 C 键进行校准')
    except Exception as e:
        print(f'无法启动手指追踪: {e}')
        print('游戏将以鼠标模式运行')
    
    if hand_provider:
        gaze_provider = hand_provider
    
    # 确保小球从焦点区域中心开始
    gaze_provider.reset_position(width, height)
    
    # 游戏状态
    game_active = False
    game_start_time = None
    game_duration = 45.0
    score = 0
    
    # 颜色定义
    BG_COLOR = (5, 5, 15)  # 深色背景突出彩虹效果
    BALL_COLOR = (255, 255, 100)  # 亮黄色小球
    TEXT_COLOR = (200, 200, 200)
    
    running = True
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                metaball_renderer.update_size(width, height)
                interference_renderer.width = width
                interference_renderer.height = height
                gaze_provider.reset_position(width, height)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_active:
                        game_active = True
                        game_start_time = time.time()
                        score = 0
                        gaze_provider.current_radius = gaze_provider.initial_radius  # 重置小球大小
                        gaze_provider.boundary_collision_count = 0  # 重置碰撞计数
                        gaze_provider.last_in_focus = True  # 重置焦点状态
                        gaze_provider.last_touching_boundary = False  # 重置边界磨到状态
                        print('游戏开始！用手指控制瞳孔保持在流动的彩虹区域内 - 瞳孔会逐渐变大增加雾度！')
                
                if event.key == pygame.K_r:
                    gaze_provider.reset_position(width, height)
                    print("小球已重置到中心")
                
                if event.key == pygame.K_c:
                    if hand_provider is not None:
                        margin = 80
                        pts = [
                            (width//2, height//2),
                            (margin, margin),
                            (width-margin, margin),
                            (margin, height-margin),
                            (width-margin, height-margin),
                            (width//2, margin),
                            (width//2, height-margin),
                            (margin, height//2),
                            (width-margin, height//2)
                        ]
                        print('开始9点手指校准...')
                        ok = hand_provider.start_calibration(screen, pts)
                        if ok:
                            print('手指校准完成！现在可以用手指控制小球了')
                        else:
                            print('校准失败：确保你的手在摄像头视野内')
        
        # 游戏逻辑
        time_left = 0
        if game_active:
            if game_start_time:
                elapsed = time.time() - game_start_time
                time_left = max(0, game_duration - elapsed)
                
                if time_left <= 0:
                    game_active = False
                    final_difficulty = gaze_provider.current_radius / gaze_provider.initial_radius
                    final_collisions = gaze_provider.get_boundary_collisions()
                    print(f'游戏结束！最终得分: {score}，最终雾度系数: x{final_difficulty:.1f}，边界碰撞次数: {final_collisions}')
        
        # 更新小球位置（手指控制）
        if game_active and hand_provider and hand_provider.calibrated:
            hand_provider.update(width, height)
        elif game_active:
            # 如果没有校准，使用基础的自动移动
            gaze_provider.update(width, height)
        
        # 更新小球大小（如果游戏进行中）
        if game_active and game_start_time:
            elapsed = time.time() - game_start_time
            gaze_provider.update_ball_size(elapsed)
        
        ball_x, ball_y = gaze_provider.get_position()
        current_radius = gaze_provider.get_radius()
        
        # 检查小球是否在动态焦点区域内并计数碰撞
        if game_active:
            gaze_provider.check_focus_boundary_collision(metaball_renderer)
            if metaball_renderer.is_point_in_focus_area(ball_x, ball_y):
                score += 1
        
        # 渲染
        screen.fill(BG_COLOR)
        
        # 渲染干扰区效果（在焦点区域外）
        interference_renderer.render(screen, metaball_renderer)
        
        # 渲染元球边界（彩虹流动效果）
        metaball_renderer.render(screen)
        
        # 绘制瞳孔样式的控制球（动态大小）
        current_time_factor = time.time() * 0.5  # 慢速动画
        draw_pupil_eye(screen, ball_x, ball_y, current_radius, current_time_factor)
        
        # 计算难度系数（用于显示）
        difficulty_factor = current_radius / gaze_provider.initial_radius
        
        # HUD信息
        finger_status = "Hand Detected" if (hand_provider and hand_provider.get_finger_position()) else "No Hand"
        calib_status = "Calibrated" if (hand_provider and hand_provider.calibrated) else "Not Calibrated"
        
        # HUD信息
        finger_status = "Hand Detected" if (hand_provider and hand_provider.get_finger_position()) else "No Hand"
        calib_status = "Calibrated" if (hand_provider and hand_provider.calibrated) else "Not Calibrated"
        collision_count = gaze_provider.get_boundary_collisions()
        
        info_lines = [
            f'Time: {time_left:.1f}s' if game_active else 'Press SPACE to start',
            f'Score: {score}',
            f'Pupil Size: {current_radius:.1f}px (x{difficulty_factor:.1f}) Max: 60px',
            f'Boundary Hits: {collision_count}',
            f'Finger: {finger_status}',
            f'Calibration: {calib_status}',
            f'Eye Position: ({ball_x:.0f}, {ball_y:.0f})',
            'Local Focus Area with Wave Interference!',
            'Controls: C=Calibrate, R=Reset, SPACE=Start'
        ]
        
        font = pygame.font.Font(None, 24)
        for i, line in enumerate(info_lines):
            text = font.render(line, True, TEXT_COLOR)
            screen.blit(text, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    # 清理
    if hand_provider:
        hand_provider.stop_camera()
    pygame.quit()


if __name__ == "__main__":
    main()