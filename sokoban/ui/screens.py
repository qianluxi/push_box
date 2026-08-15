"""游戏 UI 屏幕 — 主菜单、HUD（抬头显示）、胜利界面。"""
from __future__ import annotations

from ..theme import _sys_font

import pygame

from ..game import Game
from .widgets import Button, Label


class MenuScreen:
    """主菜单屏幕。

    显示标题和关卡选择按钮。
    """

    def __init__(self) -> None:
        self.title_label = Label("SOKOBAN", font_size=56)
        self.subtitle_label = Label("推 箱 子", font_size=24)
        self.buttons: list[Button] = []

    def build_buttons(self, buttons_per_row: int = 4, padding: int = 12,
                      btn_width: int = 120, btn_height: int = 48) -> None:
        """根据关卡数量生成按钮网格。"""
        count = len(self.buttons)
        if count > 0:
            # 已有按钮，重新计算位置
            pass

    def create_level_buttons(self, level_names: list[str],
                             screen_width: int, y_start: int = 350) -> None:
        """创建关卡选择按钮。"""
        self.buttons = []
        cols = 4
        rows_needed = (len(level_names) + cols - 1) // cols
        total_width = cols * 140 + (cols - 1) * 12
        start_x = (screen_width - total_width) // 2

        for i, name in enumerate(level_names):
            row = i // cols
            col = i % cols
            x = start_x + col * 140
            y = y_start + row * 64
            label = name.replace('.txt', '')
            btn = Button(label, x, y, width=120, height=48, font_size=18)
            self.buttons.append(btn)

    def handle_click(self, mouse_pos: tuple[int, int],
                     mouse_clicked: bool) -> str | None:
        """处理点击事件，返回选中的关卡文件名；未选中则返回 None。"""
        for btn in self.buttons:
            if btn.update(mouse_pos, mouse_clicked):
                return btn.text + '.txt'
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """绘制主菜单。"""
        screen.fill((25, 27, 38))

        # 标题
        rendered_title = _sys_font(64, bold=True).render(
            "SOKOBAN", True, (220, 200, 160))
        title_rect = rendered_title.get_rect(centerx=screen.get_width() // 2, y=150)
        screen.blit(rendered_title, title_rect)

        rendered_sub = _sys_font(24, bold=True).render(
            "推 箱 子", True, (180, 180, 180))
        sub_rect = rendered_sub.get_rect(centerx=screen.get_width() // 2, y=230)
        screen.blit(rendered_sub, sub_rect)

        # 说明文字
        rendered_info = _sys_font(16).render(
            "选择一个关卡开始游戏", True, (150, 150, 150))
        info_rect = rendered_info.get_rect(centerx=screen.get_width() // 2, y=310)
        screen.blit(rendered_info, info_rect)

        # 按键提示
        rendered_help = _sys_font(14).render(
            "方向键/WASD：移动 | Z/Shift：撤回 | R：重置 | N/M：切换关卡",
            True, (120, 120, 120))
        help_rect = rendered_help.get_rect(centerx=screen.get_width() // 2, y=screen.get_height() - 50)
        screen.blit(rendered_help, help_rect)

        # 关卡按钮
        for btn in self.buttons:
            btn.draw(screen)


class HUD:
    """抬头显示 — 步数、推箱子数、控制按钮。"""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hud_y = screen_height - 90
        self.hud_height = 80

        # 统计标签
        self.moves_label = Label("Moves: 0", font_size=18, color=(200, 200, 200))
        self.pushes_label = Label("Pushes: 0", font_size=18, color=(200, 200, 200))
        self.level_label = Label("Level: 1", font_size=16, color=(160, 160, 160))

        # 功能按钮
        btn_w = 100
        btn_h = 36
        gap = 12
        total_btn_width = 3 * btn_w + 2 * gap
        start_x = (screen_width - total_btn_width) // 2

        self.undo_btn = Button("↩ Undo", start_x, self.hud_y + 20, btn_w, btn_h, font_size=16)
        self.reset_btn = Button("⟳ Reset", start_x + btn_w + gap, self.hud_y + 20,
                                btn_w, btn_h, font_size=16)
        self.menu_btn = Button("☰ Menu", start_x + 2 * (btn_w + gap), self.hud_y + 20,
                               btn_w, btn_h, font_size=16)

        self.buttons = [self.undo_btn, self.reset_btn, self.menu_btn]

        # 上一关 / 下一关（放在两侧）
        left_btn_w = 80
        self.prev_btn = Button("◀ Prev", 10, self.hud_y + 20, left_btn_w, btn_h, font_size=14)
        self.next_btn = Button("Next ▶", screen_width - left_btn_w - 10,
                               self.hud_y + 20, left_btn_w, btn_h, font_size=14)
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

    def draw(self, screen: pygame.Surface) -> None:
        """绘制 HUD 区域。"""
        # HUD 背景条
        hud_rect = pygame.Rect(0, self.hud_y, self.screen_width, self.hud_height)
        pygame.draw.rect(screen, (20, 22, 32), hud_rect)
        pygame.draw.line(screen, (50, 55, 70), (0, self.hud_y),
                         (self.screen_width, self.hud_y), 2)

        # 统计文字
        text_w = self.screen_width // 2 - 80
        self.moves_label.pos = (text_w, self.hud_y + 8)
        self.moves_label.draw(screen)

        self.pushes_label.pos = (text_w + 150, self.hud_y + 8)
        self.pushes_label.draw(screen)

        self.level_label.pos = (self.screen_width // 2 - 50, self.hud_y + 8)
        self.level_label.draw(screen)

        # 按钮
        for btn in self.buttons:
            btn.draw(screen)
        for btn in self.side_buttons:
            btn.draw(screen)


class WinOverlay:
    """胜利覆盖层。短暂显示后自动返回。"""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.alpha_surface: pygame.Surface | None = None
        self.show_text = ""
        self.timer: int = 0  # 已显示帧数
        self.duration: int = 150  # 约 2.5 秒（60fps）

    def show(self, moves: int, pushes: int) -> None:
        """显示胜利信息。"""
        self.show_text = f"🎉 Level Complete!\nMoves: {moves}  Pushes: {pushes}"
        self.timer = 0

    def update(self) -> bool:
        """更新计时器，返回是否应该隐藏。"""
        if self.timer < self.duration:
            self.timer += 1
            return False
        return True

    def draw(self, screen: pygame.Surface) -> None:
        """绘制半透明覆盖层和胜利文字。"""
        if not self.show_text or self.timer >= self.duration:
            return

        progress = min(1.0, self.timer / 30)  # 淡入 0.5 秒
        fade_out = max(0, 1.0 - (self.timer - 120) / 30) if self.timer > 120 else 1.0

        # 半透明背景
        alpha = int(180 * progress * fade_out)
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.set_alpha(min(255, alpha))
        overlay.fill((0, 0, 0, min(200, alpha)))
        screen.blit(overlay, (0, 0))

        # 胜利文字
        text_lines = self.show_text.split('\n')
        center_x = self.screen_width // 2
        y_start = self.screen_height // 2 - 30

        big_font = _sys_font(48, bold=True)
        small_font = _sys_font(24)

        line_surfs = []
        for i, line in enumerate(text_lines):
            surf = big_font.render(line, True, (255, 220, 100)) if i == 0 else \
                   small_font.render(line, True, (200, 200, 200))
            rect = surf.get_rect(centerx=center_x, y=y_start + i * 40)
            line_surfs.append((surf, rect))

        for surf, rect in line_surfs:
            screen.blit(surf, rect)
