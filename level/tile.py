# durango_wildlands_clone/level/tile.py

import pygame
from config import TILE_SIZE, TILE_TYPE_WATER, TILE_TYPE_GRASS, TILE_TYPE_DIRT, \
                   TILE_TYPE_MOUNTAIN, TILE_TYPE_TREE_COLLIDABLE, TILE_TYPE_ROCK_COLLIDABLE, \
                   COLLISION_TILES

class Tile:
    def __init__(self, tile_id, x, y):
        self.id = tile_id
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.is_collidable = self.id in COLLISION_TILES # Check if its ID is in our collision set
        
        # Basic visual representation (can be replaced by actual sprites later)
        self.color = self._get_color_from_id(tile_id)

    def _get_color_from_id(self, tile_id):
        """Returns a color based on the tile ID for basic drawing."""
        if tile_id == TILE_TYPE_WATER:
            return (50, 50, 200)  # Blue
        elif tile_id == TILE_TYPE_GRASS:
            return (0, 150, 0)    # Green
        elif tile_id == TILE_TYPE_DIRT:
            return (139, 69, 19)  # Brown
        elif tile_id == TILE_TYPE_MOUNTAIN:
            return (100, 100, 100) # Dark Grey
        elif tile_id == TILE_TYPE_TREE_COLLIDABLE:
            return (0, 100, 0) # Darker green for tree trunk
        elif tile_id == TILE_TYPE_ROCK_COLLIDABLE:
            return (80, 80, 80) # Grey for rock
        else:
            return (200, 200, 200) # Default light grey

    def draw(self, surface, offset_x, offset_y, zoom_level):
        # Calculate scaled position and size
        scaled_x = int((self.rect.x - offset_x) * zoom_level)
        scaled_y = int((self.rect.y - offset_y) * zoom_level)
        scaled_size = int(TILE_SIZE * zoom_level)

        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_size, scaled_size)
        pygame.draw.rect(surface, self.color, scaled_rect)

        # Optional: Draw a black outline for visibility
        # pygame.draw.rect(surface, (0, 0, 0), scaled_rect, 1)