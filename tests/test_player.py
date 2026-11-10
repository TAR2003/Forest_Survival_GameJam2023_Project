"""Side-view player movement."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.input_manager import InputManager
from src.entities.player_controller import PlayerController, PlayerState, format_time


class ScriptedInput:
    """Holds a set of actions for one player update."""

    def __init__(self):
        self.held = set()
        self.pressed = set()
        self.released = set()

    def hold(self, *actions):
        self.held.update(actions)

    def tap(self, *actions):
        self.pressed.update(actions)
        self.held.update(actions)

    def is_action_held(self, action):
        return action in self.held

    def is_action_just_pressed(self, action):
        return action in self.pressed

    def is_action_just_released(self, action):
        return action in self.released

    def end_frame(self):
        self.pressed.clear()
        self.released.clear()


def test_jump_arc_lands_on_the_ground_line():
    player = PlayerController(100, 500, ScriptedInput(), audio_manager=None)
    ground = 640
    player.y = ground - player.height
    player.on_ground = True
    player.coyote_timer = player.coyote_time
    player.input_manager.tap("jump")
    left_ground = False
    for _ in range(180):
        player.update(1 / 60, ground)
        player.input_manager.end_frame()
        if not player.on_ground:
            left_ground = True
        if left_ground and player.on_ground:
            break
    assert left_ground
    assert player.on_ground
    assert abs(player.feet() - ground) < 1


def test_left_key_does_not_force_an_enemy_jump():
    keys = InputManager()
    pygame.init()
    player = PlayerController(0, 400, keys, audio_manager=None)
    keys.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    player.update(1 / 60, 640)
    assert player.enemy_should_jump is False


def test_attack_lasts_more_than_one_update():
    keys = ScriptedInput()
    player = PlayerController(0, 500, keys, audio_manager=None)
    keys.tap("attack")
    player.update(1 / 60, 640)
    assert player.attacking
    assert player.state == PlayerState.ATTACKING
    keys.end_frame()
    player.update(1 / 60, 640)
    assert player.attacking


def test_timer_is_minutes_and_seconds():
    assert format_time(0) == "00:00"
    assert format_time(125000) == "02:05"
    assert format_time(60000) == "01:00"
