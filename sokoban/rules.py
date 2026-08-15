"""推箱子游戏规则。

规则层完全不依赖 Pygame，可以被：
- Game 控制器调用
- AI Solver 调用
- 自动化测试调用
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from .board import Board
from .state import GameState, Position


class MoveType(Enum):
    """移动类型枚举，供 UI/音效/Solver 区分操作结果。"""
    BLOCKED = auto()  # 撞到墙或边界，未移动
    WALK = auto()     # 普通走步
    PUSH = auto()     # 推箱子


@dataclass
class MoveResult:
    """一次移动操作的结果。"""
    new_state: GameState
    move_type: MoveType
    won: bool


def is_solved(board: Board, state: GameState) -> bool:
    """检查当前状态是否完成。

    V1.1 修复：空箱子的关卡不再被误判为胜利（all([])==True）。
    要求箱子数量 == 目标数量，且所有箱子都在目标上。
    """
    if len(state.boxes) != len(board.goals):
        return False
    return all(board.is_goal_position(box.row, box.col) for box in state.boxes)


def move(board: Board, state: GameState, direction: tuple[int, int]) -> MoveResult:
    """根据方向和当前状态计算移动结果。

    规则逻辑：
        玩家前方是空地 → 玩家移动 (WALK)
        玩家前方是墙/越界   → 不允许 (BLOCKED)
        玩家前方是箱子 → 继续检查箱子后面
            箱子后是墙/箱子/越界 → 不允许 (BLOCKED)
            箱子后是地板/目标 → 推箱子 (PUSH)

    Args:
        board: 静态地图
        state: 当前游戏状态
        direction: (row_delta, col_delta)，例如 (-1, 0) 表示向上

    Returns:
        MoveResult，包含新的 GameState、移动类型、胜利信息
    """
    dr, dc = direction
    player = state.player

    # 玩家新位置
    new_player_pos = Position(player.row + dr, player.col + dc)

    # 使用统一的 is_blocked 接口（含越界 + 墙的完整判断）
    if board.is_blocked(new_player_pos):
        return MoveResult(
            new_state=state, move_type=MoveType.BLOCKED, won=False
        )

    # 玩家新位置有箱子
    if new_player_pos in state.boxes:
        # 箱子新位置
        box_new_pos = Position(new_player_pos.row + dr, new_player_pos.col + dc)

        # 箱子后方不能是墙、其他箱子或越界
        if board.is_blocked(box_new_pos):
            return MoveResult(
                new_state=state, move_type=MoveType.BLOCKED, won=False
            )
        if box_new_pos in state.boxes:
            return MoveResult(
                new_state=state, move_type=MoveType.BLOCKED, won=False
            )

        # 推箱子成功
        new_boxes = state.boxes - {new_player_pos} | {box_new_pos}
        new_state = GameState(
            player=new_player_pos,
            boxes=new_boxes,
            moves=state.moves + 1,
            pushes=state.pushes + 1,
        )
        won = is_solved(board, new_state)
        return MoveResult(
            new_state=new_state, move_type=MoveType.PUSH, won=won
        )

    # 前方是空位/目标 → 玩家正常移动
    new_state = GameState(
        player=new_player_pos,
        boxes=state.boxes,
        moves=state.moves + 1,
        pushes=state.pushes,
    )
    won = is_solved(board, new_state)
    return MoveResult(
        new_state=new_state, move_type=MoveType.WALK, won=won
    )
