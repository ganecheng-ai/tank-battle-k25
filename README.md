# 坦克大战 (Tank Battle)

一款使用 Python 和 Pygame 开发的经典坦克大战游戏，致敬红白机时代的经典游戏。

![Version](https://img.shields.io/badge/version-0.4.0-blue.svg)
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
- ⚡ 丰富的道具系统（加生命、加速、穿甲弹、护盾、全屏炸弹）
- 💥 炫酷的爆炸特效和粒子效果
- 🔊 音效和背景音乐支持
- 🛡️ 护盾保护机制

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

### 地图元素
- **砖块 (🧱)**: 可以破坏的障碍物
- **钢铁 (🛡️)**: 不可破坏的障碍物
- **水 (💧)**: 坦克无法通过
- **草地 (🌿)**: 坦克可以隐藏在下面
- **基地 (🏠)**: 玩家的基地，需要保护

### 道具系统
游戏中有5种道具，击败敌人后有概率掉落：

| 道具 | 图标 | 效果 |
|------|------|------|
| 生命+ | 🔴 | 增加1点生命值 |
| 加速 | 🔵 | 移动速度提升50%，持续5秒 |
| 穿甲 | 🟠 | 子弹威力翻倍，持续10秒 |
| 护盾 | 🟡 | 抵挡一次伤害，持续8秒 |
| 炸弹 | 🟢 | 立即消灭所有敌人 |

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
│   ├── tank.py           # 坦克类
│   ├── bullet.py         # 子弹类
│   ├── map.py            # 地图类
│   ├── powerup.py        # 道具系统
│   ├── particles.py      # 粒子效果
│   ├── sounds.py         # 音效系统
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

### v0.4.0 (当前版本)
- 实现道具系统，包含5种道具（加生命、加速、穿甲弹、护盾、全屏炸弹）
- 添加爆炸特效和粒子效果系统
- 实现音效和背景音乐支持框架
- 添加坦克移动轨迹效果
- 实现护盾保护和穿甲弹机制
- 击败敌人有概率掉落道具
- 更新版本号到v0.4.0
- 完善测试覆盖

### v0.3.0
- 实现关卡选择界面，支持5个不同关卡
- 添加5种不同布局的关卡地图
- 实现多关卡游戏流程
- 修复子弹碰撞检测逻辑
- 优化代码质量和测试覆盖

### v0.2.0
- 实现地图系统（砖块、钢铁、水、草地、基地）
- 实现玩家坦克（移动、射击、生命值系统）
- 实现子弹系统和碰撞检测
- 实现4种敌人类型（普通、快速、重型、超级坦克）和AI
- 修复代码问题，完善测试套件

### v0.1.0
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
