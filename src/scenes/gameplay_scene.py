"""
Forest Survival - Game Scene System
Complete scene implementation with world scenes, transitions, and state management.
"""

import pygame
import math
import time
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod

import config
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.core.scene_manager import Scene, SceneManager
from src.ui.hud_system import HUDSystem
from src.ui.inventory_system import InventorySystem
from src.ui.dialogue_system import DialogueSystem
from src.gameplay.player import Player
from src.gameplay.world import World
from src.gameplay.camera import Camera


class GameState(Enum):
    """Game state enumeration."""
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    DIALOGUE = "dialogue"
    MENU = "menu"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"


class GameplayScene(Scene):
    """
    Main gameplay scene with world, player, and all game systems.
    """
    
    def __init__(self, scene_manager: SceneManager, input_manager: InputManager, audio_manager: AudioManager):
        super().__init__("gameplay")
        self.scene_manager = scene_manager
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        
        # Game state
        self.game_state = GameState.PLAYING
        self.previous_state = GameState.PLAYING
        
        # Core game systems
        self.player = None
        self.world = None
        self.camera = None
        
        # UI systems
        self.hud_system = None
        self.inventory_system = None
        self.dialogue_system = None
        
        # Pause menu
        self.pause_overlay = None
        self.pause_menu_items = [
            "Resume",
            "Settings", 
            "Save Game",
            "Main Menu",
            "Quit Game"
        ]
        self.pause_selected_index = 0
        
        # Game over
        self.game_over_timer = 0.0
        self.game_over_fade = 0.0
        
        # Level transition
        self.level_transition_timer = 0.0
        self.level_transition_fade = 0.0
        
        # Performance tracking
        self.frame_time = 0.0
        self.fps_counter = 0
        self.fps_timer = 0.0
        self.current_fps = 60
        
        # Debug mode
        self.debug_mode = False
        self.debug_info = {}
        
        print("Gameplay scene initialized")
    
    def initialize(self):
        """Initialize the gameplay scene."""
        print("Initializing gameplay scene...")
        
        # Initialize core systems
        self._initialize_world()
        self._initialize_player()
        self._initialize_camera()
        
        # Initialize UI systems
        self._initialize_ui_systems()
        
        # Start background music
        self.audio_manager.play_music('ingame.wav', loops=-1, volume=0.4)
        
        # Initialize pause overlay
        self._initialize_pause_overlay()
        
        print("Gameplay scene initialized successfully")
    
    def _initialize_world(self):
        """Initialize the game world."""
        self.world = World()
        self.world.generate_world()
    
    def _initialize_player(self):
        """Initialize the player."""
        spawn_point = self.world.get_spawn_point() if self.world else (400, 300)
        self.player = Player(spawn_point[0], spawn_point[1])
        
        # Connect player events
        self.player.on_death = self._on_player_death
        self.player.on_level_up = self._on_player_level_up
        self.player.on_item_collected = self._on_item_collected
    
    def _initialize_camera(self):
        """Initialize the camera system."""
        self.camera = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        if self.player:
            self.camera.set_target(self.player)
        
        # Set camera bounds based on world
        if self.world:
            self.camera.set_bounds(0, 0, self.world.width, self.world.height)
    
    def _initialize_ui_systems(self):
        """Initialize UI systems."""
        # HUD system
        self.hud_system = HUDSystem(self.input_manager, self.audio_manager)
        if self.player:
            self.hud_system.set_player(self.player)
        
        # Inventory system
        self.inventory_system = InventorySystem(self.input_manager, self.audio_manager)
        if self.player:
            self.inventory_system.set_player_inventory(self.player.inventory)
        
        # Dialogue system
        self.dialogue_system = DialogueSystem(self.input_manager, self.audio_manager)
        self.dialogue_system.on_dialogue_end = self._on_dialogue_end
        
        # Connect systems
        self.hud_system.on_inventory_toggle = self._toggle_inventory
        self.inventory_system.on_close = self._close_inventory
    
    def _initialize_pause_overlay(self):
        """Initialize pause menu overlay."""
        self.pause_overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    
    def _on_player_death(self):
        """Handle player death."""
        self.game_state = GameState.GAME_OVER
        self.game_over_timer = 0.0
        self.audio_manager.stop_music()
        self.audio_manager.play_sound('fall.wav', 0, 0, volume=0.8)
    
    def _on_player_level_up(self, new_level: int):
        """Handle player level up."""
        self.audio_manager.play_sound('levelup.wav', 0, 0, volume=0.7)
        self.hud_system.show_notification(f"Level Up! Now level {new_level}", duration=3.0)
    
    def _on_item_collected(self, item):
        """Handle item collection."""
        self.audio_manager.play_sound('click.wav', 0, 0, volume=0.5)
        self.hud_system.show_notification(f"Collected {item.name}", duration=2.0)
    
    def _on_dialogue_end(self):
        """Handle dialogue end."""
        if self.game_state == GameState.DIALOGUE:
            self.game_state = self.previous_state
    
    def _toggle_inventory(self):
        """Toggle inventory display."""
        if self.game_state == GameState.PLAYING:
            self.game_state = GameState.INVENTORY
            self.inventory_system.show()
        elif self.game_state == GameState.INVENTORY:
            self.game_state = GameState.PLAYING
            self.inventory_system.hide()
    
    def _close_inventory(self):
        """Close inventory."""
        if self.game_state == GameState.INVENTORY:
            self.game_state = GameState.PLAYING
    
    def _toggle_pause(self):
        """Toggle pause state."""
        if self.game_state == GameState.PLAYING:
            self.game_state = GameState.PAUSED
            self.pause_selected_index = 0
            self.audio_manager.pause_music()
            self.audio_manager.play_sound('click.wav', 0, 0, volume=0.5)
        elif self.game_state == GameState.PAUSED:
            self.game_state = GameState.PLAYING
            self.audio_manager.resume_music()
            self.audio_manager.play_sound('click.wav', 0, 0, volume=0.5)
    
    def start_dialogue(self, dialogue_id: str):
        """Start a dialogue conversation."""
        if self.game_state in [GameState.PLAYING, GameState.INVENTORY]:
            self.previous_state = self.game_state
            self.game_state = GameState.DIALOGUE
            
            # Close inventory if open
            if self.previous_state == GameState.INVENTORY:
                self.inventory_system.hide()
            
            self.dialogue_system.start_dialogue(dialogue_id)
    
    def complete_level(self):
        """Complete the current level."""
        self.game_state = GameState.LEVEL_COMPLETE
        self.level_transition_timer = 0.0
        self.audio_manager.play_sound('celebrate.wav', 0, 0, volume=0.8)
    
    def update(self, dt: float):
        """Update the gameplay scene."""
        # Track performance
        self.frame_time = dt
        self.fps_timer += dt
        self.fps_counter += 1
        
        if self.fps_timer >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = 0.0
        
        # Update based on game state
        if self.game_state == GameState.PLAYING:
            self._update_gameplay(dt)
        elif self.game_state == GameState.PAUSED:
            self._update_pause(dt)
        elif self.game_state == GameState.INVENTORY:
            self._update_inventory(dt)
        elif self.game_state == GameState.DIALOGUE:
            self._update_dialogue(dt)
        elif self.game_state == GameState.GAME_OVER:
            self._update_game_over(dt)
        elif self.game_state == GameState.LEVEL_COMPLETE:
            self._update_level_complete(dt)
        
        # Always update camera and HUD
        if self.camera:
            self.camera.update(dt)
        
        if self.hud_system:
            self.hud_system.update(dt)
        
        # Update debug info
        if self.debug_mode:
            self._update_debug_info()
    
    def _update_gameplay(self, dt: float):
        """Update core gameplay systems."""
        # Update world
        if self.world:
            self.world.update(dt)
        
        # Update player
        if self.player:
            self.player.update(dt)
            
            # Check world interactions
            if self.world:
                self.world.check_player_interactions(self.player)
                
                # Check level completion
                if self.world.is_level_complete(self.player):
                    self.complete_level()
    
    def _update_pause(self, dt: float):
        """Update pause menu."""
        # Pause menu doesn't need much updating
        pass
    
    def _update_inventory(self, dt: float):
        """Update inventory system."""
        if self.inventory_system:
            self.inventory_system.update(dt)
    
    def _update_dialogue(self, dt: float):
        """Update dialogue system."""
        if self.dialogue_system:
            self.dialogue_system.update(dt)
    
    def _update_game_over(self, dt: float):
        """Update game over state."""
        self.game_over_timer += dt
        self.game_over_fade = min(1.0, self.game_over_timer / 2.0)
        
        # Auto-return to main menu after delay
        if self.game_over_timer > 5.0:
            self.scene_manager.change_scene("main_menu")
    
    def _update_level_complete(self, dt: float):
        """Update level complete state."""
        self.level_transition_timer += dt
        self.level_transition_fade = min(1.0, self.level_transition_timer / 2.0)
        
        # Auto-continue to next level or menu
        if self.level_transition_timer > 3.0:
            # Would load next level or return to menu
            self.scene_manager.change_scene("main_menu")
    
    def _update_debug_info(self):
        """Update debug information."""
        self.debug_info = {
            'FPS': self.current_fps,
            'Frame Time': f"{self.frame_time * 1000:.1f}ms",
            'Game State': self.game_state.value,
            'Player Pos': f"({self.player.x:.1f}, {self.player.y:.1f})" if self.player else "None",
            'Camera Pos': f"({self.camera.x:.1f}, {self.camera.y:.1f})" if self.camera else "None",
            'Entities': len(self.world.entities) if self.world else 0,
        }
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        # Handle dialogue events first
        if self.game_state == GameState.DIALOGUE:
            if self.dialogue_system and self.dialogue_system.handle_event(event):
                return True
        
        # Handle inventory events
        if self.game_state == GameState.INVENTORY:
            if self.inventory_system and self.inventory_system.handle_event(event):
                return True
        
        # Handle pause menu events
        if self.game_state == GameState.PAUSED:
            if self._handle_pause_event(event):
                return True
        
        # Handle general game events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game_state in [GameState.PLAYING, GameState.PAUSED]:
                    self._toggle_pause()
                    return True
                elif self.game_state == GameState.INVENTORY:
                    self._close_inventory()
                    return True
            
            elif event.key == pygame.K_TAB:
                if self.game_state in [GameState.PLAYING, GameState.INVENTORY]:
                    self._toggle_inventory()
                    return True
            
            elif event.key == pygame.K_F3:
                self.debug_mode = not self.debug_mode
                return True
            
            elif event.key == pygame.K_F5 and self.debug_mode:
                # Quick save in debug mode
                self._quick_save()
                return True
            
            elif event.key == pygame.K_F9 and self.debug_mode:
                # Quick load in debug mode
                self._quick_load()
                return True
        
        # Pass events to player during gameplay
        if self.game_state == GameState.PLAYING and self.player:
            return self.player.handle_event(event)
        
        return False
    
    def _handle_pause_event(self, event: pygame.event.Event) -> bool:
        """Handle pause menu events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.pause_selected_index = (self.pause_selected_index - 1) % len(self.pause_menu_items)
                self.audio_manager.play_sound('ui_move', 0, 0, volume=0.3)
                return True
            
            elif event.key == pygame.K_DOWN:
                self.pause_selected_index = (self.pause_selected_index + 1) % len(self.pause_menu_items)
                self.audio_manager.play_sound('ui_move', 0, 0, volume=0.3)
                return True
            
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self._execute_pause_action()
                return True
        
        return False
    
    def _execute_pause_action(self):
        """Execute selected pause menu action."""
        selected_item = self.pause_menu_items[self.pause_selected_index]
        
        if selected_item == "Resume":
            self._toggle_pause()
        
        elif selected_item == "Settings":
            self.scene_manager.push_scene("settings")
        
        elif selected_item == "Save Game":
            self._save_game()
            self.hud_system.show_notification("Game Saved", duration=2.0)
        
        elif selected_item == "Main Menu":
            self.scene_manager.change_scene("main_menu")
        
        elif selected_item == "Quit Game":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        self.audio_manager.play_sound('click.wav', 0, 0, volume=0.5)
    
    def _save_game(self):
        """Save the current game state."""
        # Would implement save system here
        print("Game saved")
    
    def _quick_save(self):
        """Quick save for debug mode."""
        self._save_game()
        self.hud_system.show_notification("Quick Save", duration=1.0)
    
    def _quick_load(self):
        """Quick load for debug mode."""
        # Would implement load system here
        self.hud_system.show_notification("Quick Load", duration=1.0)
        print("Game loaded")
    
    def render(self, surface: pygame.Surface):
        """Render the gameplay scene."""
        # Clear screen
        surface.fill(config.COLORS['sky_blue'] if self.world else config.COLORS['black'])
        
        # Render world
        if self.world and self.camera:
            self.world.render(surface, self.camera)
        
        # Render player
        if self.player and self.camera:
            self.player.render(surface, self.camera)
        
        # Render UI systems
        if self.hud_system:
            self.hud_system.render(surface)
        
        if self.game_state == GameState.INVENTORY and self.inventory_system:
            self.inventory_system.render(surface)
        
        if self.game_state == GameState.DIALOGUE and self.dialogue_system:
            self.dialogue_system.render(surface)
        
        # Render pause overlay
        if self.game_state == GameState.PAUSED:
            self._render_pause_menu(surface)
        
        # Render game over overlay
        if self.game_state == GameState.GAME_OVER:
            self._render_game_over(surface)
        
        # Render level complete overlay
        if self.game_state == GameState.LEVEL_COMPLETE:
            self._render_level_complete(surface)
        
        # Render debug info
        if self.debug_mode:
            self._render_debug_info(surface)
    
    def _render_pause_menu(self, surface: pygame.Surface):
        """Render pause menu overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        
        # Pause menu background
        menu_width = 300
        menu_height = len(self.pause_menu_items) * 60 + 100
        menu_x = (config.SCREEN_WIDTH - menu_width) // 2
        menu_y = (config.SCREEN_HEIGHT - menu_height) // 2
        
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(surface, config.COLORS['dark_blue'], menu_rect)
        pygame.draw.rect(surface, config.COLORS['cyan'], menu_rect, 3)
        
        # Pause title
        title_font = pygame.font.Font(None, 48)
        title_surface = title_font.render("PAUSED", True, config.COLORS['white'])
        title_rect = title_surface.get_rect(centerx=menu_rect.centerx, y=menu_y + 20)
        surface.blit(title_surface, title_rect)
        
        # Menu items
        item_font = pygame.font.Font(None, 32)
        item_y = menu_y + 80
        
        for i, item in enumerate(self.pause_menu_items):
            # Highlight selected item
            if i == self.pause_selected_index:
                highlight_rect = pygame.Rect(menu_x + 20, item_y - 5, menu_width - 40, 40)
                pygame.draw.rect(surface, config.COLORS['yellow'], highlight_rect)
                text_color = config.COLORS['black']
            else:
                text_color = config.COLORS['white']
            
            # Render text
            item_surface = item_font.render(item, True, text_color)
            item_rect = item_surface.get_rect(centerx=menu_rect.centerx, y=item_y)
            surface.blit(item_surface, item_rect)
            
            item_y += 50
    
    def _render_game_over(self, surface: pygame.Surface):
        """Render game over overlay."""
        # Fade to black
        fade_alpha = int(255 * self.game_over_fade)
        fade_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, fade_alpha))
        surface.blit(fade_surface, (0, 0))
        
        # Game over text
        if self.game_over_fade > 0.5:
            text_alpha = int(255 * (self.game_over_fade - 0.5) * 2)
            
            font = pygame.font.Font(None, 72)
            game_over_surface = font.render("GAME OVER", True, config.COLORS['red'])
            game_over_surface.set_alpha(text_alpha)
            
            text_rect = game_over_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
            surface.blit(game_over_surface, text_rect)
            
            # Continue instruction
            if self.game_over_timer > 3.0:
                continue_font = pygame.font.Font(None, 24)
                continue_surface = continue_font.render("Returning to main menu...", True, config.COLORS['white'])
                continue_surface.set_alpha(text_alpha)
                
                continue_rect = continue_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 100))
                surface.blit(continue_surface, continue_rect)
    
    def _render_level_complete(self, surface: pygame.Surface):
        """Render level complete overlay."""
        # Fade to white
        fade_alpha = int(128 * self.level_transition_fade)
        fade_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((255, 255, 255, fade_alpha))
        surface.blit(fade_surface, (0, 0))
        
        # Level complete text
        if self.level_transition_fade > 0.3:
            text_alpha = int(255 * (self.level_transition_fade - 0.3) / 0.7)
            
            font = pygame.font.Font(None, 72)
            complete_surface = font.render("LEVEL COMPLETE!", True, config.COLORS['green'])
            complete_surface.set_alpha(text_alpha)
            
            text_rect = complete_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
            surface.blit(complete_surface, text_rect)
    
    def _render_debug_info(self, surface: pygame.Surface):
        """Render debug information."""
        debug_font = pygame.font.Font(None, 24)
        y_offset = 10
        
        for key, value in self.debug_info.items():
            debug_text = f"{key}: {value}"
            debug_surface = debug_font.render(debug_text, True, config.COLORS['yellow'])
            surface.blit(debug_surface, (10, y_offset))
            y_offset += 25
    
    def cleanup(self):
        """Clean up scene resources."""
        if self.audio_manager:
            self.audio_manager.stop_music()
        
        print("Gameplay scene cleaned up")


class TransitionEffect:
    """Visual transition effects between scenes."""
    
    def __init__(self):
        self.effect_type = "fade"
        self.duration = 1.0
        self.progress = 0.0
        self.is_active = False
        self.callback = None
    
    def start(self, effect_type: str = "fade", duration: float = 1.0, callback=None):
        """Start transition effect."""
        self.effect_type = effect_type
        self.duration = duration
        self.progress = 0.0
        self.is_active = True
        self.callback = callback
    
    def update(self, dt: float):
        """Update transition effect."""
        if not self.is_active:
            return
        
        self.progress += dt / self.duration
        
        if self.progress >= 1.0:
            self.progress = 1.0
            self.is_active = False
            
            if self.callback:
                self.callback()
    
    def render(self, surface: pygame.Surface):
        """Render transition effect."""
        if not self.is_active:
            return
        
        if self.effect_type == "fade":
            self._render_fade(surface)
        elif self.effect_type == "slide_left":
            self._render_slide(surface, -1, 0)
        elif self.effect_type == "slide_right":
            self._render_slide(surface, 1, 0)
        elif self.effect_type == "slide_up":
            self._render_slide(surface, 0, -1)
        elif self.effect_type == "slide_down":
            self._render_slide(surface, 0, 1)
        elif self.effect_type == "circle_wipe":
            self._render_circle_wipe(surface)
    
    def _render_fade(self, surface: pygame.Surface):
        """Render fade transition."""
        alpha = int(255 * self.progress)
        fade_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, alpha))
        surface.blit(fade_surface, (0, 0))
    
    def _render_slide(self, surface: pygame.Surface, dir_x: int, dir_y: int):
        """Render slide transition."""
        offset_x = int(config.SCREEN_WIDTH * dir_x * self.progress)
        offset_y = int(config.SCREEN_HEIGHT * dir_y * self.progress)
        
        # Create sliding overlay
        slide_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        slide_surface.fill(config.COLORS['black'])
        surface.blit(slide_surface, (offset_x, offset_y))
    
    def _render_circle_wipe(self, surface: pygame.Surface):
        """Render circle wipe transition."""
        center_x = config.SCREEN_WIDTH // 2
        center_y = config.SCREEN_HEIGHT // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        current_radius = int(max_radius * self.progress)
        
        # Create mask surface
        mask_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 255))
        
        if current_radius > 0:
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (center_x, center_y), current_radius)
        
        surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)


class GameSceneManager(SceneManager):
    """
    Extended scene manager with game-specific transitions and effects.
    """
    
    def __init__(self, input_manager: InputManager, audio_manager: AudioManager):
        super().__init__()
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        
        # Transition system
        self.transition_effect = TransitionEffect()
        self.pending_scene_change = None
        
        # Scene stack for overlays
        self.scene_stack: List[Scene] = []
    
    def change_scene_with_transition(self, scene_name: str, transition_type: str = "fade", duration: float = 1.0):
        """Change scene with visual transition."""
        self.pending_scene_change = scene_name
        self.transition_effect.start(transition_type, duration, self._complete_scene_change)
    
    def _complete_scene_change(self):
        """Complete the scene change after transition."""
        if self.pending_scene_change:
            self.change_scene(self.pending_scene_change)
            self.pending_scene_change = None
    
    def push_scene(self, scene_name: str):
        """Push current scene to stack and change to new scene."""
        if self.current_scene:
            self.scene_stack.append(self.current_scene)
        self.change_scene(scene_name)
    
    def pop_scene(self):
        """Pop scene from stack and return to it."""
        if self.scene_stack:
            popped_scene = self.scene_stack.pop()
            self.current_scene = popped_scene
            return True
        return False
    
    def update(self, dt: float):
        """Update scene manager and transitions."""
        # Update transition effect
        self.transition_effect.update(dt)
        
        # Update current scene
        super().update(dt)
    
    def render(self, surface: pygame.Surface):
        """Render scene and transitions."""
        # Render current scene
        super().render(surface)
        
        # Render transition effect on top
        self.transition_effect.render(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events, blocking during transitions."""
        # Block input during transitions
        if self.transition_effect.is_active:
            return True
        
        return super().handle_event(event)