"""Sokoban — 推箱子游戏。程序入口。

启动流程：
1. 初始化 Pygame
2. 加载关卡列表
3. 显示主菜单，等待玩家选择关卡
4. 进入游戏循环：处理输入 → 更新状态 → 渲染画面
5. 支持撤回、重置、切换关卡等完整交互
"""

from __future__ import annotations

import sys

from sokoban.theme import _sys_font

import pygame

from sokoban.actions import Action
from sokoban.game import Game
from sokoban.level import find_level_files, get_level_path
from sokoban.renderer import Renderer
from sokoban.theme import CURRENT_THEME as THEME
from sokoban.ui.screens import HUD, MenuScreen, WinOverlay


# ---- 键盘到 Action 的映射 ----

_KEY_TO_ACTION = {
    # 方向键
    pygame.K_UP: Action.UP,
    pygame.K_DOWN: Action.DOWN,
    pygame.K_LEFT: Action.LEFT,
    pygame.K_RIGHT: Action.RIGHT,
    # WASD
    pygame.K_w: Action.UP,
    pygame.K_s: Action.DOWN,
    pygame.K_a: Action.LEFT,
    pygame.K_d: Action.RIGHT,
}

_ACTION_MAP_KEYS = {
    "undo": [pygame.K_z, pygame.K_RSHIFT],
    "reset": [pygame.K_r],
    "next_level": [pygame.K_n],
    "prev_level": [pygame.K_m],
}


def _get_action_from_key(keycode: int) -> Action | None:
    """将按键码转换为 Action。"""
    if keycode in _KEY_TO_ACTION:
        return _KEY_TO_ACTION[keycode]
    for action_name, keys in _ACTION_MAP_KEYS.items():
        if keycode in keys:
            if action_name == "undo":
                return Action.UNDO
            elif action_name == "reset":
                return Action.RESET
            elif action_name == "next_level":
                return Action.NEXT_LEVEL
            elif action_name == "prev_level":
                return Action.PREV_LEVEL
    return None


def main() -> None:
    """游戏主函数。"""

    # ---- Pygame 初始化 ----
    pygame.init()

    # 窗口尺寸（会自适应棋盘大小）
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Sokoban — 推箱子")
    clock = pygame.time.Clock()

    # 游戏实例
    game = Game()
    renderer = Renderer(cell_size=64)

    # UI 组件
    menu_screen = MenuScreen()
    hud = HUD(screen_width, screen_height)
    win_overlay = WinOverlay(screen_width, screen_height)

    # 加载关卡列表
    level_files = find_level_files("levels")
    if not level_files:
        print("错误：未找到任何关卡文件！请在 levels/ 目录下放置 .txt 关卡文件。")
        pygame.quit()
        sys.exit(1)

    game.set_level_files(level_files)
    menu_screen.create_level_buttons(level_files, screen_width)

    # 游戏状态机
    state = "menu"  # "menu" | "playing" | "win_pending"

    # 当前选中的关卡（在暂停时恢复用）
    current_level_index = 0

    running = True
    paused = False

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        # ---- 事件循环 ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if state == "playing":
                    # ESC 暂停
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                        continue

                    action = _get_action_from_key(event.key)
                    if action:
                        game.handle(action)
                    continue

                if state == "menu":
                    # 回车快速开始第一关
                    if event.key == pygame.K_RETURN and level_files:
                        game.load_level(level_files[0])
                        state = "playing"
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        # ---- 鼠标悬停状态更新（非点击帧也需要）----
        pygame.mouse.get_pressed()

        # ---- 状态机 ----

        if state == "menu":
            # 主菜单渲染
            chosen = menu_screen.handle_click(mouse_pos, mouse_clicked)
            if chosen:
                # 查找关卡索引
                try:
                    idx = level_files.index(chosen)
                    game.load_level(chosen)
                    current_level_index = idx
                    state = "playing"
                except (ValueError, FileNotFoundError):
                    pass

            menu_screen.draw(screen)
            pygame.display.flip()
            clock.tick(60)

        elif state == "playing":
            # 计算需要的窗口大小（适应棋盘）
            if game.board:
                needed_h = game.board.height * renderer.cell_size + hud.hud_height + 10
                needed_w = game.board.width * renderer.cell_size + 40
                new_w = max(screen_width, needed_w)
                new_h = max(screen_height, needed_h)
                if new_w != screen.get_width() or new_h != screen.get_height():
                    screen = pygame.display.set_mode((new_w, new_h))
                    screen_width = new_w
                    screen_height = new_h
                    hud = HUD(screen_width, screen_height)

            if paused:
                # 绘制暂停遮罩
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                screen.blit(overlay, (0, 0))

                pause_text = _sys_font(48, bold=True).render(
                    "已暂停", True, (200, 200, 200))
                pause_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(pause_text, pause_rect)
                pygame.display.flip()
                clock.tick(60)
                continue

            # HUD 按钮处理
            if mouse_clicked:
                hud_actions = hud.get_actions(mouse_pos, mouse_clicked)
                for action_name in hud_actions:
                    if action_name == "undo":
                        game.handle(Action.UNDO)
                    elif action_name == "reset":
                        game.handle(Action.RESET)
                    elif action_name == "menu":
                        state = "menu"
                        menu_screen.create_level_buttons(level_files, screen_width)
                    elif action_name == "next_level":
                        game.handle(Action.NEXT_LEVEL)
                        current_level_index = min(
                            current_level_index + 1, len(level_files) - 1)
                    elif action_name == "prev_level":
                        game.handle(Action.PREV_LEVEL)
                        current_level_index = max(current_level_index - 1, 0)

            # 绘制游戏画面
            if game.board and game.state:
                renderer.draw(screen, game.board, game.state)

                # HUD
                total_levels = len(level_files)
                hud.update_stats(
                    moves=game.state.moves,
                    pushes=game.state.pushes,
                    current=current_level_index + 1,
                    total=total_levels,
                )
                hud.draw(screen)

                # 胜利覆盖层
                if game.won and win_overlay.timer == 0:
                    win_overlay.show(game.state.moves, game.state.pushes)
                    state = "win_pending"

            pygame.display.flip()
            clock.tick(60)

        elif state == "win_pending":
            # 胜利延迟帧
            if game.board and game.state:
                renderer.draw(screen, game.board, game.state)
                hud.draw(screen)

            if win_overlay.timer == 0:
                win_overlay.show(game.state.moves, game.state.pushes)

            should_hide = win_overlay.update()
            win_overlay.draw(screen)
            pygame.display.flip()
            clock.tick(60)

            if should_hide:
                # 自动进入下一关或返回菜单
                if current_level_index < len(level_files) - 1:
                    current_level_index += 1
                    next_level = level_files[current_level_index]
                    game.load_level(next_level)
                    win_overlay.timer = -1  # 重置
                    state = "playing"
                else:
                    # 所有关卡完成！
                    all_done_text = _sys_font(48, bold=True).render(
                        "🏆 All Levels Complete!", True, (255, 220, 100))
                    back_text = _sys_font(24).render(
                        "按任意键返回主菜单", True, (200, 200, 200))

                    while True:
                        renderer.draw(screen, game.board, game.state)
                        hud.draw(screen)
                        screen.blit(all_done_text,
                                    all_done_text.get_rect(center=(screen_width // 2, screen_height // 2 - 20)))
                        screen.blit(back_text,
                                    back_text.get_rect(center=(screen_width // 2, screen_height // 2 + 40)))
                        pygame.display.flip()

                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                break
                            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                                state = "menu"
                                menu_screen.create_level_buttons(level_files, screen_width)
                                win_overlay.timer = -1
                                break
                        clock.tick(60)
                    if not running:
                        break

    # ---- 退出 ----
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
