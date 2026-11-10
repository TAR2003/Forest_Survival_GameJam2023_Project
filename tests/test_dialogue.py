"""Dialogue choices grant items and quest flags."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.gameplay.progression import Progression
from src.ui.dialogue_system import DialogueState, DialogueSystem
from src.ui.inventory_system import InventorySystem
from tests.test_inventory import SilentAudio


def test_herb_choice_sets_flag_and_inventory():
    pygame.init()
    bag = InventorySystem(None, SilentAudio(), rows=4, cols=6)
    progress = Progression()
    talk = DialogueSystem(None, SilentAudio())
    talk.bind(progress, bag)
    talk.load_file()
    talk.start_dialogue("owl_hello")
    assert talk.dialogue_box.is_typing()
    talk.dialogue_box._update_animations(0.05)
    assert talk.dialogue_box.displayed_text
    assert len(talk.dialogue_box.displayed_text) < len(talk.dialogue_box.current_text)
    talk.choose(0)
    assert progress.flags["herb_offer"] is True
    assert progress.quests["speak_owl"] == "complete"
    assert progress.active_quest == "gather_herbs"
    assert bag.get_item_count("herb") == 3
    talk.choose(0)
    assert talk.state == DialogueState.HIDDEN
