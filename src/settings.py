"""
Forest Survival - Settings Manager
Handles all game settings with JSON persistence and validation.
"""

import json
import pygame
from pathlib import Path
from typing import Any, Dict, Optional, Union
from copy import deepcopy

import config


class SettingsManager:
    """
    Manages game settings with persistence, validation, and easy access.
    """
    
    def __init__(self):
        """Initialize the settings manager."""
        self.settings_file = config.SAVES_DIR / "settings.json"
        self.settings = deepcopy(config.DEFAULT_SAVE_DATA['settings'])
        self._dirty = False  # Track if settings need saving
    
    def load_settings(self) -> bool:
        """
        Load settings from file.
        
        Returns:
            bool: True if loaded successfully, False if using defaults
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Validate and merge with defaults
                self.settings = self._validate_and_merge_settings(loaded_settings)
                print("Settings loaded successfully")
                return True
            else:
                print("No settings file found, using defaults")
                return False
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")
            print("Using default settings")
            return False
    
    def save_settings(self) -> bool:
        """
        Save current settings to file.
        
        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            self._dirty = False
            print("Settings saved successfully")
            return True
            
        except IOError as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.
        
        Args:
            key: Setting key in dot notation (e.g., 'audio.master_volume')
            default: Default value if key not found
            
        Returns:
            The setting value or default
        """
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a setting value using dot notation.
        
        Args:
            key: Setting key in dot notation
            value: New value to set
            
        Returns:
            bool: True if set successfully
        """
        try:
            keys = key.split('.')
            setting_dict = self.settings
            
            # Navigate to the parent dictionary
            for k in keys[:-1]:
                if k not in setting_dict:
                    setting_dict[k] = {}
                setting_dict = setting_dict[k]
            
            # Set the value
            old_value = setting_dict.get(keys[-1])
            setting_dict[keys[-1]] = value
            
            # Mark as dirty if value changed
            if old_value != value:
                self._dirty = True
                self._on_setting_changed(key, value, old_value)
            
            return True
            
        except Exception as e:
            print(f"Error setting {key} to {value}: {e}")
            return False
    
    def _validate_and_merge_settings(self, loaded_settings: Dict) -> Dict:
        """
        Validate loaded settings and merge with defaults.
        
        Args:
            loaded_settings: Settings loaded from file
            
        Returns:
            Validated and merged settings
        """
        result = deepcopy(config.DEFAULT_SAVE_DATA['settings'])
        
        # Recursively merge settings
        def merge_dict(default_dict, loaded_dict):
            for key, value in loaded_dict.items():
                if key in default_dict:
                    if isinstance(default_dict[key], dict) and isinstance(value, dict):
                        merge_dict(default_dict[key], value)
                    else:
                        # Validate the value type matches expected
                        if type(value) == type(default_dict[key]):
                            default_dict[key] = value
                        else:
                            print(f"Invalid type for setting {key}, using default")
        
        merge_dict(result, loaded_settings)
        return result
    
    def _on_setting_changed(self, key: str, new_value: Any, old_value: Any):
        """
        Handle setting changes for immediate application.
        
        Args:
            key: Setting key that changed
            new_value: New setting value
            old_value: Previous setting value
        """
        # Audio settings - apply immediately
        if key.startswith('audio.'):
            self._apply_audio_setting(key, new_value)
        
        # Video settings - some need restart
        elif key.startswith('video.'):
            self._apply_video_setting(key, new_value)
        
        # Control settings
        elif key.startswith('controls.'):
            self._apply_control_setting(key, new_value)
    
    def _apply_audio_setting(self, key: str, value: Any):
        """Apply audio setting immediately."""
        try:
            # Get audio manager from game instance if available
            from game import ForestSurvivalGame
            # This would need to be handled differently in actual implementation
            # For now, just validate the value
            if isinstance(value, (int, float)) and 0.0 <= value <= 1.0:
                print(f"Audio setting {key} updated to {value}")
        except ImportError:
            pass
    
    def _apply_video_setting(self, key: str, value: Any):
        """Apply video setting (some may require restart)."""
        if key == 'video.resolution':
            if value in config.SUPPORTED_RESOLUTIONS:
                print(f"Resolution change requested: {value} (restart required)")
        elif key == 'video.fullscreen':
            print(f"Fullscreen mode: {value} (restart required)")
        elif key == 'video.vsync':
            print(f"VSync: {value} (restart required)")
    
    def _apply_control_setting(self, key: str, value: Any):
        """Apply control setting immediately."""
        if key == 'controls.keyboard':
            print("Keyboard bindings updated")
    
    def reset_to_defaults(self, category: Optional[str] = None):
        """
        Reset settings to defaults.
        
        Args:
            category: Optional category to reset (e.g., 'audio', 'video')
                     If None, resets all settings
        """
        defaults = config.DEFAULT_SAVE_DATA['settings']
        
        if category:
            if category in defaults:
                self.settings[category] = deepcopy(defaults[category])
                self._dirty = True
                print(f"Reset {category} settings to defaults")
        else:
            self.settings = deepcopy(defaults)
            self._dirty = True
            print("Reset all settings to defaults")
    
    def export_settings(self, file_path: Union[str, Path]) -> bool:
        """
        Export current settings to a file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            bool: True if exported successfully
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"Settings exported to {file_path}")
            return True
        except IOError as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: Union[str, Path]) -> bool:
        """
        Import settings from a file.
        
        Args:
            file_path: Path to import file
            
        Returns:
            bool: True if imported successfully
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            self.settings = self._validate_and_merge_settings(imported_settings)
            self._dirty = True
            print(f"Settings imported from {file_path}")
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing settings: {e}")
            return False
    
    def get_keybind(self, action: str) -> Optional[int]:
        """
        Get keybind for an action.
        
        Args:
            action: Action name (e.g., 'jump', 'attack')
            
        Returns:
            pygame key constant or None if not found
        """
        keybinds = self.get_setting('controls.keyboard', {})
        return keybinds.get(action)
    
    def set_keybind(self, action: str, key: int) -> bool:
        """
        Set keybind for an action.
        
        Args:
            action: Action name
            key: pygame key constant
            
        Returns:
            bool: True if set successfully
        """
        keybinds = self.get_setting('controls.keyboard', {}).copy()
        keybinds[action] = key
        return self.set_setting('controls.keyboard', keybinds)
    
    @property
    def needs_save(self) -> bool:
        """Check if settings have been modified and need saving."""
        return self._dirty
    
    def get_display_resolution(self) -> tuple:
        """Get current display resolution setting."""
        return tuple(self.get_setting('video.resolution', config.DEFAULT_RESOLUTION))
    
    def get_audio_volumes(self) -> Dict[str, float]:
        """Get all audio volume settings."""
        return self.get_setting('audio', config.DEFAULT_VOLUMES).copy()
    
    def is_debug_mode_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get_setting('debug.enabled', False)