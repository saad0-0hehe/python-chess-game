"""Chess Master – entry point."""
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE

# Generate piece images on first run (before display is fully set up)
from piece_generator import generate_all_pieces


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)

    # Generate piece PNGs if they don't exist yet
    generate_all_pieces()

    # Import Game here so piece images are ready when BoardRenderer loads
    from game import Game
    game = Game(screen)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
