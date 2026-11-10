"""Config contract used by every game system."""

import importlib
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import config
from src.systems.particle_system import PARTICLE_PRESETS, ParticleSystem

REQUIRED_COLORS = [
    "red", "green", "blue", "yellow", "cyan", "orange", "brown", "dark_blue",
]
REQUIRED_ACTIONS = [
    "move_left", "move_right", "jump", "slide", "attack", "shield",
    "shield_up", "shield_down", "interact", "inventory", "pause",
]
ROOT = Path(__file__).resolve().parents[1]


def _modules_that_import_config():
    modules = []
    for path in sorted((ROOT / "src").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if "import config" not in text:
            continue
        relative = path.relative_to(ROOT).with_suffix("")
        modules.append(".".join(relative.parts))
    return modules


def test_display_player_and_actions():
    assert (config.SCREEN_WIDTH, config.SCREEN_HEIGHT) == (1280, 720)
    assert config.DEFAULT_RESOLUTION == (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    assert config.PLAYER_SPEED == config.PLAYER_MOVE_SPEED
    assert config.PLAYER_JUMP_STRENGTH == config.JUMP_STRENGTH
    assert config.PLAYER_WIDTH > 0
    assert config.PLAYER_HEIGHT > 0
    for name in REQUIRED_COLORS:
        assert name in config.COLORS
        assert len(config.COLORS[name]) == 3
    for action in REQUIRED_ACTIONS:
        assert action in config.DEFAULT_KEYBINDS
    audio = config.DEFAULT_SAVE_DATA["settings"]["audio"]
    assert set(audio) >= {"master", "music", "sfx"}


def test_particle_presets_construct_and_emit():
    assert "player_jump" in PARTICLE_PRESETS
    assert "blood_splatter" in PARTICLE_PRESETS
    for preset in PARTICLE_PRESETS.values():
        assert preset.count > 0
        assert len(preset.color) == 3
    system = ParticleSystem(max_particles=32)
    system.emit_burst(10, 20, "player_jump")
    system.emit_burst(10, 20, PARTICLE_PRESETS["sword_hit"])
    assert system.get_particle_count() == (
        PARTICLE_PRESETS["player_jump"].count + PARTICLE_PRESETS["sword_hit"].count
    )


def test_config_importers_load():
    failures = []
    for module_name in _modules_that_import_config():
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - reported below
            failures.append(f"{module_name}: {type(exc).__name__}: {exc}")
    assert failures == []
