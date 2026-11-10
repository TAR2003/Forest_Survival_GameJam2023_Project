"""Herb quest XP, reward item, and a save that keeps the achievement."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.save_manager import SaveManager
from src.gameplay.progression import Progression
from src.ui.inventory_system import InventorySystem, item_from_record
from tests.test_inventory import SilentAudio, catalog


def test_herb_quest_survives_reload(tmp_path):
    pygame.init()
    items = catalog()
    bag = InventorySystem(None, SilentAudio(), rows=4, cols=6)
    bag.add_item(item_from_record(items["herb"]), 3)
    progress = Progression()
    assert progress.turn_in_herbs(bag)
    assert bag.get_item_count("potion") == 1
    assert progress.total_xp > 0
    assert progress.quests["gather_herbs"] == "complete"
    assert "herb_gathered" in progress.unlocked

    saves = SaveManager(tmp_path)
    saves.game_data["progression"] = progress.to_save()
    saves.game_data["inventory"] = bag.to_save()
    assert saves.save_slot(1)

    again = SaveManager(tmp_path)
    assert again.load_slot(1)
    loaded = Progression()
    loaded.load(again.game_data["progression"])
    assert loaded.quests["gather_herbs"] == "complete"
    assert "herb_gathered" in loaded.unlocked
    restored = InventorySystem(None, SilentAudio(), rows=4, cols=6)
    restored.load_save(again.game_data["inventory"], items)
    assert restored.get_item_count("potion") == 1


def test_skill_point_and_survival_achievement():
    progress = Progression()
    progress.grant_xp(100)
    assert progress.level == 2
    assert progress.spend_point("blade")
    assert progress.damage_bonus() == 2
    progress.add_time(30)
    assert "first_steps" in progress.unlocked
    assert progress.pop_toast()
