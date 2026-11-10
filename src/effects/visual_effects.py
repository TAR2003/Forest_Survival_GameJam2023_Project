"""
Forest Survival - Screen shake and flash.

Particle bursts live in src.systems.particle_system. This module only
covers full-screen flash and camera shake.
"""

import random
from typing import List, Optional, Tuple

import pygame

import config


class EffectType:
    """Screen effect names used by the manager."""

    SCREEN_SHAKE = "screen_shake"
    FLASH = "flash"


class ScreenEffect:
    """One full-screen flash or shake."""

    def __init__(self, effect_type: str, duration: float = 1.0):
        self.effect_type = effect_type
        self.duration = max(0.01, duration)
        self.age = 0.0
        self.progress = 0.0
        self.is_alive = True
        self.intensity = 1.0
        self.color = config.COLORS['white']

    def update(self, dt: float):
        if not self.is_alive:
            return
        self.age += dt
        self.progress = min(1.0, self.age / self.duration)
        if self.progress >= 1.0:
            self.is_alive = False

    def render(self, surface: pygame.Surface) -> Tuple[float, float]:
        if not self.is_alive:
            return (0.0, 0.0)
        strength = (1.0 - self.progress) * self.intensity
        if self.effect_type == EffectType.FLASH and strength > 0:
            alpha = int(255 * min(1.0, strength))
            flash = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((*self.color, alpha))
            surface.blit(flash, (0, 0))
            return (0.0, 0.0)
        if self.effect_type == EffectType.SCREEN_SHAKE and strength > 0:
            return (
                random.uniform(-strength, strength),
                random.uniform(-strength, strength),
            )
        return (0.0, 0.0)


class VisualEffectsManager:
    """Tracks active screen flashes and shakes."""

    def __init__(self):
        self.screen_effects: List[ScreenEffect] = []

    def create_screen_effect(
        self,
        effect_type: str,
        duration: float = 1.0,
        intensity: float = 1.0,
        color: Optional[Tuple[int, int, int]] = None,
    ) -> ScreenEffect:
        effect = ScreenEffect(effect_type, duration)
        effect.intensity = intensity
        if color:
            effect.color = color
        self.screen_effects.append(effect)
        return effect

    def flash(self, duration: float = 0.15, color: Optional[Tuple[int, int, int]] = None):
        return self.create_screen_effect(EffectType.FLASH, duration, 0.6, color or config.COLORS['white'])

    def shake(self, duration: float = 0.25, intensity: float = 6.0):
        return self.create_screen_effect(EffectType.SCREEN_SHAKE, duration, intensity)

    def update(self, dt: float):
        self.screen_effects = [effect for effect in self.screen_effects if effect.is_alive or effect.age == 0]
        for effect in self.screen_effects:
            effect.update(dt)
        self.screen_effects = [effect for effect in self.screen_effects if effect.is_alive]

    def render(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> Tuple[float, float]:
        del camera_x, camera_y
        shake_x = 0.0
        shake_y = 0.0
        for effect in self.screen_effects:
            offset_x, offset_y = effect.render(surface)
            shake_x += offset_x
            shake_y += offset_y
        return (shake_x, shake_y)

    def clear_all_effects(self):
        self.screen_effects.clear()
