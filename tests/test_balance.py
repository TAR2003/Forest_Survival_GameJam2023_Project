"""Difficulty scales and the jam bugs that must stay fixed."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.input_manager import InputManager
from src.core.save_manager import SaveManager
from src.effects.gameplay_polish import damage_multiplier, expected_clear_minutes, spawn_copies
from src.entities.enemies import Enemy
from src.entities.player_controller import PlayerController, format_time
from src.entities.shield_system import projectile_blocked
from src.scenes.gameplay_scene import GameplayScene


class Held:
    def __init__(self, held=None, pressed=None):
        self.held = held or set()
        self.pressed = pressed or set()

    def is_action_held(self, name):
        return name in self.held

    def is_action_just_pressed(self, name):
        return name in self.pressed

    def is_action_just_released(self, name):
        return False


def test_difficulty_and_night_damage():
    assert damage_multiplier("normal") == 1
    assert damage_multiplier("easy") == 0.75
    assert damage_multiplier("hard") == 1.35
    assert damage_multiplier("normal", night=True) == 1.25
    assert spawn_copies("hard") == 2
    assert spawn_copies("normal") == 1
    assert 20 <= expected_clear_minutes("normal") <= 30


def test_jam_regressions_and_death_save(tmp_path):
    assert projectile_blocked(True, "middle", 540)
    assert not projectile_blocked(True, "top", 540)
    wizard = Enemy("wizard", 100, 420)
    before = wizard.x
    wizard.update(0.5, type("P", (), {"x": 0})())
    assert wizard.x == before - wizard.speed * 0.5

    player = PlayerController(0, 0, Held(pressed={"attack"}), None)
    player.update(1 / 60, ground_y=1000)
    assert player.attacking
    player.update(1 / 60, ground_y=1000)
    assert player.attacking
    assert format_time(125000) == "02:05"

    left = PlayerController(0, 0, Held(held={"move_left"}), None)
    left.update(1 / 60, ground_y=1000)
    assert left.enemy_should_jump is False

    pygame.init()
    saves = SaveManager(tmp_path)
    scene = GameplayScene(None, InputManager(), audio_manager=None, save_manager=saves)
    scene.enter_scene(None, {"zone": "ninja_palace"})
    scene.progression.unlock("first_kill")
    scene._record_death()
    assert saves.game_data["run"]["zone"] == "whispering_path"
    assert "first_kill" in saves.game_data["progression"]["unlocked"]
