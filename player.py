# durango_wildlands_clone/player.py

import pygame
# Import SPRINT_SPEED_MULTIPLIER from config
from config import PLAYER_SPEED, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, RED, SPRINT_SPEED_MULTIPLIER

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """
        Initializes the Player sprite.

        Args:
            x (int): The initial X coordinate of the player.
            y (int): The initial Y coordinate of the player.
        """
        super().__init__() # Call the parent class (Sprite) constructor

        # Player visual representation
        # Store the original (unscaled) image.
        self.original_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.original_image.fill(RED)

        # 'self.image' is the currently scaled image, which will be updated in game.py's draw loop.
        self.image = self.original_image

        self.rect = self.image.get_rect(topleft=(x, y)) # Player's world position

        # Player attributes
        self.speed = PLAYER_SPEED
        self.direction = pygame.math.Vector2() # For movement vector
        self.is_sprinting = False # Flag to track if player is sprinting

    def get_input(self):
        """Handles keyboard input for player movement and sprinting."""
        keys = pygame.key.get_pressed()

        self.direction.x = 0
        self.direction.y = 0

        # Horizontal movement
        if keys[pygame.K_a]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1

        # Vertical movement
        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1

        # Check for sprint input (Left Shift key)
        if keys[pygame.K_LSHIFT]:
            self.is_sprinting = True
        else:
            self.is_sprinting = False

        # Normalize diagonal movement: prevents faster diagonal movement
        if self.direction.length() > 0:
            self.direction.normalize_ip() # In-place normalization

    def update(self, dt, game_map):
        """
        Updates the player's position based on input, sprint status, and delta time,
        with collision detection against map tiles and boundaries.

        Args:
            dt (float): Delta time, the time elapsed since the last frame in seconds.
            game_map (Map): The game's map object for collision checks.
        """
        self.get_input()

        current_speed = self.speed
        if self.is_sprinting:
            current_speed *= SPRINT_SPEED_MULTIPLIER

        # Store current position for collision rollback
        old_x, old_y = self.rect.x, self.rect.y

        # Calculate potential new positions
        new_x = self.rect.x + self.direction.x * current_speed * dt
        new_y = self.rect.y + self.direction.y * current_speed * dt

        # Apply X movement with collision check
        # Only attempt to move if there's horizontal input
        if self.direction.x != 0:
            # Check if moving horizontally would result in collision
            if game_map.can_move_to(new_x, self.rect.y):
                self.rect.x = new_x
            else:
                # If collision, try to align to the edge of the passable tile
                # This gives a basic "slide" along walls.
                if self.direction.x > 0: # Moving right
                    # Align to the left edge of the tile the player is trying to enter
                    self.rect.right = (self.rect.x // game_map.tile_size) * game_map.tile_size + game_map.tile_size - 1
                else: # Moving left
                    # Align to the right edge of the tile the player is trying to enter
                    self.rect.left = (self.rect.x // game_map.tile_size) * game_map.tile_size + game_map.tile_size

        # Apply Y movement with collision check
        # Only attempt to move if there's vertical input
        if self.direction.y != 0:
            # Check if moving vertically would result in collision
            if game_map.can_move_to(self.rect.x, new_y):
                self.rect.y = new_y
            else:
                # If collision, try to align to the edge of the passable tile
                if self.direction.y > 0: # Moving down
                    # Align to the top edge of the tile the player is trying to enter
                    self.rect.bottom = (self.rect.y // game_map.tile_size) * game_map.tile_size + game_map.tile_size - 1
                else: # Moving up
                    # Align to the bottom edge of the tile the player is trying to enter
                    self.rect.top = (self.rect.y // game_map.tile_size) * game_map.tile_size + game_map.tile_size

        # Map Boundary Clamping (after potential movement and tile collision)
        # Ensure player stays within the absolute map boundaries
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(game_map.width, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(game_map.height, self.rect.bottom)