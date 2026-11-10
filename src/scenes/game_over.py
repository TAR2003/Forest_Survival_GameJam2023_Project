"""Run summary after the player falls."""

import pygame

import config
from src.core.scene_manager import Scene
from src.entities.player_controller import format_time
from src.ui.forest_ui import menu_rows


class GameOverScene(Scene):
    def __init__(self, scene_manager, audio_manager=None, save_manager=None):
        super().__init__("game_over")
        self.scene_manager = scene_manager
        self.audio_manager = audio_manager
        self.save_manager = save_manager
        self.font = pygame.font.Font(None, 36)
        self.score = 0
        self.time_label = "00:00"
        self.quests_done = 0
        self.options = [("Continue", "gameplay"), ("Main Menu", "main_menu")]
        self.hits = []

    def on_enter(self):
        if self.audio_manager:
            self.audio_manager.play_music("string", loops=-1)
        data = self.save_manager.game_data if self.save_manager else {}
        quests = data.get("progression", {}).get("quests", {})
        self.quests_done = sum(1 for status in quests.values() if status == "complete")
        survival = data.get("progression", {}).get("survival_time", 0)
        self.time_label = format_time(int(survival * 1000))
        self.score = self.quests_done * 100

    def update(self, delta_time: float):
        return None

    def render(self, screen: pygame.Surface):
        screen.fill(config.COLORS["black"])
        summary = f"Score {self.score}    Time {self.time_label}    Quests {self.quests_done}"
        self.hits = menu_rows(
            screen,
            summary,
            [label for label, _ in self.options],
            self.font,
        )

    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        for rect, (_, action) in zip(self.hits, self.options):
            if rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("click", volume=0.5)
                self.scene_manager.change_scene(action)
                return True
        return False
