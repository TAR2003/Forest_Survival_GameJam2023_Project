"""Menu, settings, gameplay, pause, and game over share one scene graph."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.game import ForestSurvivalGame


def test_scene_graph_reaches_pause_and_game_over():
    game = ForestSurvivalGame()
    try:
        manager = game.scene_manager
        manager.change_scene("main_menu", transition_duration=0)
        game.step(1 / 60)
        assert manager.get_current_scene_name() == "main_menu"
        assert game.audio_manager.current_music == "theme"

        manager.change_scene("settings", transition_duration=0)
        game.step(1 / 60)
        assert manager.get_current_scene_name() == "settings"

        manager.change_scene("gameplay", transition_duration=0)
        game.step(1 / 60)
        assert manager.get_current_scene_name() == "gameplay"
        assert game.audio_manager.current_music == "ingame"

        manager.change_scene("pause", transition_duration=0)
        game.step(1 / 60)
        pause = manager.current_scene
        assert [label for label, _ in pause.options] == ["Resume", "Settings", "Save", "Main Menu", "Quit"]
        assert game.audio_manager.current_music == "theme"

        manager.change_scene("game_over", transition_duration=0)
        game.step(1 / 60)
        over = manager.current_scene
        assert [label for label, _ in over.options] == ["Continue", "Main Menu"]
        assert game.audio_manager.current_music == "string"
        surface = pygame.Surface((1280, 720))
        over.render(surface)
        pause.render(surface)
    finally:
        game.cleanup()
        pygame.quit()
