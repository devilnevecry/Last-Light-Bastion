"""Boss enemies with distinct behaviors, abilities, and attack warnings."""

from __future__ import annotations

import math

from config import BOSS_STATS
from enemy import Enemy


class Boss(Enemy):
    def __init__(
        self,
        boss_id: str,
        route: list[tuple[float, float]],
        hp_mult: float = 1.0,
    ) -> None:
        # Initialize core enemy scaffolding with a placeholder archetype, then
        # overwrite every stat from BOSS_STATS so bosses are not looked up in
        # ENEMY_STATS (they are not ordinary enemies).
        super().__init__("basic", route, hp_mult=hp_mult)
        self.boss_id = boss_id
        stats = BOSS_STATS[boss_id]
        self.max_hp = stats["max_hp"] * hp_mult
        self.hp = self.max_hp
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.armor = stats["armor"]
        self.resistance = stats["resistance"]
        self.reward = stats["reward"]
        self.size = stats["size"]
        self.flying = stats["flying"]
        self.color = stats["color"]
        self.abilities = list(stats["abilities"])
        self._rage = 0.0
        self.ability_timer_ms = 0.0
        self.warning_ms = 0.0  # visual warning countdown
        self.warning_target: tuple[float, float] | None = None
        self.warning_radius = 0.0
        self.teleport_cooldown_ms = 0.0

    @property
    def rage(self) -> float:
        if self.max_hp <= 0:
            return 1.0
        return 1.0 - (self.hp / self.max_hp)

    def update(self, dt_ms: float, game) -> None:
        self.ability_timer_ms += dt_ms
        self.teleport_cooldown_ms = max(0.0, self.teleport_cooldown_ms - dt_ms)
        if self.warning_ms > 0:
            self.warning_ms -= dt_ms
            if self.warning_ms <= 0:
                self.warning_ms = 0
                self.warning_target = None
        super().update(dt_ms)
        self._maybe_use_ability(dt_ms, game)

    def _maybe_use_ability(self, dt_ms: float, game) -> None:
        if self.is_dead() or self.finished:
            return
        if self.boss_id == "void_reaver":
            self._void_reaver_ability(dt_ms, game)
        elif self.boss_id == "flame_titan":
            self._flame_titan_ability(dt_ms, game)
        elif self.boss_id == "storm_colossus":
            self._storm_colossus_ability(dt_ms, game)

    def _void_reaver_ability(self, dt_ms: float, game) -> None:
        # Teleport forward along route when health drops, plus void bolt warning.
        if self.teleport_cooldown_ms > 0:
            return
        if self.ability_timer_ms > 4000 + (1 - self.rage) * 2000:
            self.ability_timer_ms = 0
            self._teleport(game)
            self.teleport_cooldown_ms = 3000

    def _teleport(self, game) -> None:
        route = self.route
        idx = min(self.route_index + 2, len(route) - 1)
        self.route_index = idx
        self.x, self.y = route[idx]
        self.progress = 0.0
        # warn nearby towers with a pulse handled in renderer via warning target
        self.warning_ms = 600
        self.warning_target = (self.x, self.y)
        self.warning_radius = 60.0

    def _flame_titan_ability(self, dt_ms: float, game) -> None:
        if self.ability_timer_ms > 3000:
            self.ability_timer_ms = 0
            # fire wave warning then damage along path ahead
            ahead = self._ahead_position(90)
            self.warning_ms = 700
            self.warning_target = ahead
            self.warning_radius = 100.0
            game.spawn_explosion_warning(ahead, 100.0, 700, self._fire_wave_hit)

    def _fire_wave_hit(self, game) -> None:
        target = self.warning_target
        if target is None:
            return
        for enemy in game.enemies:
            if math.hypot(enemy.x - target[0], enemy.y - target[1]) <= 100:
                # placeholder: boss ability does not damage towers directly
                pass
        # Flame wave slows and damages towers in area
        tx, ty = target
        for tower in game.towers:
            tx2, ty2 = tower.center_pixel()
            if math.hypot(tx2 - tx, ty2 - ty) <= 100:
                tower.last_shot_ms += 1500  # silence tower briefly

    def _storm_colossus_ability(self, dt_ms: float, game) -> None:
        if self.ability_timer_ms > 3500:
            self.ability_timer_ms = 0
            # chain lightning to nearest towers
            tx, ty = self.center_pixel()
            targets = sorted(
                game.towers,
                key=lambda t: math.hypot(t.center_pixel()[0] - tx, t.center_pixel()[1] - ty),
            )[:3]
            self.warning_ms = 600
            self.warning_target = (tx, ty)
            self.warning_radius = 40.0
            for tower in targets:
                tower.last_shot_ms += 1200

    def _ahead_position(self, distance: float) -> tuple[float, float]:
        route = self.route
        idx = self.route_index
        if idx >= len(route) - 1:
            return (self.x, self.y)
        p0 = route[idx]
        p1 = route[min(idx + 1, len(route) - 1)]
        seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if seg <= 0:
            return (self.x, self.y)
        frac = min(1.0, distance / seg)
        return (p0[0] + (p1[0] - p0[0]) * frac, p0[1] + (p1[1] - p0[1]) * frac)

    def apply_damage(self, damage: float, armor_pierce: float = 0.0, true: bool = False) -> float:
        return super().apply_damage(damage, armor_pierce, true)
