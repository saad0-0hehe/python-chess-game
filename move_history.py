"""Move-history side panel – fixed-height scrollable box."""
import pygame
import chess
from constants import PANEL_X, PANEL_WIDTH, WINDOW_HEIGHT, WHITE, GRAY, LIGHT_GRAY
import theme as th

# ── Layout constants ────────────────────────────────────────────────
_BOX_TOP    = 490          # y where the scroll-box inner area starts
_BOX_HEIGHT = 190          # fixed height of the visible scroll area
_BOX_BOTTOM = _BOX_TOP + _BOX_HEIGHT
_TITLE_Y    = _BOX_TOP - 26   # y for the "Move History" title


class MoveHistory:
    def __init__(self):
        self._font       = pygame.font.SysFont("Consolas", 15)
        self._title_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.scroll_offset = 0
        self._line_h = 22
        self._prev_move_count = 0   # track moves to detect new ones

    def draw(self, surface, board: chess.Board):
        t = th.active_theme()

        # ── Outer box (fixed size, never grows) ──────────────────────
        box_rect = pygame.Rect(
            PANEL_X - 8,
            _TITLE_Y - 4,
            PANEL_WIDTH + 16,
            _BOX_HEIGHT + 36,          # title (26px) + 4px pad + scroll area
        )
        pygame.draw.rect(surface, t["panel_bg"], box_rect, border_radius=8)
        border_col = (*t["accent"], 80) if len(t["accent"]) == 3 else t["accent"]
        pygame.draw.rect(surface, border_col, box_rect, 1, border_radius=8)

        # ── Title ─────────────────────────────────────────────────────
        title = self._title_font.render("Move History", True, t["panel_txt"])
        surface.blit(title, (PANEL_X + 4, _TITLE_Y))

        # ── Divider under title ────────────────────────────────────────
        div_y = _BOX_TOP - 4
        pygame.draw.line(
            surface,
            (*t["accent"][:3], 60) if len(t["accent"]) >= 3 else GRAY,
            (PANEL_X - 4, div_y),
            (PANEL_X + PANEL_WIDTH + 4, div_y),
            1,
        )

        # ── No moves yet ──────────────────────────────────────────────
        move_stack = list(board.move_stack)
        if not move_stack:
            hint = self._font.render("No moves yet", True, GRAY)
            surface.blit(hint, (PANEL_X + 10, _BOX_TOP + 10))
            self._prev_move_count = 0
            return

        # ── Build move-pair list ───────────────────────────────────────
        temp  = chess.Board()
        pairs = []
        for i, move in enumerate(move_stack):
            san = temp.san(move)
            if i % 2 == 0:
                pairs.append(f"{i // 2 + 1}. {san}")
            else:
                pairs[-1] += f"   {san}"
            temp.push(move)

        total_h    = len(pairs) * self._line_h
        max_scroll = max(0, total_h - _BOX_HEIGHT + 8)

        # Auto-scroll to bottom only when a new move is added
        current_count = len(move_stack)
        if current_count != self._prev_move_count:
            self.scroll_offset = max_scroll
            self._prev_move_count = current_count

        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        # ── Clip to the scroll box ────────────────────────────────────
        clip    = pygame.Rect(PANEL_X, _BOX_TOP, PANEL_WIDTH, _BOX_HEIGHT)
        old_clip = surface.get_clip()
        surface.set_clip(clip)

        y = _BOX_TOP + 4 - self.scroll_offset
        for idx, line in enumerate(pairs):
            if y + self._line_h < _BOX_TOP:
                y += self._line_h
                continue
            if y > _BOX_BOTTOM:
                break
            col = WHITE if idx == len(pairs) - 1 else t["panel_txt"]
            txt = self._font.render(line, True, col)
            surface.blit(txt, (PANEL_X + 10, y))
            y += self._line_h

        surface.set_clip(old_clip)

        # ── Scrollbar track + thumb (if content overflows) ────────────
        if total_h > _BOX_HEIGHT:
            track_x   = PANEL_X + PANEL_WIDTH - 6
            track_rect = pygame.Rect(track_x, _BOX_TOP + 2, 4, _BOX_HEIGHT - 4)
            pygame.draw.rect(surface, (60, 62, 66), track_rect, border_radius=2)

            thumb_ratio = _BOX_HEIGHT / total_h
            thumb_h     = max(20, int((_BOX_HEIGHT - 4) * thumb_ratio))
            thumb_y     = _BOX_TOP + 2 + int(
                (self.scroll_offset / max_scroll) * (_BOX_HEIGHT - 4 - thumb_h)
            )
            thumb_rect  = pygame.Rect(track_x, thumb_y, 4, thumb_h)
            pygame.draw.rect(surface, (*t["accent"][:3], 160) if len(t["accent"]) >= 3
                             else LIGHT_GRAY, thumb_rect, border_radius=2)

    def handle_scroll(self, dy):
        """Mouse-wheel scroll (dy=+1 scroll up, dy=-1 scroll down)."""
        self.scroll_offset = max(0, self.scroll_offset - dy * 18)
