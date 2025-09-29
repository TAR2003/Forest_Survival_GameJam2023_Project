"""
Forest Survival - Menu Scene System
Complete menu scenes with navigation, animations, and transitions.
"""

import pygame
import math
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum

import config
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.core.scene_manager import Scene, SceneManager
from src.scenes.main_menu import MainMenuScene
from src.scenes.settings_menu import SettingsScene


class MenuTransition(Enum):
    """Menu transition types."""
    NONE = "none"
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class AnimatedMenuElement:
    """Base class for animated menu elements."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Animation properties
        self.target_x = x
        self.target_y = y
        self.target_scale = 1.0
        self.target_alpha = 255
        
        self.current_scale = 1.0
        self.current_alpha = 255
        
        # Animation timing
        self.animation_speed = 5.0
        self.is_animating = False
        
        # Visual effects
        self.glow_intensity = 0.0
        self.rotation = 0.0
        
        # State
        self.visible = True
        self.enabled = True
    
    def animate_to(self, x: float = None, y: float = None, scale: float = None, alpha: float = None):
        """Animate to new values."""
        if x is not None:
            self.target_x = x
        if y is not None:
            self.target_y = y
        if scale is not None:
            self.target_scale = scale
        if alpha is not None:
            self.target_alpha = alpha
        
        self.is_animating = True
    
    def update_animations(self, dt: float):
        """Update animation values."""
        if not self.is_animating:
            return
        
        # Smooth interpolation
        lerp_speed = self.animation_speed * dt
        
        # Position
        self.x += (self.target_x - self.x) * lerp_speed
        self.y += (self.target_y - self.y) * lerp_speed
        
        # Scale
        self.current_scale += (self.target_scale - self.current_scale) * lerp_speed
        
        # Alpha
        self.current_alpha += (self.target_alpha - self.current_alpha) * lerp_speed
        
        # Check if animation is complete
        tolerance = 0.01
        if (abs(self.x - self.target_x) < tolerance and
            abs(self.y - self.target_y) < tolerance and
            abs(self.current_scale - self.target_scale) < tolerance and
            abs(self.current_alpha - self.target_alpha) < tolerance):
            
            # Snap to final values
            self.x = self.target_x
            self.y = self.target_y
            self.current_scale = self.target_scale
            self.current_alpha = self.target_alpha
            
            self.is_animating = False
    
    def get_render_rect(self) -> pygame.Rect:
        """Get rectangle for rendering with scale applied."""
        scaled_width = self.width * self.current_scale
        scaled_height = self.height * self.current_scale
        
        return pygame.Rect(
            self.x - scaled_width / 2,
            self.y - scaled_height / 2,
            scaled_width,
            scaled_height
        )


class MenuButton(AnimatedMenuElement):
    """Animated menu button with hover effects."""
    
    def __init__(self, x: float, y: float, width: float, height: float, text: str, action: Callable = None):
        super().__init__(x, y, width, height)
        
        self.text = text
        self.action = action
        
        # Visual properties
        self.background_color = config.COLORS['dark_blue']
        self.border_color = config.COLORS['cyan']
        self.text_color = config.COLORS['white']
        self.hover_color = config.COLORS['yellow']
        
        # State
        self.is_hovered = False
        self.is_pressed = False
        self.is_selected = False
        
        # Font
        self.font = pygame.font.Font(None, 32)
        
        # Effects
        self.hover_pulse = 0.0
        self.press_animation = 0.0
    
    def set_selected(self, selected: bool):
        """Set button selection state."""
        self.is_selected = selected
        
        if selected:
            self.animate_to(scale=1.1, alpha=255)
        else:
            self.animate_to(scale=1.0, alpha=200)
    
    def set_hovered(self, hovered: bool):
        """Set button hover state."""
        if self.is_hovered != hovered:
            self.is_hovered = hovered
            
            if hovered:
                self.animate_to(scale=1.05)
            else:
                self.animate_to(scale=1.0 if not self.is_selected else 1.1)
    
    def press(self):
        """Press button."""
        self.is_pressed = True
        self.press_animation = 1.0
        
        if self.action:
            self.action()
    
    def update(self, dt: float):
        """Update button animations."""
        self.update_animations(dt)
        
        # Hover pulse effect
        if self.is_hovered or self.is_selected:
            self.hover_pulse += dt * 4
        else:
            self.hover_pulse = 0.0
        
        # Press animation
        if self.press_animation > 0:
            self.press_animation = max(0.0, self.press_animation - dt * 5)
    
    def render(self, surface: pygame.Surface):
        """Render the button."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Apply press animation
        if self.press_animation > 0:
            press_offset = int(5 * self.press_animation)
            render_rect.x += press_offset
            render_rect.y += press_offset
        
        # Background
        bg_color = self.background_color
        if self.is_hovered or self.is_selected:
            # Pulse effect
            pulse_intensity = (math.sin(self.hover_pulse) + 1) / 2
            bg_color = self._blend_colors(bg_color, self.hover_color, pulse_intensity * 0.3)
        
        # Create surface with alpha
        button_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        button_surface.fill((*bg_color, int(self.current_alpha)))
        surface.blit(button_surface, render_rect.topleft)
        
        # Border
        border_color = self.border_color
        if self.is_selected:
            border_color = self.hover_color
        
        border_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, (*border_color, int(self.current_alpha)), 
                        pygame.Rect(0, 0, render_rect.width, render_rect.height), 3)
        surface.blit(border_surface, render_rect.topleft)
        
        # Text
        text_color = self.text_color
        if self.is_selected:
            text_color = self.hover_color
        
        text_surface = self.font.render(self.text, True, text_color)
        text_surface.set_alpha(int(self.current_alpha))
        
        text_rect = text_surface.get_rect(center=render_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Glow effect for selected button
        if self.is_selected and self.hover_pulse > 0:
            glow_intensity = (math.sin(self.hover_pulse) + 1) / 2
            glow_size = int(10 * glow_intensity)
            
            if glow_size > 0:
                glow_rect = render_rect.inflate(glow_size * 2, glow_size * 2)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                
                for i in range(glow_size):
                    alpha = int(50 * (1 - i / glow_size) * glow_intensity)
                    pygame.draw.rect(glow_surface, (*self.hover_color, alpha),
                                   pygame.Rect(i, i, glow_rect.width - i*2, glow_rect.height - i*2), 1)
                
                surface.blit(glow_surface, glow_rect.topleft)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is inside button."""
        render_rect = self.get_render_rect()
        return render_rect.collidepoint(x, y)


class MenuTitle(AnimatedMenuElement):
    """Animated menu title with effects."""
    
    def __init__(self, x: float, y: float, text: str):
        # Calculate size based on text
        font = pygame.font.Font(None, 72)
        text_rect = font.get_rect(text)
        
        super().__init__(x, y, text_rect.width, text_rect.height)
        
        self.text = text
        self.font = font
        
        # Visual properties
        self.text_color = config.COLORS['white']
        self.shadow_color = config.COLORS['black']
        self.glow_color = config.COLORS['cyan']
        
        # Animation
        self.wave_offset = 0.0
        self.glow_pulse = 0.0
        self.character_delays: List[float] = []
        
        # Initialize character delays for wave effect
        for i in range(len(text)):
            self.character_delays.append(i * 0.1)
    
    def update(self, dt: float):
        """Update title animations."""
        self.update_animations(dt)
        
        # Wave animation
        self.wave_offset += dt * 2
        
        # Glow pulse
        self.glow_pulse += dt * 1.5
    
    def render(self, surface: pygame.Surface):
        """Render animated title."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Render each character with wave effect
        current_x = render_rect.x
        
        for i, char in enumerate(self.text):
            if char == ' ':
                current_x += self.font.size(' ')[0] * self.current_scale
                continue
            
            # Calculate wave offset for this character
            char_wave = math.sin(self.wave_offset + self.character_delays[i]) * 10
            char_y = render_rect.y + char_wave
            
            # Glow effect
            glow_intensity = (math.sin(self.glow_pulse + i * 0.3) + 1) / 2
            char_glow = int(glow_intensity * 50)
            
            # Render character shadow
            shadow_surface = self.font.render(char, True, self.shadow_color)
            shadow_surface.set_alpha(int(self.current_alpha * 0.5))
            shadow_surface = pygame.transform.scale(shadow_surface, 
                                                   (int(shadow_surface.get_width() * self.current_scale),
                                                    int(shadow_surface.get_height() * self.current_scale)))
            surface.blit(shadow_surface, (current_x + 3, char_y + 3))
            
            # Render character glow
            if char_glow > 0:
                glow_surface = self.font.render(char, True, self.glow_color)
                glow_surface.set_alpha(char_glow)
                glow_surface = pygame.transform.scale(glow_surface,
                                                     (int(glow_surface.get_width() * self.current_scale),
                                                      int(glow_surface.get_height() * self.current_scale)))
                
                # Render glow in multiple positions for blur effect
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            surface.blit(glow_surface, (current_x + dx, char_y + dy))
            
            # Render main character
            char_surface = self.font.render(char, True, self.text_color)
            char_surface.set_alpha(int(self.current_alpha))
            char_surface = pygame.transform.scale(char_surface,
                                                 (int(char_surface.get_width() * self.current_scale),
                                                  int(char_surface.get_height() * self.current_scale)))
            surface.blit(char_surface, (current_x, char_y))
            
            current_x += char_surface.get_width()


class MenuBackground:
    """Animated menu background with effects."""
    
    def __init__(self):
        # Particle system
        self.particles: List[Dict] = []
        self.max_particles = 50
        
        # Background layers
        self.bg_scroll_speed = 20.0
        self.bg_offset = 0.0
        
        # Color animation
        self.color_shift = 0.0
        
        # Effects
        self.gradient_angle = 0.0
        
        self._generate_particles()
    
    def _generate_particles(self):
        """Generate background particles."""
        import random
        
        for _ in range(self.max_particles):
            particle = {
                'x': random.uniform(0, config.SCREEN_WIDTH),
                'y': random.uniform(0, config.SCREEN_HEIGHT),
                'vx': random.uniform(-30, 30),
                'vy': random.uniform(-30, 30),
                'size': random.uniform(1, 4),
                'alpha': random.uniform(50, 150),
                'color': random.choice([config.COLORS['cyan'], config.COLORS['blue'], config.COLORS['white']]),
                'pulse_speed': random.uniform(1, 3),
                'pulse_offset': random.uniform(0, math.pi * 2)
            }
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update background animations."""
        import random
        
        # Update background scroll
        self.bg_offset += self.bg_scroll_speed * dt
        
        # Update color shift
        self.color_shift += dt * 0.5
        
        # Update gradient rotation
        self.gradient_angle += dt * 10
        
        # Update particles
        for particle in self.particles:
            # Move particle
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Wrap around screen
            if particle['x'] < -10:
                particle['x'] = config.SCREEN_WIDTH + 10
            elif particle['x'] > config.SCREEN_WIDTH + 10:
                particle['x'] = -10
            
            if particle['y'] < -10:
                particle['y'] = config.SCREEN_HEIGHT + 10
            elif particle['y'] > config.SCREEN_HEIGHT + 10:
                particle['y'] = -10
            
            # Update pulse
            pulse = math.sin(time.time() * particle['pulse_speed'] + particle['pulse_offset'])
            particle['current_alpha'] = particle['alpha'] + pulse * 30
    
    def render(self, surface: pygame.Surface):
        """Render background."""
        # Clear with base color
        base_color = config.COLORS['dark_blue']
        surface.fill(base_color)
        
        # Render animated gradient
        self._render_gradient(surface)
        
        # Render particles
        for particle in self.particles:
            if particle['current_alpha'] > 0:
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                
                alpha = max(0, min(255, int(particle['current_alpha'])))
                color_with_alpha = (*particle['color'], alpha)
                
                pygame.draw.circle(particle_surface, color_with_alpha,
                                 (int(particle['size']), int(particle['size'])),
                                 int(particle['size']))
                
                surface.blit(particle_surface, (int(particle['x'] - particle['size']),
                                              int(particle['y'] - particle['size'])))
    
    def _render_gradient(self, surface: pygame.Surface):
        """Render animated gradient background."""
        # Create gradient effect
        gradient_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Animated colors
        color1 = self._get_animated_color(config.COLORS['dark_blue'], 0.0)
        color2 = self._get_animated_color(config.COLORS['black'], 1.0)
        
        # Simple vertical gradient
        for y in range(config.SCREEN_HEIGHT):
            progress = y / config.SCREEN_HEIGHT
            r = int(color1[0] + (color2[0] - color1[0]) * progress)
            g = int(color1[1] + (color2[1] - color1[1]) * progress)
            b = int(color1[2] + (color2[2] - color1[2]) * progress)
            
            pygame.draw.line(gradient_surface, (r, g, b, 100), (0, y), (config.SCREEN_WIDTH, y))
        
        surface.blit(gradient_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _get_animated_color(self, base_color: Tuple[int, int, int], offset: float) -> Tuple[int, int, int]:
        """Get animated color variation."""
        shift = math.sin(self.color_shift + offset * math.pi) * 0.2
        
        r = max(0, min(255, int(base_color[0] * (1 + shift))))
        g = max(0, min(255, int(base_color[1] * (1 + shift))))
        b = max(0, min(255, int(base_color[2] * (1 + shift))))
        
        return (r, g, b)


class GameMenuScene(Scene):
    """
    Base class for game menu scenes with common functionality.
    """
    
    def __init__(self, name: str, scene_manager: SceneManager, input_manager: InputManager, audio_manager: AudioManager):
        super().__init__(name)
        self.scene_manager = scene_manager
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        
        # Menu elements
        self.buttons: List[MenuButton] = []
        self.title: Optional[MenuTitle] = None
        self.background = MenuBackground()
        
        # Navigation
        self.selected_index = 0
        self.navigation_enabled = True
        
        # Transitions
        self.enter_transition_timer = 0.0
        self.exit_transition_timer = 0.0
        self.is_entering = True
        self.is_exiting = False
        
        # Input handling
        self.input_delay = 0.0
        self.input_repeat_delay = 0.15
    
    def add_button(self, x: float, y: float, width: float, height: float, text: str, action: Callable = None):
        """Add a button to the menu."""
        button = MenuButton(x, y, width, height, text, action)
        self.buttons.append(button)
        
        # Set first button as selected
        if len(self.buttons) == 1:
            button.set_selected(True)
        
        return button
    
    def set_title(self, x: float, y: float, text: str):
        """Set menu title."""
        self.title = MenuTitle(x, y, text)
    
    def navigate_up(self):
        """Navigate to previous menu item."""
        if not self.navigation_enabled or not self.buttons:
            return
        
        self.buttons[self.selected_index].set_selected(False)
        self.selected_index = (self.selected_index - 1) % len(self.buttons)
        self.buttons[self.selected_index].set_selected(True)
        
        self.audio_manager.play_sound('ui_move', 0, 0, volume=0.3)
    
    def navigate_down(self):
        """Navigate to next menu item."""
        if not self.navigation_enabled or not self.buttons:
            return
        
        self.buttons[self.selected_index].set_selected(False)
        self.selected_index = (self.selected_index + 1) % len(self.buttons)
        self.buttons[self.selected_index].set_selected(True)
        
        self.audio_manager.play_sound('ui_move', 0, 0, volume=0.3)
    
    def activate_selected(self):
        """Activate currently selected button."""
        if not self.navigation_enabled or not self.buttons:
            return
        
        selected_button = self.buttons[self.selected_index]
        selected_button.press()
        
        self.audio_manager.play_sound('click', 0, 0, volume=0.5)
    
    def enter_scene(self):
        """Called when entering the scene."""
        self.is_entering = True
        self.enter_transition_timer = 0.0
        
        # Start enter animations
        for i, button in enumerate(self.buttons):
            button.animate_to(alpha=0, scale=0.5)
            # Stagger button animations
            pygame.time.set_timer(pygame.USEREVENT + i + 1, int((i + 1) * 200))
        
        if self.title:
            self.title.animate_to(alpha=0, scale=0.8)
    
    def exit_scene(self):
        """Called when exiting the scene."""
        self.is_exiting = True
        self.exit_transition_timer = 0.0
        self.navigation_enabled = False
        
        # Start exit animations
        for button in self.buttons:
            button.animate_to(alpha=0, scale=0.5)
        
        if self.title:
            self.title.animate_to(alpha=0, scale=1.2)
    
    def update(self, dt: float):
        """Update menu scene."""
        # Update background
        self.background.update(dt)
        
        # Update elements
        if self.title:
            self.title.update(dt)
        
        for button in self.buttons:
            button.update(dt)
        
        # Update transitions
        if self.is_entering:
            self.enter_transition_timer += dt
            if self.enter_transition_timer > 1.0:
                self.is_entering = False
                self.navigation_enabled = True
        
        if self.is_exiting:
            self.exit_transition_timer += dt
            if self.exit_transition_timer > 0.5:
                # Complete transition
                pass
        
        # Update input delay
        if self.input_delay > 0:
            self.input_delay = max(0, self.input_delay - dt)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        # Handle button enter animations
        if event.type >= pygame.USEREVENT + 1 and event.type <= pygame.USEREVENT + len(self.buttons):
            button_index = event.type - pygame.USEREVENT - 1
            if button_index < len(self.buttons):
                self.buttons[button_index].animate_to(alpha=255, scale=1.0)
            return True
        
        # Handle navigation
        if self.input_delay > 0 or not self.navigation_enabled:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.navigate_up()
                self.input_delay = self.input_repeat_delay
                return True
            
            elif event.key == pygame.K_DOWN:
                self.navigate_down()
                self.input_delay = self.input_repeat_delay
                return True
            
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.activate_selected()
                return True
            
            elif event.key == pygame.K_ESCAPE:
                self.handle_back()
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Handle mouse hover
            mouse_x, mouse_y = event.pos
            
            for i, button in enumerate(self.buttons):
                was_hovered = button.is_hovered
                is_hovered = button.contains_point(mouse_x, mouse_y)
                
                if is_hovered and not was_hovered:
                    # Mouse entered button
                    if self.selected_index != i:
                        self.buttons[self.selected_index].set_selected(False)
                        self.selected_index = i
                        button.set_selected(True)
                
                button.set_hovered(is_hovered)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                for button in self.buttons:
                    if button.contains_point(mouse_x, mouse_y):
                        button.press()
                        return True
        
        return False
    
    def handle_back(self):
        """Handle back action (escape key)."""
        # Override in subclasses
        pass
    
    def render(self, surface: pygame.Surface):
        """Render menu scene."""
        # Render background
        self.background.render(surface)
        
        # Render title
        if self.title:
            self.title.render(surface)
        
        # Render buttons
        for button in self.buttons:
            button.render(surface)
    
    def cleanup(self):
        """Clean up scene resources."""
        # Clean up timers
        for i in range(len(self.buttons)):
            pygame.time.set_timer(pygame.USEREVENT + i + 1, 0)


class LoadGameScene(GameMenuScene):
    """Load game menu scene."""
    
    def __init__(self, scene_manager: SceneManager, input_manager: InputManager, audio_manager: AudioManager):
        super().__init__("load_game", scene_manager, input_manager, audio_manager)
        
        # Set up menu
        self.set_title(config.SCREEN_WIDTH // 2, 100, "LOAD GAME")
        
        # Load save slots (dummy data for now)
        self.save_slots = [
            {"name": "Save Slot 1", "level": 5, "time": "2:30:45", "exists": True},
            {"name": "Save Slot 2", "level": 3, "time": "1:15:20", "exists": True},
            {"name": "Save Slot 3", "level": 1, "time": "0:10:05", "exists": True},
            {"name": "Empty Slot", "level": 0, "time": "", "exists": False},
            {"name": "Empty Slot", "level": 0, "time": "", "exists": False},
        ]
        
        # Create buttons for save slots
        button_y = 200
        for i, slot in enumerate(self.save_slots):
            if slot["exists"]:
                button_text = f"{slot['name']} - Level {slot['level']} ({slot['time']})"
                action = lambda idx=i: self.load_save_slot(idx)
            else:
                button_text = slot["name"]
                action = None
            
            button = self.add_button(config.SCREEN_WIDTH // 2, button_y, 500, 50, button_text, action)
            
            if not slot["exists"]:
                button.enabled = False
                button.current_alpha = 100
            
            button_y += 70
        
        # Back button
        self.add_button(config.SCREEN_WIDTH // 2, button_y + 50, 200, 50, "Back", self.go_back)
    
    def load_save_slot(self, slot_index: int):
        """Load a save slot."""
        slot = self.save_slots[slot_index]
        if slot["exists"]:
            print(f"Loading save slot {slot_index + 1}")
            # Would load the actual save data here
            self.scene_manager.change_scene("gameplay")
    
    def go_back(self):
        """Return to main menu."""
        self.scene_manager.change_scene("main_menu")
    
    def handle_back(self):
        """Handle escape key."""
        self.go_back()


class CreditsScene(GameMenuScene):
    """Credits scene with scrolling text."""
    
    def __init__(self, scene_manager: SceneManager, input_manager: InputManager, audio_manager: AudioManager):
        super().__init__("credits", scene_manager, input_manager, audio_manager)
        
        # Set up credits
        self.credits_text = [
            "",
            "FOREST SURVIVAL",
            "",
            "Game Development Team",
            "",
            "Programming",
            "Lead Developer",
            "",
            "Art & Graphics",
            "Character Artist",
            "Environment Artist",
            "",
            "Audio & Music",
            "Sound Designer",
            "Composer",
            "",
            "Game Design",
            "Game Designer",
            "Level Designer",
            "",
            "Special Thanks",
            "Game Jam Community",
            "Beta Testers",
            "Family & Friends",
            "",
            "Tools & Libraries",
            "Pygame",
            "Python",
            "Visual Studio Code",
            "",
            "Thank you for playing!",
            "",
            ""
        ]
        
        # Scrolling properties
        self.scroll_speed = 50.0  # pixels per second
        self.scroll_offset = config.SCREEN_HEIGHT
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        # Back button
        self.add_button(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 50, 200, 40, "Back", self.go_back)
    
    def update(self, dt: float):
        """Update credits scene."""
        super().update(dt)
        
        # Update scrolling
        self.scroll_offset -= self.scroll_speed * dt
        
        # Reset scroll when credits finish
        total_height = len(self.credits_text) * 60
        if self.scroll_offset < -total_height:
            self.scroll_offset = config.SCREEN_HEIGHT
    
    def render(self, surface: pygame.Surface):
        """Render credits scene."""
        super().render(surface)
        
        # Render scrolling credits
        current_y = self.scroll_offset
        
        for line in self.credits_text:
            if current_y > -50 and current_y < config.SCREEN_HEIGHT + 50:
                if line == "":
                    # Empty line for spacing
                    pass
                elif line == "FOREST SURVIVAL":
                    # Title
                    text_surface = self.font_large.render(line, True, config.COLORS['yellow'])
                    text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, current_y))
                    surface.blit(text_surface, text_rect)
                elif line in ["Game Development Team", "Programming", "Art & Graphics", "Audio & Music", 
                             "Game Design", "Special Thanks", "Tools & Libraries"]:
                    # Section headers
                    text_surface = self.font_medium.render(line, True, config.COLORS['cyan'])
                    text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, current_y))
                    surface.blit(text_surface, text_rect)
                else:
                    # Regular text
                    text_surface = self.font_small.render(line, True, config.COLORS['white'])
                    text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, current_y))
                    surface.blit(text_surface, text_rect)
            
            current_y += 60
    
    def go_back(self):
        """Return to main menu."""
        self.scene_manager.change_scene("main_menu")
    
    def handle_back(self):
        """Handle escape key."""
        self.go_back()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        # Handle skip with any key
        if event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE:
            # Speed up scrolling
            self.scroll_speed = 200.0
        elif event.type == pygame.KEYUP:
            # Return to normal speed
            self.scroll_speed = 50.0
        
        return super().handle_event(event)