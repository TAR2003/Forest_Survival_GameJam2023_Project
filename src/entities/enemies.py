"""Forest enemies. Each one has health, a state, and a drop."""

import pygame

ENEMY_STATS = {
    "danger_tree": {"health": 30, "damage": 1, "speed": 0, "drop": "herbs", "height": 140},
    "crocodile": {"health": 24, "damage": 1, "speed": 90, "drop": "claws", "height": 48},
    "wizard": {"health": 18, "damage": 1, "speed": 80, "drop": "weapon_scraps", "height": 70},
    "ninja": {"health": 50, "damage": 1, "speed": 40, "drop": "palace_key", "height": 96},
}


class Enemy:
    def __init__(self, kind: str, x: float, y: float):
        stats = ENEMY_STATS[kind]
        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.health = stats["health"]
        self.damage = stats["damage"]
        self.speed = stats["speed"]
        self.drop = stats["drop"]
        self.height = stats["height"]
        self.width = 64
        self.state = "idle"
        self.alive = True
        self.hurt_timer = 0.0
        self.attack_timer = 0.0
        self.projectiles = []
        self.steps = 0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def hit(self, amount: int):
        if not self.alive or self.hurt_timer > 0:
            return None
        self.health -= amount
        self.hurt_timer = 0.35
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.state = "dead"
            return self.drop
        self.state = "recover"
        return None

    def update(self, dt: float, player, paused: bool = False):
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        if not self.alive or paused:
            return
        self.steps += 1
        if self.kind == "wizard":
            self._update_wizard(dt, player)
        elif self.kind == "crocodile":
            self._update_crocodile(dt, player)
        elif self.kind == "danger_tree":
            self._update_tree(dt, player)
        elif self.kind == "ninja":
            self._update_ninja(dt, player)

    def _update_tree(self, dt, player):
        self.attack_timer += dt
        self.state = "attack" if self.attack_timer % 2.4 > 1.4 else "idle"

    def _update_crocodile(self, dt, player):
        if abs(player.x - self.x) < 420:
            self.state = "approach"
            self.x -= self.speed * dt
        else:
            self.state = "idle"

    def _update_wizard(self, dt, player):
        """Advance exactly once per update."""
        self.state = "approach"
        self.x -= self.speed * dt

    def _update_ninja(self, dt, player):
        self.state = "attack"
        self.attack_timer += dt
        if self.attack_timer >= 1.4:
            self.attack_timer = 0
            top = (480, 540, 610)[len(self.projectiles) % 3]
            self.projectiles.append({"x": self.x, "top": top})
        for shot in self.projectiles:
            shot["x"] -= 220 * dt
        self.projectiles = [shot for shot in self.projectiles if shot["x"] > -40]


def spawn_for_zone(zone: dict, difficulty: str = "normal"):
    from src.effects.gameplay_polish import spawn_copies

    enemies = []
    x = 900
    copies = spawn_copies(difficulty)
    for kind in zone.get("enemies", []):
        if kind not in ENEMY_STATS:
            continue
        ground = zone["ground_y"]
        height = ENEMY_STATS[kind]["height"]
        y = 420 if kind == "wizard" else ground - height
        for _ in range(copies):
            enemies.append(Enemy(kind, x, y))
            x += 700
    return enemies
