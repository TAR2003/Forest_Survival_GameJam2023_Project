"""Zone records and the exit into the next zone."""

from src.core.input_manager import InputManager
from src.gameplay.world import World
from src.scenes.gameplay_scene import GameplayScene


def test_four_zones_and_exit_order():
    world = World()
    assert list(world.zones) == [
        "whispering_path",
        "owl_clearing",
        "swamp_crossing",
        "ninja_palace",
    ]
    world.load("whispering_path")
    assert world.zone_after(world.width) == "owl_clearing"
    world.load("owl_clearing")
    assert world.zone_after(world.width) == "swamp_crossing"
    world.load("swamp_crossing")
    assert world.zone_after(world.width) == "ninja_palace"
    world.load("ninja_palace")
    assert world.zone_after(world.width) is None


def test_gameplay_loads_the_next_zone_and_remembers_it(tmp_path):
    from src.core.save_manager import SaveManager

    saves = SaveManager(tmp_path)
    scene = GameplayScene(None, InputManager(), audio_manager=None, save_manager=saves)
    scene.enter_scene(None, {})
    assert scene.world.zone_id == "whispering_path"
    scene.player.x = scene.world.width
    scene.update(1 / 60)
    assert scene.world.zone_id == "owl_clearing"
    assert saves.game_data["run"]["zone"] == "owl_clearing"
    assert scene.day_night.cycle_duration == 8 * 60
