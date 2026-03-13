"""
日志模块 - 提供游戏日志功能
"""
import logging
import os
import sys
from datetime import datetime


def setup_logger(name="tank_battle", log_level=logging.INFO):
    """
    配置并返回日志记录器

    Args:
        name: 日志记录器名称
        log_level: 日志级别

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 生成日志文件名
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 清除现有处理器
    logger.handlers.clear()

    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"日志系统初始化完成，日志文件: {log_file}")
    return logger
