import pygame
import random
import math

# --- 定数設定 ---
WIDTH, HEIGHT = 800, 600
NUM_BALLS = 13 # p5.js と同じく 13個

class Metaball:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # p5.js: const size = pow(random(), 2);
        size = random.random() ** 2
        
        # p5.js: this.radius = 100 * size + 20;
        self.radius = 100 * size + 20
        
        # p5.js: this.vel = p5.Vector.random2D().mult(2 * (1 - size) + 0.5);
        vel_speed = 2 * (1 - size) + 0.5
        random_angle = random.uniform(0, 2 * math.pi)
        self.vel = pygame.Vector2(math.cos(random_angle), math.sin(random_angle)) * vel_speed
        
        # 初期位置（随机）
        self.pos = pygame.Vector2(
            random.uniform(self.radius, self.width - self.radius),
            random.uniform(self.radius, self.height - self.radius)
        )
        
        # 颜色（使用 HSLA）
        self_hue = random.randint(0, 360)
        self.color = pygame.Color(0)
        self.color.hsla = (self_hue, 100, 50, 100)

    def update(self):
        # 移动并在边界反弹
        self.pos += self.vel
        if self.pos.x < self.radius:
            self.pos.x = self.radius
            self.vel.x *= -1
        if self.pos.x > self.width - self.radius:
            self.pos.x = self.width - self.radius
            self.vel.x *= -1
        if self.pos.y < self.radius:
            self.pos.y = self.radius
            self.vel.y *= -1
        if self.pos.y > self.height - self.radius:
            self.pos.y = self.height - self.radius
            self.vel.y *= -1

    def draw(self, surface):
        # 转换为整数坐标再绘制
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Metaball Simulation (Python/Pygame)")
    clock = pygame.time.Clock()

    metaballs = [Metaball(WIDTH, HEIGHT) for _ in range(NUM_BALLS)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 更新
        for ball in metaballs:
            ball.update()

        # 绘制
        screen.fill((0, 0, 0))
        for ball in metaballs:
            ball.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
