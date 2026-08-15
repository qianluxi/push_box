"""Sokoban — 推箱子游戏。程序入口。

V1.1 精简为薄入口层（≈60 行），所有状态机逻辑委托给 AppController。
"""

from __future__ import annotations


def main() -> None:
    """游戏主函数。"""
    import sys

    import pygame

    from sokoban.app import AppController

    # ---- Pygame 初始化 ----
    pygame.init()
    screen = pygame.display.set_mode((AppController.FIXED_WIDTH, AppController.FIXED_HEIGHT))
    pygame.display.set_caption("SOKOBAN -- Push Box")
    clock = pygame.time.Clock()

    # ---- 应用控制器 ----
    app = AppController()

    running = True
    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break

        app.handle_events(events)
        app.render(screen)

        pygame.display.flip()
        clock.tick(AppController.FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
