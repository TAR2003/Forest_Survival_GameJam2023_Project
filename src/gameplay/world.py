"""Side-view zones built from the jam parallax art."""

import json
from pathlib import Path

import pygame

import config


class World:
    def __init__(self, zones_path: Path = None, assets=None):
        self.assets = assets
        path = Path(zones_path) if zones_path else config.DATA_DIR / "zones.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.zones = {zone["id"]: zone for zone in payload["zones"]}
        self.zone = None
        self.zone_id = None
        self.props = []

    def load(self, zone_id: str):
        self.zone = self.zones[zone_id]
        self.zone_id = zone_id
        self.props = []
        spacing = 320
        trees = self.zone.get("trees") or []
        x = 400
        index = 0
        while trees and x < self.width - 200:
            self.props.append({"image": trees[index % len(trees)], "x": x})
            x += spacing
            index += 1

    @property
    def width(self) -> int:
        return int(self.zone["width"])

    @property
    def ground_y(self) -> int:
        return int(self.zone["ground_y"])

    @property
    def name(self) -> str:
        return self.zone["name"]

    def zone_after(self, player_x: float):
        """The next zone id when the player reaches the right edge."""
        if player_x >= self.width - 64:
            return self.zone.get("exit")
        return None

    def render(self, surface: pygame.Surface, camera, assets):
        for layer in self.zone["layers"]:
            self._blit_layer(surface, camera, assets, layer)
        for prop in self.props:
            sprite = assets.image(prop["image"])
            x, y = camera.world_to_screen(prop["x"], self.ground_y - sprite.get_height())
            if -sprite.get_width() < x < config.SCREEN_WIDTH:
                surface.blit(sprite, (x, y))

    def _blit_layer(self, surface, camera, assets, layer):
        sprite = assets.image(layer["image"])
        width = sprite.get_width()
        if width <= 0:
            return
        offset = int(camera.x * layer["speed"]) % width
        y = layer["y"]
        x = -offset
        while x < config.SCREEN_WIDTH:
            surface.blit(sprite, (x, y))
            x += width
