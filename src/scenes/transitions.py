"""
Forest Survival - Scene Transition System
Advanced scene transitions and effects for smooth scene changes.
"""

import pygame
import math
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from abc import ABC, abstractmethod

import config
from src.core.scene_manager import Scene, SceneManager


class TransitionType(Enum):
    """Types of scene transitions."""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    CIRCLE_WIPE = "circle_wipe"
    SPIRAL_WIPE = "spiral_wipe"
    PIXELATE = "pixelate"
    DISSOLVE = "dissolve"
    IRIS_OPEN = "iris_open"
    IRIS_CLOSE = "iris_close"
    FLIP_HORIZONTAL = "flip_horizontal"
    FLIP_VERTICAL = "flip_vertical"


class TransitionDirection(Enum):
    """Direction of transition."""
    IN = "in"
    OUT = "out"
    CROSS = "cross"


class BaseTransition(ABC):
    """Base class for scene transitions."""
    
    def __init__(self, transition_type: TransitionType, duration: float = 1.0):
        self.transition_type = transition_type
        self.duration = duration
        self.progress = 0.0
        self.direction = TransitionDirection.IN
        self.is_active = False
        self.is_complete = False
        
        # Callbacks
        self.on_complete: Optional[Callable] = None
        self.on_halfway: Optional[Callable] = None
        
        # Easing
        self.easing_function = self._ease_in_out_cubic
        
        # Surfaces for rendering
        self.from_surface: Optional[pygame.Surface] = None
        self.to_surface: Optional[pygame.Surface] = None
    
    def start(self, direction: TransitionDirection = TransitionDirection.IN, 
             from_surface: pygame.Surface = None, to_surface: pygame.Surface = None):
        """Start the transition."""
        self.direction = direction
        self.progress = 0.0
        self.is_active = True
        self.is_complete = False
        
        if from_surface:
            self.from_surface = from_surface.copy()
        if to_surface:
            self.to_surface = to_surface.copy()
    
    def update(self, dt: float) -> bool:
        """Update transition progress. Returns True when complete."""
        if not self.is_active or self.is_complete:
            return self.is_complete
        
        self.progress += dt / self.duration
        
        # Check for halfway point
        if self.progress >= 0.5 and self.on_halfway:
            self.on_halfway()
            self.on_halfway = None  # Call only once
        
        if self.progress >= 1.0:
            self.progress = 1.0
            self.is_complete = True
            self.is_active = False
            
            if self.on_complete:
                self.on_complete()
        
        return self.is_complete
    
    def _ease_in_out_cubic(self, t: float) -> float:
        """Cubic easing function."""
        if t < 0.5:
            return 4 * t * t * t
        else:
            p = 2 * t - 2
            return 1 + p * p * p / 2
    
    def _ease_out_bounce(self, t: float) -> float:
        """Bounce easing function."""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375
    
    def get_eased_progress(self) -> float:
        """Get eased progress value."""
        return self.easing_function(self.progress)
    
    @abstractmethod
    def render(self, surface: pygame.Surface):
        """Render the transition effect."""
        pass


class FadeTransition(BaseTransition):
    """Fade in/out transition."""
    
    def __init__(self, duration: float = 1.0, fade_color: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__(TransitionType.FADE, duration)
        self.fade_color = fade_color
    
    def render(self, surface: pygame.Surface):
        """Render fade transition."""
        if not self.is_active:
            return
        
        eased_progress = self.get_eased_progress()
        
        if self.direction == TransitionDirection.OUT:
            alpha = int(255 * eased_progress)
        else:  # IN
            alpha = int(255 * (1.0 - eased_progress))
        
        # Create fade surface
        fade_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((*self.fade_color, alpha))
        surface.blit(fade_surface, (0, 0))


class SlideTransition(BaseTransition):
    """Slide transition in any direction."""
    
    def __init__(self, direction: str, duration: float = 1.0):
        transition_type = getattr(TransitionType, f"SLIDE_{direction.upper()}")
        super().__init__(transition_type, duration)
        self.slide_direction = direction.lower()
    
    def render(self, surface: pygame.Surface):
        """Render slide transition."""
        if not self.is_active:
            return
        
        eased_progress = self.get_eased_progress()
        
        # Calculate offset based on direction
        if self.slide_direction == "left":
            offset_x = -config.SCREEN_WIDTH * eased_progress
            offset_y = 0
        elif self.slide_direction == "right":
            offset_x = config.SCREEN_WIDTH * eased_progress
            offset_y = 0
        elif self.slide_direction == "up":
            offset_x = 0
            offset_y = -config.SCREEN_HEIGHT * eased_progress
        elif self.slide_direction == "down":
            offset_x = 0
            offset_y = config.SCREEN_HEIGHT * eased_progress
        
        # Render surfaces
        if self.from_surface and self.to_surface:
            # Cross-slide
            surface.blit(self.from_surface, (offset_x, offset_y))
            
            # Calculate opposite offset for incoming surface
            if self.slide_direction == "left":
                to_offset_x = config.SCREEN_WIDTH + offset_x
                to_offset_y = 0
            elif self.slide_direction == "right":
                to_offset_x = -config.SCREEN_WIDTH + offset_x
                to_offset_y = 0
            elif self.slide_direction == "up":
                to_offset_x = 0
                to_offset_y = config.SCREEN_HEIGHT + offset_y
            elif self.slide_direction == "down":
                to_offset_x = 0
                to_offset_y = -config.SCREEN_HEIGHT + offset_y
            
            surface.blit(self.to_surface, (to_offset_x, to_offset_y))
        else:
            # Single surface slide
            slide_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            slide_surface.fill(config.COLORS['black'])
            surface.blit(slide_surface, (offset_x, offset_y))


class ZoomTransition(BaseTransition):
    """Zoom in/out transition."""
    
    def __init__(self, zoom_type: str, duration: float = 1.0):
        transition_type = getattr(TransitionType, f"ZOOM_{zoom_type.upper()}")
        super().__init__(transition_type, duration)
        self.zoom_type = zoom_type.lower()
    
    def render(self, surface: pygame.Surface):
        """Render zoom transition."""
        if not self.is_active:
            return
        
        eased_progress = self.get_eased_progress()
        
        if self.zoom_type == "in":
            scale = eased_progress
        else:  # out
            scale = 1.0 - eased_progress
        
        if scale <= 0:
            # Completely zoomed out - show black
            surface.fill(config.COLORS['black'])
            return
        
        # Calculate scaled dimensions
        scaled_width = int(config.SCREEN_WIDTH * scale)
        scaled_height = int(config.SCREEN_HEIGHT * scale)
        
        if scaled_width <= 0 or scaled_height <= 0:
            surface.fill(config.COLORS['black'])
            return
        
        # Create zoomed surface
        if self.from_surface:
            zoomed_surface = pygame.transform.scale(self.from_surface, (scaled_width, scaled_height))
        else:
            zoomed_surface = pygame.Surface((scaled_width, scaled_height))
            zoomed_surface.fill(config.COLORS['black'])
        
        # Center the zoomed surface
        zoom_rect = zoomed_surface.get_rect()
        zoom_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        
        # Fill background
        surface.fill(config.COLORS['black'])
        surface.blit(zoomed_surface, zoom_rect)


class CircleWipeTransition(BaseTransition):
    """Circle wipe transition."""
    
    def __init__(self, duration: float = 1.0, center: Tuple[int, int] = None):
        super().__init__(TransitionType.CIRCLE_WIPE, duration)
        self.center = center or (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.max_radius = math.sqrt(config.SCREEN_WIDTH**2 + config.SCREEN_HEIGHT**2) / 2
    
    def render(self, surface: pygame.Surface):
        """Render circle wipe transition."""
        if not self.is_active:
            return
        
        eased_progress = self.get_eased_progress()
        
        if self.direction == TransitionDirection.OUT:
            radius = int(self.max_radius * (1.0 - eased_progress))
        else:  # IN
            radius = int(self.max_radius * eased_progress)
        
        # Create mask surface
        mask_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 255))
        
        if radius > 0:
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), self.center, radius)
        
        surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)


class PixelateTransition(BaseTransition):
    """Pixelate transition effect."""
    
    def __init__(self, duration: float = 1.0, max_pixel_size: int = 32):
        super().__init__(TransitionType.PIXELATE, duration)
        self.max_pixel_size = max_pixel_size
    
    def render(self, surface: pygame.Surface):
        """Render pixelate transition."""
        if not self.is_active:
            return
        
        eased_progress = self.get_eased_progress()
        
        # Calculate current pixel size
        if self.direction == TransitionDirection.OUT:
            pixel_size = int(self.max_pixel_size * eased_progress)
        else:  # IN
            pixel_size = int(self.max_pixel_size * (1.0 - eased_progress))
        
        if pixel_size <= 1:
            return  # No pixelation
        
        # Create pixelated version
        small_width = max(1, config.SCREEN_WIDTH // pixel_size)
        small_height = max(1, config.SCREEN_HEIGHT // pixel_size)
        
        # Scale down
        small_surface = pygame.transform.scale(surface, (small_width, small_height))
        
        # Scale back up with nearest neighbor (pixelated effect)
        pixelated_surface = pygame.transform.scale(small_surface, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        
        surface.blit(pixelated_surface, (0, 0))


class DissolveTransition(BaseTransition):
    """Dissolve transition with noise pattern."""
    
    def __init__(self, duration: float = 1.0):
        super().__init__(TransitionType.DISSOLVE, duration)
        self.noise_pattern = self._generate_noise_pattern()
    
    def _generate_noise_pattern(self) -> List[List[float]]:
        """Generate random noise pattern for dissolve effect."""
        import random
        
        pattern = []
        for y in range(config.SCREEN_HEIGHT):
            row = []
            for x in range(config.SCREEN_WIDTH):
                row.append(random.random())
            pattern.append(row)
        return pattern
    
    def render(self, surface: pygame.Surface):
        """Render dissolve transition."""
        if not self.is_active:
            return
        
        eased_progress = self.get_eased_progress()
        
        # Create dissolve mask
        mask_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for y in range(0, config.SCREEN_HEIGHT, 2):  # Skip pixels for performance
            for x in range(0, config.SCREEN_WIDTH, 2):
                if y < len(self.noise_pattern) and x < len(self.noise_pattern[y]):
                    noise_value = self.noise_pattern[y][x]
                    
                    if self.direction == TransitionDirection.OUT:
                        if noise_value < eased_progress:
                            pygame.draw.rect(mask_surface, (0, 0, 0, 255), (x, y, 2, 2))
                    else:  # IN
                        if noise_value > eased_progress:
                            pygame.draw.rect(mask_surface, (0, 0, 0, 255), (x, y, 2, 2))
        
        surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)


class TransitionManager:
    """
    Manages scene transitions and effects.
    """
    
    def __init__(self):
        self.current_transition: Optional[BaseTransition] = None
        self.transition_queue: List[Tuple[BaseTransition, Callable]] = []
        
        # Pre-capture surfaces for smooth transitions
        self.scene_capture: Optional[pygame.Surface] = None
        
        # Default transition settings
        self.default_duration = 1.0
        self.default_transition_type = TransitionType.FADE
    
    def start_transition(self, transition_type: TransitionType, duration: float = None, 
                        direction: TransitionDirection = TransitionDirection.IN,
                        on_complete: Callable = None, **kwargs) -> BaseTransition:
        """Start a new transition."""
        if duration is None:
            duration = self.default_duration
        
        # Create appropriate transition
        transition = self._create_transition(transition_type, duration, **kwargs)
        transition.direction = direction
        transition.on_complete = on_complete
        
        # Capture current scene if needed
        if self.scene_capture:
            transition.from_surface = self.scene_capture
        
        transition.start(direction)
        self.current_transition = transition
        
        return transition
    
    def _create_transition(self, transition_type: TransitionType, duration: float, **kwargs) -> BaseTransition:
        """Create transition object based on type."""
        if transition_type == TransitionType.FADE:
            return FadeTransition(duration, kwargs.get('fade_color', (0, 0, 0)))
        
        elif transition_type in [TransitionType.SLIDE_LEFT, TransitionType.SLIDE_RIGHT, 
                               TransitionType.SLIDE_UP, TransitionType.SLIDE_DOWN]:
            direction = transition_type.value.split('_')[1]
            return SlideTransition(direction, duration)
        
        elif transition_type in [TransitionType.ZOOM_IN, TransitionType.ZOOM_OUT]:
            zoom_type = transition_type.value.split('_')[1]
            return ZoomTransition(zoom_type, duration)
        
        elif transition_type == TransitionType.CIRCLE_WIPE:
            return CircleWipeTransition(duration, kwargs.get('center'))
        
        elif transition_type == TransitionType.PIXELATE:
            return PixelateTransition(duration, kwargs.get('max_pixel_size', 32))
        
        elif transition_type == TransitionType.DISSOLVE:
            return DissolveTransition(duration)
        
        else:
            # Default to fade
            return FadeTransition(duration)
    
    def queue_transition(self, transition_type: TransitionType, duration: float = None,
                        on_complete: Callable = None, **kwargs):
        """Queue a transition to play after current one completes."""
        if duration is None:
            duration = self.default_duration
        
        transition = self._create_transition(transition_type, duration, **kwargs)
        self.transition_queue.append((transition, on_complete))
    
    def capture_scene(self, surface: pygame.Surface):
        """Capture current scene for smooth transitions."""
        self.scene_capture = surface.copy()
    
    def update(self, dt: float) -> bool:
        """Update current transition. Returns True if transition is active."""
        if self.current_transition:
            is_complete = self.current_transition.update(dt)
            
            if is_complete:
                self.current_transition = None
                
                # Start next queued transition
                if self.transition_queue:
                    transition, callback = self.transition_queue.pop(0)
                    transition.start()
                    if callback:
                        transition.on_complete = callback
                    self.current_transition = transition
        
        return self.current_transition is not None
    
    def render(self, surface: pygame.Surface):
        """Render current transition effect."""
        if self.current_transition:
            self.current_transition.render(surface)
    
    def is_transitioning(self) -> bool:
        """Check if a transition is currently active."""
        return self.current_transition is not None
    
    def skip_transition(self):
        """Skip current transition to completion."""
        if self.current_transition:
            self.current_transition.progress = 1.0
            self.current_transition.update(0)
    
    def clear_transitions(self):
        """Clear all transitions."""
        self.current_transition = None
        self.transition_queue.clear()
    
    def get_preset_transitions(self) -> Dict[str, Dict]:
        """Get preset transition configurations."""
        return {
            'quick_fade': {
                'type': TransitionType.FADE,
                'duration': 0.3,
                'fade_color': (0, 0, 0)
            },
            'slow_fade': {
                'type': TransitionType.FADE,
                'duration': 2.0,
                'fade_color': (0, 0, 0)
            },
            'slide_left_fast': {
                'type': TransitionType.SLIDE_LEFT,
                'duration': 0.5
            },
            'slide_right_fast': {
                'type': TransitionType.SLIDE_RIGHT,
                'duration': 0.5
            },
            'zoom_dramatic': {
                'type': TransitionType.ZOOM_OUT,
                'duration': 1.5
            },
            'circle_wipe_center': {
                'type': TransitionType.CIRCLE_WIPE,
                'duration': 1.0,
                'center': (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
            },
            'pixelate_retro': {
                'type': TransitionType.PIXELATE,
                'duration': 0.8,
                'max_pixel_size': 16
            },
            'dissolve_mysterious': {
                'type': TransitionType.DISSOLVE,
                'duration': 1.2
            }
        }
    
    def apply_preset(self, preset_name: str, on_complete: Callable = None) -> bool:
        """Apply a preset transition configuration."""
        presets = self.get_preset_transitions()
        
        if preset_name not in presets:
            return False
        
        preset = presets[preset_name]
        transition_type = preset.pop('type')
        duration = preset.pop('duration', self.default_duration)
        
        self.start_transition(transition_type, duration, on_complete=on_complete, **preset)
        return True