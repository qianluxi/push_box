"""应用控制器 — 替代 main.py 中的状态机混乱。

V1.1 核心改进：
- AppState Enum 统一表示所有程序状态（替代 state string + paused bool）
- AppController 封装完整的应用生命周期
- 单一主循环：handle_events → update → render
- 胜利后不自动跳关，等待玩家操作
- 删除内嵌 while True（nested event loop bug）
- Game 唯一数据源：index/level_files 由 Game 管理
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from .actions import Action
from .game import Game
from .level import find_level_files
from .renderer import Renderer
from .theme import CURRENT_THEME as THEME
from .ui.screens import HUD, MenuScreen, WinOverlay


class AppState(Enum):
    """应用程序状态枚举。"""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    WIN = auto()
    COMPLETE = auto()


# ---- 键盘到 Action 的映射 ----

_KEY_TO_ACTION = {
    pygame.K_UP: Action.UP,
    pygame.K_DOWN: Action.DOWN,
    pygame.K_LEFT: Action.LEFT,
    pygame.K_RIGHT: Action.RIGHT,
    pygame.K_w: Action.UP,
    pygame.K_s: Action.DOWN,
    pygame.K_a: Action.LEFT,
    pygame.K_d: Action.RIGHT,
}


def _key_to_action(keycode: int) -> Action | None:
    """将按键码转换为 Action，或返回 None。"""
    if keycode in _KEY_TO_ACTION:
        return _KEY_TO_ACTION[keycode]
    match keycode:
        case pygame.K_z | pygame.K_RSHIFT:
            return Action.UNDO
        case pygame.K_r:
            return Action.RESET
        case pygame.K_n:
            return Action.NEXT_LEVEL
        case pygame.K_m:
            return Action.PREV_LEVEL
        case _:
            return None


class AppController:
    """应用控制器 — 管理整个 Sokoban 游戏的主循环。

    V1.1 新架构：
        main.py (≈80 行)
            ↓
        AppController.handle_events() / update() / render(screen)
            ↓
        GameState ← Game ← Rules ← Board
    """

    FIXED_WIDTH = 960
    FIXED_HEIGHT = 720
    FPS = 60

    def __init__(self) -> None:
        self.game = Game()
        self.state = AppState.MENU

        # 关卡列表
        self.level_files = find_level_files("levels")
        if not self.level_files:
            raise RuntimeError("No level files found in levels/")

        self.game.set_level_files(self.level_files)

        # UI 组件
        self.screen_width = self.FIXED_WIDTH
        self.screen_height = self.FIXED_HEIGHT
        self.renderer = Renderer(cell_size=64)  # cell_size 会被动态调整
        self.menu_screen = MenuScreen()
        self.hud = HUD(self.screen_width, self.screen_height)
        self.win_overlay = WinOverlay(self.screen_width, self.screen_height)

        # 菜单初始化
        self.menu_screen.create_level_buttons(
            self.level_files, self.screen_width
        )

    # ---- 事件处理 ----

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """分发事件到当前状态的处理器。"""
        for event in events:
            if event.type == pygame.QUIT:
                self._handle_quit()

            elif event.type == pygame.KEYDOWN:
                if self.state == AppState.MENU:
                    self._menu_keydown(event.key)
                elif self.state == AppState.PLAYING:
                    self._playing_keydown(event.key)
                elif self.state == AppState.PAUSED:
                    self._paused_keydown(event.key)
                elif self.state in (AppState.WIN, AppState.COMPLETE):
                    self._win_keydown(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                self._mouse_click(mouse_pos)

        pygame.mouse.get_pressed()  # 刷新悬停状态

    def _handle_quit(self) -> None:
        """处理退出请求。"""
        import sys
        pygame.quit()
        sys.exit(0)

    # ---- 菜单状态 ----

    def _menu_keydown(self, key: int) -> None:
        if key == pygame.K_RETURN and self.level_files:
            self.game.load_level(self.level_files[0], self.level_files)
            self.state = AppState.PLAYING

    def _playing_keydown(self, key: int) -> None:
        action = _key_to_action(key)
        if action:
            self.game.handle(action)
        elif key == pygame.K_ESCAPE:
            self.state = AppState.PAUSED

    def _paused_keydown(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.state = AppState.PLAYING

    def _win_keydown(self, key: int) -> None:
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self._advance_from_win()

    def _mouse_click(self, pos: tuple[int, int]) -> None:
        if self.state == AppState.MENU:
            chosen = self.menu_screen.handle_click(pos, True)
            if chosen:
                self.game.load_level(chosen, self.level_files)
                self.state = AppState.PLAYING

        elif self.state == AppState.PLAYING:
            actions = self.hud.get_actions(pos, True)
            for name in actions:
                match name:
                    case "undo":
                        self.game.handle(Action.UNDO)
                    case "reset":
                        self.game.handle(Action.RESET)
                    case "prev_level":
                        self.game.prev_level()
                    case "next_level":
                        self.game.next_level()
                    case "menu":
                        self._back_to_menu()

        elif self.state == AppState.WIN:
            if self._is_in_next_button_area(pos):
                self._advance_from_win()

    def _is_in_next_button_area(self, pos: tuple[int, int]) -> bool:
        """检查点击是否在"下一关"按钮区域（屏幕底部中央）。"""
        bx = self.screen_width // 2 - 80
        by = self.screen_height - 80
        bw, bh = 160, 50
        return bx <= pos[0] <= bx + bw and by <= pos[1] <= by + bh

    def _back_to_menu(self) -> None:
        """返回主菜单。"""
        self.state = AppState.MENU
        self.menu_screen.create_level_buttons(
            self.level_files, self.screen_width
        )

    def _advance_from_win(self) -> None:
        """从胜利界面进入下一关或完成。"""
        if self.game.next_level():
            self.win_overlay.timer = -1  # 重置计时器
        else:
            self.state = AppState.COMPLETE

    # ---- 渲染 ----

    def render(self, screen: pygame.Surface) -> None:
        """根据当前状态渲染画面。"""
        if self.state == AppState.MENU:
            self._render_menu(screen)
        elif self.state == AppState.PLAYING:
            self._render_playing(screen)
        elif self.state == AppState.PAUSED:
            self._render_paused(screen)
        elif self.state == AppState.WIN:
            self._render_win(screen)
        elif self.state == AppState.COMPLETE:
            self._render_complete(screen)

    def _compute_cell_size(self) -> int:
        """根据棋盘大小计算最优 cell_size。"""
        if not self.game.board or not self.game.state:
            return 64
        board_px_max_w = self.screen_width - 40
        board_px_max_h = self.screen_height - 180  # 留出 HUD + win 空间
        cw = board_px_max_w / self.game.board.width
        ch = board_px_max_h / self.game.board.height
        return max(32, min(int(min(cw, ch)), 80))

    def _render_menu(self, screen: pygame.Surface) -> None:
        screen.fill(THEME.to_rgb(THEME.background))
        self.menu_screen.draw(screen)

    def _render_playing(self, screen: pygame.Surface) -> None:
        if not self.game.board or not self.game.state:
            return

        # 动态 cell_size
        cell = self._compute_cell_size()
        if cell != self.renderer.cell_size:
            self.renderer.cell_size = cell

        # 绘制棋盘
        self.renderer.draw(screen, self.game.board, self.game.state)

        # 更新并绘制 HUD
        total = len(self.level_files)
        self.hud.update_stats(
            moves=self.game.state.moves,
            pushes=self.game.state.pushes,
            current=self.game.current_level_index + 1,
            total=total,
        )
        self.hud.draw(screen)

        # 检测胜利
        if self.game.won and self.win_overlay.timer == 0:
            self.win_overlay.show(moves=self.game.state.moves, pushes=self.game.state.pushes)
            self.state = AppState.WIN

    def _render_paused(self, screen: pygame.Surface) -> None:
        if self.game.board and self.game.state:
            self.renderer.draw(screen, self.game.board, self.game.state)
            self.hud.draw(screen)

        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        text = pygame.font.SysFont("arial", 48, bold=True).render(
            "已暂停", True, (200, 200, 200))
        screen.blit(text, text.get_rect(center=(self.screen_width // 2,
                                                self.screen_height // 2)))

    def _render_win(self, screen: pygame.Surface) -> None:
        if self.game.board and self.game.state:
            self.renderer.draw(screen, self.game.board, self.game.state)
            self.hud.draw(screen)

        self.win_overlay.draw(screen)

    def _render_complete(self, screen: pygame.Surface) -> None:
        if self.game.board and self.game.state:
            self.renderer.draw(screen, self.game.board, self.game.state)
            self.hud.draw(screen)

        # 通关提示
        text = pygame.font.SysFont("arial", 48, bold=True).render(
            "ALL LEVELS COMPLETE!", True, (255, 220, 100))
        back = pygame.font.SysFont("arial", 24).render(
            "Press Enter to return to menu", True, (200, 200, 200))
        screen.blit(text, text.get_rect(center=(self.screen_width // 2,
                                                self.screen_height // 2 - 20)))
        screen.blit(back, back.get_rect(center=(self.screen_width // 2,
                                                self.screen_height // 2 + 40)))
