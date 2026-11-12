"""Campaign progression, achievements, and persistent meta-data."""

from __future__ import annotations

from config import (
    ACHIEVEMENTS,
    MAP_ORDER,
    MAP_UNLOCK_COST,
)
from save import save as save_save


class Campaign:
    def __init__(self, save_data: dict) -> None:
        self.save = save_data
        self.unlocked = set(self.save.get("unlocked_maps", ["wastes"]))
        self.completed = set(self.save.get("completed_maps", []))
        self.map_stars = dict(self.save.get("map_stars", {}))
        self.map_best_score = dict(self.save.get("map_best_score", {}))
        self.achievements = dict(self.save.get("achievements", {}))
        self.total_kills = int(self.save.get("total_kills", 0))
        self.total_towers_built = int(self.save.get("total_towers_built", 0))
        self.total_bosses_defeated = int(self.save.get("total_bosses_defeated", 0))
        self.best_endless_wave = int(self.save.get("best_endless_wave", 0))
        self.stats = dict(self.save.get("stats", {}))

    def is_unlocked(self, map_key: str) -> bool:
        return map_key in self.unlocked

    def unlock(self, map_key: str) -> bool:
        cost = MAP_UNLOCK_COST.get(map_key)
        if cost is None:
            return False
        if map_key in self.unlocked:
            return True
        # Unlocking costs currency tracked externally; here just mark
        self.unlocked.add(map_key)
        return True

    def is_completed(self, map_key: str) -> bool:
        return map_key in self.completed

    def complete_map(self, map_key: str, stars: int, score: int) -> list[str]:
        """Mark a map completed. Returns list of newly unlocked map keys."""
        newly = []
        if map_key not in self.completed:
            self.completed.add(map_key)
            idx = MAP_ORDER.index(map_key) if map_key in MAP_ORDER else -1
            if idx >= 0 and idx + 1 < len(MAP_ORDER):
                nxt = MAP_ORDER[idx + 1]
                self.unlocked.add(nxt)
                newly.append(nxt)
        old_stars = self.map_stars.get(map_key, 0)
        if stars > old_stars:
            self.map_stars[map_key] = stars
        old_best = self.map_best_score.get(map_key, 0)
        if score > old_best:
            self.map_best_score[map_key] = score
        self.save_to(self.save)
        return newly

    def stars_for(self, map_key: str) -> int:
        return int(self.map_stars.get(map_key, 0))

    def best_score_for(self, map_key: str) -> int:
        return int(self.map_best_score.get(map_key, 0))

    def total_stars(self) -> int:
        return sum(self.map_stars.values())

    def save_to(self, save_data: dict) -> None:
        save_data["unlocked_maps"] = sorted(self.unlocked)
        save_data["completed_maps"] = sorted(self.completed)
        save_data["map_stars"] = self.map_stars
        save_data["map_best_score"] = self.map_best_score
        save_data["total_kills"] = self.total_kills
        save_data["total_towers_built"] = self.total_towers_built
        save_data["total_bosses_defeated"] = self.total_bosses_defeated
        save_data["best_endless_wave"] = self.best_endless_wave
        save_data["stats"] = self.stats
        save_save(save_data)


class AchievementTracker:
    def __init__(self, campaign: Campaign) -> None:
        self.campaign = campaign

    def check(self, aid: str, condition: str, ctx: dict) -> list[str]:
        """Evaluate a condition against context. Returns newly unlocked achievement ids."""
        newly = []
        if aid in self.campaign.achievements:
            return newly
        if self._eval(condition, ctx):
            self.campaign.achievements[aid] = True
            newly.append(aid)
            self.campaign.save_to(self.campaign.save)
        return newly

    def _eval(self, condition: str, ctx: dict) -> bool:
        # Simple safe evaluator for conditions like 'kills_total >= 1'
        try:
            return bool(eval(condition, {"__builtins__": {}}, ctx))
        except Exception:
            return False

    def unlocked_titles(self) -> list[str]:
        titles = []
        for aid, done in self.campaign.achievements.items():
            if done and aid in ACHIEVEMENTS:
                titles.append(aid)
        return titles
