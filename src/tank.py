"""
坦克模块
"""
import pygame
from config import (
    TANK_SIZE, PLAYER_SPEED, ENEMY_SPEED, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT,
    COLOR_GREEN, COLOR_GRAY, COLOR_DARK_GRAY, COLOR_BLACK, COLOR_YELLOW, COLOR_RED,
    SCREEN_WIDTH, GAME_AREA_TOP
)
from bullet import Bullet


class Tank(pygame.sprite.Sprite):
    """坦克基类"""

    def __init__(self, x, y, is_player=True, color=None):
        super().__init__()
        self.is_player = is_player
        self.direction = DIR_UP
        self.speed = PLAYER_SPEED if is_player else ENEMY_SPEED
        self.size = TANK_SIZE
        self.hp = 1 if is_player else 1
        self.max_hp = self.hp
        self.alive = True
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 15 if is_player else 30

        # 颜色设置
        if color is None:
            self.color = COLOR_GREEN if is_player else COLOR_GRAY
        else:
            self.color = color

        # 创建坦克图像
        self.images = self._create_images()
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # 移动标志
        self.moving = False

    def _create_images(self):
        """创建四个方向的坦克图像"""
        images = []
        for direction in range(4):
            img = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

            # 坦克主体
            body_color = self.color
            pygame.draw.rect(img, body_color, (4, 4, self.size-8, self.size-8))
            pygame.draw.rect(img, COLOR_BLACK, (4, 4, self.size-8, self.size-8), 2)

            # 炮塔
            turret_color = COLOR_DARK_GRAY
            center = self.size // 2
            pygame.draw.rect(img, turret_color, (center-4, center-4, 8, 8))

            # 炮管
            barrel_color = COLOR_BLACK
            if direction == DIR_UP:
                pygame.draw.rect(img, barrel_color, (center-2, 0, 4, center))
            elif direction == DIR_DOWN:
                pygame.draw.rect(img, barrel_color, (center-2, center, 4, center))
            elif direction == DIR_LEFT:
                pygame.draw.rect(img, barrel_color, (0, center-2, center, 4))
            elif direction == DIR_RIGHT:
                pygame.draw.rect(img, barrel_color, (center, center-2, center, 4))

            # 履带细节
            pygame.draw.rect(img, COLOR_BLACK, (0, 0, 4, self.size))
            pygame.draw.rect(img, COLOR_BLACK, (self.size-4, 0, 4, self.size))

            images.append(img)
        return images

    def move(self, direction, map_tiles, other_tanks):
        """移动坦克"""
        if not self.alive:
            return False

        self.direction = direction
        self.image = self.images[direction]
        self.moving = True

        # 计算新位置
        new_rect = self.rect.copy()
        if direction == DIR_UP:
            new_rect.y -= self.speed
        elif direction == DIR_DOWN:
            new_rect.y += self.speed
        elif direction == DIR_LEFT:
            new_rect.x -= self.speed
        elif direction == DIR_RIGHT:
            new_rect.x += self.speed

        # 边界检查
        if new_rect.left < 0 or new_rect.right > SCREEN_WIDTH:
            return False
        if new_rect.top < GAME_AREA_TOP or new_rect.bottom > 600:
            return False

        # 地图碰撞检查
        for tile in map_tiles:
            if tile.solid and new_rect.colliderect(tile.rect):
                return False

        # 坦克碰撞检查
        for tank in other_tanks:
            if tank != self and tank.alive and new_rect.colliderect(tank.rect):
                return False

        self.rect = new_rect
        return True

    def stop(self):
        """停止移动"""
        self.moving = False

    def shoot(self):
        """发射子弹"""
        if not self.alive or self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = self.shoot_cooldown_max

        # 计算子弹发射位置
        center_x = self.rect.centerx
        center_y = self.rect.centery

        if self.direction == DIR_UP:
            center_y -= self.size // 2
        elif self.direction == DIR_DOWN:
            center_y += self.size // 2
        elif self.direction == DIR_LEFT:
            center_x -= self.size // 2
        elif self.direction == DIR_RIGHT:
            center_x += self.size // 2

        return Bullet(center_x, center_y, self.direction, self.is_player)

    def take_damage(self, damage):
        """受到伤害"""
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            self.kill()

    def update(self):
        """更新坦克状态"""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw_hp(self, surface):
        """绘制生命值"""
        if self.hp > 0:
            bar_width = self.size
            bar_height = 4
            hp_percent = self.hp / self.max_hp
            fill_width = int(bar_width * hp_percent)

            x = self.rect.x
            y = self.rect.y - bar_height - 2

            pygame.draw.rect(surface, COLOR_BLACK, (x, y, bar_width, bar_height))
            pygame.draw.rect(surface, COLOR_YELLOW if self.is_player else COLOR_RED,
                           (x, y, fill_width, bar_height))


class PlayerTank(Tank):
    """玩家坦克类"""

    def __init__(self, x, y, player_num=1):
        color = COLOR_GREEN if player_num == 1 else COLOR_YELLOW
        super().__init__(x, y, is_player=True, color=color)
        self.player_num = player_num
        self.hp = 3
        self.max_hp = 3


class EnemyTank(Tank):
    """敌人坦克类"""

    def __init__(self, x, y, enemy_type=1):
        colors = {
            1: COLOR_GRAY,      # 普通坦克
            2: (255, 128, 0),   # 快速坦克
            3: (128, 0, 255),   # 重型坦克
            4: COLOR_RED        # 超级坦克
        }
        color = colors.get(enemy_type, COLOR_GRAY)
        super().__init__(x, y, is_player=False, color=color)
        self.enemy_type = enemy_type
        self.ai_timer = 0
        self.move_timer = 0

        # 根据类型设置属性
        if enemy_type == 2:  # 快速坦克
            self.speed = ENEMY_SPEED * 2
            self.hp = 1
        elif enemy_type == 3:  # 重型坦克
            self.hp = 3
            self.speed = ENEMY_SPEED
        elif enemy_type == 4:  # 超级坦克
            self.hp = 4
            self.speed = ENEMY_SPEED * 1.5
        else:  # 普通坦克
            self.hp = 1
            self.speed = ENEMY_SPEED

        self.max_hp = self.hp

    def ai_update(self, player_tanks, map_tiles):
        """AI更新"""
        if not self.alive:
            return

        self.ai_timer += 1
        self.move_timer += 1

        # 随机改变方向
        if self.ai_timer >= 60:
            self.ai_timer = 0
            import random
            self.direction = random.randint(0, 3)
            self.image = self.images[self.direction]

        # 尝试移动
        self.moving = True
        other_tanks = [t for t in player_tanks if t.alive]

        if not self.move(self.direction, map_tiles, other_tanks):
            # 移动失败，随机选择新方向
            import random
            self.direction = random.randint(0, 3)
            self.image = self.images[self.direction]

        # 随机射击
        import random
        if random.random() < 0.02:
            return self.shoot()
        return None
