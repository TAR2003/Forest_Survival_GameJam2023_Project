"""
Forest Survival - Shield System
Advanced timing-based defense mechanics with visual feedback.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

import config


class ShieldState(Enum):
    """Shield activation states."""
    INACTIVE = "inactive"
    RAISING = "raising"
    ACTIVE = "active"
    PERFECT_BLOCK = "perfect_block"
    LOWERING = "lowering"
    BROKEN = "broken"
    RECHARGING = "recharging"


@dataclass
class ShieldProperties:
    """Shield configuration properties."""
    max_energy: float = 100.0
    regen_rate: float = 25.0  # Energy per second
    drain_rate: float = 30.0  # Energy per second when active
    perfect_window: float = 0.15  # Perfect block timing window
    raise_time: float = 0.1  # Time to raise shield
    lower_time: float = 0.1  # Time to lower shield
    break_threshold: float = 80.0  # Damage to break shield
    recharge_delay: float = 2.0  # Delay before regen starts
    damage_reduction: float = 0.8  # 80% damage reduction
    perfect_multiplier: float = 2.0  # Perfect block XP multiplier


class ShieldEffect:
    """Visual effect for shield interactions."""
    
    def __init__(self, x: float, y: float, effect_type: str, color: tuple):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.color = color
        self.lifetime = 0.5
        self.max_lifetime = 0.5
        self.size = 20
        self.alpha = 255
        
    def update(self, dt: float) -> bool:
        """Update effect. Returns False when expired."""
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            return False
        
        # Update visual properties
        progress = 1.0 - (self.lifetime / self.max_lifetime)
        
        if self.effect_type == "perfect_block":
            self.size = 20 + progress * 40
            self.alpha = int(255 * (1.0 - progress))
        elif self.effect_type == "block":
            self.size = 15 + progress * 25
            self.alpha = int(255 * (1.0 - progress))
        elif self.effect_type == "break":
            self.size = 30 + progress * 50
            self.alpha = int(255 * (1.0 - progress))
        
        return True
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render the effect."""
        if self.alpha <= 0:
            return
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        # Create surface with alpha
        effect_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, self.alpha)
        
        if self.effect_type == "perfect_block":
            # Bright flash with sparkles
            pygame.draw.circle(effect_surface, color_with_alpha, 
                             (self.size, self.size), self.size)
            # Add sparkle effect
            for i in range(8):
                angle = i * math.pi / 4
                spark_x = self.size + math.cos(angle) * self.size * 0.8
                spark_y = self.size + math.sin(angle) * self.size * 0.8
                pygame.draw.circle(effect_surface, color_with_alpha, 
                                 (int(spark_x), int(spark_y)), 3)
        
        elif self.effect_type == "block":
            # Simple flash
            pygame.draw.circle(effect_surface, color_with_alpha, 
                             (self.size, self.size), self.size)
        
        elif self.effect_type == "break":
            # Shattered effect
            pygame.draw.circle(effect_surface, color_with_alpha, 
                             (self.size, self.size), self.size, 3)
            # Add break lines
            for i in range(6):
                angle = i * math.pi / 3
                start_x = self.size + math.cos(angle) * self.size * 0.3
                start_y = self.size + math.sin(angle) * self.size * 0.3
                end_x = self.size + math.cos(angle) * self.size * 1.2
                end_y = self.size + math.sin(angle) * self.size * 1.2
                pygame.draw.line(effect_surface, color_with_alpha, 
                               (start_x, start_y), (end_x, end_y), 2)
        
        screen.blit(effect_surface, (render_x - self.size, render_y - self.size))


class ShieldSystem:
    """
    Advanced shield system with timing-based mechanics.
    """
    
    def __init__(self, audio_manager, properties: Optional[ShieldProperties] = None):
        """Initialize the shield system."""
        self.audio_manager = audio_manager
        self.properties = properties or ShieldProperties()
        
        # Shield state
        self.state = ShieldState.INACTIVE
        self.energy = self.properties.max_energy
        self.state_timer = 0.0
        self.recharge_delay_timer = 0.0
        
        # Input tracking
        self.shield_input_pressed = False
        self.shield_input_held = False
        self.last_input_time = 0.0
        
        # Perfect block tracking
        self.perfect_block_window_active = False
        self.perfect_block_timer = 0.0
        
        # Statistics
        self.total_blocks = 0
        self.perfect_blocks = 0
        self.damage_blocked = 0.0
        
        # Visual effects
        self.effects: List[ShieldEffect] = []
        self.shield_visual_intensity = 0.0
        self.shield_pulse_timer = 0.0
        
        # Audio
        self.shield_sound_timer = 0.0
        
        print("Shield system initialized")
    
    def update(self, dt: float, shield_input_pressed: bool, shield_input_held: bool):
        """
        Update shield system.
        
        Args:
            dt: Delta time in seconds
            shield_input_pressed: True if shield button was just pressed
            shield_input_held: True if shield button is being held
        """
        # Update timers
        self.state_timer += dt
        self.recharge_delay_timer -= dt
        self.perfect_block_timer -= dt
        self.shield_pulse_timer += dt
        self.shield_sound_timer -= dt
        
        # Store input states
        self.shield_input_pressed = shield_input_pressed
        self.shield_input_held = shield_input_held
        
        # Update state machine
        self._update_state_machine(dt)
        
        # Update energy
        self._update_energy(dt)
        
        # Update visual effects
        self._update_effects(dt)
        
        # Update perfect block window
        if self.perfect_block_window_active:
            if self.perfect_block_timer <= 0:
                self.perfect_block_window_active = False
    
    def _update_state_machine(self, dt: float):
        """Update shield state machine."""
        if self.state == ShieldState.INACTIVE:
            if self.shield_input_pressed and self.energy > 0:
                self._start_raising_shield()
        
        elif self.state == ShieldState.RAISING:
            if self.state_timer >= self.properties.raise_time:
                self._activate_shield()
            elif not self.shield_input_held:
                self._start_lowering_shield()
        
        elif self.state == ShieldState.ACTIVE:
            if not self.shield_input_held or self.energy <= 0:
                self._start_lowering_shield()
        
        elif self.state == ShieldState.PERFECT_BLOCK:
            if self.state_timer >= 0.2:  # Perfect block display duration
                if self.shield_input_held and self.energy > 0:
                    self._activate_shield()
                else:
                    self._start_lowering_shield()
        
        elif self.state == ShieldState.LOWERING:
            if self.state_timer >= self.properties.lower_time:
                self.state = ShieldState.INACTIVE
                self.state_timer = 0.0
        
        elif self.state == ShieldState.BROKEN:
            if self.energy >= self.properties.max_energy * 0.3:  # 30% to repair
                self.state = ShieldState.RECHARGING
                self.state_timer = 0.0
        
        elif self.state == ShieldState.RECHARGING:
            if self.state_timer >= 1.0:  # Recharge animation duration
                self.state = ShieldState.INACTIVE
                self.state_timer = 0.0
    
    def _start_raising_shield(self):
        """Start raising the shield."""
        self.state = ShieldState.RAISING
        self.state_timer = 0.0
        self.perfect_block_window_active = True
        self.perfect_block_timer = self.properties.perfect_window
        
        # Audio feedback
        self.audio_manager.play_sound('string', 0, 0, volume=0.6)
    
    def _activate_shield(self):
        """Activate the shield."""
        self.state = ShieldState.ACTIVE
        self.state_timer = 0.0
        self.shield_visual_intensity = 1.0
    
    def _start_lowering_shield(self):
        """Start lowering the shield."""
        self.state = ShieldState.LOWERING
        self.state_timer = 0.0
        self.perfect_block_window_active = False
    
    def _update_energy(self, dt: float):
        """Update shield energy."""
        if self.state == ShieldState.ACTIVE:
            # Drain energy while active
            self.energy -= self.properties.drain_rate * dt
            self.energy = max(0, self.energy)
            
            if self.energy <= 0:
                self._break_shield()
        
        elif self.state in [ShieldState.INACTIVE, ShieldState.RECHARGING]:
            # Regenerate energy
            if self.recharge_delay_timer <= 0:
                self.energy += self.properties.regen_rate * dt
                self.energy = min(self.properties.max_energy, self.energy)
    
    def _break_shield(self):
        """Break the shield."""
        self.state = ShieldState.BROKEN
        self.state_timer = 0.0
        self.energy = 0
        self.recharge_delay_timer = self.properties.recharge_delay
        
        # Audio and visual feedback
        self.audio_manager.play_sound('bombsound', 0, 0, volume=0.8)
        
        print("Shield broken!")
    
    def _update_effects(self, dt: float):
        """Update visual effects."""
        # Update existing effects
        self.effects = [effect for effect in self.effects if effect.update(dt)]
        
        # Update shield visual intensity
        if self.state == ShieldState.ACTIVE:
            self.shield_visual_intensity = min(1.0, self.shield_visual_intensity + dt * 3)
        else:
            self.shield_visual_intensity = max(0.0, self.shield_visual_intensity - dt * 5)
    
    def block_attack(self, damage: float, attacker_x: float, attacker_y: float, 
                    player_x: float, player_y: float) -> Tuple[float, bool, int]:
        """
        Attempt to block an attack.
        
        Args:
            damage: Incoming damage
            attacker_x: Attacker X position
            attacker_y: Attacker Y position
            player_x: Player X position
            player_y: Player Y position
            
        Returns:
            Tuple of (actual_damage, was_blocked, xp_earned)
        """
        if self.state in [ShieldState.INACTIVE, ShieldState.LOWERING, 
                         ShieldState.BROKEN, ShieldState.RECHARGING]:
            return damage, False, 0  # No block
        
        # Calculate block effectiveness
        damage_reduction = self.properties.damage_reduction
        is_perfect_block = False
        xp_earned = 10  # Base XP for blocking
        
        # Check for perfect block
        if (self.perfect_block_window_active and 
            self.state in [ShieldState.RAISING, ShieldState.ACTIVE]):
            is_perfect_block = True
            damage_reduction = 1.0  # Perfect block negates all damage
            xp_earned = int(xp_earned * self.properties.perfect_multiplier)
            self.perfect_blocks += 1
            
            # Perfect block state
            self.state = ShieldState.PERFECT_BLOCK
            self.state_timer = 0.0
            self.perfect_block_window_active = False
            
            # Audio feedback
            self.audio_manager.play_sound('celebrate', player_x, player_y)
            
            # Visual effect
            effect_x = (player_x + attacker_x) / 2
            effect_y = (player_y + attacker_y) / 2
            self.effects.append(ShieldEffect(effect_x, effect_y, "perfect_block", 
                                           config.COLORS['gold']))
            
            print(f"Perfect block! XP earned: {xp_earned}")
        
        else:
            # Regular block
            if damage > self.properties.break_threshold:
                # High damage can break shield
                self._break_shield()
                damage_reduction = 0.3  # Reduced effectiveness when broken
            
            # Audio feedback
            self.audio_manager.play_sound('bounce', player_x, player_y)
            
            # Visual effect
            effect_x = (player_x + attacker_x) / 2
            effect_y = (player_y + attacker_y) / 2
            self.effects.append(ShieldEffect(effect_x, effect_y, "block", 
                                           config.COLORS['cyan']))
        
        # Calculate final damage
        blocked_damage = damage * damage_reduction
        final_damage = damage - blocked_damage
        
        # Update statistics
        self.total_blocks += 1
        self.damage_blocked += blocked_damage
        
        # Reduce shield energy based on damage blocked
        energy_cost = blocked_damage * 0.5
        self.energy -= energy_cost
        self.energy = max(0, self.energy)
        
        # Start recharge delay
        self.recharge_delay_timer = self.properties.recharge_delay
        
        return final_damage, True, xp_earned
    
    def can_block(self) -> bool:
        """Check if shield can currently block."""
        return (self.state in [ShieldState.RAISING, ShieldState.ACTIVE, 
                              ShieldState.PERFECT_BLOCK] and self.energy > 0)
    
    def is_perfect_block_available(self) -> bool:
        """Check if perfect block window is active."""
        return self.perfect_block_window_active and self.perfect_block_timer > 0
    
    def get_shield_angle(self, player_facing_right: bool) -> float:
        """Get shield visual angle based on state."""
        base_angle = 0 if player_facing_right else math.pi
        
        if self.state == ShieldState.RAISING:
            progress = self.state_timer / self.properties.raise_time
            return base_angle + (1.0 - progress) * math.pi / 4
        
        elif self.state == ShieldState.LOWERING:
            progress = self.state_timer / self.properties.lower_time
            return base_angle + progress * math.pi / 4
        
        elif self.state == ShieldState.PERFECT_BLOCK:
            # Slight forward angle for perfect block
            return base_angle - math.pi / 8 if player_facing_right else base_angle + math.pi / 8
        
        return base_angle
    
    def get_shield_alpha(self) -> int:
        """Get shield transparency for rendering."""
        if self.state == ShieldState.INACTIVE:
            return 0
        
        elif self.state == ShieldState.RAISING:
            progress = self.state_timer / self.properties.raise_time
            return int(255 * progress)
        
        elif self.state == ShieldState.LOWERING:
            progress = 1.0 - (self.state_timer / self.properties.lower_time)
            return int(255 * progress)
        
        elif self.state == ShieldState.ACTIVE:
            # Pulse effect
            pulse = (math.sin(self.shield_pulse_timer * 8) + 1) / 2
            base_alpha = 200
            return int(base_alpha + pulse * 55)
        
        elif self.state == ShieldState.PERFECT_BLOCK:
            # Bright flash
            return 255
        
        elif self.state == ShieldState.BROKEN:
            # Flickering broken effect
            flicker = math.sin(self.state_timer * 20) > 0
            return 100 if flicker else 0
        
        elif self.state == ShieldState.RECHARGING:
            # Growing intensity
            progress = self.state_timer / 1.0
            return int(150 * progress)
        
        return 255
    
    def get_shield_color(self) -> Tuple[int, int, int]:
        """Get shield color based on state."""
        if self.state == ShieldState.PERFECT_BLOCK:
            return config.COLORS['gold']
        elif self.state == ShieldState.BROKEN:
            return config.COLORS['red']
        elif self.energy < self.properties.max_energy * 0.3:
            return config.COLORS['orange']
        else:
            return config.COLORS['cyan']
    
    def render_effects(self, screen: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render shield effects."""
        for effect in self.effects:
            effect.render(screen, camera_offset)
    
    def get_energy_percentage(self) -> float:
        """Get shield energy as percentage."""
        return self.energy / self.properties.max_energy
    
    def get_stats(self) -> Dict:
        """Get shield statistics."""
        block_accuracy = 0.0
        if self.total_blocks > 0:
            block_accuracy = self.perfect_blocks / self.total_blocks
        
        return {
            'state': self.state.value,
            'energy': self.energy,
            'max_energy': self.properties.max_energy,
            'energy_percentage': self.get_energy_percentage(),
            'total_blocks': self.total_blocks,
            'perfect_blocks': self.perfect_blocks,
            'block_accuracy': block_accuracy,
            'damage_blocked': self.damage_blocked,
            'can_block': self.can_block(),
            'perfect_window_active': self.perfect_block_window_active,
            'recharge_delay': max(0, self.recharge_delay_timer)
        }
    
    def reset(self):
        """Reset shield system to initial state."""
        self.state = ShieldState.INACTIVE
        self.energy = self.properties.max_energy
        self.state_timer = 0.0
        self.recharge_delay_timer = 0.0
        self.perfect_block_window_active = False
        self.perfect_block_timer = 0.0
        self.effects.clear()
        self.shield_visual_intensity = 0.0
        
        print("Shield system reset")