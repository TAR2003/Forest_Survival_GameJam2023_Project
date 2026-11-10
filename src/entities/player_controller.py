"""Side-view player: run, jump, slide, sword, and a three-height shield."""

from enum import Enum

import pygame

import config
from src.core.assets import AssetLoader


class PlayerState(Enum):
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
    GROUNDED = "grounded"
    AIRBORNE = "airborne"
    DASHING = "dashing"


def format_time(milliseconds: int) -> str:
    """Return a real MM:SS clock from milliseconds."""
    total_seconds = max(0, int(milliseconds) // 1000)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


class PlayerController:
    """The body the rest of the game moves and draws."""

    def __init__(self, x: float, y: float, input_manager, audio_manager, assets: AssetLoader = None):
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        self.assets = assets or AssetLoader()

        self.x = float(x)
        self.y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT
        self.move_speed = 240 + config.PLAYER_SPEED
        self.jump_speed = abs(config.PLAYER_JUMP_STRENGTH) * 16
        self.gravity = 1500
        self.coyote_time = config.COYOTE_TIME
        self.jump_buffer_time = config.JUMP_BUFFER_TIME
        self.slide_time = config.SLIDE_DURATION / 60
        self.attack_time = 0.28

        self.on_ground = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.slide_timer = 0.0
        self.attack_timer = 0.0
        self.facing_right = True
        self.shield_raised = False
        self.shield_height = "middle"
        self.enemy_should_jump = False
        self.state = PlayerState.STANDING
        self.movement_state = MovementState.GROUNDED
        self.health = config.PLAYER_START_HEALTH
        self.max_health = config.PLAYER_MAX_HEALTH
        self.stamina = 100.0
        self.stamina_regen = 25.0
        self.base_stamina_regen = 25.0
        self.max_stamina = 100.0
        self.invulnerable_timer = 0.0
        self.weapon_damage = 10
        self._was_jump_held = False

        self._frames = {
            "stand": "player/playerstanding.png",
            "run": "player/playerrunright.png",
            "jump": "player/playeronairright.png",
            "duck": "player/playerduck.png",
            "shield": "player/SHIELD.png",
            "sword": "sword.png",
        }

    @property
    def attacking(self) -> bool:
        return self.attack_timer > 0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def feet(self) -> float:
        return self.y + self.height

    def _sound(self, name: str):
        if self.audio_manager:
            self.audio_manager.play_sound(name, volume=0.4, category="sfx")

    def update(self, dt: float, ground_y: float = 640):
        self.enemy_should_jump = False
        self._read_input()
        self._apply_horizontal()
        self._apply_jump()
        self.vel_y += self.gravity * dt
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self._collide_ground(ground_y)
        self._tick_timers(dt)
        self._pick_state()

    def _read_input(self):
        keys = self.input_manager
        self._left = keys.is_action_held("move_left")
        self._right = keys.is_action_held("move_right")
        self._jump_held = keys.is_action_held("jump")
        if keys.is_action_just_pressed("jump"):
            self.jump_buffer_timer = self.jump_buffer_time
        if keys.is_action_just_pressed("slide") and self.on_ground and self.stamina >= 15:
            self.stamina -= 15
            self.slide_timer = self.slide_time
            self._sound("slide")
        if keys.is_action_just_pressed("attack") and self.stamina >= 20 and self.attack_timer <= 0:
            self.stamina -= 20
            self.attack_timer = self.attack_time
            self.state = PlayerState.ATTACKING
            self._sound("attack")
        if keys.is_action_just_pressed("shield"):
            self.shield_raised = not self.shield_raised
        if keys.is_action_just_pressed("shield_up"):
            self.shield_height = "top" if self.shield_height == "middle" else "middle"
        if keys.is_action_just_pressed("shield_down"):
            self.shield_height = "bottom" if self.shield_height == "middle" else "middle"

    def _apply_horizontal(self):
        if self.slide_timer > 0 and self.on_ground:
            direction = 1 if self.facing_right else -1
            self.vel_x = direction * self.move_speed * 1.15
            return
        if self._left and not self._right:
            self.vel_x = -self.move_speed
            self.facing_right = False
        elif self._right and not self._left:
            self.vel_x = self.move_speed
            self.facing_right = True
        else:
            self.vel_x = 0

    def _apply_jump(self):
        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
            self.vel_y = -self.jump_speed
            self.on_ground = False
            self.coyote_timer = 0
            self.jump_buffer_timer = 0
            self.movement_state = MovementState.AIRBORNE
            self._sound("jump")
        elif self._was_jump_held and not self._jump_held and self.vel_y < 0:
            self.vel_y *= 0.45
        self._was_jump_held = self._jump_held

    def _collide_ground(self, ground_y: float):
        if self.feet() >= ground_y:
            self.y = ground_y - self.height
            if self.vel_y > 0:
                self.vel_y = 0
            if not self.on_ground:
                self.on_ground = True
            self.movement_state = MovementState.GROUNDED
            self.coyote_timer = self.coyote_time
        else:
            if self.on_ground:
                self.coyote_timer = self.coyote_time
            self.on_ground = False
            self.movement_state = MovementState.AIRBORNE

    def _tick_timers(self, dt: float):
        self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)
        if not self.on_ground:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)
        self.slide_timer = max(0.0, self.slide_timer - dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
        if self.stamina < self.max_stamina and self.attack_timer <= 0:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen * dt)

    def attack_rect(self):
        from src.entities.combat_system import sword_rect
        if not self.attacking:
            return None
        return sword_rect(self.x, self.y, self.width, self.height, self.facing_right)

    def take_damage(self, amount: int) -> bool:
        """Apply damage unless invulnerable. Returns True when health reaches 0."""
        if amount <= 0 or self.invulnerable_timer > 0 or self.health <= 0:
            return self.health <= 0
        self.health = max(0, self.health - amount)
        self.invulnerable_timer = 0.7
        self.state = PlayerState.DYING if self.health <= 0 else PlayerState.HURT
        return self.health <= 0

    def _pick_state(self):
        if self.attacking:
            self.state = PlayerState.ATTACKING
        elif self.slide_timer > 0:
            self.state = PlayerState.DUCKING
        elif not self.on_ground:
            self.state = PlayerState.JUMPING if self.vel_y < 0 else PlayerState.FALLING
        elif self.shield_raised and self.vel_x == 0:
            self.state = PlayerState.SHIELDING
        elif self.vel_x > 0:
            self.state = PlayerState.RUNNING_RIGHT
        elif self.vel_x < 0:
            self.state = PlayerState.RUNNING_LEFT
        else:
            self.state = PlayerState.STANDING

    def render(self, surface: pygame.Surface, camera=None):
        frame_key = "stand"
        if self.state == PlayerState.DUCKING:
            frame_key = "duck"
        elif self.state in (PlayerState.JUMPING, PlayerState.FALLING):
            frame_key = "jump"
        elif self.state in (PlayerState.RUNNING_LEFT, PlayerState.RUNNING_RIGHT):
            frame_key = "run"
        sprite = self.assets.image(self._frames[frame_key])
        draw_x = self.x
        draw_y = self.y + self.height - sprite.get_height()
        if camera:
            draw_x, draw_y = camera.world_to_screen(draw_x, draw_y)
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (int(draw_x), int(draw_y)))
        if self.shield_raised and self.state != PlayerState.DUCKING:
            shield = self.assets.image(self._frames["shield"])
            lift = {"top": -36, "middle": -8, "bottom": 18}[self.shield_height]
            shield_x = self.x + (self.width - 10 if self.facing_right else -20)
            shield_y = self.y + lift
            if camera:
                shield_x, shield_y = camera.world_to_screen(shield_x, shield_y)
            surface.blit(shield, (int(shield_x), int(shield_y)))
        if self.attacking:
            sword = self.assets.image(self._frames["sword"])
            sword_x = self.x + (self.width if self.facing_right else -sword.get_width())
            sword_y = self.y + 20
            if camera:
                sword_x, sword_y = camera.world_to_screen(sword_x, sword_y)
            surface.blit(sword, (int(sword_x), int(sword_y)))
