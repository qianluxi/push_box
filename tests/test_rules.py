"""测试 rules.py：移动规则、胜利判断、MoveType。"""

import sys
sys.path.insert(0, "..")

from sokoban.board import Board
from sokoban.state import GameState, Position
from sokoban.rules import move, is_solved, MoveType


def _b(walls, goals, width=None, height=None):
    """创建 Board，显式设置宽高避免自动推断问题。"""
    if width is None or height is None:
        all_cells = walls | goals
        if all_cells:
            h = max(r for r, _ in all_cells) + 1
            w = max(c for _, c in all_cells) + 1
        else:
            h, w = 0, 0
        return Board(walls=walls, goals=goals, width=w, height=h)
    return Board(walls=walls, goals=goals, width=width, height=height)


def _s(player, boxes, moves=0, pushes=0):
    return GameState(player=player, boxes=frozenset(boxes), moves=moves, pushes=pushes)


# --- Walk ---
def test_walk_floor():
    # 3x2 board: row0 all floor, row1 all wall
    board = _b({(1,0),(1,1),(1,2)}, set(), width=3, height=2)
    s = _s(Position(0, 0), [])
    r = move(board, s, (0, 1))
    assert r.move_type == MoveType.WALK
    assert r.new_state.player == Position(0, 1)
    # No boxes + no goals = not solvable per our rule requiring count match
    # With 0 boxes and 0 goals → len equal → wins
    # Just verify it moved correctly
    assert r.new_state.moves == 1


def test_walk_to_goal():
    goal = {(0, 1)}
    board = _b({(1,0),(1,1),(1,2)}, goal, width=3, height=2)
    s = _s(Position(0, 0), [])
    r = move(board, s, (0, 1))
    assert r.move_type == MoveType.WALK
    assert r.new_state.player == Position(0, 1)


# --- Blocked ---
def test_blocked_wall():
    board = _b({(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)}, set())
    s = _s(Position(0, 0), [])
    r = move(board, s, (0, 1))
    assert r.move_type == MoveType.BLOCKED
    assert r.new_state == s


def test_blocked_out_of_bounds():
    board = _b(set(), set(), width=2, height=2)
    s = _s(Position(0, 0), [])
    r = move(board, s, (-1, 0))
    assert r.move_type == MoveType.BLOCKED


def test_box_into_wall():
    board = _b({(0,0),(0,1),(0,2),(0,3),(1,0),(1,3),(2,0),(2,1),(2,2),(2,3)}, set())
    s = _s(Position(2, 0), [Position(2, 1)])
    r = move(board, s, (0, 1))
    assert r.move_type == MoveType.BLOCKED


def test_box_into_box():
    board = _b({(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)}, set())
    s = _s(Position(2, 0), [Position(2, 1), Position(2, 2)])
    r = move(board, s, (0, 1))
    assert r.move_type == MoveType.BLOCKED


# --- Push ---
def test_push_floor():
    # 4-wide corridor: player(box)floor(floor)
    # Row 1: all floor
    # Row 0: walls at edges
    board = _b({(0,0),(0,3),(1,0),(1,3)}, set(), width=4, height=2)
    s = _s(Position(1, 0), [Position(1, 1)])
    r = move(board, s, (0, 1))
    assert r.move_type == MoveType.PUSH
    assert r.new_state.player == Position(1, 1)
    assert Position(1, 2) in r.new_state.boxes


def test_push_to_goal_solves():
    goal = {(0, 1)}
    # Row 0: wall goal wall
    # Row 1: all floor
    # Row 2: all floor
    board = _b({(0,0),(0,2)}, goal, width=3, height=3)
    s = _s(Position(2, 1), [Position(1, 1)])
    r = move(board, s, (-1, 0))
    assert r.move_type == MoveType.PUSH
    assert r.new_state.player == Position(1, 1)
    assert Position(0, 1) in r.new_state.boxes
    assert r.won is True


# --- Victory ---
def test_empty_boxes_not_solved():
    goals = {(0,0),(1,0),(2,0)}
    board = _b({(0,0),(0,1),(1,0),(1,1),(2,0),(2,1)}, goals)
    s = _s(Position(0, 1), frozenset())
    assert not is_solved(board, s)


def test_all_on_goals_solved():
    goals = {(0,0),(1,0)}
    board = _b(set(), goals, width=2, height=2)
    s = _s(Position(0, 1), [Position(0, 0), Position(1, 0)])
    assert is_solved(board, s)


def test_partial_not_solved():
    goals = {(0,0),(1,0)}
    board = _b(set(), goals, width=2, height=2)
    s = _s(Position(0, 1), [Position(0, 0), Position(1, 1)])
    assert not is_solved(board, s)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
