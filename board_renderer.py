"""Draws the chessboard, pieces, highlights, labels, and the green/red border."""
import os
import chess
import pygame
from constants import (
    SQUARE_SIZE, BOARD_SIZE, BOARD_BORDER, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    PIECES_DIR, HIGHLIGHT_SELECT, HIGHLIGHT_MOVE, HIGHLIGHT_LAST,
    HIGHLIGHT_CHECK, BORDER_NORMAL, BORDER_CHECK, WHITE, BLACK, GRAY,
)
import theme as th

# python-chess piece-type → filename fragment
_PIECE_NAMES = {
    chess.PAWN:   "pawn",
    chess.KNIGHT: "knight",
    chess.BISHOP: "bishop",
    chess.ROOK:   "rook",
    chess.QUEEN:  "queen",
    chess.KING:   "king",
}


class BoardRenderer:
    def __init__(self):
        self._piece_imgs = {}          # (color_bool, piece_type) → Surface
        self._load_piece_images()
        self._label_font = pygame.font.SysFont("Segoe UI", 14, bold=True)

    # ── image loading ──────────────────────────────────────────────
    def _load_piece_images(self):
        for pt, name in _PIECE_NAMES.items():
            for colour_bool, prefix in [(True, "white"), (False, "black")]:
                path = os.path.join(PIECES_DIR, f"{prefix}_{name}.png")
                if os.path.isfile(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (SQUARE_SIZE - 6, SQUARE_SIZE - 6))
                    self._piece_imgs[(colour_bool, pt)] = img

    # ── coordinate helpers ─────────────────────────────────────────
    def square_to_pixel(self, sq, flipped=False):
        """Return top-left pixel (x, y) for a python-chess square index."""
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        if flipped:
            col = 7 - file
            row = rank
        else:
            col = file
            row = 7 - rank
        x = BOARD_OFFSET_X + col * SQUARE_SIZE
        y = BOARD_OFFSET_Y + row * SQUARE_SIZE
        return x, y

    def pixel_to_square(self, mx, my, flipped=False):
        """Return python-chess square index or None."""
        col = (mx - BOARD_OFFSET_X) // SQUARE_SIZE
        row = (my - BOARD_OFFSET_Y) // SQUARE_SIZE
        if not (0 <= col < 8 and 0 <= row < 8):
            return None
        if flipped:
            file = 7 - col
            rank = row
        else:
            file = col
            rank = 7 - row
        return chess.square(file, rank)

    # ── drawing ────────────────────────────────────────────────────
    def draw(self, surface, board: chess.Board, *,
             selected_sq=None, legal_targets=None,
             last_move=None, flipped=False):
        """Draw the complete board with border, squares, pieces, highlights."""
        t = th.active_theme()
        in_check = board.is_check()
        is_mate = board.is_checkmate()

        # ── Green / Red border ─────────────────────────────────────
        if is_mate:
            border_col = BORDER_CHECK
        elif in_check:
            border_col = BORDER_CHECK
        else:
            border_col = BORDER_NORMAL

        border_rect = pygame.Rect(
            BOARD_OFFSET_X - BOARD_BORDER,
            BOARD_OFFSET_Y - BOARD_BORDER,
            BOARD_SIZE + BOARD_BORDER * 2,
            BOARD_SIZE + BOARD_BORDER * 2,
        )
        pygame.draw.rect(surface, border_col, border_rect, border_radius=3)

        # ── Squares ────────────────────────────────────────────────
        for sq in chess.SQUARES:
            x, y = self.square_to_pixel(sq, flipped)
            file = chess.square_file(sq)
            rank = chess.square_rank(sq)
            is_light = (file + rank) % 2 == 1
            colour = t["light_sq"] if is_light else t["dark_sq"]
            pygame.draw.rect(surface, colour,
                             (x, y, SQUARE_SIZE, SQUARE_SIZE))

        # ── Last-move highlight ────────────────────────────────────
        if last_move:
            for sq in (last_move.from_square, last_move.to_square):
                x, y = self.square_to_pixel(sq, flipped)
                hl = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                hl.fill(HIGHLIGHT_LAST)
                surface.blit(hl, (x, y))

        # ── Selected square ───────────────────────────────────────
        if selected_sq is not None:
            x, y = self.square_to_pixel(selected_sq, flipped)
            hl = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            hl.fill(HIGHLIGHT_SELECT)
            surface.blit(hl, (x, y))

        # ── Legal-move dots ────────────────────────────────────────
        if legal_targets:
            for sq in legal_targets:
                x, y = self.square_to_pixel(sq, flipped)
                cx = x + SQUARE_SIZE // 2
                cy = y + SQUARE_SIZE // 2
                dot = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                if board.piece_at(sq):  # capture: ring
                    pygame.draw.circle(dot, (*HIGHLIGHT_MOVE[:3], 120),
                                       (SQUARE_SIZE // 2, SQUARE_SIZE // 2),
                                       SQUARE_SIZE // 2, 5)
                else:  # quiet: dot
                    pygame.draw.circle(dot, HIGHLIGHT_MOVE,
                                       (SQUARE_SIZE // 2, SQUARE_SIZE // 2),
                                       SQUARE_SIZE // 7)
                surface.blit(dot, (x, y))

        # ── King in check ──────────────────────────────────────────
        if in_check:
            king_sq = board.king(board.turn)
            if king_sq is not None:
                kx, ky = self.square_to_pixel(king_sq, flipped)
                hl = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                hl.fill(HIGHLIGHT_CHECK)
                surface.blit(hl, (kx, ky))

        # ── Pieces ─────────────────────────────────────────────────
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece is None:
                continue
            key = (piece.color, piece.piece_type)
            img = self._piece_imgs.get(key)
            if img:
                x, y = self.square_to_pixel(sq, flipped)
                surface.blit(img, (x + 3, y + 3))

        # ── Coordinate labels ─────────────────────────────────────
        files = "abcdefgh"
        ranks = "12345678"
        if flipped:
            files = files[::-1]
            ranks = ranks[::-1]
        for i in range(8):
            # file labels (bottom)
            lbl = self._label_font.render(files[i], True, GRAY)
            lx = BOARD_OFFSET_X + i * SQUARE_SIZE + SQUARE_SIZE // 2 - lbl.get_width() // 2
            ly = BOARD_OFFSET_Y + BOARD_SIZE + 4
            surface.blit(lbl, (lx, ly))
            # rank labels (left)
            lbl = self._label_font.render(ranks[7 - i], True, GRAY)
            lx = BOARD_OFFSET_X - 16
            ly = BOARD_OFFSET_Y + i * SQUARE_SIZE + SQUARE_SIZE // 2 - lbl.get_height() // 2
            surface.blit(lbl, (lx, ly))
