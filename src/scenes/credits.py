"""Short credits for the forest."""

import pygame

import config
from src.core.scene_manager import Scene
from src.ui.forest_ui import panel


class CreditsScene(Scene):
    def __init__(self, scene_manager, audio_manager):
        super().__init__("credits")
        self.scene_manager = scene_manager
        self.audio_manager = audio_manager
        self.font = pygame.font.Font(None, 36)
        self.lines = [
            "Forest Survival",
            "A side-view walk through four zones",
            "Art and audio from the 2023 jam",
            "Click to return",
        ]

    def on_enter(self):
        if self.audio_manager:
            self.audio_manager.play_music("theme", loops=-1)

    def update(self, delta_time: float):
        return None

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["black"])
        rect = pygame.Rect(0, 0, 640, 320)
        rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        panel(screen, rect)
        for index, line in enumerate(self.lines):
            text = self.font.render(line, True, config.COLORS["white"])
            screen.blit(text, text.get_rect(center=(rect.centerx, rect.y + 60 + index * 56)))

    def handle_event(self, event: pygame.event.Event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self.scene_manager.change_scene("main_menu")
            return True
        return False
