"""Pawn-promotion popup dialog."""
import chess
import pygame
from constants import (SQUARE_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
                       BOARD_SIZE, WHITE, BLACK, GRAY, DARK_GRAY)
import os
from constants import PIECES_DIR


class PromotionDialog:
    """Overlay that lets the player pick a promotion piece."""

    CHOICES = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    _NAMES = {chess.QUEEN: "queen", chess.ROOK: "rook",
              chess.BISHOP: "bishop", chess.KNIGHT: "knight"}

    def __init__(self):
        self._font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self._imgs = {}
        self._load_images()

    def _load_images(self):
        for colour_bool, prefix in [(True, "white"), (False, "black")]:
            for pt, name in self._NAMES.items():
                path = os.path.join(PIECES_DIR, f"{prefix}_{name}.png")
                if os.path.isfile(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
                    self._imgs[(colour_bool, pt)] = img

    def draw(self, surface, colour_bool):
        """Draw the promotion dialog and return list of clickable rects."""
        # dark overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # dialog box
        dw = SQUARE_SIZE * 4 + 40
        dh = SQUARE_SIZE + 60
        dx = BOARD_OFFSET_X + (BOARD_SIZE - dw) // 2
        dy = BOARD_OFFSET_Y + (BOARD_SIZE - dh) // 2
        pygame.draw.rect(surface, (45, 45, 50), (dx, dy, dw, dh), border_radius=12)
        pygame.draw.rect(surface, (100, 200, 100), (dx, dy, dw, dh), 2, border_radius=12)

        # title
        title = self._font.render("Promote pawn to:", True, WHITE)
        surface.blit(title, (dx + dw // 2 - title.get_width() // 2, dy + 8))

        # piece options
        rects = []
        for i, pt in enumerate(self.CHOICES):
            rx = dx + 20 + i * (SQUARE_SIZE + 2)
            ry = dy + 34
            r = pygame.Rect(rx, ry, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, DARK_GRAY, r, border_radius=6)
            rects.append((r, pt))
            img = self._imgs.get((colour_bool, pt))
            if img:
                surface.blit(img, (rx + 5, ry + 5))

        return rects

    def handle_click(self, rects, pos):
        """Returns the chosen piece type, or None."""
        for r, pt in rects:
            if r.collidepoint(pos):
                return pt
        return None
