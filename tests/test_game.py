"""
游戏自验证测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import pygame
from unittest.mock import patch, MagicMock

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, VERSION,
    TANK_SIZE, TILE_SIZE, PLAYER_SPEED, ENEMY_SPEED, BULLET_SPEED
)
from logger import setup_logger
from map import GameMap, MapTile, Base
from tank import Tank, PlayerTank, EnemyTank
from bullet import Bullet
from ui import Button, Menu, HUD, GameOverScreen, PauseScreen, LevelSelectScreen


class TestConfig(unittest.TestCase):
    """测试配置文件"""

    def test_version(self):
        """测试版本号"""
        self.assertEqual(VERSION, "0.3.0")

    def test_screen_settings(self):
        """测试屏幕设置"""
        self.assertEqual(SCREEN_WIDTH, 800)
        self.assertEqual(SCREEN_HEIGHT, 600)
        self.assertEqual(FPS, 60)

    def test_game_constants(self):
        """测试游戏常量"""
        self.assertEqual(TANK_SIZE, 32)
        self.assertEqual(TILE_SIZE, 32)
        self.assertEqual(PLAYER_SPEED, 2)
        self.assertEqual(ENEMY_SPEED, 1)
        self.assertEqual(BULLET_SPEED, 4)


class TestLogger(unittest.TestCase):
    """测试日志系统"""

    def test_logger_creation(self):
        """测试日志记录器创建"""
        logger = setup_logger("test_logger")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")

    def test_log_file_created(self):
        """测试日志文件创建"""
        logger = setup_logger("test_file")
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        self.assertTrue(os.path.exists(log_dir))


class TestMap(unittest.TestCase):
    """测试地图系统"""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_map_tile_creation(self):
        """测试地图元素创建"""
        tile = MapTile(0, 0, 1)  # 砖块
        self.assertEqual(tile.tile_type, 1)
        self.assertTrue(tile.solid)
        self.assertTrue(tile.destroyable)

        tile_steel = MapTile(0, 0, 2)  # 钢铁
        self.assertTrue(tile_steel.solid)
        self.assertFalse(tile_steel.destroyable)

    def test_base_creation(self):
        """测试基地创建"""
        base = Base(100, 100)
        self.assertFalse(base.destroyed)
        self.assertEqual(base.tile_type, 5)

    def test_game_map_load(self):
        """测试地图加载"""
        game_map = GameMap()
        result = game_map.load_map()
        self.assertTrue(result)
        self.assertTrue(len(game_map.tiles) > 0)

    def test_game_map_load_level(self):
        """测试加载特定关卡"""
        game_map = GameMap()
        # 测试加载各个关卡
        for level in range(1, 6):
            result = game_map.load_map(level)
            self.assertTrue(result)
            self.assertEqual(game_map.current_level, level)
            self.assertTrue(len(game_map.tiles) > 0)

    def test_game_map_level_count(self):
        """测试关卡数量"""
        game_map = GameMap()
        self.assertEqual(game_map.get_level_count(), 5)

    def test_spawn_points(self):
        """测试出生点"""
        game_map = GameMap()
        player_spawn, enemy_spawns = game_map.get_spawn_points()
        self.assertIsNotNone(player_spawn)
        self.assertEqual(len(enemy_spawns), 3)


class TestTank(unittest.TestCase):
    """测试坦克系统"""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_player_tank_creation(self):
        """测试玩家坦克创建"""
        tank = PlayerTank(100, 100, 1)
        self.assertTrue(tank.is_player)
        self.assertEqual(tank.hp, 3)
        self.assertEqual(tank.max_hp, 3)
        self.assertTrue(tank.alive)

    def test_enemy_tank_creation(self):
        """测试敌人坦克创建"""
        enemy = EnemyTank(100, 100, 1)
        self.assertFalse(enemy.is_player)
        self.assertTrue(enemy.alive)
        self.assertIn(enemy.enemy_type, [1, 2, 3, 4])

    def test_enemy_types(self):
        """测试不同类型敌人"""
        # 普通坦克
        normal = EnemyTank(100, 100, 1)
        self.assertEqual(normal.hp, 1)

        # 快速坦克
        fast = EnemyTank(100, 100, 2)
        self.assertEqual(fast.speed, ENEMY_SPEED * 2)

        # 重型坦克
        heavy = EnemyTank(100, 100, 3)
        self.assertEqual(heavy.hp, 3)

        # 超级坦克
        super_tank = EnemyTank(100, 100, 4)
        self.assertEqual(super_tank.hp, 4)

    def test_tank_damage(self):
        """测试坦克受伤"""
        tank = PlayerTank(100, 100)
        tank.take_damage(1)
        self.assertEqual(tank.hp, 2)

        tank.take_damage(2)
        self.assertFalse(tank.alive)

    def test_tank_shoot(self):
        """测试坦克射击"""
        tank = PlayerTank(100, 100)
        bullet = tank.shoot()
        self.assertIsNotNone(bullet)
        self.assertIsInstance(bullet, Bullet)


class TestBullet(unittest.TestCase):
    """测试子弹系统"""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_bullet_creation(self):
        """测试子弹创建"""
        bullet = Bullet(100, 100, 0, True)  # 玩家子弹，向上
        self.assertTrue(bullet.active)
        self.assertTrue(bullet.is_player)
        self.assertEqual(bullet.direction, 0)

    def test_bullet_movement(self):
        """测试子弹移动"""
        bullet = Bullet(100, 100, 0, True)  # 向上
        initial_y = bullet.rect.y
        bullet.update([], [], None)
        self.assertTrue(bullet.rect.y < initial_y)


class TestUI(unittest.TestCase):
    """测试UI系统"""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_button_creation(self):
        """测试按钮创建"""
        button = Button(100, 100, 200, 50, "测试按钮")
        self.assertEqual(button.text, "测试按钮")
        self.assertEqual(button.rect.width, 200)
        self.assertEqual(button.rect.height, 50)

    def test_menu_creation(self):
        """测试菜单创建"""
        menu = Menu()
        self.assertIn('start', menu.buttons)
        self.assertIn('quit', menu.buttons)

    def test_hud_creation(self):
        """测试HUD创建"""
        hud = HUD()
        self.assertEqual(hud.score, 0)
        self.assertEqual(hud.lives, 3)
        self.assertEqual(hud.level, 1)

    def test_pause_screen_creation(self):
        """测试暂停界面创建"""
        pause = PauseScreen()
        self.assertIn('resume', pause.buttons)
        self.assertIn('quit', pause.buttons)

    def test_game_over_screen_creation(self):
        """测试游戏结束界面创建"""
        game_over = GameOverScreen(victory=False)
        self.assertFalse(game_over.victory)

    def test_level_select_screen_creation(self):
        """测试关卡选择界面创建"""
        level_select = LevelSelectScreen(max_level=5)
        self.assertEqual(level_select.max_level, 5)
        self.assertEqual(level_select.selected_level, 1)
        self.assertEqual(len(level_select.level_buttons), 5)

    def test_level_buttons(self):
        """测试关卡按钮"""
        level_select = LevelSelectScreen(max_level=3)
        # 检查每个关卡的按钮
        for i, (level, btn) in enumerate(level_select.level_buttons):
            self.assertEqual(level, i + 1)
            self.assertEqual(btn.text, str(i + 1))


class TestIntegration(unittest.TestCase):
    """集成测试"""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_game_initialization(self):
        """测试游戏初始化"""
        from main import Game

        # 使用补丁避免实际初始化 Pygame 显示
        with patch.object(pygame.display, 'set_mode', return_value=MagicMock()):
            with patch.object(pygame.display, 'set_caption'):
                game = Game()
                self.assertEqual(game.state, 0)  # STATE_MENU
                self.assertEqual(game.score, 0)
                self.assertTrue(game.running)

    def test_map_and_tanks(self):
        """测试地图和坦克交互"""
        game_map = GameMap()
        game_map.load_map()

        tank = PlayerTank(100, 100)
        solid_tiles = [t for t in game_map.tiles if t.solid]

        # 坦克不应该能够穿过墙壁
        result = tank.move(0, solid_tiles, [])  # 尝试向上移动
        # 结果取决于位置，但方法应该正常执行
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestMap))
    suite.addTests(loader.loadTestsFromTestCase(TestTank))
    suite.addTests(loader.loadTestsFromTestCase(TestBullet))
    suite.addTests(loader.loadTestsFromTestCase(TestUI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果
    print("\n" + "="*70)
    print(f"测试运行: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*70)

    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)
