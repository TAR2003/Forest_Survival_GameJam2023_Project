"""HUD render reads the player and draws a half-health fill."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.gameplay.progression import Progression
from src.ui.hud_system import HUDSystem
from tests.test_inventory import SilentAudio


def test_half_health_fill_ratio():
    pygame.init()
    hud = HUDSystem(None, SilentAudio())
    player = type("Player", (), {
        "health": 50,
        "max_health": 100,
        "stamina": 40,
        "max_stamina": 100,
        "x": 250,
        "weapon_name": "Hunter Sword",
    })()
    zone = {"name": "Whispering Path", "width": 1000, "exit": "owl_clearing"}
    hud.update(0.016, 1280, 720, player=player, progression=Progression(), zone=zone, time_label="00:30")
    surface = pygame.Surface((1280, 720))
    hud.render(surface)
    assert abs(hud.health_bar.fill_ratio - 0.5) < 0.001
    assert hud.zone_name == "Whispering Path"
    assert hud.quest_line
    assert abs(hud.player_ratio - 0.25) < 0.001
