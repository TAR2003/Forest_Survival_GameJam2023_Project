"""Walkable forest zones."""

import pygame

import config
from src.core.assets import AssetLoader
from src.core.scene_manager import Scene
from src.entities.player_controller import PlayerController, format_time
from src.gameplay.camera import Camera
from src.gameplay.world import World
from src.scenes.world_scene import DayNightCycle, WeatherSystem, WeatherType


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
        self.camera = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 3400)
        self.day_night = DayNightCycle()
        self.day_night.cycle_duration = 8 * 60
        self.weather = WeatherSystem()
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
        self._load_zone(zone_id, reset_player=True)
        if self.audio_manager:
            self.audio_manager.play_music("ingame", loops=-1)
        self._entered = True

    def _load_zone(self, zone_id: str, reset_player: bool):
        self.world.load(zone_id)
        self.camera.zone_width = self.world.width
        weather_name = self.world.zone.get("weather", "clear")
        self.weather.current_weather = WEATHER.get(weather_name, WeatherType.CLEAR)
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
        if self.input_manager.is_action_just_pressed("pause"):
            self.request_scene("main_menu")
            return
        self.player.update(delta_time, self.world.ground_y)
        self.player.x = max(0, min(self.player.x, self.world.width - self.player.width))
        next_zone = self.world.zone_after(self.player.x + self.player.width)
        if next_zone:
            self._load_zone(next_zone, reset_player=True)
        self.camera.follow(self.player.x, self.player.y)
        self.day_night.update(delta_time)
        self.elapsed_ms += int(delta_time * 1000)

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["black"])
        self.world.render(screen, self.camera, self.assets)
        self.player.render(screen, self.camera)
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
