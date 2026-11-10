"""Sword damage, shield heights, and death."""

from src.core.input_manager import InputManager
from src.core.save_manager import SaveManager
from src.entities.combat_system import deal_sword_damage
from src.entities.shield_system import projectile_blocked
from src.scenes.gameplay_scene import GameplayScene


def _scene(tmp_path):
    scene = GameplayScene(None, InputManager(), audio_manager=None, save_manager=SaveManager(tmp_path))
    scene.enter_scene(None, {})
    return scene


def test_matching_shield_blocks_and_mismatch_hits(tmp_path):
    scene = _scene(tmp_path)
    scene.player.shield_raised = True
    scene.player.shield_height = "middle"
    assert projectile_blocked(True, "middle", 540)
    assert scene.resolve_projectile(540, 1) == "blocked"
    assert scene.player.health == 3

    scene.player.shield_height = "top"
    assert scene.resolve_projectile(540, 1) == "hit"
    assert scene.player.health == 2


def test_sword_deals_ten_and_zero_health_ends_the_run(tmp_path):
    scene = _scene(tmp_path)
    scene.player.attack_timer = 0.2
    assert deal_sword_damage(30) == 20
    assert scene.strike(30) == 20

    scene.player.health = 1
    scene.player.invulnerable_timer = 0
    scene.player.shield_raised = False
    assert scene.resolve_projectile(610, 1) == "dead"
    assert scene.player.health == 0
    assert scene.get_next_scene()[0] == "game_over"
    assert (tmp_path / "slot_1.json").exists()
    reloaded = SaveManager(tmp_path)
    assert reloaded.load_slot(1)
    assert reloaded.game_data["run"]["health"] == 0
