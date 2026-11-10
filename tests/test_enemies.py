"""Enemy health, wizard stepping, and ninja shots."""

from src.entities.enemies import ENEMY_STATS, Enemy
from src.entities.shield_system import projectile_blocked


def test_each_enemy_can_be_killed_and_drops_loot():
    for kind, stats in ENEMY_STATS.items():
        enemy = Enemy(kind, 100, 100)
        drop = None
        while enemy.alive:
            drop = enemy.hit(stats["health"])
        assert enemy.state == "dead"
        assert drop == stats["drop"]


def test_wizard_moves_once_per_update():
    wizard = Enemy("wizard", 800, 420)
    before = wizard.x
    wizard.update(1, player=type("P", (), {"x": 100})())
    assert wizard.x == before - wizard.speed
    assert wizard.steps == 1


def test_wrong_shield_height_does_not_block_a_ninja_shot():
    assert projectile_blocked(True, "top", 610) is False
    assert projectile_blocked(True, "bottom", 610) is True


def test_other_enemies_pause_while_the_ninja_fights():
    tree = Enemy("danger_tree", 0, 0)
    ninja = Enemy("ninja", 400, 0)
    player = type("P", (), {"x": 100})()
    tree.update(1, player, paused=True)
    ninja.update(1, player, paused=False)
    assert tree.steps == 0
    assert ninja.steps == 1
