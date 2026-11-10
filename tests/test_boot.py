"""The game window can open, switch scenes, and quit."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.game import ForestSurvivalGame


def test_boot_switches_menu_and_settings_then_quits():
    game = ForestSurvivalGame()
    try:
        for _ in range(3):
            game.step(1 / 60)
        assert game.scene_manager.get_current_scene_name() == "splash"

        game.scene_manager.change_scene("settings", transition_duration=0)
        game.step(1 / 60)
        assert game.scene_manager.get_current_scene_name() == "settings"

        game.scene_manager.change_scene("main_menu", transition_duration=0)
        game.step(1 / 60)
        assert game.scene_manager.get_current_scene_name() == "main_menu"
        labels = [button.text for button in game.scene_manager.current_scene.buttons]
        assert labels == ["Start", "Settings", "Quit"]

        game.audio_manager.play_music("theme", loops=-1)
        first = game.audio_manager.current_music
        game.audio_manager.play_music("theme", loops=-1)
        assert game.audio_manager.current_music == first == "theme"

        game.scene_manager.change_scene("quit")
        game.step(1 / 60)
        assert game.running is False
    finally:
        game.cleanup()
        pygame.quit()
