"""
Forest Survival - Combat System
Advanced combat mechanics with combos, weapons, and damage calculation.
"""

import pygame
import math
import time
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass

import config


class AttackType(Enum):
    """Types of attacks available."""
    LIGHT = "light"
    HEAVY = "heavy"
    SPECIAL = "special"
    COMBO_FINISHER = "combo_finisher"
    DASH_ATTACK = "dash_attack"
    AERIAL_ATTACK = "aerial_attack"


class WeaponType(Enum):
    """Available weapon types."""
    SWORD = "sword"
    GUN = "gun"
    FISTS = "fists"
    MAGIC = "magic"


class ComboState(Enum):
    """Combo system states."""
    IDLE = "idle"
    BUILDING = "building"
    WINDOW = "window"
    FINISHED = "finished"
    BROKEN = "broken"


@dataclass
class AttackData:
    """Attack configuration data."""
    name: str
    damage: int
    range_: float
    duration: float
    recovery: float
    stamina_cost: int
    knockback: float
    hit_stun: float
    combo_contribution: int
    crit_chance: float = 0.1
    crit_multiplier: float = 1.5


@dataclass
class WeaponData:
    """Weapon configuration data."""
    name: str
    weapon_type: WeaponType
    base_damage: int
    range_: float
    attack_speed: float
    crit_chance: float
    special_attack: Optional[str] = None
    durability: int = 100
    requirements: Dict = None


class AttackHitbox:
    """Represents an attack hitbox."""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 attack_data: AttackData, source_id: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.attack_data = attack_data
        self.source_id = source_id
        self.lifetime = attack_data.duration
        self.hit_entities: Set[str] = set()  # Prevent multi-hitting
        self.active = True
        
        # Visual properties
        self.angle = 0.0
        self.scale = 1.0
        
    def update(self, dt: float) -> bool:
        """Update hitbox. Returns False when expired."""
        self.lifetime -= dt
        return self.lifetime > 0 and self.active
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def has_hit(self, entity_id: str) -> bool:
        """Check if this hitbox has already hit an entity."""
        return entity_id in self.hit_entities
    
    def mark_hit(self, entity_id: str):
        """Mark an entity as hit by this hitbox."""
        self.hit_entities.add(entity_id)


class ComboSystem:
    """Manages combo building and execution."""
    
    def __init__(self):
        self.state = ComboState.IDLE
        self.combo_count = 0
        self.combo_timer = 0.0
        self.combo_window = 2.0  # Time to continue combo
        self.max_combo = 0  # Track highest combo this session
        
        # Combo multipliers
        self.damage_multiplier = 1.0
        self.xp_multiplier = 1.0
        
        # Combo thresholds for bonuses
        self.combo_thresholds = {
            5: {'damage': 1.1, 'xp': 1.2},
            10: {'damage': 1.2, 'xp': 1.5},
            25: {'damage': 1.5, 'xp': 2.0},
            50: {'damage': 2.0, 'xp': 3.0},
            100: {'damage': 3.0, 'xp': 5.0}
        }
    
    def add_hit(self, damage_dealt: int) -> Dict:
        """
        Add a hit to the combo.
        
        Args:
            damage_dealt: Damage dealt by the hit
            
        Returns:
            Dictionary with combo information
        """
        if self.state == ComboState.IDLE:
            self.state = ComboState.BUILDING
        
        self.combo_count += 1
        self.combo_timer = self.combo_window
        
        # Update max combo
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
        
        # Calculate multipliers
        self._update_multipliers()
        
        return {
            'combo_count': self.combo_count,
            'damage_multiplier': self.damage_multiplier,
            'xp_multiplier': self.xp_multiplier,
            'is_milestone': self.combo_count in self.combo_thresholds
        }
    
    def update(self, dt: float):
        """Update combo system."""
        if self.state in [ComboState.BUILDING, ComboState.WINDOW]:
            self.combo_timer -= dt
            
            if self.combo_timer <= 0:
                self._break_combo()
    
    def _update_multipliers(self):
        """Update damage and XP multipliers based on combo count."""
        self.damage_multiplier = 1.0
        self.xp_multiplier = 1.0
        
        for threshold, bonuses in self.combo_thresholds.items():
            if self.combo_count >= threshold:
                self.damage_multiplier = bonuses['damage']
                self.xp_multiplier = bonuses['xp']
    
    def _break_combo(self):
        """Break the current combo."""
        if self.combo_count > 0:
            self.state = ComboState.BROKEN
            print(f"Combo broken at {self.combo_count} hits!")
        
        self.combo_count = 0
        self.combo_timer = 0.0
        self.damage_multiplier = 1.0
        self.xp_multiplier = 1.0
        
        # Reset to idle after a brief moment
        self.state = ComboState.IDLE
    
    def get_stats(self) -> Dict:
        """Get combo statistics."""
        return {
            'current_combo': self.combo_count,
            'max_combo': self.max_combo,
            'damage_multiplier': self.damage_multiplier,
            'xp_multiplier': self.xp_multiplier,
            'time_remaining': max(0, self.combo_timer),
            'state': self.state.value
        }


class CombatSystem:
    """
    Advanced combat system with weapons, combos, and special attacks.
    """
    
    def __init__(self, audio_manager, particle_system=None):
        """Initialize the combat system."""
        self.audio_manager = audio_manager
        self.particle_system = particle_system
        
        # Combat state
        self.is_attacking = False
        self.attack_timer = 0.0
        self.recovery_timer = 0.0
        self.current_attack = None
        
        # Weapon system
        self.equipped_weapon = self._create_default_weapon()
        self.available_weapons = self._initialize_weapons()
        
        # Combo system
        self.combo_system = ComboSystem()
        
        # Active hitboxes
        self.active_hitboxes: List[AttackHitbox] = []
        
        # Attack queue for combos
        self.attack_queue: List[AttackType] = []
        self.max_queue_size = 3
        
        # Stamina system
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen_rate = 20  # per second
        self.stamina_delay = 1.0  # delay before regen starts
        self.stamina_delay_timer = 0.0
        
        # Critical hit system
        self.last_crit_time = 0.0
        self.crit_chance_bonus = 0.0
        
        # Statistics
        self.total_damage_dealt = 0
        self.total_hits_landed = 0
        self.total_crits = 0
        self.attacks_made = 0
        
        print("Combat system initialized")
    
    def _create_default_weapon(self) -> WeaponData:
        """Create the default starting weapon."""
        return WeaponData(
            name="Fists",
            weapon_type=WeaponType.FISTS,
            base_damage=15,
            range_=40,
            attack_speed=1.2,
            crit_chance=0.05
        )
    
    def _initialize_weapons(self) -> Dict[str, WeaponData]:
        """Initialize available weapons."""
        weapons = {}
        
        # Sword
        weapons['iron_sword'] = WeaponData(
            name="Iron Sword",
            weapon_type=WeaponType.SWORD,
            base_damage=35,
            range_=60,
            attack_speed=1.0,
            crit_chance=0.15,
            special_attack="sword_slash",
            durability=100,
            requirements={'level': 3}
        )
        
        # Gun
        weapons['forest_gun'] = WeaponData(
            name="Forest Gun",
            weapon_type=WeaponType.GUN,
            base_damage=50,
            range_=200,
            attack_speed=0.8,
            crit_chance=0.20,
            special_attack="rapid_fire",
            durability=80,
            requirements={'level': 5}
        )
        
        # Magic weapon
        weapons['nature_staff'] = WeaponData(
            name="Nature Staff",
            weapon_type=WeaponType.MAGIC,
            base_damage=40,
            range_=120,
            attack_speed=0.6,
            crit_chance=0.25,
            special_attack="nature_burst",
            durability=60,
            requirements={'level': 8}
        )
        
        return weapons
    
    def update(self, dt: float):
        """Update combat system."""
        # Update timers
        self.attack_timer -= dt
        self.recovery_timer -= dt
        self.stamina_delay_timer -= dt
        
        # Update combo system
        self.combo_system.update(dt)
        
        # Update stamina
        self._update_stamina(dt)
        
        # Update active hitboxes
        self.active_hitboxes = [hitbox for hitbox in self.active_hitboxes 
                               if hitbox.update(dt)]
        
        # Check if attack is finished
        if self.is_attacking and self.attack_timer <= 0:
            self.is_attacking = False
            self.current_attack = None
    
    def _update_stamina(self, dt: float):
        """Update stamina regeneration."""
        if self.stamina_delay_timer <= 0 and self.stamina < self.max_stamina:
            self.stamina += self.stamina_regen_rate * dt
            self.stamina = min(self.max_stamina, self.stamina)
    
    def attempt_attack(self, attack_type: AttackType, player_x: float, player_y: float, 
                      facing_right: bool, on_ground: bool) -> bool:
        """
        Attempt to perform an attack.
        
        Args:
            attack_type: Type of attack to perform
            player_x: Player X position
            player_y: Player Y position
            facing_right: Player facing direction
            on_ground: Whether player is on ground
            
        Returns:
            True if attack was executed
        """
        # Check if we can attack
        if not self._can_attack(attack_type, on_ground):
            return False
        
        # Get attack data
        attack_data = self._get_attack_data(attack_type)
        if not attack_data:
            return False
        
        # Check stamina
        if self.stamina < attack_data.stamina_cost:
            return False
        
        # Execute attack
        self._execute_attack(attack_data, player_x, player_y, facing_right)
        
        # Consume stamina
        self.stamina -= attack_data.stamina_cost
        self.stamina_delay_timer = self.stamina_delay
        
        # Update statistics
        self.attacks_made += 1
        
        return True
    
    def _can_attack(self, attack_type: AttackType, on_ground: bool) -> bool:
        """Check if an attack can be performed."""
        # Can't attack while already attacking (unless combo)
        if self.is_attacking and attack_type != AttackType.LIGHT:
            return False
        
        # Can't attack during recovery
        if self.recovery_timer > 0:
            return False
        
        # Aerial attacks only in air
        if attack_type == AttackType.AERIAL_ATTACK and on_ground:
            return False
        
        # Some attacks require ground
        if attack_type in [AttackType.HEAVY, AttackType.SPECIAL] and not on_ground:
            return False
        
        return True
    
    def _get_attack_data(self, attack_type: AttackType) -> Optional[AttackData]:
        """Get attack data for the specified attack type."""
        weapon = self.equipped_weapon
        
        if attack_type == AttackType.LIGHT:
            return AttackData(
                name="Light Attack",
                damage=int(weapon.base_damage * 0.8),
                range_=weapon.range_,
                duration=0.2,
                recovery=0.3,
                stamina_cost=10,
                knockback=100,
                hit_stun=0.2,
                combo_contribution=1
            )
        
        elif attack_type == AttackType.HEAVY:
            return AttackData(
                name="Heavy Attack",
                damage=int(weapon.base_damage * 1.5),
                range_=weapon.range_ * 1.2,
                duration=0.4,
                recovery=0.8,
                stamina_cost=25,
                knockback=250,
                hit_stun=0.5,
                combo_contribution=2,
                crit_chance=weapon.crit_chance * 1.5
            )
        
        elif attack_type == AttackType.DASH_ATTACK:
            return AttackData(
                name="Dash Attack",
                damage=int(weapon.base_damage * 1.2),
                range_=weapon.range_ * 1.5,
                duration=0.3,
                recovery=0.5,
                stamina_cost=20,
                knockback=300,
                hit_stun=0.3,
                combo_contribution=2
            )
        
        elif attack_type == AttackType.AERIAL_ATTACK:
            return AttackData(
                name="Aerial Attack",
                damage=int(weapon.base_damage * 1.1),
                range_=weapon.range_,
                duration=0.25,
                recovery=0.4,
                stamina_cost=15,
                knockback=200,
                hit_stun=0.3,
                combo_contribution=1
            )
        
        elif attack_type == AttackType.SPECIAL:
            return self._get_special_attack_data()
        
        return None
    
    def _get_special_attack_data(self) -> Optional[AttackData]:
        """Get special attack data based on equipped weapon."""
        weapon = self.equipped_weapon
        
        if weapon.weapon_type == WeaponType.SWORD:
            return AttackData(
                name="Sword Slash",
                damage=int(weapon.base_damage * 2.0),
                range_=weapon.range_ * 1.8,
                duration=0.6,
                recovery=1.2,
                stamina_cost=40,
                knockback=400,
                hit_stun=0.8,
                combo_contribution=3,
                crit_chance=weapon.crit_chance * 2.0
            )
        
        elif weapon.weapon_type == WeaponType.GUN:
            return AttackData(
                name="Rapid Fire",
                damage=int(weapon.base_damage * 0.6),
                range_=weapon.range_,
                duration=1.0,
                recovery=1.5,
                stamina_cost=50,
                knockback=150,
                hit_stun=0.1,
                combo_contribution=1  # Multi-hit
            )
        
        elif weapon.weapon_type == WeaponType.MAGIC:
            return AttackData(
                name="Nature Burst",
                damage=int(weapon.base_damage * 1.8),
                range_=weapon.range_ * 2.0,
                duration=0.8,
                recovery=2.0,
                stamina_cost=60,
                knockback=300,
                hit_stun=1.0,
                combo_contribution=4,
                crit_chance=weapon.crit_chance * 1.5
            )
        
        return None
    
    def _execute_attack(self, attack_data: AttackData, player_x: float, 
                       player_y: float, facing_right: bool):
        """Execute an attack."""
        self.is_attacking = True
        self.attack_timer = attack_data.duration
        self.recovery_timer = attack_data.recovery
        self.current_attack = attack_data
        
        # Create hitbox
        hitbox_x = player_x
        hitbox_y = player_y
        hitbox_width = attack_data.range_
        hitbox_height = 40  # Default height
        
        # Adjust hitbox position based on facing direction
        if facing_right:
            hitbox_x += 20  # Offset from player center
        else:
            hitbox_x -= attack_data.range_ + 20
        
        # Create and add hitbox
        hitbox = AttackHitbox(
            hitbox_x, hitbox_y, hitbox_width, hitbox_height,
            attack_data, "player"
        )
        
        self.active_hitboxes.append(hitbox)
        
        # Play attack sound
        self._play_attack_sound(attack_data)
        
        # Create visual effects
        if self.particle_system:
            self._create_attack_particles(hitbox_x, hitbox_y, attack_data, facing_right)
        
        print(f"Executed {attack_data.name}")
    
    def _play_attack_sound(self, attack_data: AttackData):
        """Play appropriate sound for attack."""
        weapon_type = self.equipped_weapon.weapon_type
        
        if weapon_type == WeaponType.SWORD:
            self.audio_manager.play_sound('attack', 0, 0, volume=0.7)
        elif weapon_type == WeaponType.GUN:
            self.audio_manager.play_sound('bulletsound', 0, 0, volume=0.8)
        elif weapon_type == WeaponType.MAGIC:
            self.audio_manager.play_sound('string', 0, 0, volume=0.6)
        else:  # Fists or default
            self.audio_manager.play_sound('attack', 0, 0, volume=0.5)
    
    def _create_attack_particles(self, x: float, y: float, attack_data: AttackData, 
                               facing_right: bool):
        """Create particle effects for attack."""
        # This would create particles based on weapon type and attack
        # Implementation depends on particle system
        pass
    
    def check_hit(self, target_rect: pygame.Rect, target_id: str) -> Optional[Dict]:
        """
        Check if any active hitboxes hit a target.
        
        Args:
            target_rect: Target collision rectangle
            target_id: Unique identifier for target
            
        Returns:
            Hit information dictionary if hit occurred
        """
        for hitbox in self.active_hitboxes:
            if hitbox.has_hit(target_id):
                continue  # Already hit this target
            
            if hitbox.get_rect().colliderect(target_rect):
                # Hit detected!
                hitbox.mark_hit(target_id)
                
                # Calculate damage
                base_damage = hitbox.attack_data.damage
                
                # Apply combo multiplier
                combo_info = self.combo_system.add_hit(base_damage)
                final_damage = int(base_damage * combo_info['damage_multiplier'])
                
                # Check for critical hit
                is_crit = self._check_critical_hit(hitbox.attack_data)
                if is_crit:
                    final_damage = int(final_damage * hitbox.attack_data.crit_multiplier)
                    self.total_crits += 1
                
                # Update statistics
                self.total_damage_dealt += final_damage
                self.total_hits_landed += 1
                
                # Calculate XP reward
                xp_reward = 5 * combo_info['xp_multiplier']
                if is_crit:
                    xp_reward *= 1.5
                
                return {
                    'damage': final_damage,
                    'knockback': hitbox.attack_data.knockback,
                    'hit_stun': hitbox.attack_data.hit_stun,
                    'is_crit': is_crit,
                    'combo_info': combo_info,
                    'xp_reward': int(xp_reward),
                    'attack_name': hitbox.attack_data.name
                }
        
        return None
    
    def _check_critical_hit(self, attack_data: AttackData) -> bool:
        """Check if attack should be a critical hit."""
        total_crit_chance = attack_data.crit_chance + self.crit_chance_bonus
        
        # Bonus crit chance based on combo
        combo_bonus = min(0.1, self.combo_system.combo_count * 0.002)
        total_crit_chance += combo_bonus
        
        return time.time() % 1.0 < total_crit_chance  # Simple random check
    
    def equip_weapon(self, weapon_id: str) -> bool:
        """
        Equip a weapon.
        
        Args:
            weapon_id: ID of weapon to equip
            
        Returns:
            True if weapon was equipped successfully
        """
        if weapon_id not in self.available_weapons:
            return False
        
        weapon = self.available_weapons[weapon_id]
        
        # Check requirements
        if weapon.requirements:
            # This would check player level, stats, etc.
            # For now, just equip it
            pass
        
        self.equipped_weapon = weapon
        print(f"Equipped {weapon.name}")
        return True
    
    def get_weapon_stats(self) -> Dict:
        """Get current weapon statistics."""
        weapon = self.equipped_weapon
        return {
            'name': weapon.name,
            'type': weapon.weapon_type.value,
            'damage': weapon.base_damage,
            'range': weapon.range_,
            'attack_speed': weapon.attack_speed,
            'crit_chance': weapon.crit_chance,
            'durability': getattr(weapon, 'durability', 100),
            'special_attack': weapon.special_attack
        }
    
    def get_combat_stats(self) -> Dict:
        """Get combat statistics."""
        hit_accuracy = 0.0
        if self.attacks_made > 0:
            hit_accuracy = self.total_hits_landed / self.attacks_made
        
        crit_rate = 0.0
        if self.total_hits_landed > 0:
            crit_rate = self.total_crits / self.total_hits_landed
        
        return {
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'stamina_percentage': self.stamina / self.max_stamina,
            'is_attacking': self.is_attacking,
            'current_attack': self.current_attack.name if self.current_attack else None,
            'combo_stats': self.combo_system.get_stats(),
            'total_damage_dealt': self.total_damage_dealt,
            'total_hits_landed': self.total_hits_landed,
            'total_crits': self.total_crits,
            'attacks_made': self.attacks_made,
            'hit_accuracy': hit_accuracy,
            'crit_rate': crit_rate,
            'weapon_stats': self.get_weapon_stats()
        }
    
    def reset_combo(self):
        """Reset the combo system."""
        self.combo_system._break_combo()
    
    def can_attack_type(self, attack_type: AttackType) -> bool:
        """Check if a specific attack type can be performed."""
        attack_data = self._get_attack_data(attack_type)
        if not attack_data:
            return False
        
        return (not self.is_attacking and 
                self.recovery_timer <= 0 and 
                self.stamina >= attack_data.stamina_cost)
    
    def get_active_hitboxes(self) -> List[AttackHitbox]:
        """Get list of active hitboxes for rendering."""
        return self.active_hitboxes