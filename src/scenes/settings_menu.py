"""
Forest Survival - Settings Menu Scene
Comprehensive settings menu with modern UI and real-time preview.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

import config
from src.core.scene_manager import BaseScene, SceneTransition
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.scenes.main_menu import UIElement, AnimatedButton


class SettingsCategory(Enum):
    """Settings categories."""
    GRAPHICS = "graphics"
    AUDIO = "audio"
    GAMEPLAY = "gameplay"
    CONTROLS = "controls"
    ACCESSIBILITY = "accessibility"


class SliderControl(UIElement):
    """Animated slider control for numeric settings."""
    
    def __init__(self, x: float, y: float, width: float, height: float,
                 min_value: float, max_value: float, current_value: float,
                 label: str, font: pygame.font.Font, audio_manager: AudioManager):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value
        self.label = label
        self.font = font
        self.audio_manager = audio_manager
        
        # Slider properties
        self.dragging = False
        self.knob_radius = 12
        self.track_height = 6
        self.track_y = y + height // 2 - self.track_height // 2
        
        # Animation
        self.knob_scale = 1.0
        self.glow_intensity = 0.0
        
        # Colors
        self.track_color = config.COLORS['dark_gray']
        self.track_fill_color = config.COLORS['blue']
        self.knob_color = config.COLORS['white']
        self.knob_border_color = config.COLORS['cyan']
        
        # Value display
        self.show_percentage = True
        self.format_string = "{:.0f}%"
    
    def _update_animations(self, dt: float):
        """Update slider animations."""
        # Knob scale animation
        target_scale = 1.3 if (self.hovered or self.dragging) else 1.0
        scale_speed = 8.0
        
        if self.knob_scale < target_scale:
            self.knob_scale = min(target_scale, self.knob_scale + scale_speed * dt)
        elif self.knob_scale > target_scale:
            self.knob_scale = max(target_scale, self.knob_scale - scale_speed * dt)
        
        # Glow animation
        if self.hovered or self.dragging:
            self.glow_intensity = min(1.0, self.glow_intensity + dt * 5)
        else:
            self.glow_intensity = max(0.0, self.glow_intensity - dt * 3)
    
    def get_knob_position(self) -> Tuple[int, int]:
        """Get current knob position."""
        progress = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        knob_x = int(self.x + progress * self.width)
        knob_y = int(self.y + self.height // 2)
        return (knob_x, knob_y)
    
    def set_value_from_position(self, mouse_x: int):
        """Set value based on mouse position."""
        progress = max(0.0, min(1.0, (mouse_x - self.x) / self.width))
        old_value = self.current_value
        self.current_value = self.min_value + progress * (self.max_value - self.min_value)
        
        # Play sound if value changed significantly
        if abs(self.current_value - old_value) > (self.max_value - self.min_value) * 0.05:
            self.audio_manager.play_sound('click', 0, 0, volume=0.2)
    
    def handle_mouse_down(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse down event."""
        knob_pos = self.get_knob_position()
        knob_rect = pygame.Rect(knob_pos[0] - self.knob_radius, knob_pos[1] - self.knob_radius,
                               self.knob_radius * 2, self.knob_radius * 2)
        
        if knob_rect.collidepoint(mouse_pos):
            self.dragging = True
            return True
        elif self.is_point_inside(mouse_pos):
            # Click on track to jump to position
            self.set_value_from_position(mouse_pos[0])
            self.dragging = True
            return True
        
        return False
    
    def handle_mouse_up(self):
        """Handle mouse up event."""
        if self.dragging:
            self.dragging = False
            self.audio_manager.play_sound('click', 0, 0, volume=0.3)
    
    def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
        """Handle mouse motion event."""
        if self.dragging:
            self.set_value_from_position(mouse_pos[0])
    
    def render(self, surface: pygame.Surface):
        """Render the slider."""
        if not self.visible:
            return
        
        # Draw label
        label_surface = self.font.render(self.label, True, config.COLORS['white'])
        label_rect = label_surface.get_rect()
        label_rect.x = int(self.x)
        label_rect.y = int(self.y - 25)
        surface.blit(label_surface, label_rect)
        
        # Draw track background
        track_rect = pygame.Rect(self.x, self.track_y, self.width, self.track_height)
        pygame.draw.rect(surface, self.track_color, track_rect)
        pygame.draw.rect(surface, config.COLORS['gray'], track_rect, 1)
        
        # Draw track fill
        progress = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        fill_width = progress * self.width
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.track_y, fill_width, self.track_height)
            pygame.draw.rect(surface, self.track_fill_color, fill_rect)
        
        # Draw knob glow
        if self.glow_intensity > 0:
            knob_pos = self.get_knob_position()
            glow_radius = int(self.knob_radius * 2 * self.glow_intensity)
            glow_alpha = int(100 * self.glow_intensity)
            
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = (*self.knob_border_color, glow_alpha)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            
            surface.blit(glow_surface, (knob_pos[0] - glow_radius, knob_pos[1] - glow_radius))
        
        # Draw knob
        knob_pos = self.get_knob_position()
        knob_radius = int(self.knob_radius * self.knob_scale)
        
        # Knob shadow
        shadow_pos = (knob_pos[0] + 2, knob_pos[1] + 2)
        pygame.draw.circle(surface, config.COLORS['black'], shadow_pos, knob_radius)
        
        # Knob body
        pygame.draw.circle(surface, self.knob_color, knob_pos, knob_radius)
        pygame.draw.circle(surface, self.knob_border_color, knob_pos, knob_radius, 2)
        
        # Draw value
        if self.show_percentage:
            value_text = self.format_string.format(self.current_value)
        else:
            value_text = f"{self.current_value:.1f}"
        
        value_surface = self.font.render(value_text, True, config.COLORS['cyan'])
        value_rect = value_surface.get_rect()
        value_rect.x = int(self.x + self.width + 10)
        value_rect.centery = int(self.y + self.height // 2)
        surface.blit(value_surface, value_rect)


class ToggleControl(UIElement):
    """Animated toggle switch for boolean settings."""
    
    def __init__(self, x: float, y: float, width: float, height: float,
                 current_value: bool, label: str, font: pygame.font.Font,
                 audio_manager: AudioManager):
        super().__init__(x, y, width, height)
        self.current_value = current_value
        self.label = label
        self.font = font
        self.audio_manager = audio_manager
        
        # Toggle properties
        self.switch_width = 60
        self.switch_height = 30
        self.knob_size = 24
        
        # Animation
        self.switch_progress = 1.0 if current_value else 0.0
        self.scale = 1.0
        
        # Colors
        self.off_color = config.COLORS['dark_gray']
        self.on_color = config.COLORS['green']
        self.knob_color = config.COLORS['white']
    
    def _update_animations(self, dt: float):
        """Update toggle animations."""
        # Switch progress animation
        target_progress = 1.0 if self.current_value else 0.0
        progress_speed = 8.0
        
        if self.switch_progress < target_progress:
            self.switch_progress = min(target_progress, self.switch_progress + progress_speed * dt)
        elif self.switch_progress > target_progress:
            self.switch_progress = max(target_progress, self.switch_progress - progress_speed * dt)
        
        # Scale animation
        target_scale = 1.1 if self.hovered else 1.0
        scale_speed = 6.0
        
        if self.scale < target_scale:
            self.scale = min(target_scale, self.scale + scale_speed * dt)
        elif self.scale > target_scale:
            self.scale = max(target_scale, self.scale - scale_speed * dt)
    
    def toggle_value(self):
        """Toggle the boolean value."""
        self.current_value = not self.current_value
        self.audio_manager.play_sound('click', 0, 0, volume=0.4)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle click event."""
        if self.is_point_inside(mouse_pos):
            self.toggle_value()
            return True
        return False
    
    def render(self, surface: pygame.Surface):
        """Render the toggle."""
        if not self.visible:
            return
        
        # Draw label
        label_surface = self.font.render(self.label, True, config.COLORS['white'])
        label_rect = label_surface.get_rect()
        label_rect.x = int(self.x)
        label_rect.centery = int(self.y + self.height // 2)
        surface.blit(label_surface, label_rect)
        
        # Calculate switch position
        switch_x = self.x + self.width - self.switch_width
        switch_y = self.y + (self.height - self.switch_height) // 2
        
        # Apply scale
        scaled_width = int(self.switch_width * self.scale)
        scaled_height = int(self.switch_height * self.scale)
        switch_rect = pygame.Rect(switch_x, switch_y, scaled_width, scaled_height)
        
        # Draw switch background
        current_color = self._blend_colors(self.off_color, self.on_color, self.switch_progress)
        pygame.draw.rect(surface, current_color, switch_rect, border_radius=scaled_height // 2)
        pygame.draw.rect(surface, config.COLORS['gray'], switch_rect, 2, border_radius=scaled_height // 2)
        
        # Draw knob
        knob_travel = scaled_width - scaled_height
        knob_x = switch_x + (scaled_height // 2) + (knob_travel * self.switch_progress)
        knob_y = switch_y + scaled_height // 2
        knob_radius = int((self.knob_size * self.scale) // 2)
        
        # Knob shadow
        shadow_pos = (int(knob_x + 2), int(knob_y + 2))
        pygame.draw.circle(surface, config.COLORS['black'], shadow_pos, knob_radius)
        
        # Knob body
        pygame.draw.circle(surface, self.knob_color, (int(knob_x), int(knob_y)), knob_radius)
        pygame.draw.circle(surface, config.COLORS['cyan'], (int(knob_x), int(knob_y)), knob_radius, 2)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)


class DropdownControl(UIElement):
    """Animated dropdown for multiple choice settings."""
    
    def __init__(self, x: float, y: float, width: float, height: float,
                 options: List[str], current_index: int, label: str,
                 font: pygame.font.Font, audio_manager: AudioManager):
        super().__init__(x, y, width, height)
        self.options = options
        self.current_index = current_index
        self.label = label
        self.font = font
        self.audio_manager = audio_manager
        
        # Dropdown state
        self.expanded = False
        self.option_height = 30
        self.max_visible_options = 5
        
        # Animation
        self.expand_progress = 0.0
        self.hover_option_index = -1
        
        # Colors
        self.background_color = config.COLORS['dark_gray']
        self.border_color = config.COLORS['gray']
        self.hover_color = config.COLORS['blue']
        self.selected_color = config.COLORS['cyan']
    
    def _update_animations(self, dt: float):
        """Update dropdown animations."""
        # Expand animation
        target_progress = 1.0 if self.expanded else 0.0
        expand_speed = 8.0
        
        if self.expand_progress < target_progress:
            self.expand_progress = min(target_progress, self.expand_progress + expand_speed * dt)
        elif self.expand_progress > target_progress:
            self.expand_progress = max(target_progress, self.expand_progress - expand_speed * dt)
    
    def toggle_expanded(self):
        """Toggle dropdown expanded state."""
        self.expanded = not self.expanded
        self.audio_manager.play_sound('click', 0, 0, volume=0.3)
    
    def select_option(self, index: int):
        """Select an option."""
        if 0 <= index < len(self.options):
            self.current_index = index
            self.expanded = False
            self.audio_manager.play_sound('click', 0, 0, volume=0.4)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle click event."""
        # Check main dropdown area
        main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if main_rect.collidepoint(mouse_pos):
            self.toggle_expanded()
            return True
        
        # Check options if expanded
        if self.expanded and self.expand_progress > 0.5:
            options_y = self.y + self.height
            visible_options = min(len(self.options), self.max_visible_options)
            
            for i in range(visible_options):
                option_rect = pygame.Rect(self.x, options_y + i * self.option_height,
                                        self.width, self.option_height)
                if option_rect.collidepoint(mouse_pos):
                    self.select_option(i)
                    return True
        
        # Click outside - close dropdown
        if self.expanded:
            self.expanded = False
            return True
        
        return False
    
    def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
        """Handle mouse motion for hover effects."""
        self.hover_option_index = -1
        
        if self.expanded and self.expand_progress > 0.5:
            options_y = self.y + self.height
            visible_options = min(len(self.options), self.max_visible_options)
            
            for i in range(visible_options):
                option_rect = pygame.Rect(self.x, options_y + i * self.option_height,
                                        self.width, self.option_height)
                if option_rect.collidepoint(mouse_pos):
                    self.hover_option_index = i
                    break
    
    def render(self, surface: pygame.Surface):
        """Render the dropdown."""
        if not self.visible:
            return
        
        # Draw label
        label_surface = self.font.render(self.label, True, config.COLORS['white'])
        label_rect = label_surface.get_rect()
        label_rect.x = int(self.x)
        label_rect.y = int(self.y - 25)
        surface.blit(label_surface, label_rect)
        
        # Draw main dropdown box
        main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        color = self.hover_color if self.hovered else self.background_color
        pygame.draw.rect(surface, color, main_rect)
        pygame.draw.rect(surface, self.border_color, main_rect, 2)
        
        # Draw current selection
        if 0 <= self.current_index < len(self.options):
            current_text = self.options[self.current_index]
            text_surface = self.font.render(current_text, True, config.COLORS['white'])
            text_rect = text_surface.get_rect()
            text_rect.x = int(self.x + 10)
            text_rect.centery = int(self.y + self.height // 2)
            surface.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_size = 8
        arrow_x = int(self.x + self.width - 20)
        arrow_y = int(self.y + self.height // 2)
        
        if self.expanded:
            # Up arrow
            arrow_points = [
                (arrow_x, arrow_y + arrow_size // 2),
                (arrow_x - arrow_size // 2, arrow_y - arrow_size // 2),
                (arrow_x + arrow_size // 2, arrow_y - arrow_size // 2)
            ]
        else:
            # Down arrow
            arrow_points = [
                (arrow_x, arrow_y - arrow_size // 2),
                (arrow_x - arrow_size // 2, arrow_y + arrow_size // 2),
                (arrow_x + arrow_size // 2, arrow_y + arrow_size // 2)
            ]
        
        pygame.draw.polygon(surface, config.COLORS['white'], arrow_points)
        
        # Draw expanded options
        if self.expand_progress > 0:
            self._draw_expanded_options(surface)
    
    def _draw_expanded_options(self, surface: pygame.Surface):
        """Draw expanded dropdown options."""
        options_y = self.y + self.height
        visible_options = min(len(self.options), self.max_visible_options)
        
        # Calculate expanded height
        expanded_height = int(visible_options * self.option_height * self.expand_progress)
        
        if expanded_height > 0:
            # Create clipping surface
            options_surface = pygame.Surface((self.width, expanded_height), pygame.SRCALPHA)
            
            # Draw options
            for i in range(visible_options):
                option_y = i * self.option_height
                option_rect = pygame.Rect(0, option_y, self.width, self.option_height)
                
                # Option background
                if i == self.hover_option_index:
                    color = self.hover_color
                elif i == self.current_index:
                    color = self.selected_color
                else:
                    color = self.background_color
                
                pygame.draw.rect(options_surface, color, option_rect)
                pygame.draw.rect(options_surface, self.border_color, option_rect, 1)
                
                # Option text
                if i < len(self.options):
                    text_surface = self.font.render(self.options[i], True, config.COLORS['white'])
                    text_rect = text_surface.get_rect()
                    text_rect.x = 10
                    text_rect.centery = option_y + self.option_height // 2
                    options_surface.blit(text_surface, text_rect)
            
            # Apply alpha for animation
            options_surface.set_alpha(int(255 * self.expand_progress))
            surface.blit(options_surface, (self.x, options_y))


class CategoryTab(UIElement):
    """Tab for settings categories."""
    
    def __init__(self, x: float, y: float, width: float, height: float,
                 category: SettingsCategory, font: pygame.font.Font,
                 audio_manager: AudioManager):
        super().__init__(x, y, width, height)
        self.category = category
        self.font = font
        self.audio_manager = audio_manager
        
        # State
        self.active = False
        
        # Animation
        self.activation_progress = 0.0
        
        # Colors
        self.inactive_color = config.COLORS['dark_gray']
        self.active_color = config.COLORS['blue']
        self.text_color = config.COLORS['white']
    
    def _update_animations(self, dt: float):
        """Update tab animations."""
        target_progress = 1.0 if self.active else 0.0
        progress_speed = 6.0
        
        if self.activation_progress < target_progress:
            self.activation_progress = min(target_progress, self.activation_progress + progress_speed * dt)
        elif self.activation_progress > target_progress:
            self.activation_progress = max(target_progress, self.activation_progress - progress_speed * dt)
    
    def set_active(self, active: bool):
        """Set tab active state."""
        if active != self.active:
            self.active = active
            if active:
                self.audio_manager.play_sound('click', 0, 0, volume=0.3)
    
    def render(self, surface: pygame.Surface):
        """Render the tab."""
        if not self.visible:
            return
        
        # Calculate colors
        bg_color = self._blend_colors(self.inactive_color, self.active_color, self.activation_progress)
        
        # Draw tab background
        tab_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, bg_color, tab_rect)
        
        # Draw border (bottom only if active)
        if self.active:
            border_color = config.COLORS['cyan']
            border_rect = pygame.Rect(self.x, self.y + self.height - 3, self.width, 3)
            pygame.draw.rect(surface, border_color, border_rect)
        else:
            pygame.draw.rect(surface, config.COLORS['gray'], tab_rect, 1)
        
        # Draw text
        text = self.category.value.replace('_', ' ').title()
        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=tab_rect.center)
        surface.blit(text_surface, text_rect)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)


class SettingsScene(BaseScene):
    """
    Comprehensive settings scene with modern UI.
    """
    
    def __init__(self, scene_manager, input_manager: InputManager,
                 audio_manager: AudioManager, settings_manager):
        super().__init__(scene_manager)
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        self.settings_manager = settings_manager
        
        # Current category
        self.current_category = SettingsCategory.GRAPHICS
        
        # Load fonts
        self._load_fonts()
        
        # UI Elements
        self.category_tabs: List[CategoryTab] = []
        self.controls: Dict[str, UIElement] = {}
        self.back_button = None
        self.apply_button = None
        self.reset_button = None
        
        # Layout
        self.tab_height = 50
        self.control_spacing = 80
        self.left_margin = 50
        self.top_margin = 120
        
        # State
        self.settings_changed = False
        self.applying_settings = False
        
        self._setup_ui_elements()
        self._load_current_settings()
        
        print("Settings scene initialized")
    
    def _load_fonts(self):
        """Load fonts for the settings menu."""
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.tab_font = pygame.font.Font(None, 28)
            self.control_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.title_font = pygame.font.Font(None, 48)
            self.tab_font = pygame.font.Font(None, 28)
            self.control_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
    
    def _setup_ui_elements(self):
        """Setup all UI elements."""
        # Create category tabs
        tab_width = 150
        tab_y = 60
        
        for i, category in enumerate(SettingsCategory):
            tab_x = 50 + i * (tab_width + 10)
            tab = CategoryTab(tab_x, tab_y, tab_width, self.tab_height,
                            category, self.tab_font, self.audio_manager)
            tab.set_active(category == self.current_category)
            self.category_tabs.append(tab)
        
        # Create settings controls for each category
        self._create_graphics_controls()
        self._create_audio_controls()
        self._create_gameplay_controls()
        self._create_controls_controls()
        self._create_accessibility_controls()
        
        # Create action buttons
        button_width = 120
        button_height = 40
        button_y = config.SCREEN_HEIGHT - 80
        
        self.back_button = AnimatedButton(
            50, button_y, button_width, button_height,
            "Back", self.control_font, self.audio_manager
        )
        
        self.apply_button = AnimatedButton(
            config.SCREEN_WIDTH - 300, button_y, button_width, button_height,
            "Apply", self.control_font, self.audio_manager
        )
        
        self.reset_button = AnimatedButton(
            config.SCREEN_WIDTH - 170, button_y, button_width, button_height,
            "Reset", self.control_font, self.audio_manager
        )
        
        # Style action buttons
        self.apply_button.border_color = config.COLORS['green']
        self.apply_button.hover_color = config.COLORS['green']
        self.reset_button.border_color = config.COLORS['red']
        self.reset_button.hover_color = config.COLORS['red']
    
    def _create_graphics_controls(self):
        """Create graphics settings controls."""
        y_offset = self.top_margin
        controls = {}
        
        # Resolution dropdown
        resolutions = ["1920x1080", "1680x1050", "1600x900", "1366x768", "1280x720"]
        controls['resolution'] = DropdownControl(
            self.left_margin, y_offset, 200, 35,
            resolutions, 0, "Resolution", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Fullscreen toggle
        controls['fullscreen'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            False, "Fullscreen", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # VSync toggle
        controls['vsync'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            True, "VSync", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Graphics Quality dropdown
        quality_options = ["Low", "Medium", "High", "Ultra"]
        controls['graphics_quality'] = DropdownControl(
            self.left_margin, y_offset, 200, 35,
            quality_options, 2, "Graphics Quality", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Particle Quality slider
        controls['particle_quality'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            0, 100, 75, "Particle Quality", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Shadow Quality slider
        controls['shadow_quality'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            0, 100, 50, "Shadow Quality", self.control_font, self.audio_manager
        )
        
        self.controls[SettingsCategory.GRAPHICS] = controls
    
    def _create_audio_controls(self):
        """Create audio settings controls."""
        y_offset = self.top_margin
        controls = {}
        
        # Master Volume slider
        controls['master_volume'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            0, 100, 80, "Master Volume", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Music Volume slider
        controls['music_volume'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            0, 100, 70, "Music Volume", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # SFX Volume slider
        controls['sfx_volume'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            0, 100, 85, "Sound Effects", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Voice Volume slider
        controls['voice_volume'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            0, 100, 90, "Voice Volume", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Audio Quality dropdown
        quality_options = ["Low", "Medium", "High"]
        controls['audio_quality'] = DropdownControl(
            self.left_margin, y_offset, 200, 35,
            quality_options, 1, "Audio Quality", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Spatial Audio toggle
        controls['spatial_audio'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            True, "3D Spatial Audio", self.control_font, self.audio_manager
        )
        
        self.controls[SettingsCategory.AUDIO] = controls
    
    def _create_gameplay_controls(self):
        """Create gameplay settings controls."""
        y_offset = self.top_margin
        controls = {}
        
        # Difficulty dropdown
        difficulty_options = ["Easy", "Normal", "Hard", "Nightmare"]
        controls['difficulty'] = DropdownControl(
            self.left_margin, y_offset, 200, 35,
            difficulty_options, 1, "Difficulty", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Auto-save toggle
        controls['auto_save'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            True, "Auto-save", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Save Frequency slider
        controls['save_frequency'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            1, 10, 5, "Save Frequency (minutes)", self.control_font, self.audio_manager
        )
        controls['save_frequency'].show_percentage = False
        controls['save_frequency'].format_string = "{:.0f} min"
        y_offset += self.control_spacing
        
        # Mouse Sensitivity slider
        controls['mouse_sensitivity'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            10, 200, 100, "Mouse Sensitivity", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Camera Shake toggle
        controls['camera_shake'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            True, "Camera Shake", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Show FPS toggle
        controls['show_fps'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            False, "Show FPS", self.control_font, self.audio_manager
        )
        
        self.controls[SettingsCategory.GAMEPLAY] = controls
    
    def _create_controls_controls(self):
        """Create control settings."""
        y_offset = self.top_margin
        controls = {}
        
        # Key binding display would go here
        # For now, just add a placeholder
        controls['key_bindings'] = AnimatedButton(
            self.left_margin, y_offset, 200, 40,
            "Configure Keys", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Gamepad support toggle
        controls['gamepad_support'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            True, "Gamepad Support", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Invert Y-axis toggle
        controls['invert_y'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            False, "Invert Y-axis", self.control_font, self.audio_manager
        )
        
        self.controls[SettingsCategory.CONTROLS] = controls
    
    def _create_accessibility_controls(self):
        """Create accessibility settings controls."""
        y_offset = self.top_margin
        controls = {}
        
        # Colorblind Support dropdown
        colorblind_options = ["None", "Protanopia", "Deuteranopia", "Tritanopia"]
        controls['colorblind_support'] = DropdownControl(
            self.left_margin, y_offset, 200, 35,
            colorblind_options, 0, "Colorblind Support", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # High Contrast toggle
        controls['high_contrast'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            False, "High Contrast Mode", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Font Size slider
        controls['font_size'] = SliderControl(
            self.left_margin, y_offset, 250, 35,
            80, 150, 100, "Font Size", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Motion Reduction toggle
        controls['reduce_motion'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            False, "Reduce Motion", self.control_font, self.audio_manager
        )
        y_offset += self.control_spacing
        
        # Screen Reader toggle
        controls['screen_reader'] = ToggleControl(
            self.left_margin, y_offset, 300, 35,
            False, "Screen Reader Support", self.control_font, self.audio_manager
        )
        
        self.controls[SettingsCategory.ACCESSIBILITY] = controls
    
    def _load_current_settings(self):
        """Load current settings values into controls."""
        # This would load from settings_manager
        # For now, just use default values
        pass
    
    def update(self, dt: float):
        """Update settings scene."""
        # Update tabs
        for tab in self.category_tabs:
            tab.update(dt, pygame.mouse.get_pos())
        
        # Update current category controls
        if self.current_category in self.controls:
            for control in self.controls[self.current_category].values():
                control.update(dt, pygame.mouse.get_pos())
        
        # Update action buttons
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(dt, mouse_pos)
        self.apply_button.update(dt, mouse_pos)
        self.reset_button.update(dt, mouse_pos)
        
        # Check if settings changed
        self._check_settings_changed()
    
    def _check_settings_changed(self):
        """Check if any settings have been modified."""
        # This would compare current control values with saved settings
        # For now, assume settings can change
        pass
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check tab clicks
            for tab in self.category_tabs:
                if tab.is_point_inside(mouse_pos):
                    self._switch_category(tab.category)
                    return True
            
            # Check current category controls
            if self.current_category in self.controls:
                for control in self.controls[self.current_category].values():
                    if hasattr(control, 'handle_click'):
                        if control.handle_click(mouse_pos):
                            self.settings_changed = True
                            return True
                    elif hasattr(control, 'handle_mouse_down'):
                        if control.handle_mouse_down(mouse_pos):
                            return True
            
            # Check action buttons
            if self.back_button.is_point_inside(mouse_pos):
                self._handle_back()
                return True
            elif self.apply_button.is_point_inside(mouse_pos):
                self._handle_apply()
                return True
            elif self.reset_button.is_point_inside(mouse_pos):
                self._handle_reset()
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Handle slider releases
            if self.current_category in self.controls:
                for control in self.controls[self.current_category].values():
                    if hasattr(control, 'handle_mouse_up'):
                        control.handle_mouse_up()
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle slider dragging and dropdown hover
            if self.current_category in self.controls:
                for control in self.controls[self.current_category].values():
                    if hasattr(control, 'handle_mouse_motion'):
                        control.handle_mouse_motion(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._handle_back()
                return True
            elif event.key == pygame.K_RETURN:
                self._handle_apply()
                return True
        
        return False
    
    def _switch_category(self, category: SettingsCategory):
        """Switch to a different settings category."""
        if category != self.current_category:
            # Update tab states
            for tab in self.category_tabs:
                tab.set_active(tab.category == category)
            
            self.current_category = category
    
    def _handle_back(self):
        """Handle back button."""
        if self.settings_changed:
            # Show confirmation dialog
            # For now, just go back
            pass
        
        transition = SceneTransition("slide", 0.5, direction="right")
        self.scene_manager.change_scene("main_menu", transition)
    
    def _handle_apply(self):
        """Handle apply button."""
        self.applying_settings = True
        
        # Apply all settings
        self._apply_settings()
        
        self.settings_changed = False
        self.applying_settings = False
        
        # Show confirmation message
        self.audio_manager.play_sound('levelup', 0, 0, volume=0.5)
    
    def _handle_reset(self):
        """Handle reset button."""
        # Reset all settings to defaults
        self._reset_settings()
        self.settings_changed = True
        
        self.audio_manager.play_sound('click', 0, 0, volume=0.5)
    
    def _apply_settings(self):
        """Apply all current settings."""
        # This would save settings to settings_manager
        # and apply them to the game
        pass
    
    def _reset_settings(self):
        """Reset all settings to default values."""
        # This would reset all control values
        pass
    
    def render(self, screen: pygame.Surface):
        """Render the settings scene."""
        # Clear screen with dark background
        screen.fill(config.COLORS['dark_blue'])
        
        # Draw title
        title_text = self.title_font.render("SETTINGS", True, config.COLORS['white'])
        title_rect = title_text.get_rect()
        title_rect.centerx = config.SCREEN_WIDTH // 2
        title_rect.y = 20
        screen.blit(title_text, title_rect)
        
        # Draw category tabs
        for tab in self.category_tabs:
            tab.render(screen)
        
        # Draw current category controls
        if self.current_category in self.controls:
            for control in self.controls[self.current_category].values():
                control.render(screen)
        
        # Draw action buttons
        self.back_button.render(screen)
        self.apply_button.render(screen)
        self.reset_button.render(screen)
        
        # Draw settings changed indicator
        if self.settings_changed:
            indicator_text = self.small_font.render("Settings modified - click Apply to save", 
                                                  True, config.COLORS['yellow'])
            indicator_rect = indicator_text.get_rect()
            indicator_rect.centerx = config.SCREEN_WIDTH // 2
            indicator_rect.y = config.SCREEN_HEIGHT - 120
            screen.blit(indicator_text, indicator_rect)
        
        # Draw applying indicator
        if self.applying_settings:
            applying_text = self.control_font.render("Applying settings...", 
                                                   True, config.COLORS['green'])
            applying_rect = applying_text.get_rect()
            applying_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
            
            # Draw background
            bg_rect = applying_rect.inflate(40, 20)
            pygame.draw.rect(screen, config.COLORS['black'], bg_rect)
            pygame.draw.rect(screen, config.COLORS['green'], bg_rect, 2)
            
            screen.blit(applying_text, applying_rect)
    
    def on_enter(self):
        """Called when entering the scene."""
        # Load current settings
        self._load_current_settings()
        self.settings_changed = False
    
    def on_exit(self):
        """Called when exiting the scene."""
        pass