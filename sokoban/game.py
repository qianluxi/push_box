"""游戏控制器 — 协调 Action、Rules 和 GameState。

Game 很薄，不负责具体规则，只做：
- 接收 Action → 调用 Rules
- 管理历史记录（Undo）
- 关卡切换与重置
- 检查胜利状态
"""

from __future__ import annotations

import copy

from .actions import Action
from .board import Board
from .level import load_level
from .rules import move
from .state import GameState


class Game:
    """推箱子游戏控制器。

    Attributes:
        board:     当前关卡的静态地图
        state:     当前动态游戏状态
        history:   历史状态栈（用于 Undo），不包含初始状态
        current_level: 当前关卡文件名
    """

    def __init__(self) -> None:
        self.board: Board | None = None
        self.state: GameState | None = None
        self.history: list[GameState] = []
        self.current_level: str = ""
        self.won: bool = False
        self.level_files: list[str] = []

    def load_level(self, level_name: str) -> None:
        """加载一个关卡并初始化游戏状态。

        Args:
            level_name: 可以是文件名（如 "level_01.txt"）或相对路径
        """
        board, state = load_level(level_name)
        self.board = board
        self.state = state
        self.history = []
        self.current_level = level_name
        self.won = False

    def set_level_files(self, files: list[str]) -> None:
        """设置可用的关卡列表。"""
        self.level_files = files

    # ---- 动作分发 ----

    def handle(self, action: Action) -> None:
        """处理玩家输入的动作。

        Args:
            action: 来自键盘/鼠标/AI的动作枚举
        """
        if self.won:
            if action == Action.RESET:
                self.reset()
            return

        if action in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
            self._move(action)
        elif action == Action.UNDO:
            self.undo()
        elif action == Action.RESET:
            self.reset()
        elif action == Action.NEXT_LEVEL:
            self._next_level()
        elif action == Action.PREV_LEVEL:
            self._prev_level()

    # ---- 移动逻辑 ----

    _DIRECTION_MAP = {
        Action.UP: (-1, 0),
        Action.DOWN: (1, 0),
        Action.LEFT: (0, -1),
        Action.RIGHT: (0, 1),
    }

    def _move(self, action: Action) -> None:
        """执行一次移动（带历史记录保存）。"""
        if self.board is None or self.state is None:
            return

        direction = self._DIRECTION_MAP[action]
        result = move(self.board, self.state, direction)

        if result.new_state != self.state:  # 实际发生了移动
            self.history.append(copy.copy(self.state))
            self.state = result.new_state
            self.won = result.won

    # ---- 撤回 / 重置 ----

    def undo(self) -> None:
        """撤回上一步操作。"""
        if not self.history:
            return
        self.state = self.history.pop()
        self.won = False

    def reset(self) -> None:
        """重置当前关卡到初始状态。"""
        if self.current_level:
            self.load_level(self.current_level)

    # ---- 关卡切换 ----

    def _next_level(self) -> None:
        """进入下一关。"""
        if not self.level_files:
            return
        try:
            idx = self.level_files.index(self.current_level)
        except ValueError:
            idx = -1
        if idx < len(self.level_files) - 1:
            self.load_level(self.level_files[idx + 1])

    def _prev_level(self) -> None:
        """返回上一关。"""
        if not self.level_files:
            return
        try:
            idx = self.level_files.index(self.current_level)
        except ValueError:
            idx = 0
        if idx > 0:
            self.load_level(self.level_files[idx - 1])
