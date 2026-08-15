"""测试 board.py：空间查询接口。"""

import sys
sys.path.insert(0, "..")

from sokoban.board import Board
from sokoban.state import Position


def _b(walls, goals, width=None, height=None):
    all_cells = walls | goals
    if width is None or height is None:
        if all_cells:
            h = max(r for r, _ in all_cells) + 1
            w = max(c for _, c in all_cells) + 1
        else:
            h = w = 0
    else:
        w = width
        h = height
    return Board(walls=walls, goals=goals, width=w, height=h)


# --- Bounds ---
def test_in_bounds_true():
    b = _b({(0,0),(0,1),(1,0),(1,1)}, set(), width=2, height=2)
    assert b.in_bounds(0, 0)
    assert b.in_bounds(1, 1)
    assert not b.in_bounds(-1, 0)
    assert not b.in_bounds(2, 0)


def test_empty_board_out_of_bounds():
    b = _b(set(), set())
    assert not b.in_bounds(0, 0)


# --- Walkable / Blocked ---
def test_walkable_floor_inner():
    b = _b({(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)}, set(), width=3, height=3)
    assert b.is_walkable(Position(1, 1))
    assert not b.is_blocked(Position(1, 1))


def test_blocked_wall():
    b = _b({(0,0)}, set())
    p = Position(0, 0)
    assert not b.is_walkable(p)
    assert b.is_blocked(p)


def test_blocked_oob_row():
    b = _b(set(), set(), width=5, height=5)
    assert b.is_blocked(Position(-1, 0))
    assert b.is_blocked(Position(5, 0))


def test_blocked_oob_col():
    b = _b(set(), set(), width=5, height=5)
    assert b.is_blocked(Position(0, -1))
    assert b.is_blocked(Position(0, 5))


def test_goal_is_walkable():
    b = _b(set(), {(1,1)}, width=3, height=3)
    assert b.is_walkable(Position(1, 1))
    assert not b.is_blocked(Position(1, 1))


# --- Dimensions ---
def test_explicit_dimensions():
    b = _b(set(), set(), width=10, height=5)
    assert b.width == 10
    assert b.height == 5


def test_auto_from_walls():
    walls = {(0,0),(0,2),(1,0),(1,2)}
    b = _b(walls, set())
    assert b.width == 3
    assert b.height == 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
