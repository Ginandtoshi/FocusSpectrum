import pygame
import random
import math

# --- 常量设置 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DISTRACTOR_RECT = pygame.Rect(550, 50, 200, 200) # 干扰物出现的区域
MAX_CIRCLES = 4

# --- 模拟 p5.js 的 Circle 类 ---
class WigglyCircle:
    def __init__(self, base_x, base_y):
        # 基础属性
        self.start_time = pygame.time.get_ticks()
        self.base_pos = pygame.Vector2(base_x, base_y)
        
        # 随机化“扭动”参数
        self.amplitude_x = random.randint(15, 30) # X轴摆动幅度
        self.amplitude_y = random.randint(15, 30) # Y轴摆动幅度
        self.frequency_x = random.uniform(0.002, 0.005) # X轴摆动速度
        self.frequency_y = random.uniform(0.003, 0.006) # Y轴摆动速度 (不同速度)
        
        self.radius = random.randint(10, 25)
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        
        # 模拟 p5.js 的 filter()，每个圆圈有自己的生命周期
        self.lifetime = random.randint(3000, 6000) # 3到6秒

    def is_alive(self, current_time):
        """检查是否存活"""
        return (current_time - self.start_time) < self.lifetime

    def draw(self, surface, current_time):
        """计算扭动并绘制"""
        
        # 1. 计算自出生以来的时间 (p5.js 中的 millis)
        age = current_time - self.start_time
        
        # 2. 模拟 p5.js 中的 sin() 扭曲
        # 使用 sin 和 cos 函数来创建平滑的、无序的摆动
        offset_x = math.sin(age * self.frequency_x) * self.amplitude_x
        offset_y = math.cos(age * self.frequency_y) * self.amplitude_y
        
        # 3. 计算最终位置
        current_pos = self.base_pos + pygame.Vector2(offset_x, offset_y)
        
        # pygame.draw.circle 需要整数坐标
        pygame.draw.circle(surface, self.color, (int(current_pos.x), int(current_pos.y)), self.radius)

# --- 主程序 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("动态干扰物 (Pygame 模拟)")
    clock = pygame.time.Clock()

    circles = []
    running = True

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- 逻辑更新 ---
        
        # 1. 模拟 p5.js 的 filter() - 移除"死亡"的圆圈
        circles = [c for c in circles if c.is_alive(current_time)]

        # 2. 模拟 p5.js 的 random() > 0.7 - 随机添加新圆圈
        # (这里用 0.95 是因为循环更快，需要更低的概率)
        if len(circles) < MAX_CIRCLES and random.random() > 0.95:
            # 在干扰区域内随机生成
            spawn_x = DISTRACTOR_RECT.x + random.randint(30, DISTRACTOR_RECT.width - 30)
            spawn_y = DISTRACTOR_RECT.y + random.randint(30, DISTRACTOR_RECT.height - 30)
            circles.append(WigglyCircle(spawn_x, spawn_y))

        # --- 绘制 ---
        screen.fill((255, 255, 255)) # 白色背景

        # (这里是你主要游戏内容绘制的地方)
        # ...
        # ...

        # 绘制干扰物区域
        # 1. 绘制一个灰色背景框，明确告诉眼动仪这是“干扰区”
        pygame.draw.rect(screen, (240, 240, 240), DISTRACTOR_RECT) 
        pygame.draw.rect(screen, (200, 200, 200), DISTRACTOR_RECT, 2)
        
        # 2. 绘制所有“扭动”的圆圈
        for circle in circles:
            circle.draw(screen, current_time)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
