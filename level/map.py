# durango_wildlands_clone/level/map.py

import pygame
import random
from config import TILE_SIZE, MAP_WIDTH_TILES, MAP_HEIGHT_TILES, \
                   TILE_TYPE_WATER, TILE_TYPE_GRASS, TILE_TYPE_DIRT, \
                   TILE_TYPE_MOUNTAIN, TILE_TYPE_TREE_COLLIDABLE, TILE_TYPE_ROCK_COLLIDABLE
from level.tile import Tile # Import the Tile class

class Map:
    def __init__(self):
        self.rows = MAP_HEIGHT_TILES
        self.cols = MAP_WIDTH_TILES
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE
        self.data = self._generate_map() # This will now store Tile objects

    def _generate_map(self):
        """Generates a random map with different tile types and collidable objects."""
        # Simple random generation for now. Can be improved with noise, perlin, etc.
        map_data = []
        for r in range(self.rows):
            row_tiles = []
            for c in range(self.cols):
                tile_id = TILE_TYPE_GRASS # Default to grass

                rand_val = random.random()
                if rand_val < 0.1:  # 10% water
                    tile_id = TILE_TYPE_WATER
                elif rand_val < 0.2: # 10% dirt (grass + dirt = 80%)
                    tile_id = TILE_TYPE_DIRT
                elif rand_val < 0.25: # 5% mountains
                    tile_id = TILE_TYPE_MOUNTAIN
                elif rand_val < 0.30: # 5% trees
                    tile_id = TILE_TYPE_TREE_COLLIDABLE
                elif rand_val < 0.33: # 3% rocks
                    tile_id = TILE_TYPE_ROCK_COLLIDABLE

                # Create a Tile object for each grid cell
                tile = Tile(tile_id, c * TILE_SIZE, r * TILE_SIZE)
                row_tiles.append(tile)
            map_data.append(row_tiles)
        return map_data

    def get_tile_at_pixel(self, pixel_x, pixel_y):
        """Returns the Tile object at a given pixel coordinate."""
        col = int(pixel_x // TILE_SIZE)
        row = int(pixel_y // TILE_SIZE)

        # Ensure coordinates are within map bounds
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.data[row][col]
        return None # Return None if out of bounds

    def draw(self, surface, offset_x, offset_y, zoom_level):
        """Draws all tiles on the map, considering camera offset and zoom."""
        # Only draw tiles that are visible on screen to optimize
        screen_width_tiles = int(surface.get_width() / (TILE_SIZE * zoom_level)) + 2 # +2 for padding
        screen_height_tiles = int(surface.get_height() / (TILE_SIZE * zoom_level)) + 2

        start_col = max(0, int(offset_x / TILE_SIZE))
        end_col = min(self.cols, start_col + screen_width_tiles)
        start_row = max(0, int(offset_y / TILE_SIZE))
        end_row = min(self.rows, start_row + screen_height_tiles)

        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                tile = self.data[r][c]
                tile.draw(surface, offset_x, offset_y, zoom_level)