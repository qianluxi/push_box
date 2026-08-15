"""测试 game.py：游戏控制器、Undo、关卡切换。"""

import sys
sys.path.insert(0, "..")

from sokoban.actions import Action
from sokoban.game import Game


class TestGameMovement:
    def setup_method(self):
        self.game = Game()
        # load_level uses get_level_path which prepends "levels/"
        # so pass bare filenames
        self.game.set_level_files(["level_01.txt", "level_02.txt"])

    def test_load_level(self):
        self.game.load_level("level_01.txt", ["level_01.txt"])
        assert self.game.board is not None
        assert self.game.state is not None
        assert self.game.won is False

    def test_move_and_push(self):
        self.game.load_level("level_01.txt", ["level_01.txt"])
        initial = self.game.state.player
        self.game.handle(Action.UP)
        assert self.game.state.moves >= 1
        assert self.game.state.player != initial  # player moved

    def test_undo_restores_state(self):
        self.game.load_level("level_01.txt", ["level_01.txt"])
        initial = self.game.state
        self.game.handle(Action.UP)
        self.game.undo()
        assert self.game.state == initial
        assert not self.game.won

    def test_reset_clears_moves(self):
        self.game.load_level("level_01.txt", ["level_01.txt"])
        self.game.handle(Action.UP)
        assert self.game.state.moves > 0
        self.game.reset()
        assert self.game.state.moves == 0
        assert not self.game.won

    def test_won_blocks_further_movement(self):
        self.game.load_level("level_01.txt", ["level_01.txt"])
        self.game.handle(Action.UP)
        assert self.game.won
        old_moves = self.game.state.moves
        self.game.handle(Action.RIGHT)
        self.game.handle(Action.UP)
        assert self.game.state.moves == old_moves  # no more moves after win


class TestLevelNavigation:
    def setup_method(self):
        self.game = Game()

    def test_next_level(self):
        self.game.set_level_files(["level_01.txt", "level_02.txt"])
        self.game.load_level("level_01.txt", ["level_01.txt", "level_02.txt"])
        result = self.game.next_level()
        assert result is True
        assert self.game.current_level == "level_02.txt"

    def test_prev_level(self):
        self.game.set_level_files(["level_01.txt", "level_02.txt"])
        self.game.load_level("level_02.txt", ["level_01.txt", "level_02.txt"])
        result = self.game.prev_level()
        assert result is True
        assert self.game.current_level == "level_01.txt"

    def test_no_copy_needed_in_history(self):
        """GameState immutable frozenset — history stores direct refs."""
        self.game.set_level_files(["level_01.txt"])
        self.game.load_level("level_01.txt", ["level_01.txt"])
        self.game.handle(Action.UP)
        assert len(self.game.history) >= 1
        assert isinstance(self.game.history[0], type(self.game.state))


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
