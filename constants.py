"""Shared constants for the chess game."""
import os

# ── Window ──────────────────────────────────────────────────────────
WINDOW_WIDTH  = 1080
WINDOW_HEIGHT = 720
FPS = 60
TITLE = "Chess Master"

# ── Board geometry ──────────────────────────────────────────────────
SQUARE_SIZE = 75
BOARD_SQUARES = 8
BOARD_SIZE = SQUARE_SIZE * BOARD_SQUARES          # 600
BOARD_BORDER = 6
LABEL_MARGIN = 22
BOARD_OFFSET_X = LABEL_MARGIN + BOARD_BORDER
BOARD_OFFSET_Y = 55 + BOARD_BORDER

# ── Side panel ──────────────────────────────────────────────────────
PANEL_X = BOARD_OFFSET_X + BOARD_SIZE + BOARD_BORDER + 30
PANEL_WIDTH = WINDOW_WIDTH - PANEL_X - 15
PANEL_TOP = 15

# ── Colours ─────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
GRAY        = (128, 128, 128)
LIGHT_GRAY  = (200, 200, 200)
DARK_GRAY   = (60, 60, 60)

BORDER_NORMAL = (34, 139, 34)       # Forest-green
BORDER_CHECK  = (220, 20, 60)       # Crimson-red
BORDER_MATE   = (180, 0, 0)

HIGHLIGHT_SELECT = (106, 135, 77, 160)
HIGHLIGHT_MOVE   = (130, 170, 100, 140)
HIGHLIGHT_LAST   = (205, 210, 106, 100)
HIGHLIGHT_CHECK  = (235, 67, 52, 150)

# ── Game states ─────────────────────────────────────────────────────
STATE_MENU        = "menu"
STATE_MODE_SELECT = "mode_select"
STATE_SETTINGS    = "settings"
STATE_PLAYING     = "playing"
STATE_PAUSED      = "paused"
STATE_PROMOTION   = "promotion"
STATE_GAME_OVER   = "game_over"

# ── Paths ───────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PIECES_DIR = os.path.join(ASSETS_DIR, "pieces")
