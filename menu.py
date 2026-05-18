"""Menu screens – Main (Title), Mode Select, Difficulty, Settings, Pause, Game Over."""
import pygame
import math
import random
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY,
    DARK_GRAY, BORDER_NORMAL, BORDER_CHECK,
    STATE_MENU, STATE_MODE_SELECT, STATE_SETTINGS,
    STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER,
    STATE_DIFFICULTY_SELECT,
)
import theme as th


# ═══════════════════════════════════════════════════════════════════
#  Reusable button
# ═══════════════════════════════════════════════════════════════════
class _Button:
    def __init__(self, text, x, y, w, h, font, *, colour=(70, 75, 80),
                 hover=(100, 170, 90), text_col=WHITE, icon=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.colour = colour
        self.hover = hover
        self.text_col = text_col
        self._font = font
        self._hovered = False
        self.icon = icon  # optional icon text

    def draw(self, surface, mx, my, tick=0):
        self._hovered = self.rect.collidepoint(mx, my)
        col = self.hover if self._hovered else self.colour

        # Subtle hover scale animation
        r = self.rect.copy()
        if self._hovered:
            grow = 3
            r.inflate_ip(grow * 2, grow)
            # Subtle glow behind button
            glow = pygame.Surface((r.w + 12, r.h + 12), pygame.SRCALPHA)
            glow_col = (*self.hover[:3], 40)
            pygame.draw.rect(glow, glow_col, glow.get_rect(), border_radius=14)
            surface.blit(glow, (r.x - 6, r.y - 6))

        pygame.draw.rect(surface, col, r, border_radius=10)
        # Subtle border gradient
        border_col = (255, 255, 255, 35) if not self._hovered else (255, 255, 255, 70)
        pygame.draw.rect(surface, border_col, r, 1, border_radius=10)

        # Render text
        lbl = self._font.render(self.text, True, self.text_col)
        tx = r.centerx - lbl.get_width() // 2
        ty = r.centery - lbl.get_height() // 2
        surface.blit(lbl, (tx, ty))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ═══════════════════════════════════════════════════════════════════
#  Floating chess piece for title background
# ═══════════════════════════════════════════════════════════════════
class _FloatingPiece:
    """A single floating chess unicode symbol that drifts across the screen."""
    SYMBOLS = ["♔", "♕", "♖", "♗", "♘", "♙", "♚", "♛", "♜", "♝", "♞", "♟"]

    def __init__(self):
        self.symbol = random.choice(self.SYMBOLS)
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(-80, WINDOW_HEIGHT + 80)
        self.size = random.randint(24, 56)
        self.alpha = random.randint(15, 45)
        self.speed_x = random.uniform(-0.3, 0.3)
        self.speed_y = random.uniform(-0.6, -0.15)
        self.wobble_phase = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.01, 0.03)
        self._font = pygame.font.SysFont("Segoe UI Symbol", self.size)

    def update(self):
        self.x += self.speed_x + math.sin(self.wobble_phase) * 0.3
        self.y += self.speed_y
        self.wobble_phase += self.wobble_speed
        # Respawn when off screen
        if self.y < -100:
            self.y = WINDOW_HEIGHT + random.randint(20, 80)
            self.x = random.randint(0, WINDOW_WIDTH)

    def draw(self, surface):
        txt = self._font.render(self.symbol, True, (255, 255, 255))
        alpha_surf = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(txt, (0, 0))
        alpha_surf.set_alpha(self.alpha)
        surface.blit(alpha_surf, (int(self.x), int(self.y)))


# ═══════════════════════════════════════════════════════════════════
#  Menu base
# ═══════════════════════════════════════════════════════════════════
class MenuBase:
    def __init__(self):
        self.btn_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.title_font = pygame.font.SysFont("Segoe UI", 52, bold=True)
        self.sub_font = pygame.font.SysFont("Segoe UI", 18)

    def _draw_bg(self, surface, t, tick):
        surface.fill(t["bg"])
        # subtle animated gradient overlay
        for i in range(0, WINDOW_HEIGHT, 4):
            alpha = int(8 + 6 * math.sin((i + tick * 0.4) / 80))
            bar = pygame.Surface((WINDOW_WIDTH, 4), pygame.SRCALPHA)
            bar.fill((255, 255, 255, alpha))
            surface.blit(bar, (0, i))


# ═══════════════════════════════════════════════════════════════════
#  Main Menu (Animated Title Screen)
# ═══════════════════════════════════════════════════════════════════
class MainMenu(MenuBase):
    def __init__(self):
        super().__init__()
        # Larger title fonts
        self._big_title_font = pygame.font.SysFont("Segoe UI", 62, bold=True)
        self._glow_font = pygame.font.SysFont("Segoe UI", 66, bold=True)
        self._subtitle_font = pygame.font.SysFont("Segoe UI", 16)
        self._version_font = pygame.font.SysFont("Segoe UI", 12)
        self._crown_font = pygame.font.SysFont("Segoe UI Symbol", 80)

        cx = WINDOW_WIDTH // 2
        bw, bh = 260, 52
        by = 400
        gap = 64
        self.btn_play = _Button("♟  New Game", cx - bw // 2, by, bw, bh, self.btn_font,
                                colour=(45, 80, 45), hover=(60, 140, 60))
        self.btn_settings = _Button("⚙  Settings", cx - bw // 2, by + gap, bw, bh, self.btn_font,
                                    colour=(55, 60, 70), hover=(80, 100, 130))
        self.btn_quit = _Button("✕  Quit", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
                                colour=(100, 40, 40), hover=(160, 50, 50))

        # Floating pieces for background
        self._floating_pieces = [_FloatingPiece() for _ in range(18)]
        self._fade_in = 0  # fade-in counter

    def draw(self, surface, tick):
        t = th.active_theme()

        # ── Background ──────────────────────────────────────────
        surface.fill((18, 18, 22))

        # Decorative chess board pattern (faded, offset, rotated feel)
        board_alpha = 12
        sq = 60
        for row in range(14):
            for col in range(20):
                if (row + col) % 2 == 0:
                    s = pygame.Surface((sq, sq), pygame.SRCALPHA)
                    s.fill((255, 255, 255, board_alpha))
                    surface.blit(s, (col * sq - 30, row * sq - 20))

        # Animated gradient sweep (diagonal)
        sweep_x = int((tick * 1.5) % (WINDOW_WIDTH + 400)) - 200
        grad_surf = pygame.Surface((200, WINDOW_HEIGHT), pygame.SRCALPHA)
        for i in range(200):
            alpha = int(12 * math.sin(i / 200 * math.pi))
            pygame.draw.line(grad_surf, (100, 200, 120, alpha), (i, 0), (i, WINDOW_HEIGHT))
        surface.blit(grad_surf, (sweep_x, 0))

        # ── Floating chess pieces ──────────────────────────────
        for fp in self._floating_pieces:
            fp.update()
            fp.draw(surface)

        # ── Crown / Chess piece hero icon ──────────────────────
        crown = self._crown_font.render("♚", True, BORDER_NORMAL)
        # Gentle bob
        bob = math.sin(tick * 0.03) * 6
        cx = WINDOW_WIDTH // 2
        crown_y = 100 + bob
        # Glow behind crown
        glow_r = 55 + int(8 * math.sin(tick * 0.05))
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (34, 139, 34, 30), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (cx - glow_r, int(crown_y + crown.get_height() // 2 - glow_r)))
        surface.blit(crown, (cx - crown.get_width() // 2, int(crown_y)))

        # ── Title text with glow effect ─────────────────────────
        title_y = 200
        # Outer glow (slightly larger, colored, low alpha)
        pulse = 0.5 + 0.5 * math.sin(tick * 0.04)
        glow_alpha = int(60 + 40 * pulse)
        glow_text = self._glow_font.render("Chess Master", True, BORDER_NORMAL)
        glow_s = pygame.Surface(glow_text.get_size(), pygame.SRCALPHA)
        glow_s.blit(glow_text, (0, 0))
        glow_s.set_alpha(glow_alpha)
        surface.blit(glow_s, (cx - glow_text.get_width() // 2 - 2, title_y - 2))

        # Main title
        title = self._big_title_font.render("Chess Master", True, (240, 245, 240))
        surface.blit(title, (cx - title.get_width() // 2, title_y))

        # Decorative line under title
        line_w = 200 + int(30 * math.sin(tick * 0.03))
        line_y = title_y + title.get_height() + 10
        pygame.draw.line(surface, (*BORDER_NORMAL, 150),
                         (cx - line_w // 2, line_y), (cx + line_w // 2, line_y), 2)

        # Subtitle
        sub = self._subtitle_font.render("A complete chess experience", True, (140, 145, 140))
        surface.blit(sub, (cx - sub.get_width() // 2, line_y + 12))

        # ── Buttons ─────────────────────────────────────────────
        mx, my = pygame.mouse.get_pos()
        # Fade in effect for buttons
        self._fade_in = min(255, self._fade_in + 6)
        btn_surf = pygame.Surface((WINDOW_WIDTH, 250), pygame.SRCALPHA)
        self.btn_play.draw(btn_surf, mx, my - 400, tick)
        self.btn_settings.draw(btn_surf, mx, my - 400, tick)
        self.btn_quit.draw(btn_surf, mx, my - 400, tick)
        btn_surf.set_alpha(self._fade_in)
        surface.blit(btn_surf, (0, 400))

        # Actually draw buttons on main surface too (for click detection)
        if self._fade_in >= 200:
            self.btn_play.draw(surface, mx, my, tick)
            self.btn_settings.draw(surface, mx, my, tick)
            self.btn_quit.draw(surface, mx, my, tick)

        # ── Version text ────────────────────────────────────────
        ver = self._version_font.render("v2.0  |  python-chess + pygame", True, (80, 80, 85))
        surface.blit(ver, (cx - ver.get_width() // 2, WINDOW_HEIGHT - 30))

    def handle_click(self, pos):
        if self.btn_play.clicked(pos):
            return STATE_MODE_SELECT
        if self.btn_settings.clicked(pos):
            return STATE_SETTINGS
        if self.btn_quit.clicked(pos):
            return "quit"
        return None


# ═══════════════════════════════════════════════════════════════════
#  Mode Select
# ═══════════════════════════════════════════════════════════════════
class ModeSelectMenu(MenuBase):
    def __init__(self):
        super().__init__()
        cx = WINDOW_WIDTH // 2
        bw, bh = 280, 52
        by = 320
        gap = 72
        self.btn_pvp = _Button("♟  Player vs Player", cx - bw // 2, by, bw, bh, self.btn_font,
                               colour=(55, 70, 55), hover=(70, 140, 70))
        self.btn_pvai = _Button("🤖  Player vs AI", cx - bw // 2, by + gap, bw, bh, self.btn_font,
                                colour=(55, 60, 75), hover=(70, 100, 160))
        self.btn_back = _Button("←  Back", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
                                colour=(90, 80, 80), hover=(130, 110, 110))

    def draw(self, surface, tick):
        t = th.active_theme()
        self._draw_bg(surface, t, tick)
        title = self.title_font.render("Choose Mode", True, t["panel_txt"])
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        mx, my = pygame.mouse.get_pos()
        self.btn_pvp.draw(surface, mx, my, tick)
        self.btn_pvai.draw(surface, mx, my, tick)
        self.btn_back.draw(surface, mx, my, tick)

    def handle_click(self, pos):
        if self.btn_pvp.clicked(pos):
            return "pvp"
        if self.btn_pvai.clicked(pos):
            return "pvai"
        if self.btn_back.clicked(pos):
            return STATE_MENU
        return None


# ═══════════════════════════════════════════════════════════════════
#  Difficulty Select (for AI mode)
# ═══════════════════════════════════════════════════════════════════
class DifficultyMenu(MenuBase):
    def __init__(self):
        super().__init__()
        self._desc_font = pygame.font.SysFont("Segoe UI", 14)
        cx = WINDOW_WIDTH // 2
        bw, bh = 280, 52
        by = 280
        gap = 80

        self.btn_easy = _Button("🟢  Easy", cx - bw // 2, by, bw, bh, self.btn_font,
                                colour=(40, 80, 40), hover=(60, 130, 60))
        self.btn_medium = _Button("🟡  Medium", cx - bw // 2, by + gap, bw, bh, self.btn_font,
                                  colour=(100, 85, 30), hover=(160, 140, 40))
        self.btn_hard = _Button("🔴  Hard", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
                                colour=(100, 35, 35), hover=(170, 50, 50))
        self.btn_back = _Button("←  Back", cx - bw // 2, by + gap * 3, bw, bh, self.btn_font,
                                colour=(90, 80, 80), hover=(130, 110, 110))

        # Difficulty descriptions
        self._descriptions = {
            "easy": "AI thinks 1 move ahead — great for beginners",
            "medium": "AI thinks 3 moves ahead — a fair challenge",
            "hard": "AI thinks 5 moves ahead — prepare yourself!",
        }

    def draw(self, surface, tick):
        t = th.active_theme()
        self._draw_bg(surface, t, tick)

        title = self.title_font.render("Select Difficulty", True, t["panel_txt"])
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 180))

        mx, my = pygame.mouse.get_pos()
        self.btn_easy.draw(surface, mx, my, tick)
        self.btn_medium.draw(surface, mx, my, tick)
        self.btn_hard.draw(surface, mx, my, tick)
        self.btn_back.draw(surface, mx, my, tick)

        # Show description for hovered button
        desc = None
        if self.btn_easy.rect.collidepoint(mx, my):
            desc = self._descriptions["easy"]
        elif self.btn_medium.rect.collidepoint(mx, my):
            desc = self._descriptions["medium"]
        elif self.btn_hard.rect.collidepoint(mx, my):
            desc = self._descriptions["hard"]

        if desc:
            dtxt = self._desc_font.render(desc, True, (160, 170, 160))
            surface.blit(dtxt, (WINDOW_WIDTH // 2 - dtxt.get_width() // 2,
                                self.btn_back.rect.bottom + 20))

    def handle_click(self, pos):
        if self.btn_easy.clicked(pos):
            return "easy"
        if self.btn_medium.clicked(pos):
            return "medium"
        if self.btn_hard.clicked(pos):
            return "hard"
        if self.btn_back.clicked(pos):
            return STATE_MODE_SELECT
        return None


# ═══════════════════════════════════════════════════════════════════
#  Settings
# ═══════════════════════════════════════════════════════════════════
class SettingsMenu(MenuBase):
    def __init__(self, sound_mgr):
        super().__init__()
        cx = WINDOW_WIDTH // 2
        bw, bh = 280, 48
        by = 280
        gap = 60
        self.btn_theme = _Button("", cx - bw // 2, by, bw, bh, self.btn_font)
        self.btn_sound = _Button("", cx - bw // 2, by + gap, bw, bh, self.btn_font)
        self.btn_music = _Button("", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font)
        self.btn_back = _Button("←  Back", cx - bw // 2, by + gap * 3, bw, bh, self.btn_font,
                                colour=(90, 80, 80), hover=(130, 110, 110))
        self.sound_mgr = sound_mgr

    def draw(self, surface, tick):
        t = th.active_theme()
        self._draw_bg(surface, t, tick)
        title = self.title_font.render("Settings", True, t["panel_txt"])
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 190))
        # update labels
        self.btn_theme.text = f"🎨  Theme: {th.active_name()}"
        self.btn_sound.text = f"🔊  Sound: {'ON' if self.sound_mgr.enabled else 'OFF'}"
        self.btn_music.text = f"🎵  Music: {'ON' if self.sound_mgr.music_enabled else 'OFF'}"
        mx, my = pygame.mouse.get_pos()
        self.btn_theme.draw(surface, mx, my, tick)
        self.btn_sound.draw(surface, mx, my, tick)
        self.btn_music.draw(surface, mx, my, tick)
        self.btn_back.draw(surface, mx, my, tick)

    def handle_click(self, pos):
        if self.btn_theme.clicked(pos):
            th.next_theme()
            return "changed"
        if self.btn_sound.clicked(pos):
            self.sound_mgr.toggle()
            return "changed"
        if self.btn_music.clicked(pos):
            self.sound_mgr.toggle_music()
            return "changed"
        if self.btn_back.clicked(pos):
            return STATE_MENU
        return None


# ═══════════════════════════════════════════════════════════════════
#  Pause Menu (in-game overlay)
# ═══════════════════════════════════════════════════════════════════
class PauseMenu(MenuBase):
    def __init__(self):
        super().__init__()
        cx = WINDOW_WIDTH // 2
        bw, bh = 240, 48
        by = 280
        gap = 62
        self.btn_resume = _Button("▶  Resume", cx - bw // 2, by, bw, bh, self.btn_font,
                                  colour=(45, 80, 45), hover=(60, 140, 60))
        self.btn_new = _Button("🔄  New Game", cx - bw // 2, by + gap, bw, bh, self.btn_font)
        self.btn_menu = _Button("🏠  Main Menu", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
                                colour=(120, 50, 50), hover=(180, 60, 60))

    def draw(self, surface):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        title = self.title_font.render("Paused", True, WHITE)
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 190))
        mx, my = pygame.mouse.get_pos()
        self.btn_resume.draw(surface, mx, my)
        self.btn_new.draw(surface, mx, my)
        self.btn_menu.draw(surface, mx, my)

    def handle_click(self, pos):
        if self.btn_resume.clicked(pos):
            return STATE_PLAYING
        if self.btn_new.clicked(pos):
            return STATE_MODE_SELECT
        if self.btn_menu.clicked(pos):
            return STATE_MENU
        return None


# ═══════════════════════════════════════════════════════════════════
#  Game Over screen
# ═══════════════════════════════════════════════════════════════════
class GameOverScreen(MenuBase):
    def __init__(self):
        super().__init__()
        self.result_font = pygame.font.SysFont("Segoe UI", 42, bold=True)
        self.detail_font = pygame.font.SysFont("Segoe UI", 22)
        cx = WINDOW_WIDTH // 2
        bw, bh = 240, 52
        by = 440
        gap = 66
        self.btn_retry = _Button("🔄  Try Again", cx - bw // 2, by, bw, bh, self.btn_font,
                                 colour=(34, 139, 34), hover=(50, 180, 50))
        self.btn_menu = _Button("🏠  Main Menu", cx - bw // 2, by + gap, bw, bh, self.btn_font,
                                colour=(90, 80, 80), hover=(130, 110, 110))

    def draw(self, surface, result_text, detail_text, tick):
        # dark overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # pulsing "GAME OVER" banner
        pulse = 1.0 + 0.04 * math.sin(tick * 0.06)
        go_font = pygame.font.SysFont("Segoe UI", int(54 * pulse), bold=True)
        go = go_font.render("Game Over", True, BORDER_CHECK)
        surface.blit(go, (WINDOW_WIDTH // 2 - go.get_width() // 2, 200))

        # result
        res = self.result_font.render(result_text, True, WHITE)
        surface.blit(res, (WINDOW_WIDTH // 2 - res.get_width() // 2, 290))

        # detail
        det = self.detail_font.render(detail_text, True, LIGHT_GRAY)
        surface.blit(det, (WINDOW_WIDTH // 2 - det.get_width() // 2, 360))

        mx, my = pygame.mouse.get_pos()
        self.btn_retry.draw(surface, mx, my, tick)
        self.btn_menu.draw(surface, mx, my, tick)

    def handle_click(self, pos):
        if self.btn_retry.clicked(pos):
            return "retry"
        if self.btn_menu.clicked(pos):
            return STATE_MENU
        return None
