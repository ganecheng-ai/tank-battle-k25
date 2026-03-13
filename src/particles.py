"""
粒子效果模块 - 游戏中的爆炸和粒子特效
"""
import pygame
import random
import math
from config import (
    COLOR_YELLOW, COLOR_ORANGE, COLOR_RED, COLOR_WHITE, COLOR_GRAY, COLOR_BLACK
)


class Particle:
    """单个粒子"""

    def __init__(self, x, y, color, size, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.active = True

    def update(self):
        """更新粒子状态"""
        if not self.active:
            return

        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # 添加重力效果
        self.vy += 0.1

        if self.lifetime <= 0:
            self.active = False

    def draw(self, surface):
        """绘制粒子"""
        if not self.active:
            return

        # 根据生命周期调整透明度
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color_with_alpha = (*self.color[:3], alpha)

        # 创建带透明度的表面
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha,
                          (self.size, self.size), self.size)

        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


class Explosion:
    """爆炸效果"""

    # 爆炸类型
    TYPE_SMALL = 1    # 小爆炸（子弹命中）
    TYPE_MEDIUM = 2   # 中等爆炸（坦克被摧毁）
    TYPE_LARGE = 3    # 大爆炸（基地被摧毁）

    def __init__(self, x, y, explosion_type=TYPE_MEDIUM):
        self.x = x
        self.y = y
        self.explosion_type = explosion_type
        self.particles = []
        self.active = True
        self.flash_duration = 10  # 闪光持续时间
        self.current_flash = 0

        # 根据爆炸类型设置参数
        self._create_explosion()

    def _create_explosion(self):
        """创建爆炸粒子"""
        if self.explosion_type == self.TYPE_SMALL:
            num_particles = 8
            max_size = 4
            max_speed = 3
            lifetime_range = (20, 40)
            colors = [COLOR_YELLOW, COLOR_ORANGE]
        elif self.explosion_type == self.TYPE_MEDIUM:
            num_particles = 20
            max_size = 8
            max_speed = 5
            lifetime_range = (30, 60)
            colors = [COLOR_YELLOW, COLOR_ORANGE, COLOR_RED]
        else:  # TYPE_LARGE
            num_particles = 40
            max_size = 12
            max_speed = 7
            lifetime_range = (50, 100)
            colors = [COLOR_YELLOW, COLOR_ORANGE, COLOR_RED, COLOR_WHITE]

        # 创建粒子
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, max_speed)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            size = random.randint(2, max_size)
            lifetime = random.randint(*lifetime_range)
            color = random.choice(colors)

            particle = Particle(self.x, self.y, color, size, (vx, vy), lifetime)
            self.particles.append(particle)

    def update(self):
        """更新爆炸效果"""
        if not self.active:
            return

        # 更新闪光
        if self.current_flash < self.flash_duration:
            self.current_flash += 1

        # 更新粒子
        active_particles = 0
        for particle in self.particles:
            particle.update()
            if particle.active:
                active_particles += 1

        # 所有粒子消失后爆炸结束
        if active_particles == 0 and self.current_flash >= self.flash_duration:
            self.active = False

    def draw(self, surface):
        """绘制爆炸效果"""
        if not self.active:
            return

        # 绘制闪光
        if self.current_flash < self.flash_duration:
            flash_alpha = int(255 * (1 - self.current_flash / self.flash_duration))
            flash_size = int(30 * (1 - self.current_flash / self.flash_duration))
            flash_surface = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (255, 255, 200, flash_alpha),
                             (flash_size, flash_size), flash_size)
            surface.blit(flash_surface, (int(self.x - flash_size), int(self.y - flash_size)))

        # 绘制粒子
        for particle in self.particles:
            particle.draw(surface)


class ParticleManager:
    """粒子管理器"""

    def __init__(self):
        self.explosions = []
        self.particles = []

    def add_explosion(self, x, y, explosion_type=Explosion.TYPE_MEDIUM):
        """添加爆炸效果"""
        explosion = Explosion(x, y, explosion_type)
        self.explosions.append(explosion)
        return explosion

    def add_explosion_at_sprite(self, sprite, explosion_type=Explosion.TYPE_MEDIUM):
        """在精灵位置添加爆炸效果"""
        if hasattr(sprite, 'rect'):
            x = sprite.rect.centerx
            y = sprite.rect.centery
        else:
            x, y = sprite.x, sprite.y
        return self.add_explosion(x, y, explosion_type)

    def add_spark(self, x, y, color=COLOR_YELLOW, count=5):
        """添加火花效果"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.randint(1, 3)
            lifetime = random.randint(10, 20)
            particle = Particle(x, y, color, size, (vx, vy), lifetime)
            self.particles.append(particle)

    def add_smoke(self, x, y, count=3):
        """添加烟雾效果"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 1  # 向上飘
            size = random.randint(4, 8)
            lifetime = random.randint(30, 50)
            gray_value = random.randint(100, 150)
            color = (gray_value, gray_value, gray_value)
            particle = Particle(x, y, color, size, (vx, vy), lifetime)
            self.particles.append(particle)

    def update(self):
        """更新所有粒子效果"""
        # 更新爆炸
        for explosion in list(self.explosions):
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)

        # 更新单个粒子
        for particle in list(self.particles):
            particle.update()
            if not particle.active:
                self.particles.remove(particle)

    def draw(self, surface):
        """绘制所有粒子效果"""
        # 绘制爆炸
        for explosion in self.explosions:
            explosion.draw(surface)

        # 绘制粒子
        for particle in self.particles:
            particle.draw(surface)

    def clear(self):
        """清除所有粒子效果"""
        self.explosions.clear()
        self.particles.clear()

    def add_tank_explosion(self, tank):
        """坦克爆炸效果"""
        return self.add_explosion_at_sprite(tank, Explosion.TYPE_MEDIUM)

    def add_bullet_hit(self, bullet, is_wall=False):
        """子弹命中效果"""
        if hasattr(bullet, 'rect'):
            x = bullet.rect.centerx
            y = bullet.rect.centery
        else:
            x, y = bullet.x, bullet.y

        if is_wall:
            # 打中墙壁产生火花
            self.add_spark(x, y, COLOR_YELLOW, 8)
            self.add_smoke(x, y, 2)
            return self.add_explosion(x, y, Explosion.TYPE_SMALL)
        else:
            # 打中坦克产生火花
            self.add_spark(x, y, COLOR_ORANGE, 10)
            return self.add_explosion(x, y, Explosion.TYPE_SMALL)

    def add_base_explosion(self, base):
        """基地爆炸效果"""
        return self.add_explosion_at_sprite(base, Explosion.TYPE_LARGE)


class TankTrail:
    """坦克移动轨迹效果"""

    def __init__(self):
        self.trails = {}  # {tank: [(x, y, lifetime), ...]}

    def add_trail(self, tank):
        """添加轨迹点"""
        if tank not in self.trails:
            self.trails[tank] = []

        # 添加新的轨迹点
        if tank.moving and tank.alive:
            self.trails[tank].append({
                'x': tank.rect.centerx,
                'y': tank.rect.centery,
                'lifetime': 15
            })

        # 限制轨迹点数量
        if len(self.trails[tank]) > 10:
            self.trails[tank].pop(0)

    def update(self):
        """更新轨迹"""
        for tank in list(self.trails.keys()):
            if not tank.alive:
                del self.trails[tank]
                continue

            for trail in self.trails[tank]:
                trail['lifetime'] -= 1

            # 移除过期的轨迹点
            self.trails[tank] = [t for t in self.trails[tank] if t['lifetime'] > 0]

    def draw(self, surface):
        """绘制轨迹"""
        for tank, trails in self.trails.items():
            if not trails:
                continue

            color = COLOR_GRAY if tank.is_player else COLOR_RED
            for i, trail in enumerate(trails):
                alpha = int(255 * (trail['lifetime'] / 15) * (i / len(trails)))
                size = int(3 * (trail['lifetime'] / 15))
                trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*color[:3], alpha // 2),
                                 (size, size), size)
                surface.blit(trail_surface, (trail['x'] - size, trail['y'] - size))

    def clear(self):
        """清除所有轨迹"""
        self.trails.clear()
