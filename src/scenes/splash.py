"""Short skippable splash before the main menu."""

import pygame

import config
from src.core.scene_manager import Scene


class SplashScene(Scene):
    def __init__(self, scene_manager):
        super().__init__("splash")
        self.scene_manager = scene_manager
        self.elapsed = 0.0
        self.font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 28)

    def update(self, delta_time: float):
        self.elapsed += delta_time
        if self.elapsed >= 1.2:
            self.request_scene("main_menu")

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["dark_green"])
        title = self.font.render("Forest Survival", True, config.COLORS["white"])
        hint = self.small_font.render("Press any key", True, config.COLORS["leaf_green"])
        screen.blit(title, title.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 20)))
        screen.blit(hint, hint.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 40)))

    def handle_event(self, event: pygame.event.Event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.request_scene("main_menu")
