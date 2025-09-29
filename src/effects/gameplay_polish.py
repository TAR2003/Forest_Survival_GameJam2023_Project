"""
Forest Survival - Gameplay Polish System
Advanced gameplay refinements, balance, and quality-of-life improvements.
"""

import time
import math
import random
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from enum import Enum
from dataclasses import dataclass

import config


class DifficultyMode(Enum):
    """Game difficulty modes."""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    NIGHTMARE = "nightmare"
    CUSTOM = "custom"


class QualityOfLifeFeature(Enum):
    """Quality of life improvement features."""
    AUTO_SAVE = "auto_save"
    QUICK_ACTIONS = "quick_actions"
    SMART_CAMERA = "smart_camera"
    CONTEXT_HINTS = "context_hints"
    AUTO_PICKUP = "auto_pickup"
    SMART_TARGETING = "smart_targeting"
    GESTURE_SHORTCUTS = "gesture_shortcuts"
    ADAPTIVE_UI = "adaptive_ui"


@dataclass
class BalanceModifier:
    """Gameplay balance modifier."""
    name: str
    category: str
    base_value: float
    current_value: float
    min_value: float
    max_value: float
    
    # Dynamic scaling
    scaling_factor: float = 1.0
    time_modifier: float = 0.0
    
    # Conditions
    conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
    
    def get_value(self, context: Dict[str, Any] = None) -> float:
        """Get current modified value."""
        value = self.current_value * self.scaling_factor
        
        # Apply time modifier
        if self.time_modifier != 0:
            time_factor = 1.0 + (time.time() * self.time_modifier * 0.001)
            value *= time_factor
        
        # Apply contextual conditions
        if context and self.conditions:
            for condition, modifier in self.conditions.items():
                if condition in context:
                    value *= modifier
        
        return max(self.min_value, min(self.max_value, value))
    
    def adjust(self, factor: float):
        """Adjust the current value by a factor."""
        self.current_value = max(self.min_value, min(self.max_value, 
                                                   self.current_value * factor))


class AdaptiveDifficulty:
    """Dynamic difficulty adjustment system."""
    
    def __init__(self):
        # Player performance tracking
        self.performance_history: List[float] = []
        self.max_history_length = 100
        
        # Performance metrics
        self.deaths_per_hour = 0.0
        self.average_survival_time = 0.0
        self.resource_efficiency = 1.0
        self.combat_success_rate = 0.5
        
        # Difficulty parameters
        self.current_difficulty = 1.0  # 0.5 = easier, 2.0 = harder
        self.target_difficulty = 1.0
        self.adjustment_speed = 0.1
        
        # Thresholds
        self.easy_threshold = 0.3
        self.hard_threshold = 0.7
        
        # Adaptation settings
        self.adaptation_enabled = True
        self.max_difficulty_change = 0.5
        self.adaptation_delay = 60.0  # seconds before first adjustment
        
        # Time tracking
        self.session_start_time = time.time()
        self.last_adjustment_time = time.time()
        
        print("Adaptive difficulty system initialized")
    
    def record_performance(self, metric_type: str, value: float):
        """Record a performance metric."""
        if metric_type == "death":
            # Player died
            self.performance_history.append(0.0)
        elif metric_type == "survival":
            # Player survived for a duration
            self.performance_history.append(min(1.0, value / 300.0))  # Normalize to 5 minutes
        elif metric_type == "combat_win":
            self.performance_history.append(1.0)
        elif metric_type == "combat_loss":
            self.performance_history.append(0.0)
        elif metric_type == "resource_collection":
            # Efficiency metric
            self.performance_history.append(min(1.0, value))
        
        # Limit history size
        if len(self.performance_history) > self.max_history_length:
            self.performance_history.pop(0)
    
    def calculate_performance_score(self) -> float:
        """Calculate current performance score (0.0 to 1.0)."""
        if not self.performance_history:
            return 0.5  # Neutral performance
        
        # Recent performance weighted more heavily
        weights = [1.0 + i * 0.1 for i in range(len(self.performance_history))]
        weighted_sum = sum(score * weight for score, weight in zip(self.performance_history, weights))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.5
    
    def update_difficulty(self, dt: float):
        """Update adaptive difficulty based on performance."""
        if not self.adaptation_enabled:
            return
        
        current_time = time.time()
        session_duration = current_time - self.session_start_time
        
        # Wait for adaptation delay
        if session_duration < self.adaptation_delay:
            return
        
        performance = self.calculate_performance_score()
        
        # Determine target difficulty
        if performance < self.easy_threshold:
            # Player struggling - make easier
            self.target_difficulty = max(0.5, self.current_difficulty - 0.2)
        elif performance > self.hard_threshold:
            # Player doing well - make harder
            self.target_difficulty = min(2.0, self.current_difficulty + 0.2)
        else:
            # Performance is good - maintain current difficulty
            pass
        
        # Gradually adjust difficulty
        difficulty_diff = self.target_difficulty - self.current_difficulty
        adjustment = difficulty_diff * self.adjustment_speed * dt
        
        # Limit adjustment speed
        max_adjustment = self.max_difficulty_change * dt
        adjustment = max(-max_adjustment, min(max_adjustment, adjustment))
        
        self.current_difficulty += adjustment
        self.current_difficulty = max(0.5, min(2.0, self.current_difficulty))
    
    def get_difficulty_modifier(self) -> float:
        """Get current difficulty modifier."""
        return self.current_difficulty
    
    def get_difficulty_description(self) -> str:
        """Get human-readable difficulty description."""
        if self.current_difficulty < 0.7:
            return "Easy"
        elif self.current_difficulty < 1.3:
            return "Normal"
        elif self.current_difficulty < 1.7:
            return "Hard"
        else:
            return "Very Hard"


class GameplayPolishSystem:
    """
    Advanced gameplay polish system with balance, QoL features, and adaptive systems.
    """
    
    def __init__(self):
        # Difficulty system
        self.adaptive_difficulty = AdaptiveDifficulty()
        self.current_difficulty_mode = DifficultyMode.NORMAL
        
        # Balance modifiers
        self.balance_modifiers: Dict[str, BalanceModifier] = {}
        self.initialize_balance_modifiers()
        
        # Quality of life features
        self.qol_features: Dict[QualityOfLifeFeature, bool] = {
            QualityOfLifeFeature.AUTO_SAVE: True,
            QualityOfLifeFeature.QUICK_ACTIONS: True,
            QualityOfLifeFeature.SMART_CAMERA: True,
            QualityOfLifeFeature.CONTEXT_HINTS: True,
            QualityOfLifeFeature.AUTO_PICKUP: False,
            QualityOfLifeFeature.SMART_TARGETING: True,
            QualityOfLifeFeature.GESTURE_SHORTCUTS: False,
            QualityOfLifeFeature.ADAPTIVE_UI: True
        }
        
        # Auto-save system
        self.auto_save_interval = 300.0  # 5 minutes
        self.last_auto_save = time.time()
        
        # Smart camera system
        self.camera_focus_objects: List[Dict[str, Any]] = []
        self.camera_smoothing = 0.1
        
        # Context hints system
        self.active_hints: List[Dict[str, Any]] = []
        self.hint_cooldowns: Dict[str, float] = {}
        
        # Quick actions
        self.quick_action_bindings: Dict[str, Callable] = {}
        self.gesture_buffer: List[Tuple[float, float]] = []  # (time, direction)
        
        # Performance tracking
        self.performance_metrics: Dict[str, Any] = {
            'frame_time': 0.0,
            'memory_usage': 0.0,
            'active_objects': 0,
            'draw_calls': 0
        }
        
        # Accessibility features
        self.colorblind_friendly = False
        self.high_contrast = False
        self.large_text = False
        self.simplified_effects = False
        
        print("Gameplay polish system initialized")
    
    def initialize_balance_modifiers(self):
        """Initialize balance modifiers for different game aspects."""
        # Player stats
        self.balance_modifiers["player_health"] = BalanceModifier(
            "Player Health", "player", 100.0, 100.0, 50.0, 200.0
        )
        self.balance_modifiers["player_stamina"] = BalanceModifier(
            "Player Stamina", "player", 100.0, 100.0, 50.0, 200.0
        )
        self.balance_modifiers["player_speed"] = BalanceModifier(
            "Player Speed", "player", 5.0, 5.0, 2.0, 10.0
        )
        
        # Combat
        self.balance_modifiers["damage_multiplier"] = BalanceModifier(
            "Damage Multiplier", "combat", 1.0, 1.0, 0.5, 3.0
        )
        self.balance_modifiers["enemy_health"] = BalanceModifier(
            "Enemy Health", "combat", 50.0, 50.0, 20.0, 200.0
        )
        self.balance_modifiers["enemy_damage"] = BalanceModifier(
            "Enemy Damage", "combat", 10.0, 10.0, 5.0, 50.0
        )
        
        # Resources
        self.balance_modifiers["resource_spawn_rate"] = BalanceModifier(
            "Resource Spawn Rate", "resources", 1.0, 1.0, 0.5, 3.0
        )
        self.balance_modifiers["crafting_speed"] = BalanceModifier(
            "Crafting Speed", "resources", 1.0, 1.0, 0.5, 3.0
        )
        
        # Environmental
        self.balance_modifiers["day_length"] = BalanceModifier(
            "Day Length", "environment", 600.0, 600.0, 300.0, 1200.0
        )
        self.balance_modifiers["weather_intensity"] = BalanceModifier(
            "Weather Intensity", "environment", 1.0, 1.0, 0.0, 2.0
        )
    
    def set_difficulty_mode(self, mode: DifficultyMode):
        """Set game difficulty mode and adjust balance accordingly."""
        self.current_difficulty_mode = mode
        
        if mode == DifficultyMode.EASY:
            multipliers = {
                "player_health": 1.5,
                "player_stamina": 1.3,
                "damage_multiplier": 1.2,
                "enemy_health": 0.7,
                "enemy_damage": 0.8,
                "resource_spawn_rate": 1.5
            }
        elif mode == DifficultyMode.NORMAL:
            multipliers = {key: 1.0 for key in self.balance_modifiers.keys()}
        elif mode == DifficultyMode.HARD:
            multipliers = {
                "player_health": 0.8,
                "player_stamina": 0.9,
                "damage_multiplier": 0.9,
                "enemy_health": 1.3,
                "enemy_damage": 1.2,
                "resource_spawn_rate": 0.8
            }
        elif mode == DifficultyMode.NIGHTMARE:
            multipliers = {
                "player_health": 0.6,
                "player_stamina": 0.7,
                "damage_multiplier": 0.8,
                "enemy_health": 1.6,
                "enemy_damage": 1.5,
                "resource_spawn_rate": 0.6
            }
        else:  # CUSTOM
            return  # Don't modify custom settings
        
        # Apply multipliers
        for modifier_name, multiplier in multipliers.items():
            if modifier_name in self.balance_modifiers:
                modifier = self.balance_modifiers[modifier_name]
                modifier.current_value = modifier.base_value * multiplier
    
    def get_balance_value(self, modifier_name: str, context: Dict[str, Any] = None) -> float:
        """Get a balanced value with difficulty and context modifications."""
        if modifier_name not in self.balance_modifiers:
            return 1.0
        
        modifier = self.balance_modifiers[modifier_name]
        base_value = modifier.get_value(context)
        
        # Apply adaptive difficulty
        if self.adaptive_difficulty.adaptation_enabled:
            difficulty_mod = self.adaptive_difficulty.get_difficulty_modifier()
            
            # Different modifiers react differently to difficulty
            if "player" in modifier.category:
                # Player stats get better when difficulty is lower
                base_value *= (2.0 - difficulty_mod)
            elif "enemy" in modifier.category or "combat" in modifier.category:
                # Enemy stats get harder when difficulty is higher
                base_value *= difficulty_mod
            elif "resources" in modifier.category:
                # Resources get more abundant when difficulty is lower
                base_value *= (2.0 - difficulty_mod)
        
        return base_value
    
    def enable_qol_feature(self, feature: QualityOfLifeFeature, enabled: bool = True):
        """Enable or disable a quality of life feature."""
        self.qol_features[feature] = enabled
        print(f"QoL feature {feature.value}: {'enabled' if enabled else 'disabled'}")
    
    def is_qol_enabled(self, feature: QualityOfLifeFeature) -> bool:
        """Check if a quality of life feature is enabled."""
        return self.qol_features.get(feature, False)
    
    def add_context_hint(self, hint_id: str, message: str, position: Tuple[float, float],
                        duration: float = 5.0, priority: int = 1):
        """Add a context-sensitive hint."""
        if not self.is_qol_enabled(QualityOfLifeFeature.CONTEXT_HINTS):
            return
        
        # Check cooldown
        if hint_id in self.hint_cooldowns:
            if time.time() - self.hint_cooldowns[hint_id] < 10.0:  # 10 second cooldown
                return
        
        hint = {
            'id': hint_id,
            'message': message,
            'position': position,
            'duration': duration,
            'priority': priority,
            'start_time': time.time(),
            'alpha': 0.0
        }
        
        # Remove existing hint with same ID
        self.active_hints = [h for h in self.active_hints if h['id'] != hint_id]
        
        # Add new hint (sorted by priority)
        self.active_hints.append(hint)
        self.active_hints.sort(key=lambda h: h['priority'], reverse=True)
        
        # Limit number of hints
        if len(self.active_hints) > 3:
            self.active_hints = self.active_hints[:3]
        
        self.hint_cooldowns[hint_id] = time.time()
    
    def update_camera_focus(self, target_objects: List[Dict[str, Any]]):
        """Update smart camera focus objects."""
        if not self.is_qol_enabled(QualityOfLifeFeature.SMART_CAMERA):
            return
        
        self.camera_focus_objects = target_objects
    
    def get_smart_camera_offset(self) -> Tuple[float, float]:
        """Calculate smart camera offset for better viewing."""
        if not self.camera_focus_objects:
            return (0.0, 0.0)
        
        # Calculate centroid of focus objects
        total_x = sum(obj.get('x', 0) for obj in self.camera_focus_objects)
        total_y = sum(obj.get('y', 0) for obj in self.camera_focus_objects)
        count = len(self.camera_focus_objects)
        
        centroid_x = total_x / count
        centroid_y = total_y / count
        
        # Apply smoothing
        offset_x = centroid_x * self.camera_smoothing
        offset_y = centroid_y * self.camera_smoothing
        
        return (offset_x, offset_y)
    
    def record_gesture(self, direction: float):
        """Record a gesture input for gesture shortcuts."""
        if not self.is_qol_enabled(QualityOfLifeFeature.GESTURE_SHORTCUTS):
            return
        
        current_time = time.time()
        self.gesture_buffer.append((current_time, direction))
        
        # Remove old gestures (older than 2 seconds)
        self.gesture_buffer = [(t, d) for t, d in self.gesture_buffer if current_time - t < 2.0]
        
        # Check for gesture patterns
        self._check_gesture_patterns()
    
    def _check_gesture_patterns(self):
        """Check for recognized gesture patterns."""
        if len(self.gesture_buffer) < 3:
            return
        
        # Get recent directions
        recent_directions = [d for t, d in self.gesture_buffer[-4:]]
        
        # Simple patterns (more complex patterns could be added)
        if len(recent_directions) >= 4:
            # Circle gesture (right, down, left, up)
            if self._is_circle_gesture(recent_directions):
                self._execute_gesture_action("circle")
            
            # Quick save gesture (up, down, up, down)
            elif recent_directions == [0, 180, 0, 180]:  # Assuming 0=up, 180=down
                self._execute_gesture_action("quick_save")
    
    def _is_circle_gesture(self, directions: List[float]) -> bool:
        """Check if directions form a circle gesture."""
        # Simplified circle detection
        expected_sequence = [0, 90, 180, 270]  # Right, Down, Left, Up
        tolerance = 45  # degrees
        
        if len(directions) < 4:
            return False
        
        for i, expected in enumerate(expected_sequence):
            actual = directions[i] if i < len(directions) else 0
            angle_diff = abs(actual - expected)
            if min(angle_diff, 360 - angle_diff) > tolerance:
                return False
        
        return True
    
    def _execute_gesture_action(self, gesture_name: str):
        """Execute action for recognized gesture."""
        if gesture_name == "circle":
            # Open quick menu
            print("Gesture: Quick menu opened")
        elif gesture_name == "quick_save":
            # Quick save
            print("Gesture: Quick save triggered")
        
        # Clear gesture buffer after successful recognition
        self.gesture_buffer.clear()
    
    def check_auto_save(self) -> bool:
        """Check if auto-save should be triggered."""
        if not self.is_qol_enabled(QualityOfLifeFeature.AUTO_SAVE):
            return False
        
        current_time = time.time()
        if current_time - self.last_auto_save >= self.auto_save_interval:
            self.last_auto_save = current_time
            return True
        
        return False
    
    def update_performance_metrics(self, frame_time: float, memory_usage: float,
                                 active_objects: int, draw_calls: int):
        """Update performance metrics for optimization."""
        self.performance_metrics['frame_time'] = frame_time
        self.performance_metrics['memory_usage'] = memory_usage
        self.performance_metrics['active_objects'] = active_objects
        self.performance_metrics['draw_calls'] = draw_calls
        
        # Auto-adjust quality settings if performance is poor
        if self.is_qol_enabled(QualityOfLifeFeature.ADAPTIVE_UI):
            if frame_time > 33.33:  # Below 30 FPS
                self._auto_adjust_quality(False)  # Reduce quality
            elif frame_time < 16.67 and not self.simplified_effects:  # Above 60 FPS
                self._auto_adjust_quality(True)   # Increase quality
    
    def _auto_adjust_quality(self, increase_quality: bool):
        """Automatically adjust quality settings based on performance."""
        if increase_quality:
            self.simplified_effects = False
            print("Performance good - increased visual quality")
        else:
            self.simplified_effects = True
            print("Performance poor - reduced visual quality")
    
    def set_accessibility_option(self, option: str, enabled: bool):
        """Set accessibility options."""
        if option == "colorblind_friendly":
            self.colorblind_friendly = enabled
        elif option == "high_contrast":
            self.high_contrast = enabled
        elif option == "large_text":
            self.large_text = enabled
        elif option == "simplified_effects":
            self.simplified_effects = enabled
        
        print(f"Accessibility option {option}: {'enabled' if enabled else 'disabled'}")
    
    def update(self, dt: float):
        """Update gameplay polish systems."""
        # Update adaptive difficulty
        self.adaptive_difficulty.update_difficulty(dt)
        
        # Update context hints
        current_time = time.time()
        for hint in self.active_hints[:]:
            elapsed = current_time - hint['start_time']
            
            # Fade in/out
            if elapsed < 0.5:
                hint['alpha'] = elapsed / 0.5
            elif elapsed > hint['duration'] - 0.5:
                hint['alpha'] = (hint['duration'] - elapsed) / 0.5
            else:
                hint['alpha'] = 1.0
            
            # Remove expired hints
            if elapsed >= hint['duration']:
                self.active_hints.remove(hint)
    
    def get_active_hints(self) -> List[Dict[str, Any]]:
        """Get currently active context hints."""
        return self.active_hints.copy()
    
    def get_polish_info(self) -> Dict[str, Any]:
        """Get gameplay polish system information."""
        return {
            'difficulty_mode': self.current_difficulty_mode.value,
            'adaptive_difficulty': self.adaptive_difficulty.get_difficulty_modifier(),
            'difficulty_description': self.adaptive_difficulty.get_difficulty_description(),
            'qol_features': {feature.value: enabled for feature, enabled in self.qol_features.items()},
            'active_hints': len(self.active_hints),
            'performance_metrics': self.performance_metrics.copy(),
            'accessibility': {
                'colorblind_friendly': self.colorblind_friendly,
                'high_contrast': self.high_contrast,
                'large_text': self.large_text,
                'simplified_effects': self.simplified_effects
            }
        }