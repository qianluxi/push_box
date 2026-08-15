"""玩家动作枚举。

所有操作（键盘、鼠标、AI Solver）统一抽象为 Action，
由 Game 控制器协调分发。UI 层不直接修改游戏状态。
"""

from enum import Enum, auto


class Action(Enum):
    """推箱子游戏的标准动作。"""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    UNDO = auto()   # 撤回上一步
    RESET = auto()  # 重置当前关卡
    NEXT_LEVEL = auto()  # 进入下一关
    PREV_LEVEL = auto()  # 返回上一关
    QUIT = auto()     # 退出游戏
