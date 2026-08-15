"""游戏状态 — 整个游戏最核心的数据结构。

Position 是不可变的（frozen），因此可以放入 set/frozenset，
也便于将来 AI Solver 做状态哈希和 visited 集合。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """不可变的位置坐标。"""
    row: int
    col: int


@dataclass(frozen=True)
class GameState:
    """当前游戏状态（动态部分）。

    与 Board（静态墙/地板/目标）完全分离。
    """
    player: Position
    boxes: frozenset[Position]
    moves: int = 0
    pushes: int = 0
