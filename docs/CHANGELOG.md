# Changelog

## Forest Survival RPG

The side-view game that `python main.py` launches. The original jam loop remains at `legacy/original_main.py`.

- Windowed 1280x720 scene engine: splash, main menu, settings, credits, pause, gameplay, and game over.
- Four walkable zones with parallax, exits, an 8-minute day, and clear, rain, or fog.
- Player run, jump, slide, sword hitbox, and a shield that blocks only a matching shot height.
- Danger tree, crocodile, wizard, and ninja boss, with loot.
- Fifteen items, inventory, equipment, three skills, five quests, and achievements stored in a save slot.
- Four NPC conversations. One choice can give an item and one can move a quest.
- HUD for health, stamina, weapon, zone, quest, time of day, and a zone bar.
- Shared bark-panel menus. Theme on menus, ingame in zones, string on game over.
- Easy, normal, and hard damage, with a night damage multiplier. A failed run returns to Whispering Path and keeps meta progress.
- `python deploy.py --check` runs the pytest suite and does not build an executable.
