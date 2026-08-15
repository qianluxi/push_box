"""地图（棋盘）— 静态部分。

地图包含：墙、地板、目标位置。
玩家和箱子属于动态状态，存放在 GameState 中。
两者分离是 Sokoban 最关键的架构设计之一。
"""

from __future__ import annotations


class Board:
    """不可变的静态地图。

    Attributes:
        walls:  所有墙格的位置集合
        goals:  所有目标格的位置集合
        floors: 所有可走地板格的位置集合（不含墙）
        width:  地图宽度（列数）
        height: 地图高度（行数）
    """

    def __init__(self, walls: set[tuple[int, int]], goals: set[tuple[int, int]]) -> None:
        self.walls = frozenset(walls)
        self.goals = frozenset(goals)
        # 宽高由墙 + 目标的最大坐标决定（地图边界由这些固定元素定义）
        all_fixed = walls | goals
        if all_fixed:
            self.height = max(r for r, _ in all_fixed) + 1
            self.width = max(c for _, c in all_fixed) + 1
        else:
            self.height = 0
            self.width = 0
        # floor = 所有非墙的格子（仅遍历有效区域）
        self.floors = frozenset(
            (r, c) for r in range(self.height) for c in range(self.width)
            if (r, c) not in self.walls
        )

    @property
    def is_goal(self) -> bool:
        """所有箱子是否都到达目标。由上层根据 GameState + Board 判断。"""
        return False  # 实际判断在 Game 中进行

    def contains_wall(self, row: int, col: int) -> bool:
        return (row, col) in self.walls

    def is_floor(self, row: int, col: int) -> bool:
        return (row, col) in self.floors

    def is_goal_position(self, row: int, col: int) -> bool:
        return (row, col) in self.goals

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width
