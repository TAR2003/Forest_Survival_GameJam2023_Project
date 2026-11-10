"""Game over screen. The run summary arrives with later tickets."""

import pygame

import config
from src.core.scene_manager import Scene


class GameOverScene(Scene):
    def __init__(self, scene_manager):
        super().__init__("game_over")
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 32)

    def update(self, delta_time: float):
        return None

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["black"])
        title = self.font.render("Game Over", True, config.COLORS["red"])
        hint = self.small_font.render("Click or press Enter to return", True, config.COLORS["white"])
        screen.blit(title, title.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 20)))
        screen.blit(hint, hint.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50)))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN or (
            event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE)
        ):
            self.request_scene("main_menu")
