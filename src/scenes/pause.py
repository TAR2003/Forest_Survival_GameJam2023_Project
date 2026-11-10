"""Pause menu over the current run."""

import pygame

import config
from src.core.scene_manager import Scene
from src.ui.forest_ui import menu_rows


class PauseScene(Scene):
    def __init__(self, scene_manager, audio_manager, save_manager):
        super().__init__("pause")
        self.scene_manager = scene_manager
        self.audio_manager = audio_manager
        self.save_manager = save_manager
        self.font = pygame.font.Font(None, 36)
        self.options = [
            ("Resume", "gameplay"),
            ("Settings", "settings"),
            ("Save", "save"),
            ("Main Menu", "main_menu"),
            ("Quit", "quit"),
        ]
        self.hits = []

    def on_enter(self):
        if self.audio_manager:
            self.audio_manager.play_music("theme", loops=-1)

    def update(self, delta_time: float):
        return None

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["black"])
        self.hits = menu_rows(screen, "Paused", [label for label, _ in self.options], self.font)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.scene_manager.change_scene("gameplay")
            return True
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        for rect, (_, action) in zip(self.hits, self.options):
            if rect.collidepoint(event.pos):
                self._activate(action)
                return True
        return False

    def _activate(self, action: str):
        if self.audio_manager:
            self.audio_manager.play_sound("click", volume=0.5)
        if action == "save":
            if self.save_manager:
                self.save_manager.save_game_data()
            return
        self.scene_manager.change_scene(action)
