"""
UI模块 - 游戏界面元素
"""
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GAME_AREA_TOP,
    COLOR_WHITE, COLOR_BLACK, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_GRAY,
    FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE, FONT_SIZE_HUGE,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_VICTORY
)


class Button:
    """按钮类"""

    def __init__(self, x, y, width, height, text, font_size=FONT_SIZE_NORMAL):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.normal_color = COLOR_GRAY
        self.hover_color = COLOR_GREEN
        self.text_color = COLOR_WHITE
        self.hovered = False
        self.clicked = False

    def draw(self, surface):
        """绘制按钮"""
        color = self.hover_color if self.hovered else self.normal_color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_WHITE, self.rect, 2, border_radius=5)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos, mouse_pressed):
        """更新按钮状态"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.clicked = self.hovered and mouse_pressed[0]
        return self.clicked


class Menu:
    """菜单类"""

    def __init__(self):
        self.font_title = pygame.font.SysFont(None, FONT_SIZE_HUGE)
        self.font_normal = pygame.font.SysFont(None, FONT_SIZE_NORMAL)

        # 创建按钮
        button_width = 200
        button_height = 50
        start_x = (SCREEN_WIDTH - button_width) // 2
        start_y = 200

        self.buttons = {
            'start': Button(start_x, start_y, button_width, button_height, "开始游戏"),
            'options': Button(start_x, start_y + 70, button_width, button_height, "游戏设置"),
            'help': Button(start_x, start_y + 140, button_width, button_height, "游戏帮助"),
            'quit': Button(start_x, start_y + 210, button_width, button_height, "退出游戏"),
        }

    def draw(self, surface):
        """绘制菜单"""
        # 背景
        surface.fill(COLOR_BLACK)

        # 标题
        title = self.font_title.render("坦克大战", True, COLOR_GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)

        # 版本号
        from config import VERSION
        version = self.font_normal.render(f"v{VERSION}", True, COLOR_GRAY)
        version_rect = version.get_rect(center=(SCREEN_WIDTH // 2, 140))
        surface.blit(version, version_rect)

        # 按钮
        for button in self.buttons.values():
            button.draw(surface)

    def update(self, mouse_pos, mouse_pressed):
        """更新菜单状态"""
        for key, button in self.buttons.items():
            if button.update(mouse_pos, mouse_pressed):
                return key
        return None


class HUD:
    """游戏界面抬头显示"""

    def __init__(self):
        self.font = pygame.font.SysFont(None, FONT_SIZE_NORMAL)
        self.font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
        self.score = 0
        self.lives = 3
        self.level = 1
        self.enemy_count = 0

    def draw(self, surface, player_tanks, enemies):
        """绘制游戏HUD"""
        # 顶部状态栏背景
        pygame.draw.rect(surface, COLOR_GRAY, (0, 0, SCREEN_WIDTH, GAME_AREA_TOP))
        pygame.draw.line(surface, COLOR_WHITE, (0, GAME_AREA_TOP), (SCREEN_WIDTH, GAME_AREA_TOP), 2)

        # 分数
        score_text = self.font.render(f"分数: {self.score}", True, COLOR_WHITE)
        surface.blit(score_text, (10, 15))

        # 关卡
        level_text = self.font.render(f"关卡: {self.level}", True, COLOR_WHITE)
        surface.blit(level_text, (200, 15))

        # 敌人数量
        enemy_count = len([e for e in enemies if e.alive])
        enemy_text = self.font.render(f"敌人: {enemy_count}", True, COLOR_RED)
        surface.blit(enemy_text, (350, 15))

        # 生命值
        lives = sum([t.hp for t in player_tanks if t.alive])
        lives_text = self.font.render(f"生命: {lives}", True, COLOR_GREEN)
        lives_text_rect = lives_text.get_rect()
        surface.blit(lives_text, (SCREEN_WIDTH - lives_text_rect.width - 10, 15))


class GameOverScreen:
    """游戏结束画面"""

    def __init__(self, victory=False):
        self.victory = victory
        self.font_title = pygame.font.SysFont(None, FONT_SIZE_HUGE)
        self.font_normal = pygame.font.SysFont(None, FONT_SIZE_NORMAL)

        button_width = 200
        button_height = 50
        start_x = (SCREEN_WIDTH - button_width) // 2

        self.buttons = {
            'restart': Button(start_x, 350, button_width, button_height, "重新开始"),
            'menu': Button(start_x, 420, button_width, button_height, "返回菜单"),
            'quit': Button(start_x, 490, button_width, button_height, "退出游戏"),
        }

    def draw(self, surface, score):
        """绘制游戏结束画面"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(200)
        surface.blit(overlay, (0, 0))

        # 标题
        if self.victory:
            title = self.font_title.render("胜利！", True, COLOR_GREEN)
        else:
            title = self.font_title.render("游戏结束", True, COLOR_RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(title, title_rect)

        # 分数
        score_text = self.font_normal.render(f"最终分数: {score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        surface.blit(score_text, score_rect)

        # 按钮
        for button in self.buttons.values():
            button.draw(surface)

    def update(self, mouse_pos, mouse_pressed):
        """更新状态"""
        for key, button in self.buttons.items():
            if button.update(mouse_pos, mouse_pressed):
                return key
        return None


class PauseScreen:
    """暂停画面"""

    def __init__(self):
        self.font_title = pygame.font.SysFont(None, FONT_SIZE_LARGE)
        self.font_normal = pygame.font.SysFont(None, FONT_SIZE_NORMAL)

        button_width = 200
        button_height = 50
        start_x = (SCREEN_WIDTH - button_width) // 2

        self.buttons = {
            'resume': Button(start_x, 250, button_width, button_height, "继续游戏"),
            'restart': Button(start_x, 320, button_width, button_height, "重新开始"),
            'menu': Button(start_x, 390, button_width, button_height, "返回菜单"),
            'quit': Button(start_x, 460, button_width, button_height, "退出游戏"),
        }

    def draw(self, surface):
        """绘制暂停画面"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(180)
        surface.blit(overlay, (0, 0))

        # 标题
        title = self.font_title.render("游戏暂停", True, COLOR_YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 180))
        surface.blit(title, title_rect)

        # 按钮
        for button in self.buttons.values():
            button.draw(surface)

    def update(self, mouse_pos, mouse_pressed):
        """更新状态"""
        for key, button in self.buttons.items():
            if button.update(mouse_pos, mouse_pressed):
                return key
        return None


class LevelSelectScreen:
    """关卡选择界面"""

    def __init__(self, max_level=5):
        self.font_title = pygame.font.SysFont(None, FONT_SIZE_HUGE)
        self.font_normal = pygame.font.SysFont(None, FONT_SIZE_NORMAL)
        self.max_level = max_level
        self.selected_level = 1

        # 创建关卡按钮
        self.level_buttons = []
        button_size = 60
        gap = 20
        levels_per_row = 5
        start_x = (SCREEN_WIDTH - (levels_per_row * (button_size + gap) - gap)) // 2
        start_y = 220

        for i in range(1, max_level + 1):
            row = (i - 1) // levels_per_row
            col = (i - 1) % levels_per_row
            x = start_x + col * (button_size + gap)
            y = start_y + row * (button_size + gap)
            btn = Button(x, y, button_size, button_size, str(i), FONT_SIZE_NORMAL)
            self.level_buttons.append((i, btn))

        # 返回按钮
        self.back_button = Button(
            (SCREEN_WIDTH - 200) // 2, 420, 200, 50, "返回菜单"
        )

    def draw(self, surface):
        """绘制关卡选择界面"""
        # 背景
        surface.fill(COLOR_BLACK)

        # 标题
        title = self.font_title.render("选择关卡", True, COLOR_GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)

        # 说明文字
        info = self.font_normal.render(f"当前选择: 第 {self.selected_level} 关", True, COLOR_YELLOW)
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, 160))
        surface.blit(info, info_rect)

        # 关卡按钮
        for level, btn in self.level_buttons:
            # 高亮当前选中的关卡
            if level == self.selected_level:
                btn.normal_color = COLOR_GREEN
                btn.hover_color = (0, 200, 0)
            else:
                btn.normal_color = COLOR_GRAY
                btn.hover_color = COLOR_GREEN
            btn.draw(surface)

        # 返回按钮
        self.back_button.draw(surface)

    def update(self, mouse_pos, mouse_pressed):
        """更新状态"""
        # 检查关卡按钮
        for level, btn in self.level_buttons:
            if btn.update(mouse_pos, mouse_pressed):
                self.selected_level = level
                return f'level_{level}'

        # 检查返回按钮
        if self.back_button.update(mouse_pos, mouse_pressed):
            return 'back'

        return None

