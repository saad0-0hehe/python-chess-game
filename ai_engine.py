"""Minimax AI with alpha-beta pruning (runs in a background thread)."""
import chess
import random
import threading


# ── Piece values ────────────────────────────────────────────────────
PIECE_VAL = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000,
}

# ── Piece-square tables (from White's perspective, index 0 = a1) ──
_PST_PAWN = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

_PST_KNIGHT = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

_PST_BISHOP = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5,  5,  5,  5,  5,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

_PST_ROOK = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

_PST_QUEEN = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

_PST_KING_MID = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

_PST = {
    chess.PAWN: _PST_PAWN, chess.KNIGHT: _PST_KNIGHT,
    chess.BISHOP: _PST_BISHOP, chess.ROOK: _PST_ROOK,
    chess.QUEEN: _PST_QUEEN, chess.KING: _PST_KING_MID,
}


def _evaluate(board: chess.Board) -> float:
    """Static evaluation – positive favours White."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        val = PIECE_VAL[piece.piece_type]
        pst = _PST[piece.piece_type]
        if piece.color == chess.WHITE:
            score += val + pst[sq]
        else:
            score -= val + pst[chess.square_mirror(sq)]
    return score


def _order_moves(board: chess.Board):
    """Simple move ordering – captures & checks first."""
    moves = list(board.legal_moves)
    def key(m):
        s = 0
        if board.is_capture(m):
            s += 1000
        if board.gives_check(m):
            s += 500
        return -s
    moves.sort(key=key)
    return moves


def _minimax(board, depth, alpha, beta, maximising):
    if depth == 0 or board.is_game_over():
        return _evaluate(board), None

    best_move = None
    if maximising:
        max_eval = -float("inf")
        for move in _order_moves(board):
            board.push(move)
            val, _ = _minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if val > max_eval:
                max_eval = val
                best_move = move
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for move in _order_moves(board):
            board.push(move)
            val, _ = _minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if val < min_eval:
                min_eval = val
                best_move = move
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_eval, best_move


class ChessAI:
    """Threaded AI that computes a move without freezing the GUI."""

    def __init__(self, depth=3):
        self.depth = depth
        self._thread = None
        self.result_move = None
        self.thinking = False

    def start_thinking(self, board: chess.Board):
        if self.thinking:
            return
        self.thinking = True
        self.result_move = None
        board_copy = board.copy()
        self._thread = threading.Thread(target=self._run, args=(board_copy,), daemon=True)
        self._thread.start()

    def _run(self, board):
        maximising = board.turn == chess.WHITE
        _, move = _minimax(board, self.depth, -float("inf"), float("inf"), maximising)
        if move is None:
            moves = list(board.legal_moves)
            move = random.choice(moves) if moves else None
        self.result_move = move
        self.thinking = False

    def poll(self):
        """Returns the computed move or None if still thinking."""
        if not self.thinking and self.result_move:
            m = self.result_move
            self.result_move = None
            return m
        return None
