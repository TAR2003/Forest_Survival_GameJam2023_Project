"""
Forest Survival - Visual Effects System
Advanced visual effects including particles, screen effects, and animations.
"""

import pygame
import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

import config


class EffectType(Enum):
    """Types of visual effects."""
    EXPLOSION = "explosion"
    FIRE = "fire"
    SMOKE = "smoke"
    SPARKS = "sparks"
    MAGIC = "magic"
    BLOOD = "blood"
    DUST = "dust"
    LEAVES = "leaves"
    WATER_SPLASH = "water_splash"
    HEAL = "heal"
    DAMAGE_NUMBER = "damage_number"
    SCREEN_SHAKE = "screen_shake"
    FLASH = "flash"
    TRAIL = "trail"
    AURA = "aura"


class BlendMode(Enum):
    """Particle blend modes."""
    NORMAL = pygame.BLEND_ALPHA_SDL2
    ADD = pygame.BLEND_ADD
    MULTIPLY = pygame.BLEND_MULT
    SUBTRACT = pygame.BLEND_SUB


@dataclass
class ParticleDefinition:
    """Definition for particle system behavior."""
    # Emission
    emission_rate: float = 50.0  # Particles per second
    emission_duration: float = 1.0  # How long to emit
    max_particles: int = 100
    
    # Lifetime
    lifetime_min: float = 1.0
    lifetime_max: float = 3.0
    
    # Position
    spawn_radius: float = 0.0
    spawn_shape: str = "circle"  # circle, rectangle, line
    
    # Velocity
    velocity_min: float = 50.0
    velocity_max: float = 100.0
    direction_min: float = 0.0  # Degrees
    direction_max: float = 360.0
    
    # Appearance
    size_start: float = 5.0
    size_end: float = 1.0
    color_start: Tuple[int, int, int] = (255, 255, 255)
    color_end: Tuple[int, int, int] = (128, 128, 128)
    alpha_start: int = 255
    alpha_end: int = 0
    
    # Physics
    gravity: float = 0.0
    drag: float = 0.95
    rotation_speed: float = 0.0
    
    # Visual
    blend_mode: BlendMode = BlendMode.NORMAL
    texture: Optional[str] = None


class Particle:
    """Individual particle in a particle system."""
    
    def __init__(self, x: float, y: float, definition: ParticleDefinition):
        # Position
        self.x = x
        self.y = y
        
        # Spawn offset
        if definition.spawn_radius > 0:
            if definition.spawn_shape == "circle":
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, definition.spawn_radius)
                self.x += math.cos(angle) * radius
                self.y += math.sin(angle) * radius
            elif definition.spawn_shape == "rectangle":
                self.x += random.uniform(-definition.spawn_radius, definition.spawn_radius)
                self.y += random.uniform(-definition.spawn_radius, definition.spawn_radius)
        
        # Velocity
        speed = random.uniform(definition.velocity_min, definition.velocity_max)
        direction = math.radians(random.uniform(definition.direction_min, definition.direction_max))
        self.velocity_x = math.cos(direction) * speed
        self.velocity_y = math.sin(direction) * speed
        
        # Lifetime
        self.lifetime = random.uniform(definition.lifetime_min, definition.lifetime_max)
        self.age = 0.0
        self.life_progress = 0.0
        
        # Appearance
        self.size = definition.size_start
        self.color = definition.color_start
        self.alpha = definition.alpha_start
        self.rotation = 0.0
        
        # Physics
        self.acceleration_x = 0.0
        self.acceleration_y = definition.gravity
        
        # Reference to definition for updates
        self.definition = definition
        
        self.is_alive = True
    
    def update(self, dt: float):
        """Update particle."""
        if not self.is_alive:
            return
        
        # Age particle
        self.age += dt
        self.life_progress = self.age / self.lifetime
        
        # Check if particle should die
        if self.life_progress >= 1.0:
            self.is_alive = False
            return
        
        # Update physics
        self.velocity_x += self.acceleration_x * dt
        self.velocity_y += self.acceleration_y * dt
        
        # Apply drag
        self.velocity_x *= self.definition.drag
        self.velocity_y *= self.definition.drag
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update rotation
        self.rotation += self.definition.rotation_speed * dt
        
        # Update appearance based on life progress
        self._update_appearance()
    
    def _update_appearance(self):
        """Update particle appearance based on life progress."""
        # Interpolate size
        self.size = self._lerp(self.definition.size_start, self.definition.size_end, self.life_progress)
        
        # Interpolate color
        start_color = self.definition.color_start
        end_color = self.definition.color_end
        
        r = int(self._lerp(start_color[0], end_color[0], self.life_progress))
        g = int(self._lerp(start_color[1], end_color[1], self.life_progress))
        b = int(self._lerp(start_color[2], end_color[2], self.life_progress))
        self.color = (r, g, b)
        
        # Interpolate alpha
        self.alpha = int(self._lerp(self.definition.alpha_start, self.definition.alpha_end, self.life_progress))
    
    def _lerp(self, start: float, end: float, progress: float) -> float:
        """Linear interpolation."""
        return start + (end - start) * progress
    
    def render(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Render the particle."""
        if not self.is_alive or self.alpha <= 0 or self.size <= 0:
            return
        
        # Calculate screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Skip if off-screen
        margin = int(self.size * 2)
        if (screen_x < -margin or screen_x > config.SCREEN_WIDTH + margin or
            screen_y < -margin or screen_y > config.SCREEN_HEIGHT + margin):
            return
        
        # Create particle surface
        particle_size = int(self.size * 2)
        if particle_size <= 0:
            return
        
        particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
        
        # Draw particle shape
        center = (particle_size // 2, particle_size // 2)
        radius = max(1, int(self.size))
        
        # Apply color and alpha
        color_with_alpha = (*self.color, self.alpha)
        
        # Draw circle (can be extended for other shapes)
        pygame.draw.circle(particle_surface, color_with_alpha, center, radius)
        
        # Apply rotation if needed
        if self.rotation != 0:
            particle_surface = pygame.transform.rotate(particle_surface, math.degrees(self.rotation))
        
        # Blit to surface with blend mode
        blit_rect = particle_surface.get_rect(center=(screen_x, screen_y))
        surface.blit(particle_surface, blit_rect, special_flags=self.definition.blend_mode.value)


class ParticleSystem:
    """Particle system for managing groups of particles."""
    
    def __init__(self, x: float, y: float, definition: ParticleDefinition):
        self.x = x
        self.y = y
        self.definition = definition
        
        # Particles
        self.particles: List[Particle] = []
        
        # Emission
        self.emission_timer = 0.0
        self.emission_accumulator = 0.0
        self.is_emitting = True
        self.emission_elapsed = 0.0
        
        # System lifetime
        self.age = 0.0
        self.is_alive = True
    
    def set_position(self, x: float, y: float):
        """Set system position."""
        self.x = x
        self.y = y
    
    def emit_burst(self, count: int):
        """Emit a burst of particles."""
        for _ in range(count):
            if len(self.particles) < self.definition.max_particles:
                particle = Particle(self.x, self.y, self.definition)
                self.particles.append(particle)
    
    def stop_emission(self):
        """Stop emitting new particles."""
        self.is_emitting = False
    
    def update(self, dt: float):
        """Update particle system."""
        self.age += dt
        
        # Update emission
        if self.is_emitting:
            self.emission_elapsed += dt
            
            # Check if emission duration has passed
            if self.emission_elapsed >= self.definition.emission_duration:
                self.is_emitting = False
            else:
                # Emit particles
                self.emission_accumulator += self.definition.emission_rate * dt
                
                while self.emission_accumulator >= 1.0 and len(self.particles) < self.definition.max_particles:
                    particle = Particle(self.x, self.y, self.definition)
                    self.particles.append(particle)
                    self.emission_accumulator -= 1.0
        
        # Update existing particles
        for particle in self.particles[:]:  # Copy list to avoid modification during iteration
            particle.update(dt)
            if not particle.is_alive:
                self.particles.remove(particle)
        
        # Check if system should die
        if not self.is_emitting and len(self.particles) == 0:
            self.is_alive = False
    
    def render(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Render all particles in the system."""
        for particle in self.particles:
            particle.render(surface, camera_x, camera_y)
    
    def get_particle_count(self) -> int:
        """Get current number of particles."""
        return len(self.particles)


class ScreenEffect:
    """Screen-wide visual effects."""
    
    def __init__(self, effect_type: EffectType, duration: float = 1.0):
        self.effect_type = effect_type
        self.duration = duration
        self.age = 0.0
        self.progress = 0.0
        self.is_alive = True
        
        # Effect properties
        self.intensity = 1.0
        self.color = config.COLORS['white']
        self.blend_mode = pygame.BLEND_ALPHA_SDL2
        
        # Animation
        self.easing_function = self._ease_out_cubic
    
    def _ease_out_cubic(self, t: float) -> float:
        """Cubic ease-out function."""
        return 1 - pow(1 - t, 3)
    
    def update(self, dt: float):
        """Update screen effect."""
        if not self.is_alive:
            return
        
        self.age += dt
        self.progress = min(1.0, self.age / self.duration)
        
        if self.progress >= 1.0:
            self.is_alive = False
        
        # Update effect-specific properties
        if self.effect_type == EffectType.FLASH:
            self._update_flash()
        elif self.effect_type == EffectType.SCREEN_SHAKE:
            self._update_screen_shake()
    
    def _update_flash(self):
        """Update flash effect."""
        # Flash intensity decreases over time
        self.intensity = 1.0 - self.easing_function(self.progress)
    
    def _update_screen_shake(self):
        """Update screen shake effect."""
        # Shake intensity decreases over time
        self.intensity = (1.0 - self.progress) * 10.0
    
    def render(self, surface: pygame.Surface) -> Tuple[float, float]:
        """Render screen effect. Returns camera offset for shake effects."""
        if not self.is_alive:
            return (0.0, 0.0)
        
        if self.effect_type == EffectType.FLASH:
            return self._render_flash(surface)
        elif self.effect_type == EffectType.SCREEN_SHAKE:
            return self._render_screen_shake(surface)
        
        return (0.0, 0.0)
    
    def _render_flash(self, surface: pygame.Surface) -> Tuple[float, float]:
        """Render flash effect."""
        if self.intensity > 0:
            alpha = int(255 * self.intensity)
            flash_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((*self.color, alpha))
            surface.blit(flash_surface, (0, 0))
        
        return (0.0, 0.0)
    
    def _render_screen_shake(self, surface: pygame.Surface) -> Tuple[float, float]:
        """Render screen shake effect."""
        if self.intensity > 0:
            offset_x = random.uniform(-self.intensity, self.intensity)
            offset_y = random.uniform(-self.intensity, self.intensity)
            return (offset_x, offset_y)
        
        return (0.0, 0.0)


class VisualEffectsManager:
    """
    Manages all visual effects in the game.
    """
    
    def __init__(self):
        # Active systems
        self.particle_systems: List[ParticleSystem] = []
        self.screen_effects: List[ScreenEffect] = []
        
        # Effect definitions
        self.effect_definitions = self._create_effect_definitions()
        
        # Performance
        self.max_particle_systems = 50
        self.max_total_particles = 1000
        
        # Camera shake accumulation
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0
        
        print("Visual effects manager initialized")
    
    def _create_effect_definitions(self) -> Dict[EffectType, ParticleDefinition]:
        """Create predefined particle effect definitions."""
        definitions = {}
        
        # Explosion effect
        definitions[EffectType.EXPLOSION] = ParticleDefinition(
            emission_rate=200.0,
            emission_duration=0.5,
            max_particles=50,
            lifetime_min=0.5,
            lifetime_max=2.0,
            spawn_radius=20.0,
            velocity_min=100.0,
            velocity_max=300.0,
            size_start=8.0,
            size_end=2.0,
            color_start=(255, 100, 0),
            color_end=(255, 0, 0),
            alpha_start=255,
            alpha_end=0,
            gravity=50.0,
            drag=0.95,
            blend_mode=BlendMode.ADD
        )
        
        # Fire effect
        definitions[EffectType.FIRE] = ParticleDefinition(
            emission_rate=80.0,
            emission_duration=2.0,
            max_particles=40,
            lifetime_min=0.8,
            lifetime_max=1.5,
            spawn_radius=15.0,
            velocity_min=20.0,
            velocity_max=60.0,
            direction_min=240.0,
            direction_max=300.0,
            size_start=6.0,
            size_end=12.0,
            color_start=(255, 80, 0),
            color_end=(255, 255, 0),
            alpha_start=200,
            alpha_end=0,
            gravity=-30.0,
            drag=0.98,
            blend_mode=BlendMode.ADD
        )
        
        # Smoke effect
        definitions[EffectType.SMOKE] = ParticleDefinition(
            emission_rate=30.0,
            emission_duration=3.0,
            max_particles=25,
            lifetime_min=2.0,
            lifetime_max=4.0,
            spawn_radius=10.0,
            velocity_min=10.0,
            velocity_max=30.0,
            direction_min=260.0,
            direction_max=280.0,
            size_start=4.0,
            size_end=16.0,
            color_start=(100, 100, 100),
            color_end=(200, 200, 200),
            alpha_start=150,
            alpha_end=0,
            gravity=-10.0,
            drag=0.99
        )
        
        # Sparks effect
        definitions[EffectType.SPARKS] = ParticleDefinition(
            emission_rate=150.0,
            emission_duration=0.3,
            max_particles=30,
            lifetime_min=0.3,
            lifetime_max=1.0,
            spawn_radius=5.0,
            velocity_min=80.0,
            velocity_max=200.0,
            size_start=3.0,
            size_end=1.0,
            color_start=(255, 255, 100),
            color_end=(255, 100, 0),
            alpha_start=255,
            alpha_end=0,
            gravity=150.0,
            drag=0.92,
            blend_mode=BlendMode.ADD
        )
        
        # Magic effect
        definitions[EffectType.MAGIC] = ParticleDefinition(
            emission_rate=60.0,
            emission_duration=1.5,
            max_particles=35,
            lifetime_min=1.0,
            lifetime_max=2.5,
            spawn_radius=25.0,
            velocity_min=30.0,
            velocity_max=80.0,
            size_start=5.0,
            size_end=8.0,
            color_start=(100, 100, 255),
            color_end=(255, 100, 255),
            alpha_start=200,
            alpha_end=0,
            gravity=-20.0,
            drag=0.97,
            rotation_speed=180.0,
            blend_mode=BlendMode.ADD
        )
        
        # Blood effect
        definitions[EffectType.BLOOD] = ParticleDefinition(
            emission_rate=100.0,
            emission_duration=0.2,
            max_particles=20,
            lifetime_min=0.5,
            lifetime_max=1.5,
            spawn_radius=5.0,
            velocity_min=50.0,
            velocity_max=150.0,
            size_start=4.0,
            size_end=2.0,
            color_start=(200, 0, 0),
            color_end=(100, 0, 0),
            alpha_start=255,
            alpha_end=0,
            gravity=200.0,
            drag=0.9
        )
        
        # Dust effect
        definitions[EffectType.DUST] = ParticleDefinition(
            emission_rate=40.0,
            emission_duration=1.0,
            max_particles=20,
            lifetime_min=1.0,
            lifetime_max=3.0,
            spawn_radius=20.0,
            velocity_min=10.0,
            velocity_max=40.0,
            size_start=2.0,
            size_end=6.0,
            color_start=(150, 120, 80),
            color_end=(100, 80, 60),
            alpha_start=100,
            alpha_end=0,
            gravity=10.0,
            drag=0.99
        )
        
        # Leaves effect
        definitions[EffectType.LEAVES] = ParticleDefinition(
            emission_rate=20.0,
            emission_duration=2.0,
            max_particles=15,
            lifetime_min=3.0,
            lifetime_max=6.0,
            spawn_radius=30.0,
            velocity_min=20.0,
            velocity_max=50.0,
            size_start=6.0,
            size_end=4.0,
            color_start=(100, 200, 50),
            color_end=(200, 100, 0),
            alpha_start=200,
            alpha_end=0,
            gravity=30.0,
            drag=0.98,
            rotation_speed=90.0
        )
        
        # Water splash effect
        definitions[EffectType.WATER_SPLASH] = ParticleDefinition(
            emission_rate=120.0,
            emission_duration=0.4,
            max_particles=30,
            lifetime_min=0.4,
            lifetime_max=1.2,
            spawn_radius=10.0,
            velocity_min=60.0,
            velocity_max=150.0,
            size_start=3.0,
            size_end=1.0,
            color_start=(100, 150, 255),
            color_end=(50, 100, 200),
            alpha_start=200,
            alpha_end=0,
            gravity=180.0,
            drag=0.94,
            blend_mode=BlendMode.ADD
        )
        
        # Heal effect
        definitions[EffectType.HEAL] = ParticleDefinition(
            emission_rate=50.0,
            emission_duration=1.0,
            max_particles=25,
            lifetime_min=1.5,
            lifetime_max=2.5,
            spawn_radius=20.0,
            velocity_min=20.0,
            velocity_max=60.0,
            direction_min=240.0,
            direction_max=300.0,
            size_start=4.0,
            size_end=8.0,
            color_start=(100, 255, 100),
            color_end=(255, 255, 200),
            alpha_start=180,
            alpha_end=0,
            gravity=-40.0,
            drag=0.97,
            blend_mode=BlendMode.ADD
        )
        
        return definitions
    
    def create_effect(self, effect_type: EffectType, x: float, y: float, 
                     custom_definition: ParticleDefinition = None) -> ParticleSystem:
        """Create a new particle effect."""
        # Check particle system limit
        if len(self.particle_systems) >= self.max_particle_systems:
            # Remove oldest system
            self.particle_systems.pop(0)
        
        # Use custom definition or default
        definition = custom_definition or self.effect_definitions.get(effect_type)
        if not definition:
            print(f"Warning: No definition found for effect type {effect_type}")
            return None
        
        # Create particle system
        system = ParticleSystem(x, y, definition)
        self.particle_systems.append(system)
        
        return system
    
    def create_screen_effect(self, effect_type: EffectType, duration: float = 1.0, 
                           intensity: float = 1.0, color: Tuple[int, int, int] = None):
        """Create a screen-wide effect."""
        effect = ScreenEffect(effect_type, duration)
        effect.intensity = intensity
        
        if color:
            effect.color = color
        
        self.screen_effects.append(effect)
        
        return effect
    
    def create_explosion(self, x: float, y: float, size: float = 1.0):
        """Create explosion effect with screen shake."""
        # Particle explosion
        definition = self.effect_definitions[EffectType.EXPLOSION]
        definition.spawn_radius *= size
        definition.velocity_max *= size
        definition.max_particles = int(definition.max_particles * size)
        
        self.create_effect(EffectType.EXPLOSION, x, y, definition)
        
        # Screen effects
        self.create_screen_effect(EffectType.SCREEN_SHAKE, 0.5, size * 5)
        self.create_screen_effect(EffectType.FLASH, 0.3, size * 0.8, (255, 150, 0))
    
    def create_damage_number(self, x: float, y: float, damage: int, color: Tuple[int, int, int] = None):
        """Create floating damage number effect."""
        # This would be implemented as a special text particle
        # For now, create a simple particle effect
        if not color:
            color = (255, 100, 100) if damage > 0 else (100, 255, 100)
        
        definition = ParticleDefinition(
            emission_rate=1.0,
            emission_duration=0.1,
            max_particles=1,
            lifetime_min=1.5,
            lifetime_max=1.5,
            velocity_min=30.0,
            velocity_max=30.0,
            direction_min=270.0,
            direction_max=270.0,
            size_start=8.0,
            size_end=4.0,
            color_start=color,
            color_end=color,
            alpha_start=255,
            alpha_end=0,
            gravity=-20.0
        )
        
        self.create_effect(EffectType.DAMAGE_NUMBER, x, y, definition)
    
    def update(self, dt: float):
        """Update all visual effects."""
        # Update particle systems
        for system in self.particle_systems[:]:
            system.update(dt)
            if not system.is_alive:
                self.particle_systems.remove(system)
        
        # Update screen effects
        for effect in self.screen_effects[:]:
            effect.update(dt)
            if not effect.is_alive:
                self.screen_effects.remove(effect)
        
        # Reset camera offsets
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0
        
        # Check total particle count for performance
        total_particles = sum(system.get_particle_count() for system in self.particle_systems)
        if total_particles > self.max_total_particles:
            # Remove some older systems
            systems_to_remove = len(self.particle_systems) // 4
            for _ in range(systems_to_remove):
                if self.particle_systems:
                    self.particle_systems.pop(0)
    
    def render(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> Tuple[float, float]:
        """Render all visual effects. Returns camera shake offset."""
        # Render particle systems
        for system in self.particle_systems:
            system.render(surface, camera_x, camera_y)
        
        # Render screen effects and accumulate camera shake
        total_shake_x = 0.0
        total_shake_y = 0.0
        
        for effect in self.screen_effects:
            shake_x, shake_y = effect.render(surface)
            total_shake_x += shake_x
            total_shake_y += shake_y
        
        return (total_shake_x, total_shake_y)
    
    def clear_all_effects(self):
        """Clear all active effects."""
        self.particle_systems.clear()
        self.screen_effects.clear()
    
    def get_effect_count(self) -> Tuple[int, int]:
        """Get count of particle systems and total particles."""
        total_particles = sum(system.get_particle_count() for system in self.particle_systems)
        return len(self.particle_systems), total_particles
    
    def set_quality_level(self, quality: str):
        """Set visual quality level."""
        if quality == "low":
            self.max_particle_systems = 20
            self.max_total_particles = 500
        elif quality == "medium":
            self.max_particle_systems = 35
            self.max_total_particles = 750
        elif quality == "high":
            self.max_particle_systems = 50
            self.max_total_particles = 1000
        elif quality == "ultra":
            self.max_particle_systems = 75
            self.max_total_particles = 1500