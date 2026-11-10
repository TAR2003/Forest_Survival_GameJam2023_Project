"""
Forest Survival - Main Game Class
Central game controller managing all systems and game flow.
"""

import pygame
import sys
from typing import Dict, Optional
from pathlib import Path

from src.core.scene_manager import SceneManager
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.core.save_manager import SaveManager
from src.core.performance_monitor import PerformanceMonitor
from src.settings import SettingsManager

import config


class ForestSurvivalGame:
    """
    Main game class that coordinates all systems and manages the game lifecycle.
    """
    
    def __init__(self):
        """Initialize the game and all its systems."""
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init(
            frequency=config.AUDIO_FREQUENCY,
            channels=config.AUDIO_CHANNELS,
            buffer=config.AUDIO_BUFFER_SIZE
        )
        
        # Initialize core systems
        self.settings_manager = SettingsManager()
        self.performance_monitor = PerformanceMonitor()
        self.save_manager = SaveManager()
        self.input_manager = InputManager()
        self.audio_manager = AudioManager()
        self.scene_manager = SceneManager()
        
        # Initialize display
        self._setup_display()
        
        # Register scenes
        self._register_scenes()
        
        # Load settings and save data
        self.settings_manager.load_settings()
        self.save_manager.load_game_data()
        
        # Apply loaded settings
        self._apply_settings()
        
        print(f"{config.GAME_TITLE} v{config.VERSION} initialized successfully!")
    
    def _setup_display(self):
        """Set up the game display window."""
        # Get display settings
        resolution = self.settings_manager.get_setting('video.resolution', config.DEFAULT_RESOLUTION)
        fullscreen = self.settings_manager.get_setting('video.fullscreen', False)
        vsync = self.settings_manager.get_setting('video.vsync', config.VSYNC_DEFAULT)
        
        # Create display
        if isinstance(resolution, (list, tuple)) and len(resolution) == 2:
            resolution = (int(resolution[0]), int(resolution[1]))
        else:
            resolution = config.DEFAULT_RESOLUTION

        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        vsync_flag = getattr(pygame, "VSYNC", 0)
        if vsync and vsync_flag:
            flags |= vsync_flag
        if fullscreen:
            flags |= pygame.FULLSCREEN

        try:
            self.screen = pygame.display.set_mode(resolution, flags)
        except pygame.error:
            self.screen = pygame.display.set_mode(resolution)
        pygame.display.set_caption(f"{config.GAME_TITLE} v{config.VERSION}")
        
        # Set icon if available
        icon_path = config.IMAGES_DIR / "icon.png"
        if icon_path.exists():
            icon = pygame.image.load(str(icon_path))
            pygame.display.set_icon(icon)
    
    def _register_scenes(self):
        """Register all game scenes with the scene manager."""
        from src.scenes.game_over import GameOverScene
        from src.scenes.main_menu import MainMenuScene
        from src.scenes.settings_menu import SettingsScene
        from src.scenes.splash import SplashScene
        from src.scenes.zone_coming import ZoneComingScene

        self.scene_manager.register_scene('splash', SplashScene(self.scene_manager))
        self.scene_manager.register_scene(
            'main_menu',
            MainMenuScene(self.scene_manager, self.input_manager, self.audio_manager, self.settings_manager),
        )
        self.scene_manager.register_scene('gameplay', ZoneComingScene(self.scene_manager))
        self.scene_manager.register_scene(
            'settings',
            SettingsScene(self.scene_manager, self.input_manager, self.audio_manager, self.settings_manager),
        )
        self.scene_manager.register_scene('game_over', GameOverScene(self.scene_manager))
        self.scene_manager.change_scene('splash', transition_duration=0)
    
    def _apply_settings(self):
        """Apply loaded settings to all systems."""
        # Audio settings
        master_volume = self.settings_manager.get_setting('audio.master', 0.8)
        self.audio_manager.set_master_volume(master_volume)
        
        music_volume = self.settings_manager.get_setting('audio.music', 0.7)
        self.audio_manager.set_music_volume(music_volume)
        
        sfx_volume = self.settings_manager.get_setting('audio.sfx', 0.9)
        self.audio_manager.set_sfx_volume(sfx_volume)
        
        # Input settings
        keybinds = self.settings_manager.get_setting('controls.keyboard', config.DEFAULT_KEYBINDS)
        self.input_manager.set_keybinds(keybinds)
        
        # Performance settings
        quality_preset = self.settings_manager.get_setting('video.quality_preset', 'medium')
        self.performance_monitor.set_quality_preset(quality_preset)
    
    def run(self):
        """Main game loop."""
        self.running = True
        
        while self.running:
            delta_time = self.clock.tick(config.FPS_TARGET) / 1000.0
            self.step(delta_time)

    def step(self, delta_time: float):
        """Advance one frame. Tests call this without owning the clock."""
        self.performance_monitor.update(delta_time)
        self.input_manager.update(delta_time)
        self._handle_events()
        self.scene_manager.update(delta_time)
        self._consume_scene_request()
        self._render()
        if self.scene_manager.should_quit:
            self.running = False

    def _consume_scene_request(self):
        scene = self.scene_manager.current_scene
        if not scene:
            return
        requested = scene.get_next_scene()
        if not requested:
            return
        if isinstance(requested, tuple):
            scene_name, data = requested
        else:
            scene_name, data = requested, None
        self.scene_manager.change_scene(scene_name, data)
    
    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                # Global hotkeys
                if event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT):
                    # Alt+F4 to quit
                    self.running = False
                elif event.key == config.DEFAULT_KEYBINDS['debug']:
                    # Toggle debug mode
                    self.performance_monitor.toggle_debug_overlay()
                elif event.key == config.DEFAULT_KEYBINDS['console']:
                    # Toggle debug console (if implemented)
                    pass
            
            # Pass event to input manager
            self.input_manager.handle_event(event)
            
            # Pass event to current scene
            if self.scene_manager.current_scene:
                self.scene_manager.current_scene.handle_event(event)
    
    def _render(self):
        """Render the current frame."""
        # Clear screen
        self.screen.fill(config.COLORS['black'])
        
        # Render current scene
        self.scene_manager.render(self.screen)
        
        # Render debug overlay if enabled
        if self.performance_monitor.debug_enabled:
            self.performance_monitor.render_debug_overlay(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def cleanup(self):
        """Clean up resources before exiting."""
        print("Cleaning up game resources...")
        
        # Save settings and game data
        self.settings_manager.save_settings()
        self.save_manager.save_game_data()
        
        # Cleanup systems
        if hasattr(self, 'audio_manager'):
            self.audio_manager.cleanup()
        
        if hasattr(self, 'scene_manager'):
            self.scene_manager.cleanup()
        
        if hasattr(self, 'performance_monitor'):
            self.performance_monitor.save_session_data()
        
        print("Cleanup complete.")
    
    def get_system(self, system_name: str):
        """Get reference to a game system."""
        systems = {
            'input': self.input_manager,
            'audio': self.audio_manager,
            'save': self.save_manager,
            'settings': self.settings_manager,
            'performance': self.performance_monitor,
            'scene': self.scene_manager
        }
        return systems.get(system_name)
    
    def quit_game(self):
        """Request game shutdown."""
        self.running = False