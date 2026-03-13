"""
子弹模块
"""
import pygame
from config import (
    BULLET_SPEED, TANK_SIZE, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT,
    COLOR_YELLOW, COLOR_RED
)


class Bullet(pygame.sprite.Sprite):
    """子弹类"""

    def __init__(self, x, y, direction, is_player=True, power=1):
        super().__init__()
        self.direction = direction
        self.is_player = is_player
        self.power = power
        self.size = 8

        # 创建子弹图像
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color = COLOR_YELLOW if is_player else COLOR_RED
        pygame.draw.rect(self.image, color, (0, 0, self.size, self.size))
        pygame.draw.rect(self.image, COLOR_YELLOW, (2, 2, self.size-4, self.size-4))

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # 设置速度
        self.vx, self.vy = 0, 0
        if direction == DIR_UP:
            self.vy = -BULLET_SPEED
        elif direction == DIR_DOWN:
            self.vy = BULLET_SPEED
        elif direction == DIR_LEFT:
            self.vx = -BULLET_SPEED
        elif direction == DIR_RIGHT:
            self.vx = BULLET_SPEED

        self.active = True

    def update(self, map_tiles, tanks, base=None):
        """更新子弹位置，返回是否击中了墙壁"""
        if not self.active:
            return False

        hit_wall = False

        self.rect.x += self.vx
        self.rect.y += self.vy

        # 检查是否出界
        if (self.rect.left < 0 or self.rect.right > 800 or
            self.rect.top < 50 or self.rect.bottom > 600):
            self.active = False
            self.kill()
            return False

        # 检查与地图元素的碰撞
        for tile in map_tiles:
            if self.rect.colliderect(tile.rect):
                if tile.destroyable:
                    tile.take_damage(self.power)
                    self.active = False
                    self.kill()
                    return True  # 击中了可破坏墙壁
                elif tile.solid:
                    self.active = False
                    self.kill()
                    return True  # 击中了不可破坏墙壁

        # 检查与基地的碰撞
        if base and self.rect.colliderect(base.rect):
            base.destroyed = True
            self.active = False
            self.kill()
            return True

        # 检查与坦克的碰撞
        for tank in tanks:
            if self.is_player != tank.is_player:
                if self.rect.colliderect(tank.rect):
                    tank.take_damage(self.power)
                    self.active = False
                    self.kill()
                    return False  # 击中坦克不算击中墙壁

        return False
