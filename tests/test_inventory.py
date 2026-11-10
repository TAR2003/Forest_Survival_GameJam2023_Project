"""Inventory stacking, use, equip, and save."""

import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.ui.inventory_system import InventorySystem, item_from_record


class SilentAudio:
    def play_sound(self, *args, **kwargs):
        return None


def catalog():
    payload = json.loads(open("data/items.json", encoding="utf-8").read())
    return {record["id"]: record for record in payload["items"]}


def test_stack_use_equip_and_reload():
    pygame.init()
    items = catalog()
    assert len(items) >= 15
    bag = InventorySystem(input_manager=None, audio_manager=SilentAudio(), rows=4, cols=6)
    herb = item_from_record(items["herb"])
    assert bag.add_item(herb, 3) == 0
    assert bag.add_item(item_from_record(items["herb"]), 2) == 0
    assert bag.get_item_count("herb") == 5

    player = type("Player", (), {"health": 1, "max_health": 5, "weapon_damage": 10, "shield_defense": 0})()
    assert bag.add_item(item_from_record(items["potion"]), 1) == 0
    assert bag.use_item("potion", player)
    assert player.health == 3
    assert bag.get_item_count("potion") == 0

    assert bag.add_item(item_from_record(items["iron_sword"]), 1) == 0
    assert bag.equip_item("iron_sword", player)
    assert player.weapon_damage == 16

    saved = bag.to_save()
    other = InventorySystem(None, SilentAudio(), rows=4, cols=6)
    other.load_save(saved, items)
    assert other.get_item_count("herb") == 5
    assert other.equipped_weapon == "iron_sword"
