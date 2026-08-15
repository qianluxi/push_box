"""游戏控制器 — 协调 Action、Rules 和 GameState。

Game 很薄，不负责具体规则，只做：
- 接收 Action → 调用 Rules
- 管理历史记录（Undo）
- 关卡切换与重置
- 检查胜利状态

V1.1 改进：
- 删除 copy.copy（GameState 已是 immutable value object）
- 统一关卡索引管理到 Game 内部
- load_level 通过 get_level_path() 获取路径
"""

from __future__ import annotations

from .actions import Action
from .board import Board
from .level import get_level_path
from .state import GameState


class Game:
    """推箱子游戏控制器。

    Attributes:
        board:           当前关卡的静态地图
        state:           当前动态游戏状态
        history:         历史状态栈（用于 Undo），不包含初始状态
        current_level:   当前关卡文件名
        current_level_index: 当前关卡在列表中的索引
        won:             是否已完成当前关卡
        level_files:     可用关卡文件名列表
    """

    def __init__(self) -> None:
        self.board: Board | None = None
        self.state: GameState | None = None
        self.history: list[GameState] = []
        self.current_level: str = ""
        self.current_level_index: int = -1
        self.won: bool = False
        self.level_files: list[str] = []

    def load_level(self, level_name: str, file_list: list[str] | None = None) -> None:
        """加载一个关卡并初始化游戏状态。

        Args:
            level_name: 关卡文件名，如 "level_01.txt"
            file_list: 可选，传入时同时更新关卡列表和索引
        """
        path = get_level_path(level_name)
        if not path.exists():
            raise FileNotFoundError(f"Level file not found: {path}")

        # 直接导入，避免循环依赖
        from .level import load_level as _load_level
        board, state = _load_level(level_name)
        self.board = board
        self.state = state
        self.history = []
        self.current_level = level_name
        self.won = False

        # 更新索引
        if file_list:
            self.level_files = file_list
            try:
                self.current_level_index = file_list.index(level_name)
            except ValueError:
                self.current_level_index = 0
        elif file_list is None and self.level_files:
            try:
                self.current_level_index = self.level_files.index(level_name)
            except ValueError:
                self.current_level_index = 0

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
            # 胜利后只响应 Reset
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

        from .rules import move as rules_move

        direction = self._DIRECTION_MAP[action]
        result = rules_move(self.board, self.state, direction)

        if result.new_state != self.state:  # 实际发生了移动
            self.history.append(self.state)  # 无需 copy.copy，GameState 已不可变
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
            self.load_level(self.current_level, self.level_files if self.level_files else None)

    # ---- 关卡切换 ----

    def next_level(self) -> bool:
        """进入下一关，成功返回 True。"""
        if not self.level_files or self.current_level_index < 0:
            return False
        if self.current_level_index < len(self.level_files) - 1:
            self.load_level(
                self.level_files[self.current_level_index + 1],
                self.level_files
            )
            return True
        return False

    def prev_level(self) -> bool:
        """返回上一关，成功返回 True。"""
        if not self.level_files or self.current_level_index <= 0:
            return False
        self.load_level(
            self.level_files[self.current_level_index - 1],
            self.level_files
        )
        return True
