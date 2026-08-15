"""移动结果 — 每次移动的详细信息。

不要让 move() 到处修改全局状态，而是返回一个明确的结果对象，
包含 moved / pushed / won 三个字段。这样非常适合后续的：
- 音效（走步 vs 推箱）
- 动画（玩家移动 vs 同步推拉）
- 统计与 UI 反馈
"""

from __future__ import annotations

from dataclasses import dataclass

from .state import GameState, Position


@dataclass
class MoveResult:
    """一次移动操作的结果。"""
    new_state: GameState
    moved: bool = False     # 玩家是否发生了位置变化
    pushed: bool = False    # 是否推了箱子
    won: bool = False       # 本轮是否胜利


def _is_goal(board: "Board", state: GameState) -> bool:
    """检查所有箱子是否都在目标位置上。"""
    return all(board.is_goal_position(box.row, box.col) for box in state.boxes)


def move(board: Board, state: GameState, direction: tuple[int, int]) -> MoveResult:
    """根据方向和当前状态计算移动结果。

    规则逻辑：
        玩家前方是空地 → 玩家移动
        玩家前方是墙   → 不允许
        玩家前方是箱子 → 继续检查箱子后面
            箱子后是墙/箱子 → 不允许
            箱子后是地板/目标 → 推箱子

    Args:
        board: 静态地图
        state: 当前游戏状态
        direction: (row_delta, col_delta)，例如 (-1, 0) 表示向上

    Returns:
        MoveResult，包含新的 GameState 和动作类型信息
    """
    dr, dc = direction
    player = state.player

    # 玩家新位置
    new_player_row = player.row + dr
    new_player_col = player.col + dc
    new_player_pos = Position(new_player_row, new_player_col)

    # 前方是墙或出界 → 不能移动
    if board.contains_wall(new_player_pos.row, new_player_pos.col):
        return MoveResult(new_state=state, moved=False, pushed=False, won=False)

    # 玩家新位置有箱子（现在都是 Position 对象，in 比较正确工作）
    if new_player_pos in state.boxes:
        # 箱子新位置
        box_new_pos = Position(new_player_row + dr, new_player_col + dc)

        # 箱子后方不能是墙或其他箱子
        if board.contains_wall(box_new_pos.row, box_new_pos.col):
            return MoveResult(new_state=state, moved=False, pushed=False, won=False)

        if box_new_pos in state.boxes:
            return MoveResult(new_state=state, moved=False, pushed=False, won=False)

        # 推箱子成功
        new_boxes = state.boxes - {new_player_pos} | {box_new_pos}
        won = _is_goal(board, GameState(player=new_player_pos, boxes=new_boxes))
        new_state = GameState(
            player=new_player_pos,
            boxes=new_boxes,
            moves=state.moves + 1,
            pushes=state.pushes + 1,
        )
        return MoveResult(new_state=new_state, moved=True, pushed=True, won=won)

    # 前方是空位/目标 → 玩家正常移动
    won = _is_goal(board, GameState(player=new_player_pos, boxes=state.boxes))
    new_state = GameState(
        player=new_player_pos,
        boxes=state.boxes,
        moves=state.moves + 1,
        pushes=state.pushes,
    )
    return MoveResult(new_state=new_state, moved=True, pushed=False, won=won)
