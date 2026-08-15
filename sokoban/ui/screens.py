"""游戏 UI 屏幕 — 主菜单、HUD（抬头显示）、胜利界面。

V1.1 改进：
- 所有颜色从 Theme 读取，不再硬编码 RGB
- 删除未实现的 build_buttons() 方法
- WinOverlay 预创建字体和覆盖层（性能）
- 移除 emoji（跨平台兼容）
"""

from __future__ import annotations

from ..theme import _sys_font, CURRENT_THEME as THEME
from .widgets import Button, Label


class MenuScreen:
    """主菜单屏幕。显示标题和关卡选择按钮。"""

    def __init__(self) -> None:
        self.buttons: list[Button] = []

    def create_level_buttons(self, level_names: list[str],
                             screen_width: int, y_start: int = 350) -> None:
        """创建关卡选择按钮网格。"""
        self.buttons = []
        cols = 4
        total_width = cols * 140 + (cols - 1) * 12
        start_x = (screen_width - total_width) // 2

        for i, name in enumerate(level_names):
            row = i // cols
            col = i % cols
            x = start_x + col * 140
            y = y_start + row * 64
            label = name.replace(".txt", "")
            btn = Button(label, x, y, width=120, height=48, font_size=18)
            self.buttons.append(btn)

    def handle_click(self, mouse_pos: tuple[int, int],
                     mouse_clicked: bool) -> str | None:
        """处理点击事件，返回选中的关卡文件名；未选中则返回 None。"""
        for btn in self.buttons:
            if btn.update(mouse_pos, mouse_clicked):
                return btn.text + ".txt"
        return None

    def draw(self, screen) -> None:
        """绘制主菜单。"""
        import pygame
        from ..theme import CURRENT_THEME as T

        w = screen.get_width()
        h = screen.get_height()

        screen.fill(T.to_rgb(T.background))

        title_text = _sys_font(64, bold=True).render("SOKOBAN", True, T.to_rgb(T.box))
        title_rect = title_text.get_rect(centerx=w // 2, y=150)
        screen.blit(title_text, title_rect)

        sub_text = _sys_font(24, bold=True).render("Push Box", True, T.to_rgb(T.text))
        sub_rect = sub_text.get_rect(centerx=w // 2, y=230)
        screen.blit(sub_text, sub_rect)

        info_text = _sys_font(16).render("Select a level to start", True, T.to_rgb(T.text))
        info_rect = info_text.get_rect(centerx=w // 2, y=310)
        screen.blit(info_text, info_rect)

        help_text = _sys_font(14).render(
            "Arrow/WASD: Move | Z/Shift: Undo | R: Reset | N/M: Level | ESC: Pause",
            True, (120, 120, 120))
        screen.blit(help_text, help_text.get_rect(centerx=w // 2, y=h - 50))

        for btn in self.buttons:
            btn.draw(screen)


class HUD:
    """抬头显示 — 步数、推箱子数、控制按钮。"""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hud_y = screen_height - 90
        self.hud_height = 80

        # 统计标签（使用 Theme 颜色）
        text_color = THEME.to_rgb(THEME.text)
        dim_color = (160, 160, 160)
        self.moves_label = Label("Moves: 0", font_size=18, color=text_color)
        self.pushes_label = Label("Pushes: 0", font_size=18, color=text_color)
        self.level_label = Label("Level: 1", font_size=16, color=dim_color)

        # 功能按钮
        btn_w = 100
        btn_h = 36
        gap = 12
        total_btn_width = 3 * btn_w + 2 * gap
        start_x = (screen_width - total_btn_width) // 2

        self.undo_btn = Button("Undo", start_x, self.hud_y + 20, btn_w, btn_h, font_size=16)
        self.reset_btn = Button("Reset", start_x + btn_w + gap, self.hud_y + 20,
                                 btn_w, btn_h, font_size=16)
        self.menu_btn = Button("Menu", start_x + 2 * (btn_w + gap), self.hud_y + 20,
                                btn_w, btn_h, font_size=16)

        self.buttons = [self.undo_btn, self.reset_btn, self.menu_btn]

        # 上一关 / 下一关
        side_w = 80
        self.prev_btn = Button("Prev", 10, self.hud_y + 20, side_w, btn_h, font_size=14)
        self.next_btn = Button("Next", screen_width - side_w - 10, self.hud_y + 20,
                                side_w, btn_h, font_size=14)
        self.side_buttons = [self.prev_btn, self.next_btn]

    def update_stats(self, moves: int, pushes: int, current: int, total: int) -> None:
        """更新统计信息。"""
        self.moves_label.text = f"Moves: {moves}"
        self.pushes_label.text = f"Pushes: {pushes}"
        self.level_label.text = f"Level {current}/{total}"

    def get_actions(self, mouse_pos: tuple[int, int],
                    mouse_clicked: bool) -> list[str]:
        """处理 HUD 点击，返回触发的动作名列表。"""
        actions = []
        all_btns = self.buttons + self.side_buttons
        for btn in all_btns:
            if btn.update(mouse_pos, mouse_clicked):
                if btn is self.undo_btn:
                    actions.append("undo")
                elif btn is self.reset_btn:
                    actions.append("reset")
                elif btn is self.menu_btn:
                    actions.append("menu")
                elif btn is self.prev_btn:
                    actions.append("prev_level")
                elif btn is self.next_btn:
                    actions.append("next_level")
        return actions

    def draw(self, screen) -> None:
        """绘制 HUD 区域。"""
        import pygame
        hud_rect = pygame.Rect(0, self.hud_y, self.screen_width, self.hud_height)
        pygame.draw.rect(screen, THEME.to_rgb(THEME.hud_background), hud_rect)
        line_color = (50, 55, 70)
        pygame.draw.line(screen, line_color, (0, self.hud_y),
                         (self.screen_width, self.hud_y), 2)

        text_w = self.screen_width // 2 - 80
        self.moves_label.pos = (text_w, self.hud_y + 8)
        self.moves_label.draw(screen)
        self.pushes_label.pos = (text_w + 150, self.hud_y + 8)
        self.pushes_label.draw(screen)
        self.level_label.pos = (self.screen_width // 2 - 50, self.hud_y + 8)
        self.level_label.draw(screen)

        for btn in self.buttons:
            btn.draw(screen)
        for btn in self.side_buttons:
            btn.draw(screen)


class WinOverlay:
    """胜利覆盖层 — 显示结果，等待玩家操作（不自动跳关）。"""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.show_text = ""
        self.timer: int = 0
        # ← 标记本局是否已触发过显示（替代原来的 timer==0 判断）
        self._shown: bool = False
        self.big_font = _sys_font(48, bold=True)
        self.small_font = _sys_font(24)

    def show(self, moves: int, pushes: int) -> None:
        """显示胜利信息。"""
        self.show_text = f"LEVEL COMPLETE!\nMoves: {moves}  Pushes: {pushes}"
        self.timer = 0
        self._shown = True

    def draw(self, screen) -> None:
        """绘制半透明覆盖层和胜利文字 + 下一步提示。"""
        import pygame

        if not self.show_text:
            return

        progress = min(1.0, self.timer / 30)
        alpha = int(180 * progress)

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.set_alpha(min(150, alpha))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        text_lines = self.show_text.split(chr(10))
        center_x = self.screen_width // 2
        y_start = self.screen_height // 2 - 40

        for i, line in enumerate(text_lines):
            surf = self.big_font.render(line, True, (255, 220, 100)) if i == 0 else \
                self.small_font.render(line, True, (200, 200, 200))
            rect = surf.get_rect(centerx=center_x, y=y_start + i * 40)
            screen.blit(surf, rect)

        btn_text = self.small_font.render("Press Enter or SPACE for next level", True, (180, 180, 180))
        screen.blit(btn_text, btn_text.get_rect(centerx=center_x, y=self.screen_height - 80))
