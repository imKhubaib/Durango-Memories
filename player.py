# durango_wildlands_clone/player.py

import pygame
from config import PLAYER_SIZE, PLAYER_COLOR, PLAYER_SPEED, TILE_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Store original_image for scaling with zoom
        self.original_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.original_image, PLAYER_COLOR, (PLAYER_SIZE // 2, PLAYER_SIZE // 2), PLAYER_SIZE // 2)
        
        self.image = self.original_image # This will be updated by game.py for scaling
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = PLAYER_SPEED
        self.dx = 0 # Change in x
        self.dy = 0 # Change in y

    def update(self, dt, game_map):
        """Updates the player's position and handles input and collision."""
        self._get_input()

        # Store current position before moving
        old_x, old_y = self.rect.x, self.rect.y

        # Apply movement
        self.rect.x += self.dx * self.speed * dt
        self.rect.y += self.dy * self.speed * dt

        # Collision handling for X-axis
        if self.dx != 0:
            self._handle_collision_x(game_map, old_x)

        # Collision handling for Y-axis
        if self.dy != 0:
            self._handle_collision_y(game_map, old_y)

        # Ensure player stays within map bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(game_map.width, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(game_map.height, self.rect.bottom)


    def _get_input(self):
        """Handles player input for movement."""
        self.dx = 0
        self.dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.dy = -1
        if keys[pygame.K_s]:
            self.dy = 1
        if keys[pygame.K_a]:
            self.dx = -1
        if keys[pygame.K_d]:
            self.dx = 1

        # Normalize diagonal movement (optional, but good practice)
        if self.dx != 0 and self.dy != 0:
            # Using 0.707 (1/sqrt(2)) for diagonal speed
            self.dx *= 0.707
            self.dy *= 0.707

    def _handle_collision_x(self, game_map, old_x):
        """Handles horizontal collisions with map tiles."""
        # Get tiles player is currently overlapping or about to overlap horizontally
        # Check all four corners (or more points for better precision)
        
        # Determine affected columns based on player movement
        start_col = int(self.rect.left // TILE_SIZE)
        end_col = int(self.rect.right // TILE_SIZE)
        start_row = int(self.rect.top // TILE_SIZE)
        end_row = int(self.rect.bottom // TILE_SIZE)

        # Iterate over potentially overlapping tiles
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                # Ensure tile coordinates are within map bounds
                if 0 <= row < game_map.rows and 0 <= col < game_map.cols:
                    tile = game_map.data[row][col]
                    if tile.is_collidable:
                        # Check for collision
                        if self.rect.colliderect(tile.rect):
                            # If collided horizontally, revert x position
                            self.rect.x = old_x
                            break # Stop checking horizontal tiles if a collision is found in this row
            else: # This 'else' belongs to the inner 'for' loop
                continue # Continue to the next row if no collision in current row
            break # Break from outer loop if a collision was found and X was reverted


    def _handle_collision_y(self, game_map, old_y):
        """Handles vertical collisions with map tiles."""
        # Similar logic to _handle_collision_x but for y-axis
        start_col = int(self.rect.left // TILE_SIZE)
        end_col = int(self.rect.right // TILE_SIZE)
        start_row = int(self.rect.top // TILE_SIZE)
        end_row = int(self.rect.bottom // TILE_SIZE)

        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                if 0 <= row < game_map.rows and 0 <= col < game_map.cols:
                    tile = game_map.data[row][col]
                    if tile.is_collidable:
                        if self.rect.colliderect(tile.rect):
                            self.rect.y = old_y
                            break # Stop checking vertical tiles if a collision is found in this col
            else:
                continue
            break