"""
Forest Survival - Main Game Class
Central game controller managing all systems and game flow.
"""

import pygame
import sys
from typing import Dict, Optional
from pathlib import Path

# Import core systems
from core.scene_manager import SceneManager
from core.input_manager import InputManager
from core.audio_manager import AudioManager
from core.save_manager import SaveManager
from core.performance_monitor import PerformanceMonitor
from settings import SettingsManager

# Import scenes
from scenes.splash_screen import SplashScreenScene
from scenes.main_menu_scene import MainMenuScene
from scenes.gameplay_scene import GameplayScene
from scenes.settings_scene import SettingsScene
from scenes.game_over_scene import GameOverScene

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
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if vsync:
            flags |= pygame.VSYNC
        if fullscreen:
            flags |= pygame.FULLSCREEN
            
        self.screen = pygame.display.set_mode(resolution, flags)
        pygame.display.set_caption(f"{config.GAME_TITLE} v{config.VERSION}")
        
        # Set icon if available
        icon_path = config.IMAGES_DIR / "icon.png"
        if icon_path.exists():
            icon = pygame.image.load(str(icon_path))
            pygame.display.set_icon(icon)
    
    def _register_scenes(self):
        """Register all game scenes with the scene manager."""
        self.scene_manager.register_scene('splash', SplashScreenScene())
        self.scene_manager.register_scene('main_menu', MainMenuScene())
        self.scene_manager.register_scene('gameplay', GameplayScene())
        self.scene_manager.register_scene('settings', SettingsScene())
        self.scene_manager.register_scene('game_over', GameOverScene())
        
        # Start with splash screen
        self.scene_manager.change_scene('splash')
    
    def _apply_settings(self):
        """Apply loaded settings to all systems."""
        # Audio settings
        master_volume = self.settings_manager.get_setting('audio.master_volume', 0.8)
        self.audio_manager.set_master_volume(master_volume)
        
        music_volume = self.settings_manager.get_setting('audio.music_volume', 0.7)
        self.audio_manager.set_music_volume(music_volume)
        
        sfx_volume = self.settings_manager.get_setting('audio.sfx_volume', 0.9)
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
        
        # Start background music
        self.audio_manager.play_music('theme', loops=-1)
        
        while self.running:
            # Calculate delta time
            delta_time = self.clock.tick(config.FPS_TARGET) / 1000.0
            
            # Update performance monitoring
            self.performance_monitor.update(delta_time)
            
            # Handle events
            self._handle_events()
            
            # Update current scene
            if self.scene_manager.current_scene:
                self.scene_manager.current_scene.update(delta_time)
                
                # Check for scene change requests
                next_scene = self.scene_manager.current_scene.get_next_scene()
                if next_scene:
                    self.scene_manager.change_scene(next_scene)
            
            # Render
            self._render()
            
            # Check for quit conditions
            if self.scene_manager.should_quit or not self.running:
                self.running = False
    
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
        if self.scene_manager.current_scene:
            self.scene_manager.current_scene.render(self.screen)
        
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