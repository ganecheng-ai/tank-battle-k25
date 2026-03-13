"""
地图模块
"""
import pygame
from config import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, GAME_AREA_TOP,
    TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_BASE,
    COLOR_BROWN, COLOR_GRAY, COLOR_BLUE, COLOR_GREEN, COLOR_WHITE, COLOR_BLACK
)


class MapTile(pygame.sprite.Sprite):
    """地图元素类"""

    def __init__(self, x, y, tile_type):
        super().__init__()
        self.tile_type = tile_type
        self.x = x
        self.y = y + GAME_AREA_TOP
        self.size = TILE_SIZE
        self.hp = 1
        self.destroyable = False
        self.solid = False
        self.hidden = False

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self._setup_tile()

    def _setup_tile(self):
        """根据类型设置地图元素属性"""
        if self.tile_type == TILE_EMPTY:
            self.image.fill((0, 0, 0, 0))

        elif self.tile_type == TILE_BRICK:
            self.destroyable = True
            self.solid = True
            self.hp = 1
            # 绘制砖块
            self.image.fill(COLOR_BROWN)
            # 添加砖块纹理
            for i in range(0, self.size, 8):
                pygame.draw.line(self.image, COLOR_BLACK, (i, 0), (i, self.size), 1)
                pygame.draw.line(self.image, COLOR_BLACK, (0, i), (self.size, i), 1)
            pygame.draw.rect(self.image, COLOR_BLACK, (0, 0, self.size, self.size), 2)

        elif self.tile_type == TILE_STEEL:
            self.destroyable = False
            self.solid = True
            # 绘制钢铁
            self.image.fill(COLOR_GRAY)
            # 添加金属纹理
            pygame.draw.rect(self.image, COLOR_WHITE, (2, 2, self.size-4, self.size-4), 1)
            pygame.draw.line(self.image, COLOR_BLACK, (4, 4), (self.size-4, self.size-4), 2)
            pygame.draw.line(self.image, COLOR_BLACK, (self.size-4, 4), (4, self.size-4), 2)
            pygame.draw.rect(self.image, COLOR_BLACK, (0, 0, self.size, self.size), 2)

        elif self.tile_type == TILE_WATER:
            self.destroyable = False
            self.solid = True  # 坦克不能通过
            # 绘制水
            self.image.fill(COLOR_BLUE)
            # 添加水波纹理
            for i in range(4, self.size, 8):
                pygame.draw.arc(self.image, (0, 100, 200),
                              (i-4, self.size//3, 8, 8), 0, 3.14)
                pygame.draw.arc(self.image, (0, 100, 200),
                              (i, self.size*2//3, 8, 8), 0, 3.14)

        elif self.tile_type == TILE_GRASS:
            self.destroyable = False
            self.solid = False  # 坦克可以通过
            self.hidden = True  # 坦克隐藏
            # 绘制草地
            self.image.fill((0, 100, 0, 180))
            # 添加草丛纹理
            for _ in range(20):
                import random
                gx = random.randint(0, self.size-4)
                gy = random.randint(0, self.size-4)
                pygame.draw.rect(self.image, COLOR_GREEN, (gx, gy, 4, 8))

        elif self.tile_type == TILE_BASE:
            self.destroyable = False
            self.solid = True
            # 绘制基地
            self.image.fill(COLOR_BLACK)
            # 基地标志
            pygame.draw.polygon(self.image, COLOR_WHITE,
                              [(self.size//2, 4), (self.size-4, self.size//2),
                               (self.size//2, self.size-4), (4, self.size//2)])
            pygame.draw.rect(self.image, COLOR_GREEN, (8, 8, self.size-16, self.size-16), 2)
            # 鹰的标志
            font = pygame.font.SysFont(None, 20)
            text = font.render("鹰", True, COLOR_WHITE)
            text_rect = text.get_rect(center=(self.size//2, self.size//2))
            self.image.blit(text, text_rect)

    def take_damage(self, damage):
        """受到伤害"""
        if self.destroyable:
            self.hp -= damage
            if self.hp <= 0:
                self.tile_type = TILE_EMPTY
                self.solid = False
                self.destroyable = False
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                self.image.fill((0, 0, 0, 0))


class Base(MapTile):
    """玩家基地类"""

    def __init__(self, x, y):
        super().__init__(x, y, TILE_BASE)
        self.destroyed = False

    def destroy(self):
        """基地被摧毁"""
        self.destroyed = True
        self.image.fill(COLOR_BLACK)
        # 绘制爆炸效果
        pygame.draw.circle(self.image, COLOR_RED, (self.size//2, self.size//2), self.size//2-4)
        pygame.draw.circle(self.image, COLOR_WHITE, (self.size//2, self.size//2), self.size//3)


class GameMap:
    """游戏地图类"""

    # 默认关卡地图 (26x26)
    DEFAULT_MAP = [
        "WWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W........................W",
        "W..BB..BB..BB..BB..BB..B.W",
        "W..BB..BB..BB..BB..BB..B.W",
        "W..BB..BB..BB..BB..BB..B.W",
        "W........................W",
        "W..SS..BB......BB..SS..B.W",
        "W..SS..BB......BB..SS..B.W",
        "W......BB..BB..BB......B.W",
        "W......BB..BB..BB......B.W",
        "W..BB......SS......BB..B.W",
        "W..BB......SS......BB..B.W",
        "W..............SS........W",
        "W..BB..BB..BB..BB..BB..B.W",
        "W..BB..BB..BB..BB..BB..B.W",
        "W......SS............BB.W",
        "W......SS............BB.W",
        "W..BB......BB..BB......B.W",
        "W..BB......BB..BB......B.W",
        "W..BB..SS..BB..BB..SS..B.W",
        "W..BB..SS..BB..BB..SS..B.W",
        "W........................W",
        "W..BB..BB..BB..BB..BB..B.W",
        "W..BB..BB..B...BB..BB..B.W",
        "W...........E............W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWW",
    ]

    def __init__(self):
        self.tiles = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.steels = pygame.sprite.Group()
        self.waters = pygame.sprite.Group()
        self.grasses = pygame.sprite.Group()
        self.base = None
        self.width = MAP_WIDTH * TILE_SIZE
        self.height = MAP_HEIGHT * TILE_SIZE

    def load_map(self, map_data=None):
        """加载地图"""
        if map_data is None:
            map_data = self.DEFAULT_MAP

        self.tiles.empty()
        self.bricks.empty()
        self.steels.empty()
        self.waters.empty()
        self.grasses.empty()

        for row_idx, row in enumerate(map_data):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE

                if char == 'B':  # 砖块
                    tile = MapTile(x, y, TILE_BRICK)
                    self.bricks.add(tile)
                    self.tiles.add(tile)
                elif char == 'S':  # 钢铁
                    tile = MapTile(x, y, TILE_STEEL)
                    self.steels.add(tile)
                    self.tiles.add(tile)
                elif char == 'W':  # 水
                    tile = MapTile(x, y, TILE_WATER)
                    self.waters.add(tile)
                    self.tiles.add(tile)
                elif char == 'G':  # 草地
                    tile = MapTile(x, y, TILE_GRASS)
                    self.grasses.add(tile)
                    self.tiles.add(tile)
                elif char == 'E':  # 基地
                    self.base = Base(x, y)
                    self.tiles.add(self.base)

        return True

    def draw(self, surface):
        """绘制地图"""
        # 绘制背景
        surface.fill((0, 0, 0))

        # 绘制所有地图元素
        for tile in self.tiles:
            surface.blit(tile.image, tile.rect)

    def get_spawn_points(self):
        """获取出生点"""
        player_spawn = (4 * TILE_SIZE, 20 * TILE_SIZE)
        enemy_spawns = [
            (4 * TILE_SIZE, 2 * TILE_SIZE),
            (12 * TILE_SIZE, 2 * TILE_SIZE),
            (20 * TILE_SIZE, 2 * TILE_SIZE),
        ]
        return player_spawn, enemy_spawns
