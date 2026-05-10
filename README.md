# Chess Master

A complete chess game built with **python-chess** and **pygame**.

## Features

- **Full chess rules** – castling, en passant, pawn promotion, check/checkmate/stalemate, 50-move rule, threefold repetition
- **10-minute chess timer** per player (PvP & PvAI)
- **Player vs Player** and **Player vs AI** modes
- **AI opponent** – minimax with alpha-beta pruning (depth 3)
- **Sound effects** – move, capture, check, checkmate, illegal move (procedurally generated)
- **Green board border** that turns **red** on check/checkmate
- **Game Over screen** with Try Again button
- **3 board themes** – Classic Wood, Dark Slate, Ice Blue
- **Move history** panel with scrolling
- **Captured pieces** display
- **Pawn promotion** dialog

## Screenshots

*(Run the game to see it in action!)*

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Click | Select / move pieces |
| ESC | Pause / resume |
| Ctrl+Z | Undo move |
| F | Flip board |

## Project Structure

```
chess_game/
├── main.py              # Entry point
├── game.py              # Core game loop, timers, state machine
├── board_renderer.py    # Board drawing with green/red border
├── menu.py              # Menu screens + game over overlay
├── ai_engine.py         # Minimax AI (threaded)
├── sound_manager.py     # Procedural sound generation
├── piece_generator.py   # Fallback piece image generator
├── promotion_dialog.py  # Pawn promotion popup
├── move_history.py      # Side panel move list
├── constants.py         # Shared constants
├── theme.py             # Board colour themes
├── requirements.txt     # chess, pygame
└── assets/pieces/       # Chess piece PNG images
```

## License

MIT
