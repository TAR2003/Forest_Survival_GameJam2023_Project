"""
Forest Survival - Save Manager
Handles game data persistence with JSON format and backup system.
"""

import json
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from copy import deepcopy
from datetime import datetime

import config


class SaveManager:
    """
    Manages game save data with automatic backups and corruption protection.
    """
    
    def __init__(self):
        """Initialize the save manager."""
        self.save_dir = config.SAVES_DIR
        self.save_file = self.save_dir / "game_data.json"
        self.backup_dir = self.save_dir / "backups"
        self.max_backups = 5
        
        # Current game data
        self.game_data = deepcopy(config.DEFAULT_SAVE_DATA)
        
        # Track changes for auto-save
        self._data_dirty = False
        self._last_auto_save = time.time()
        self.auto_save_interval = 300  # 5 minutes
        
        # Ensure directories exist
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        print("Save Manager initialized")
    
    def load_game_data(self) -> bool:
        """
        Load game data from file.
        
        Returns:
            True if loaded successfully, False if using defaults
        """
        try:
            if self.save_file.exists():
                # Try to load main save file
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Validate and merge with defaults
                self.game_data = self._validate_and_merge_data(loaded_data)
                print("Game data loaded successfully")
                return True
            else:
                print("No save file found, using defaults")
                return False
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading save file: {e}")
            
            # Try to load from backup
            if self._restore_from_backup():
                print("Restored from backup")
                return True
            else:
                print("Using default game data")
                return False
    
    def save_game_data(self, create_backup: bool = True) -> bool:
        """
        Save current game data to file.
        
        Args:
            create_backup: Whether to create a backup before saving
            
        Returns:
            True if saved successfully
        """
        try:
            # Create backup if requested
            if create_backup and self.save_file.exists():
                self._create_backup()
            
            # Update metadata
            self.game_data['last_save_time'] = datetime.now().isoformat()
            self.game_data['save_count'] = self.game_data.get('save_count', 0) + 1
            
            # Write to temporary file first
            temp_file = self.save_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.game_data, f, indent=2, ensure_ascii=False)
            
            # Replace original file with temporary file
            shutil.move(str(temp_file), str(self.save_file))
            
            self._data_dirty = False
            self._last_auto_save = time.time()
            print("Game data saved successfully")
            return True
            
        except IOError as e:
            print(f"Error saving game data: {e}")
            return False
    
    def auto_save_if_needed(self):
        """Perform auto-save if enough time has passed and data is dirty."""
        current_time = time.time()
        if (self._data_dirty and 
            current_time - self._last_auto_save >= self.auto_save_interval):
            self.save_game_data()
    
    def _validate_and_merge_data(self, loaded_data: Dict) -> Dict:
        """
        Validate loaded data and merge with defaults.
        
        Args:
            loaded_data: Data loaded from save file
            
        Returns:
            Validated and merged data
        """
        result = deepcopy(config.DEFAULT_SAVE_DATA)
        
        # Check version compatibility
        loaded_version = loaded_data.get('version', '0.0.0')
        if loaded_version != config.SAVE_VERSION:
            print(f"Save version mismatch: {loaded_version} vs {config.SAVE_VERSION}")
            # Could implement migration logic here
        
        # Recursively merge data
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
                            print(f"Invalid type for save data {key}, using default")
                else:
                    # New key not in defaults, add it anyway
                    default_dict[key] = value
        
        merge_dict(result, loaded_data)
        return result
    
    def _create_backup(self):
        """Create a backup of the current save file."""
        if not self.save_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"game_data_backup_{timestamp}.json"
        
        try:
            shutil.copy2(str(self.save_file), str(backup_file))
            
            # Clean up old backups
            self._cleanup_old_backups()
            
        except IOError as e:
            print(f"Error creating backup: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backup files, keeping only the most recent ones."""
        backup_files = list(self.backup_dir.glob("game_data_backup_*.json"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove excess backups
        for backup_file in backup_files[self.max_backups:]:
            try:
                backup_file.unlink()
            except IOError:
                pass
    
    def _restore_from_backup(self) -> bool:
        """
        Try to restore from the most recent backup.
        
        Returns:
            True if restored successfully
        """
        backup_files = list(self.backup_dir.glob("game_data_backup_*.json"))
        if not backup_files:
            return False
        
        # Sort by modification time, newest first
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for backup_file in backup_files:
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                self.game_data = self._validate_and_merge_data(loaded_data)
                
                # Copy backup to main save file
                shutil.copy2(str(backup_file), str(self.save_file))
                
                return True
                
            except (json.JSONDecodeError, IOError):
                continue  # Try next backup
        
        return False
    
    def get_player_data(self) -> Dict:
        """Get player data section."""
        return self.game_data.get('player', {})
    
    def set_player_data(self, key: str, value: Any):
        """Set player data value."""
        if 'player' not in self.game_data:
            self.game_data['player'] = {}
        
        self.game_data['player'][key] = value
        self._data_dirty = True
    
    def get_statistics(self) -> Dict:
        """Get statistics data section."""
        return self.game_data.get('statistics', {})
    
    def update_statistic(self, key: str, value: Any):
        """Update a statistic value."""
        if 'statistics' not in self.game_data:
            self.game_data['statistics'] = {}
        
        self.game_data['statistics'][key] = value
        self._data_dirty = True
    
    def increment_statistic(self, key: str, amount: int = 1):
        """Increment a statistic counter."""
        if 'statistics' not in self.game_data:
            self.game_data['statistics'] = {}
        
        current_value = self.game_data['statistics'].get(key, 0)
        self.game_data['statistics'][key] = current_value + amount
        self._data_dirty = True
    
    def get_achievements(self) -> Dict:
        """Get achievements data section."""
        return self.game_data.get('achievements', {})
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """
        Unlock an achievement.
        
        Args:
            achievement_id: Achievement identifier
            
        Returns:
            True if achievement was newly unlocked
        """
        if 'achievements' not in self.game_data:
            self.game_data['achievements'] = {'unlocked': [], 'progress': {}}
        
        unlocked_list = self.game_data['achievements'].get('unlocked', [])
        
        if achievement_id not in unlocked_list:
            unlocked_list.append(achievement_id)
            self.game_data['achievements']['unlocked'] = unlocked_list
            self._data_dirty = True
            
            # Add XP reward if defined
            if achievement_id in config.ACHIEVEMENTS:
                xp_reward = config.ACHIEVEMENTS[achievement_id].get('xp_reward', 0)
                if xp_reward > 0:
                    self.add_xp(xp_reward)
            
            return True
        
        return False
    
    def update_achievement_progress(self, achievement_id: str, progress: Dict):
        """Update progress for an achievement."""
        if 'achievements' not in self.game_data:
            self.game_data['achievements'] = {'unlocked': [], 'progress': {}}
        
        if 'progress' not in self.game_data['achievements']:
            self.game_data['achievements']['progress'] = {}
        
        self.game_data['achievements']['progress'][achievement_id] = progress
        self._data_dirty = True
    
    def get_unlocks(self) -> Dict:
        """Get unlocks data section."""
        return self.game_data.get('unlocks', {})
    
    def unlock_item(self, category: str, item_id: str) -> bool:
        """
        Unlock an item in a category.
        
        Args:
            category: Category (e.g., 'skins', 'weapons')
            item_id: Item identifier
            
        Returns:
            True if item was newly unlocked
        """
        if 'unlocks' not in self.game_data:
            self.game_data['unlocks'] = {}
        
        if category not in self.game_data['unlocks']:
            self.game_data['unlocks'][category] = []
        
        if item_id not in self.game_data['unlocks'][category]:
            self.game_data['unlocks'][category].append(item_id)
            self._data_dirty = True
            return True
        
        return False
    
    def is_item_unlocked(self, category: str, item_id: str) -> bool:
        """Check if an item is unlocked."""
        unlocks = self.get_unlocks()
        return item_id in unlocks.get(category, [])
    
    def get_settings(self) -> Dict:
        """Get settings data section."""
        return self.game_data.get('settings', {})
    
    def update_settings(self, settings: Dict):
        """Update settings data."""
        if 'settings' not in self.game_data:
            self.game_data['settings'] = {}
        
        self.game_data['settings'].update(settings)
        self._data_dirty = True
    
    def add_xp(self, amount: int):
        """Add XP and handle level ups."""
        current_xp = self.get_player_data().get('xp', 0)
        new_xp = current_xp + amount
        
        self.set_player_data('xp', new_xp)
        self.increment_statistic('total_xp', amount)
        
        # Check for level up
        current_level = self.get_player_data().get('level', 1)
        new_level = self._calculate_level(new_xp)
        
        if new_level > current_level:
            self.set_player_data('level', new_level)
            
            # Award skill points for level up
            skill_points = self.get_player_data().get('skill_points', 0)
            self.set_player_data('skill_points', skill_points + (new_level - current_level))
            
            return new_level - current_level  # Return levels gained
        
        return 0
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP."""
        # XP formula: 100 * (level^1.5)
        level = 1
        while True:
            xp_required = int(100 * (level ** 1.5))
            if xp < xp_required:
                return level - 1
            level += 1
            if level > 50:  # Max level cap
                return 50
    
    def get_current_run_data(self) -> Dict:
        """Get current run data for session tracking."""
        return {
            'start_time': time.time(),
            'score': 0,
            'enemies_defeated': 0,
            'damage_taken': 0,
            'perfect_blocks': 0,
            'combo_max': 0,
            'distance_traveled': 0
        }
    
    def save_run_results(self, run_data: Dict):
        """Save results from a completed run."""
        # Update statistics
        stats = self.get_statistics()
        stats['runs_completed'] = stats.get('runs_completed', 0) + 1
        
        # Update bests
        if run_data.get('score', 0) > stats.get('best_score', 0):
            stats['best_score'] = run_data['score']
        
        survival_time = run_data.get('survival_time', 0)
        if survival_time > stats.get('longest_survival', 0):
            stats['longest_survival'] = survival_time
        
        if run_data.get('combo_max', 0) > stats.get('highest_combo', 0):
            stats['highest_combo'] = run_data['combo_max']
        
        # Accumulate totals
        stats['total_enemies_defeated'] = stats.get('total_enemies_defeated', 0) + run_data.get('enemies_defeated', 0)
        stats['total_damage_taken'] = stats.get('total_damage_taken', 0) + run_data.get('damage_taken', 0)
        stats['perfect_blocks'] = stats.get('perfect_blocks', 0) + run_data.get('perfect_blocks', 0)
        stats['total_distance'] = stats.get('total_distance', 0) + run_data.get('distance_traveled', 0)
        
        # Update death cause if applicable
        death_cause = run_data.get('death_cause')
        if death_cause:
            stats['deaths'] = stats.get('deaths', 0) + 1
            if 'deaths_by_enemy' not in stats:
                stats['deaths_by_enemy'] = {}
            stats['deaths_by_enemy'][death_cause] = stats['deaths_by_enemy'].get(death_cause, 0) + 1
        
        # Award XP based on performance
        xp_earned = self._calculate_run_xp(run_data)
        if xp_earned > 0:
            levels_gained = self.add_xp(xp_earned)
            run_data['xp_earned'] = xp_earned
            run_data['levels_gained'] = levels_gained
        
        # Save immediately after run
        self.save_game_data()
    
    def _calculate_run_xp(self, run_data: Dict) -> int:
        """Calculate XP earned from a run."""
        xp = 0
        
        # Base XP for survival time
        survival_time = run_data.get('survival_time', 0)
        xp += int(survival_time)  # 1 XP per second
        
        # Bonus XP for enemies defeated
        enemies_defeated = run_data.get('enemies_defeated', 0)
        xp += enemies_defeated * 10
        
        # Bonus XP for perfect blocks
        perfect_blocks = run_data.get('perfect_blocks', 0)
        xp += perfect_blocks * 25
        
        # Bonus XP for high combo
        combo_max = run_data.get('combo_max', 0)
        if combo_max >= 50:
            xp += 100
        elif combo_max >= 25:
            xp += 50
        elif combo_max >= 10:
            xp += 25
        
        return xp
    
    def export_save_data(self, file_path: Path) -> bool:
        """Export save data to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.game_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error exporting save data: {e}")
            return False
    
    def import_save_data(self, file_path: Path) -> bool:
        """Import save data from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Create backup of current data first
            self._create_backup()
            
            # Validate and apply imported data
            self.game_data = self._validate_and_merge_data(imported_data)
            self._data_dirty = True
            
            # Save immediately
            return self.save_game_data()
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing save data: {e}")
            return False
    
    def reset_save_data(self, keep_settings: bool = True):
        """Reset save data to defaults."""
        # Backup current settings if requested
        settings_backup = None
        if keep_settings:
            settings_backup = deepcopy(self.get_settings())
        
        # Reset to defaults
        self.game_data = deepcopy(config.DEFAULT_SAVE_DATA)
        
        # Restore settings if backed up
        if settings_backup:
            self.game_data['settings'] = settings_backup
        
        self._data_dirty = True
        print("Save data reset to defaults")
    
    def get_save_summary(self) -> Dict:
        """Get summary of save data for display."""
        player = self.get_player_data()
        stats = self.get_statistics()
        
        return {
            'player_name': player.get('name', 'Player'),
            'level': player.get('level', 1),
            'best_score': stats.get('best_score', 0),
            'longest_survival': stats.get('longest_survival', 0),
            'total_playtime': stats.get('total_playtime', 0),
            'runs_completed': stats.get('runs_completed', 0),
            'achievements_unlocked': len(self.get_achievements().get('unlocked', [])),
            'last_save': self.game_data.get('last_save_time', 'Never')
        }