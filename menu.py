"""Menu screens – Main, Mode Select, Settings, Pause, Game Over."""
import pygame
import math
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY,
    DARK_GRAY, BORDER_NORMAL, BORDER_CHECK,
    STATE_MENU, STATE_MODE_SELECT, STATE_SETTINGS,
    STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER,
)
import theme as th


# ═══════════════════════════════════════════════════════════════════
#  Reusable button
# ═══════════════════════════════════════════════════════════════════
class _Button:
    def __init__(self, text, x, y, w, h, font, *, colour=(70, 75, 80),
                 hover=(100, 170, 90), text_col=WHITE):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.colour = colour
        self.hover = hover
        self.text_col = text_col
        self._font = font
        self._hovered = False

    def draw(self, surface, mx, my):
        self._hovered = self.rect.collidepoint(mx, my)
        col = self.hover if self._hovered else self.colour
        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 200, 60), self.rect, 1, border_radius=10)
        lbl = self._font.render(self.text, True, self.text_col)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                           self.rect.centery - lbl.get_height() // 2))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


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
#  Main Menu
# ═══════════════════════════════════════════════════════════════════
class MainMenu(MenuBase):
    def __init__(self):
        super().__init__()
        cx = WINDOW_WIDTH // 2
        bw, bh = 260, 52
        by = 340
        gap = 68
        self.btn_play = _Button("New Game", cx - bw // 2, by, bw, bh, self.btn_font)
        self.btn_settings = _Button("Settings", cx - bw // 2, by + gap, bw, bh, self.btn_font)
        self.btn_quit = _Button("Quit", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
                                colour=(120, 50, 50), hover=(180, 60, 60))

    def draw(self, surface, tick):
        t = th.active_theme()
        self._draw_bg(surface, t, tick)
        # title
        title = self.title_font.render("♚ Chess Master", True, BORDER_NORMAL)
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 180))
        sub = self.sub_font.render("A complete chess experience", True, GRAY)
        surface.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 260))
        mx, my = pygame.mouse.get_pos()
        self.btn_play.draw(surface, mx, my)
        self.btn_settings.draw(surface, mx, my)
        self.btn_quit.draw(surface, mx, my)

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
        self.btn_pvp = _Button("Player vs Player", cx - bw // 2, by, bw, bh, self.btn_font)
        self.btn_pvai = _Button("Player vs AI", cx - bw // 2, by + gap, bw, bh, self.btn_font)
        self.btn_back = _Button("← Back", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
                                colour=(90, 80, 80), hover=(130, 110, 110))

    def draw(self, surface, tick):
        t = th.active_theme()
        self._draw_bg(surface, t, tick)
        title = self.title_font.render("Choose Mode", True, t["panel_txt"])
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        mx, my = pygame.mouse.get_pos()
        self.btn_pvp.draw(surface, mx, my)
        self.btn_pvai.draw(surface, mx, my)
        self.btn_back.draw(surface, mx, my)

    def handle_click(self, pos):
        if self.btn_pvp.clicked(pos):
            return "pvp"
        if self.btn_pvai.clicked(pos):
            return "pvai"
        if self.btn_back.clicked(pos):
            return STATE_MENU
        return None


# ═══════════════════════════════════════════════════════════════════
#  Settings
# ═══════════════════════════════════════════════════════════════════
class SettingsMenu(MenuBase):
    def __init__(self, sound_mgr):
        super().__init__()
        cx = WINDOW_WIDTH // 2
        bw, bh = 280, 48
        by = 300
        gap = 64
        self.btn_theme = _Button("", cx - bw // 2, by, bw, bh, self.btn_font)
        self.btn_sound = _Button("", cx - bw // 2, by + gap, bw, bh, self.btn_font)
        self.btn_back = _Button("← Back", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
                                colour=(90, 80, 80), hover=(130, 110, 110))
        self.sound_mgr = sound_mgr

    def draw(self, surface, tick):
        t = th.active_theme()
        self._draw_bg(surface, t, tick)
        title = self.title_font.render("Settings", True, t["panel_txt"])
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 190))
        # update labels
        self.btn_theme.text = f"Theme: {th.active_name()}"
        self.btn_sound.text = f"Sound: {'ON' if self.sound_mgr.enabled else 'OFF'}"
        mx, my = pygame.mouse.get_pos()
        self.btn_theme.draw(surface, mx, my)
        self.btn_sound.draw(surface, mx, my)
        self.btn_back.draw(surface, mx, my)

    def handle_click(self, pos):
        if self.btn_theme.clicked(pos):
            th.next_theme()
            return "changed"
        if self.btn_sound.clicked(pos):
            self.sound_mgr.toggle()
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
        self.btn_resume = _Button("Resume", cx - bw // 2, by, bw, bh, self.btn_font)
        self.btn_new = _Button("New Game", cx - bw // 2, by + gap, bw, bh, self.btn_font)
        self.btn_menu = _Button("Main Menu", cx - bw // 2, by + gap * 2, bw, bh, self.btn_font,
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
        self.btn_retry = _Button("Try Again", cx - bw // 2, by, bw, bh, self.btn_font,
                                 colour=(34, 139, 34), hover=(50, 180, 50))
        self.btn_menu = _Button("Main Menu", cx - bw // 2, by + gap, bw, bh, self.btn_font,
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
        self.btn_retry.draw(surface, mx, my)
        self.btn_menu.draw(surface, mx, my)

    def handle_click(self, pos):
        if self.btn_retry.clicked(pos):
            return "retry"
        if self.btn_menu.clicked(pos):
            return STATE_MENU
        return None
