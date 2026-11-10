"""Skills, quests, and achievements stored inside a save slot."""

import json
from pathlib import Path

import config


def _read(name: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / name
    return json.loads(path.read_text(encoding="utf-8"))


class Progression:
    """Tracks skill ranks, quest status, and unlocked achievements."""

    def __init__(self):
        skills = _read("skills.json")
        quests = _read("quests.json")
        self.xp_per_level = skills["xp_per_level"]
        self.skill_defs = {row["id"]: row for row in skills["skills"]}
        self.quest_defs = {row["id"]: row for row in quests["quests"]}
        self.ranks = {skill_id: 0 for skill_id in self.skill_defs}
        self.quests = {quest_id: "active" for quest_id in self.quest_defs}
        self.xp = 0
        self.level = 1
        self.skill_points = 0
        self.total_xp = 0
        self.unlocked = []
        self.toasts = []
        self.survival_time = 0.0
        self.active_quest = "speak_owl"

    def objective(self) -> str:
        quest = self.quest_defs.get(self.active_quest)
        if quest is None or self.quests.get(self.active_quest) == "complete":
            for quest_id, status in self.quests.items():
                if status != "complete":
                    self.active_quest = quest_id
                    return self.quest_defs[quest_id]["objective"]
            return "The forest is quiet."
        return quest["objective"]

    def grant_xp(self, amount: int):
        self.xp += amount
        self.total_xp += amount
        while self.xp >= self.xp_per_level:
            self.xp -= self.xp_per_level
            self.level += 1
            self.skill_points += 1
            self.toasts.append(f"Level {self.level}")

    def spend_point(self, skill_id: str) -> bool:
        definition = self.skill_defs.get(skill_id)
        if definition is None or self.skill_points <= 0:
            return False
        if self.ranks[skill_id] >= definition["max_rank"]:
            return False
        self.ranks[skill_id] += 1
        self.skill_points -= 1
        return True

    def damage_bonus(self) -> int:
        return self.ranks["blade"] * self.skill_defs["blade"]["damage_per_rank"]

    def apply_to_player(self, player):
        if not hasattr(player, "base_move_speed"):
            player.base_move_speed = player.move_speed
        speed_step = self.skill_defs["stride"]["speed_per_rank"]
        player.move_speed = player.base_move_speed * (1 + speed_step * self.ranks["stride"])
        if not hasattr(player, "base_stamina_regen"):
            player.base_stamina_regen = getattr(player, "stamina_regen", 25)
        regen_step = self.skill_defs["guard"]["regen_per_rank"]
        player.stamina_regen = player.base_stamina_regen * (1 + regen_step * self.ranks["guard"])

    def complete_quest(self, quest_id: str) -> bool:
        if quest_id not in self.quests or self.quests[quest_id] == "complete":
            return False
        definition = self.quest_defs[quest_id]
        self.quests[quest_id] = "complete"
        self.grant_xp(definition["xp"])
        achievement = definition.get("achievement")
        if achievement:
            self.unlock(achievement)
        self.toasts.append(definition["name"])
        return True

    def turn_in_herbs(self, inventory) -> bool:
        """Spend herbs and grant the potion plus quest XP."""
        if self.quests.get("gather_herbs") == "complete":
            return False
        if inventory.get_item_count("herbs") >= 1:
            inventory.remove_item("herbs", 1)
        elif inventory.get_item_count("herb") >= 3:
            inventory.remove_item("herb", 3)
        else:
            return False
        from src.ui.inventory_system import item_from_record
        import json
        catalog = json.loads((Path(__file__).resolve().parents[2] / "data" / "items.json").read_text(encoding="utf-8"))
        potion = next(row for row in catalog["items"] if row["id"] == "potion")
        inventory.add_item(item_from_record(potion), 1)
        return self.complete_quest("gather_herbs")

    def note(self, event: str):
        mapping = {
            "block": "first_block",
            "kill": "first_kill",
            "night": "night_survived",
            "ninja": "ninja_defeated",
        }
        if event == "kill":
            self.grant_xp(15)
        if event == "ninja":
            self.complete_quest("defeat_ninja")
        if event == "night":
            self.complete_quest("survive_night")
        achievement = mapping.get(event)
        if achievement:
            self.unlock(achievement)

    def add_time(self, seconds: float):
        before = self.survival_time
        self.survival_time += seconds
        marks = [
            (30, "first_steps"),
            (120, "survivor"),
            (300, "unstoppable"),
            (600, "legend"),
        ]
        for mark, achievement_id in marks:
            if before < mark <= self.survival_time:
                self.unlock(achievement_id)

    def unlock(self, achievement_id: str):
        if achievement_id in self.unlocked or achievement_id not in config.ACHIEVEMENTS:
            return
        self.unlocked.append(achievement_id)
        name = config.ACHIEVEMENTS[achievement_id]["name"]
        self.toasts.append(name)
        self.grant_xp(config.ACHIEVEMENTS[achievement_id]["xp_reward"])

    def pop_toast(self):
        if not self.toasts:
            return None
        return self.toasts.pop(0)

    def to_save(self) -> dict:
        return {
            "xp": self.xp,
            "level": self.level,
            "skill_points": self.skill_points,
            "total_xp": self.total_xp,
            "ranks": dict(self.ranks),
            "quests": dict(self.quests),
            "unlocked": list(self.unlocked),
            "survival_time": self.survival_time,
            "active_quest": self.active_quest,
        }

    def load(self, data: dict):
        if not data:
            return
        self.xp = data.get("xp", 0)
        self.level = data.get("level", 1)
        self.skill_points = data.get("skill_points", 0)
        self.total_xp = data.get("total_xp", 0)
        self.ranks.update(data.get("ranks", {}))
        self.quests.update(data.get("quests", {}))
        self.unlocked = list(data.get("unlocked", []))
        self.survival_time = data.get("survival_time", 0)
        self.active_quest = data.get("active_quest", self.active_quest)
