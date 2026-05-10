"""Generate chess-piece PNG images at first run.

Uses pygame drawing primitives to create clean, recognisable piece silhouettes
and saves them to assets/pieces/.  The game loads these PNGs at startup.
"""
import os
import math
import pygame
from constants import PIECES_DIR, SQUARE_SIZE

# Render at 2× then downscale for anti-aliased quality
_S = SQUARE_SIZE * 2  # 150
_PAD = 14             # padding inside cell


def _ensure_dir():
    os.makedirs(PIECES_DIR, exist_ok=True)


def _save(surf, name):
    """Down-scale to target size and save."""
    small = pygame.transform.smoothscale(surf, (SQUARE_SIZE, SQUARE_SIZE))
    pygame.image.save(small, os.path.join(PIECES_DIR, name))


# ═══════════════════════════════════════════════════════════════════
#  Drawing helpers  (all coords relative to _S × _S surface)
# ═══════════════════════════════════════════════════════════════════
def _base(surf, colour, outline):
    """Draw a standard piece base / pedestal."""
    cx = _S // 2
    by = _S - _PAD
    bw = int(_S * 0.52)
    bh = int(_S * 0.08)
    rect = pygame.Rect(cx - bw // 2, by - bh, bw, bh)
    pygame.draw.rect(surf, colour, rect, border_radius=4)
    pygame.draw.rect(surf, outline, rect, 2, border_radius=4)
    return by - bh  # top-of-base y


def _body(surf, colour, outline, top_y, top_w, base_y, base_w):
    """Trapezoidal body."""
    cx = _S // 2
    pts = [
        (cx - top_w // 2, top_y),
        (cx + top_w // 2, top_y),
        (cx + base_w // 2, base_y),
        (cx - base_w // 2, base_y),
    ]
    pygame.draw.polygon(surf, colour, pts)
    pygame.draw.polygon(surf, outline, pts, 2)
    return pts


# ═══════════════════════════════════════════════════════════════════
#  Individual piece drawers
# ═══════════════════════════════════════════════════════════════════
def _draw_pawn(surf, fill, outline):
    cx = _S // 2
    base_top = _base(surf, fill, outline)
    # body
    bw_top = int(_S * 0.18)
    bw_bot = int(_S * 0.32)
    body_top = int(_S * 0.42)
    _body(surf, fill, outline, body_top, bw_top, base_top, bw_bot)
    # head
    r = int(_S * 0.12)
    pygame.draw.circle(surf, fill, (cx, body_top - r + 4), r)
    pygame.draw.circle(surf, outline, (cx, body_top - r + 4), r, 2)


def _draw_rook(surf, fill, outline):
    cx = _S // 2
    base_top = _base(surf, fill, outline)
    bw = int(_S * 0.36)
    body_top = int(_S * 0.30)
    # main body
    rect = pygame.Rect(cx - bw // 2, body_top, bw, base_top - body_top)
    pygame.draw.rect(surf, fill, rect)
    pygame.draw.rect(surf, outline, rect, 2)
    # battlements
    merlon_w = bw // 5
    merlon_h = int(_S * 0.09)
    for i in range(3):
        mx = cx - bw // 2 + i * 2 * merlon_w
        mr = pygame.Rect(mx, body_top - merlon_h, merlon_w, merlon_h)
        pygame.draw.rect(surf, fill, mr)
        pygame.draw.rect(surf, outline, mr, 2)
    # top bar
    bar = pygame.Rect(cx - bw // 2, body_top - 2, bw, 4)
    pygame.draw.rect(surf, fill, bar)
    pygame.draw.rect(surf, outline, bar, 2)


def _draw_knight(surf, fill, outline):
    cx = _S // 2
    base_top = _base(surf, fill, outline)
    # horse head as polygon – right-facing profile
    pts = [
        (cx - 20, base_top),
        (cx - 26, base_top - 30),
        (cx - 24, base_top - 60),
        (cx - 16, base_top - 78),  # back of head
        (cx - 6,  base_top - 90),  # top of head
        (cx + 6,  base_top - 96),  # ear tip
        (cx + 14, base_top - 86),
        (cx + 18, base_top - 78),  # forehead
        (cx + 24, base_top - 62),  # nose bridge
        (cx + 28, base_top - 42),  # nose
        (cx + 22, base_top - 36),  # mouth
        (cx + 14, base_top - 38),  # chin
        (cx + 8,  base_top - 20),  # throat
        (cx + 20, base_top),
    ]
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, outline, pts, 2)
    # eye
    pygame.draw.circle(surf, outline, (cx + 4, base_top - 72), 3)


def _draw_bishop(surf, fill, outline):
    cx = _S // 2
    base_top = _base(surf, fill, outline)
    bw_top = int(_S * 0.12)
    bw_bot = int(_S * 0.34)
    body_top = int(_S * 0.28)
    _body(surf, fill, outline, body_top, bw_top, base_top, bw_bot)
    # mitre top
    r = int(_S * 0.10)
    pygame.draw.circle(surf, fill, (cx, body_top - r + 6), r)
    pygame.draw.circle(surf, outline, (cx, body_top - r + 6), r, 2)
    # cross/slit
    pygame.draw.line(surf, outline,
                     (cx - 6, body_top - r + 6 - 4),
                     (cx + 6, body_top - r + 6 + 8), 2)
    # small ball on top
    pygame.draw.circle(surf, fill, (cx, body_top - r - 4), 4)
    pygame.draw.circle(surf, outline, (cx, body_top - r - 4), 4, 2)


def _draw_queen(surf, fill, outline):
    cx = _S // 2
    base_top = _base(surf, fill, outline)
    bw_top = int(_S * 0.14)
    bw_bot = int(_S * 0.38)
    body_top = int(_S * 0.32)
    _body(surf, fill, outline, body_top, bw_top, base_top, bw_bot)
    # crown – 5 prongs
    crown_base = body_top
    crown_top = int(_S * 0.14)
    n_prongs = 5
    span = int(_S * 0.30)
    for i in range(n_prongs):
        px = cx - span // 2 + i * span // (n_prongs - 1)
        pygame.draw.line(surf, outline, (px, crown_base), (px, crown_top + i % 2 * 12), 2)
        pygame.draw.circle(surf, fill, (px, crown_top + i % 2 * 12 - 2), 5)
        pygame.draw.circle(surf, outline, (px, crown_top + i % 2 * 12 - 2), 5, 2)


def _draw_king(surf, fill, outline):
    cx = _S // 2
    base_top = _base(surf, fill, outline)
    bw_top = int(_S * 0.16)
    bw_bot = int(_S * 0.40)
    body_top = int(_S * 0.34)
    _body(surf, fill, outline, body_top, bw_top, base_top, bw_bot)
    # orb
    orb_r = int(_S * 0.07)
    orb_y = body_top - orb_r + 2
    pygame.draw.circle(surf, fill, (cx, orb_y), orb_r)
    pygame.draw.circle(surf, outline, (cx, orb_y), orb_r, 2)
    # cross
    cr_h = int(_S * 0.14)
    cr_w = int(_S * 0.10)
    cross_top = orb_y - orb_r - cr_h
    pygame.draw.line(surf, outline, (cx, cross_top), (cx, orb_y - orb_r + 2), 3)
    pygame.draw.line(surf, outline,
                     (cx - cr_w // 2, cross_top + cr_h // 3),
                     (cx + cr_w // 2, cross_top + cr_h // 3), 3)


# ═══════════════════════════════════════════════════════════════════
#  Colour palettes
# ═══════════════════════════════════════════════════════════════════
_WHITE_FILL    = (255, 250, 240)
_WHITE_OUTLINE = (60, 60, 60)
_BLACK_FILL    = (50, 50, 50)
_BLACK_OUTLINE = (20, 20, 20)

_DRAWERS = {
    "pawn":   _draw_pawn,
    "knight": _draw_knight,
    "bishop": _draw_bishop,
    "rook":   _draw_rook,
    "queen":  _draw_queen,
    "king":   _draw_king,
}


def generate_all_pieces():
    """Create all 12 piece PNGs if they don't already exist."""
    _ensure_dir()
    # Check whether generation is needed
    expected = [f"{c}_{p}.png" for c in ("white", "black") for p in _DRAWERS]
    if all(os.path.isfile(os.path.join(PIECES_DIR, f)) for f in expected):
        return  # already generated

    # Need a display surface for image.save – use a tiny hidden window
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_surface():
        try:
            pygame.display.set_mode((1, 1), pygame.HIDDEN)
        except Exception:
            pygame.display.set_mode((1, 1))

    for piece_name, draw_fn in _DRAWERS.items():
        for colour, fill, outline in [
            ("white", _WHITE_FILL, _WHITE_OUTLINE),
            ("black", _BLACK_FILL, _BLACK_OUTLINE),
        ]:
            surf = pygame.Surface((_S, _S), pygame.SRCALPHA)
            draw_fn(surf, fill, outline)
            _save(surf, f"{colour}_{piece_name}.png")
    print(f"[piece_generator] saved {len(expected)} piece images -> {PIECES_DIR}")
