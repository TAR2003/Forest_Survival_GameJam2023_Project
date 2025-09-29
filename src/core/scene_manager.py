"""
Forest Survival - Scene Manager
Manages game scenes and transitions between them.
"""

import pygame
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

import config


class BaseScene(ABC):
    """
    Abstract base class for all game scenes.
    """
    
    def __init__(self):
        """Initialize the scene."""
        self.next_scene = None
        self.scene_data = {}
    
    @abstractmethod
    def update(self, delta_time: float):
        """
        Update scene logic.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """
        Render the scene.
        
        Args:
            screen: Screen surface to render on
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
        """
        pass
    
    def enter_scene(self, previous_scene: Optional[str] = None, data: Optional[Dict] = None):
        """
        Called when entering this scene.
        
        Args:
            previous_scene: Name of the previous scene
            data: Optional data passed from previous scene
        """
        if data:
            self.scene_data.update(data)
    
    def exit_scene(self) -> Optional[Dict]:
        """
        Called when exiting this scene.
        
        Returns:
            Optional data to pass to next scene
        """
        return None
    
    def change_scene(self, scene_name: str, data: Optional[Dict] = None):
        """
        Request scene change.
        
        Args:
            scene_name: Name of scene to change to
            data: Optional data to pass to next scene
        """
        self.next_scene = (scene_name, data)
    
    def get_next_scene(self) -> Optional[tuple]:
        """Get next scene request and clear it."""
        next_scene = self.next_scene
        self.next_scene = None
        return next_scene


class SceneTransition:
    """Handles smooth transitions between scenes."""
    
    def __init__(self, transition_type: str = 'fade', duration: float = 0.5):
        """
        Initialize scene transition.
        
        Args:
            transition_type: Type of transition ('fade', 'slide', 'zoom')
            duration: Transition duration in seconds
        """
        self.transition_type = transition_type
        self.duration = duration
        self.current_time = 0.0
        self.active = False
        self.direction = 'out'  # 'out' or 'in'
        self.from_surface = None
        self.to_surface = None
    
    def start_transition(self, from_surface: pygame.Surface, to_surface: pygame.Surface):
        """Start transition between two scene surfaces."""
        self.from_surface = from_surface.copy()
        self.to_surface = to_surface.copy()
        self.current_time = 0.0
        self.active = True
        self.direction = 'out'
    
    def update(self, delta_time: float) -> bool:
        """
        Update transition.
        
        Args:
            delta_time: Time since last frame
            
        Returns:
            True if transition is complete
        """
        if not self.active:
            return True
        
        self.current_time += delta_time
        
        if self.current_time >= self.duration:
            self.active = False
            return True
        
        return False
    
    def render(self, screen: pygame.Surface):
        """Render transition effect."""
        if not self.active or not self.from_surface or not self.to_surface:
            return
        
        progress = self.current_time / self.duration
        
        if self.transition_type == 'fade':
            self._render_fade(screen, progress)
        elif self.transition_type == 'slide':
            self._render_slide(screen, progress)
        elif self.transition_type == 'zoom':
            self._render_zoom(screen, progress)
    
    def _render_fade(self, screen: pygame.Surface, progress: float):
        """Render fade transition."""
        screen.blit(self.from_surface, (0, 0))
        
        # Create alpha surface for to_surface
        alpha_surface = self.to_surface.copy()
        alpha_value = int(255 * progress)
        alpha_surface.set_alpha(alpha_value)
        screen.blit(alpha_surface, (0, 0))
    
    def _render_slide(self, screen: pygame.Surface, progress: float):
        """Render slide transition."""
        screen_width = screen.get_width()
        offset = int(screen_width * progress)
        
        # Slide from surface out to the left
        screen.blit(self.from_surface, (-offset, 0))
        
        # Slide to surface in from the right
        screen.blit(self.to_surface, (screen_width - offset, 0))
    
    def _render_zoom(self, screen: pygame.Surface, progress: float):
        """Render zoom transition."""
        screen.blit(self.from_surface, (0, 0))
        
        # Scale and center the to_surface
        scale = progress
        if scale > 0:
            scaled_size = (
                int(self.to_surface.get_width() * scale),
                int(self.to_surface.get_height() * scale)
            )
            scaled_surface = pygame.transform.scale(self.to_surface, scaled_size)
            
            # Center the scaled surface
            x = (screen.get_width() - scaled_size[0]) // 2
            y = (screen.get_height() - scaled_size[1]) // 2
            screen.blit(scaled_surface, (x, y))


class SceneManager:
    """
    Manages game scenes and handles transitions between them.
    """
    
    def __init__(self):
        """Initialize the scene manager."""
        self.scenes: Dict[str, BaseScene] = {}
        self.current_scene: Optional[BaseScene] = None
        self.current_scene_name: Optional[str] = None
        self.transition: Optional[SceneTransition] = None
        self.should_quit = False
        
        print("Scene Manager initialized")
    
    def register_scene(self, name: str, scene: BaseScene):
        """
        Register a scene with the manager.
        
        Args:
            name: Scene name identifier
            scene: Scene instance
        """
        self.scenes[name] = scene
        print(f"Scene '{name}' registered")
    
    def change_scene(self, scene_name: str, data: Optional[Dict] = None, 
                    transition_type: str = 'fade', transition_duration: float = 0.5):
        """
        Change to a different scene.
        
        Args:
            scene_name: Name of scene to change to
            data: Optional data to pass to new scene
            transition_type: Type of transition effect
            transition_duration: Duration of transition in seconds
        """
        if scene_name == 'quit':
            self.should_quit = True
            return
        
        if scene_name not in self.scenes:
            print(f"Warning: Scene '{scene_name}' not found")
            return
        
        new_scene = self.scenes[scene_name]
        
        # Handle scene exit
        exit_data = None
        if self.current_scene:
            exit_data = self.current_scene.exit_scene()
        
        # Merge exit data with passed data
        final_data = exit_data or {}
        if data:
            final_data.update(data)
        
        # Set up transition if both scenes exist
        if (self.current_scene and transition_duration > 0 and 
            hasattr(pygame, 'display') and pygame.display.get_surface()):
            
            # Create transition
            self.transition = SceneTransition(transition_type, transition_duration)
            
            # Render current scene to surface for transition
            screen = pygame.display.get_surface()
            from_surface = screen.copy()
            
            # Temporarily switch to new scene to render it
            old_scene = self.current_scene
            self.current_scene = new_scene
            self.current_scene.enter_scene(self.current_scene_name, final_data)
            
            # Render new scene
            screen.fill((0, 0, 0))
            new_scene.render(screen)
            to_surface = screen.copy()
            
            # Start transition
            self.transition.start_transition(from_surface, to_surface)
            
            # Restore old scene temporarily for transition
            self.current_scene = old_scene
        else:
            # Direct scene change without transition
            self.current_scene = new_scene
            self.current_scene_name = scene_name
            self.current_scene.enter_scene(self.current_scene_name, final_data)
        
        print(f"Changed to scene: {scene_name}")
    
    def update(self, delta_time: float):
        """
        Update current scene and transitions.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        # Update transition
        if self.transition and self.transition.active:
            transition_complete = self.transition.update(delta_time)
            if transition_complete:
                # Transition finished, complete scene change
                self._complete_scene_change()
        
        # Update current scene
        if self.current_scene:
            self.current_scene.update(delta_time)
    
    def _complete_scene_change(self):
        """Complete scene change after transition."""
        if self.transition:
            # Extract scene info from transition completion
            # This would be set during change_scene call
            self.transition = None
    
    def render(self, screen: pygame.Surface):
        """
        Render current scene and transitions.
        
        Args:
            screen: Screen surface to render on
        """
        # Render transition if active
        if self.transition and self.transition.active:
            self.transition.render(screen)
        else:
            # Render current scene
            if self.current_scene:
                self.current_scene.render(screen)
    
    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events for current scene.
        
        Args:
            event: Pygame event
        """
        # Don't pass events during transitions
        if self.transition and self.transition.active:
            return
        
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def get_current_scene_name(self) -> Optional[str]:
        """Get name of current scene."""
        return self.current_scene_name
    
    def get_scene(self, name: str) -> Optional[BaseScene]:
        """Get scene by name."""
        return self.scenes.get(name)
    
    def pause_current_scene(self):
        """Pause current scene (if it supports pausing)."""
        if self.current_scene and hasattr(self.current_scene, 'pause'):
            self.current_scene.pause()
    
    def resume_current_scene(self):
        """Resume current scene (if it supports pausing)."""
        if self.current_scene and hasattr(self.current_scene, 'resume'):
            self.current_scene.resume()
    
    def cleanup(self):
        """Clean up scene manager resources."""
        # Clean up current scene
        if self.current_scene and hasattr(self.current_scene, 'cleanup'):
            self.current_scene.cleanup()
        
        # Clean up all registered scenes
        for scene in self.scenes.values():
            if hasattr(scene, 'cleanup'):
                scene.cleanup()
        
        self.scenes.clear()
        self.current_scene = None
        print("Scene Manager cleaned up")
    
    def get_scene_stack_info(self) -> Dict[str, Any]:
        """Get information about scene stack for debugging."""
        return {
            'current_scene': self.current_scene_name,
            'registered_scenes': list(self.scenes.keys()),
            'transition_active': self.transition is not None and self.transition.active,
            'should_quit': self.should_quit
        }