"""UI 控件组件 — 按钮、标签等基础 Widget。"""

from __future__ import annotations

import pygame

from ..theme import CURRENT_THEME as THEME, _sys_font


def create_font(size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """创建字体，优先使用微软雅黑，失败则回退到默认字体。"""
    return _sys_font(size, bold=bold, italic=italic)


class Button:
    """可点击按钮。

    Args:
        text:     按钮文字
        pos:      (x, y) 左上角坐标
        width:    宽度
        height:   高度
        font_size:字号
    """

    def __init__(self, text: str, x: int, y: int, width: int = 100,
                 height: int = 40, font_size: int = 20) -> None:
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = create_font(font_size, bold=True)
        self.hovered = False
        self.clicked = False

    def update(self, mouse_pos: tuple[int, int], mouse_clicked: bool) -> bool:
        """更新按钮状态，返回是否被点击。

        Args:
            mouse_pos:     当前鼠标位置 (x, y)
            mouse_clicked: 鼠标是否刚刚按下左键

        Returns:
            True if button was clicked
        """
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_clicked:
            return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        """绘制按钮。"""
        bg_color = THEME.to_rgb(THEME.button_hover) if self.hovered \
            else THEME.to_rgb(THEME.button)
        text_color = THEME.to_rgb(THEME.button_text)

        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(
            screen,
            tuple(min(255, c + 30) for c in bg_color),
            self.rect, width=2, border_radius=8,
        )

        rendered = self.font.render(self.text, True, text_color)
        text_rect = rendered.get_rect(center=self.rect.center)
        screen.blit(rendered, text_rect)


class Label:
    """文本标签。

    Args:
        text:      显示文字
        pos:       (x, y) 左上角坐标（相对于某个容器）
        font_size: 字号
        color:     Color 对象
    """

    def __init__(self, text: str, x: int = 0, y: int = 0,
                 font_size: int = 18, color: tuple[int, int, int] | None = None) -> None:
        self.text = text
        self.pos = (x, y)
        self.font = create_font(font_size)
        self.color = color or THEME.to_rgb(THEME.text)

    def draw(self, screen: pygame.Surface, offset_x: int = 0, offset_y: int = 0) -> None:
        """绘制标签。"""
        rendered = self.font.render(self.text, True, self.color)
        screen.blit(rendered, (self.pos[0] + offset_x, self.pos[1] + offset_y))
