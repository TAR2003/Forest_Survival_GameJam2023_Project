"""Input, audio, settings, and save slots."""

import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.audio_manager import AudioManager
from src.core.input_manager import InputManager
from src.core.save_manager import SaveManager
from src.core.scene_manager import SceneManager
from src.scenes.settings_menu import SettingsCategory, SettingsScene
from src.settings import SettingsManager


def test_held_press_release_mouse_and_rebind():
    pygame.init()
    manager = InputManager()
    manager.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert manager.is_action_held("move_left")
    assert manager.is_action_just_pressed("move_left")
    manager.update(0.016)
    assert manager.is_action_held("move_left")
    assert not manager.is_action_just_pressed("move_left")

    manager.handle_event(pygame.event.Event(pygame.KEYUP, key=pygame.K_a))
    assert manager.is_action_just_released("move_left")
    assert not manager.is_action_held("move_left")

    manager.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(12, 34), rel=(0, 0), buttons=(0, 0, 0)))
    assert manager.get_mouse_position() == (12, 34)

    assert manager.set_keybind("jump", pygame.K_w)
    manager.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
    assert manager.is_action_just_pressed("jump")


def test_music_does_not_restart_and_bad_wav_is_skipped(tmp_path):
    pygame.init()
    pygame.mixer.init()
    audio = AudioManager()
    audio.current_music = "theme"
    loads = []
    original_load = pygame.mixer.music.load
    original_busy = pygame.mixer.music.get_busy
    pygame.mixer.music.load = lambda path: loads.append(path)
    pygame.mixer.music.get_busy = lambda: True
    try:
        audio.play_music("theme", loops=-1)
        assert loads == []
        assert audio.current_music == "theme"
    finally:
        pygame.mixer.music.load = original_load
        pygame.mixer.music.get_busy = original_busy

    bad = tmp_path / "broken.wav"
    bad.write_bytes(b"this is not a wav")
    assert audio._load_sound_file(bad) is False
    assert "broken" not in audio.sounds


def test_settings_round_trip(tmp_path):
    pygame.init()
    pygame.mixer.init()
    settings_path = tmp_path / "settings.json"
    settings = SettingsManager(settings_path)
    audio = AudioManager()
    scene = SettingsScene(SceneManager(), InputManager(), audio, settings)
    scene.controls[SettingsCategory.AUDIO]["master"].current_value = 25
    scene.controls[SettingsCategory.AUDIO]["music"].current_value = 50
    scene.controls[SettingsCategory.AUDIO]["sfx"].current_value = 75
    scene.controls[SettingsCategory.GRAPHICS]["fullscreen"].current_value = True
    scene.controls[SettingsCategory.GRAPHICS]["vsync"].current_value = False
    scene._apply_settings()

    reloaded = SettingsManager(settings_path)
    assert reloaded.load_settings()
    assert reloaded.get_setting("audio.master") == 0.25
    assert reloaded.get_setting("audio.music") == 0.5
    assert reloaded.get_setting("audio.sfx") == 0.75
    assert reloaded.get_setting("video.fullscreen") is True
    assert reloaded.get_setting("video.vsync") is False


def test_save_slot_survives_a_new_manager(tmp_path):
    first = SaveManager(tmp_path)
    first.game_data["player"]["name"] = "Ash"
    assert first.save_slot(2)
    assert (tmp_path / "slot_2.json").exists()

    second = SaveManager(tmp_path)
    assert second.load_slot(2)
    assert second.game_data["player"]["name"] == "Ash"

    second.game_data["player"]["name"] = "Birch"
    assert second.save_slot(2)
    assert (tmp_path / "backups" / "slot_2.json").exists()

    third = SaveManager(tmp_path)
    stale = {"version": "0.0.1", "player": {"name": "Gone"}}
    (tmp_path / "slot_1.json").write_text(json.dumps(stale), encoding="utf-8")
    assert third.load_slot(1) is False
    assert third.game_data["player"]["name"] == "Player"
