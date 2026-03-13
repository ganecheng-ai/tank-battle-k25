"""
道具模块 - 游戏中的道具系统
"""
import pygame
import random
from config import (
    TILE_SIZE, COLOR_YELLOW, COLOR_GREEN, COLOR_BLUE, COLOR_RED,
    COLOR_WHITE, COLOR_ORANGE, GAME_AREA_TOP, SCREEN_WIDTH, SCREEN_HEIGHT
)


class PowerUp(pygame.sprite.Sprite):
    """道具基类"""

    # 道具类型
    TYPE_EXTRA_LIFE = 1      # 加生命
    TYPE_SPEED_BOOST = 2     # 加速
    TYPE_ARMOR_PIERCING = 3  # 穿甲弹
    TYPE_SHIELD = 4          # 护盾
    TYPE_BOMB = 5            # 全屏炸弹

    # 道具显示名称
    TYPE_NAMES = {
        TYPE_EXTRA_LIFE: "生命+",
        TYPE_SPEED_BOOST: "加速",
        TYPE_ARMOR_PIERCING: "穿甲",
        TYPE_SHIELD: "护盾",
        TYPE_BOMB: "炸弹"
    }

    # 道具颜色
    TYPE_COLORS = {
        TYPE_EXTRA_LIFE: COLOR_RED,
        TYPE_SPEED_BOOST: COLOR_BLUE,
        TYPE_ARMOR_PIERCING: COLOR_ORANGE,
        TYPE_SHIELD: COLOR_YELLOW,
        TYPE_BOMB: COLOR_GREEN
    }

    # 道具持续时间（帧数）
    DURATION = {
        TYPE_EXTRA_LIFE: 0,       # 立即生效，无持续时间
        TYPE_SPEED_BOOST: 300,    # 5秒
        TYPE_ARMOR_PIERCING: 600, # 10秒
        TYPE_SHIELD: 480,         # 8秒
        TYPE_BOMB: 0              # 立即生效
    }

    def __init__(self, x, y, power_type=None):
        super().__init__()
        self.power_type = power_type if power_type else random.randint(1, 5)
        self.size = TILE_SIZE
        self.active = True
        self.blink_timer = 0
        self.blink_visible = True

        # 创建道具图像
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._create_image()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def _create_image(self):
        """创建道具图像"""
        color = self.TYPE_COLORS.get(self.power_type, COLOR_WHITE)

        # 背景圆
        center = self.size // 2
        pygame.draw.circle(self.image, color, (center, center), center - 2)
        pygame.draw.circle(self.image, COLOR_WHITE, (center, center), center - 2, 2)

        # 道具图标
        font = pygame.font.SysFont(None, 20)
        text = self.TYPE_NAMES.get(self.power_type, "?")
        text_surface = font.render(text, True, COLOR_WHITE)
        text_rect = text_surface.get_rect(center=(center, center))
        self.image.blit(text_surface, text_rect)

    def update(self):
        """更新道具状态"""
        self.blink_timer += 1
        if self.blink_timer >= 10:
            self.blink_timer = 0
            self.blink_visible = not self.blink_visible

    def draw(self, surface):
        """绘制道具"""
        if self.blink_visible:
            surface.blit(self.image, self.rect)


class PowerUpManager:
    """道具管理器"""

    def __init__(self):
        self.powerups = pygame.sprite.Group()
        self.active_effects = {}  # {tank: {effect_type: remaining_frames}}
        self.spawn_timer = 0
        self.spawn_interval = 600  # 10秒生成一次道具

    def update(self, player_tank, enemy_tanks, map_tiles):
        """更新道具系统"""
        # 更新道具闪烁效果
        for powerup in self.powerups:
            powerup.update()

        # 检查道具拾取
        self._check_collection(player_tank, enemy_tanks)

        # 更新生效中的效果
        self._update_effects()

    def _check_collection(self, player_tank, enemy_tanks):
        """检查道具拾取"""
        # 只有玩家可以拾取道具
        if not player_tank or not player_tank.alive:
            return

        for powerup in list(self.powerups):
            if powerup.rect.colliderect(player_tank.rect):
                self._apply_effect(player_tank, powerup.power_type)
                powerup.active = False
                self.powerups.remove(powerup)

    def _apply_effect(self, tank, power_type):
        """应用道具效果"""
        if tank not in self.active_effects:
            self.active_effects[tank] = {}

        if power_type == PowerUp.TYPE_EXTRA_LIFE:
            # 加生命
            tank.hp = min(tank.hp + 1, tank.max_hp + 1)
            tank.max_hp = max(tank.max_hp, tank.hp)
        elif power_type == PowerUp.TYPE_BOMB:
            # 全屏炸弹 - 消灭所有敌人
            for enemy in list(tank.groups()[0] if tank.groups() else []):
                if hasattr(enemy, 'is_player') and not enemy.is_player:
                    enemy.take_damage(999)
        else:
            # 其他效果设置持续时间
            duration = PowerUp.DURATION.get(power_type, 300)
            self.active_effects[tank][power_type] = duration

            # 立即应用效果
            if power_type == PowerUp.TYPE_SPEED_BOOST:
                tank.speed = int(tank.speed * 1.5)
            elif power_type == PowerUp.TYPE_ARMOR_PIERCING:
                tank.armor_piercing = True
            elif power_type == PowerUp.TYPE_SHIELD:
                tank.shield = True

    def _update_effects(self):
        """更新效果持续时间"""
        for tank in list(self.active_effects.keys()):
            effects = self.active_effects[tank]
            for effect_type in list(effects.keys()):
                effects[effect_type] -= 1
                if effects[effect_type] <= 0:
                    # 效果结束，恢复属性
                    self._remove_effect(tank, effect_type)
                    del effects[effect_type]

            # 清理空的效果字典
            if not effects:
                del self.active_effects[tank]

    def _remove_effect(self, tank, effect_type):
        """移除道具效果"""
        if effect_type == PowerUp.TYPE_SPEED_BOOST:
            # 恢复速度
            from config import PLAYER_SPEED, ENEMY_SPEED
            tank.speed = PLAYER_SPEED if tank.is_player else ENEMY_SPEED
        elif effect_type == PowerUp.TYPE_ARMOR_PIERCING:
            # 移除穿甲弹效果
            tank.armor_piercing = False
        elif effect_type == PowerUp.TYPE_SHIELD:
            # 移除护盾
            tank.shield = False

    def spawn_powerup(self, x=None, y=None, power_type=None):
        """在指定位置生成道具，或随机位置"""
        if x is None or y is None:
            # 随机位置（在游戏区域内）
            x = random.randint(1, 24) * TILE_SIZE
            y = random.randint(3, 22) * TILE_SIZE + GAME_AREA_TOP

        powerup = PowerUp(x, y, power_type)
        self.powerups.add(powerup)
        return powerup

    def spawn_random(self):
        """随机生成道具"""
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_powerup()
            return True
        return False

    def draw(self, surface):
        """绘制所有道具"""
        for powerup in self.powerups:
            powerup.draw(surface)

    def draw_active_effects(self, surface, x, y):
        """绘制当前生效的效果列表"""
        font = pygame.font.SysFont(None, 20)
        effects_y = y

        for tank, effects in self.active_effects.items():
            if tank.is_player:  # 只显示玩家的效果
                for effect_type, remaining in effects.items():
                    name = PowerUp.TYPE_NAMES.get(effect_type, "?")
                    seconds = remaining // 60
                    text = f"{name}: {seconds}s"
                    text_surface = font.render(text, True, COLOR_YELLOW)
                    surface.blit(text_surface, (x, effects_y))
                    effects_y += 25

    def has_effect(self, tank, effect_type):
        """检查坦克是否有指定效果"""
        if tank in self.active_effects:
            return effect_type in self.active_effects[tank]
        return False

    def get_effect_time(self, tank, effect_type):
        """获取效果的剩余时间"""
        if tank in self.active_effects and effect_type in self.active_effects[tank]:
            return self.active_effects[tank][effect_type]
        return 0

    def clear(self):
        """清除所有道具和效果"""
        self.powerups.empty()
        self.active_effects.clear()
        self.spawn_timer = 0
