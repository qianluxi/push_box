"""关卡系统 — 从文本文件加载地图和初始状态。

使用经典的 Sokoban 文本格式，增加关卡不需要修改 Python 代码：
    # = Wall（墙）
      = Floor（地板）
    . = Goal（目标）
    $ = Box（箱子）
    @ = Player（玩家）
    * = Box on Goal（箱子在目标上）
    + = Player on Goal（玩家在目标上）

V1.1 改进：
- 删除未使用的 _parse_line() 函数
- 删除未使用的 import os
- 新增 validate_level() 校验关卡完整性
- 新增未知字符报错
- 统一路径到 get_level_path()
- Board 宽高作为构造参数显式传入
"""

from __future__ import annotations

import re
from pathlib import Path

from .board import Board
from .state import GameState, Position


# ---- 关卡解析常量 ----

WALL_CHARS = ('#',)
GOAL_CHARS = ('.',)
BOX_CHARS = ('$',)
PLAYER_CHARS = ('@',)
COMBINED_CHARS = {'*': 'box_on_goal', '+': 'player_on_goal'}


def load_level(level_name: str) -> tuple[Board, GameState]:
    """从关卡文件加载一个局面。

    Args:
        level_name: 关卡文件名，如 "level_01.txt"
                    路径通过 get_level_path() 自动定位，不依赖 CWD

    Returns:
        (Board, GameState) 元组

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件格式错误（未知字符、校验失败等）
    """
    path = get_level_path(level_name)
    raw_text = path.read_text(encoding='utf-8')

    walls: set[tuple[int, int]] = set()
    goals: set[tuple[int, int]] = set()
    player_pos: Position | None = None
    player_count: int = 0
    box_positions: set[Position] = set()
    row_max = -1
    col_max = -1

    for row_idx, line in enumerate(raw_text.splitlines()):
        stripped = line.rstrip('\r\n')
        if not stripped.strip():  # 跳过空行
            continue

        row_max = max(row_max, row_idx)

        for col_idx, ch in enumerate(stripped):
            col_max = max(col_max, col_idx)

            if ch == '#':
                walls.add((row_idx, col_idx))
            elif ch == '.':
                goals.add((row_idx, col_idx))
            elif ch == '$':
                box_positions.add(Position(row_idx, col_idx))
            elif ch == '@':
                player_count += 1
                if player_count > 1:
                    raise ValueError(
                        f"Multiple player positions found at "
                        f"row={row_idx}, col={col_idx}. "
                        f"A valid level must have exactly one player (@)."
                    )
                player_pos = Position(row_idx, col_idx)
            elif ch == '*':
                box_positions.add(Position(row_idx, col_idx))
                goals.add((row_idx, col_idx))
            elif ch == '+':
                player_count += 1
                if player_count > 1:
                    raise ValueError(
                        f"Multiple player positions found at "
                        f"row={row_idx}, col={col_idx}. "
                        f"A valid level must have exactly one player (+ on goal)."
                    )
                player_pos = Position(row_idx, col_idx)
                goals.add((row_idx, col_idx))
            elif ch == ' ':
                pass  # 空格 = 地板，无需记录
            else:
                raise ValueError(
                    f"Unknown character {ch!r} at "
                    f"row={row_idx}, col={col_idx}"
                )

    # 计算显式宽高
    width = col_max + 1 if col_max >= 0 else 0
    height = row_max + 1 if row_max >= 0 else 0

    if player_pos is None:
        raise ValueError(f"No player position found in level: {path}")

    board = Board(walls=walls, goals=goals, width=width, height=height)
    state = GameState(
        player=player_pos,
        boxes=frozenset(box_positions),
        moves=0,
        pushes=0,
    )

    # ← 调用校验器，防止非法关卡进入游戏
    errors = validate_level(board, state)
    if errors:
        raise ValueError(
            f"Level {path} validation failed ({len(errors)} error(s)):" +
            "".join(f"\n  - {e}" for e in errors)
        )

    return board, state


def validate_level(board: Board, state: GameState) -> list[str]:
    """验证关卡的合法性，返回错误列表（空表示无错误）。

    V1.1 新增：防止加载有问题的关卡导致后续行为异常。
    """
    errors: list[str] = []

    # 1. 必须有且仅有一个玩家（已在 load_level 中保证）

    # 2. 至少有一个箱子
    if len(state.boxes) < 1:
        errors.append("No boxes found (need at least 1)")

    # 3. 箱子数量必须等于目标数量
    if len(state.boxes) != len(board.goals):
        errors.append(
            f"Box count ({len(state.boxes)}) != goal count ({len(board.goals)})"
        )

    # 4. 所有箱子和玩家都在可行区域内
    for box in state.boxes:
        if board.is_blocked(box):
            errors.append(f"Box at {tuple(box)} is on a wall or out of bounds")

    if state.player and board.is_blocked(state.player):
        errors.append(
            f"Player at {tuple(state.player)} is on a wall or out of bounds"
        )

    return errors


def find_level_files(directory: str = "levels") -> list[str]:
    """在指定目录中找到所有关卡文件。

    V1.1 改进：使用正则提取数字排序，不假设固定命名格式。
    支持 level_01.txt、level_2.txt、stage_15.txt 等。
    """
    level_dir = Path(__file__).parent.parent / directory
    if not level_dir.exists():
        return []

    files = [f.name for f in level_dir.iterdir() if f.suffix == '.txt']

    def sort_key(name: str) -> int:
        """按文件中第一个数字排序，找不到则放末尾。"""
        match = re.search(r'(\d+)', name)
        return int(match.group(1)) if match else 999999

    files.sort(key=sort_key)
    return files


def get_level_path(level_name: str) -> Path:
    """获取关卡文件的完整路径。"""
    return Path(__file__).parent.parent / "levels" / level_name
