# -*- coding: utf-8 -*-
"""Sokoban Solver — BFS 最优解求解器 + 死锁检测。

仅作为关卡验证工具使用，不作为游戏功能暴露给玩家。

Solver API：
    solve(board, state) → SolveResult  # 搜索最优解
    count_solutions(board, state, n)  → int  # 统计不同解的数量（最多返回 n 条）

Deadlock detection：
    has_corner_deadlock(position, board) → bool
    has_wall_deadlock(box_pos, goal_pos, board) → bool
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from .board import Board
from .state import GameState, Position


# ================================================================
# 求解结果
# ================================================================

class SolveStatus(Enum):
    SOLVED = auto()
    UNSOLVABLE = auto()
    DEADLOCKED = auto()
    TOO_EXPENSIVE = auto()


@dataclass
class SolveResult:
    """一次求解的结果。"""
    status: SolveStatus
    solved: bool = False
    total_moves: int = 0      # 总移动步数（walk + push）
    total_pushes: int = 0     # 推箱次数
    explored_states: int = 0  # 探索的状态数
    solution_path: list[tuple[str, tuple[int, int]]] = field(default_factory=list)
    # solution_path: [(move_name, direction), ...] 如 [("PUSH", (-1,0)), ("WALK", (0,1))]
    deadlock_details: list[str] = field(default_factory=list)


# ================================================================
# 核心状态表示
# ================================================================

def _state_key(player: Position, boxes: frozenset[Position]) -> tuple[tuple[int, int], tuple[tuple[int, int], ...]]:
    """将 (player, boxes) 序列化为哈希 key。"""
    return ((player.row, player.col), tuple(sorted((b.row, b.col) for b in boxes)))


# ================================================================
# 移动方向
# ================================================================

_DIR_NAMES = {(-1, 0): "UP", (1, 0): "DOWN", (0, -1): "LEFT", (0, 1): "RIGHT"}
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def _apply_move(
    board: Board,
    player: Position,
    boxes: frozenset[Position],
    direction: tuple[int, int],
) -> Optional[tuple[Position, frozenset[Position]]]:
    """应用一次移动，返回新 (player, boxes) 或 None（被阻挡）。"""
    dr, dc = direction
    new_player = Position(player.row + dr, player.col + dc)

    if board.is_blocked(new_player):
        return None

    new_boxes = boxes
    if new_player in boxes:
        box_new = Position(new_player.row + dr, new_player.col + dc)
        if board.is_blocked(box_new) or box_new in boxes:
            return None
        new_boxes = boxes - {new_player} | {box_new}

    return (new_player, new_boxes)


# ================================================================
# 死锁检测
# ================================================================

def _is_corner_deadlock(pos: Position, board: Board, goals: set[tuple[int, int]]) -> bool:
    """检测箱子是否进入非目标角的死锁位置。

    角：上方和左方都是墙/边界，或上方和右方都是墙/边界等。
    如果该角不是目标格，箱子永远无法移出。
    """
    r, c = pos.row, pos.col

    # 四个角落的方向组合
    corner_checks = [
        # 左上角：上+左都被阻挡
        ((-1, 0), (0, -1)),
        # 右上角：上+右都被阻挡
        ((-1, 0), (0, 1)),
        # 左下角：下+左都被阻挡
        ((1, 0), (0, -1)),
        # 右下角：下+右都被阻挡
        ((1, 0), (0, 1)),
    ]

    for d1, d2 in corner_checks:
        blocked_1 = board.in_bounds(r + d1[0], c + d1[1]) and board.contains_wall(r + d1[0], c + d1[1])
        blocked_2 = board.in_bounds(r + d2[0], c + d2[1]) and board.contains_wall(r + d2[0], c + d2[1])
        if blocked_1 and blocked_2:
            # 两个相邻方向都被墙包围 → 这是一个角
            if (r, c) not in goals:
                return True

    return False


def detect_all_deadlocks(board: Board, state: GameState) -> list[str]:
    """扫描当前局面所有箱子的潜在死锁位置（不改变状态）。

    用于关卡设计分析：哪些格子是危险的。
    """
    issues: list[str] = []
    # board.goals 存储的是 frozenset[tuple[int,int]]，不是 Position 对象
    goals_set = {(g[0], g[1]) if isinstance(g, tuple) else (g.row, g.col) for g in board.goals}

    for box in state.boxes:
        b_pos = box if isinstance(box, Position) else Position(box[0], box[1])
        if _is_corner_deadlock(b_pos, board, goals_set):
            issues.append(f"Corner deadlock risk at ({b_pos.row},{b_pos.col})")

    return issues


# ================================================================
# BFS 最优求解器
# ================================================================

def solve(
    board: Board,
    state: GameState,
    max_explored: int = 500_000,
) -> SolveResult:
    """用 BFS 搜索 Sokoban 的最优解（最少移动步数）。

    Args:
        board:       静态地图
        state:       初始游戏状态
        max_explored: 最大探索状态数（防止内存溢出），默认 50 万

    Returns:
        SolveResult，包含解、统计数据或失败原因
    """
    from .rules import is_solved

    if is_solved(board, state):
        return SolveResult(
            status=SolveStatus.SOLVED,
            solved=True,
            total_moves=0,
            total_pushes=0,
            explored_states=0,
            solution_path=[],
        )

    start = _state_key(state.player, state.boxes)
    seen: set = {start}
    # BFS 队列：(player_pos_tuple, box_tuples_tuple, path_list)
    queue: deque = deque([(state.player, state.boxes, [])])
    explored = 0

    while queue and explored < max_explored:
        player, boxes, path = queue.popleft()
        explored += 1

        pr, pc = player.row, player.col
        cur_goals_count = sum(1 for b in boxes if board.is_goal_position(b.row, b.col))

        for dr, dc in DIRS:
            result = _apply_move(board, player, boxes, (dr, dc))
            if result is None:
                continue

            new_player, new_boxes = result
            key = _state_key(new_player, new_boxes)
            if key in seen:
                continue
            seen.add(key)

            # 构造临时 GameState 用于检查胜利
            tmp_state = GameState(
                player=new_player,
                boxes=frozenset(new_boxes),
                moves=state.moves + 1,
                pushes=state.pushes + (1 if new_boxes != boxes else 0),
            )

            move_name = f"PUSH{_DIR_NAMES[(dr, dc)]}" if new_boxes != boxes else f"WALK{_DIR_NAMES[(dr, dc)]}"
            new_path = path + [(move_name, (dr, dc))]

            if is_solved(board, tmp_state):
                return SolveResult(
                    status=SolveStatus.SOLVED,
                    solved=True,
                    total_moves=explored,
                    total_pushes=tmp_state.pushes,
                    explored_states=explored,
                    solution_path=new_path,
                )

            # 启发式：如果当前已将所有箱子放到位，但还没通关
            # （不太可能，因为 is_solved 已经检查过了）
            queue.append((new_player, new_boxes, new_path))

    # 探索完仍未找到解
    deadlock_issues = detect_all_deadlocks(board, state)
    status = SolveStatus.DEADLOCKED if deadlock_issues else SolveStatus.UNSOLVABLE
    return SolveResult(
        status=status,
        solved=False,
        total_moves=explored,
        total_pushes=0,
        explored_states=explored,
        solution_path=[],
        deadlock_details=deadlock_issues,
    )


def count_optimal_solutions(
    board: Board,
    state: GameState,
    max_solutions: int = 5,
    limit_per_solution: int = 100_000,
) -> int:
    """统计最优解数量（用于评估关卡的唯一性约束程度）。

    通过修改 BFS 的终止条件来实现：找到第一个解时记录其长度，
    然后继续探索所有相同长度的解。
    """
    from .rules import is_solved

    if is_solved(board, state):
        return 999  # 已通关

    start = _state_key(state.player, state.boxes)
    seen: set = {start}
    queue: deque = deque([(state.player, state.boxes)])
    explored = 0
    found_count = 0
    best_length = None

    while queue and found_count <= max_solutions:
        player, boxes = queue.popleft()
        explored += 1

        if explored > limit_per_solution:
            break

        for dr, dc in DIRS:
            result = _apply_move(board, player, boxes, (dr, dc))
            if result is None:
                continue

            new_player, new_boxes = result
            key = _state_key(new_player, new_boxes)
            if key in seen:
                continue
            seen.add(key)

            tmp_state = GameState(
                player=new_player,
                boxes=frozenset(new_boxes),
                moves=state.moves + 1,
                pushes=state.pushes + (1 if new_boxes != boxes else 0),
            )

            if is_solved(board, tmp_state):
                current_len = tmp_state.moves
                if best_length is None:
                    best_length = current_len
                    found_count += 1
                elif current_len == best_length:
                    found_count += 1
                continue

            queue.append((new_player, new_boxes))

    return found_count
