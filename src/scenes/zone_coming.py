"""Placeholder gameplay scene until the forest zones exist."""

import pygame

import config
from src.core.scene_manager import Scene


class ZoneComingScene(Scene):
    def __init__(self, scene_manager):
        super().__init__("gameplay")
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)

    def update(self, delta_time: float):
        return None

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["forest_green"])
        title = self.font.render("zone coming", True, config.COLORS["white"])
        hint = self.small_font.render("Esc returns to the menu", True, config.COLORS["black"])
        screen.blit(title, title.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)))
        screen.blit(hint, hint.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50)))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene("main_menu")
