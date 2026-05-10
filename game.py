"""Core game logic – state machine, move handling, AI coordination."""
import chess
import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PANEL_X, PANEL_WIDTH, PANEL_TOP,
    STATE_MENU, STATE_MODE_SELECT, STATE_SETTINGS,
    STATE_PLAYING, STATE_PAUSED, STATE_PROMOTION, STATE_GAME_OVER,
    WHITE, GRAY, LIGHT_GRAY, BORDER_NORMAL,
)
import theme as th
from board_renderer import BoardRenderer
from move_history import MoveHistory
from promotion_dialog import PromotionDialog
from ai_engine import ChessAI
from sound_manager import SoundManager
from menu import MainMenu, ModeSelectMenu, SettingsMenu, PauseMenu, GameOverScreen


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.tick = 0

        # sub-systems
        self.sound = SoundManager()
        self.renderer = BoardRenderer()
        self.history = MoveHistory()
        self.promo_dialog = PromotionDialog()
        self.ai = ChessAI(depth=3)

        # menus
        self.main_menu = MainMenu()
        self.mode_menu = ModeSelectMenu()
        self.settings_menu = SettingsMenu(self.sound)
        self.pause_menu = PauseMenu()
        self.game_over_screen = GameOverScreen()

        # game state
        self.state = STATE_MENU
        self.board = chess.Board()
        self.selected_sq = None
        self.legal_targets = []
        self.last_move = None
        self.mode = "pvp"          # "pvp" or "pvai"
        self.ai_colour = chess.BLACK
        self.flipped = False

        # promotion state
        self._promo_move_from = None
        self._promo_move_to = None
        self._promo_rects = []

        # game-over text
        self._result_text = ""
        self._detail_text = ""

        # fonts
        self._info_font = pygame.font.SysFont("Segoe UI", 17, bold=True)
        self._status_font = pygame.font.SysFont("Segoe UI", 15)
        self._thinking_font = pygame.font.SysFont("Segoe UI", 14, italic=True)
        self._captured_font = pygame.font.SysFont("Segoe UI Symbol", 22)

    # ═══════════════════════════════════════════════════════════════
    #  Main loop
    # ═══════════════════════════════════════════════════════════════
    def run(self):
        running = True
        while running:
            self.tick += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                    dy = 1 if event.button == 4 else -1
                    self.history.handle_scroll(dy)
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(60)

    # ═══════════════════════════════════════════════════════════════
    #  Update (AI polling, etc.)
    # ═══════════════════════════════════════════════════════════════
    def _update(self):
        if self.state != STATE_PLAYING:
            return
        if self.mode == "pvai" and self.board.turn == self.ai_colour:
            if not self.ai.thinking and not self.ai.result_move:
                self.ai.start_thinking(self.board)
            move = self.ai.poll()
            if move:
                self._execute_move(move)

    # ═══════════════════════════════════════════════════════════════
    #  Drawing
    # ═══════════════════════════════════════════════════════════════
    def _draw(self):
        t = th.active_theme()

        if self.state == STATE_MENU:
            self.main_menu.draw(self.screen, self.tick)
            return
        if self.state == STATE_MODE_SELECT:
            self.mode_menu.draw(self.screen, self.tick)
            return
        if self.state == STATE_SETTINGS:
            self.settings_menu.draw(self.screen, self.tick)
            return

        # ── Game screen background ────────────────────────────────
        self.screen.fill(t["bg"])

        # ── Board ─────────────────────────────────────────────────
        self.renderer.draw(self.screen, self.board,
                           selected_sq=self.selected_sq,
                           legal_targets=self.legal_targets,
                           last_move=self.last_move,
                           flipped=self.flipped)

        # ── Side panel ────────────────────────────────────────────
        self._draw_side_panel(t)

        # ── Move history ──────────────────────────────────────────
        self.history.draw(self.screen, self.board)

        # ── Overlays ──────────────────────────────────────────────
        if self.state == STATE_PROMOTION:
            colour = self.board.turn  # whose pawn is promoting
            self._promo_rects = self.promo_dialog.draw(self.screen, colour)

        if self.state == STATE_PAUSED:
            self.pause_menu.draw(self.screen)

        if self.state == STATE_GAME_OVER:
            self.game_over_screen.draw(self.screen,
                                       self._result_text,
                                       self._detail_text,
                                       self.tick)

    def _draw_side_panel(self, t):
        """Turn indicator, captured pieces, status."""
        x = PANEL_X
        y = PANEL_TOP

        # Turn indicator
        turn_text = "White to move" if self.board.turn == chess.WHITE else "Black to move"
        dot_col = (240, 240, 230) if self.board.turn == chess.WHITE else (50, 50, 50)
        pygame.draw.circle(self.screen, dot_col, (x + 10, y + 12), 8)
        pygame.draw.circle(self.screen, GRAY, (x + 10, y + 12), 8, 1)
        lbl = self._info_font.render(turn_text, True, t["panel_txt"])
        self.screen.blit(lbl, (x + 26, y + 3))

        # Mode badge
        mode_txt = "PvP" if self.mode == "pvp" else "vs AI"
        badge = self._status_font.render(mode_txt, True, t["accent"])
        self.screen.blit(badge, (x + 26, y + 28))

        # AI thinking indicator
        if self.mode == "pvai" and self.ai.thinking:
            dots = "." * ((self.tick // 15) % 4)
            think = self._thinking_font.render(f"AI thinking{dots}", True, (180, 180, 100))
            self.screen.blit(think, (x + 26, y + 48))

        # Status line (check / draw claim)
        status = ""
        if self.board.is_check():
            status = "CHECK!"
        elif self.board.can_claim_draw():
            status = "Draw claimable"
        if status:
            st = self._info_font.render(status, True, (235, 80, 60))
            self.screen.blit(st, (x + 26, y + 68))

        # Captured pieces
        self._draw_captured(t, x, y + 96)

    def _draw_captured(self, t, x, y):
        """Show captured pieces for each side."""
        _SYMBOLS = {
            chess.PAWN: ("♙", "♟"), chess.KNIGHT: ("♘", "♞"),
            chess.BISHOP: ("♗", "♝"), chess.ROOK: ("♖", "♜"),
            chess.QUEEN: ("♕", "♛"), chess.KING: ("♔", "♚"),
        }
        white_captured = []
        black_captured = []
        # Determine captured by diffing from initial material
        initial = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2,
                   chess.ROOK: 2, chess.QUEEN: 1, chess.KING: 1}
        for colour in [chess.WHITE, chess.BLACK]:
            for pt in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
                count = len(self.board.pieces(pt, colour))
                diff = initial[pt] - count
                sym = _SYMBOLS[pt][0 if colour == chess.WHITE else 1]
                lst = black_captured if colour == chess.WHITE else white_captured
                lst.extend([sym] * diff)

        # White's captures (black pieces taken by white)
        lbl = self._status_font.render("White captured:", True, GRAY)
        self.screen.blit(lbl, (x, y))
        cap_str = " ".join(white_captured) if white_captured else "—"
        cap = self._captured_font.render(cap_str, True, (200, 200, 200))
        self.screen.blit(cap, (x, y + 20))

        # Black's captures
        lbl2 = self._status_font.render("Black captured:", True, GRAY)
        self.screen.blit(lbl2, (x, y + 52))
        cap_str2 = " ".join(black_captured) if black_captured else "—"
        cap2 = self._captured_font.render(cap_str2, True, (200, 200, 200))
        self.screen.blit(cap2, (x, y + 72))

    # ═══════════════════════════════════════════════════════════════
    #  Input handling
    # ═══════════════════════════════════════════════════════════════
    def _handle_click(self, pos):
        if self.state == STATE_MENU:
            result = self.main_menu.handle_click(pos)
            if result == "quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif result:
                self.sound.play_menu()
                self.state = result
            return

        if self.state == STATE_MODE_SELECT:
            result = self.mode_menu.handle_click(pos)
            if result in ("pvp", "pvai"):
                self.sound.play_menu()
                self.mode = result
                self._new_game()
            elif result:
                self.sound.play_menu()
                self.state = result
            return

        if self.state == STATE_SETTINGS:
            result = self.settings_menu.handle_click(pos)
            if result:
                self.sound.play_menu()
                if result == STATE_MENU:
                    self.state = STATE_MENU
            return

        if self.state == STATE_PAUSED:
            result = self.pause_menu.handle_click(pos)
            if result == STATE_PLAYING:
                self.state = STATE_PLAYING
            elif result == STATE_MODE_SELECT:
                self.state = STATE_MODE_SELECT
            elif result == STATE_MENU:
                self.state = STATE_MENU
            if result:
                self.sound.play_menu()
            return

        if self.state == STATE_GAME_OVER:
            result = self.game_over_screen.handle_click(pos)
            if result == "retry":
                self.sound.play_menu()
                self._new_game()
            elif result == STATE_MENU:
                self.sound.play_menu()
                self.state = STATE_MENU
            return

        if self.state == STATE_PROMOTION:
            choice = self.promo_dialog.handle_click(self._promo_rects, pos)
            if choice:
                move = chess.Move(self._promo_move_from,
                                  self._promo_move_to,
                                  promotion=choice)
                self.state = STATE_PLAYING
                self._execute_move(move)
            return

        if self.state == STATE_PLAYING:
            # skip clicks while AI is thinking
            if self.mode == "pvai" and self.board.turn == self.ai_colour:
                return
            sq = self.renderer.pixel_to_square(*pos, self.flipped)
            if sq is None:
                self.selected_sq = None
                self.legal_targets = []
                return
            self._board_click(sq)

    def _board_click(self, sq):
        """Handle a click on a board square."""
        if self.selected_sq is None:
            # Select a piece
            piece = self.board.piece_at(sq)
            if piece and piece.color == self.board.turn:
                self.selected_sq = sq
                self.legal_targets = [
                    m.to_square for m in self.board.legal_moves
                    if m.from_square == sq
                ]
                if not self.legal_targets:
                    self.selected_sq = None
        else:
            # Try to move
            if sq == self.selected_sq:
                # deselect
                self.selected_sq = None
                self.legal_targets = []
                return

            # Check for promotion
            piece = self.board.piece_at(self.selected_sq)
            if (piece and piece.piece_type == chess.PAWN and
                    chess.square_rank(sq) in (0, 7)):
                # Check this is actually a legal move target
                promo_move = chess.Move(self.selected_sq, sq, promotion=chess.QUEEN)
                if promo_move in self.board.legal_moves:
                    self._promo_move_from = self.selected_sq
                    self._promo_move_to = sq
                    self.state = STATE_PROMOTION
                    self.selected_sq = None
                    self.legal_targets = []
                    return

            move = chess.Move(self.selected_sq, sq)
            if move in self.board.legal_moves:
                self._execute_move(move)
            else:
                # Maybe clicked another own piece → reselect
                other = self.board.piece_at(sq)
                if other and other.color == self.board.turn:
                    self.selected_sq = sq
                    self.legal_targets = [
                        m.to_square for m in self.board.legal_moves
                        if m.from_square == sq
                    ]
                else:
                    self.sound.play_illegal()
                    self.selected_sq = None
                    self.legal_targets = []

    def _execute_move(self, move):
        """Push a move, play sounds, check for game end."""
        is_capture = self.board.is_capture(move)
        self.board.push(move)
        self.last_move = move
        self.selected_sq = None
        self.legal_targets = []

        # sounds
        if self.board.is_checkmate():
            self.sound.play_mate()
            self._end_game()
        elif self.board.is_check():
            self.sound.play_check()
        elif is_capture:
            self.sound.play_capture()
        else:
            self.sound.play_move()

        # check other game-end conditions
        if self.board.is_game_over() and self.state != STATE_GAME_OVER:
            self.sound.play_game_over()
            self._end_game()

    def _end_game(self):
        """Transition to game-over state."""
        self.state = STATE_GAME_OVER
        outcome = self.board.outcome()
        if outcome:
            if outcome.winner is None:
                self._result_text = "Draw!"
                term = str(outcome.termination).split(".")[-1].replace("_", " ").title()
                self._detail_text = term
            elif outcome.winner == chess.WHITE:
                self._result_text = "White Wins!"
                self._detail_text = "Checkmate" if self.board.is_checkmate() else "Game Over"
            else:
                self._result_text = "Black Wins!"
                self._detail_text = "Checkmate" if self.board.is_checkmate() else "Game Over"
        else:
            self._result_text = "Game Over"
            self._detail_text = ""

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            if self.state == STATE_PLAYING:
                self.state = STATE_PAUSED
            elif self.state == STATE_PAUSED:
                self.state = STATE_PLAYING
        elif key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self._undo()
        elif key == pygame.K_f:
            if self.state == STATE_PLAYING:
                self.flipped = not self.flipped

    def _undo(self):
        """Undo last move (or last two in PvAI)."""
        if self.state != STATE_PLAYING or not self.board.move_stack:
            return
        if self.mode == "pvai":
            # undo AI move + player move
            if len(self.board.move_stack) >= 2:
                self.board.pop()
                self.board.pop()
        else:
            self.board.pop()
        self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
        self.selected_sq = None
        self.legal_targets = []

    def _new_game(self):
        """Reset board and start playing."""
        self.board = chess.Board()
        self.selected_sq = None
        self.legal_targets = []
        self.last_move = None
        self.state = STATE_PLAYING
        self.ai.result_move = None
        self.ai.thinking = False
        self.history.scroll_offset = 0
