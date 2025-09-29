"""
Forest Survival - In-Game HUD System
Modern, adaptive HUD with smooth animations and contextual information.
"""

import pygame
import math
import time
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

import config
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.systems.particle_system import ParticleSystem, PARTICLE_PRESETS


class HUDState(Enum):
    """HUD display states."""
    NORMAL = "normal"
    INVENTORY = "inventory"
    MAP = "map"
    PAUSED = "paused"
    DIALOGUE = "dialogue"
    COMBAT = "combat"
    STEALTH = "stealth"


class HUDElement:
    """Base class for HUD elements."""
    
    def __init__(self, x: float, y: float, width: float, height: float,
                 anchor: str = "top_left"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = anchor
        
        # Animation properties
        self.alpha = 255
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # State
        self.visible = True
        self.enabled = True
        self.priority = 0  # Higher priority elements render on top
        
        # Animation timers
        self.animation_timer = 0.0
        self.pulse_timer = 0.0
        self.fade_timer = 0.0
        
        # Effects
        self.glow_intensity = 0.0
        self.shake_intensity = 0.0
        self.flash_alpha = 0.0
    
    def update(self, dt: float, screen_width: int, screen_height: int):
        """Update HUD element animations and state."""
        self.animation_timer += dt
        self.pulse_timer += dt
        self.fade_timer += dt
        
        # Update position based on anchor
        self._update_anchored_position(screen_width, screen_height)
        
        # Update animations
        self._update_animations(dt)
        
        # Reduce effects over time
        self.glow_intensity = max(0.0, self.glow_intensity - dt * 2)
        self.shake_intensity = max(0.0, self.shake_intensity - dt * 5)
        self.flash_alpha = max(0.0, self.flash_alpha - dt * 300)
    
    def _update_anchored_position(self, screen_width: int, screen_height: int):
        """Update position based on anchor point."""
        if self.anchor == "top_right":
            self.x = screen_width - self.width - abs(self.x)
        elif self.anchor == "bottom_left":
            self.y = screen_height - self.height - abs(self.y)
        elif self.anchor == "bottom_right":
            self.x = screen_width - self.width - abs(self.x)
            self.y = screen_height - self.height - abs(self.y)
        elif self.anchor == "center":
            self.x = screen_width // 2 - self.width // 2 + self.x
            self.y = screen_height // 2 - self.height // 2 + self.y
    
    def _update_animations(self, dt: float):
        """Update specific animations - override in subclasses."""
        pass
    
    def add_effect(self, effect_type: str, intensity: float = 1.0):
        """Add visual effect to element."""
        if effect_type == "glow":
            self.glow_intensity = min(1.0, self.glow_intensity + intensity)
        elif effect_type == "shake":
            self.shake_intensity = min(1.0, self.shake_intensity + intensity)
        elif effect_type == "flash":
            self.flash_alpha = min(255, self.flash_alpha + intensity * 255)
    
    def get_render_rect(self) -> pygame.Rect:
        """Get rectangle for rendering with effects applied."""
        # Apply shake
        shake_x = 0
        shake_y = 0
        if self.shake_intensity > 0:
            import random
            shake_amount = self.shake_intensity * 5
            shake_x = random.uniform(-shake_amount, shake_amount)
            shake_y = random.uniform(-shake_amount, shake_amount)
        
        # Calculate final position with scale and effects
        scaled_width = self.width * self.scale
        scaled_height = self.height * self.scale
        render_x = self.x + self.offset_x + shake_x - (scaled_width - self.width) / 2
        render_y = self.y + self.offset_y + shake_y - (scaled_height - self.height) / 2
        
        return pygame.Rect(render_x, render_y, scaled_width, scaled_height)
    
    def render(self, surface: pygame.Surface):
        """Render the HUD element - override in subclasses."""
        pass


class HealthBar(HUDElement):
    """Animated health bar with damage effects."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y, width, height)
        
        # Health values
        self.max_health = 100.0
        self.current_health = 100.0
        self.displayed_health = 100.0  # For smooth animation
        self.last_damage_time = 0.0
        
        # Visual properties
        self.background_color = config.COLORS['dark_gray']
        self.health_color = config.COLORS['green']
        self.low_health_color = config.COLORS['red']
        self.damage_color = config.COLORS['yellow']
        self.border_color = config.COLORS['white']
        
        # Animation
        self.damage_flash_timer = 0.0
        self.low_health_pulse = 0.0
        self.health_change_speed = 50.0  # Health per second for smooth transition
        
        # Segments for better visual
        self.segment_count = 10
        self.segment_spacing = 2
    
    def set_health(self, health: float, max_health: float = None):
        """Set current health values."""
        if max_health is not None:
            self.max_health = max_health
        
        # Detect damage
        if health < self.current_health:
            self.last_damage_time = time.time()
            self.damage_flash_timer = 0.3
            self.add_effect("flash", 0.8)
            self.add_effect("shake", 0.5)
        
        self.current_health = max(0, min(max_health or self.max_health, health))
    
    def _update_animations(self, dt: float):
        """Update health bar animations."""
        # Smooth health display transition
        health_diff = self.current_health - self.displayed_health
        if abs(health_diff) > 0.1:
            move_amount = self.health_change_speed * dt
            if health_diff > 0:
                self.displayed_health = min(self.current_health, self.displayed_health + move_amount)
            else:
                self.displayed_health = max(self.current_health, self.displayed_health - move_amount)
        else:
            self.displayed_health = self.current_health
        
        # Update timers
        self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        self.low_health_pulse += dt * 4
        
        # Low health effects
        if self.current_health / self.max_health < 0.25:
            self.add_effect("glow", 0.3)
    
    def render(self, surface: pygame.Surface):
        """Render the health bar."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Draw background
        pygame.draw.rect(surface, self.background_color, render_rect)
        pygame.draw.rect(surface, self.border_color, render_rect, 2)
        
        # Calculate health percentage
        health_percent = self.displayed_health / self.max_health if self.max_health > 0 else 0
        
        # Determine health color
        if health_percent < 0.25:
            # Pulsing red for low health
            pulse_factor = (math.sin(self.low_health_pulse) + 1) / 2
            health_color = self._blend_colors(self.low_health_color, config.COLORS['dark_red'], pulse_factor * 0.5)
        elif health_percent < 0.5:
            # Transition from red to yellow
            transition = (health_percent - 0.25) / 0.25
            health_color = self._blend_colors(self.low_health_color, config.COLORS['yellow'], transition)
        else:
            # Green health
            health_color = self.health_color
        
        # Draw health segments
        segment_width = (render_rect.width - (self.segment_count - 1) * self.segment_spacing) // self.segment_count
        
        for i in range(self.segment_count):
            segment_x = render_rect.x + i * (segment_width + self.segment_spacing)
            segment_rect = pygame.Rect(segment_x, render_rect.y + 2, segment_width, render_rect.height - 4)
            
            # Calculate if this segment should be filled
            segment_threshold = (i + 1) / self.segment_count
            if health_percent >= segment_threshold:
                # Full segment
                pygame.draw.rect(surface, health_color, segment_rect)
            elif health_percent > i / self.segment_count:
                # Partial segment
                partial_height = int((health_percent - i / self.segment_count) * self.segment_count * segment_rect.height)
                partial_rect = pygame.Rect(segment_rect.x, segment_rect.bottom - partial_height, 
                                         segment_rect.width, partial_height)
                pygame.draw.rect(surface, health_color, partial_rect)
        
        # Draw damage flash
        if self.damage_flash_timer > 0:
            flash_alpha = int(255 * self.damage_flash_timer / 0.3)
            flash_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
            flash_surface.fill((*self.damage_color, flash_alpha))
            surface.blit(flash_surface, render_rect.topleft)
        
        # Draw glow effect
        if self.glow_intensity > 0:
            self._draw_glow(surface, render_rect)
        
        # Draw health text
        health_text = f"{int(self.current_health)}/{int(self.max_health)}"
        font = pygame.font.Font(None, 20)
        text_surface = font.render(health_text, True, config.COLORS['white'])
        text_rect = text_surface.get_rect(center=render_rect.center)
        
        # Text shadow
        shadow_surface = font.render(health_text, True, config.COLORS['black'])
        shadow_rect = text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)
    
    def _draw_glow(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw glow effect around health bar."""
        glow_size = int(8 * self.glow_intensity)
        glow_alpha = int(100 * self.glow_intensity)
        
        glow_surface = pygame.Surface((rect.width + glow_size * 2, rect.height + glow_size * 2), pygame.SRCALPHA)
        
        for i in range(glow_size, 0, -1):
            alpha = int(glow_alpha * (1 - i / glow_size))
            if alpha > 0:
                glow_color = (*self.low_health_color, alpha)
                glow_rect = pygame.Rect(glow_size - i, glow_size - i, 
                                      rect.width + i * 2, rect.height + i * 2)
                pygame.draw.rect(glow_surface, glow_color, glow_rect, 2)
        
        surface.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))


class StaminaBar(HUDElement):
    """Animated stamina bar with depletion effects."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y, width, height)
        
        # Stamina values
        self.max_stamina = 100.0
        self.current_stamina = 100.0
        self.displayed_stamina = 100.0
        
        # Visual properties
        self.background_color = config.COLORS['dark_gray']
        self.stamina_color = config.COLORS['cyan']
        self.low_stamina_color = config.COLORS['orange']
        self.depleted_color = config.COLORS['red']
        self.border_color = config.COLORS['white']
        
        # Animation
        self.stamina_change_speed = 75.0
        self.exhaustion_pulse = 0.0
        self.regenerating = False
        self.regen_particles = []
    
    def set_stamina(self, stamina: float, max_stamina: float = None):
        """Set current stamina values."""
        if max_stamina is not None:
            self.max_stamina = max_stamina
        
        old_stamina = self.current_stamina
        self.current_stamina = max(0, min(max_stamina or self.max_stamina, stamina))
        
        # Detect regeneration
        self.regenerating = self.current_stamina > old_stamina
        
        # Effects for low stamina
        if self.current_stamina < 20:
            self.add_effect("glow", 0.2)
    
    def _update_animations(self, dt: float):
        """Update stamina bar animations."""
        # Smooth stamina display transition
        stamina_diff = self.current_stamina - self.displayed_stamina
        if abs(stamina_diff) > 0.1:
            move_amount = self.stamina_change_speed * dt
            if stamina_diff > 0:
                self.displayed_stamina = min(self.current_stamina, self.displayed_stamina + move_amount)
            else:
                self.displayed_stamina = max(self.current_stamina, self.displayed_stamina - move_amount)
        else:
            self.displayed_stamina = self.current_stamina
        
        # Update exhaustion pulse
        self.exhaustion_pulse += dt * 6
        
        # Update regeneration particles
        if self.regenerating and self.current_stamina < self.max_stamina:
            self._spawn_regen_particles()
        
        self._update_regen_particles(dt)
    
    def _spawn_regen_particles(self):
        """Spawn stamina regeneration particles."""
        if len(self.regen_particles) < 10:
            import random
            particle = {
                'x': random.uniform(self.x, self.x + self.width),
                'y': self.y + self.height,
                'vel_y': random.uniform(-30, -20),
                'life': 1.0,
                'max_life': 1.0,
                'size': random.uniform(2, 4)
            }
            self.regen_particles.append(particle)
    
    def _update_regen_particles(self, dt: float):
        """Update regeneration particles."""
        for particle in self.regen_particles[:]:
            particle['y'] += particle['vel_y'] * dt
            particle['life'] -= dt
            
            if particle['life'] <= 0:
                self.regen_particles.remove(particle)
    
    def render(self, surface: pygame.Surface):
        """Render the stamina bar."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Draw background
        pygame.draw.rect(surface, self.background_color, render_rect)
        pygame.draw.rect(surface, self.border_color, render_rect, 2)
        
        # Calculate stamina percentage
        stamina_percent = self.displayed_stamina / self.max_stamina if self.max_stamina > 0 else 0
        
        # Determine stamina color
        if stamina_percent < 0.1:
            # Pulsing red for depleted stamina
            pulse_factor = (math.sin(self.exhaustion_pulse) + 1) / 2
            stamina_color = self._blend_colors(self.depleted_color, config.COLORS['dark_red'], pulse_factor * 0.5)
        elif stamina_percent < 0.3:
            # Orange for low stamina
            stamina_color = self.low_stamina_color
        else:
            # Cyan for normal stamina
            stamina_color = self.stamina_color
        
        # Draw stamina fill
        fill_width = int(render_rect.width * stamina_percent)
        if fill_width > 0:
            fill_rect = pygame.Rect(render_rect.x + 2, render_rect.y + 2, 
                                  fill_width - 4, render_rect.height - 4)
            pygame.draw.rect(surface, stamina_color, fill_rect)
            
            # Add gradient effect
            for i in range(fill_rect.height // 2):
                alpha = int(50 * (1 - i / (fill_rect.height // 2)))
                gradient_color = (*config.COLORS['white'], alpha)
                gradient_rect = pygame.Rect(fill_rect.x, fill_rect.y + i, fill_rect.width, 1)
                surface.fill(gradient_color, gradient_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Draw regeneration particles
        for particle in self.regen_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            if alpha > 0:
                particle_color = (*self.stamina_color, alpha)
                pygame.draw.circle(surface, particle_color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 int(particle['size']))
        
        # Draw glow effect for low stamina
        if self.glow_intensity > 0:
            self._draw_glow(surface, render_rect)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)
    
    def _draw_glow(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw glow effect around stamina bar."""
        glow_size = int(6 * self.glow_intensity)
        glow_alpha = int(80 * self.glow_intensity)
        
        glow_surface = pygame.Surface((rect.width + glow_size * 2, rect.height + glow_size * 2), pygame.SRCALPHA)
        
        for i in range(glow_size, 0, -1):
            alpha = int(glow_alpha * (1 - i / glow_size))
            if alpha > 0:
                glow_color = (*self.low_stamina_color, alpha)
                glow_rect = pygame.Rect(glow_size - i, glow_size - i, 
                                      rect.width + i * 2, rect.height + i * 2)
                pygame.draw.rect(glow_surface, glow_color, glow_rect, 2)
        
        surface.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))


class Minimap(HUDElement):
    """Animated minimap with real-time updates."""
    
    def __init__(self, x: float, y: float, size: float):
        super().__init__(x, y, size, size, anchor="top_right")
        
        # Map properties
        self.zoom_level = 1.0
        self.rotation = 0.0
        self.center_x = 0.0
        self.center_y = 0.0
        
        # Visual elements
        self.background_color = config.COLORS['dark_blue']
        self.border_color = config.COLORS['cyan']
        self.player_color = config.COLORS['green']
        self.enemy_color = config.COLORS['red']
        self.objective_color = config.COLORS['yellow']
        
        # Map data
        self.terrain_data = []
        self.entities = []
        self.objectives = []
        self.fog_of_war = True
        
        # Animation
        self.pulse_timer = 0.0
        self.scan_angle = 0.0
        self.scan_speed = 2.0
    
    def update_map_data(self, player_pos: Tuple[float, float], entities: List[Dict], 
                       objectives: List[Dict] = None):
        """Update minimap with current game data."""
        self.center_x, self.center_y = player_pos
        self.entities = entities or []
        self.objectives = objectives or []
    
    def _update_animations(self, dt: float):
        """Update minimap animations."""
        self.pulse_timer += dt * 3
        self.scan_angle += self.scan_speed * dt
        
        if self.scan_angle > math.pi * 2:
            self.scan_angle = 0.0
    
    def render(self, surface: pygame.Surface):
        """Render the minimap."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Create minimap surface
        minimap_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.circle(minimap_surface, self.background_color, 
                         (render_rect.width // 2, render_rect.height // 2), 
                         render_rect.width // 2 - 2)
        
        # Draw border with pulse effect
        border_alpha = int(200 + 55 * math.sin(self.pulse_timer))
        border_color = (*self.border_color, border_alpha)
        pygame.draw.circle(minimap_surface, border_color, 
                         (render_rect.width // 2, render_rect.height // 2), 
                         render_rect.width // 2 - 2, 3)
        
        # Draw terrain (simplified)
        self._draw_terrain(minimap_surface, render_rect)
        
        # Draw entities
        self._draw_entities(minimap_surface, render_rect)
        
        # Draw objectives
        self._draw_objectives(minimap_surface, render_rect)
        
        # Draw player (center)
        player_radius = 6
        pygame.draw.circle(minimap_surface, self.player_color,
                         (render_rect.width // 2, render_rect.height // 2), 
                         player_radius)
        pygame.draw.circle(minimap_surface, config.COLORS['white'],
                         (render_rect.width // 2, render_rect.height // 2), 
                         player_radius, 2)
        
        # Draw player direction indicator
        direction_length = 12
        direction_end_x = render_rect.width // 2 + math.cos(self.rotation) * direction_length
        direction_end_y = render_rect.height // 2 + math.sin(self.rotation) * direction_length
        pygame.draw.line(minimap_surface, config.COLORS['white'],
                        (render_rect.width // 2, render_rect.height // 2),
                        (direction_end_x, direction_end_y), 2)
        
        # Draw radar scan effect
        if self.fog_of_war:
            self._draw_radar_scan(minimap_surface, render_rect)
        
        # Apply circular mask
        self._apply_circular_mask(minimap_surface, render_rect)
        
        surface.blit(minimap_surface, render_rect.topleft)
    
    def _draw_terrain(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw simplified terrain on minimap."""
        # Draw some sample terrain features
        center_x = rect.width // 2
        center_y = rect.height // 2
        
        # Trees (small green dots)
        import random
        random.seed(42)  # Consistent terrain
        for _ in range(20):
            x = random.randint(10, rect.width - 10)
            y = random.randint(10, rect.height - 10)
            
            # Check if within circle
            dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if dist < rect.width // 2 - 10:
                pygame.draw.circle(surface, config.COLORS['dark_green'], (x, y), 2)
    
    def _draw_entities(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw entities on minimap."""
        center_x = rect.width // 2
        center_y = rect.height // 2
        map_scale = 0.1  # Scale factor for world to minimap coordinates
        
        for entity in self.entities:
            # Calculate relative position
            rel_x = (entity['x'] - self.center_x) * map_scale
            rel_y = (entity['y'] - self.center_y) * map_scale
            
            # Convert to minimap coordinates
            map_x = center_x + rel_x
            map_y = center_y + rel_y
            
            # Check if within minimap bounds
            if 0 <= map_x < rect.width and 0 <= map_y < rect.height:
                dist = math.sqrt((map_x - center_x) ** 2 + (map_y - center_y) ** 2)
                if dist < rect.width // 2 - 5:
                    entity_color = self.enemy_color if entity.get('hostile', False) else config.COLORS['blue']
                    pygame.draw.circle(surface, entity_color, (int(map_x), int(map_y)), 3)
    
    def _draw_objectives(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw objectives on minimap."""
        center_x = rect.width // 2
        center_y = rect.height // 2
        map_scale = 0.1
        
        for objective in self.objectives:
            # Calculate relative position
            rel_x = (objective['x'] - self.center_x) * map_scale
            rel_y = (objective['y'] - self.center_y) * map_scale
            
            # Convert to minimap coordinates
            map_x = center_x + rel_x
            map_y = center_y + rel_y
            
            # Check if within minimap bounds
            if 0 <= map_x < rect.width and 0 <= map_y < rect.height:
                dist = math.sqrt((map_x - center_x) ** 2 + (map_y - center_y) ** 2)
                if dist < rect.width // 2 - 5:
                    # Pulsing objective marker
                    pulse_size = 4 + 2 * math.sin(self.pulse_timer * 2)
                    pygame.draw.circle(surface, self.objective_color, 
                                     (int(map_x), int(map_y)), int(pulse_size))
                    pygame.draw.circle(surface, config.COLORS['white'], 
                                     (int(map_x), int(map_y)), int(pulse_size), 2)
    
    def _draw_radar_scan(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw radar scan effect."""
        center_x = rect.width // 2
        center_y = rect.height // 2
        radius = rect.width // 2 - 2
        
        # Calculate scan line end point
        scan_end_x = center_x + math.cos(self.scan_angle) * radius
        scan_end_y = center_y + math.sin(self.scan_angle) * radius
        
        # Draw scan line
        pygame.draw.line(surface, config.COLORS['cyan'], 
                        (center_x, center_y), (scan_end_x, scan_end_y), 2)
        
        # Draw fade trail
        for i in range(1, 6):
            trail_angle = self.scan_angle - i * 0.1
            trail_alpha = int(100 * (1 - i / 5))
            if trail_alpha > 0:
                trail_end_x = center_x + math.cos(trail_angle) * radius
                trail_end_y = center_y + math.sin(trail_angle) * radius
                
                trail_color = (*config.COLORS['cyan'], trail_alpha)
                # Note: pygame doesn't support alpha on lines directly, so we use a surface
                trail_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.line(trail_surface, trail_color, 
                               (center_x, center_y), (trail_end_x, trail_end_y), 1)
                surface.blit(trail_surface, (0, 0))
    
    def _apply_circular_mask(self, surface: pygame.Surface, rect: pygame.Rect):
        """Apply circular mask to minimap."""
        # Create a mask surface
        mask_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))
        
        # Draw circle on mask
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), 
                         (rect.width // 2, rect.height // 2), 
                         rect.width // 2 - 2)
        
        # Apply mask using per-pixel alpha
        for x in range(rect.width):
            for y in range(rect.height):
                mask_pixel = mask_surface.get_at((x, y))
                if mask_pixel[3] == 0:  # Transparent pixel in mask
                    surface.set_at((x, y), (0, 0, 0, 0))


class WeaponDisplay(HUDElement):
    """Display current weapon and ammo information."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y, width, height, anchor="bottom_right")
        
        # Weapon data
        self.weapon_name = "Sword"
        self.weapon_icon = None
        self.ammo_current = 0
        self.ammo_max = 0
        self.has_ammo = False
        
        # Visual properties
        self.background_color = config.COLORS['dark_gray']
        self.border_color = config.COLORS['white']
        self.ammo_color = config.COLORS['yellow']
        self.weapon_color = config.COLORS['cyan']
        
        # Animation
        self.weapon_change_timer = 0.0
        self.reload_progress = 0.0
        self.is_reloading = False
    
    def set_weapon(self, weapon_name: str, ammo_current: int = 0, ammo_max: int = 0):
        """Set current weapon information."""
        if weapon_name != self.weapon_name:
            self.weapon_change_timer = 0.5
            self.add_effect("flash", 0.6)
        
        self.weapon_name = weapon_name
        self.ammo_current = ammo_current
        self.ammo_max = ammo_max
        self.has_ammo = ammo_max > 0
    
    def set_reload_progress(self, progress: float):
        """Set reload progress (0.0 to 1.0)."""
        self.reload_progress = progress
        self.is_reloading = progress > 0.0 and progress < 1.0
    
    def _update_animations(self, dt: float):
        """Update weapon display animations."""
        self.weapon_change_timer = max(0.0, self.weapon_change_timer - dt)
    
    def render(self, surface: pygame.Surface):
        """Render the weapon display."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Draw background
        bg_alpha = 180
        bg_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*self.background_color, bg_alpha))
        surface.blit(bg_surface, render_rect.topleft)
        
        pygame.draw.rect(surface, self.border_color, render_rect, 2)
        
        # Draw weapon name
        font = pygame.font.Font(None, 28)
        weapon_text = font.render(self.weapon_name, True, self.weapon_color)
        weapon_rect = weapon_text.get_rect()
        weapon_rect.centerx = render_rect.centerx
        weapon_rect.y = render_rect.y + 10
        
        # Weapon change effect
        if self.weapon_change_timer > 0:
            scale_factor = 1.0 + (self.weapon_change_timer / 0.5) * 0.3
            scaled_weapon = pygame.transform.scale(weapon_text, 
                                                 (int(weapon_text.get_width() * scale_factor),
                                                  int(weapon_text.get_height() * scale_factor)))
            weapon_rect = scaled_weapon.get_rect()
            weapon_rect.centerx = render_rect.centerx
            weapon_rect.y = render_rect.y + 10
            surface.blit(scaled_weapon, weapon_rect)
        else:
            surface.blit(weapon_text, weapon_rect)
        
        # Draw ammo if applicable
        if self.has_ammo:
            ammo_font = pygame.font.Font(None, 24)
            ammo_text = f"{self.ammo_current}/{self.ammo_max}"
            
            # Color based on ammo level
            ammo_ratio = self.ammo_current / self.ammo_max if self.ammo_max > 0 else 0
            if ammo_ratio < 0.25:
                ammo_color = config.COLORS['red']
            elif ammo_ratio < 0.5:
                ammo_color = config.COLORS['orange']
            else:
                ammo_color = self.ammo_color
            
            ammo_surface = ammo_font.render(ammo_text, True, ammo_color)
            ammo_rect = ammo_surface.get_rect()
            ammo_rect.centerx = render_rect.centerx
            ammo_rect.y = render_rect.y + 45
            surface.blit(ammo_surface, ammo_rect)
        
        # Draw reload progress
        if self.is_reloading:
            self._draw_reload_progress(surface, render_rect)
        
        # Draw weapon change flash
        if self.weapon_change_timer > 0:
            flash_alpha = int(150 * (self.weapon_change_timer / 0.5))
            flash_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
            flash_surface.fill((*config.COLORS['white'], flash_alpha))
            surface.blit(flash_surface, render_rect.topleft)
    
    def _draw_reload_progress(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw reload progress bar."""
        progress_height = 4
        progress_y = rect.bottom - 15
        progress_rect = pygame.Rect(rect.x + 10, progress_y, rect.width - 20, progress_height)
        
        # Background
        pygame.draw.rect(surface, config.COLORS['dark_gray'], progress_rect)
        
        # Progress fill
        fill_width = int(progress_rect.width * self.reload_progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, fill_width, progress_height)
            pygame.draw.rect(surface, config.COLORS['orange'], fill_rect)
        
        # Border
        pygame.draw.rect(surface, config.COLORS['white'], progress_rect, 1)
        
        # Reload text
        reload_font = pygame.font.Font(None, 20)
        reload_text = reload_font.render("RELOADING...", True, config.COLORS['orange'])
        reload_rect = reload_text.get_rect()
        reload_rect.centerx = rect.centerx
        reload_rect.y = progress_y - 20
        surface.blit(reload_text, reload_rect)


class NotificationSystem(HUDElement):
    """System for displaying temporary notifications."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y, width, height, anchor="top_right")
        
        # Notification queue
        self.notifications = []
        self.max_notifications = 5
        self.notification_height = 40
        self.notification_spacing = 5
        
        # Animation
        self.slide_speed = 200.0
    
    def add_notification(self, text: str, notification_type: str = "info", duration: float = 3.0):
        """Add a new notification."""
        notification = {
            'text': text,
            'type': notification_type,
            'duration': duration,
            'timer': 0.0,
            'y_offset': -self.notification_height,  # Start off-screen
            'target_y': len(self.notifications) * (self.notification_height + self.notification_spacing),
            'alpha': 0
        }
        
        self.notifications.append(notification)
        
        # Remove old notifications if queue is full
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
        
        # Update target positions
        self._update_notification_positions()
    
    def _update_notification_positions(self):
        """Update target positions for all notifications."""
        for i, notification in enumerate(self.notifications):
            notification['target_y'] = i * (self.notification_height + self.notification_spacing)
    
    def _update_animations(self, dt: float):
        """Update notification animations."""
        for notification in self.notifications[:]:
            notification['timer'] += dt
            
            # Animate slide in
            y_diff = notification['target_y'] - notification['y_offset']
            if abs(y_diff) > 1:
                notification['y_offset'] += y_diff * self.slide_speed * dt / 100
            else:
                notification['y_offset'] = notification['target_y']
            
            # Animate alpha
            if notification['timer'] < 0.3:
                # Fade in
                notification['alpha'] = min(255, notification['alpha'] + 850 * dt)
            elif notification['timer'] > notification['duration'] - 0.5:
                # Fade out
                notification['alpha'] = max(0, notification['alpha'] - 510 * dt)
            else:
                # Fully visible
                notification['alpha'] = 255
            
            # Remove expired notifications
            if notification['timer'] > notification['duration']:
                self.notifications.remove(notification)
                self._update_notification_positions()
    
    def render(self, surface: pygame.Surface):
        """Render all notifications."""
        if not self.visible or not self.notifications:
            return
        
        font = pygame.font.Font(None, 24)
        
        for notification in self.notifications:
            if notification['alpha'] <= 0:
                continue
            
            # Calculate position
            notif_y = self.y + notification['y_offset']
            notif_rect = pygame.Rect(self.x, notif_y, self.width, self.notification_height)
            
            # Skip if off-screen
            if notif_y < -self.notification_height or notif_y > surface.get_height():
                continue
            
            # Get colors based on type
            bg_color, border_color, text_color = self._get_notification_colors(notification['type'])
            
            # Create notification surface with alpha
            notif_surface = pygame.Surface((self.width, self.notification_height), pygame.SRCALPHA)
            
            # Draw background
            bg_surface = pygame.Surface((self.width, self.notification_height), pygame.SRCALPHA)
            bg_surface.fill((*bg_color, int(180 * notification['alpha'] / 255)))
            notif_surface.blit(bg_surface, (0, 0))
            
            # Draw border
            border_alpha = int(notification['alpha'])
            pygame.draw.rect(notif_surface, (*border_color, border_alpha), 
                           pygame.Rect(0, 0, self.width, self.notification_height), 2)
            
            # Draw text
            text_alpha = int(notification['alpha'])
            text_surface = font.render(notification['text'], True, (*text_color, text_alpha))
            text_rect = text_surface.get_rect()
            text_rect.center = (self.width // 2, self.notification_height // 2)
            notif_surface.blit(text_surface, text_rect)
            
            # Apply overall alpha
            notif_surface.set_alpha(notification['alpha'])
            surface.blit(notif_surface, notif_rect.topleft)
    
    def _get_notification_colors(self, notification_type: str) -> Tuple[Tuple[int, int, int], 
                                                                      Tuple[int, int, int], 
                                                                      Tuple[int, int, int]]:
        """Get colors for notification type."""
        if notification_type == "error":
            return config.COLORS['red'], config.COLORS['red'], config.COLORS['white']
        elif notification_type == "warning":
            return config.COLORS['orange'], config.COLORS['orange'], config.COLORS['white']
        elif notification_type == "success":
            return config.COLORS['green'], config.COLORS['green'], config.COLORS['white']
        else:  # info
            return config.COLORS['blue'], config.COLORS['cyan'], config.COLORS['white']


class HUDSystem:
    """
    Main HUD system that manages all HUD elements.
    """
    
    def __init__(self, input_manager: InputManager, audio_manager: AudioManager):
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        
        # HUD state
        self.state = HUDState.NORMAL
        self.elements: List[HUDElement] = []
        
        # Screen dimensions (updated dynamically)
        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT
        
        # Create HUD elements
        self._create_hud_elements()
        
        # Effects
        self.particle_system = ParticleSystem(max_particles=100)
        
        print("HUD system initialized")
    
    def _create_hud_elements(self):
        """Create all HUD elements."""
        # Health bar (top-left)
        self.health_bar = HealthBar(20, 20, 200, 25)
        self.elements.append(self.health_bar)
        
        # Stamina bar (below health)
        self.stamina_bar = StaminaBar(20, 55, 200, 20)
        self.elements.append(self.stamina_bar)
        
        # Minimap (top-right)
        self.minimap = Minimap(-150, 20, 120)
        self.elements.append(self.minimap)
        
        # Weapon display (bottom-right)
        self.weapon_display = WeaponDisplay(-180, -80, 160, 70)
        self.elements.append(self.weapon_display)
        
        # Notification system (top-right, below minimap)
        self.notification_system = NotificationSystem(-300, 150, 280, 200)
        self.elements.append(self.notification_system)
        
        # Sort by priority
        self.elements.sort(key=lambda x: x.priority)
    
    def update(self, dt: float, screen_width: int, screen_height: int):
        """Update all HUD elements."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Update all elements
        for element in self.elements:
            element.update(dt, screen_width, screen_height)
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render all HUD elements."""
        # Render particle effects first (behind HUD)
        self.particle_system.render(screen, camera_offset)
        
        # Render HUD elements in priority order
        for element in self.elements:
            element.render(screen)
        
        # Render state-specific overlays
        if self.state == HUDState.PAUSED:
            self._render_pause_overlay(screen)
        elif self.state == HUDState.COMBAT:
            self._render_combat_overlay(screen)
    
    def _render_pause_overlay(self, screen: pygame.Surface):
        """Render pause overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.Font(None, 72)
        pause_text = font.render("PAUSED", True, config.COLORS['white'])
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(pause_text, pause_rect)
    
    def _render_combat_overlay(self, screen: pygame.Surface):
        """Render combat state overlay."""
        # Combat border effect
        border_width = 5
        border_color = config.COLORS['red']
        
        # Top border
        pygame.draw.rect(screen, border_color, (0, 0, self.screen_width, border_width))
        # Bottom border
        pygame.draw.rect(screen, border_color, (0, self.screen_height - border_width, 
                                              self.screen_width, border_width))
        # Left border
        pygame.draw.rect(screen, border_color, (0, 0, border_width, self.screen_height))
        # Right border
        pygame.draw.rect(screen, border_color, (self.screen_width - border_width, 0, 
                                              border_width, self.screen_height))
    
    def set_state(self, state: HUDState):
        """Set HUD state."""
        if state != self.state:
            self.state = state
            
            # Trigger state-specific effects
            if state == HUDState.COMBAT:
                self.add_screen_effect("combat_enter")
            elif state == HUDState.NORMAL:
                self.add_screen_effect("combat_exit")
    
    def update_health(self, current: float, maximum: float):
        """Update health display."""
        self.health_bar.set_health(current, maximum)
    
    def update_stamina(self, current: float, maximum: float):
        """Update stamina display."""
        self.stamina_bar.set_stamina(current, maximum)
    
    def update_weapon(self, weapon_name: str, ammo_current: int = 0, ammo_max: int = 0):
        """Update weapon display."""
        self.weapon_display.set_weapon(weapon_name, ammo_current, ammo_max)
    
    def set_reload_progress(self, progress: float):
        """Set weapon reload progress."""
        self.weapon_display.set_reload_progress(progress)
    
    def update_minimap(self, player_pos: Tuple[float, float], entities: List[Dict],
                      objectives: List[Dict] = None):
        """Update minimap data."""
        self.minimap.update_map_data(player_pos, entities, objectives)
    
    def show_notification(self, text: str, notification_type: str = "info", duration: float = 3.0):
        """Show a notification."""
        self.notification_system.add_notification(text, notification_type, duration)
    
    def add_screen_effect(self, effect_type: str):
        """Add screen-wide effect."""
        if effect_type == "damage":
            # Add damage particles at screen edges
            for _ in range(5):
                import random
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                self.particle_system.emit_burst(x, y, PARTICLE_PRESETS['blood_splatter'])
        
        elif effect_type == "combat_enter":
            # Combat entry effect
            self.health_bar.add_effect("glow", 0.8)
            self.stamina_bar.add_effect("glow", 0.8)
            
        elif effect_type == "combat_exit":
            # Combat exit effect - calm down effects
            pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events for HUD interaction."""
        # For now, HUD elements don't handle direct input
        # This could be extended for interactive HUD elements
        return False