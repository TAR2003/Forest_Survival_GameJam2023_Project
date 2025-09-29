"""
Forest Survival - Player Controller
Enhanced player movement with feel-good mechanics and advanced controls.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional
from enum import Enum

import config
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager


class PlayerState(Enum):
    """Player animation and movement states."""
    STANDING = "standing"
    RUNNING_LEFT = "running_left"
    RUNNING_RIGHT = "running_right"
    JUMPING = "jumping"
    FALLING = "falling"
    DUCKING = "ducking"
    ATTACKING = "attacking"
    SHIELDING = "shielding"
    HURT = "hurt"
    DYING = "dying"


class MovementState(Enum):
    """Physics movement states."""
    GROUNDED = "grounded"
    AIRBORNE = "airborne"
    WALL_SLIDING = "wall_sliding"
    DASHING = "dashing"


class PlayerController:
    """
    Advanced player controller with feel-good movement mechanics.
    """
    
    def __init__(self, x: float, y: float, input_manager: InputManager, audio_manager: AudioManager):
        """Initialize the player controller."""
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        
        # Position and physics
        self.x = float(x)
        self.y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.last_x = self.x
        self.last_y = self.y
        
        # Movement parameters (tuned for feel-good movement)
        self.move_speed = config.PLAYER_SPEED
        self.jump_strength = config.PLAYER_JUMP_STRENGTH
        self.gravity = config.GRAVITY
        self.friction = 0.85  # Ground friction
        self.air_friction = 0.98  # Air resistance
        self.acceleration = 1200  # Pixels per second squared
        self.deceleration = 1500
        
        # Advanced movement features
        self.max_fall_speed = 800
        self.jump_cut_multiplier = 0.5  # Variable jump height
        self.coyote_time = 0.15  # Grace period after leaving ground
        self.jump_buffer_time = 0.1  # Input buffering for jumps
        self.wall_slide_speed = 150
        self.wall_jump_force = 500
        
        # Dash mechanics
        self.dash_speed = 800
        self.dash_duration = 0.2
        self.dash_cooldown = 1.0
        self.dash_distance = 160
        
        # State tracking
        self.state = PlayerState.STANDING
        self.movement_state = MovementState.GROUNDED
        self.facing_right = True
        self.on_ground = False
        self.on_wall = False
        self.wall_direction = 0  # -1 for left wall, 1 for right wall
        
        # Timing variables
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.state_timer = 0.0
        
        # Animation system
        self.animations = {}
        self.current_animation = None
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 8.0  # FPS for animations
        
        # Combat properties
        self.health = config.PLAYER_MAX_HEALTH
        self.max_health = config.PLAYER_MAX_HEALTH
        self.shield_active = False
        self.shield_energy = 100.0
        self.max_shield_energy = 100.0
        self.shield_regen_rate = 25.0  # per second
        self.shield_delay = 2.0  # delay before regen starts
        self.shield_delay_timer = 0.0
        
        # Combat state
        self.invulnerable = False
        self.invulnerability_timer = 0.0
        self.invulnerability_duration = 1.0
        
        # Hitbox and collision
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT
        self.hitbox_offset_x = 0
        self.hitbox_offset_y = 0
        
        # Visual effects
        self.sprite_offset_x = 0
        self.sprite_offset_y = 0
        self.screen_shake_trauma = 0.0
        
        # Input state
        self.input_left = False
        self.input_right = False
        self.input_jump = False
        self.input_jump_held = False
        self.input_duck = False
        self.input_dash = False
        self.input_attack = False
        self.input_shield = False
        
        # Movement feel improvements
        self.landing_particles = []
        self.dust_particles = []
        self.movement_sound_timer = 0.0
        
        self._load_animations()
        self._setup_collision_rect()
        
        print(f"Player initialized at ({x}, {y})")
    
    def _load_animations(self):
        """Load player animation frames."""
        try:
            # Load animation images
            self.animations = {
                PlayerState.STANDING: [pygame.image.load("pictures/player/playerstanding.png")],
                PlayerState.RUNNING_RIGHT: [
                    pygame.image.load("pictures/player/playerrunright.png"),
                    pygame.image.load("pictures/player/1.png"),
                    pygame.image.load("pictures/player/2.png"),
                    pygame.image.load("pictures/player/3.png"),
                    pygame.image.load("pictures/player/4.png")
                ],
                PlayerState.RUNNING_LEFT: [
                    pygame.image.load("pictures/player/playerrunleft.png")
                ],
                PlayerState.JUMPING: [pygame.image.load("pictures/player/playeronairright.png")],
                PlayerState.FALLING: [pygame.image.load("pictures/player/playeronairrleftt.png")],
                PlayerState.DUCKING: [pygame.image.load("pictures/player/playerduck.png")],
                PlayerState.SHIELDING: [pygame.image.load("pictures/player/SHIELD.png")]
            }
            
            # Convert images for better performance
            for state, frames in self.animations.items():
                for i, frame in enumerate(frames):
                    self.animations[state][i] = frame.convert_alpha()
            
            self.current_animation = self.animations[PlayerState.STANDING]
            
        except pygame.error as e:
            print(f"Error loading player animations: {e}")
            # Create placeholder animations
            placeholder = pygame.Surface((self.width, self.height))
            placeholder.fill(config.COLORS['green'])
            
            for state in PlayerState:
                self.animations[state] = [placeholder]
            
            self.current_animation = self.animations[PlayerState.STANDING]
    
    def _setup_collision_rect(self):
        """Setup collision rectangle."""
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, dt: float, level_bounds: pygame.Rect, collision_tiles: List[pygame.Rect]):
        """
        Update player controller.
        
        Args:
            dt: Delta time in seconds
            level_bounds: Level boundary rectangle
            collision_tiles: List of collision rectangles
        """
        # Update timers
        self._update_timers(dt)
        
        # Handle input
        self._handle_input()
        
        # Update physics based on movement state
        if self.movement_state == MovementState.DASHING:
            self._update_dash_movement(dt)
        else:
            self._update_normal_movement(dt)
        
        # Apply physics
        self._apply_physics(dt)
        
        # Handle collisions
        self._handle_collisions(collision_tiles, level_bounds)
        
        # Update animation state
        self._update_animation_state()
        
        # Update animation frames
        self._update_animation(dt)
        
        # Update shield
        self._update_shield(dt)
        
        # Update effects
        self._update_effects(dt)
        
        # Update collision rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _update_timers(self, dt: float):
        """Update all timers."""
        self.coyote_timer -= dt
        self.jump_buffer_timer -= dt
        self.dash_timer -= dt
        self.dash_cooldown_timer -= dt
        self.state_timer += dt
        self.invulnerability_timer -= dt
        self.shield_delay_timer -= dt
        self.movement_sound_timer -= dt
        
        if self.invulnerability_timer <= 0:
            self.invulnerable = False
    
    def _handle_input(self):
        """Process player input."""
        # Get input states
        self.input_left = self.input_manager.is_action_held('move_left')
        self.input_right = self.input_manager.is_action_held('move_right')
        self.input_duck = self.input_manager.is_action_held('duck')
        self.input_jump_held = self.input_manager.is_action_held('jump')
        self.input_shield = self.input_manager.is_action_held('shield')
        
        # Check for jump press (with buffering)
        if self.input_manager.is_action_pressed('jump'):
            self.jump_buffer_timer = self.jump_buffer_time
        
        # Check for dash press
        if self.input_manager.is_action_pressed('dash'):
            self.input_dash = True
        else:
            self.input_dash = False
        
        # Check for attack press
        if self.input_manager.is_action_pressed('attack'):
            self.input_attack = True
        else:
            self.input_attack = False
    
    def _update_normal_movement(self, dt: float):
        """Update normal movement physics."""
        # Horizontal movement
        target_vel_x = 0.0
        
        if self.input_left and not self.input_right:
            target_vel_x = -self.move_speed
            self.facing_right = False
        elif self.input_right and not self.input_left:
            target_vel_x = self.move_speed
            self.facing_right = True
        
        # Apply acceleration/deceleration
        if abs(target_vel_x) > 0:
            # Accelerating
            accel = self.acceleration if self.on_ground else self.acceleration * 0.6
            if self.vel_x < target_vel_x:
                self.vel_x = min(self.vel_x + accel * dt, target_vel_x)
            elif self.vel_x > target_vel_x:
                self.vel_x = max(self.vel_x - accel * dt, target_vel_x)
        else:
            # Decelerating
            decel = self.deceleration if self.on_ground else self.deceleration * 0.3
            if self.vel_x > 0:
                self.vel_x = max(0, self.vel_x - decel * dt)
            elif self.vel_x < 0:
                self.vel_x = min(0, self.vel_x + decel * dt)
        
        # Handle jumping
        self._handle_jumping()
        
        # Handle dashing
        self._handle_dash_input()
        
        # Handle ducking
        if self.input_duck and self.on_ground:
            self.vel_x *= 0.5  # Slow down when ducking
    
    def _handle_jumping(self):
        """Handle jump mechanics with coyote time and jump buffering."""
        can_jump = (self.on_ground or self.coyote_timer > 0 or 
                   (self.on_wall and self.movement_state != MovementState.GROUNDED))
        
        wants_to_jump = self.jump_buffer_timer > 0
        
        if wants_to_jump and can_jump:
            if self.on_wall and not self.on_ground:
                # Wall jump
                self.vel_y = -self.jump_strength * 0.9
                self.vel_x = self.wall_direction * self.wall_jump_force
                self.on_wall = False
                self.movement_state = MovementState.AIRBORNE
                self.audio_manager.play_sound('jump', self.x, self.y)
                self._create_jump_particles()
            else:
                # Normal jump
                self.vel_y = -self.jump_strength
                self.movement_state = MovementState.AIRBORNE
                self.audio_manager.play_sound('jump', self.x, self.y)
                self._create_jump_particles()
            
            self.jump_buffer_timer = 0
            self.coyote_timer = 0
        
        # Variable jump height (jump cut)
        if not self.input_jump_held and self.vel_y < 0:
            self.vel_y *= self.jump_cut_multiplier
    
    def _handle_dash_input(self):
        """Handle dash input and mechanics."""
        if (self.input_dash and self.dash_cooldown_timer <= 0 and 
            self.movement_state != MovementState.DASHING):
            
            # Determine dash direction
            dash_dir_x = 0
            if self.input_left:
                dash_dir_x = -1
            elif self.input_right:
                dash_dir_x = 1
            else:
                dash_dir_x = 1 if self.facing_right else -1
            
            # Start dash
            self.movement_state = MovementState.DASHING
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            
            # Set dash velocity
            self.vel_x = dash_dir_x * self.dash_speed
            self.vel_y = 0  # Horizontal dash only
            
            self.audio_manager.play_sound('slide', self.x, self.y)
            self._create_dash_particles()
            
            # Brief invulnerability during dash
            self.invulnerable = True
            self.invulnerability_timer = self.dash_duration
    
    def _update_dash_movement(self, dt: float):
        """Update movement during dash."""
        if self.dash_timer <= 0:
            self.movement_state = MovementState.AIRBORNE if not self.on_ground else MovementState.GROUNDED
            self.vel_x *= 0.3  # Reduce velocity after dash
    
    def _apply_physics(self, dt: float):
        """Apply physics calculations."""
        # Apply gravity
        if self.movement_state != MovementState.DASHING:
            if self.on_wall and self.vel_y > 0:
                # Wall sliding
                self.vel_y = min(self.vel_y + self.gravity * dt * 0.3, self.wall_slide_speed)
                self.movement_state = MovementState.WALL_SLIDING
            else:
                # Normal gravity
                self.vel_y += self.gravity * dt
                self.vel_y = min(self.vel_y, self.max_fall_speed)
        
        # Store previous position
        self.last_x = self.x
        self.last_y = self.y
        
        # Apply velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
    
    def _handle_collisions(self, collision_tiles: List[pygame.Rect], level_bounds: pygame.Rect):
        """Handle collision detection and response."""
        # Update collision rect
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Check ground collision
        was_on_ground = self.on_ground
        self.on_ground = False
        self.on_wall = False
        
        # Collision with tiles
        for tile in collision_tiles:
            if player_rect.colliderect(tile):
                self._resolve_tile_collision(player_rect, tile)
        
        # Level bounds collision
        if player_rect.left < level_bounds.left:
            self.x = level_bounds.left
            self.vel_x = max(0, self.vel_x)
        elif player_rect.right > level_bounds.right:
            self.x = level_bounds.right - self.width
            self.vel_x = min(0, self.vel_x)
        
        if player_rect.top < level_bounds.top:
            self.y = level_bounds.top
            self.vel_y = max(0, self.vel_y)
        elif player_rect.bottom > level_bounds.bottom:
            self.y = level_bounds.bottom - self.height
            self.vel_y = 0
            self.on_ground = True
        
        # Update movement state
        if self.on_ground and not was_on_ground:
            self.movement_state = MovementState.GROUNDED
            self.coyote_timer = self.coyote_time
            self._create_landing_particles()
            if abs(self.vel_y) > 300:  # Hard landing
                self.audio_manager.play_sound('fall', self.x, self.y)
        elif not self.on_ground and was_on_ground:
            self.coyote_timer = self.coyote_time
            if self.movement_state != MovementState.DASHING:
                self.movement_state = MovementState.AIRBORNE
    
    def _resolve_tile_collision(self, player_rect: pygame.Rect, tile: pygame.Rect):
        """Resolve collision with a single tile."""
        # Calculate overlap
        overlap_x = min(player_rect.right - tile.left, tile.right - player_rect.left)
        overlap_y = min(player_rect.bottom - tile.top, tile.bottom - player_rect.top)
        
        # Resolve based on smallest overlap
        if overlap_x < overlap_y:
            # Horizontal collision
            if player_rect.centerx < tile.centerx:
                # Hit from left
                self.x = tile.left - self.width
                if self.vel_x > 0:
                    self.vel_x = 0
                    self.on_wall = True
                    self.wall_direction = 1
            else:
                # Hit from right
                self.x = tile.right
                if self.vel_x < 0:
                    self.vel_x = 0
                    self.on_wall = True
                    self.wall_direction = -1
        else:
            # Vertical collision
            if player_rect.centery < tile.centery:
                # Hit from above (landing)
                self.y = tile.top - self.height
                if self.vel_y > 0:
                    self.vel_y = 0
                    self.on_ground = True
            else:
                # Hit from below (ceiling)
                self.y = tile.bottom
                if self.vel_y < 0:
                    self.vel_y = 0
    
    def _update_animation_state(self):
        """Update animation state based on player state."""
        new_state = None
        
        if self.state == PlayerState.HURT or self.state == PlayerState.DYING:
            return  # Don't change state during hurt/death
        
        # Determine new state
        if self.input_shield and self.shield_energy > 10:
            new_state = PlayerState.SHIELDING
        elif self.input_duck and self.on_ground:
            new_state = PlayerState.DUCKING
        elif not self.on_ground:
            if self.vel_y < 0:
                new_state = PlayerState.JUMPING
            else:
                new_state = PlayerState.FALLING
        elif abs(self.vel_x) > 50:  # Moving threshold
            if self.facing_right:
                new_state = PlayerState.RUNNING_RIGHT
            else:
                new_state = PlayerState.RUNNING_LEFT
        else:
            new_state = PlayerState.STANDING
        
        # Update state if changed
        if new_state != self.state:
            self.state = new_state
            self.state_timer = 0.0
            self.animation_frame = 0
            self.animation_timer = 0.0
            self.current_animation = self.animations[self.state]
    
    def _update_animation(self, dt: float):
        """Update animation frames."""
        if not self.current_animation:
            return
        
        self.animation_timer += dt
        
        if self.animation_timer >= 1.0 / self.animation_speed:
            self.animation_timer = 0.0
            self.animation_frame = (self.animation_frame + 1) % len(self.current_animation)
    
    def _update_shield(self, dt: float):
        """Update shield mechanics."""
        if self.input_shield and self.shield_energy > 0:
            self.shield_active = True
            self.shield_energy -= 30 * dt  # Drain while active
            self.shield_energy = max(0, self.shield_energy)
        else:
            self.shield_active = False
            
            # Regenerate shield after delay
            if self.shield_delay_timer <= 0:
                self.shield_energy += self.shield_regen_rate * dt
                self.shield_energy = min(self.max_shield_energy, self.shield_energy)
    
    def _update_effects(self, dt: float):
        """Update visual effects."""
        # Update particles
        self.landing_particles = [p for p in self.landing_particles if p.update(dt)]
        self.dust_particles = [p for p in self.dust_particles if p.update(dt)]
        
        # Screen shake decay
        self.screen_shake_trauma = max(0, self.screen_shake_trauma - dt * 2)
        
        # Movement sounds
        if (abs(self.vel_x) > 100 and self.on_ground and 
            self.movement_sound_timer <= 0):
            self.audio_manager.play_sound('move', self.x, self.y, volume=0.3)
            self.movement_sound_timer = 0.4
    
    def _create_jump_particles(self):
        """Create particles when jumping."""
        # This would create particle effects at feet position
        pass
    
    def _create_landing_particles(self):
        """Create particles when landing."""
        # This would create dust particles at feet position
        pass
    
    def _create_dash_particles(self):
        """Create particles during dash."""
        # This would create trail particles
        pass
    
    def take_damage(self, amount: int, damage_source: str = "unknown") -> bool:
        """
        Take damage with shield and invulnerability checks.
        
        Args:
            amount: Damage amount
            damage_source: Source of damage for logging
            
        Returns:
            True if damage was taken
        """
        if self.invulnerable:
            return False
        
        if self.shield_active and self.shield_energy > 0:
            # Shield absorbs damage
            shield_damage = min(amount, self.shield_energy)
            self.shield_energy -= shield_damage
            amount -= shield_damage
            
            self.audio_manager.play_sound('bounce', self.x, self.y)
            self.shield_delay_timer = self.shield_delay
            
            if amount <= 0:
                return False  # All damage absorbed
        
        # Take health damage
        self.health -= amount
        self.health = max(0, self.health)
        
        # Start invulnerability
        self.invulnerable = True
        self.invulnerability_timer = self.invulnerability_duration
        
        # Screen shake
        self.screen_shake_trauma = min(1.0, self.screen_shake_trauma + amount * 0.1)
        
        # Audio and visual feedback
        self.audio_manager.play_sound('monstershout', self.x, self.y)
        
        # Change state
        if self.health <= 0:
            self.state = PlayerState.DYING
        else:
            self.state = PlayerState.HURT
            self.state_timer = 0.0
        
        print(f"Player took {amount} damage from {damage_source}. Health: {self.health}")
        return True
    
    def heal(self, amount: int):
        """Heal the player."""
        self.health = min(self.max_health, self.health + amount)
    
    def get_hitbox(self) -> pygame.Rect:
        """Get player hitbox for collision detection."""
        return pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.width,
            self.height
        )
    
    def get_current_sprite(self) -> pygame.Surface:
        """Get current animation frame."""
        if not self.current_animation:
            # Fallback sprite
            fallback = pygame.Surface((self.width, self.height))
            fallback.fill(config.COLORS['green'])
            return fallback
        
        return self.current_animation[self.animation_frame]
    
    def reset_to_checkpoint(self, x: float, y: float):
        """Reset player to checkpoint position."""
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.health = self.max_health
        self.shield_energy = self.max_shield_energy
        self.state = PlayerState.STANDING
        self.movement_state = MovementState.GROUNDED
        self.invulnerable = False
        self.invulnerability_timer = 0
        
        print(f"Player reset to checkpoint: ({x}, {y})")
    
    def get_stats(self) -> Dict:
        """Get player statistics for display."""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'shield': self.shield_energy,
            'max_shield': self.max_shield_energy,
            'position': (self.x, self.y),
            'velocity': (self.vel_x, self.vel_y),
            'state': self.state.value,
            'on_ground': self.on_ground,
            'facing_right': self.facing_right,
            'dash_cooldown': max(0, self.dash_cooldown_timer)
        }