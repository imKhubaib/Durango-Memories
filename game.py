# durango_wildlands_clone/game.py

import pygame
import sys
import random
import json
import os # New: For file operations like renaming and listing files
from enum import Enum
from config import * # Import all constants

# --- New: InputBox Class ---
class InputBox:
    def __init__(self, x, y, width, height, text='', font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = INPUT_BOX_COLOR_INACTIVE
        self.color_active = INPUT_BOX_COLOR_ACTIVE
        self.outline_color = INPUT_BOX_OUTLINE_COLOR
        self.text_color = INPUT_BOX_TEXT_COLOR
        self.text = text
        self.font = font if font else pygame.font.Font(None, INPUT_BOX_FONT_SIZE)
        self.active = False # Is this input box currently selected for typing?
        self.txt_surface = self.font.render(text, True, self.text_color)
        self.placeholder_text = "Enter filename..." # Default placeholder

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active state.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # When Enter is pressed, return the text
                    # This won't be handled directly by the InputBox, but by the game loop
                    pass 
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.text_color)

    def draw(self, surface):
        # Blit the text.
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(surface, self.outline_color, self.rect, 2) # Draw outline
        current_fill_color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, current_fill_color, self.rect)
        # Re-blit text after drawing fill to ensure it's on top
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

        # Placeholder text
        if not self.text and not self.active:
            placeholder_surface = self.font.render(self.placeholder_text, True, (150,150,150)) # Lighter grey
            surface.blit(placeholder_surface, (self.rect.x + 5, self.rect.y + 5))

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.txt_surface = self.font.render(self.text, True, self.text_color)

# --- End InputBox Class ---


# Define Game States (Updated)
class GameState(Enum):
    START_SCREEN = 1
    PLAYING = 2
    PAUSE_MENU = 3
    SLOT_SELECTION = 4
    INPUT_TEXT_PROMPT = 5 # New state for getting text input from user

class Game:
    def __init__(self):
        """Initializes the game, sets up the screen, and loads assets."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Durango Wildlands Clone")
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_state = GameState.START_SCREEN

        # Game components (initialized to None, will be set when playing or loading)
        self.map = None
        self.player = None

        # Camera settings
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.zoom_level = INITIAL_ZOOM_LEVEL

        # Fonts for UI text
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        self.input_font = pygame.font.Font(None, INPUT_BOX_FONT_SIZE) # New font for input box

        # --- Buttons for Start Screen (unchanged) ---
        self.start_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_SPACING,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Start Game", self._start_new_game
        )
        self.load_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Load Game", 
            action=lambda: self._enter_slot_selection(mode='load')
        )
        self.exit_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 + BUTTON_HEIGHT + BUTTON_SPACING,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Exit Game", self._exit_game
        )
        self.start_screen_buttons = [self.start_button, self.load_button, self.exit_button]

        # --- Buttons for Pause Menu (slightly changed for save action) ---
        self.resume_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 - (BUTTON_HEIGHT + BUTTON_SPACING) * 1.5,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Resume Game", self._resume_game
        )
        self.save_game_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 - (BUTTON_HEIGHT + BUTTON_SPACING) * 0.5,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Save Game", 
            action=lambda: self._prompt_save_filename() # New action to prompt filename
        )
        self.load_game_button_pause = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 + (BUTTON_HEIGHT + BUTTON_SPACING) * 0.5,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Load Game", 
            action=lambda: self._enter_slot_selection(mode='load')
        )
        self.exit_to_main_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 + (BUTTON_HEIGHT + BUTTON_SPACING) * 1.5,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Exit to Main Menu", self._exit_to_main_menu
        )
        self.pause_menu_buttons = [
            self.resume_button, self.save_game_button, 
            self.load_game_button_pause, self.exit_to_main_button
        ]

        # --- Dynamic Slot Selection Buttons ---
        self.slot_selection_buttons = []
        self.num_save_slots = 10
        self.slot_selection_mode = 'load' 

        # --- Input Box for file naming / renaming ---
        self.input_box_active = False # Controls if the input box is currently active
        self.current_input_box = None
        self.input_callback = None # Function to call when input is finished
        self.input_prompt_text = "" # Text displayed above the input box


    def _create_slot_selection_buttons(self, mode):
        """Helper to create buttons for each save/load slot based on the mode."""
        self.slot_selection_buttons = []
        self.slot_selection_mode = mode

        total_buttons_height = (self.num_save_slots + 1) * (BUTTON_HEIGHT + BUTTON_SPACING) - BUTTON_SPACING
        start_y = (SCREEN_HEIGHT - total_buttons_height) // 2

        # Get existing save files to display their actual names
        existing_saves = self._get_existing_save_files()

        for i in range(self.num_save_slots): # Loop from 0 to 9 for save file index
            slot_number = i + 1 # User-facing slot number 1-10
            
            # Determine button text: either "Empty Slot X" or actual filename
            current_filename = existing_saves.get(f'slot_{slot_number}', f"Empty Slot {slot_number}")
            button_text = f"Slot {slot_number}: {current_filename}" # Show actual filename

            button_y = start_y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
            
            action_func = None
            if mode == 'save':
                # When in save mode, clicking a slot saves to that slot (overwriting if exists)
                action_func = lambda slot_num=slot_number: self._prompt_save_filename_for_slot(slot_num)
            elif mode == 'load':
                # When in load mode, clicking a slot loads that slot
                action_func = lambda slot_num=slot_number: self._load_game_from_slot(slot_num)

            button = Button(
                (SCREEN_WIDTH - BUTTON_WIDTH * 1.5) // 2, # Make buttons a bit wider to fit filename
                button_y,
                int(BUTTON_WIDTH * 1.5), BUTTON_HEIGHT, button_text, # Adjust width
                action=action_func
            )
            self.slot_selection_buttons.append(button)

            # Add a Rename button next to each slot (if it's not empty)
            if existing_saves.get(f'slot_{slot_number}') != f"Empty Slot {slot_number}":
                 rename_button = Button(
                    button.rect.right + BUTTON_SPACING, # Position to the right of the slot button
                    button_y,
                    BUTTON_WIDTH // 2, BUTTON_HEIGHT, "Rename",
                    action=lambda slot_num=slot_number, old_name=current_filename: self._prompt_rename_filename(slot_num, old_name)
                )
                 self.slot_selection_buttons.append(rename_button)

        # Add Back button
        back_button_y = start_y + self.num_save_slots * (BUTTON_HEIGHT + BUTTON_SPACING)
        self.slot_selection_buttons.append(
            Button(
                (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
                back_button_y,
                BUTTON_WIDTH, BUTTON_HEIGHT, "Back", 
                action=self._return_from_slot_selection
            )
        )
        
    def _get_existing_save_files(self):
        """Returns a dictionary of existing save files mapped to their slot numbers."""
        saves = {}
        for i in range(1, self.num_save_slots + 1):
            filename_path = f'save_slot_{i}.json' # This is the internal fixed filename for the slot
            if os.path.exists(filename_path):
                try:
                    with open(filename_path, 'r') as f:
                        data = json.load(f)
                        # The actual user-given name is stored inside the save file
                        saves[f'slot_{i}'] = data.get('save_name', f"Unnamed Save {i}")
                except (json.JSONDecodeError, KeyError):
                    saves[f'slot_{i}'] = f"Corrupted Slot {i}"
            else:
                saves[f'slot_{i}'] = f"Empty Slot {i}" # Indicates no file for this slot
        return saves

    def _initialize_game_components(self):
        """Initializes map and player for a new game."""
        self.map = Map()

        valid_spawn_tiles = []
        for row in range(self.map.rows):
            for col in range(self.map.cols):
                tile_type = self.map.data[row][col]
                if tile_type == 1 or tile_type == 2: # Grass or Dirt
                    valid_spawn_tiles.append((col * TILE_SIZE, row * TILE_SIZE))

        spawn_x, spawn_y = PLAYER_START_X, PLAYER_START_Y
        if valid_spawn_tiles:
            spawn_x, spawn_y = random.choice(valid_spawn_tiles)
        else:
            print("Warning: No valid spawn tiles (Grass or Dirt) found on the map. Spawning at default location.")

        self.player = Player(spawn_x, spawn_y)

    # --- Button Action Methods ---
    def _start_new_game(self):
        self._initialize_game_components()
        self.game_state = GameState.PLAYING
        print("Starting New Game!")

    def _resume_game(self):
        self.game_state = GameState.PLAYING
        print("Resuming Game...")

    def _enter_slot_selection(self, mode):
        self._previous_game_state = self.game_state 
        self.game_state = GameState.SLOT_SELECTION
        self._create_slot_selection_buttons(mode) # Generate buttons based on mode
        print(f"Entering Slot Selection for {mode.upper()}...")

    def _return_from_slot_selection(self):
        self.game_state = self._previous_game_state 
        print("Returning from Slot Selection...")

    def _exit_to_main_menu(self):
        self.game_state = GameState.START_SCREEN
        self.map = None
        self.player = None
        print("Exiting to Main Menu...")

    def _exit_game(self):
        self.running = False
        print("Exiting Game...")

    # --- New Save/Load/Rename Logic ---
    def _prompt_save_filename(self):
        """Initiates the input prompt for a new save filename."""
        self._previous_game_state = self.game_state
        self.game_state = GameState.INPUT_TEXT_PROMPT
        self.input_prompt_text = "Enter save filename:"
        self.current_input_box = InputBox(
            (SCREEN_WIDTH - INPUT_BOX_WIDTH) // 2,
            SCREEN_HEIGHT // 2,
            INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT,
            text='MySaveGame', font=self.input_font # Default text
        )
        self.current_input_box.active = True
        self.input_callback = self._finalize_save_with_filename # Set callback for when input is done
        print("Prompting for save filename...")

    def _prompt_save_filename_for_slot(self, slot_number):
        """Initiates the input prompt for a filename when saving to a specific slot."""
        self._previous_game_state = self.game_state # This will be SLOT_SELECTION
        self.game_state = GameState.INPUT_TEXT_PROMPT
        self.input_prompt_text = f"Enter filename for Slot {slot_number}:"
        
        # Get existing name if available
        existing_saves = self._get_existing_save_files()
        current_name = existing_saves.get(f'slot_{slot_number}', 'NewSave')
        if current_name.startswith("Empty Slot") or current_name.startswith("Corrupted Slot"):
            current_name = "NewSave" # Default for empty/corrupted slots

        self.current_input_box = InputBox(
            (SCREEN_WIDTH - INPUT_BOX_WIDTH) // 2,
            SCREEN_HEIGHT // 2,
            INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT,
            text=current_name, font=self.input_font
        )
        self.current_input_box.active = True
        # Set callback with the specific slot number
        self.input_callback = lambda filename: self._finalize_save_with_filename_and_slot(filename, slot_number)
        print(f"Prompting for filename for slot {slot_number}...")

    def _prompt_rename_filename(self, slot_number, old_display_name):
        """Initiates the input prompt to rename a save file."""
        self._previous_game_state = self.game_state # This will be SLOT_SELECTION
        self.game_state = GameState.INPUT_TEXT_PROMPT
        self.input_prompt_text = f"Rename Slot {slot_number}: Enter new name"
        
        # Extract just the name, not "Slot X: " prefix
        initial_name = old_display_name.split(': ')[-1] if ': ' in old_display_name else old_display_name

        self.current_input_box = InputBox(
            (SCREEN_WIDTH - INPUT_BOX_WIDTH) // 2,
            SCREEN_HEIGHT // 2,
            INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT,
            text=initial_name, font=self.input_font
        )
        self.current_input_box.active = True
        # Set callback for renaming specific slot
        self.input_callback = lambda new_name: self._finalize_rename_filename(slot_number, new_name)
        print(f"Prompting to rename slot {slot_number}...")


    def _finalize_save_with_filename(self, filename):
        """Callback to save the game using the user-provided filename."""
        if not filename.strip(): # Check if filename is empty or just spaces
            print("Save cancelled: filename cannot be empty.")
            self.game_state = self._previous_game_state # Return to previous state
            return

        # Find the first empty slot to save to
        target_slot = -1
        for i in range(1, self.num_save_slots + 1):
            filename_path = f'save_slot_{i}.json'
            if not os.path.exists(filename_path):
                target_slot = i
                break
        
        if target_slot != -1:
            self._save_game_to_slot(target_slot, filename)
        else:
            print("All save slots are full! Cannot save new game without overwriting.")
            # Optionally, prompt to overwrite or go to slot selection
            self.game_state = self._previous_game_state # Return to previous state

    def _finalize_save_with_filename_and_slot(self, filename, slot_number):
        """Callback to save game to a specific slot with user-provided filename."""
        if not filename.strip():
            print("Save cancelled: filename cannot be empty.")
            self.game_state = self._previous_game_state
            return
        self._save_game_to_slot(slot_number, filename)


    def _finalize_rename_filename(self, slot_number, new_name):
        """Callback to rename a save file."""
        if not new_name.strip():
            print("Rename cancelled: new filename cannot be empty.")
            self.game_state = self._previous_game_state
            return

        filename_path = f'save_slot_{slot_number}.json'
        if os.path.exists(filename_path):
            try:
                with open(filename_path, 'r') as f:
                    save_data = json.load(f)
                save_data['save_name'] = new_name # Update the name inside the JSON
                with open(filename_path, 'w') as f:
                    json.dump(save_data, f, indent=4)
                print(f"Renamed slot {slot_number} to '{new_name}'")
                # Refresh slot selection buttons to show new name
                self._create_slot_selection_buttons(self.slot_selection_mode)
                self.game_state = self._previous_game_state # Go back to slot selection
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                print(f"Error renaming file for slot {slot_number}: {e}")
                self.game_state = self._previous_game_state
        else:
            print(f"Cannot rename: No save file found for slot {slot_number}.")
            self.game_state = self._previous_game_state


    def _save_game_to_slot(self, slot_number, filename_to_save_as):
        """Performs the actual saving of the game data to a specific slot."""
        if self.player is None or self.map is None:
            print("No game in progress to save!")
            self.game_state = self._previous_game_state # Return
            return

        save_data = {
            'player_x': self.player.rect.x,
            'player_y': self.player.rect.y,
            'map_data': self.map.data,
            'save_name': filename_to_save_as # Store the user-given name
        }
        
        # All saves will now be named save_slot_X.json internally, and display user name
        filename_path = f'save_slot_{slot_number}.json' 
        try:
            with open(filename_path, 'w') as f:
                json.dump(save_data, f, indent=4)
            print(f"Game saved successfully as '{filename_to_save_as}' to {filename_path}")
            self.game_state = self._previous_game_state # Return to previous state (e.g., PAUSE_MENU)
        except Exception as e:
            print(f"Error saving game: {e}")
            self.game_state = self._previous_game_state

    def _load_game_from_slot(self, slot_number):
        """Loads game state from a specific slot."""
        filename_path = f'save_slot_{slot_number}.json'
        try:
            with open(filename_path, 'r') as f:
                save_data = json.load(f)
            
            self.map = Map()
            self.map.data = save_data['map_data'] 

            self.player = Player(save_data['player_x'], save_data['player_y'])
            
            self.game_state = GameState.PLAYING
            print(f"Game loaded successfully from slot {slot_number} ('{save_data.get('save_name', 'Unnamed')}')")
        except FileNotFoundError:
            print(f"No save file found for slot {slot_number}.")
        except json.JSONDecodeError:
            print(f"Error reading save file {filename_path}. It might be corrupted.")
        except Exception as e:
            print(f"An unexpected error occurred while loading game from slot {slot_number}: {e}")
        finally:
            self.game_state = GameState.PLAYING # Always return to playing or handle error appropriately

    # --- End New Save/Load/Rename Logic ---


    def handle_events(self):
        """Handles Pygame events based on current game state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.game_state == GameState.START_SCREEN:
                for button in self.start_screen_buttons:
                    button.handle_event(event)
            elif self.game_state == GameState.PAUSE_MENU:
                for button in self.pause_menu_buttons:
                    button.handle_event(event)
            elif self.game_state == GameState.SLOT_SELECTION:
                for button in self.slot_selection_buttons:
                    button.handle_event(event)
            elif self.game_state == GameState.INPUT_TEXT_PROMPT:
                if self.current_input_box:
                    self.current_input_box.handle_event(event)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        # User pressed Enter, trigger the callback
                        if self.input_callback:
                            entered_text = self.current_input_box.get_text()
                            self.input_callback(entered_text)
                            self.current_input_box = None # Clear the input box
                            self.input_callback = None
                        
            elif self.game_state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # Press ESC to pause
                        self.game_state = GameState.PAUSE_MENU


    def update(self, dt):
        """Updates game logic based on current game state."""
        if self.game_state == GameState.PLAYING:
            if self.player and self.map:
                self.player.update(dt, self.map)

                target_camera_x = self.player.rect.centerx - (SCREEN_WIDTH / self.zoom_level) // 2
                target_camera_y = self.player.rect.centery - (SCREEN_HEIGHT / self.zoom_level) // 2

                max_camera_x = self.map.width - (SCREEN_WIDTH / self.zoom_level)
                max_camera_y = self.map.height - (SCREEN_HEIGHT / self.zoom_level)

                self.camera_offset_x = max(0, min(target_camera_x, max_camera_x))
                self.camera_offset_y = max(0, min(target_camera_y, max_camera_y))

    def draw(self):
        """Draws game elements to the screen based on current game state."""
        self.screen.fill(DARK_GREY)

        # Draw main game world always IF it exists (so menus overlay it)
        if self.game_state in [GameState.PLAYING, GameState.PAUSE_MENU, GameState.SLOT_SELECTION, GameState.INPUT_TEXT_PROMPT] and self.map and self.player:
            self._draw_playing_screen()
            
            # Optional: Add a semi-transparent overlay when paused or in selection screen
            if self.game_state in [GameState.PAUSE_MENU, GameState.SLOT_SELECTION, GameState.INPUT_TEXT_PROMPT]:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150)) # Black with 150 alpha (transparency)
                self.screen.blit(overlay, (0,0))


        if self.game_state == GameState.START_SCREEN:
            self._draw_start_screen()
        elif self.game_state == GameState.PAUSE_MENU:
            self._draw_pause_menu()
        elif self.game_state == GameState.SLOT_SELECTION:
            self._draw_slot_selection_screen()
        elif self.game_state == GameState.INPUT_TEXT_PROMPT:
            self._draw_input_prompt()
            
        pygame.display.flip()

    def _draw_start_screen(self):
        """Draws the elements for the start screen."""
        title_text = self.title_font.render("Durango Wildlands Clone", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.start_button.rect.top - TITLE_FONT_SIZE // 2 - BUTTON_SPACING))
        self.screen.blit(title_text, title_rect)

        for button in self.start_screen_buttons:
            button.draw(self.screen)

    def _draw_pause_menu(self):
        """Draws the elements for the pause menu."""
        title_text = self.title_font.render("Game Paused", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.resume_button.rect.top - TITLE_FONT_SIZE // 2 - BUTTON_SPACING))
        self.screen.blit(title_text, title_rect)

        for button in self.pause_menu_buttons:
            button.draw(self.screen)

    def _draw_slot_selection_screen(self):
        """Draws the elements for the save/load slot selection screen."""
        if self.slot_selection_mode == 'save':
            title_text = self.title_font.render("Select Save Slot", True, TEXT_COLOR)
        else: # mode == 'load'
            title_text = self.title_font.render("Select Load Slot", True, TEXT_COLOR)
            
        # Ensure there's at least one button to get reference from, otherwise center generically
        if self.slot_selection_buttons:
            first_button_top = self.slot_selection_buttons[0].rect.top
        else:
            first_button_top = SCREEN_HEIGHT // 2 # Fallback if no buttons for some reason

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, first_button_top - TITLE_FONT_SIZE // 2 - BUTTON_SPACING))
        self.screen.blit(title_text, title_rect)

        for button in self.slot_selection_buttons:
            button.draw(self.screen)

    def _draw_input_prompt(self):
        """Draws the input box and its prompt."""
        # Draw the prompt text
        prompt_surface = self.small_font.render(self.input_prompt_text, True, TEXT_COLOR)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(prompt_surface, prompt_rect)

        # Draw the input box itself
        if self.current_input_box:
            self.current_input_box.draw(self.screen)


    def _draw_playing_screen(self):
        """Draws the main game elements."""
        if self.map and self.player:
            self.map.draw(self.screen, self.camera_offset_x, self.camera_offset_y, self.zoom_level)

            scaled_player_width = int(self.player.original_image.get_width() * self.zoom_level)
            scaled_player_height = int(self.player.original_image.get_height() * self.zoom_level)
            self.player.image = pygame.transform.scale(self.player.original_image, (scaled_player_width, scaled_player_height))

            player_screen_x = (self.player.rect.x - self.camera_offset_x) * self.zoom_level
            player_screen_y = (self.player.rect.y - self.camera_offset_y) * self.zoom_level
            
            player_screen_rect = self.player.image.get_rect(topleft=(player_screen_x, player_screen_y))

            self.screen.blit(self.player.image, player_screen_rect)

    def run(self):
        """The main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()