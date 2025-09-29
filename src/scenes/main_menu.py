"""
Forest Survival - Main Menu Scene
Modern, animated main menu with smooth transitions and effects.
"""

import pygame
import math
import time
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

import config
from src.core.scene_manager import BaseScene, SceneTransition
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.systems.particle_system import ParticleSystem, PARTICLE_PRESETS


class MenuState(Enum):
    """Main menu states."""
    INTRO = "intro"
    MAIN = "main"
    SETTINGS = "settings"
    CREDITS = "credits"
    QUIT_CONFIRM = "quit_confirm"
    TRANSITIONING = "transitioning"


class UIElement:
    """Base class for UI elements with animations."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.initial_x = x
        self.initial_y = y
        
        # Animation properties
        self.alpha = 255
        self.scale = 1.0
        self.rotation = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # State
        self.visible = True
        self.enabled = True
        self.hovered = False
        self.pressed = False
        
        # Animation timers
        self.animation_timer = 0.0
        self.hover_timer = 0.0
        self.pulse_timer = 0.0
        
        # Effects
        self.glow_intensity = 0.0
        self.particle_emitter = None
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update UI element animations and state."""
        self.animation_timer += dt
        self.pulse_timer += dt
        
        # Check hover state
        was_hovered = self.hovered
        self.hovered = self.is_point_inside(mouse_pos)
        
        if self.hovered != was_hovered:
            if self.hovered:
                self.on_hover_enter()
            else:
                self.on_hover_exit()
        
        # Update hover timer
        if self.hovered:
            self.hover_timer += dt
        else:
            self.hover_timer = max(0, self.hover_timer - dt * 3)
        
        # Update glow effect
        if self.hovered:
            self.glow_intensity = min(1.0, self.glow_intensity + dt * 5)
        else:
            self.glow_intensity = max(0.0, self.glow_intensity - dt * 3)
        
        self._update_animations(dt)
    
    def _update_animations(self, dt: float):
        """Update specific animations - override in subclasses."""
        pass
    
    def is_point_inside(self, point: Tuple[int, int]) -> bool:
        """Check if point is inside the element."""
        return (self.x <= point[0] <= self.x + self.width and
                self.y <= point[1] <= self.y + self.height)
    
    def on_hover_enter(self):
        """Called when mouse enters element."""
        pass
    
    def on_hover_exit(self):
        """Called when mouse exits element."""
        pass
    
    def on_click(self):
        """Called when element is clicked."""
        pass
    
    def get_render_rect(self) -> pygame.Rect:
        """Get rectangle for rendering with scale and offset."""
        scaled_width = self.width * self.scale
        scaled_height = self.height * self.scale
        render_x = self.x + self.offset_x - (scaled_width - self.width) / 2
        render_y = self.y + self.offset_y - (scaled_height - self.height) / 2
        
        return pygame.Rect(render_x, render_y, scaled_width, scaled_height)


class AnimatedButton(UIElement):
    """Animated button with hover effects and sound."""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 text: str, font: pygame.font.Font, audio_manager: AudioManager):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.audio_manager = audio_manager
        
        # Colors
        self.base_color = config.COLORS['dark_gray']
        self.hover_color = config.COLORS['blue']
        self.text_color = config.COLORS['white']
        self.border_color = config.COLORS['cyan']
        
        # Animation properties
        self.hover_scale = 1.1
        self.click_scale = 0.95
        self.border_width = 0.0
        self.max_border_width = 3.0
        
        # Effects
        self.ripple_effects: List[Dict] = []
        self.sparkle_timer = 0.0
        
    def _update_animations(self, dt: float):
        """Update button animations."""
        # Scale animation
        target_scale = 1.0
        if self.hovered:
            target_scale = self.hover_scale
        if self.pressed:
            target_scale = self.click_scale
        
        scale_speed = 8.0
        if self.scale < target_scale:
            self.scale = min(target_scale, self.scale + scale_speed * dt)
        elif self.scale > target_scale:
            self.scale = max(target_scale, self.scale - scale_speed * dt)
        
        # Border animation
        target_border = self.max_border_width if self.hovered else 0.0
        border_speed = 15.0
        if self.border_width < target_border:
            self.border_width = min(target_border, self.border_width + border_speed * dt)
        elif self.border_width > target_border:
            self.border_width = max(target_border, self.border_width - border_speed * dt)
        
        # Update ripple effects
        self.ripple_effects = [effect for effect in self.ripple_effects 
                              if self._update_ripple_effect(effect, dt)]
        
        # Sparkle timer for special buttons
        self.sparkle_timer += dt
    
    def _update_ripple_effect(self, effect: Dict, dt: float) -> bool:
        """Update ripple effect. Returns False when expired."""
        effect['timer'] += dt
        effect['radius'] += effect['speed'] * dt
        effect['alpha'] = max(0, effect['alpha'] - 300 * dt)
        
        return effect['timer'] < effect['lifetime'] and effect['alpha'] > 0
    
    def on_hover_enter(self):
        """Called when mouse enters button."""
        self.audio_manager.play_sound('click', 0, 0, volume=0.3)
    
    def on_click(self):
        """Called when button is clicked."""
        self.audio_manager.play_sound('click', 0, 0, volume=0.5)
        self.pressed = True
        
        # Create ripple effect
        self.ripple_effects.append({
            'x': self.x + self.width / 2,
            'y': self.y + self.height / 2,
            'radius': 0.0,
            'speed': 200.0,
            'alpha': 100,
            'timer': 0.0,
            'lifetime': 0.8
        })
    
    def render(self, surface: pygame.Surface):
        """Render the button."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Calculate current color
        color_progress = self.glow_intensity
        current_color = self._blend_colors(self.base_color, self.hover_color, color_progress)
        
        # Draw button background with gradient
        self._draw_gradient_rect(surface, render_rect, current_color)
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, render_rect, int(self.border_width))
        
        # Draw glow effect
        if self.glow_intensity > 0:
            self._draw_glow_effect(surface, render_rect)
        
        # Draw ripple effects
        for effect in self.ripple_effects:
            self._draw_ripple_effect(surface, effect)
        
        # Draw text
        self._draw_text(surface, render_rect)
        
        # Draw sparkles for special buttons
        if self.hovered and self.sparkle_timer > 0.5:
            self._draw_sparkles(surface, render_rect)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress (0.0 to 1.0)."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)
    
    def _draw_gradient_rect(self, surface: pygame.Surface, rect: pygame.Rect, 
                           base_color: Tuple[int, int, int]):
        """Draw rectangle with vertical gradient."""
        # Simple two-tone gradient
        for y in range(rect.height):
            progress = y / rect.height
            # Lighter at top, darker at bottom
            factor = 1.2 - progress * 0.4
            
            gradient_color = (
                min(255, int(base_color[0] * factor)),
                min(255, int(base_color[1] * factor)),
                min(255, int(base_color[2] * factor))
            )
            
            pygame.draw.line(surface, gradient_color, 
                           (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))
    
    def _draw_glow_effect(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw glow effect around button."""
        glow_size = int(10 * self.glow_intensity)
        glow_alpha = int(50 * self.glow_intensity)
        
        # Create glow surface
        glow_surface = pygame.Surface((rect.width + glow_size * 2, 
                                     rect.height + glow_size * 2), pygame.SRCALPHA)
        
        # Draw multiple glow rings
        for i in range(glow_size, 0, -2):
            alpha = int(glow_alpha * (1 - i / glow_size))
            glow_color = (*self.border_color, alpha)
            
            glow_rect = pygame.Rect(glow_size - i, glow_size - i, 
                                  rect.width + i * 2, rect.height + i * 2)
            pygame.draw.rect(glow_surface, glow_color, glow_rect, 2)
        
        surface.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))
    
    def _draw_ripple_effect(self, surface: pygame.Surface, effect: Dict):
        """Draw ripple effect."""
        if effect['alpha'] <= 0:
            return
        
        ripple_color = (*self.border_color, int(effect['alpha']))
        pygame.draw.circle(surface, ripple_color, 
                         (int(effect['x']), int(effect['y'])), 
                         int(effect['radius']), 2)
    
    def _draw_text(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw button text."""
        # Render text with shadow
        text_surface = self.font.render(self.text, True, self.text_color)
        shadow_surface = self.font.render(self.text, True, config.COLORS['black'])
        
        # Center text
        text_rect = text_surface.get_rect(center=rect.center)
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        
        # Apply alpha
        text_surface.set_alpha(self.alpha)
        shadow_surface.set_alpha(self.alpha // 2)
        
        # Draw shadow first, then text
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
    
    def _draw_sparkles(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw sparkle effects for special buttons."""
        if self.sparkle_timer < 0.5:
            return
        
        import random
        for _ in range(3):
            x = random.randint(rect.x, rect.x + rect.width)
            y = random.randint(rect.y, rect.y + rect.height)
            
            sparkle_color = config.COLORS['yellow']
            pygame.draw.circle(surface, sparkle_color, (x, y), 2)


class TitleDisplay(UIElement):
    """Animated title display with effects."""
    
    def __init__(self, x: float, y: float, title: str, subtitle: str, 
                 title_font: pygame.font.Font, subtitle_font: pygame.font.Font):
        # Calculate size based on text
        title_surface = title_font.render(title, True, config.COLORS['white'])
        subtitle_surface = subtitle_font.render(subtitle, True, config.COLORS['white'])
        
        width = max(title_surface.get_width(), subtitle_surface.get_width())
        height = title_surface.get_height() + subtitle_surface.get_height() + 20
        
        super().__init__(x, y, width, height)
        
        self.title = title
        self.subtitle = subtitle
        self.title_font = title_font
        self.subtitle_font = subtitle_font
        
        # Animation properties
        self.wave_offset = 0.0
        self.glow_pulse = 0.0
        self.letter_delays: List[float] = []
        
        # Initialize letter animation delays
        for i in range(len(title)):
            self.letter_delays.append(i * 0.1)
    
    def _update_animations(self, dt: float):
        """Update title animations."""
        self.wave_offset += dt * 3
        self.glow_pulse += dt * 2
        
        # Floating animation
        self.offset_y = math.sin(self.animation_timer * 1.5) * 3
    
    def render(self, surface: pygame.Surface):
        """Render the title with effects."""
        if not self.visible:
            return
        
        # Draw title with wave effect
        self._draw_wavy_title(surface)
        
        # Draw subtitle
        self._draw_subtitle(surface)
        
        # Draw glow effects
        self._draw_title_glow(surface)
    
    def _draw_wavy_title(self, surface: pygame.Surface):
        """Draw title with wavy letter animation."""
        char_x = self.x + self.offset_x
        base_y = self.y + self.offset_y
        
        for i, char in enumerate(self.title):
            if char == ' ':
                char_width = self.title_font.size(' ')[0]
                char_x += char_width
                continue
            
            # Calculate wave offset for this character
            wave_y = math.sin(self.wave_offset + i * 0.5) * 5
            
            # Calculate appearance animation
            letter_progress = max(0, min(1, (self.animation_timer - self.letter_delays[i]) / 0.5))
            char_alpha = int(255 * letter_progress)
            char_scale = 0.5 + letter_progress * 0.5
            
            if char_alpha > 0:
                # Render character
                char_surface = self.title_font.render(char, True, config.COLORS['white'])
                char_surface.set_alpha(char_alpha)
                
                # Scale if needed
                if char_scale != 1.0:
                    char_width = int(char_surface.get_width() * char_scale)
                    char_height = int(char_surface.get_height() * char_scale)
                    char_surface = pygame.transform.scale(char_surface, (char_width, char_height))
                
                # Position and draw
                char_rect = char_surface.get_rect()
                char_rect.x = int(char_x)
                char_rect.y = int(base_y + wave_y)
                
                surface.blit(char_surface, char_rect)
                
                char_x += char_surface.get_width() + 2
            else:
                # Still invisible, but advance position
                char_width = self.title_font.size(char)[0]
                char_x += char_width + 2
    
    def _draw_subtitle(self, surface: pygame.Surface):
        """Draw subtitle with fade-in effect."""
        subtitle_alpha = int(255 * min(1, max(0, (self.animation_timer - 1.5) / 1.0)))
        
        if subtitle_alpha > 0:
            subtitle_surface = self.subtitle_font.render(self.subtitle, True, config.COLORS['cyan'])
            subtitle_surface.set_alpha(subtitle_alpha)
            
            subtitle_rect = subtitle_surface.get_rect()
            subtitle_rect.centerx = int(self.x + self.width // 2)
            subtitle_rect.y = int(self.y + self.title_font.get_height() + 20)
            
            surface.blit(subtitle_surface, subtitle_rect)
    
    def _draw_title_glow(self, surface: pygame.Surface):
        """Draw glowing effect behind title."""
        glow_intensity = (math.sin(self.glow_pulse) + 1) / 2
        glow_alpha = int(30 * glow_intensity)
        
        if glow_alpha > 0:
            # Create glow surface
            glow_surface = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
            glow_color = (*config.COLORS['yellow'], glow_alpha)
            
            # Draw multiple glow circles
            center_x = 20 + self.width // 2
            center_y = 20 + self.height // 2
            
            for radius in range(60, 20, -10):
                alpha = int(glow_alpha * (1 - (radius - 20) / 40))
                if alpha > 0:
                    color = (*config.COLORS['yellow'], alpha)
                    pygame.draw.circle(glow_surface, color, (center_x, center_y), radius)
            
            surface.blit(glow_surface, (self.x - 20, self.y - 20))


class BackgroundRenderer:
    """Renders animated background for main menu."""
    
    def __init__(self, screen_width: int, screen_height: int, particle_system: ParticleSystem):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particle_system = particle_system
        
        # Background elements
        self.floating_leaves: List[Dict] = []
        self.background_trees: List[Dict] = []
        self.parallax_layers: List[pygame.Surface] = []
        
        # Animation timers
        self.wind_timer = 0.0
        self.ambient_timer = 0.0
        
        self._initialize_background_elements()
    
    def _initialize_background_elements(self):
        """Initialize background elements."""
        import random
        
        # Create floating leaves
        for _ in range(20):
            self.floating_leaves.append({
                'x': random.uniform(0, self.screen_width),
                'y': random.uniform(0, self.screen_height),
                'vel_x': random.uniform(-20, 20),
                'vel_y': random.uniform(-10, 10),
                'rotation': random.uniform(0, math.pi * 2),
                'rotation_speed': random.uniform(-2, 2),
                'size': random.uniform(3, 8),
                'color': random.choice([config.COLORS['green'], config.COLORS['brown'], 
                                      config.COLORS['orange'], config.COLORS['yellow']])
            })
        
        # Create background trees (silhouettes)
        for _ in range(8):
            self.background_trees.append({
                'x': random.uniform(-100, self.screen_width + 100),
                'y': self.screen_height - random.uniform(100, 300),
                'width': random.uniform(40, 120),
                'height': random.uniform(200, 400),
                'sway_phase': random.uniform(0, math.pi * 2),
                'sway_amplitude': random.uniform(2, 8)
            })
    
    def update(self, dt: float):
        """Update background animations."""
        self.wind_timer += dt
        self.ambient_timer += dt
        
        # Update floating leaves
        for leaf in self.floating_leaves:
            # Apply wind effect
            wind_strength = math.sin(self.wind_timer * 0.8) * 15
            
            leaf['x'] += (leaf['vel_x'] + wind_strength) * dt
            leaf['y'] += leaf['vel_y'] * dt
            leaf['rotation'] += leaf['rotation_speed'] * dt
            
            # Wrap around screen
            if leaf['x'] < -20:
                leaf['x'] = self.screen_width + 20
            elif leaf['x'] > self.screen_width + 20:
                leaf['x'] = -20
            
            if leaf['y'] < -20:
                leaf['y'] = self.screen_height + 20
            elif leaf['y'] > self.screen_height + 20:
                leaf['y'] = -20
        
        # Spawn ambient particles occasionally
        if self.ambient_timer > 2.0:
            self.ambient_timer = 0.0
            import random
            
            # Spawn some magical particles
            for _ in range(3):
                x = random.uniform(0, self.screen_width)
                y = random.uniform(0, self.screen_height)
                self.particle_system.emit_burst(x, y, PARTICLE_PRESETS['magic_cast'])
    
    def render(self, surface: pygame.Surface):
        """Render the background."""
        # Fill with dark forest color
        surface.fill(config.COLORS['dark_green'])
        
        # Draw gradient overlay
        self._draw_gradient_overlay(surface)
        
        # Draw background trees
        self._draw_background_trees(surface)
        
        # Draw floating leaves
        self._draw_floating_leaves(surface)
        
        # Draw atmospheric effects
        self._draw_atmospheric_effects(surface)
    
    def _draw_gradient_overlay(self, surface: pygame.Surface):
        """Draw gradient overlay for atmosphere."""
        # Create vertical gradient from dark blue to transparent
        gradient_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        for y in range(self.screen_height):
            progress = y / self.screen_height
            alpha = int(80 * (1 - progress))
            
            if alpha > 0:
                color = (*config.COLORS['dark_blue'], alpha)
                pygame.draw.line(gradient_surface, color, (0, y), (self.screen_width, y))
        
        surface.blit(gradient_surface, (0, 0))
    
    def _draw_background_trees(self, surface: pygame.Surface):
        """Draw silhouetted trees in background."""
        for tree in self.background_trees:
            # Calculate swaying motion
            sway_offset = math.sin(self.wind_timer + tree['sway_phase']) * tree['sway_amplitude']
            
            # Draw tree silhouette
            tree_points = [
                (tree['x'] + sway_offset, tree['y']),
                (tree['x'] - tree['width']//3, tree['y'] + tree['height']),
                (tree['x'] + tree['width']//3, tree['y'] + tree['height'])
            ]
            
            # Draw with semi-transparency
            tree_color = (*config.COLORS['black'], 100)
            tree_surface = pygame.Surface((tree['width'], tree['height']), pygame.SRCALPHA)
            pygame.draw.polygon(tree_surface, tree_color, 
                              [(p[0] - tree['x'] + tree['width']//2, p[1] - tree['y']) for p in tree_points])
            
            surface.blit(tree_surface, (tree['x'] - tree['width']//2, tree['y']))
    
    def _draw_floating_leaves(self, surface: pygame.Surface):
        """Draw floating leaves."""
        for leaf in self.floating_leaves:
            # Create leaf surface
            leaf_size = int(leaf['size'])
            leaf_surface = pygame.Surface((leaf_size * 2, leaf_size * 2), pygame.SRCALPHA)
            
            # Draw leaf shape (simple oval)
            pygame.draw.ellipse(leaf_surface, leaf['color'], 
                              pygame.Rect(0, 0, leaf_size * 2, leaf_size))
            
            # Rotate leaf
            if leaf['rotation'] != 0:
                leaf_surface = pygame.transform.rotate(leaf_surface, math.degrees(leaf['rotation']))
            
            # Draw with transparency
            leaf_surface.set_alpha(180)
            
            # Blit to screen
            leaf_rect = leaf_surface.get_rect(center=(leaf['x'], leaf['y']))
            surface.blit(leaf_surface, leaf_rect)
    
    def _draw_atmospheric_effects(self, surface: pygame.Surface):
        """Draw atmospheric lighting effects."""
        # Draw some light rays
        light_alpha = int(20 * (math.sin(self.ambient_timer * 0.5) + 1) / 2)
        
        if light_alpha > 0:
            light_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            light_color = (*config.COLORS['yellow'], light_alpha)
            
            # Draw diagonal light rays
            for i in range(0, self.screen_width + 200, 100):
                start_pos = (i - 100, 0)
                end_pos = (i, self.screen_height)
                pygame.draw.line(light_surface, light_color, start_pos, end_pos, 3)
            
            surface.blit(light_surface, (0, 0))


class MainMenuScene(BaseScene):
    """
    Main menu scene with modern UI and animations.
    """
    
    def __init__(self, scene_manager, input_manager: InputManager, 
                 audio_manager: AudioManager, settings_manager):
        super().__init__(scene_manager)
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        self.settings_manager = settings_manager
        
        # Scene state
        self.state = MenuState.INTRO
        self.state_timer = 0.0
        
        # Initialize systems
        self.particle_system = ParticleSystem(max_particles=500)
        self.background_renderer = BackgroundRenderer(
            config.SCREEN_WIDTH, config.SCREEN_HEIGHT, self.particle_system
        )
        
        # Load fonts
        self._load_fonts()
        
        # UI Elements
        self.ui_elements: List[UIElement] = []
        self.buttons: List[AnimatedButton] = []
        self.title_display = None
        
        # Menu layout
        self.button_width = 300
        self.button_height = 60
        self.button_spacing = 20
        
        # Effects
        self.screen_flash_alpha = 0
        self.intro_complete = False
        
        self._setup_ui_elements()
        self._start_intro_sequence()
        
        print("Main menu scene initialized")
    
    def _load_fonts(self):
        """Load fonts for the menu."""
        try:
            self.title_font = pygame.font.Font(None, 72)
            self.subtitle_font = pygame.font.Font(None, 36)
            self.button_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
        except:
            # Fallback to default font
            self.title_font = pygame.font.Font(None, 72)
            self.subtitle_font = pygame.font.Font(None, 36)
            self.button_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
    
    def _setup_ui_elements(self):
        """Setup all UI elements."""
        # Title display
        title_x = config.SCREEN_WIDTH // 2 - 200
        title_y = 80
        self.title_display = TitleDisplay(
            title_x, title_y, "FOREST SURVIVAL", "Survive the Wild",
            self.title_font, self.subtitle_font
        )
        self.ui_elements.append(self.title_display)
        
        # Main menu buttons
        button_start_y = 300
        button_x = config.SCREEN_WIDTH // 2 - self.button_width // 2
        
        button_configs = [
            ("New Game", "new_game"),
            ("Continue", "continue"),
            ("Settings", "settings"),
            ("Credits", "credits"),
            ("Quit", "quit")
        ]
        
        for i, (text, action) in enumerate(button_configs):
            button_y = button_start_y + i * (self.button_height + self.button_spacing)
            button = AnimatedButton(
                button_x, button_y, self.button_width, self.button_height,
                text, self.button_font, self.audio_manager
            )
            button.action = action
            
            # Special styling for certain buttons
            if action == "new_game":
                button.border_color = config.COLORS['green']
                button.hover_color = config.COLORS['green']
            elif action == "quit":
                button.border_color = config.COLORS['red']
                button.hover_color = config.COLORS['red']
            
            self.buttons.append(button)
            self.ui_elements.append(button)
        
        # Initially hide all elements
        for element in self.ui_elements:
            element.visible = False
            element.alpha = 0
    
    def _start_intro_sequence(self):
        """Start the intro animation sequence."""
        self.state = MenuState.INTRO
        self.state_timer = 0.0
        
        # Flash effect
        self.screen_flash_alpha = 255
        
        # Play intro sound
        self.audio_manager.play_sound('theme', 0, 0, volume=0.8)
    
    def update(self, dt: float):
        """Update main menu scene."""
        self.state_timer += dt
        
        # Update background
        self.background_renderer.update(dt)
        self.particle_system.update(dt)
        
        # Update based on current state
        if self.state == MenuState.INTRO:
            self._update_intro_state(dt)
        elif self.state == MenuState.MAIN:
            self._update_main_state(dt)
        
        # Update UI elements
        mouse_pos = pygame.mouse.get_pos()
        for element in self.ui_elements:
            element.update(dt, mouse_pos)
        
        # Handle screen flash
        if self.screen_flash_alpha > 0:
            self.screen_flash_alpha = max(0, self.screen_flash_alpha - 300 * dt)
    
    def _update_intro_state(self, dt: float):
        """Update intro animation state."""
        # Show title first
        if self.state_timer > 0.5:
            self.title_display.visible = True
            title_progress = min(1.0, (self.state_timer - 0.5) / 2.0)
            self.title_display.alpha = int(255 * title_progress)
        
        # Show buttons after title
        if self.state_timer > 3.0:
            button_delay = 0.2
            for i, button in enumerate(self.buttons):
                button_start_time = 3.0 + i * button_delay
                if self.state_timer > button_start_time:
                    button.visible = True
                    button_progress = min(1.0, (self.state_timer - button_start_time) / 0.5)
                    button.alpha = int(255 * button_progress)
                    button.offset_y = (1.0 - button_progress) * 50  # Slide up effect
        
        # Transition to main state
        if self.state_timer > 5.0 and not self.intro_complete:
            self.intro_complete = True
            self.state = MenuState.MAIN
            self.state_timer = 0.0
    
    def _update_main_state(self, dt: float):
        """Update main menu state."""
        # All UI elements should be fully visible
        for element in self.ui_elements:
            element.visible = True
            element.alpha = 255
            element.offset_y = 0
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
            # Check button clicks
            for button in self.buttons:
                if button.visible and button.enabled and button.is_point_inside(mouse_pos):
                    button.on_click()
                    self._handle_button_action(button.action)
                    return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == MenuState.MAIN:
                    self._handle_button_action("quit")
                return True
            
            elif event.key == pygame.K_RETURN:
                # Quick start with Enter key
                if self.state == MenuState.MAIN:
                    self._handle_button_action("new_game")
                return True
        
        return False
    
    def _handle_button_action(self, action: str):
        """Handle button action."""
        if action == "new_game":
            # Transition to game scene
            transition = SceneTransition("fade", 1.0, config.COLORS['black'])
            self.scene_manager.change_scene("game", transition)
        
        elif action == "continue":
            # Load saved game
            # For now, just start new game
            transition = SceneTransition("fade", 1.0, config.COLORS['black'])
            self.scene_manager.change_scene("game", transition)
        
        elif action == "settings":
            # Transition to settings scene
            transition = SceneTransition("slide", 0.5, direction="left")
            self.scene_manager.change_scene("settings", transition)
        
        elif action == "credits":
            # Show credits
            self.state = MenuState.CREDITS
            self.state_timer = 0.0
        
        elif action == "quit":
            # Show quit confirmation
            self.state = MenuState.QUIT_CONFIRM
            self.state_timer = 0.0
    
    def render(self, screen: pygame.Surface):
        """Render the main menu scene."""
        # Clear screen
        screen.fill(config.COLORS['black'])
        
        # Render background
        self.background_renderer.render(screen)
        
        # Render particles
        self.particle_system.render(screen, (0, 0))
        
        # Render UI elements
        for element in self.ui_elements:
            if hasattr(element, 'render'):
                element.render(screen)
        
        # Render screen flash
        if self.screen_flash_alpha > 0:
            flash_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            flash_surface.fill(config.COLORS['white'])
            flash_surface.set_alpha(self.screen_flash_alpha)
            screen.blit(flash_surface, (0, 0))
        
        # Render version info
        version_text = self.small_font.render(f"v{config.VERSION}", True, config.COLORS['gray'])
        screen.blit(version_text, (10, config.SCREEN_HEIGHT - 30))
    
    def on_enter(self):
        """Called when entering the scene."""
        # Start background music
        self.audio_manager.play_music('theme', loops=-1, fade_in=2.0)
        
        # Reset intro if needed
        if not self.intro_complete:
            self._start_intro_sequence()
    
    def on_exit(self):
        """Called when exiting the scene."""
        # Stop music
        self.audio_manager.stop_music(fade_out=1.0)
        
        # Clear particles
        self.particle_system.clear_particles()