"""关卡系统 — 从文本文件加载地图和初始状态。

使用经典的 Sokoban 文本格式，增加关卡不需要修改 Python 代码：
    # = Wall（墙）
      = Floor（地板）
    . = Goal（目标）
    $ = Box（箱子）
    @ = Player（玩家）
    * = Box on Goal（箱子在目标上）
    + = Player on Goal（玩家在目标上）
"""

from __future__ import annotations

import os
from pathlib import Path

from .board import Board
from .state import GameState, Position


def _parse_line(line: str) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """解析一行关卡字符串。

    Returns:
        (walls, goals) 集合
    """
    walls: set[tuple[int, int]] = set()
    goals: set[tuple[int, int]] = set()

    for col, ch in enumerate(line.rstrip('\n').rstrip('\r')):
        if ch == '#':
            walls.add((0, col))  # row 暂时用 0，最后统一调整
        elif ch == '.':
            goals.add((0, col))

    return walls, goals


def load_level(filepath: str | Path) -> tuple[Board, GameState]:
    """从文本文件加载一个关卡。

    Args:
        filepath: 关卡文件路径

    Returns:
        (Board, GameState) 元组

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件格式错误
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Level file not found: {path}")

    lines = path.read_text(encoding='utf-8').splitlines()
    # 过滤空行（标准 Sokoban 格式不使用 # 做注释）
    content_lines = [l for l in lines if l.strip()]

    if not content_lines:
        raise ValueError(f"Empty level file: {path}")

    # 第一遍扫描：收集墙、目标、玩家、箱子位置
    walls: set[tuple[int, int]] = set()
    goals: set[tuple[int, int]] = set()
    player_pos: Position | None = None
    box_positions: set[Position] = set()

    for row_idx, line in enumerate(content_lines):
        stripped = line.rstrip('\n').rstrip('\r')
        for col_idx, ch in enumerate(stripped):
            if ch == '#':
                walls.add((row_idx, col_idx))
            elif ch == '.':
                goals.add((row_idx, col_idx))
            elif ch == '$':
                box_positions.add(Position(row_idx, col_idx))
            elif ch == '@':
                player_pos = Position(row_idx, col_idx)
            elif ch == '*':  # 箱子在目标上
                box_positions.add(Position(row_idx, col_idx))
                goals.add((row_idx, col_idx))
            elif ch == '+':  # 玩家在目标上
                player_pos = Position(row_idx, col_idx)
                goals.add((row_idx, col_idx))

    if player_pos is None:
        raise ValueError(f"No player position found in level: {path}")

    board = Board(walls=walls, goals=goals)
    state = GameState(
        player=player_pos,
        boxes=frozenset(box_positions),
        moves=0,
        pushes=0,
    )

    return board, state


def find_level_files(directory: str = "levels") -> list[str]:
    """在指定目录中找到所有关卡文件。

    Returns:
        按数字排序的文件名字符串列表，例如 ["level_01.txt", "level_02.txt", ...]
    """
    level_dir = Path(__file__).parent.parent / directory
    if not level_dir.exists():
        return []

    files = [f.name for f in level_dir.iterdir() if f.suffix == '.txt']
    files.sort(key=lambda f: int(f.split('_')[1].split('.')[0]))
    return files


def get_level_path(level_name: str) -> Path:
    """获取关卡文件的完整路径。"""
    return Path(__file__).parent.parent / "levels" / level_name
