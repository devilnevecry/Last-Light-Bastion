"""Tower definitions, targeting, upgrades, and projectile emission."""

from __future__ import annotations

import math
from dataclasses import dataclass

from config import (
    TOWER_BASE_COSTS,
    TOWER_STATS,
    UPGRADE_COSTS,
    UPGRADE_DESCRIPTIONS,
    UPGRADE_MULTIPLIERS,
)


@dataclass
class ProjectileData:
    x: float
    y: float
    target_x: float
    target_y: float
    speed: float
    damage: float
    proj_id: str
    splash: float = 0.0
    chain: int = 0
    slow: float = 0.0
    slow_ms: int = 0
    dot: float = 0.0
    dot_ms: int = 0
    owner_id: str = ""
    piercing: bool = False


class Tower:
    """Base tower. Gameplay logic separated from rendering."""

    def __init__(self, tower_id: str, x: int, y: int, game) -> None:
        self.tower_id = tower_id
        self.x = x
        self.y = y
        self.level = 1
        self.game = game
        self.last_shot_ms = 0.0
        self.target_mode = "first"
        self.target: object | None = None
        self._apply_stats()
        # A freshly built tower can fire immediately.
        self.last_shot_ms = -self.cooldown_ms

    def _apply_stats(self) -> None:
        base = TOWER_STATS[self.tower_id]
        mult = UPGRADE_MULTIPLIERS[self.level]
        self.range = base["range"] * mult["range"]
        self.cooldown_ms = base["cooldown_ms"] * mult["cooldown"]
        self.damage = base["damage"] * mult["damage"]
        self.projectile_speed = base["projectile_speed"]
        self.projectile_id = base["projectile"]
        self.splash = base["splash"] * mult["damage"]
        self.chain = base["chain"]
        self.slow = base["slow"]
        self.slow_ms = base["slow_ms"]
        self.dot = base["dot"] * mult["damage"]
        self.dot_ms = base["dot_ms"]
        self.support_multiplier = base["support_multiplier"]
        if self.level == 3 and self.tower_id == "support":
            self.support_multiplier = 1.6

    def upgrade_cost(self) -> int | None:
        if self.level >= 3:
            return None
        return UPGRADE_COSTS[self.tower_id][self.level - 1]

    def upgrade(self) -> bool:
        cost = self.upgrade_cost()
        if cost is None:
            return False
        self.level += 1
        self._apply_stats()
        return True

    def sell_value(self) -> int:
        return int(
            TOWER_BASE_COSTS[self.tower_id] * 0.7
            + sum(UPGRADE_COSTS[self.tower_id][i] * 0.7 for i in range(self.level - 1))
        )

    def center_pixel(self, tile_size: int = 32) -> tuple[float, float]:
        return (self.x * tile_size + tile_size / 2, self.y * tile_size + tile_size / 2)

    def in_range(self, ex: float, ey: float) -> bool:
        tx, ty = self.center_pixel()
        return math.hypot(ex - tx, ey - ty) <= self.range + 2

    def can_shoot(self, now_ms: float) -> bool:
        if self.tower_id == "support":
            return False
        return now_ms - self.last_shot_ms >= self.cooldown_ms

    def select_target(self, enemies: list, now_ms: float) -> object | None:
        candidates = [e for e in enemies if self.in_range(e.x, e.y) and e.alive and not e.is_dead()]
        if not candidates:
            self.target = None
            return None
        if self.target_mode == "first":
            chosen = max(candidates, key=lambda e: e.progress)
        elif self.target_mode == "last":
            chosen = min(candidates, key=lambda e: e.progress)
        elif self.target_mode == "closest":
            tx, ty = self.center_pixel()
            chosen = min(candidates, key=lambda e: math.hypot(e.x - tx, e.y - ty))
        elif self.target_mode == "strongest":
            chosen = max(candidates, key=lambda e: e.max_hp)
        elif self.target_mode == "weakest":
            chosen = min(candidates, key=lambda e: e.hp)
        else:
            chosen = max(candidates, key=lambda e: e.progress)
        self.target = chosen
        return chosen

    def shoot(self, target, now_ms: float) -> list[ProjectileData]:
        self.last_shot_ms = now_ms
        tx, ty = self.center_pixel()
        projectiles: list[ProjectileData] = []
        count = 3 if (self.level == 3 and self.tower_id == "archer") else 1
        count = 2 if (self.level == 3 and self.tower_id == "cannon") else count
        for _ in range(count):
            projectiles.append(
                ProjectileData(
                    x=tx,
                    y=ty,
                    target_x=target.x,
                    target_y=target.y,
                    speed=self.projectile_speed,
                    damage=self.damage,
                    proj_id=self.projectile_id,
                    splash=self.splash,
                    chain=self.chain,
                    slow=self.slow,
                    slow_ms=self.slow_ms,
                    dot=self.dot,
                    dot_ms=self.dot_ms,
                    owner_id=f"{self.tower_id}:{self.x},{self.y}",
                )
            )
        return projectiles

    def supports(self, other: "Tower") -> bool:
        if self.tower_id != "support":
            return False
        tx, ty = self.center_pixel()
        ox, oy = other.center_pixel()
        return math.hypot(ox - tx, oy - ty) <= self.range + 2

    def get_upgrade_description(self) -> str:
        return UPGRADE_DESCRIPTIONS.get(self.tower_id, {}).get(self.level, "")

    def to_dict(self) -> dict:
        return {
            "tower_id": self.tower_id,
            "x": self.x,
            "y": self.y,
            "level": self.level,
            "target_mode": self.target_mode,
        }

    @classmethod
    def from_dict(cls, data: dict, game) -> "Tower":
        tower = cls(data["tower_id"], data["x"], data["y"], game)
        tower.level = data.get("level", 1)
        tower.target_mode = data.get("target_mode", "first")
        tower._apply_stats()
        return tower
