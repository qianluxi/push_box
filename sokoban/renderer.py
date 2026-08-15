"""Pygame 渲染层。

纯矩形/圆形绘制，不依赖外部图片素材。
第一版一个文件即可，超过 300~400 行再拆分。
"""

from __future__ import annotations

import pygame

from .board import Board
from .state import GameState, Position
from .theme import Color, CURRENT_THEME as THEME


class Renderer:
    """游戏画面渲染器。

    所有绘制基于 pygame.draw 和 pygame.font 完成，
    不需要任何外部图片素材。

    Args:
        cell_size: 每个格子的像素大小（默认 64）
    """

    def __init__(self, cell_size: int = 64) -> None:
        self.cell_size = cell_size

    # ---- 入口 ----

    def draw(self, screen: pygame.Surface, board: Board, state: GameState) -> None:
        """绘制完整的游戏画面。

        Args:
            screen: pygame 显示表面
            board: 静态地图
            state: 动态状态
        """
        # 清屏
        screen.fill(THEME.to_rgb(THEME.background))

        # 计算画布偏移（居中）
        offset_x, offset_y = self._compute_offset(board)

        # 绘制地板和墙
        for row in range(board.height):
            for col in range(board.width):
                rect = pygame.Rect(
                    offset_x + col * self.cell_size,
                    offset_y + row * self.cell_size,
                    self.cell_size, self.cell_size,
                )

                if board.contains_wall(row, col):
                    pygame.draw.rect(screen, THEME.to_rgb(THEME.wall), rect)
                    # 墙上加一点纹理效果
                    pygame.draw.rect(
                        screen,
                        tuple(max(0, c - 15) for c in THEME.to_rgb(THEME.wall)),
                        rect, border_radius=2,
                    )
                else:
                    pygame.draw.rect(screen, THEME.to_rgb(THEME.floor), rect)
                    pygame.draw.rect(
                        screen,
                        tuple(min(255, c + 5) for c in THEME.to_rgb(THEME.floor)),
                        rect, width=1, border_radius=4,
                    )

        # 绘制目标点
        for goal in board.goals:
            cx = offset_x + goal[1] * self.cell_size + self.cell_size // 2
            cy = offset_y + goal[0] * self.cell_size + self.cell_size // 2
            r = self.cell_size // 6
            pygame.draw.circle(screen, THEME.to_rgb(THEME.goal), (cx, cy), r)

        # 绘制箱子
        for box in state.boxes:
            self._draw_box(screen, board, state, box, offset_x, offset_y)

        # 绘制玩家
        self._draw_player(screen, state.player, offset_x, offset_y)

    # ---- 各元素绘制 ----

    def _draw_box(
        self, screen: pygame.Surface, board: Board, state: GameState,
        box: Position, offset_x: int, offset_y: int,
    ) -> None:
        """绘制单个箱子。在目标上时使用不同颜色。"""
        on_goal = board.is_goal_position(box.row, box.col)
        color = THEME.to_rgb(THEME.box_on_goal) if on_goal else THEME.to_rgb(THEME.box)

        margin = self.cell_size // 8
        rect = pygame.Rect(
            offset_x + box.col * self.cell_size + margin,
            offset_y + box.row * self.cell_size + margin,
            self.cell_size - 2 * margin,
            self.cell_size - 2 * margin,
        )
        pygame.draw.rect(screen, color, rect, border_radius=6)

        # 箱子内部十字线
        mid = self.cell_size // 2
        inner_margin = margin + 4
        pygame.draw.line(
            screen,
            tuple(max(0, c - 40) for c in color),
            (offset_x + box.col * self.cell_size + inner_margin,
             offset_y + box.row * self.cell_size + mid),
            (offset_x + box.col * self.cell_size + self.cell_size - inner_margin,
             offset_y + box.row * self.cell_size + mid),
            width=2,
        )
        pygame.draw.line(
            screen,
            tuple(max(0, c - 40) for c in color),
            (offset_x + box.col * self.cell_size + mid,
             offset_y + box.row * self.cell_size + inner_margin),
            (offset_x + box.col * self.cell_size + mid,
             offset_y + box.row * self.cell_size + self.cell_size - inner_margin),
            width=2,
        )

    def _draw_player(self, screen: pygame.Surface, player: Position,
                     offset_x: int, offset_y: int) -> None:
        """绘制玩家 — 用圆形表示。"""
        cx = offset_x + player.col * self.cell_size + self.cell_size // 2
        cy = offset_y + player.row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 3

        # 外圈光晕
        pygame.draw.circle(screen, THEME.to_rgb(THEME.player), (cx, cy), radius + 2)
        # 主体
        color = tuple(min(255, c + 30) for c in THEME.to_rgb(THEME.player))
        pygame.draw.circle(screen, color, (cx, cy), radius)

    # ---- 辅助方法 ----

    def _compute_offset(self, board: Board) -> tuple[int, int]:
        """计算棋盘居中偏移。"""
        board_px_width = board.width * self.cell_size
        board_px_height = board.height * self.cell_size

        surf = pygame.display.get_surface()
        if surf is not None:
            screen_height = surf.get_height()
            hud_area = max(0, screen_height - board_px_height - 90)
            offset_x = max(0, (surf.get_width() - board_px_width) // 2)
            offset_y = max(0, (screen_height - board_px_height - hud_area) // 2)
        else:
            # 无显示表面时的默认值
            offset_x = 20
            offset_y = 10

        return offset_x, offset_y
