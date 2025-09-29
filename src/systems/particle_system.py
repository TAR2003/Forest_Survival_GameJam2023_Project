"""
Forest Survival - Particle System
Advanced particle effects for visual feedback and polish.
"""

import pygame
import math
import random
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

import config


class ParticleType(Enum):
    """Types of particles available."""
    DUST = "dust"
    SPARK = "spark"
    SMOKE = "smoke"
    BLOOD = "blood"
    MAGIC = "magic"
    EXPLOSION = "explosion"
    TRAIL = "trail"
    LEAF = "leaf"
    WATER = "water"
    FIRE = "fire"
    ELECTRIC = "electric"
    HEAL = "heal"


class BlendMode(Enum):
    """Particle blend modes."""
    NORMAL = pygame.BLEND_ALPHA_SDL2
    ADDITIVE = pygame.BLEND_ADD
    MULTIPLY = pygame.BLEND_MULT
    SUBTRACT = pygame.BLEND_SUB


@dataclass
class ParticleConfig:
    """Configuration for particle creation."""
    particle_type: ParticleType
    count: int = 10
    lifetime: float = 1.0
    speed_min: float = 50
    speed_max: float = 150
    size_min: float = 2
    size_max: float = 8
    color: Tuple[int, int, int] = (255, 255, 255)
    gravity: float = 0
    fade_out: bool = True
    blend_mode: BlendMode = BlendMode.NORMAL
    spread_angle: float = math.pi * 2  # Full circle
    direction: float = 0  # Base direction in radians


class Particle:
    """Individual particle class."""
    
    def __init__(self, x: float, y: float, config: ParticleConfig):
        """Initialize a particle."""
        self.x = x
        self.y = y
        
        # Calculate velocity based on config
        angle = config.direction + (random.random() - 0.5) * config.spread_angle
        speed = random.uniform(config.speed_min, config.speed_max)
        
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        
        # Properties
        self.size = random.uniform(config.size_min, config.size_max)
        self.initial_size = self.size
        self.lifetime = config.lifetime
        self.max_lifetime = config.lifetime
        self.gravity = config.gravity
        
        # Visual properties
        self.color = config.color
        self.alpha = 255
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-5, 5)
        
        # Type-specific properties
        self.particle_type = config.particle_type
        self.fade_out = config.fade_out
        self.blend_mode = config.blend_mode
        
        # Special effects
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.flicker = False
        self.trail_points: List[Tuple[float, float]] = []
        
        # Physics modifiers
        self.friction = 0.98
        self.bounce = 0.3
        self.wind_resistance = 1.0
        
        self._setup_type_specific_properties()
    
    def _setup_type_specific_properties(self):
        """Setup properties specific to particle type."""
        if self.particle_type == ParticleType.DUST:
            self.friction = 0.95
            self.gravity = 100
            self.wind_resistance = 0.8
            
        elif self.particle_type == ParticleType.SPARK:
            self.friction = 0.98
            self.gravity = 200
            self.flicker = True
            
        elif self.particle_type == ParticleType.SMOKE:
            self.friction = 0.99
            self.gravity = -50  # Rises upward
            self.wind_resistance = 0.7
            
        elif self.particle_type == ParticleType.BLOOD:
            self.friction = 0.90
            self.gravity = 400
            self.bounce = 0.1
            
        elif self.particle_type == ParticleType.MAGIC:
            self.friction = 1.0  # No friction
            self.gravity = 0
            
        elif self.particle_type == ParticleType.EXPLOSION:
            self.friction = 0.85
            self.gravity = 0
            
        elif self.particle_type == ParticleType.LEAF:
            self.friction = 0.99
            self.gravity = 80
            self.wind_resistance = 0.5
            self.rotation_speed = random.uniform(-2, 2)
            
        elif self.particle_type == ParticleType.WATER:
            self.friction = 0.98
            self.gravity = 300
            self.bounce = 0.2
            
        elif self.particle_type == ParticleType.FIRE:
            self.friction = 0.99
            self.gravity = -100  # Rises upward
            self.flicker = True
            
        elif self.particle_type == ParticleType.ELECTRIC:
            self.friction = 1.0
            self.gravity = 0
            self.flicker = True
            
        elif self.particle_type == ParticleType.HEAL:
            self.friction = 0.99
            self.gravity = -80  # Rises slowly
    
    def update(self, dt: float, wind_x: float = 0, wind_y: float = 0) -> bool:
        """
        Update particle. Returns False when particle should be removed.
        
        Args:
            dt: Delta time in seconds
            wind_x: Wind force in X direction
            wind_y: Wind force in Y direction
        """
        # Update lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        
        # Apply wind
        self.vel_x += wind_x * self.wind_resistance * dt
        self.vel_y += wind_y * self.wind_resistance * dt
        
        # Apply gravity
        self.vel_y += self.gravity * dt
        
        # Apply friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Update position
        new_x = self.x + self.vel_x * dt
        new_y = self.y + self.vel_y * dt
        
        # Store trail point for trail particles
        if self.particle_type == ParticleType.TRAIL:
            self.trail_points.append((self.x, self.y))
            if len(self.trail_points) > 10:
                self.trail_points.pop(0)
        
        self.x = new_x
        self.y = new_y
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Update visual properties
        self._update_visuals(dt)
        
        return True
    
    def _update_visuals(self, dt: float):
        """Update visual properties of the particle."""
        progress = 1.0 - (self.lifetime / self.max_lifetime)
        
        # Update alpha (fade out)
        if self.fade_out:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Type-specific visual updates
        if self.particle_type == ParticleType.MAGIC:
            # Pulsing magic particles
            self.pulse_phase += dt * 8
            pulse = (math.sin(self.pulse_phase) + 1) / 2
            self.alpha = int(150 + pulse * 105)
            
        elif self.particle_type == ParticleType.SPARK:
            # Flickering sparks
            if self.flicker and random.random() < 0.3:
                self.alpha = random.randint(100, 255)
                
        elif self.particle_type == ParticleType.FIRE:
            # Flickering fire with size change
            if self.flicker:
                flicker_factor = 0.8 + random.random() * 0.4
                self.size = self.initial_size * flicker_factor
                
        elif self.particle_type == ParticleType.ELECTRIC:
            # Rapid flickering electric particles
            if random.random() < 0.6:
                self.alpha = random.randint(150, 255)
                
        elif self.particle_type == ParticleType.EXPLOSION:
            # Growing explosion particles
            self.size = self.initial_size * (1 + progress * 2)
            
        elif self.particle_type == ParticleType.HEAL:
            # Gently pulsing heal particles
            self.pulse_phase += dt * 4
            pulse = (math.sin(self.pulse_phase) + 1) / 2
            self.size = self.initial_size * (0.8 + pulse * 0.4)
        
        # Ensure alpha doesn't go negative
        self.alpha = max(0, min(255, self.alpha))
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render the particle to the surface."""
        if self.alpha <= 0:
            return
        
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Skip if off-screen (with margin)
        if (screen_x < -50 or screen_x > surface.get_width() + 50 or
            screen_y < -50 or screen_y > surface.get_height() + 50):
            return
        
        # Create particle surface
        particle_surface = self._create_particle_surface()
        if not particle_surface:
            return
        
        # Apply alpha
        particle_surface.set_alpha(self.alpha)
        
        # Calculate render position (centered)
        render_x = screen_x - particle_surface.get_width() // 2
        render_y = screen_y - particle_surface.get_height() // 2
        
        # Render with blend mode
        surface.blit(particle_surface, (render_x, render_y), 
                    special_flags=self.blend_mode.value)
    
    def _create_particle_surface(self) -> Optional[pygame.Surface]:
        """Create the particle surface based on type."""
        size = max(1, int(self.size))
        
        if self.particle_type == ParticleType.TRAIL:
            return self._create_trail_surface()
        
        # Create basic particle surface
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        if self.particle_type == ParticleType.DUST:
            # Simple circle
            pygame.draw.circle(particle_surface, self.color, (size, size), size)
            
        elif self.particle_type == ParticleType.SPARK:
            # Star-like spark
            self._draw_star(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.SMOKE:
            # Soft circle with gradient
            self._draw_soft_circle(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.BLOOD:
            # Irregular blob
            self._draw_blob(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.MAGIC:
            # Glowing orb
            self._draw_glow_orb(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.EXPLOSION:
            # Expanding ring
            pygame.draw.circle(particle_surface, self.color, (size, size), size, 2)
            
        elif self.particle_type == ParticleType.LEAF:
            # Leaf shape
            self._draw_leaf(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.WATER:
            # Water droplet
            self._draw_droplet(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.FIRE:
            # Flame shape
            self._draw_flame(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.ELECTRIC:
            # Electric bolt
            self._draw_electric(particle_surface, size, size, size, self.color)
            
        elif self.particle_type == ParticleType.HEAL:
            # Plus sign
            self._draw_plus(particle_surface, size, size, size, self.color)
            
        else:
            # Default circle
            pygame.draw.circle(particle_surface, self.color, (size, size), size)
        
        return particle_surface
    
    def _create_trail_surface(self) -> Optional[pygame.Surface]:
        """Create trail surface connecting trail points."""
        if len(self.trail_points) < 2:
            return None
        
        # Calculate bounding box
        min_x = min(point[0] for point in self.trail_points)
        max_x = max(point[0] for point in self.trail_points)
        min_y = min(point[1] for point in self.trail_points)
        max_y = max(point[1] for point in self.trail_points)
        
        width = int(max_x - min_x + 20)
        height = int(max_y - min_y + 20)
        
        if width <= 0 or height <= 0:
            return None
        
        trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw trail lines
        adjusted_points = [(point[0] - min_x + 10, point[1] - min_y + 10) 
                          for point in self.trail_points]
        
        if len(adjusted_points) >= 2:
            pygame.draw.lines(trail_surface, self.color, False, adjusted_points, 
                            max(1, int(self.size)))
        
        return trail_surface
    
    def _draw_star(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw a star shape."""
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            if i % 2 == 0:
                radius = size
            else:
                radius = size // 2
            
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            points.append((x, y))
        
        pygame.draw.polygon(surface, color, points)
    
    def _draw_soft_circle(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw a soft circle with gradient effect."""
        for i in range(size, 0, -1):
            alpha = int(255 * (i / size))
            soft_color = (*color, alpha)
            pygame.draw.circle(surface, soft_color, (cx, cy), i)
    
    def _draw_blob(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw an irregular blob shape."""
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            radius = size * (0.7 + random.random() * 0.6)
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            points.append((x, y))
        
        pygame.draw.polygon(surface, color, points)
    
    def _draw_glow_orb(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw a glowing orb."""
        # Outer glow
        for i in range(size * 2, 0, -2):
            alpha = int(100 * (1 - i / (size * 2)))
            glow_color = (*color, alpha)
            pygame.draw.circle(surface, glow_color, (cx, cy), i)
    
    def _draw_leaf(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw a leaf shape."""
        # Simple oval rotated
        rect = pygame.Rect(cx - size//2, cy - size, size, size * 2)
        pygame.draw.ellipse(surface, color, rect)
    
    def _draw_droplet(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw a water droplet shape."""
        # Circle with a point at the top
        pygame.draw.circle(surface, color, (cx, cy + size//4), size//2)
        points = [(cx, cy - size), (cx - size//3, cy), (cx + size//3, cy)]
        pygame.draw.polygon(surface, color, points)
    
    def _draw_flame(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw a flame shape."""
        # Teardrop pointing upward
        points = [
            (cx, cy - size),
            (cx - size//2, cy),
            (cx - size//4, cy + size//2),
            (cx + size//4, cy + size//2),
            (cx + size//2, cy)
        ]
        pygame.draw.polygon(surface, color, points)
    
    def _draw_electric(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw an electric bolt."""
        # Zigzag pattern
        points = [
            (cx - size, cy - size),
            (cx, cy - size//2),
            (cx - size//2, cy),
            (cx + size//2, cy),
            (cx, cy + size//2),
            (cx + size, cy + size)
        ]
        pygame.draw.lines(surface, color, False, points, 2)
    
    def _draw_plus(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        """Draw a plus sign."""
        # Horizontal line
        pygame.draw.line(surface, color, (cx - size, cy), (cx + size, cy), 3)
        # Vertical line
        pygame.draw.line(surface, color, (cx, cy - size), (cx, cy + size), 3)


class ParticleEmitter:
    """Manages emission of particles."""
    
    def __init__(self, x: float, y: float, config: ParticleConfig, 
                 emission_rate: float = 10, duration: float = -1):
        """
        Initialize particle emitter.
        
        Args:
            x, y: Emitter position
            config: Particle configuration
            emission_rate: Particles per second
            duration: How long to emit (-1 for infinite)
        """
        self.x = x
        self.y = y
        self.config = config
        self.emission_rate = emission_rate
        self.duration = duration
        self.active = True
        
        self.emission_timer = 0.0
        self.duration_timer = duration
        
        # Movement
        self.vel_x = 0.0
        self.vel_y = 0.0
    
    def update(self, dt: float) -> List[Particle]:
        """Update emitter and return new particles."""
        new_particles = []
        
        if not self.active:
            return new_particles
        
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Update duration
        if self.duration > 0:
            self.duration_timer -= dt
            if self.duration_timer <= 0:
                self.active = False
                return new_particles
        
        # Emit particles
        self.emission_timer += dt
        particles_to_emit = int(self.emission_timer * self.emission_rate)
        self.emission_timer -= particles_to_emit / self.emission_rate
        
        for _ in range(particles_to_emit):
            particle = Particle(self.x, self.y, self.config)
            new_particles.append(particle)
        
        return new_particles


class ParticleSystem:
    """
    Main particle system managing all particles and emitters.
    """
    
    def __init__(self, max_particles: int = 1000):
        """Initialize the particle system."""
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.emitters: List[ParticleEmitter] = []
        
        # Environmental effects
        self.wind_x = 0.0
        self.wind_y = 0.0
        
        # Performance settings
        self.enabled = True
        self.quality_scale = 1.0  # 0.0 to 1.0
        
        print("Particle system initialized")
    
    def update(self, dt: float):
        """Update all particles and emitters."""
        if not self.enabled:
            return
        
        # Update emitters and collect new particles
        new_particles = []
        active_emitters = []
        
        for emitter in self.emitters:
            emitted = emitter.update(dt)
            new_particles.extend(emitted)
            
            if emitter.active:
                active_emitters.append(emitter)
        
        self.emitters = active_emitters
        
        # Add new particles (respecting max limit)
        particles_to_add = min(len(new_particles), 
                              self.max_particles - len(self.particles))
        self.particles.extend(new_particles[:particles_to_add])
        
        # Update existing particles
        active_particles = []
        for particle in self.particles:
            if particle.update(dt, self.wind_x, self.wind_y):
                active_particles.append(particle)
        
        self.particles = active_particles
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render all particles."""
        if not self.enabled:
            return
        
        # Apply quality scaling
        particles_to_render = self.particles
        if self.quality_scale < 1.0:
            count = int(len(self.particles) * self.quality_scale)
            particles_to_render = self.particles[:count]
        
        for particle in particles_to_render:
            particle.render(surface, camera_offset)
    
    def emit_burst(self, x: float, y: float, config: ParticleConfig):
        """Emit a burst of particles at a position."""
        for _ in range(config.count):
            particle = Particle(x, y, config)
            if len(self.particles) < self.max_particles:
                self.particles.append(particle)
    
    def create_emitter(self, x: float, y: float, config: ParticleConfig, 
                      emission_rate: float = 10, duration: float = -1) -> ParticleEmitter:
        """Create and add a new emitter."""
        emitter = ParticleEmitter(x, y, config, emission_rate, duration)
        self.emitters.append(emitter)
        return emitter
    
    def set_wind(self, wind_x: float, wind_y: float):
        """Set environmental wind forces."""
        self.wind_x = wind_x
        self.wind_y = wind_y
    
    def clear_particles(self):
        """Clear all particles and emitters."""
        self.particles.clear()
        self.emitters.clear()
    
    def get_particle_count(self) -> int:
        """Get current particle count."""
        return len(self.particles)
    
    def get_emitter_count(self) -> int:
        """Get current emitter count."""
        return len(self.emitters)
    
    def set_quality(self, quality: float):
        """Set particle quality scale (0.0 to 1.0)."""
        self.quality_scale = max(0.0, min(1.0, quality))
    
    def toggle_enabled(self):
        """Toggle particle system on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.clear_particles()


# Preset particle configurations
PARTICLE_PRESETS = {
    'player_jump': ParticleConfig(
        ParticleType.DUST,
        count=8,
        lifetime=0.8,
        speed_min=30,
        speed_max=80,
        size_min=3,
        size_max=6,
        color=config.COLORS['brown'],
        gravity=150,
        spread_angle=math.pi / 3,
        direction=-math.pi / 2  # Upward
    ),
    
    'player_landing': ParticleConfig(
        ParticleType.DUST,
        count=12,
        lifetime=1.0,
        speed_min=50,
        speed_max=120,
        size_min=2,
        size_max=8,
        color=config.COLORS['brown'],
        gravity=200,
        spread_angle=math.pi / 2,
        direction=0  # Horizontal
    ),
    
    'sword_hit': ParticleConfig(
        ParticleType.SPARK,
        count=15,
        lifetime=0.6,
        speed_min=80,
        speed_max=200,
        size_min=2,
        size_max=5,
        color=config.COLORS['yellow'],
        gravity=300,
        spread_angle=math.pi / 4
    ),
    
    'enemy_death': ParticleConfig(
        ParticleType.EXPLOSION,
        count=20,
        lifetime=1.5,
        speed_min=60,
        speed_max=180,
        size_min=4,
        size_max=12,
        color=config.COLORS['red'],
        gravity=100,
        spread_angle=math.pi * 2
    ),
    
    'magic_cast': ParticleConfig(
        ParticleType.MAGIC,
        count=25,
        lifetime=2.0,
        speed_min=20,
        speed_max=80,
        size_min=3,
        size_max=8,
        color=config.COLORS['cyan'],
        gravity=0,
        spread_angle=math.pi * 2
    ),
    
    'heal_effect': ParticleConfig(
        ParticleType.HEAL,
        count=15,
        lifetime=1.5,
        speed_min=10,
        speed_max=40,
        size_min=4,
        size_max=8,
        color=config.COLORS['green'],
        gravity=-60,
        spread_angle=math.pi / 6,
        direction=-math.pi / 2
    )
}