# Forest Survival API

These are the objects the running game is built from.

## ForestSurvivalGame

`src/game.py`

```python
game = ForestSurvivalGame()
game.step(dt)   # one frame, used by tests
game.run()      # window loop until quit
game.cleanup()
```

`step` reads input, updates the current scene, applies a requested scene change, and renders.

## SceneManager

`src/core/scene_manager.py`

```python
scene_manager.register_scene(name, scene)
scene_manager.change_scene(name, data=None, transition_type="fade", transition_duration=0.5)
scene_manager.get_current_scene_name()
```

`change_scene` fades, then makes the named scene current. The name `"quit"` stops the game. A scene can also call `request_scene(name, data)` and the game applies it after the frame.

## PlayerController

`src/entities/player_controller.py`

```python
player = PlayerController(x, y, input_manager, audio_manager, assets=None)
player.update(dt, ground_y=640)
player.attack_rect()          # sword rect while the swing is live, else None
player.take_damage(amount)   # True when health reaches 0
format_time(milliseconds)     # "MM:SS"
```

`enemy_should_jump` stays false. Holding left only moves the player.

## CombatSystem

`src/entities/combat_system.py` and `src/entities/shield_system.py`

```python
deal_sword_damage(health, damage=10)   # default sword is 10
sword_rect(x, y, width, height, facing_right)
projectile_blocked(shield_raised, shield_height, shot_top)
```

A shot is blocked only when the shield is up and its height matches the shot. Equipped weapon damage is read from the player.

## SaveManager

`src/core/save_manager.py`

```python
saves = SaveManager(save_dir)
saves.load_slot(1)          # missing or wrong version loads defaults
saves.save_slot(1)          # JSON plus a backup copy
saves.save_game_data()      # writes the active slot
```

The slot holds the run zone, inventory, skills, quests, and unlocked achievements. Death puts the run back on `whispering_path` and leaves that meta progress in place.
