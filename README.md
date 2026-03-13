# 坦克大战 (Tank Battle)

一款使用 Python 和 Pygame 开发的经典坦克大战游戏，致敬红白机时代的经典游戏。

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 游戏特点

- 🎮 经典复古的游戏体验
- 🎯 精美细腻的游戏画面
- 🏆 多个关卡挑战
- 👾 多种敌人类型（普通、快速、重型、超级坦克）
- 🎨 简体中文界面
- 💾 完整的日志系统
- 🖥️ 跨平台支持 (Windows/Linux/macOS)

## 操作说明

### 玩家1控制

| 按键 | 功能 |
|------|------|
| W | 向上移动 |
| S | 向下移动 |
| A | 向左移动 |
| D | 向右移动 |
| 空格键 | 发射炮弹 |

### 其他按键

| 按键 | 功能 |
|------|------|
| ESC | 暂停/继续游戏 |

## 游戏元素

- **砖块 (🧱)**: 可以破坏的障碍物
- **钢铁 (🛡️)**: 不可破坏的障碍物
- **水 (💧)**: 坦克无法通过
- **草地 (🌿)**: 坦克可以隐藏在下面
- **基地 (🏠)**: 玩家的基地，需要保护

## 安装要求

- Python 3.10 或更高版本
- Pygame 2.5.0 或更高版本

## 快速开始

### 从源码运行

1. 克隆仓库
```bash
git clone git@github.com:ganecheng-ai/tank-battle-k25.git
cd tank-battle-k25
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行游戏
```bash
cd src
python main.py
```

### 下载预编译版本

从 [Releases](https://github.com/ganecheng-ai/tank-battle-k25/releases) 页面下载对应平台的版本。

## 项目结构

```
tank-battle-k25/
├── assets/                 # 游戏资源
│   ├── images/            # 图片资源
│   ├── sounds/            # 音效资源
│   └── fonts/             # 字体文件
├── src/                   # 源代码
│   ├── main.py           # 游戏入口
│   ├── game.py           # 游戏主逻辑
│   ├── tank.py           # 坦克类
│   ├── bullet.py         # 子弹类
│   ├── map.py            # 地图类
│   ├── enemy.py          # 敌人类
│   ├── ui.py             # 界面模块
│   ├── config.py         # 配置文件
│   └── logger.py         # 日志模块
├── tests/                 # 测试代码
├── .github/workflows/     # GitHub Actions
├── logs/                  # 日志文件
├── requirements.txt       # 依赖文件
├── plan.md               # 开发计划
└── README.md             # 本文件
```

## 开发计划

详见 [plan.md](plan.md) 文件

## 技术栈

- **编程语言**: Python 3.10+
- **游戏框架**: Pygame 2.5+
- **构建工具**: PyInstaller
- **日志系统**: Python logging模块

## 版本历史

### v0.1.0 (当前版本)
- 初始化项目结构
- 实现基础游戏功能
- 实现日志系统
- 配置GitHub Actions自动构建

## 贡献指南

欢迎提交 Issue 和 Pull Request。

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过 GitHub Issue 联系我们。

---

**享受游戏乐趣！** 🎮
