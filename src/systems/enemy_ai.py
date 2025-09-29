"""
Forest Survival - Enemy AI Framework
Sophisticated enemy behavior with state machines and decision making.
"""

import pygame
import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

import config


class AIState(Enum):
    """Base AI states for all enemies."""
    IDLE = "idle"
    PATROL = "patrol"
    SEARCH = "search"
    CHASE = "chase"
    ATTACK = "attack"
    RETREAT = "retreat"
    STUNNED = "stunned"
    DYING = "dying"
    DEAD = "dead"


class EnemyType(Enum):
    """Types of enemies with different AI behaviors."""
    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    RANGED = "ranged"
    FLYING = "flying"
    BOSS = "boss"


class AlertLevel(Enum):
    """Enemy alertness levels."""
    UNAWARE = "unaware"
    SUSPICIOUS = "suspicious"
    ALERT = "alert"
    COMBAT = "combat"


@dataclass
class AIParameters:
    """Configuration parameters for AI behavior."""
    # Detection
    sight_range: float = 150.0
    sight_angle: float = math.pi / 2  # 90 degrees
    hearing_range: float = 100.0
    
    # Movement
    move_speed: float = 80.0
    chase_speed: float = 120.0
    retreat_speed: float = 100.0
    
    # Combat
    attack_range: float = 40.0
    attack_damage: int = 20
    attack_cooldown: float = 2.0
    
    # Behavior
    aggression: float = 0.5  # 0.0 to 1.0
    intelligence: float = 0.5  # 0.0 to 1.0
    patrol_radius: float = 100.0
    retreat_threshold: float = 0.3  # Health percentage
    
    # State timers
    idle_time_min: float = 2.0
    idle_time_max: float = 5.0
    search_time: float = 8.0
    stun_recovery: float = 1.5


class Blackboard:
    """Shared memory for AI decision making."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.timers: Dict[str, float] = {}
    
    def set(self, key: str, value: Any):
        """Set a value in the blackboard."""
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the blackboard."""
        return self.data.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if blackboard has a key."""
        return key in self.data
    
    def remove(self, key: str):
        """Remove a key from the blackboard."""
        self.data.pop(key, None)
    
    def set_timer(self, key: str, duration: float):
        """Set a countdown timer."""
        self.timers[key] = duration
    
    def get_timer(self, key: str) -> float:
        """Get time remaining on timer."""
        return self.timers.get(key, 0.0)
    
    def update_timers(self, dt: float):
        """Update all timers."""
        for key in list(self.timers.keys()):
            self.timers[key] -= dt
            if self.timers[key] <= 0:
                del self.timers[key]


class SensorSystem:
    """Handles enemy perception and detection."""
    
    def __init__(self, ai_params: AIParameters):
        self.params = ai_params
        self.last_seen_player_pos = None
        self.last_seen_time = 0.0
        self.alert_level = AlertLevel.UNAWARE
        self.noise_events: List[Tuple[float, float, float]] = []  # x, y, timestamp
    
    def update(self, dt: float, enemy_pos: Tuple[float, float], 
               enemy_facing: float, player_pos: Tuple[float, float],
               obstacles: List[pygame.Rect]) -> Dict[str, Any]:
        """
        Update sensor system and return perception data.
        
        Args:
            dt: Delta time
            enemy_pos: Enemy position (x, y)
            enemy_facing: Enemy facing direction in radians
            player_pos: Player position (x, y)
            obstacles: List of obstacle rectangles
            
        Returns:
            Dictionary with perception data
        """
        perception = {
            'can_see_player': False,
            'can_hear_player': False,
            'player_direction': 0.0,
            'player_distance': 0.0,
            'last_known_position': self.last_seen_player_pos,
            'alert_level': self.alert_level,
            'noise_sources': []
        }
        
        # Calculate distance to player
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        perception['player_distance'] = distance
        
        if distance > 0:
            perception['player_direction'] = math.atan2(dy, dx)
        
        # Visual detection
        if self._can_see_player(enemy_pos, enemy_facing, player_pos, obstacles):
            perception['can_see_player'] = True
            self.last_seen_player_pos = player_pos
            self.last_seen_time = time.time()
            self._increase_alert_level()
        
        # Audio detection
        if distance <= self.params.hearing_range:
            perception['can_hear_player'] = True
            if self.alert_level == AlertLevel.UNAWARE:
                self.alert_level = AlertLevel.SUSPICIOUS
        
        # Process noise events
        current_time = time.time()
        self.noise_events = [(x, y, t) for x, y, t in self.noise_events 
                            if current_time - t < 5.0]  # Keep noise for 5 seconds
        
        for noise_x, noise_y, noise_time in self.noise_events:
            noise_dx = noise_x - enemy_pos[0]
            noise_dy = noise_y - enemy_pos[1]
            noise_distance = math.sqrt(noise_dx * noise_dx + noise_dy * noise_dy)
            
            if noise_distance <= self.params.hearing_range:
                perception['noise_sources'].append({
                    'position': (noise_x, noise_y),
                    'age': current_time - noise_time,
                    'distance': noise_distance
                })
        
        # Decay alert level over time
        self._decay_alert_level(dt)
        
        return perception
    
    def _can_see_player(self, enemy_pos: Tuple[float, float], enemy_facing: float,
                       player_pos: Tuple[float, float], obstacles: List[pygame.Rect]) -> bool:
        """Check if enemy can see the player."""
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check range
        if distance > self.params.sight_range:
            return False
        
        # Check angle
        angle_to_player = math.atan2(dy, dx)
        angle_diff = abs(angle_to_player - enemy_facing)
        
        # Normalize angle difference
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        angle_diff = abs(angle_diff)
        
        if angle_diff > self.params.sight_angle / 2:
            return False
        
        # Check line of sight (ray casting)
        return self._has_line_of_sight(enemy_pos, player_pos, obstacles)
    
    def _has_line_of_sight(self, start: Tuple[float, float], 
                          end: Tuple[float, float], obstacles: List[pygame.Rect]) -> bool:
        """Check if there's a clear line of sight between two points."""
        # Simple ray casting - check if line intersects any obstacles
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])))
        if steps == 0:
            return True
        
        dx = (end[0] - start[0]) / steps
        dy = (end[1] - start[1]) / steps
        
        for i in range(steps):
            x = start[0] + dx * i
            y = start[1] + dy * i
            
            # Check if point is inside any obstacle
            for obstacle in obstacles:
                if obstacle.collidepoint(x, y):
                    return False
        
        return True
    
    def _increase_alert_level(self):
        """Increase alert level when player is detected."""
        if self.alert_level == AlertLevel.UNAWARE:
            self.alert_level = AlertLevel.SUSPICIOUS
        elif self.alert_level == AlertLevel.SUSPICIOUS:
            self.alert_level = AlertLevel.ALERT
        elif self.alert_level == AlertLevel.ALERT:
            self.alert_level = AlertLevel.COMBAT
    
    def _decay_alert_level(self, dt: float):
        """Gradually decrease alert level over time."""
        current_time = time.time()
        time_since_detection = current_time - self.last_seen_time
        
        if time_since_detection > 10.0:  # 10 seconds
            if self.alert_level == AlertLevel.COMBAT:
                self.alert_level = AlertLevel.ALERT
        
        if time_since_detection > 20.0:  # 20 seconds
            if self.alert_level == AlertLevel.ALERT:
                self.alert_level = AlertLevel.SUSPICIOUS
        
        if time_since_detection > 30.0:  # 30 seconds
            if self.alert_level == AlertLevel.SUSPICIOUS:
                self.alert_level = AlertLevel.UNAWARE
    
    def add_noise_event(self, x: float, y: float):
        """Add a noise event that enemies can hear."""
        self.noise_events.append((x, y, time.time()))


class AIBehaviorTree:
    """Simple behavior tree implementation for AI decisions."""
    
    class Node(ABC):
        """Base node class."""
        
        @abstractmethod
        def execute(self, blackboard: Blackboard, perception: Dict) -> bool:
            """Execute the node. Returns True on success, False on failure."""
            pass
    
    class Sequence(Node):
        """Executes children in order, stops on first failure."""
        
        def __init__(self, children: List['AIBehaviorTree.Node']):
            self.children = children
        
        def execute(self, blackboard: Blackboard, perception: Dict) -> bool:
            for child in self.children:
                if not child.execute(blackboard, perception):
                    return False
            return True
    
    class Selector(Node):
        """Executes children in order, stops on first success."""
        
        def __init__(self, children: List['AIBehaviorTree.Node']):
            self.children = children
        
        def execute(self, blackboard: Blackboard, perception: Dict) -> bool:
            for child in self.children:
                if child.execute(blackboard, perception):
                    return True
            return False
    
    class Condition(Node):
        """Conditional node that checks a condition."""
        
        def __init__(self, condition_func):
            self.condition_func = condition_func
        
        def execute(self, blackboard: Blackboard, perception: Dict) -> bool:
            return self.condition_func(blackboard, perception)
    
    class Action(Node):
        """Action node that performs an action."""
        
        def __init__(self, action_func):
            self.action_func = action_func
        
        def execute(self, blackboard: Blackboard, perception: Dict) -> bool:
            return self.action_func(blackboard, perception)


class EnemyAI:
    """
    Main AI controller for enemy entities.
    """
    
    def __init__(self, enemy_id: str, enemy_type: EnemyType, ai_params: AIParameters):
        """Initialize enemy AI."""
        self.enemy_id = enemy_id
        self.enemy_type = enemy_type
        self.params = ai_params
        
        # State management
        self.current_state = AIState.IDLE
        self.state_timer = 0.0
        self.previous_state = None
        
        # Systems
        self.blackboard = Blackboard()
        self.sensors = SensorSystem(ai_params)
        self.behavior_tree = self._create_behavior_tree()
        
        # Movement and position
        self.position = (0.0, 0.0)
        self.velocity = (0.0, 0.0)
        self.facing_direction = 0.0
        self.target_position = None
        
        # Combat
        self.health = 100
        self.max_health = 100
        self.last_attack_time = 0.0
        
        # Patrol behavior
        self.patrol_center = (0.0, 0.0)
        self.patrol_points: List[Tuple[float, float]] = []
        self.current_patrol_index = 0
        
        # Decision making
        self.decision_timer = 0.0
        self.decision_interval = 0.2  # Make decisions every 200ms
        
        print(f"Enemy AI {enemy_id} ({enemy_type.value}) initialized")
    
    def update(self, dt: float, enemy_pos: Tuple[float, float], 
               player_pos: Tuple[float, float], obstacles: List[pygame.Rect]) -> Dict[str, Any]:
        """
        Update AI and return action commands.
        
        Args:
            dt: Delta time
            enemy_pos: Current enemy position
            player_pos: Current player position
            obstacles: List of obstacle rectangles for pathfinding
            
        Returns:
            Dictionary with AI commands and state
        """
        self.position = enemy_pos
        
        # Update timers
        self.state_timer += dt
        self.decision_timer += dt
        self.blackboard.update_timers(dt)
        
        # Update sensors
        perception = self.sensors.update(dt, enemy_pos, self.facing_direction, 
                                       player_pos, obstacles)
        
        # Make decisions
        commands = {}
        if self.decision_timer >= self.decision_interval:
            self.decision_timer = 0.0
            
            # Execute behavior tree
            self.behavior_tree.execute(self.blackboard, perception)
            
            # Update state machine
            commands = self._update_state_machine(perception, obstacles)
        
        # Apply physics and movement
        movement_commands = self._update_movement(dt)
        commands.update(movement_commands)
        
        # Add debug information
        commands.update({
            'ai_state': self.current_state.value,
            'alert_level': perception['alert_level'].value,
            'can_see_player': perception['can_see_player'],
            'player_distance': perception['player_distance'],
            'health': self.health,
            'facing_direction': self.facing_direction
        })
        
        return commands
    
    def _create_behavior_tree(self):
        """Create behavior tree based on enemy type."""
        # This is a simplified example - real implementation would be more complex
        
        def can_see_player(blackboard, perception):
            return perception['can_see_player']
        
        def player_in_attack_range(blackboard, perception):
            return perception['player_distance'] <= self.params.attack_range
        
        def health_low(blackboard, perception):
            return self.health / self.max_health <= self.params.retreat_threshold
        
        def set_state_chase(blackboard, perception):
            self._change_state(AIState.CHASE)
            return True
        
        def set_state_attack(blackboard, perception):
            self._change_state(AIState.ATTACK)
            return True
        
        def set_state_retreat(blackboard, perception):
            self._change_state(AIState.RETREAT)
            return True
        
        def set_state_search(blackboard, perception):
            self._change_state(AIState.SEARCH)
            return True
        
        def set_state_patrol(blackboard, perception):
            self._change_state(AIState.PATROL)
            return True
        
        # Build behavior tree based on enemy type
        if self.enemy_type == EnemyType.AGGRESSIVE:
            # Aggressive enemies prioritize combat
            root = AIBehaviorTree.Selector([
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(health_low),
                    AIBehaviorTree.Action(set_state_retreat)
                ]),
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(can_see_player),
                    AIBehaviorTree.Condition(player_in_attack_range),
                    AIBehaviorTree.Action(set_state_attack)
                ]),
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(can_see_player),
                    AIBehaviorTree.Action(set_state_chase)
                ]),
                AIBehaviorTree.Action(set_state_patrol)
            ])
        
        elif self.enemy_type == EnemyType.DEFENSIVE:
            # Defensive enemies are more cautious
            root = AIBehaviorTree.Selector([
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(health_low),
                    AIBehaviorTree.Action(set_state_retreat)
                ]),
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(can_see_player),
                    AIBehaviorTree.Condition(player_in_attack_range),
                    AIBehaviorTree.Action(set_state_attack)
                ]),
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(can_see_player),
                    AIBehaviorTree.Action(set_state_search)
                ]),
                AIBehaviorTree.Action(set_state_patrol)
            ])
        
        else:  # Basic and other types
            root = AIBehaviorTree.Selector([
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(can_see_player),
                    AIBehaviorTree.Condition(player_in_attack_range),
                    AIBehaviorTree.Action(set_state_attack)
                ]),
                AIBehaviorTree.Sequence([
                    AIBehaviorTree.Condition(can_see_player),
                    AIBehaviorTree.Action(set_state_chase)
                ]),
                AIBehaviorTree.Action(set_state_patrol)
            ])
        
        return root
    
    def _update_state_machine(self, perception: Dict, obstacles: List[pygame.Rect]) -> Dict[str, Any]:
        """Update AI state machine and return commands."""
        commands = {}
        
        if self.current_state == AIState.IDLE:
            # Wait for a random time, then start patrolling
            if self.state_timer > random.uniform(self.params.idle_time_min, 
                                               self.params.idle_time_max):
                self._change_state(AIState.PATROL)
        
        elif self.current_state == AIState.PATROL:
            # Move between patrol points
            commands.update(self._handle_patrol_state())
        
        elif self.current_state == AIState.SEARCH:
            # Search for the player at last known location
            commands.update(self._handle_search_state(perception))
        
        elif self.current_state == AIState.CHASE:
            # Chase the player
            commands.update(self._handle_chase_state(perception))
        
        elif self.current_state == AIState.ATTACK:
            # Attack the player
            commands.update(self._handle_attack_state(perception))
        
        elif self.current_state == AIState.RETREAT:
            # Retreat from the player
            commands.update(self._handle_retreat_state(perception))
        
        elif self.current_state == AIState.STUNNED:
            # Recover from stun
            if self.state_timer > self.params.stun_recovery:
                self._change_state(AIState.IDLE)
        
        return commands
    
    def _handle_patrol_state(self) -> Dict[str, Any]:
        """Handle patrol state behavior."""
        if not self.patrol_points:
            self._generate_patrol_points()
        
        if self.patrol_points and len(self.patrol_points) > 0:
            target = self.patrol_points[self.current_patrol_index]
            
            # Move towards current patrol point
            dx = target[0] - self.position[0]
            dy = target[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 20:  # Reached patrol point
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
                
                # Brief pause at patrol point
                self._change_state(AIState.IDLE)
            else:
                # Move towards patrol point
                self.target_position = target
                return {'move_towards': target, 'speed': self.params.move_speed}
        
        return {}
    
    def _handle_search_state(self, perception: Dict) -> Dict[str, Any]:
        """Handle search state behavior."""
        if perception['can_see_player']:
            self._change_state(AIState.CHASE)
            return {}
        
        # Move to last known player position
        if perception['last_known_position']:
            target = perception['last_known_position']
            
            dx = target[0] - self.position[0]
            dy = target[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 30:  # Reached search location
                # Search around the area
                if self.state_timer > self.params.search_time:
                    self._change_state(AIState.PATROL)
            else:
                self.target_position = target
                return {'move_towards': target, 'speed': self.params.move_speed}
        
        return {}
    
    def _handle_chase_state(self, perception: Dict) -> Dict[str, Any]:
        """Handle chase state behavior."""
        if not perception['can_see_player']:
            # Lost sight of player
            if perception['last_known_position']:
                self._change_state(AIState.SEARCH)
            else:
                self._change_state(AIState.PATROL)
            return {}
        
        # Check if close enough to attack
        if perception['player_distance'] <= self.params.attack_range:
            self._change_state(AIState.ATTACK)
            return {}
        
        # Chase the player
        player_pos = (perception['player_distance'] * math.cos(perception['player_direction']) + self.position[0],
                     perception['player_distance'] * math.sin(perception['player_direction']) + self.position[1])
        
        self.target_position = player_pos
        return {'move_towards': player_pos, 'speed': self.params.chase_speed}
    
    def _handle_attack_state(self, perception: Dict) -> Dict[str, Any]:
        """Handle attack state behavior."""
        current_time = time.time()
        
        # Check if player is still in range
        if perception['player_distance'] > self.params.attack_range:
            self._change_state(AIState.CHASE)
            return {}
        
        # Check attack cooldown
        if current_time - self.last_attack_time >= self.params.attack_cooldown:
            self.last_attack_time = current_time
            
            # Face the player
            self.facing_direction = perception['player_direction']
            
            return {
                'attack': True,
                'attack_damage': self.params.attack_damage,
                'attack_range': self.params.attack_range,
                'face_direction': perception['player_direction']
            }
        
        return {'face_direction': perception['player_direction']}
    
    def _handle_retreat_state(self, perception: Dict) -> Dict[str, Any]:
        """Handle retreat state behavior."""
        # Move away from player
        if perception['player_distance'] > 0:
            # Calculate retreat direction (opposite of player)
            retreat_direction = perception['player_direction'] + math.pi
            retreat_distance = 100  # Retreat this far
            
            retreat_x = self.position[0] + math.cos(retreat_direction) * retreat_distance
            retreat_y = self.position[1] + math.sin(retreat_direction) * retreat_distance
            
            self.target_position = (retreat_x, retreat_y)
            
            # If health is restored, return to combat
            if self.health / self.max_health > self.params.retreat_threshold + 0.2:
                self._change_state(AIState.CHASE)
            
            return {'move_towards': (retreat_x, retreat_y), 'speed': self.params.retreat_speed}
        
        return {}
    
    def _update_movement(self, dt: float) -> Dict[str, Any]:
        """Update movement physics and return movement commands."""
        if not self.target_position:
            return {}
        
        # Calculate direction to target
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 5:  # Don't move if very close
            # Normalize direction
            move_x = (dx / distance) * self.params.move_speed
            move_y = (dy / distance) * self.params.move_speed
            
            # Update facing direction
            self.facing_direction = math.atan2(dy, dx)
            
            return {
                'velocity': (move_x, move_y),
                'facing_direction': self.facing_direction
            }
        
        return {}
    
    def _generate_patrol_points(self):
        """Generate patrol points around the patrol center."""
        if not hasattr(self, 'patrol_center') or self.patrol_center == (0.0, 0.0):
            self.patrol_center = self.position
        
        # Generate 3-5 patrol points in a circle
        num_points = random.randint(3, 5)
        self.patrol_points = []
        
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            radius = random.uniform(self.params.patrol_radius * 0.5, 
                                   self.params.patrol_radius)
            
            x = self.patrol_center[0] + math.cos(angle) * radius
            y = self.patrol_center[1] + math.sin(angle) * radius
            
            self.patrol_points.append((x, y))
    
    def _change_state(self, new_state: AIState):
        """Change AI state and reset timers."""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_timer = 0.0
            
            # State-specific initialization
            if new_state == AIState.PATROL and not self.patrol_points:
                self._generate_patrol_points()
    
    def take_damage(self, damage: int, source_pos: Tuple[float, float]):
        """Handle taking damage and react accordingly."""
        self.health -= damage
        self.health = max(0, self.health)
        
        # Add noise event at damage location
        self.sensors.add_noise_event(source_pos[0], source_pos[1])
        
        # React to damage
        if self.health <= 0:
            self._change_state(AIState.DYING)
        elif self.current_state not in [AIState.CHASE, AIState.ATTACK]:
            # Become alert when damaged
            self._change_state(AIState.SEARCH)
            self.sensors.last_seen_player_pos = source_pos
            self.sensors.alert_level = AlertLevel.COMBAT
    
    def apply_stun(self, duration: float):
        """Apply stun effect to the enemy."""
        self._change_state(AIState.STUNNED)
        self.params.stun_recovery = duration
    
    def set_patrol_center(self, x: float, y: float):
        """Set the center point for patrol behavior."""
        self.patrol_center = (x, y)
        self.patrol_points = []  # Force regeneration
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about AI state."""
        return {
            'state': self.current_state.value,
            'alert_level': self.sensors.alert_level.value,
            'health': f"{self.health}/{self.max_health}",
            'position': f"({self.position[0]:.1f}, {self.position[1]:.1f})",
            'target': f"({self.target_position[0]:.1f}, {self.target_position[1]:.1f})" if self.target_position else "None",
            'facing': f"{math.degrees(self.facing_direction):.1f}°",
            'patrol_points': len(self.patrol_points),
            'blackboard_keys': list(self.blackboard.data.keys())
        }