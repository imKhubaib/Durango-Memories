# durango_wildlands_clone/main.py

import pygame
import sys # sys is generally good to have for clean exit, but not strictly required for this simple example

from game import Game # Import the Game class from game.py

if __name__ == '__main__':
    pygame.init() # Initialize all the Pygame modules
    
    game = Game() # Create an instance of your Game class
    game.run()    # Start the main game loop

    pygame.quit() # Uninitialize Pygame modules when the game loop ends
    sys.exit()    # Exit the Python program cleanly