"""
音效模块 - 游戏中的音效和背景音乐
"""
import pygame
import os
import logging

logger = logging.getLogger("tank_battle")


class SoundManager:
    """音效管理器"""

    # 音量设置
    DEFAULT_VOLUME = 0.5
    DEFAULT_MUSIC_VOLUME = 0.3

    # 音效文件列表
    SOUND_FILES = {
        'shoot': 'shoot.wav',
        'explosion': 'explosion.wav',
        'hit': 'hit.wav',
        'powerup': 'powerup.wav',
        'tank_move': 'tank_move.wav',
        'game_start': 'game_start.wav',
        'game_over': 'game_over.wav',
        'victory': 'victory.wav',
        'shield_hit': 'shield_hit.wav',
        'menu_click': 'menu_click.wav',
    }

    def __init__(self, assets_path='assets/sounds'):
        self.assets_path = assets_path
        self.sounds = {}
        self.music_path = None
        self.enabled = True
        self.sound_volume = self.DEFAULT_VOLUME
        self.music_volume = self.DEFAULT_MUSIC_VOLUME
        self.mixer_initialized = False

        # 初始化音频系统
        self._init_audio()

    def _init_audio(self):
        """初始化音频系统"""
        try:
            # 初始化 mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_initialized = True

            # 设置音量
            pygame.mixer.set_num_channels(16)  # 设置声道数

            # 加载音效
            self._load_sounds()

            logger.info("音频系统初始化成功")
        except Exception as e:
            logger.warning(f"音频系统初始化失败: {e}")
            self.enabled = False

    def _load_sounds(self):
        """加载音效文件"""
        if not self.mixer_initialized:
            return

        # 确保音效目录存在
        sound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.assets_path)

        for sound_name, filename in self.SOUND_FILES.items():
            filepath = os.path.join(sound_dir, filename)
            if os.path.exists(filepath):
                try:
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sound_volume)
                    self.sounds[sound_name] = sound
                    logger.debug(f"加载音效: {sound_name}")
                except Exception as e:
                    logger.warning(f"加载音效失败 {filename}: {e}")
            else:
                logger.debug(f"音效文件不存在: {filepath}")

    def play(self, sound_name):
        """播放音效"""
        if not self.enabled or not self.mixer_initialized:
            return False

        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                return True
            except Exception as e:
                logger.warning(f"播放音效失败 {sound_name}: {e}")
        return False

    def play_shoot(self):
        """播放射击音效"""
        return self.play('shoot')

    def play_explosion(self):
        """播放爆炸音效"""
        return self.play('explosion')

    def play_hit(self):
        """播放命中音效"""
        return self.play('hit')

    def play_powerup(self):
        """播放道具拾取音效"""
        return self.play('powerup')

    def play_shield_hit(self):
        """播放护盾被击中音效"""
        return self.play('shield_hit')

    def play_game_start(self):
        """播放游戏开始音效"""
        return self.play('game_start')

    def play_game_over(self):
        """播放游戏结束音效"""
        return self.play('game_over')

    def play_victory(self):
        """播放胜利音效"""
        return self.play('victory')

    def play_menu_click(self):
        """播放菜单点击音效"""
        return self.play('menu_click')

    def set_volume(self, volume):
        """设置音效音量 (0.0 - 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        if self.mixer_initialized:
            for sound in self.sounds.values():
                sound.set_volume(self.sound_volume)

    def set_music_volume(self, volume):
        """设置音乐音量 (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.mixer_initialized and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume)

    def toggle_sound(self):
        """切换音效开关"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_all()
        return self.enabled

    def stop_all(self):
        """停止所有音效"""
        if self.mixer_initialized:
            pygame.mixer.stop()

    def pause_all(self):
        """暂停所有音效"""
        if self.mixer_initialized:
            pygame.mixer.pause()

    def resume_all(self):
        """恢复所有音效"""
        if self.mixer_initialized:
            pygame.mixer.unpause()


class MusicManager:
    """背景音乐管理器"""

    def __init__(self, assets_path='assets/music'):
        self.assets_path = assets_path
        self.enabled = True
        self.volume = 0.3
        self.current_track = None
        self.mixer_initialized = False

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_initialized = True
        except:
            pass

    def play(self, track_name, loops=-1):
        """播放背景音乐"""
        if not self.enabled or not self.mixer_initialized:
            return False

        music_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.assets_path)
        filepath = os.path.join(music_dir, track_name)

        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(loops)
                self.current_track = track_name
                logger.info(f"播放背景音乐: {track_name}")
                return True
            except Exception as e:
                logger.warning(f"播放背景音乐失败 {track_name}: {e}")
        else:
            logger.debug(f"背景音乐文件不存在: {filepath}")
        return False

    def play_menu_music(self):
        """播放菜单背景音乐"""
        return self.play('menu.mp3') or self.play('menu.ogg') or self.play('menu.wav')

    def play_game_music(self):
        """播放游戏背景音乐"""
        return self.play('game.mp3') or self.play('game.ogg') or self.play('game.wav')

    def stop(self):
        """停止背景音乐"""
        if self.mixer_initialized:
            pygame.mixer.music.stop()
            self.current_track = None

    def pause(self):
        """暂停背景音乐"""
        if self.mixer_initialized:
            pygame.mixer.music.pause()

    def resume(self):
        """恢复背景音乐"""
        if self.mixer_initialized:
            pygame.mixer.music.unpause()

    def set_volume(self, volume):
        """设置音量 (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.mixer_initialized:
            pygame.mixer.music.set_volume(self.volume)

    def fadeout(self, time_ms=500):
        """淡出音乐"""
        if self.mixer_initialized:
            pygame.mixer.music.fadeout(time_ms)


def create_placeholder_sounds():
    """创建占位音效文件（空文件，用于测试）"""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    sounds_dir = os.path.join(assets_dir, 'sounds')
    music_dir = os.path.join(assets_dir, 'music')

    # 创建目录
    os.makedirs(sounds_dir, exist_ok=True)
    os.makedirs(music_dir, exist_ok=True)

    logger.info(f"音效目录: {sounds_dir}")
    logger.info(f"音乐目录: {music_dir}")

    return sounds_dir, music_dir
