"""地图（棋盘）— 静态部分。

地图包含：墙、目标。玩家和箱子属于动态状态，存放在 GameState 中。
两者分离是 Sokoban 最关键的架构设计之一。

V1.1 改进：
- 宽高作为构造参数显式传入，不依赖元素反推
- 新增 is_walkable() / is_blocked() 统一空间查询接口
"""

from __future__ import annotations


class Board:
    """不可变的静态地图。

    Attributes:
        walls:   所有墙格的位置集合
        goals:   所有目标格的位置集合
        width:   地图宽度（列数），显式设定不依赖元素反推
        height:  地图高度（行数），显式设定不依赖元素反推
    """

    def __init__(self, walls: set[tuple[int, int]], goals: set[tuple[int, int]],
                 width: int | None = None, height: int | None = None) -> None:
        self.walls = frozenset(walls)
        self.goals = frozenset(goals)

        # 宽高由元素范围自动推断，或显式传入
        all_cells = walls | goals
        if width is not None and height is not None:
            self.width = width
            self.height = height
        elif all_cells:
            self.height = max(r for r, _ in all_cells) + 1
            self.width = max(c for _, c in all_cells) + 1
        else:
            self.height = 0
            self.width = 0

    def contains_wall(self, row: int, col: int) -> bool:
        return (row, col) in self.walls

    def is_goal_position(self, row: int, col: int) -> bool:
        return (row, col) in self.goals

    def in_bounds(self, row: int, col: int) -> bool:
        """位置是否在地图有效范围内。"""
        return 0 <= row < self.height and 0 <= col < self.width

    def is_walkable(self, pos: "Position") -> bool:
        """判断某位置是否可通行（在界内且不是墙）。"""
        return self.in_bounds(pos.row, pos.col) and not self.contains_wall(
            pos.row, pos.col)

    def is_blocked(self, pos: "Position") -> bool:
        """判断某位置是否阻挡通行（越界或是墙）。"""
        return not self.is_walkable(pos)
