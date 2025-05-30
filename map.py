# durango_wildlands_clone/map.py

import pygame
import random

# Import necessary constants from config.py
from config import (
    TILE_SIZE, WHITE, GREEN, BLUE, LIGHT_GREY, DARK_GREY,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MAP_WIDTH_TILES, MAP_HEIGHT_TILES,
    NUM_MOUNTAIN_BLOBS, MOUNTAIN_BLOB_RADIUS_MIN, MOUNTAIN_BLOB_RADIUS_MAX, MOUNTAIN_INTENSITY_THRESHOLD,
    NUM_WATER_BLOBS, WATER_BLOB_RADIUS_MIN, WATER_BLOB_RADIUS_MAX, WATER_INTENSITY_THRESHOLD,
    DIRT_PLACEMENT_CHANCE_NEAR_FEATURE,
    IMPASSABLE_TILES # Import IMPASSABLE_TILES for collision detection
)

class Map:
    def __init__(self):
        """
        Initializes the map by generating its tile data using smoothed random noise.
        """
        self.tile_size = TILE_SIZE
        self.rows = MAP_HEIGHT_TILES
        self.cols = MAP_WIDTH_TILES
        # Map's total world dimensions (unscaled)
        self.width = self.cols * self.tile_size
        self.height = self.rows * self.tile_size

        # Define colors for different tile types based on their number
        self.tile_colors = {
            0: BLUE,         # 0 for Water
            1: GREEN,        # 1 for Grass (base terrain)
            2: LIGHT_GREY,   # 2 for Dirt
            3: DARK_GREY,    # 3 for Mountains/Rocks
        }

        # Generate the map data using the pure Python blob-based method
        self.data = self._generate_noise_map()

    def _generate_noise_map(self):
        """
        Generates a 2D map array using a blob-based procedural generation algorithm.
        This method uses pure Python random functions to create varied terrain.
        """
        # Initialize map with base terrain (e.g., all grass)
        map_data = [[1 for _ in range(self.cols)] for _ in range(self.rows)] # All grass (tile type 1)

        # Generate Mountains (tile type 3)
        for _ in range(NUM_MOUNTAIN_BLOBS):
            center_x = random.randint(0, self.cols - 1)
            center_y = random.randint(0, self.rows - 1)
            radius = random.randint(MOUNTAIN_BLOB_RADIUS_MIN, MOUNTAIN_BLOB_RADIUS_MAX)

            for r_offset in range(-radius, radius + 1):
                for c_offset in range(-radius, radius + 1):
                    dist_sq = r_offset**2 + c_offset**2
                    if dist_sq < radius**2: # Check if within the circular radius
                        nr, nc = center_y + r_offset, center_x + c_offset
                        # Ensure coordinates are within map bounds
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            intensity = 1 - (dist_sq / radius**2) # Higher intensity near center
                            if intensity > MOUNTAIN_INTENSITY_THRESHOLD:
                                map_data[nr][nc] = 3 # Assign Mountain tile

        # Generate Water bodies (tile type 0)
        for _ in range(NUM_WATER_BLOBS):
            center_x = random.randint(0, self.cols - 1)
            center_y = random.randint(0, self.rows - 1)
            radius = random.randint(WATER_BLOB_RADIUS_MIN, WATER_BLOB_RADIUS_MAX)

            for r_offset in range(-radius, radius + 1):
                for c_offset in range(-radius, radius + 1):
                    dist_sq = r_offset**2 + c_offset**2
                    if dist_sq < radius**2: # Check if within the circular radius
                        nr, nc = center_y + r_offset, center_x + c_offset
                        # Ensure coordinates are within map bounds
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            intensity = 1 - (dist_sq / radius**2)
                            if intensity > WATER_INTENSITY_THRESHOLD:
                                map_data[nr][nc] = 0 # Assign Water tile

        # Generate Dirt (tile type 2) around features (mountains/water) for transitions
        temp_map_data = [row[:] for row in map_data] # Create a copy for neighbor checks
        for row in range(self.rows):
            for col in range(self.cols):
                if temp_map_data[row][col] == 1: # If current tile is still Grass
                    is_near_feature = False
                    # Check 8 neighbors
                    for r_offset in range(-1, 2):
                        for c_offset in range(-1, 2):
                            if r_offset == 0 and c_offset == 0: # Skip the current tile itself
                                continue
                            nr, nc = row + r_offset, col + c_offset
                            if 0 <= nr < self.rows and 0 <= nc < self.cols: # Check neighbor bounds
                                if temp_map_data[nr][nc] in [0, 3]: # Is neighbor water (0) or mountain (3)?
                                    is_near_feature = True
                                    break
                        if is_near_feature:
                            break
                    if is_near_feature and random.random() < DIRT_PLACEMENT_CHANCE_NEAR_FEATURE:
                        map_data[row][col] = 2 # Change grass to dirt

        return map_data

    def get_tile_at(self, x, y):
        """
        Returns the tile type at specific world coordinates.

        Args:
            x (int): World X coordinate.
            y (int): World Y coordinate.

        Returns:
            int or None: The tile type number, or None if out of bounds.
        """
        # Convert world coordinates to tile grid coordinates
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)

        # Check if tile coordinates are within map bounds
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.data[row][col]
        return None # Return None if out of map bounds

    def can_move_to(self, target_x, target_y):
        """
        Checks if the player (a TILE_SIZE x TILE_SIZE square) can move to the given
        top-left world coordinates. This checks both map boundaries and impassable tile types
        for all four corners of the player's bounding box.

        Args:
            target_x (float): The target world X coordinate (top-left of player).
            target_y (float): The target world Y coordinate (top-left of player).

        Returns:
            bool: True if movement is allowed, False otherwise.
        """
        # Define the four corners of the player's bounding box relative to target_x, target_y
        corners = [
            (target_x, target_y),                               # Top-left
            (target_x + TILE_SIZE - 1, target_y),               # Top-right (-1 to ensure it's within the tile)
            (target_x, target_y + TILE_SIZE - 1),               # Bottom-left (-1 to ensure it's within the tile)
            (target_x + TILE_SIZE - 1, target_y + TILE_SIZE - 1) # Bottom-right (-1 to ensure it's within the tile)
        ]

        for cx, cy in corners:
            tile_type = self.get_tile_at(cx, cy)
            
            # If any corner is outside map bounds (tile_type is None) or on an impassable tile
            if tile_type is None or tile_type in IMPASSABLE_TILES:
                return False
        return True


    def draw(self, surface, camera_offset_x=0, camera_offset_y=0, zoom_level=1.0):
        """
        Draws the map onto the given surface, applying camera offset and zoom level.

        Args:
            surface (pygame.Surface): The surface to draw the map on (e.g., the screen).
            camera_offset_x (float): The X offset of the camera in world units.
            camera_offset_y (float): The Y offset of the camera in world units.
            zoom_level (float): The current zoom level.
        """
        scaled_tile_size = int(self.tile_size * zoom_level)

        # Calculate the visible area of the map in world units
        view_width_world = SCREEN_WIDTH / zoom_level
        view_height_world = SCREEN_HEIGHT / zoom_level

        # Calculate which tiles are visible on screen for optimized drawing (culling)
        # These calculations are in world tile coordinates
        start_col = max(0, int(camera_offset_x // self.tile_size))
        end_col = min(self.cols, int((camera_offset_x + view_width_world) // self.tile_size) + 1)
        start_row = max(0, int(camera_offset_y // self.tile_size))
        end_row = min(self.rows, int((camera_offset_y + view_height_world) // self.tile_size) + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_type = self.data[row][col]
                color = self.tile_colors.get(tile_type, WHITE)

                # Calculate screen position of the tile
                # Convert world coordinates (col * self.tile_size, row * self.tile_size)
                # to camera-relative coordinates, then scale to screen pixels.
                draw_x = (col * self.tile_size - camera_offset_x) * zoom_level
                draw_y = (row * self.tile_size - camera_offset_y) * zoom_level

                rect = pygame.Rect(draw_x, draw_y, scaled_tile_size, scaled_tile_size)
                pygame.draw.rect(surface, color, rect)