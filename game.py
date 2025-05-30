# durango_wildlands_clone/game.py

import pygame
import sys
import random
import json
import os 
from enum import Enum
from config import * # Import all constants
from player import Player
from button import Button 
from level.map import Map # Import Map from the level package
from level.tile import Tile # Corrected: Added this import

# --- InputBox Class ---
class InputBox:
    def __init__(self, x, y, width, height, text='', font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = INPUT_BOX_COLOR_INACTIVE
        self.color_active = INPUT_BOX_COLOR_ACTIVE
        self.outline_color = INPUT_BOX_OUTLINE_COLOR
        self.text_color = INPUT_BOX_TEXT_COLOR
        self.text = text
        self.font = font if font else pygame.font.Font(None, INPUT_BOX_FONT_SIZE)
        self.active = False 
        self.txt_surface = self.font.render(text, True, self.text_color)
        self.placeholder_text = "Enter filename..." 

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    pass 
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.text_color)

    def draw(self, surface):
        current_fill_color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, current_fill_color, self.rect)
        pygame.draw.rect(surface, self.outline_color, self.rect, 2) 

        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        else:
            placeholder_surface = self.font.render(self.placeholder_text, True, (150,150,150))
            surface.blit(placeholder_surface, (self.rect.x + 5, self.rect.y + 5))
            
    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.txt_surface = self.font.render(self.text, True, self.text_color)


# Define Game States 
class GameState(Enum):
    START_SCREEN = 1
    PLAYING = 2
    PAUSE_MENU = 3
    SLOT_SELECTION = 4
    INPUT_TEXT_PROMPT = 5

class Game:
    def __init__(self):
        """Initializes the game, sets up the screen, and loads assets."""
        pygame.init()
        # Initial screen setup (will be updated by _set_screen_mode)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Durango Wildlands Clone")
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_state = GameState.START_SCREEN
        self.fullscreen = False # New: Track fullscreen state

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
        self.input_font = pygame.font.Font(None, INPUT_BOX_FONT_SIZE) 

        # --- Buttons for Start Screen ---
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

        # --- Buttons for Pause Menu ---
        self.resume_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 - (BUTTON_HEIGHT + BUTTON_SPACING) * 1.5,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Resume Game", self._resume_game
        )
        self.save_game_button = Button(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 - (BUTTON_HEIGHT + BUTTON_SPACING) * 0.5,
            BUTTON_WIDTH, BUTTON_HEIGHT, "Save Game", 
            action=lambda: self._prompt_save_filename() 
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
        self.current_input_box = None
        self.input_callback = None # Function to call when input is finished
        self.input_prompt_text = "" # Text displayed above the input box

    def _set_screen_mode(self):
        """Toggles between windowed and fullscreen modes."""
        if self.fullscreen:
            # Use pygame.FULLSCREEN flag
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) 
            # When going fullscreen, you often want to use the current display's resolution
            # The (0,0) tells Pygame to use the current display's best resolution.
            # You might want to update SCREEN_WIDTH and SCREEN_HEIGHT in config
            # or use display.Info() to get actual resolution if scaling UI elements.
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Durango Wildlands Clone")


    def _create_slot_selection_buttons(self, mode):
        """Helper to create buttons for each save/load slot based on the mode."""
        self.slot_selection_buttons = []
        self.slot_selection_mode = mode
        
        # Adjusting layout for current screen size
        current_screen_width, current_screen_height = self.screen.get_size()
        
        total_rows_height = (self.num_save_slots + 1) * (BUTTON_HEIGHT + BUTTON_SPACING) - BUTTON_SPACING
        start_y = (current_screen_height - total_rows_height) // 2

        existing_saves = self._get_existing_save_files()

        for i in range(self.num_save_slots): 
            slot_number = i + 1 
            
            current_filename_display = existing_saves.get(f'slot_{slot_number}', f"Empty Slot {slot_number}")
            button_text = f"Slot {slot_number}: {current_filename_display}" 

            button_y = start_y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
            
            action_func = None
            if mode == 'save':
                action_func = lambda slot_num=slot_number: self._prompt_save_filename_for_slot(slot_num)
            elif mode == 'load':
                action_func = lambda slot_num=slot_number: self._load_game_from_slot(slot_num)

            slot_button_width = int(BUTTON_WIDTH * 1.5) 
            
            slot_button = Button(
                (current_screen_width - slot_button_width) // 2, # Center horizontally
                button_y,
                slot_button_width, BUTTON_HEIGHT, button_text, 
                action=action_func
            )
            self.slot_selection_buttons.append(slot_button)

            if not current_filename_display.startswith("Empty Slot") and not current_filename_display.startswith("Corrupted Slot"):
                 rename_button_width = BUTTON_WIDTH // 2
                 rename_button = Button(
                    slot_button.rect.right + BUTTON_SPACING, 
                    button_y,
                    rename_button_width, BUTTON_HEIGHT, "Rename",
                    action=lambda slot_num=slot_number, old_name=current_filename_display: self._prompt_rename_filename(slot_num, old_name)
                )
                 self.slot_selection_buttons.append(rename_button)

        back_button_y = start_y + self.num_save_slots * (BUTTON_HEIGHT + BUTTON_SPACING)
        self.slot_selection_buttons.append(
            Button(
                (current_screen_width - BUTTON_WIDTH) // 2, # Center horizontally
                back_button_y,
                BUTTON_WIDTH, BUTTON_HEIGHT, "Back", 
                action=self._return_from_slot_selection
            )
        )
        
    def _get_existing_save_files(self):
        """Returns a dictionary of existing save files mapped to their slot numbers."""
        saves = {}
        for i in range(1, self.num_save_slots + 1):
            filename_path = f'save_slot_{i}.json' 
            if os.path.exists(filename_path):
                try:
                    with open(filename_path, 'r') as f:
                        data = json.load(f)
                        saves[f'slot_{i}'] = data.get('save_name', f"Unnamed Save {i}")
                except (json.JSONDecodeError, KeyError):
                    saves[f'slot_{i}'] = f"Corrupted Slot {i}"
            else:
                saves[f'slot_{i}'] = f"Empty Slot {i}" 
        return saves

    def _initialize_game_components(self):
        """Initializes map and player for a new game."""
        self.map = Map() 

        valid_spawn_tiles = []
        for r_idx in range(self.map.rows):
            for c_idx in range(self.map.cols):
                tile = self.map.data[r_idx][c_idx] 
                # Player can only spawn on non-collidable tiles (grass or dirt for now)
                if not tile.is_collidable:
                    valid_spawn_tiles.append((tile.rect.x, tile.rect.y))

        spawn_x, spawn_y = PLAYER_START_X, PLAYER_START_Y
        if valid_spawn_tiles:
            spawn_x, spawn_y = random.choice(valid_spawn_tiles)
        else:
            print("Warning: No valid spawn tiles found on the map. Spawning at default location.")

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
        self._create_slot_selection_buttons(mode) 
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

    # --- Save/Load/Rename Logic ---
    def _prompt_save_filename(self):
        self._previous_game_state = self.game_state
        self.game_state = GameState.INPUT_TEXT_PROMPT
        self.input_prompt_text = "Enter save filename:"
        self.current_input_box = InputBox(
            (self.screen.get_width() - INPUT_BOX_WIDTH) // 2, # Use current screen width
            self.screen.get_height() // 2,                     # Use current screen height
            INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT,
            text='MySaveGame', font=self.input_font 
        )
        self.current_input_box.active = True
        self.input_callback = self._finalize_save_with_filename 
        print("Prompting for save filename...")

    def _prompt_save_filename_for_slot(self, slot_number):
        self._previous_game_state = self.game_state 
        self.game_state = GameState.INPUT_TEXT_PROMPT
        self.input_prompt_text = f"Enter filename for Slot {slot_number}:"
        
        existing_saves = self._get_existing_save_files()
        current_name = existing_saves.get(f'slot_{slot_number}', 'NewSave')
        if current_name.startswith("Empty Slot") or current_name.startswith("Corrupted Slot"):
            current_name = "NewSave" 

        self.current_input_box = InputBox(
            (self.screen.get_width() - INPUT_BOX_WIDTH) // 2, 
            self.screen.get_height() // 2,                    
            INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT,
            text=current_name, font=self.input_font
        )
        self.current_input_box.active = True
        self.input_callback = lambda filename: self._finalize_save_with_filename_and_slot(filename, slot_number)
        print(f"Prompting for filename for slot {slot_number}...")

    def _prompt_rename_filename(self, slot_number, old_display_name):
        self._previous_game_state = self.game_state 
        self.game_state = GameState.INPUT_TEXT_PROMPT
        self.input_prompt_text = f"Rename Slot {slot_number}: Enter new name"
        
        initial_name = old_display_name.split(': ')[-1] if ': ' in old_display_name else old_display_name

        self.current_input_box = InputBox(
            (self.screen.get_width() - INPUT_BOX_WIDTH) // 2, 
            self.screen.get_height() // 2,                    
            INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT,
            text=initial_name, font=self.input_font
        )
        self.current_input_box.active = True
        self.input_callback = lambda new_name: self._finalize_rename_filename(slot_number, new_name)
        print(f"Prompting to rename slot {slot_number}...")


    def _finalize_save_with_filename(self, filename):
        if not filename.strip(): 
            print("Save cancelled: filename cannot be empty.")
            self.game_state = self._previous_game_state 
            return

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
            self.game_state = self._previous_game_state 

    def _finalize_save_with_filename_and_slot(self, filename, slot_number):
        if not filename.strip():
            print("Save cancelled: filename cannot be empty.")
            self.game_state = self._previous_game_state
            return
        self._save_game_to_slot(slot_number, filename)


    def _finalize_rename_filename(self, slot_number, new_name):
        if not new_name.strip():
            print("Rename cancelled: new filename cannot be empty.")
            self.game_state = self._previous_game_state
            return

        filename_path = f'save_slot_{slot_number}.json'
        if os.path.exists(filename_path):
            try:
                with open(filename_path, 'r') as f:
                    save_data = json.load(f)
                save_data['save_name'] = new_name 
                with open(filename_path, 'w') as f:
                    json.dump(save_data, f, indent=4)
                print(f"Renamed slot {slot_number} to '{new_name}'")
                # Re-create slot buttons to update names on the UI
                self._create_slot_selection_buttons(self.slot_selection_mode)
                self.game_state = self._previous_game_state 
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                print(f"Error renaming file for slot {slot_number}: {e}")
                self.game_state = self._previous_game_state
        else:
            print(f"Cannot rename: No save file found for slot {slot_number}.")
            self.game_state = self._previous_game_state


    def _save_game_to_slot(self, slot_number, filename_to_save_as):
        if self.player is None or self.map is None:
            print("No game in progress to save!")
            self.game_state = self._previous_game_state 
            return

        # When saving, only save the tile IDs, not the entire Tile objects
        map_id_data = [[tile.id for tile in row] for row in self.map.data]

        save_data = {
            'player_x': self.player.rect.x,
            'player_y': self.player.rect.y,
            'map_data': map_id_data, 
            'save_name': filename_to_save_as 
        }
        
        filename_path = f'save_slot_{slot_number}.json' 
        try:
            with open(filename_path, 'w') as f:
                json.dump(save_data, f, indent=4)
            print(f"Game saved successfully as '{filename_to_save_as}' to {filename_path}")
            self.game_state = self._previous_game_state 
        except Exception as e:
            print(f"Error saving game: {e}")
            self.game_state = self._previous_game_state

    def _load_game_from_slot(self, slot_number):
        filename_path = f'save_slot_{slot_number}.json'
        try:
            with open(filename_path, 'r') as f:
                save_data = json.load(f)
            
            # Reconstruct Map with Tile objects from saved IDs
            self.map = Map() 
            loaded_map_id_data = save_data['map_data']
            
            # Create Tile objects from the loaded IDs
            reconstructed_map_data = []
            for r_idx, row_ids in enumerate(loaded_map_id_data):
                reconstructed_row = []
                for c_idx, tile_id in enumerate(row_ids):
                    reconstructed_row.append(Tile(tile_id, c_idx * TILE_SIZE, r_idx * TILE_SIZE))
                reconstructed_map_data.append(reconstructed_row)
            
            self.map.data = reconstructed_map_data 
            self.map.rows = len(reconstructed_map_data)
            self.map.cols = len(reconstructed_map_data[0]) if reconstructed_map_data else 0
            self.map.width = self.map.cols * TILE_SIZE
            self.map.height = self.map.rows * TILE_SIZE


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
            if self.game_state == GameState.SLOT_SELECTION: 
                self.game_state = self._previous_game_state 


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Global keyboard shortcut for fullscreen
            if event.type == pygame.KEYDOWN:
                # Check for Alt + Enter
                if event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT):
                    self.fullscreen = not self.fullscreen
                    self._set_screen_mode() # Call the new function to update display mode
                # Check for Ctrl + Enter
                elif event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.fullscreen = not self.fullscreen
                    self._set_screen_mode()

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
                        if self.input_callback:
                            entered_text = self.current_input_box.get_text()
                            self.input_callback(entered_text)
                            self.current_input_box = None 
                            self.input_callback = None
                        
            elif self.game_state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: 
                        self.game_state = GameState.PAUSE_MENU


    def update(self, dt):
        if self.game_state == GameState.PLAYING:
            if self.player and self.map:
                self.player.update(dt, self.map)

                # Camera centering and clamping
                # Calculate the desired camera offset based on player's position
                target_camera_x = self.player.rect.centerx - self.screen.get_width() / (2 * self.zoom_level)
                target_camera_y = self.player.rect.centery - self.screen.get_height() / (2 * self.zoom_level)

                # Clamp camera to map boundaries
                max_camera_x = self.map.width - self.screen.get_width() / self.zoom_level
                max_camera_y = self.map.height - self.screen.get_height() / self.zoom_level

                self.camera_offset_x = max(0, min(target_camera_x, max_camera_x))
                self.camera_offset_y = max(0, min(target_camera_y, max_camera_y))


    def draw(self):
        self.screen.fill(DARK_GREY)

        # Draw playing screen components if game is active or overlaid
        if self.game_state in [GameState.PLAYING, GameState.PAUSE_MENU, GameState.SLOT_SELECTION, GameState.INPUT_TEXT_PROMPT] and self.map and self.player:
            self._draw_playing_screen()
            
            # Apply a semi-transparent overlay when in menus over the game
            if self.game_state in [GameState.PAUSE_MENU, GameState.SLOT_SELECTION, GameState.INPUT_TEXT_PROMPT]:
                # The overlay should scale to the current screen size
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150)) # Black with 150 alpha (out of 255)
                self.screen.blit(overlay, (0,0))


        # Draw specific UI for current game state
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
        # UI elements positioning should adapt to current screen dimensions if going full screen
        current_screen_width, current_screen_height = self.screen.get_size()

        title_text = self.title_font.render("Durango Wildlands Clone", True, TEXT_COLOR)
        # Position relative to current screen dimensions
        title_rect = title_text.get_rect(center=(current_screen_width // 2, current_screen_height // 2 - 150)) # Adjusted Y
        self.screen.blit(title_text, title_rect)

        # Update button positions based on current screen dimensions
        self.start_button.rect.center = (current_screen_width // 2, current_screen_height // 2 - BUTTON_HEIGHT - BUTTON_SPACING)
        self.load_button.rect.center = (current_screen_width // 2, current_screen_height // 2)
        self.exit_button.rect.center = (current_screen_width // 2, current_screen_height // 2 + BUTTON_HEIGHT + BUTTON_SPACING)

        for button in self.start_screen_buttons:
            button.draw(self.screen)

    def _draw_pause_menu(self):
        current_screen_width, current_screen_height = self.screen.get_size()

        title_text = self.title_font.render("Game Paused", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(current_screen_width // 2, current_screen_height // 2 - 200)) # Adjusted Y
        self.screen.blit(title_text, title_rect)

        # Update button positions based on current screen dimensions
        self.resume_button.rect.center = (current_screen_width // 2, current_screen_height // 2 - (BUTTON_HEIGHT + BUTTON_SPACING) * 1.5)
        self.save_game_button.rect.center = (current_screen_width // 2, current_screen_height // 2 - (BUTTON_HEIGHT + BUTTON_SPACING) * 0.5)
        self.load_game_button_pause.rect.center = (current_screen_width // 2, current_screen_height // 2 + (BUTTON_HEIGHT + BUTTON_SPACING) * 0.5)
        self.exit_to_main_button.rect.center = (current_screen_width // 2, current_screen_height // 2 + (BUTTON_HEIGHT + BUTTON_SPACING) * 1.5)


        for button in self.pause_menu_buttons:
            button.draw(self.screen)

    def _draw_slot_selection_screen(self):
        current_screen_width, current_screen_height = self.screen.get_size()

        if self.slot_selection_mode == 'save':
            title_text = self.title_font.render("Select Save Slot", True, TEXT_COLOR)
        else: 
            title_text = self.title_font.render("Select Load Slot", True, TEXT_COLOR)
            
        # Re-calculate button positions before drawing them
        self._create_slot_selection_buttons(self.slot_selection_mode) # This will update button rects based on current screen size

        if self.slot_selection_buttons:
            # Find the top-most button to position the title relative to it
            first_button_top = min(b.rect.top for b in self.slot_selection_buttons if "Slot" in b.text)
        else:
            first_button_top = current_screen_height // 2 

        title_rect = title_text.get_rect(center=(current_screen_width // 2, first_button_top - TITLE_FONT_SIZE // 2 - BUTTON_SPACING))
        self.screen.blit(title_text, title_rect)

        for button in self.slot_selection_buttons:
            button.draw(self.screen)

    def _draw_input_prompt(self):
        current_screen_width, current_screen_height = self.screen.get_size()

        prompt_surface = self.small_font.render(self.input_prompt_text, True, TEXT_COLOR)
        prompt_rect = prompt_surface.get_rect(center=(current_screen_width // 2, current_screen_height // 2 - 50))
        self.screen.blit(prompt_surface, prompt_rect)

        # Update input box position based on current screen dimensions
        self.current_input_box.rect.center = (current_screen_width // 2, current_screen_height // 2 + 20) # Adjusted Y

        if self.current_input_box:
            self.current_input_box.draw(self.screen)


    def _draw_playing_screen(self):
        if self.map and self.player:
            self.map.draw(self.screen, self.camera_offset_x, self.camera_offset_y, self.zoom_level)

            if hasattr(self.player, 'original_image'):
                # Player size should be relative to TILE_SIZE and zoom, not screen size
                # The PLAYER_SIZE from config is already for zoom_level 1.0
                scaled_player_width = int(PLAYER_SIZE * self.zoom_level)
                scaled_player_height = int(PLAYER_SIZE * self.zoom_level)
                
                self.player.image = pygame.transform.scale(self.player.original_image, (scaled_player_width, scaled_player_height))
            else:
                print("Warning: Player has no original_image. Drawing a default rectangle.")
                pygame.draw.rect(self.screen, RED, self.player.rect)
                return 

            player_screen_x = (self.player.rect.x - self.camera_offset_x) * self.zoom_level
            player_screen_y = (self.player.rect.y - self.camera_offset_y) * self.zoom_level
            
            player_screen_rect = self.player.image.get_rect(topleft=(player_screen_x, player_screen_y))

            self.screen.blit(self.player.image, player_screen_rect)


    def run(self):
        self._set_screen_mode() # Set initial screen mode
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()