"""
Forest Survival - World Scene System
Complete world scenes with environments, levels, and interactive elements.
"""

import pygame
import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

import config
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.core.scene_manager import Scene, SceneManager


class BiomeType(Enum):
    """Types of biomes in the game world."""
    FOREST = "forest"
    MEADOW = "meadow"
    SWAMP = "swamp"
    MOUNTAIN = "mountain"
    CAVE = "cave"
    RIVER = "river"
    CLEARING = "clearing"


class WeatherType(Enum):
    """Weather conditions."""
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"
    FOG = "fog"
    SNOW = "snow"


class TimeOfDay(Enum):
    """Time periods."""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    NIGHT = "night"


@dataclass
class WorldTile:
    """Individual tile in the world grid."""
    x: int
    y: int
    biome: BiomeType
    elevation: float
    moisture: float
    temperature: float
    
    # Visual properties
    base_color: Tuple[int, int, int]
    overlay_color: Optional[Tuple[int, int, int]] = None
    
    # Gameplay properties
    walkable: bool = True
    resource_type: Optional[str] = None
    resource_amount: int = 0
    
    # Environmental effects
    wind_strength: float = 0.0
    light_level: float = 1.0


class EnvironmentalEffect:
    """Environmental effects like particles, weather, etc."""
    
    def __init__(self, effect_type: str, x: float, y: float):
        self.effect_type = effect_type
        self.x = x
        self.y = y
        self.age = 0.0
        self.lifetime = 5.0
        
        # Visual properties
        self.color = config.COLORS['white']
        self.size = 2.0
        self.alpha = 255
        
        # Physics
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.acceleration_x = 0.0
        self.acceleration_y = 0.0
        
        # Animation
        self.scale = 1.0
        self.rotation = 0.0
        self.pulse_frequency = 1.0
        
        self.is_alive = True
    
    def update(self, dt: float):
        """Update effect."""
        self.age += dt
        
        # Update physics
        self.velocity_x += self.acceleration_x * dt
        self.velocity_y += self.acceleration_y * dt
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update visual properties based on age
        life_progress = self.age / self.lifetime
        
        if self.effect_type == "falling_leaf":
            self._update_falling_leaf(dt, life_progress)
        elif self.effect_type == "rain_drop":
            self._update_rain_drop(dt, life_progress)
        elif self.effect_type == "snow_flake":
            self._update_snow_flake(dt, life_progress)
        elif self.effect_type == "wind_particle":
            self._update_wind_particle(dt, life_progress)
        elif self.effect_type == "firefly":
            self._update_firefly(dt, life_progress)
        
        # Check if effect should die
        if self.age >= self.lifetime:
            self.is_alive = False
    
    def _update_falling_leaf(self, dt: float, life_progress: float):
        """Update falling leaf effect."""
        # Gentle swaying motion
        self.velocity_x = math.sin(self.age * 2) * 20
        self.velocity_y = 50 + math.sin(self.age * 1.5) * 10
        
        # Rotation
        self.rotation += dt * 90
        
        # Fade out near end of life
        if life_progress > 0.8:
            fade_progress = (life_progress - 0.8) / 0.2
            self.alpha = int(255 * (1.0 - fade_progress))
        
        # Color changes
        autumn_colors = [
            config.COLORS.get('orange', (255, 165, 0)),
            config.COLORS.get('red', (255, 0, 0)),
            config.COLORS.get('yellow', (255, 255, 0)),
            config.COLORS.get('brown', (139, 69, 19))
        ]
        color_index = int(life_progress * len(autumn_colors))
        if color_index < len(autumn_colors):
            self.color = autumn_colors[color_index]
    
    def _update_rain_drop(self, dt: float, life_progress: float):
        """Update rain drop effect."""
        # Fast downward motion
        self.velocity_y = 300
        
        # Slight wind effect
        self.velocity_x = math.sin(self.age) * 20
        
        # Scale decreases over time
        self.scale = 1.0 - life_progress * 0.5
        
        self.color = config.COLORS.get('blue', (0, 100, 255))
    
    def _update_snow_flake(self, dt: float, life_progress: float):
        """Update snow flake effect."""
        # Gentle falling with wind
        self.velocity_y = 30 + math.sin(self.age * 3) * 10
        self.velocity_x = math.sin(self.age * 2) * 15
        
        # Rotation
        self.rotation += dt * 45
        
        # Pulsing scale
        self.scale = 1.0 + math.sin(self.age * self.pulse_frequency) * 0.3
        
        self.color = config.COLORS.get('white', (255, 255, 255))
    
    def _update_wind_particle(self, dt: float, life_progress: float):
        """Update wind particle effect."""
        # Fast horizontal motion
        self.velocity_x = 150
        self.velocity_y = math.sin(self.age * 4) * 30
        
        # Fade in and out
        if life_progress < 0.3:
            self.alpha = int(255 * (life_progress / 0.3))
        elif life_progress > 0.7:
            fade_progress = (life_progress - 0.7) / 0.3
            self.alpha = int(255 * (1.0 - fade_progress))
        
        self.color = config.COLORS.get('gray', (128, 128, 128))
    
    def _update_firefly(self, dt: float, life_progress: float):
        """Update firefly effect."""
        # Random movement
        self.velocity_x += random.uniform(-50, 50) * dt
        self.velocity_y += random.uniform(-50, 50) * dt
        
        # Limit velocity
        max_speed = 40
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > max_speed:
            self.velocity_x = (self.velocity_x / speed) * max_speed
            self.velocity_y = (self.velocity_y / speed) * max_speed
        
        # Pulsing light
        pulse = (math.sin(self.age * self.pulse_frequency * 6) + 1) / 2
        self.alpha = int(100 + pulse * 155)
        self.scale = 0.5 + pulse * 0.5
        
        self.color = config.COLORS.get('yellow', (255, 255, 0))
    
    def render(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Render the effect."""
        if not self.is_alive or self.alpha <= 0:
            return
        
        # Calculate screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Skip if off-screen
        if (screen_x < -50 or screen_x > config.SCREEN_WIDTH + 50 or
            screen_y < -50 or screen_y > config.SCREEN_HEIGHT + 50):
            return
        
        # Create effect surface
        effect_size = int(self.size * self.scale)
        if effect_size <= 0:
            return
        
        effect_surface = pygame.Surface((effect_size * 2, effect_size * 2), pygame.SRCALPHA)
        
        if self.effect_type in ["falling_leaf", "snow_flake"]:
            # Draw as rotated square/diamond
            points = []
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle + self.rotation)
                px = effect_size + math.cos(rad) * effect_size
                py = effect_size + math.sin(rad) * effect_size
                points.append((px, py))
            
            pygame.draw.polygon(effect_surface, (*self.color, self.alpha), points)
        
        else:
            # Draw as circle
            pygame.draw.circle(effect_surface, (*self.color, self.alpha),
                             (effect_size, effect_size), effect_size)
        
        # Apply alpha to entire surface
        effect_surface.set_alpha(self.alpha)
        
        # Blit to screen
        surface.blit(effect_surface, (screen_x - effect_size, screen_y - effect_size))


class WeatherSystem:
    """Manages weather effects and conditions."""
    
    def __init__(self):
        self.current_weather = WeatherType.CLEAR
        self.weather_intensity = 0.0
        self.weather_duration = 0.0
        self.weather_timer = 0.0
        
        # Weather change parameters
        self.weather_change_chance = 0.01  # Per second
        self.min_weather_duration = 30.0  # Seconds
        self.max_weather_duration = 180.0
        
        # Effects
        self.weather_effects: List[EnvironmentalEffect] = []
        self.max_weather_effects = 100
        
        # Weather impact on gameplay
        self.visibility_modifier = 1.0
        self.movement_modifier = 1.0
    
    def update(self, dt: float, world_bounds: Tuple[int, int, int, int]):
        """Update weather system."""
        self.weather_timer += dt
        
        # Check for weather changes
        if (self.weather_timer > self.weather_duration and 
            random.random() < self.weather_change_chance * dt):
            self._change_weather()
        
        # Update current weather effects
        self._update_weather_effects(dt, world_bounds)
        
        # Update gameplay modifiers
        self._update_weather_modifiers()
    
    def _change_weather(self):
        """Change to a new weather type."""
        weather_types = list(WeatherType)
        
        # Remove current weather to encourage change
        if self.current_weather in weather_types:
            weather_types.remove(self.current_weather)
        
        self.current_weather = random.choice(weather_types)
        self.weather_intensity = random.uniform(0.3, 1.0)
        self.weather_duration = random.uniform(self.min_weather_duration, self.max_weather_duration)
        self.weather_timer = 0.0
        
        print(f"Weather changed to {self.current_weather.value} (intensity: {self.weather_intensity:.2f})")
    
    def _update_weather_effects(self, dt: float, world_bounds: Tuple[int, int, int, int]):
        """Update weather particle effects."""
        # Remove dead effects
        self.weather_effects = [effect for effect in self.weather_effects if effect.is_alive]
        
        # Update existing effects
        for effect in self.weather_effects:
            effect.update(dt)
        
        # Spawn new effects based on weather
        if self.current_weather == WeatherType.RAIN:
            self._spawn_rain_effects(dt, world_bounds)
        elif self.current_weather == WeatherType.SNOW:
            self._spawn_snow_effects(dt, world_bounds)
        elif self.current_weather == WeatherType.STORM:
            self._spawn_storm_effects(dt, world_bounds)
    
    def _spawn_rain_effects(self, dt: float, world_bounds: Tuple[int, int, int, int]):
        """Spawn rain particle effects."""
        spawn_rate = self.weather_intensity * 30  # Particles per second
        spawn_count = int(spawn_rate * dt)
        
        for _ in range(spawn_count):
            if len(self.weather_effects) < self.max_weather_effects:
                x = random.uniform(world_bounds[0] - 100, world_bounds[2] + 100)
                y = world_bounds[1] - 50
                
                effect = EnvironmentalEffect("rain_drop", x, y)
                effect.lifetime = 3.0
                effect.size = random.uniform(1, 3)
                self.weather_effects.append(effect)
    
    def _spawn_snow_effects(self, dt: float, world_bounds: Tuple[int, int, int, int]):
        """Spawn snow particle effects."""
        spawn_rate = self.weather_intensity * 20
        spawn_count = int(spawn_rate * dt)
        
        for _ in range(spawn_count):
            if len(self.weather_effects) < self.max_weather_effects:
                x = random.uniform(world_bounds[0] - 100, world_bounds[2] + 100)
                y = world_bounds[1] - 50
                
                effect = EnvironmentalEffect("snow_flake", x, y)
                effect.lifetime = 8.0
                effect.size = random.uniform(2, 5)
                effect.pulse_frequency = random.uniform(0.5, 2.0)
                self.weather_effects.append(effect)
    
    def _spawn_storm_effects(self, dt: float, world_bounds: Tuple[int, int, int, int]):
        """Spawn storm effects (heavy rain + wind)."""
        # Heavy rain
        spawn_rate = self.weather_intensity * 50
        spawn_count = int(spawn_rate * dt)
        
        for _ in range(spawn_count):
            if len(self.weather_effects) < self.max_weather_effects:
                x = random.uniform(world_bounds[0] - 100, world_bounds[2] + 100)
                y = world_bounds[1] - 50
                
                effect = EnvironmentalEffect("rain_drop", x, y)
                effect.lifetime = 2.0
                effect.size = random.uniform(2, 4)
                # Add wind effect
                effect.acceleration_x = random.uniform(50, 100)
                self.weather_effects.append(effect)
        
        # Wind particles
        wind_spawn_rate = self.weather_intensity * 10
        wind_spawn_count = int(wind_spawn_rate * dt)
        
        for _ in range(wind_spawn_count):
            if len(self.weather_effects) < self.max_weather_effects:
                x = world_bounds[0] - 50
                y = random.uniform(world_bounds[1], world_bounds[3])
                
                effect = EnvironmentalEffect("wind_particle", x, y)
                effect.lifetime = 4.0
                effect.size = random.uniform(3, 6)
                self.weather_effects.append(effect)
    
    def _update_weather_modifiers(self):
        """Update gameplay modifiers based on weather."""
        if self.current_weather == WeatherType.CLEAR:
            self.visibility_modifier = 1.0
            self.movement_modifier = 1.0
        
        elif self.current_weather == WeatherType.RAIN:
            self.visibility_modifier = 0.8
            self.movement_modifier = 0.9
        
        elif self.current_weather == WeatherType.STORM:
            self.visibility_modifier = 0.6
            self.movement_modifier = 0.7
        
        elif self.current_weather == WeatherType.FOG:
            self.visibility_modifier = 0.4
            self.movement_modifier = 1.0
        
        elif self.current_weather == WeatherType.SNOW:
            self.visibility_modifier = 0.7
            self.movement_modifier = 0.8
    
    def render(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Render weather effects."""
        for effect in self.weather_effects:
            effect.render(surface, camera_x, camera_y)
        
        # Add weather overlay
        if self.current_weather == WeatherType.FOG:
            self._render_fog_overlay(surface)
        elif self.current_weather == WeatherType.STORM:
            self._render_storm_overlay(surface)
    
    def _render_fog_overlay(self, surface: pygame.Surface):
        """Render fog overlay."""
        fog_alpha = int(100 * self.weather_intensity)
        fog_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((200, 200, 200, fog_alpha))
        surface.blit(fog_surface, (0, 0))
    
    def _render_storm_overlay(self, surface: pygame.Surface):
        """Render storm overlay."""
        storm_alpha = int(80 * self.weather_intensity)
        storm_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        storm_surface.fill((50, 50, 80, storm_alpha))
        surface.blit(storm_surface, (0, 0))


class DayNightCycle:
    """Manages day/night cycle and lighting."""
    
    def __init__(self):
        self.time_of_day = TimeOfDay.MORNING
        self.day_progress = 0.25  # 0 = midnight, 0.5 = noon, 1 = midnight
        self.cycle_duration = 300.0  # 5 minutes for full day
        
        # Lighting
        self.ambient_light = 1.0
        self.light_color = config.COLORS['white']
        
        # Sky colors for different times
        self.sky_colors = {
            TimeOfDay.NIGHT: (20, 20, 40),
            TimeOfDay.DAWN: (100, 80, 120),
            TimeOfDay.MORNING: (135, 206, 235),
            TimeOfDay.NOON: (135, 206, 250),
            TimeOfDay.AFTERNOON: (255, 165, 0),
            TimeOfDay.DUSK: (255, 100, 100),
        }
    
    def update(self, dt: float):
        """Update day/night cycle."""
        # Advance time
        self.day_progress += dt / self.cycle_duration
        
        # Wrap around day
        if self.day_progress >= 1.0:
            self.day_progress = 0.0
        
        # Determine time of day
        if self.day_progress < 0.1:  # 0.0 - 0.1
            self.time_of_day = TimeOfDay.NIGHT
        elif self.day_progress < 0.2:  # 0.1 - 0.2
            self.time_of_day = TimeOfDay.DAWN
        elif self.day_progress < 0.4:  # 0.2 - 0.4
            self.time_of_day = TimeOfDay.MORNING
        elif self.day_progress < 0.6:  # 0.4 - 0.6
            self.time_of_day = TimeOfDay.NOON
        elif self.day_progress < 0.8:  # 0.6 - 0.8
            self.time_of_day = TimeOfDay.AFTERNOON
        elif self.day_progress < 0.9:  # 0.8 - 0.9
            self.time_of_day = TimeOfDay.DUSK
        else:  # 0.9 - 1.0
            self.time_of_day = TimeOfDay.NIGHT
        
        # Update lighting
        self._update_lighting()
    
    def _update_lighting(self):
        """Update ambient lighting based on time of day."""
        if self.time_of_day == TimeOfDay.NIGHT:
            self.ambient_light = 0.3
            self.light_color = (100, 100, 150)
        
        elif self.time_of_day == TimeOfDay.DAWN:
            # Gradual brightening
            dawn_progress = (self.day_progress - 0.1) / 0.1
            self.ambient_light = 0.3 + dawn_progress * 0.4
            self.light_color = self._blend_colors((100, 100, 150), (255, 200, 150), dawn_progress)
        
        elif self.time_of_day == TimeOfDay.MORNING:
            self.ambient_light = 0.9
            self.light_color = (255, 240, 200)
        
        elif self.time_of_day == TimeOfDay.NOON:
            self.ambient_light = 1.0
            self.light_color = (255, 255, 255)
        
        elif self.time_of_day == TimeOfDay.AFTERNOON:
            self.ambient_light = 0.9
            self.light_color = (255, 220, 180)
        
        elif self.time_of_day == TimeOfDay.DUSK:
            # Gradual darkening
            dusk_progress = (self.day_progress - 0.8) / 0.1
            self.ambient_light = 0.8 - dusk_progress * 0.3
            self.light_color = self._blend_colors((255, 180, 100), (150, 100, 100), dusk_progress)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)
    
    def get_sky_color(self) -> Tuple[int, int, int]:
        """Get current sky color."""
        base_color = self.sky_colors.get(self.time_of_day, self.sky_colors[TimeOfDay.NOON])
        
        # Apply ambient light modifier
        r = int(base_color[0] * self.ambient_light)
        g = int(base_color[1] * self.ambient_light)
        b = int(base_color[2] * self.ambient_light)
        
        return (r, g, b)
    
    def apply_lighting(self, surface: pygame.Surface):
        """Apply lighting overlay to surface."""
        if self.ambient_light >= 1.0:
            return  # No overlay needed for full daylight
        
        # Create lighting overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Calculate darkness
        darkness = int((1.0 - self.ambient_light) * 150)
        overlay.fill((0, 0, 0, darkness))
        
        # Apply colored lighting
        if self.light_color != (255, 255, 255):
            light_overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            light_alpha = int(50 * (1.0 - self.ambient_light))
            light_overlay.fill((*self.light_color, light_alpha))
            surface.blit(light_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Apply darkness
        surface.blit(overlay, (0, 0))


class WorldScene(Scene):
    """
    Complete world scene with environment, weather, and day/night cycle.
    """
    
    def __init__(self, name: str, scene_manager: SceneManager, input_manager: InputManager, audio_manager: AudioManager):
        super().__init__(name)
        self.scene_manager = scene_manager
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        
        # World properties
        self.world_width = 2000
        self.world_height = 1500
        self.tile_size = 32
        
        # World grid
        self.tiles: List[List[WorldTile]] = []
        self.grid_width = self.world_width // self.tile_size
        self.grid_height = self.world_height // self.tile_size
        
        # Environmental systems
        self.weather_system = WeatherSystem()
        self.day_night_cycle = DayNightCycle()
        
        # Ambient effects
        self.ambient_effects: List[EnvironmentalEffect] = []
        self.ambient_spawn_timer = 0.0
        self.ambient_spawn_interval = 2.0
        
        # Background elements
        self.background_elements: List[Dict] = []
        
        # World generation parameters
        self.noise_scale = 0.05
        self.elevation_threshold = 0.3
        self.moisture_threshold = 0.4
        
        print(f"World scene '{name}' initialized")
    
    def generate_world(self):
        """Generate the world terrain and features."""
        print("Generating world...")
        
        # Initialize tile grid
        self.tiles = []
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                tile = self._generate_tile(x, y)
                row.append(tile)
            self.tiles.append(row)
        
        # Post-process for smooth transitions
        self._smooth_world()
        
        # Generate background elements
        self._generate_background_elements()
        
        print("World generation complete")
    
    def _generate_tile(self, grid_x: int, grid_y: int) -> WorldTile:
        """Generate a single world tile."""
        # Use simple noise function (simplified Perlin noise)
        elevation = self._noise(grid_x * self.noise_scale, grid_y * self.noise_scale)
        moisture = self._noise(grid_x * self.noise_scale + 100, grid_y * self.noise_scale + 100)
        temperature = 1.0 - (grid_y / self.grid_height) * 0.5  # Cooler towards top
        
        # Determine biome based on elevation, moisture, and temperature
        biome = self._determine_biome(elevation, moisture, temperature)
        
        # Set tile properties
        tile = WorldTile(
            x=grid_x * self.tile_size,
            y=grid_y * self.tile_size,
            biome=biome,
            elevation=elevation,
            moisture=moisture,
            temperature=temperature,
            base_color=self._get_biome_color(biome),
            walkable=biome != BiomeType.RIVER
        )
        
        # Add resources based on biome
        self._add_tile_resources(tile)
        
        return tile
    
    def _noise(self, x: float, y: float) -> float:
        """Simple noise function (simplified)."""
        # Very basic pseudo-noise
        import math
        return (math.sin(x * 12.9898 + y * 78.233) * 43758.5453) % 1.0
    
    def _determine_biome(self, elevation: float, moisture: float, temperature: float) -> BiomeType:
        """Determine biome based on environmental factors."""
        if elevation > 0.7:
            return BiomeType.MOUNTAIN
        elif elevation < 0.2:
            return BiomeType.RIVER if moisture > 0.6 else BiomeType.SWAMP
        elif moisture > 0.6 and temperature > 0.5:
            return BiomeType.FOREST
        elif moisture < 0.3:
            return BiomeType.CLEARING
        else:
            return BiomeType.MEADOW
    
    def _get_biome_color(self, biome: BiomeType) -> Tuple[int, int, int]:
        """Get base color for biome."""
        biome_colors = {
            BiomeType.FOREST: (34, 139, 34),      # Forest green
            BiomeType.MEADOW: (144, 238, 144),     # Light green
            BiomeType.SWAMP: (85, 107, 47),       # Dark olive green
            BiomeType.MOUNTAIN: (139, 137, 137),   # Gray
            BiomeType.CAVE: (64, 64, 64),         # Dark gray
            BiomeType.RIVER: (65, 105, 225),      # Royal blue
            BiomeType.CLEARING: (255, 255, 224)   # Light yellow
        }
        return biome_colors.get(biome, (128, 128, 128))
    
    def _add_tile_resources(self, tile: WorldTile):
        """Add resources to tile based on biome."""
        resource_chances = {
            BiomeType.FOREST: [("wood", 0.3), ("berries", 0.1)],
            BiomeType.MEADOW: [("flowers", 0.2), ("herbs", 0.15)],
            BiomeType.SWAMP: [("mushrooms", 0.25)],
            BiomeType.MOUNTAIN: [("stone", 0.4), ("ore", 0.1)],
            BiomeType.RIVER: [("fish", 0.2)],
            BiomeType.CLEARING: [("seeds", 0.1)]
        }
        
        if tile.biome in resource_chances:
            for resource_type, chance in resource_chances[tile.biome]:
                if random.random() < chance:
                    tile.resource_type = resource_type
                    tile.resource_amount = random.randint(1, 5)
                    break
    
    def _smooth_world(self):
        """Apply smoothing to world generation."""
        # Simple smoothing pass
        for y in range(1, self.grid_height - 1):
            for x in range(1, self.grid_width - 1):
                tile = self.tiles[y][x]
                
                # Average elevation with neighbors
                neighbor_elevation = 0
                neighbor_count = 0
                
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        neighbor_elevation += self.tiles[y + dy][x + dx].elevation
                        neighbor_count += 1
                
                # Slightly blend with neighbors
                avg_elevation = neighbor_elevation / neighbor_count
                tile.elevation = tile.elevation * 0.7 + avg_elevation * 0.3
    
    def _generate_background_elements(self):
        """Generate decorative background elements."""
        self.background_elements = []
        
        # Trees
        for _ in range(200):
            x = random.uniform(0, self.world_width)
            y = random.uniform(0, self.world_height)
            
            # Check biome at this location
            grid_x = int(x // self.tile_size)
            grid_y = int(y // self.tile_size)
            
            if (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
                tile = self.tiles[grid_y][grid_x]
                
                if tile.biome in [BiomeType.FOREST, BiomeType.MEADOW]:
                    tree_type = "pine" if tile.biome == BiomeType.FOREST else "oak"
                    self.background_elements.append({
                        'type': 'tree',
                        'subtype': tree_type,
                        'x': x,
                        'y': y,
                        'size': random.uniform(0.8, 1.5),
                        'color_variation': random.uniform(-20, 20)
                    })
        
        # Rocks
        for _ in range(100):
            x = random.uniform(0, self.world_width)
            y = random.uniform(0, self.world_height)
            
            grid_x = int(x // self.tile_size)
            grid_y = int(y // self.tile_size)
            
            if (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
                tile = self.tiles[grid_y][grid_x]
                
                if tile.biome in [BiomeType.MOUNTAIN, BiomeType.CLEARING]:
                    self.background_elements.append({
                        'type': 'rock',
                        'x': x,
                        'y': y,
                        'size': random.uniform(0.5, 1.2),
                        'color_variation': random.uniform(-30, 30)
                    })
    
    def update(self, dt: float):
        """Update world scene."""
        # Update environmental systems
        world_bounds = (0, 0, self.world_width, self.world_height)
        self.weather_system.update(dt, world_bounds)
        self.day_night_cycle.update(dt)
        
        # Update ambient effects
        self._update_ambient_effects(dt)
        
        # Spawn ambient effects
        self.ambient_spawn_timer += dt
        if self.ambient_spawn_timer >= self.ambient_spawn_interval:
            self._spawn_ambient_effects()
            self.ambient_spawn_timer = 0.0
    
    def _update_ambient_effects(self, dt: float):
        """Update ambient environmental effects."""
        # Remove dead effects
        self.ambient_effects = [effect for effect in self.ambient_effects if effect.is_alive]
        
        # Update existing effects
        for effect in self.ambient_effects:
            effect.update(dt)
    
    def _spawn_ambient_effects(self):
        """Spawn ambient effects like fireflies, floating particles."""
        if self.day_night_cycle.time_of_day in [TimeOfDay.DUSK, TimeOfDay.NIGHT]:
            # Spawn fireflies in forest areas
            if len(self.ambient_effects) < 50:
                for _ in range(random.randint(1, 3)):
                    x = random.uniform(0, self.world_width)
                    y = random.uniform(0, self.world_height)
                    
                    grid_x = int(x // self.tile_size)
                    grid_y = int(y // self.tile_size)
                    
                    if (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
                        tile = self.tiles[grid_y][grid_x]
                        
                        if tile.biome == BiomeType.FOREST:
                            firefly = EnvironmentalEffect("firefly", x, y)
                            firefly.lifetime = random.uniform(20, 40)
                            firefly.pulse_frequency = random.uniform(0.5, 2.0)
                            self.ambient_effects.append(firefly)
        
        # Falling leaves in autumn-like conditions
        if (self.day_night_cycle.time_of_day in [TimeOfDay.AFTERNOON, TimeOfDay.DUSK] and
            random.random() < 0.3):
            
            if len(self.ambient_effects) < 30:
                for _ in range(random.randint(1, 2)):
                    x = random.uniform(0, self.world_width)
                    y = -50
                    
                    leaf = EnvironmentalEffect("falling_leaf", x, y)
                    leaf.lifetime = random.uniform(8, 15)
                    self.ambient_effects.append(leaf)
    
    def render(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Render the world scene."""
        # Clear with sky color
        sky_color = self.day_night_cycle.get_sky_color()
        surface.fill(sky_color)
        
        # Calculate visible tile range
        start_x = max(0, int(camera_x // self.tile_size) - 1)
        end_x = min(self.grid_width, int((camera_x + config.SCREEN_WIDTH) // self.tile_size) + 2)
        start_y = max(0, int(camera_y // self.tile_size) - 1)
        end_y = min(self.grid_height, int((camera_y + config.SCREEN_HEIGHT) // self.tile_size) + 2)
        
        # Render terrain tiles
        self._render_terrain(surface, camera_x, camera_y, start_x, end_x, start_y, end_y)
        
        # Render background elements
        self._render_background_elements(surface, camera_x, camera_y)
        
        # Render ambient effects
        for effect in self.ambient_effects:
            effect.render(surface, camera_x, camera_y)
        
        # Render weather effects
        self.weather_system.render(surface, camera_x, camera_y)
        
        # Apply lighting
        self.day_night_cycle.apply_lighting(surface)
    
    def _render_terrain(self, surface: pygame.Surface, camera_x: float, camera_y: float,
                       start_x: int, end_x: int, start_y: int, end_y: int):
        """Render terrain tiles."""
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                
                # Calculate screen position
                screen_x = tile.x - camera_x
                screen_y = tile.y - camera_y
                
                # Skip if completely off-screen
                if (screen_x + self.tile_size < 0 or screen_x > config.SCREEN_WIDTH or
                    screen_y + self.tile_size < 0 or screen_y > config.SCREEN_HEIGHT):
                    continue
                
                # Apply lighting to tile color
                lit_color = self._apply_lighting_to_color(tile.base_color)
                
                # Draw tile
                tile_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                pygame.draw.rect(surface, lit_color, tile_rect)
                
                # Draw resource indicators
                if tile.resource_type:
                    self._render_resource_indicator(surface, tile, screen_x, screen_y)
    
    def _render_background_elements(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """Render background decorative elements."""
        for element in self.background_elements:
            screen_x = element['x'] - camera_x
            screen_y = element['y'] - camera_y
            
            # Skip if off-screen
            if (screen_x < -100 or screen_x > config.SCREEN_WIDTH + 100 or
                screen_y < -100 or screen_y > config.SCREEN_HEIGHT + 100):
                continue
            
            if element['type'] == 'tree':
                self._render_tree(surface, element, screen_x, screen_y)
            elif element['type'] == 'rock':
                self._render_rock(surface, element, screen_x, screen_y)
    
    def _render_tree(self, surface: pygame.Surface, tree: Dict, screen_x: float, screen_y: float):
        """Render a tree."""
        size = int(20 * tree['size'])
        
        # Tree trunk
        trunk_color = self._apply_lighting_to_color((101, 67, 33))
        trunk_rect = pygame.Rect(screen_x - 3, screen_y - size//4, 6, size//2)
        pygame.draw.rect(surface, trunk_color, trunk_rect)
        
        # Tree canopy
        if tree['subtype'] == 'pine':
            # Pine tree (triangle)
            canopy_color = self._apply_lighting_to_color((34, 139, 34))
            points = [
                (screen_x, screen_y - size),
                (screen_x - size//2, screen_y),
                (screen_x + size//2, screen_y)
            ]
            pygame.draw.polygon(surface, canopy_color, points)
        else:
            # Oak tree (circle)
            canopy_color = self._apply_lighting_to_color((34, 139, 34))
            pygame.draw.circle(surface, canopy_color, (int(screen_x), int(screen_y - size//3)), size//2)
    
    def _render_rock(self, surface: pygame.Surface, rock: Dict, screen_x: float, screen_y: float):
        """Render a rock."""
        size = int(15 * rock['size'])
        rock_color = self._apply_lighting_to_color((128, 128, 128))
        
        # Draw irregular rock shape
        points = [
            (screen_x - size//2, screen_y),
            (screen_x - size//3, screen_y - size//2),
            (screen_x + size//3, screen_y - size//3),
            (screen_x + size//2, screen_y + size//4),
            (screen_x, screen_y + size//2)
        ]
        pygame.draw.polygon(surface, rock_color, points)
    
    def _render_resource_indicator(self, surface: pygame.Surface, tile: WorldTile, 
                                 screen_x: float, screen_y: float):
        """Render resource indicator on tile."""
        indicator_size = 4
        indicator_x = screen_x + self.tile_size // 2
        indicator_y = screen_y + self.tile_size // 2
        
        # Color based on resource type
        resource_colors = {
            'wood': (139, 69, 19),      # Brown
            'stone': (128, 128, 128),   # Gray
            'berries': (255, 0, 0),     # Red
            'herbs': (0, 255, 0),       # Green
            'mushrooms': (128, 0, 128), # Purple
            'ore': (255, 215, 0),       # Gold
            'fish': (0, 0, 255),        # Blue
            'flowers': (255, 192, 203), # Pink
            'seeds': (139, 69, 19)      # Brown
        }
        
        color = resource_colors.get(tile.resource_type, (255, 255, 255))
        lit_color = self._apply_lighting_to_color(color)
        
        # Draw small indicator
        pygame.draw.circle(surface, lit_color, (int(indicator_x), int(indicator_y)), indicator_size)
    
    def _apply_lighting_to_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply day/night lighting to a color."""
        light_level = self.day_night_cycle.ambient_light
        light_color = self.day_night_cycle.light_color
        
        # Apply ambient light level
        r = int(color[0] * light_level)
        g = int(color[1] * light_level)
        b = int(color[2] * light_level)
        
        # Apply light color tint
        if light_color != (255, 255, 255):
            tint_strength = 0.3 * (1.0 - light_level)
            r = int(r + (light_color[0] - 255) * tint_strength)
            g = int(g + (light_color[1] - 255) * tint_strength)
            b = int(b + (light_color[2] - 255) * tint_strength)
        
        # Clamp values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return (r, g, b)
    
    def get_tile_at(self, world_x: float, world_y: float) -> Optional[WorldTile]:
        """Get tile at world coordinates."""
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.tiles[grid_y][grid_x]
        return None
    
    def is_walkable(self, world_x: float, world_y: float) -> bool:
        """Check if position is walkable."""
        tile = self.get_tile_at(world_x, world_y)
        return tile.walkable if tile else False
    
    def get_weather_modifiers(self) -> Tuple[float, float]:
        """Get current weather modifiers for visibility and movement."""
        return self.weather_system.visibility_modifier, self.weather_system.movement_modifier
    
    def cleanup(self):
        """Clean up world scene resources."""
        self.tiles.clear()
        self.background_elements.clear()
        self.ambient_effects.clear()
        self.weather_system.weather_effects.clear()
        
        print(f"World scene '{self.name}' cleaned up")