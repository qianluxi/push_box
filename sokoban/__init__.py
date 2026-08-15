"""Sokoban — 推箱子游戏核心模块。

架构原则：
- 游戏逻辑层（state / board / rules）完全不依赖 Pygame
- Board（静态地图）与 GameState（动态状态）分离
- 所有操作通过 Action 抽象，由 Game 控制器协调
- 移动返回 MoveResult，而非修改全局状态
"""
