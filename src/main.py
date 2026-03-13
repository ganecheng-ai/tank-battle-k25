"""
游戏主模块
"""
import pygame
import sys
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, GAME_AREA_TOP,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_VICTORY,
    MODE_SINGLE, MODE_TWO_PLAYER,
    KEY_PLAYER1_UP, KEY_PLAYER1_DOWN, KEY_PLAYER1_LEFT, KEY_PLAYER1_RIGHT, KEY_PLAYER1_SHOOT,
    KEY_PLAYER2_UP, KEY_PLAYER2_DOWN, KEY_PLAYER2_LEFT, KEY_PLAYER2_RIGHT, KEY_PLAYER2_SHOOT,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from logger import setup_logger
from map import GameMap
from tank import PlayerTank, EnemyTank
from bullet import Bullet
from ui import Menu, HUD, GameOverScreen, PauseScreen, LevelSelectScreen, SaveSelectScreen
from powerup import PowerUpManager
from particles import ParticleManager, TankTrail
from sounds import SoundManager, MusicManager, create_placeholder_sounds
from save_manager import SaveManager

# 额外游戏状态
STATE_LEVEL_SELECT = 5
STATE_SAVE_SELECT = 6
STATE_LOAD_SELECT = 7


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
        self.game_mode = MODE_SINGLE  # 游戏模式：单人/双人
        self.score = 0
        self.level = 1
        self.max_unlocked_level = 1  # 最大解锁关卡

        # 游戏对象
        self.map = None
        self.player = None
        self.player2 = None  # 双人模式玩家2
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

        # 存档系统
        self.save_manager = SaveManager()

        # UI
        self.menu = Menu()
        self.hud = HUD()
        self.pause_screen = PauseScreen()
        self.game_over_screen = None
        self.level_select_screen = None
        self.save_select_screen = None
        self.load_select_screen = None

        # 按键状态
        self.keys_pressed = {
            'p1_up': False, 'p1_down': False, 'p1_left': False, 'p1_right': False, 'p1_shoot': False,
            'p2_up': False, 'p2_down': False, 'p2_left': False, 'p2_right': False, 'p2_shoot': False,
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

        # 创建玩家1
        player_spawn, _ = self.map.get_spawn_points()
        self.player = PlayerTank(player_spawn[0], player_spawn[1], player_num=1)
        self.all_sprites.add(self.player)

        # 双人模式下创建玩家2
        if self.game_mode == MODE_TWO_PLAYER:
            player2_spawn = (player_spawn[0] + 64, player_spawn[1])  # 在玩家1右侧
            self.player2 = PlayerTank(player2_spawn[0], player2_spawn[1], player_num=2)
            self.all_sprites.add(self.player2)
        else:
            self.player2 = None

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
                    # 玩家1按键
                    if event.key == KEY_PLAYER1_UP:
                        self.keys_pressed['p1_up'] = True
                    elif event.key == KEY_PLAYER1_DOWN:
                        self.keys_pressed['p1_down'] = True
                    elif event.key == KEY_PLAYER1_LEFT:
                        self.keys_pressed['p1_left'] = True
                    elif event.key == KEY_PLAYER1_RIGHT:
                        self.keys_pressed['p1_right'] = True
                    elif event.key == KEY_PLAYER1_SHOOT:
                        self.keys_pressed['p1_shoot'] = True
                    # 玩家2按键
                    elif event.key == KEY_PLAYER2_UP:
                        self.keys_pressed['p2_up'] = True
                    elif event.key == KEY_PLAYER2_DOWN:
                        self.keys_pressed['p2_down'] = True
                    elif event.key == KEY_PLAYER2_LEFT:
                        self.keys_pressed['p2_left'] = True
                    elif event.key == KEY_PLAYER2_RIGHT:
                        self.keys_pressed['p2_right'] = True
                    elif event.key == KEY_PLAYER2_SHOOT:
                        self.keys_pressed['p2_shoot'] = True

                elif event.type == pygame.KEYUP:
                    # 玩家1按键释放
                    if event.key == KEY_PLAYER1_UP:
                        self.keys_pressed['p1_up'] = False
                    elif event.key == KEY_PLAYER1_DOWN:
                        self.keys_pressed['p1_down'] = False
                    elif event.key == KEY_PLAYER1_LEFT:
                        self.keys_pressed['p1_left'] = False
                    elif event.key == KEY_PLAYER1_RIGHT:
                        self.keys_pressed['p1_right'] = False
                    elif event.key == KEY_PLAYER1_SHOOT:
                        self.keys_pressed['p1_shoot'] = False
                    # 玩家2按键释放
                    elif event.key == KEY_PLAYER2_UP:
                        self.keys_pressed['p2_up'] = False
                    elif event.key == KEY_PLAYER2_DOWN:
                        self.keys_pressed['p2_down'] = False
                    elif event.key == KEY_PLAYER2_LEFT:
                        self.keys_pressed['p2_left'] = False
                    elif event.key == KEY_PLAYER2_RIGHT:
                        self.keys_pressed['p2_right'] = False
                    elif event.key == KEY_PLAYER2_SHOOT:
                        self.keys_pressed['p2_shoot'] = False

    def update(self):
        """更新游戏状态"""
        if self.state != STATE_PLAYING:
            return

        # 获取可碰撞的地图元素
        solid_tiles = [t for t in self.map.tiles if t.solid]

        # 更新玩家1
        if self.player and self.player.alive:
            self.player.update()
            self.tank_trail.add_trail(self.player)

            # 处理玩家1移动
            moved = False
            if self.keys_pressed['p1_up']:
                moved = self.player.move(DIR_UP, solid_tiles, self.enemies)
            elif self.keys_pressed['p1_down']:
                moved = self.player.move(DIR_DOWN, solid_tiles, self.enemies)
            elif self.keys_pressed['p1_left']:
                moved = self.player.move(DIR_LEFT, solid_tiles, self.enemies)
            elif self.keys_pressed['p1_right']:
                moved = self.player.move(DIR_RIGHT, solid_tiles, self.enemies)
            else:
                self.player.stop()

            # 处理玩家1射击
            if self.keys_pressed['p1_shoot']:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    self.sound_manager.play_shoot()

        # 更新玩家2（双人模式）
        if self.player2 and self.player2.alive:
            self.player2.update()
            self.tank_trail.add_trail(self.player2)

            # 处理玩家2移动
            if self.keys_pressed['p2_up']:
                self.player2.move(DIR_UP, solid_tiles, self.enemies)
            elif self.keys_pressed['p2_down']:
                self.player2.move(DIR_DOWN, solid_tiles, self.enemies)
            elif self.keys_pressed['p2_left']:
                self.player2.move(DIR_LEFT, solid_tiles, self.enemies)
            elif self.keys_pressed['p2_right']:
                self.player2.move(DIR_RIGHT, solid_tiles, self.enemies)
            else:
                self.player2.stop()

            # 处理玩家2射击
            if self.keys_pressed['p2_shoot']:
                bullet = self.player2.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    self.sound_manager.play_shoot()

        # 更新敌人
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update()
                self.tank_trail.add_trail(enemy)
                # AI更新 - 同时考虑两个玩家
                players = [p for p in [self.player, self.player2] if p and p.alive]
                bullet = enemy.ai_update(players, solid_tiles)
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)

        # 更新子弹
        all_tanks = [t for t in [self.player, self.player2] + list(self.enemies) if t and t.alive]
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

        # 更新道具系统 - 检查两个玩家
        players = [p for p in [self.player, self.player2] if p and p.alive]
        for player in players:
            self.powerup_manager.update(player, self.enemies, solid_tiles)
        # 随机生成道具
        self.powerup_manager.spawn_random()

        # 更新粒子效果
        self.particle_manager.update()
        self.tank_trail.update()

        # 检查游戏结束条件
        # 单人模式：玩家死亡游戏结束
        # 双人模式：两个玩家都死亡游戏结束
        players_alive = [p for p in [self.player, self.player2] if p and p.alive]
        if len(players_alive) == 0 and (self.player or self.player2):
            self.logger.info("玩家死亡，游戏结束")
            if self.player and not self.player.alive:
                self.particle_manager.add_tank_explosion(self.player)
            if self.player2 and not self.player2.alive:
                self.particle_manager.add_tank_explosion(self.player2)
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
                # 恢复存活玩家的生命值
                for p in players_alive:
                    if p.hp < p.max_hp:
                        p.hp = min(p.hp + 1, p.max_hp)
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
        self.hud.players = [self.player, self.player2] if self.game_mode == MODE_TWO_PLAYER else [self.player]

    def save_game(self, slot):
        """保存游戏状态"""
        if not self.player:
            self.logger.warning("没有可保存的游戏状态")
            return False

        # 构建游戏状态
        game_state = {
            "level": self.level,
            "score": self.score,
            "max_unlocked_level": self.max_unlocked_level,
            "player": {
                "hp": self.player.hp,
                "max_hp": self.player.max_hp,
                "x": self.player.rect.x,
                "y": self.player.rect.y,
                "direction": self.player.direction,
                "shield": self.player.shield,
                "armor_piercing": self.player.armor_piercing,
            },
            "enemies": [
                {
                    "x": enemy.rect.x,
                    "y": enemy.rect.y,
                    "type": enemy.enemy_type,
                    "hp": enemy.hp,
                    "direction": enemy.direction,
                }
                for enemy in self.enemies if enemy.alive
            ],
            "active_effects": self._get_active_effects(),
        }

        if self.save_manager.save_game(slot, game_state):
            self.logger.info(f"游戏已保存到槽位 {slot}")
            return True
        return False

    def load_game(self, slot):
        """加载游戏状态"""
        game_state = self.save_manager.load_game(slot)
        if not game_state:
            self.logger.warning(f"无法从槽位 {slot} 加载游戏")
            return False

        try:
            self.logger.info(f"从槽位 {slot} 加载游戏")

            # 恢复基本状态
            self.level = game_state.get("level", 1)
            self.score = game_state.get("score", 0)
            self.max_unlocked_level = game_state.get("max_unlocked_level", 1)
            self.state = STATE_PLAYING

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
            self.map.load_map(self.level)

            # 恢复玩家状态
            player_data = game_state.get("player", {})
            player_spawn = self.map.get_spawn_points()[0]
            self.player = PlayerTank(
                player_data.get("x", player_spawn[0]),
                player_data.get("y", player_spawn[1])
            )
            self.player.hp = player_data.get("hp", 3)
            self.player.max_hp = player_data.get("max_hp", 3)
            self.player.direction = player_data.get("direction", 0)
            self.player.image = self.player.images[self.player.direction]
            self.player.shield = player_data.get("shield", False)
            self.player.armor_piercing = player_data.get("armor_piercing", False)
            self.all_sprites.add(self.player)

            # 恢复敌人
            for enemy_data in game_state.get("enemies", []):
                enemy = EnemyTank(
                    enemy_data.get("x", 0),
                    enemy_data.get("y", 0),
                    enemy_data.get("type", 1)
                )
                enemy.hp = enemy_data.get("hp", 1)
                enemy.direction = enemy_data.get("direction", 0)
                enemy.image = enemy.images[enemy.direction]
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

            # 恢复道具效果
            effects_data = game_state.get("active_effects", {})
            self._restore_effects(effects_data)

            # 更新HUD
            self.hud.score = self.score
            self.hud.level = self.level

            # 播放游戏开始音效
            self.sound_manager.play_game_start()
            self.music_manager.play_game_music()

            self.logger.info("游戏加载完成")
            return True

        except Exception as e:
            self.logger.error(f"加载游戏失败: {e}")
            return False

    def _get_active_effects(self):
        """获取当前生效的道具效果"""
        effects = {}
        for tank, tank_effects in self.powerup_manager.active_effects.items():
            if tank.is_player:
                effects = tank_effects.copy()
                break
        return effects

    def _restore_effects(self, effects_data):
        """恢复道具效果"""
        if effects_data and self.player:
            self.powerup_manager.active_effects[self.player] = effects_data.copy()
            # 重新应用效果
            for effect_type, remaining in effects_data.items():
                if effect_type == 2:  # 速度提升
                    self.player.speed = int(self.player.speed * 1.5)
                elif effect_type == 3:  # 穿甲弹
                    self.player.armor_piercing = True
                elif effect_type == 4:  # 护盾
                    self.player.shield = True

    def draw(self):
        """绘制游戏画面"""
        if self.state == STATE_MENU:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.menu.update(mouse_pos, mouse_pressed)

            if result == 'single':
                self.game_mode = MODE_SINGLE
                self.state = STATE_LEVEL_SELECT
                self.level_select_screen = LevelSelectScreen(max_level=5)
            elif result == 'two_player':
                self.game_mode = MODE_TWO_PLAYER
                self.state = STATE_LEVEL_SELECT
                self.level_select_screen = LevelSelectScreen(max_level=5)
            elif result == 'load':
                self.state = STATE_LOAD_SELECT
                self.load_select_screen = SaveSelectScreen(self.save_manager, is_save=False)
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

        elif self.state == STATE_SAVE_SELECT:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.save_select_screen.update(mouse_pos, mouse_pressed)

            if result and result.startswith('slot_'):
                slot = int(result.split('_')[1])
                self.save_game(slot)
                self.state = STATE_PAUSED
            elif result == 'back':
                self.state = STATE_PAUSED

            self.save_select_screen.draw(self.screen)

        elif self.state == STATE_LOAD_SELECT:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.load_select_screen.update(mouse_pos, mouse_pressed)

            if result and result.startswith('slot_'):
                slot = int(result.split('_')[1])
                if self.load_game(slot):
                    self.state = STATE_PLAYING
                else:
                    self.state = STATE_MENU
            elif result == 'back':
                self.state = STATE_MENU

            self.load_select_screen.draw(self.screen)

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
            players = [p for p in [self.player, self.player2] if p]
            self.hud.draw(self.screen, players, self.enemies)

            # 绘制当前生效的效果（玩家1）
            if self.player and self.player.alive:
                self.powerup_manager.draw_active_effects(self.screen, 10, GAME_AREA_TOP + 10)
            # 绘制当前生效的效果（玩家2）
            if self.player2 and self.player2.alive:
                self.powerup_manager.draw_active_effects(self.screen, SCREEN_WIDTH - 100, GAME_AREA_TOP + 10)

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
            players = [p for p in [self.player, self.player2] if p]
            self.hud.draw(self.screen, players, self.enemies)

            # 再绘制暂停界面
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            result = self.pause_screen.update(mouse_pos, mouse_pressed)

            if result == 'resume':
                self.state = STATE_PLAYING
            elif result == 'restart':
                self.start_game(self.level)
            elif result == 'save':
                self.state = STATE_SAVE_SELECT
                self.save_select_screen = SaveSelectScreen(self.save_manager, is_save=True)
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
