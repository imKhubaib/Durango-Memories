# durango_wildlands_clone/config.py

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FULLSCREEN = False # Set to True for fullscreen mode

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)        # Used for Player
GREEN = (0, 150, 0)      # Darker Green for Grass tiles
BLUE = (0, 0, 255)       # Used for Water tiles
LIGHT_GREY = (200, 200, 200) # Used for Dirt/Road tiles
DARK_GREY = (50, 50, 50)     # Used for Mountains/Rocks tiles and background fill

# Colors for UI elements
BUTTON_COLOR = (70, 70, 70)       # Dark grey for normal button state
BUTTON_HOVER_COLOR = (100, 100, 100) # Lighter grey for hover state
BUTTON_ACTIVE_COLOR = (120, 120, 120) # Even lighter for clicked state (optional, can use hover color)
TEXT_COLOR = WHITE                # White text on buttons

# Button dimensions and spacing
BUTTON_WIDTH = 180 # Reduced width for load screen buttons
BUTTON_HEIGHT = 40 # Reduced height for load screen buttons
BUTTON_SPACING = 10 # Reduced vertical space between buttons
BUTTON_FONT_SIZE = 30 # Slightly reduced font size for smaller buttons
TITLE_FONT_SIZE = 74 # Font size for the main title
SMALL_FONT_SIZE = 36 # Font size for smaller text (like "Press SPACE")

# Game settings
FPS = 60 # Frames per second

# Initial camera zoom level
# 1.0 is no zoom (original size)
# 0.5 would be zoomed out (half size)
# 2.0 would be zoomed in (double size)
INITIAL_ZOOM_LEVEL = 0.5

# Player settings
PLAYER_SPEED = 200 # Pixels per second
SPRINT_SPEED_MULTIPLIER = 2.0 # Player speed will be multiplied by this when sprinting

# Player start position (relative to screen, actual world position will be based on map)
# This is now a fallback; actual spawn point is determined by map generation for grass/dirt.
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT // 2

# Tile settings
TILE_SIZE = 64 # Size of each tile in pixels (e.g., 64x64)

# Impassable tile types (Water=0, Mountain=3)
IMPASSABLE_TILES = [0, 3] # Player cannot move onto these tile types

# Map Generation Settings (for pure Python blob-based noise)
MAP_WIDTH_TILES = 150  # Increased map size slightly for more land
MAP_HEIGHT_TILES = 150 # Increased map size slightly for more land

# Blob generation parameters (adjust these to change map appearance)
NUM_MOUNTAIN_BLOBS = int((MAP_WIDTH_TILES * MAP_HEIGHT_TILES) * 0.003)
MOUNTAIN_BLOB_RADIUS_MIN = 4
MOUNTAIN_BLOB_RADIUS_MAX = 12
MOUNTAIN_INTENSITY_THRESHOLD = 0.6

# Tuned parameters for water to create lakes/patches, not oceans
NUM_WATER_BLOBS = int((MAP_WIDTH_TILES * MAP_HEIGHT_TILES) * 0.0005) # Significantly fewer water blobs (0.05% of map tiles)
WATER_BLOB_RADIUS_MIN = 3 # Smaller minimum radius
WATER_BLOB_RADIUS_MAX = 8 # Smaller maximum radius
WATER_INTENSITY_THRESHOLD = 0.7 # Higher threshold means less water fills within a blob

DIRT_PLACEMENT_CHANCE_NEAR_FEATURE = 0.4

# Colors for UI elements
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
BUTTON_ACTIVE_COLOR = (120, 120, 120)
TEXT_COLOR = WHITE

# Input Box settings (New)
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