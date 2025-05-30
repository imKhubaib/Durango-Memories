# durango_wildlands_clone/config.py

import pygame

# Screen Dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GREY = (150, 150, 150)
DARK_GREY = (50, 50, 50)

# Game specific constants
INITIAL_ZOOM_LEVEL = 1.0 # 1.0 for no zoom
PLAYER_START_X = 200
PLAYER_START_Y = 200

# Tile properties
TILE_SIZE = 64 # Size of each tile in pixels (e.g., 64x64)

# Map Dimensions (in tiles)
MAP_WIDTH_TILES = 100
MAP_HEIGHT_TILES = 100

# Define Tile Types using numbers (Crucial for map generation and collision)
TILE_TYPE_WATER = 0  # Impassable
TILE_TYPE_GRASS = 1  # Walkable
TILE_TYPE_DIRT = 2   # Walkable
TILE_TYPE_MOUNTAIN = 3 # Impassable
TILE_TYPE_TREE_COLLIDABLE = 4 # Impassable
TILE_TYPE_ROCK_COLLIDABLE = 5 # Impassable


# Collision Properties
# A set of tile IDs that represent impassable terrain
COLLISION_TILES = {
    TILE_TYPE_WATER,
    TILE_TYPE_MOUNTAIN,
    TILE_TYPE_TREE_COLLIDABLE,
    TILE_TYPE_ROCK_COLLIDABLE
}


# Player settings
PLAYER_SIZE = 32
PLAYER_COLOR = (255, 0, 0) # Red
PLAYER_SPEED = 200 # Pixels per second

# Colors for UI elements
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
BUTTON_ACTIVE_COLOR = (120, 120, 120)
TEXT_COLOR = WHITE

# Input Box settings
INPUT_BOX_COLOR_INACTIVE = (100, 100, 100) # Grey
INPUT_BOX_COLOR_ACTIVE = (150, 150, 150)   # Lighter grey when typing
INPUT_BOX_TEXT_COLOR = BLACK                # Black text inside input box
INPUT_BOX_OUTLINE_COLOR = WHITE             # White border
INPUT_BOX_WIDTH = 300
INPUT_BOX_HEIGHT = 40
INPUT_BOX_FONT_SIZE = 30

# Button dimensions and spacing
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 40
BUTTON_SPACING = 10
BUTTON_FONT_SIZE = 30
TITLE_FONT_SIZE = 74
SMALL_FONT_SIZE = 36