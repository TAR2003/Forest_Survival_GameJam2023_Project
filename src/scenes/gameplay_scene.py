"""Walkable forest zones."""

import pygame

import config
from src.core.assets import AssetLoader
from src.core.scene_manager import Scene
from src.effects.visual_effects import VisualEffectsManager
from src.entities.combat_system import CombatSystem, deal_sword_damage
from src.entities.enemies import spawn_for_zone
from src.entities.player_controller import PlayerController, format_time
from src.entities.shield_system import projectile_blocked
from src.gameplay.camera import Camera
from src.gameplay.world import World
from src.scenes.world_scene import DayNightCycle, TimeOfDay, WeatherSystem, WeatherType
from src.systems.particle_system import ParticleSystem
from src.ui.inventory_system import InventorySystem
from src.ui.dialogue_system import DialogueState, DialogueSystem
from src.gameplay.progression import Progression


class _QuietAudio:
    def play_sound(self, *args, **kwargs):
        return None
    def play_music(self, *args, **kwargs):
        return None


WEATHER = {
    "clear": WeatherType.CLEAR,
    "rain": WeatherType.RAIN,
    "fog": WeatherType.FOG,
}


class GameplayScene(Scene):
    def __init__(self, scene_manager, input_manager, audio_manager, save_manager=None, assets=None):
        super().__init__("gameplay")
        self.scene_manager = scene_manager
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        self.save_manager = save_manager
        self.assets = assets or AssetLoader()
        self.world = World(assets=self.assets)
        self.player = PlayerController(120, 400, input_manager, audio_manager, self.assets)
        self.combat = CombatSystem(audio_manager)
        self.player.weapon_damage = self.combat.equipped_weapon.base_damage
        if self.player.weapon_damage != 10:
            self.player.weapon_damage = 10
        self.effects = VisualEffectsManager()
        self.particles = ParticleSystem(max_particles=64)
        if not pygame.get_init():
            pygame.init()
        self.inventory = InventorySystem(input_manager, audio_manager or _QuietAudio(), rows=4, cols=6)
        self.progression = Progression()
        self.dialogue = DialogueSystem(input_manager, audio_manager or _QuietAudio())
        self.dialogue.bind(self.progression, self.inventory)
        self.dialogue.load_file()
        self.dialogue.assets = assets
        self.camera = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 3400)
        self.day_night = DayNightCycle()
        self.day_night.cycle_duration = 8 * 60
        self.weather = WeatherSystem()
        self.enemies = []
        self.loot = []
        self.elapsed_ms = 0
        self.font = None
        self._entered = False

    def enter_scene(self, previous_scene=None, data=None):
        super().enter_scene(previous_scene, data)
        zone_id = "whispering_path"
        if data and data.get("zone"):
            zone_id = data["zone"]
        elif self.save_manager:
            zone_id = self.save_manager.game_data.get("run", {}).get("zone", zone_id)
        if self.save_manager:
            self.progression.load(self.save_manager.game_data.get("progression"))
        self.progression.apply_to_player(self.player)
        self._load_zone(zone_id, reset_player=True)
        if self.audio_manager:
            self.audio_manager.play_music("ingame", loops=-1)
        self._entered = True

    def _load_zone(self, zone_id: str, reset_player: bool):
        self.world.load(zone_id)
        self.camera.zone_width = self.world.width
        weather_name = self.world.zone.get("weather", "clear")
        self.weather.current_weather = WEATHER.get(weather_name, WeatherType.CLEAR)
        self.enemies = spawn_for_zone(self.world.zone)
        if reset_player:
            self.player.x = 120
            self.player.y = self.world.ground_y - self.player.height
            self.player.vel_x = 0
            self.player.vel_y = 0
        if self.save_manager:
            run = self.save_manager.game_data.setdefault("run", {})
            run["zone"] = zone_id

    def update(self, delta_time: float):
        if not self._entered:
            self._load_zone("whispering_path", reset_player=True)
            self._entered = True
        if self.input_manager.is_action_just_pressed("inventory") and self.dialogue.state == DialogueState.HIDDEN:
            self.open_inventory()
        if self.input_manager.is_action_just_pressed("pause"):
            self.request_scene("main_menu")
            return
        if self.dialogue.state != DialogueState.HIDDEN:
            self.dialogue.update(delta_time)
            if self.input_manager.is_action_just_pressed("interact"):
                self.dialogue.advance_dialogue()
        else:
            speaker = self._nearby_speaker()
            if speaker and self.input_manager.is_action_just_pressed("interact"):
                self.dialogue.start_dialogue(speaker["start"])
            else:
                self.player.update(delta_time, self.world.ground_y)
                self._update_enemies(delta_time)
        self.player.x = max(0, min(self.player.x, self.world.width - self.player.width))
        next_zone = self.world.zone_after(self.player.x + self.player.width)
        if next_zone:
            self._load_zone(next_zone, reset_player=True)
        self.camera.follow(self.player.x, self.player.y)
        self.effects.update(delta_time)
        self.particles.update(delta_time)
        self.day_night.update(delta_time)
        self.elapsed_ms += int(delta_time * 1000)
        self.progression.add_time(delta_time)
        if self.day_night.time_of_day == TimeOfDay.NIGHT and not getattr(self, "_night_noted", False):
            self.progression.note("night")
            self._night_noted = True

    def _update_enemies(self, delta_time: float):
        boss = any(enemy.kind == "ninja" and enemy.alive for enemy in self.enemies)
        attack = self.player.attack_rect()
        for enemy in self.enemies:
            enemy.update(delta_time, self.player, paused=boss and enemy.kind != "ninja")
            if attack and enemy.alive and attack.colliderect(enemy.rect()):
                drop = enemy.hit(self.player.weapon_damage + self.progression.damage_bonus())
                if drop:
                    self.loot.append(drop)
                    self.particles.emit_burst(enemy.x, enemy.y, "enemy_death")
                    self.progression.note("kill")
                    if enemy.kind == "ninja":
                        self.progression.note("ninja")
                    elif enemy.kind == "crocodile":
                        self.progression.complete_quest("clear_swamp")
            if enemy.kind == "ninja":
                for shot in list(enemy.projectiles):
                    if abs(shot["x"] - self.player.x) < 40:
                        self.resolve_projectile(shot["top"], enemy.damage)
                        enemy.projectiles.remove(shot)

    def open_inventory(self):
        self.inventory.toggle_inventory()

    def _nearby_speaker(self):
        for speaker in getattr(self.dialogue, "speakers", []):
            if speaker["zone"] != self.world.zone_id:
                continue
            if abs(self.player.x - speaker["x"]) < 90:
                return speaker
        return None

    def resolve_projectile(self, shot_top: int, damage: int = 1) -> str:
        """Block a shot only at the matching shield height. Otherwise hurt the player."""
        if projectile_blocked(self.player.shield_raised, self.player.shield_height, shot_top):
            self.progression.note("block")
            return "blocked"
        return self._hurt(damage)

    def strike(self, target_health: int):
        """Apply the equipped sword to a target while the attack hitbox is live."""
        if self.player.attack_rect() is None:
            return target_health
        remaining = deal_sword_damage(target_health, self.player.weapon_damage)
        if remaining < target_health:
            rect = self.player.attack_rect()
            self.effects.shake(0.12, 4)
            self.particles.emit_burst(rect.centerx, rect.centery, "sword_hit")
        return remaining

    def _hurt(self, damage: int) -> str:
        died = self.player.take_damage(damage)
        if damage > 0 and self.player.invulnerable_timer > 0:
            self.effects.shake(0.18, 6)
        if died:
            self._record_death()
            self.request_scene("game_over")
            return "dead"
        return "hit"

    def _record_death(self):
        if not self.save_manager:
            return
        run = self.save_manager.game_data.setdefault("run", {})
        run["health"] = 0
        run["zone"] = self.world.zone_id
        self._persist_progress()
        self.save_manager.save_game_data()

    def _persist_progress(self):
        if not self.save_manager:
            return
        self.save_manager.game_data["progression"] = self.progression.to_save()
        self.save_manager.game_data["inventory"] = self.inventory.to_save()

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["black"])
        self.world.render(screen, self.camera, self.assets)
        self.player.render(screen, self.camera)
        sprites = {
            "danger_tree": "trees/dangertree1.png",
            "crocodile": "croc.png",
            "wizard": "wizard.png",
            "ninja": "ninja.png",
        }
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            image = self.assets.image(sprites[enemy.kind])
            screen.blit(image, self.camera.world_to_screen(enemy.x, enemy.y))
        self._overlay_weather(screen)
        self.day_night.apply_lighting(screen)
        if self.font is None:
            self.font = pygame.font.Font(None, 32)
        label = self.font.render(
            f"{self.world.name}  {format_time(self.elapsed_ms)}",
            True,
            config.COLORS["white"],
        )
        screen.blit(label, (24, 16))

    def _overlay_weather(self, screen: pygame.Surface):
        if self.weather.current_weather == WeatherType.RAIN:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((80, 120, 160, 40))
            screen.blit(overlay, (0, 0))
        elif self.weather.current_weather == WeatherType.FOG:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((180, 180, 180, 70))
            screen.blit(overlay, (0, 0))

    def handle_event(self, event: pygame.event.Event):
        return None
