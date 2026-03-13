"""
游戏主模块
"""
import pygame
import sys
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, GAME_AREA_TOP,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_VICTORY,
    STATE_LEVEL_SELECT,
    KEY_PLAYER1_UP, KEY_PLAYER1_DOWN, KEY_PLAYER1_LEFT, KEY_PLAYER1_RIGHT, KEY_PLAYER1_SHOOT,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from logger import setup_logger
from map import GameMap
from tank import PlayerTank, EnemyTank
from bullet import Bullet
from ui import Menu, HUD, GameOverScreen, PauseScreen, LevelSelectScreen


class Game:
    """游戏主类"""

    def __init__(self):
        # 初始化日志
        self.logger = setup_logger("tank_battle")
        self.logger.info("初始化游戏...")

        # 初始化Pygame
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # 游戏状态
        self.state = STATE_MENU
        self.score = 0
        self.level = 1

        # 游戏对象
        self.map = None
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        # UI
        self.menu = Menu()
        self.level_select = LevelSelectScreen()
        self.hud = HUD()
        self.pause_screen = PauseScreen()
        self.game_over_screen = None

        # 按键状态
        self.keys_pressed = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'shoot': False,
        }

        self.logger.info("游戏初始化完成")

    def start_game(self):
        """开始新游戏"""
        self.logger.info("开始新游戏")
        self.state = STATE_PLAYING
        self.score = 0
        self.level = 1

        # 清空精灵组
        self.enemies.empty()
        self.bullets.empty()
        self.all_sprites.empty()

        # 加载地图
        self.map = GameMap()
        self.map.load_map()

        # 创建玩家
        player_spawn, _ = self.map.get_spawn_points()
        self.player = PlayerTank(player_spawn[0], player_spawn[1])
        self.all_sprites.add(self.player)

        # 创建敌人
        self.spawn_enemies()

        # 更新HUD
        self.hud.score = self.score
        self.hud.level = self.level

    def spawn_enemies(self):
        """生成敌人"""
        _, enemy_spawns = self.map.get_spawn_points()
        num_enemies = min(3 + self.level, 6)

        for i in range(num_enemies):
            if i < len(enemy_spawns):
                # 随机敌人类型
                enemy_type = random.randint(1, 4)
                enemy = EnemyTank(enemy_spawns[i][0], enemy_spawns[i][1], enemy_type)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.logger.info("游戏退出")
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                        self.logger.info("游戏暂停")
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                        self.logger.info("游戏继续")

            if self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == KEY_PLAYER1_UP:
                        self.keys_pressed['up'] = True
                    elif event.key == KEY_PLAYER1_DOWN:
                        self.keys_pressed['down'] = True
                    elif event.key == KEY_PLAYER1_LEFT:
                        self.keys_pressed['left'] = True
                    elif event.key == KEY_PLAYER1_RIGHT:
                        self.keys_pressed['right'] = True
                    elif event.key == KEY_PLAYER1_SHOOT:
                        self.keys_pressed['shoot'] = True

                elif event.type == pygame.KEYUP:
                    if event.key == KEY_PLAYER1_UP:
                        self.keys_pressed['up'] = False
                    elif event.key == KEY_PLAYER1_DOWN:
                        self.keys_pressed['down'] = False
                    elif event.key == KEY_PLAYER1_LEFT:
                        self.keys_pressed['left'] = False
                    elif event.key == KEY_PLAYER1_RIGHT:
                        self.keys_pressed['right'] = False
                    elif event.key == KEY_PLAYER1_SHOOT:
                        self.keys_pressed['shoot'] = False

    def update(self):
        """更新游戏状态"""
        if self.state != STATE_PLAYING:
            return

        # 获取可碰撞的地图元素
        solid_tiles = [t for t in self.map.tiles if t.solid]

        # 更新玩家
        if self.player and self.player.alive:
            self.player.update()

            # 处理玩家移动
            moved = False
            if self.keys_pressed['up']:
                moved = self.player.move(DIR_UP, solid_tiles, self.enemies)
            elif self.keys_pressed['down']:
                moved = self.player.move(DIR_DOWN, solid_tiles, self.enemies)
            elif self.keys_pressed['left']:
                moved = self.player.move(DIR_LEFT, solid_tiles, self.enemies)
            elif self.keys_pressed['right']:
                moved = self.player.move(DIR_RIGHT, solid_tiles, self.enemies)
            else:
                self.player.stop()

            # 处理射击
            if self.keys_pressed['shoot']:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)

        # 更新敌人
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update()
                # AI更新
                bullet = enemy.ai_update([self.player] if self.player else [], solid_tiles)
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)

        # 更新子弹
        all_tanks = [self.player] + list(self.enemies) if self.player else list(self.enemies)
        all_tanks = [t for t in all_tanks if t is not None]
        for bullet in self.bullets:
            bullet.update(self.map.tiles, all_tanks, self.map.base)

        # 清理死亡的精灵
        for enemy in list(self.enemies):
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.all_sprites.remove(enemy)
                self.score += 100 * enemy.enemy_type
                self.logger.info(f"消灭敌人，获得 {100 * enemy.enemy_type} 分")

        for bullet in list(self.bullets):
            if not bullet.active:
                self.bullets.remove(bullet)
                self.all_sprites.remove(bullet)

        # 检查游戏结束条件
        if self.player and not self.player.alive:
            self.logger.info("玩家死亡，游戏结束")
            self.state = STATE_GAME_OVER
            self.game_over_screen = GameOverScreen(victory=False)

        if self.map.base and self.map.base.destroyed:
            self.logger.info("基地被摧毁，游戏结束")
            self.state = STATE_GAME_OVER
            self.game_over_screen = GameOverScreen(victory=False)

        # 检查胜利条件
        if len([e for e in self.enemies if e.alive]) == 0:
            self.logger.info("所有敌人被消灭，关卡完成")
            self.level += 1
            self.spawn_enemies()

        # 更新HUD
        self.hud.score = self.score

    def draw(self):
        """绘制游戏画面"""
        if self.state == STATE_MENU:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.menu.update(mouse_pos, mouse_pressed)

            if result == 'start':
                self.state = STATE_LEVEL_SELECT
            elif result == 'quit':
                self.running = False

            self.menu.draw(self.screen)

        elif self.state == STATE_LEVEL_SELECT:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.level_select.update(mouse_pos, mouse_pressed)

            if result == 'start':
                self.level = self.level_select.get_selected_level()
                self.start_game()
            elif result == 'back':
                self.state = STATE_MENU

            self.level_select.draw(self.screen)

        elif self.state == STATE_PLAYING:
            # 绘制地图
            if self.map:
                self.map.draw(self.screen)

            # 绘制所有精灵
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
                if hasattr(sprite, 'draw_hp'):
                    sprite.draw_hp(self.screen)

            # 绘制HUD
            self.hud.draw(self.screen, [self.player] if self.player else [], self.enemies)

        elif self.state == STATE_PAUSED:
            # 先绘制游戏画面
            if self.map:
                self.map.draw(self.screen)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            self.hud.draw(self.screen, [self.player] if self.player else [], self.enemies)

            # 再绘制暂停界面
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.pause_screen.update(mouse_pos, mouse_pressed)

            if result == 'resume':
                self.state = STATE_PLAYING
            elif result == 'restart':
                self.start_game()
            elif result == 'menu':
                self.state = STATE_MENU
            elif result == 'quit':
                self.running = False

            self.pause_screen.draw(self.screen)

        elif self.state == STATE_GAME_OVER:
            # 绘制游戏画面
            if self.map:
                self.map.draw(self.screen)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)

            # 绘制游戏结束界面
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.game_over_screen.update(mouse_pos, mouse_pressed)

            if result == 'restart':
                self.start_game()
            elif result == 'menu':
                self.state = STATE_MENU
            elif result == 'quit':
                self.running = False

            self.game_over_screen.draw(self.screen, self.score)

        pygame.display.flip()

    def run(self):
        """游戏主循环"""
        self.logger.info("游戏主循环开始")

        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        self.logger.info("游戏主循环结束")
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
