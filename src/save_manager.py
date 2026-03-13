"""
存档管理模块 - 游戏存档/读档功能
"""
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger("tank_battle")


class SaveManager:
    """存档管理器"""

    SAVE_DIR = "saves"
    MAX_SLOTS = 5  # 最大存档槽位数

    def __init__(self):
        """初始化存档管理器"""
        self.save_dir = self._get_save_dir()
        self._ensure_save_dir()

    def _get_save_dir(self):
        """获取存档目录路径"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, self.SAVE_DIR)

    def _ensure_save_dir(self):
        """确保存档目录存在"""
        os.makedirs(self.save_dir, exist_ok=True)

    def _get_save_path(self, slot):
        """获取存档文件路径"""
        return os.path.join(self.save_dir, f"save_slot_{slot}.json")

    def save_game(self, slot, game_state):
        """
        保存游戏

        Args:
            slot: 存档槽位 (1-MAX_SLOTS)
            game_state: 游戏状态字典

        Returns:
            bool: 是否保存成功
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            logger.error(f"无效的存档槽位: {slot}")
            return False

        try:
            save_data = {
                "version": "1.0.0",
                "save_time": datetime.now().isoformat(),
                "slot": slot,
                "game_state": game_state
            }

            save_path = self._get_save_path(slot)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            logger.info(f"游戏已保存到槽位 {slot}")
            return True

        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
            return False

    def load_game(self, slot):
        """
        读取游戏

        Args:
            slot: 存档槽位 (1-MAX_SLOTS)

        Returns:
            dict or None: 游戏状态字典，失败返回None
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            logger.error(f"无效的存档槽位: {slot}")
            return None

        save_path = self._get_save_path(slot)

        if not os.path.exists(save_path):
            logger.warning(f"存档槽位 {slot} 不存在")
            return None

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            logger.info(f"游戏已从槽位 {slot} 加载")
            return save_data.get("game_state", None)

        except Exception as e:
            logger.error(f"加载游戏失败: {e}")
            return None

    def delete_save(self, slot):
        """
        删除存档

        Args:
            slot: 存档槽位 (1-MAX_SLOTS)

        Returns:
            bool: 是否删除成功
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            logger.error(f"无效的存档槽位: {slot}")
            return False

        save_path = self._get_save_path(slot)

        if not os.path.exists(save_path):
            logger.warning(f"存档槽位 {slot} 不存在，无需删除")
            return True

        try:
            os.remove(save_path)
            logger.info(f"存档槽位 {slot} 已删除")
            return True

        except Exception as e:
            logger.error(f"删除存档失败: {e}")
            return False

    def get_save_info(self, slot):
        """
        获取存档信息

        Args:
            slot: 存档槽位 (1-MAX_SLOTS)

        Returns:
            dict or None: 存档信息，不存在返回None
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            return None

        save_path = self._get_save_path(slot)

        if not os.path.exists(save_path):
            return None

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            return {
                "slot": slot,
                "save_time": save_data.get("save_time", "未知"),
                "level": save_data.get("game_state", {}).get("level", 1),
                "score": save_data.get("game_state", {}).get("score", 0),
                "exists": True
            }

        except Exception as e:
            logger.error(f"读取存档信息失败: {e}")
            return None

    def get_all_saves(self):
        """
        获取所有存档信息

        Returns:
            list: 所有存档信息列表
        """
        saves = []
        for slot in range(1, self.MAX_SLOTS + 1):
            info = self.get_save_info(slot)
            if info:
                saves.append(info)
            else:
                saves.append({
                    "slot": slot,
                    "exists": False,
                    "save_time": None,
                    "level": None,
                    "score": None
                })
        return saves

    def has_save(self, slot):
        """
        检查存档是否存在

        Args:
            slot: 存档槽位 (1-MAX_SLOTS)

        Returns:
            bool: 存档是否存在
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            return False
        return os.path.exists(self._get_save_path(slot))

    def get_save_count(self):
        """
        获取存档数量

        Returns:
            int: 存档数量
        """
        count = 0
        for slot in range(1, self.MAX_SLOTS + 1):
            if self.has_save(slot):
                count += 1
        return count

    def auto_save(self, game_state):
        """
        自动存档（使用槽位1作为自动存档）

        Args:
            game_state: 游戏状态字典

        Returns:
            bool: 是否保存成功
        """
        return self.save_game(1, game_state)

    def load_auto_save(self):
        """
        读取自动存档

        Returns:
            dict or None: 游戏状态字典，失败返回None
        """
        return self.load_game(1)
