"""
游戏主模块
"""
import pygame
import sys
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, GAME_AREA_TOP,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_VICTORY,
    KEY_PLAYER1_UP, KEY_PLAYER1_DOWN, KEY_PLAYER1_LEFT, KEY_PLAYER1_RIGHT, KEY_PLAYER1_SHOOT,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from logger import setup_logger
from map import GameMap
from tank import PlayerTank, EnemyTank
from bullet import Bullet
from ui import Menu, HUD, GameOverScreen, PauseScreen, LevelSelectScreen
from powerup import PowerUpManager
from particles import ParticleManager, TankTrail
from sounds import SoundManager, MusicManager, create_placeholder_sounds

# 额外游戏状态
STATE_LEVEL_SELECT = 5


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
        self.max_unlocked_level = 1  # 最大解锁关卡

        # 游戏对象
        self.map = None
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        # 道具系统
        self.powerup_manager = PowerUpManager()

        # 粒子效果系统
        self.particle_manager = ParticleManager()
        self.tank_trail = TankTrail()

        # 音效系统
        create_placeholder_sounds()  # 创建音效目录
        self.sound_manager = SoundManager()
        self.music_manager = MusicManager()

        # UI
        self.menu = Menu()
        self.hud = HUD()
        self.pause_screen = PauseScreen()
        self.game_over_screen = None
        self.level_select_screen = None

        # 按键状态
        self.keys_pressed = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'shoot': False,
        }

        self.logger.info("游戏初始化完成")

    def start_game(self, level=1):
        """开始新游戏"""
        self.logger.info(f"开始新游戏 - 第 {level} 关")
        self.state = STATE_PLAYING
        self.score = 0
        self.level = level

        # 清空精灵组
        self.enemies.empty()
        self.bullets.empty()
        self.all_sprites.empty()

        # 重置系统
        self.powerup_manager.clear()
        self.particle_manager.clear()
        self.tank_trail.clear()

        # 加载地图
        self.map = GameMap()
        self.map.load_map(level)

        # 创建玩家
        player_spawn, _ = self.map.get_spawn_points()
        self.player = PlayerTank(player_spawn[0], player_spawn[1])
        self.all_sprites.add(self.player)

        # 创建敌人
        self.spawn_enemies()

        # 播放游戏开始音效
        self.sound_manager.play_game_start()
        self.music_manager.play_game_music()

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
                    elif self.state == STATE_LEVEL_SELECT:
                        self.state = STATE_MENU
                        self.logger.info("返回主菜单")

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

            # 添加移动轨迹
            self.tank_trail.add_trail(self.player)

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
                    self.sound_manager.play_shoot()

        # 更新敌人
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update()
                # 添加移动轨迹
                self.tank_trail.add_trail(enemy)
                # AI更新
                bullet = enemy.ai_update([self.player] if self.player else [], solid_tiles)
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)

        # 更新子弹
        all_tanks = [self.player] + list(self.enemies) if self.player else list(self.enemies)
        all_tanks = [t for t in all_tanks if t is not None]
        for bullet in self.bullets:
            hit_wall = bullet.update(self.map.tiles, all_tanks, self.map.base)
            # 检查子弹是否击中了墙壁
            if not bullet.active and hit_wall:
                self.particle_manager.add_bullet_hit(bullet, is_wall=True)
                self.sound_manager.play_hit()

        # 清理死亡的精灵
        for enemy in list(self.enemies):
            if not enemy.alive:
                # 添加爆炸效果
                self.particle_manager.add_tank_explosion(enemy)
                self.sound_manager.play_explosion()
                self.enemies.remove(enemy)
                self.all_sprites.remove(enemy)
                self.score += 100 * enemy.enemy_type
                self.logger.info(f"消灭敌人，获得 {100 * enemy.enemy_type} 分")
                # 随机生成道具（20%概率）
                if random.random() < 0.2:
                    self.powerup_manager.spawn_powerup(enemy.rect.x, enemy.rect.y)

        for bullet in list(self.bullets):
            if not bullet.active:
                self.bullets.remove(bullet)
                self.all_sprites.remove(bullet)

        # 更新道具系统
        self.powerup_manager.update(self.player, self.enemies, solid_tiles)
        # 随机生成道具
        self.powerup_manager.spawn_random()

        # 更新粒子效果
        self.particle_manager.update()
        self.tank_trail.update()

        # 检查游戏结束条件
        if self.player and not self.player.alive:
            self.logger.info("玩家死亡，游戏结束")
            self.particle_manager.add_tank_explosion(self.player)
            self.sound_manager.play_explosion()
            self.sound_manager.play_game_over()
            self.music_manager.fadeout(1000)
            self.state = STATE_GAME_OVER
            self.game_over_screen = GameOverScreen(victory=False)

        if self.map.base and self.map.base.destroyed:
            self.logger.info("基地被摧毁，游戏结束")
            self.particle_manager.add_base_explosion(self.map.base)
            self.sound_manager.play_explosion()
            self.sound_manager.play_game_over()
            self.music_manager.fadeout(1000)
            self.state = STATE_GAME_OVER
            self.game_over_screen = GameOverScreen(victory=False)

        # 检查胜利条件
        if len([e for e in self.enemies if e.alive]) == 0:
            self.logger.info("所有敌人被消灭，关卡完成")
            self.sound_manager.play_victory()
            if self.level < 5:
                self.level += 1
                # 解锁新关卡
                if self.level > self.max_unlocked_level:
                    self.max_unlocked_level = self.level
                self.spawn_enemies()
            else:
                # 通关所有关卡
                self.logger.info("恭喜！通关所有关卡！")
                self.music_manager.fadeout(1000)
                self.state = STATE_GAME_OVER
                self.game_over_screen = GameOverScreen(victory=True)

        # 更新HUD
        self.hud.score = self.score
        self.hud.level = self.level

    def draw(self):
        """绘制游戏画面"""
        if self.state == STATE_MENU:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.menu.update(mouse_pos, mouse_pressed)

            if result == 'start':
                self.state = STATE_LEVEL_SELECT
                self.level_select_screen = LevelSelectScreen(max_level=5)
            elif result == 'quit':
                self.running = False

            self.menu.draw(self.screen)

        elif self.state == STATE_LEVEL_SELECT:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.level_select_screen.update(mouse_pos, mouse_pressed)

            if result and result.startswith('level_'):
                level = int(result.split('_')[1])
                self.start_game(level)
            elif result == 'back':
                self.state = STATE_MENU

            self.level_select_screen.draw(self.screen)

        elif self.state == STATE_PLAYING:
            # 绘制地图
            if self.map:
                self.map.draw(self.screen)

            # 绘制坦克轨迹
            self.tank_trail.draw(self.screen)

            # 绘制道具
            self.powerup_manager.draw(self.screen)

            # 绘制所有精灵
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
                if hasattr(sprite, 'draw_hp'):
                    sprite.draw_hp(self.screen)
                if hasattr(sprite, 'draw_shield'):
                    sprite.draw_shield(self.screen)

            # 绘制粒子效果
            self.particle_manager.draw(self.screen)

            # 绘制HUD
            self.hud.draw(self.screen, [self.player] if self.player else [], self.enemies)

            # 绘制当前生效的效果
            self.powerup_manager.draw_active_effects(self.screen, 10, GAME_AREA_TOP + 10)

        elif self.state == STATE_PAUSED:
            # 先绘制游戏画面
            if self.map:
                self.map.draw(self.screen)

            # 绘制坦克轨迹
            self.tank_trail.draw(self.screen)

            # 绘制道具
            self.powerup_manager.draw(self.screen)

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
                if hasattr(sprite, 'draw_hp'):
                    sprite.draw_hp(self.screen)
                if hasattr(sprite, 'draw_shield'):
                    sprite.draw_shield(self.screen)

            # 绘制粒子效果
            self.particle_manager.draw(self.screen)
            self.hud.draw(self.screen, [self.player] if self.player else [], self.enemies)

            # 再绘制暂停界面
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.pause_screen.update(mouse_pos, mouse_pressed)

            if result == 'resume':
                self.state = STATE_PLAYING
            elif result == 'restart':
                self.start_game(self.level)
            elif result == 'menu':
                self.state = STATE_MENU
            elif result == 'quit':
                self.running = False

            self.pause_screen.draw(self.screen)

        elif self.state == STATE_GAME_OVER:
            # 绘制游戏画面
            if self.map:
                self.map.draw(self.screen)

            # 绘制坦克轨迹
            self.tank_trail.draw(self.screen)

            # 绘制道具
            self.powerup_manager.draw(self.screen)

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
                if hasattr(sprite, 'draw_hp'):
                    sprite.draw_hp(self.screen)
                if hasattr(sprite, 'draw_shield'):
                    sprite.draw_shield(self.screen)

            # 绘制粒子效果
            self.particle_manager.draw(self.screen)

            # 绘制游戏结束界面
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.game_over_screen.update(mouse_pos, mouse_pressed)

            if result == 'restart':
                self.start_game(self.level)
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
