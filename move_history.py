"""Move-history side panel with scrolling."""
import pygame
import chess
from constants import PANEL_X, PANEL_WIDTH, WINDOW_HEIGHT, WHITE, GRAY, LIGHT_GRAY
import theme as th


class MoveHistory:
    def __init__(self):
        self._font = pygame.font.SysFont("Consolas", 15)
        self._title_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.scroll_offset = 0
        self._line_h = 22
        self._top = 200
        self._bottom = WINDOW_HEIGHT - 30
        self._visible_h = self._bottom - self._top

    def draw(self, surface, board: chess.Board):
        t = th.active_theme()
        # panel background
        panel_rect = pygame.Rect(PANEL_X - 8, self._top - 30,
                                 PANEL_WIDTH + 16, self._visible_h + 40)
        pygame.draw.rect(surface, t["panel_bg"], panel_rect, border_radius=8)
        pygame.draw.rect(surface, (*t["accent"], 80) if len(t["accent"]) == 3
                         else t["accent"], panel_rect, 1, border_radius=8)

        # title
        title = self._title_font.render("Move History", True, t["panel_txt"])
        surface.blit(title, (PANEL_X + 4, self._top - 26))

        # moves
        move_stack = list(board.move_stack)
        if not move_stack:
            hint = self._font.render("No moves yet", True, GRAY)
            surface.blit(hint, (PANEL_X + 10, self._top + 10))
            return

        # Build move-pair list
        temp = chess.Board()
        pairs = []
        for i, move in enumerate(move_stack):
            san = temp.san(move)
            if i % 2 == 0:
                pairs.append(f"{i // 2 + 1}. {san}")
            else:
                pairs[-1] += f"   {san}"
            temp.push(move)

        total_h = len(pairs) * self._line_h
        max_scroll = max(0, total_h - self._visible_h + 20)
        self.scroll_offset = min(self.scroll_offset, max_scroll)

        # clip
        clip = pygame.Rect(PANEL_X, self._top + 6,
                           PANEL_WIDTH, self._visible_h - 10)
        old_clip = surface.get_clip()
        surface.set_clip(clip)

        y = self._top + 8 - self.scroll_offset
        for idx, line in enumerate(pairs):
            if y + self._line_h < self._top:
                y += self._line_h
                continue
            if y > self._bottom:
                break
            # highlight last move pair
            col = WHITE if idx == len(pairs) - 1 else t["panel_txt"]
            txt = self._font.render(line, True, col)
            surface.blit(txt, (PANEL_X + 10, y))
            y += self._line_h

        surface.set_clip(old_clip)

        # auto-scroll to bottom
        if total_h > self._visible_h - 20:
            self.scroll_offset = max_scroll

    def handle_scroll(self, dy):
        self.scroll_offset = max(0, self.scroll_offset - dy * 18)
