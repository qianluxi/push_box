"""视觉主题 — 用数据类定义配色方案。

方便将来扩展更多主题（Dark / Pastel / Forest / Ocean 等）。
第一版先提供两个预设：Classic 和 Dark。
"""

from __future__ import annotations

import pygame
from dataclasses import dataclass


def _sys_font(size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """创建系统字体，带多层回退机制。"""
    try:
        return pygame.font.SysFont("microsoftyahei", size, bold=bold, italic=italic)
    except Exception:
        pass
    try:
        f = pygame.font.match_font("arial")
        if f:
            return pygame.font.Font(f, size)
    except Exception:
        pass
    return pygame.font.Font(None, size)


@dataclass(frozen=True)
class Color:
    """RGB 颜色元组。"""
    r: int
    g: int
    b: int


@dataclass(frozen=True)
class Theme:
    """一组视觉主题常量。"""
    background: Color
    wall: Color
    floor: Color
    goal: Color
    box: Color
    box_on_goal: Color
    player: Color
    text: Color
    button: Color
    button_hover: Color
    button_text: Color
    hud_background: Color

    def to_rgb(self, c: Color) -> tuple[int, int, int]:
        return (c.r, c.g, c.b)


# ---- 预设主题 ----

CLASSIC = Theme(
    background=Color(30, 30, 46),
    wall=Color(71, 85, 105),
    floor=Color(49, 50, 68),
    goal=Color(240, 240, 240),
    box=Color(229, 182, 88),
    box_on_goal=Color(86, 156, 86),
    player=Color(205, 133, 63),
    text=Color(220, 220, 220),
    button=Color(59, 64, 86),
    button_hover=Color(83, 89, 114),
    button_text=Color(220, 220, 220),
    hud_background=Color(25, 27, 38),
)

DARK = Theme(
    background=Color(15, 15, 25),
    wall=Color(35, 35, 55),
    floor=Color(25, 25, 40),
    goal=Color(200, 200, 200),
    box=Color(180, 140, 60),
    box_on_goal=Color(60, 160, 60),
    player=Color(180, 120, 40),
    text=Color(200, 200, 200),
    button=Color(40, 40, 60),
    button_hover=Color(55, 55, 80),
    button_text=Color(200, 200, 200),
    hud_background=Color(10, 10, 20),
)

# 默认使用 Classic 主题
CURRENT_THEME = CLASSIC
