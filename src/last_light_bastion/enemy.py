"""Enemy archetypes, movement, and status effects."""

from __future__ import annotations

import math

from config import ENEMY_STATS


class StatusEffect:
    def __init__(self, kind: str, value: float, duration_ms: int) -> None:
        self.kind = kind  # 'slow', 'poison'
        self.value = value
        self.duration_ms = duration_ms
        self.remaining_ms = duration_ms
        self.tick_ms = 0.0

    def update(self, dt_ms: float) -> None:
        self.remaining_ms -= dt_ms

    def expired(self) -> bool:
        return self.remaining_ms <= 0


class Enemy:
    def __init__(
        self, enemy_id: str, route: list[tuple[float, float]], hp_mult: float = 1.0, speed_mult: float = 1.0
    ) -> None:
        self.enemy_id = enemy_id
        stats = ENEMY_STATS[enemy_id]
        self.max_hp = stats["max_hp"] * hp_mult
        self.hp = self.max_hp
        self.speed = stats["speed"] * speed_mult
        self.armor = stats["armor"]
        self.resistance = stats["resistance"]
        self.reward = stats["reward"]
        self.size = stats["size"]
        self.flying = stats["flying"]
        self.regeneration = stats["regeneration"]
        self.color = stats["color"]
        self.route = route
        self.route_index = 0
        self.progress = 0.0  # 0..1 along route
        self.finished = False
        self.alive = True
        self.x, self.y = route[0] if route else (0.0, 0.0)
        self.effects: list[StatusEffect] = []
        self._regen_timer_ms = 0.0

    def is_dead(self) -> bool:
        return not self.alive or self.hp <= 0

    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    def add_effect(self, effect: StatusEffect) -> None:
        # replace same-kind effect with stronger/longer
        for existing in self.effects:
            if existing.kind == effect.kind:
                if effect.duration_ms > existing.remaining_ms or effect.value > existing.value:
                    existing.remaining_ms = max(existing.remaining_ms, effect.duration_ms)
                    existing.value = max(existing.value, effect.value)
                return
        self.effects.append(effect)

    def apply_damage(self, damage: float, armor_pierce: float = 0.0, true: bool = False) -> float:
        if self.is_dead():
            return 0.0
        if true:
            dealt = damage
        else:
            effective_armor = max(0.0, self.armor - armor_pierce)
            dealt = max(0.0, damage - effective_armor)
            dealt *= 1.0 - self.resistance
        self.hp -= dealt
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return dealt

    def heal(self, amount: float) -> None:
        if self.is_dead():
            return
        self.hp = min(self.max_hp, self.hp + amount)

    def _move_along_route(self, dt_ms: float) -> None:
        if self.finished or not self.route:
            return
        route = self.route
        if self.route_index >= len(route) - 1:
            # at final waypoint; snap
            self.x, self.y = route[-1]
            self.finished = True
            self.progress = 1.0
            return
        p0 = route[self.route_index]
        p1 = route[self.route_index + 1]
        seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if seg <= 0:
            self.route_index += 1
            return
        move_dist = (self.speed / 1000.0) * dt_ms
        # slow effects reduce speed
        slow_factor = 1.0
        for e in self.effects:
            if e.kind == "slow":
                slow_factor = min(slow_factor, 1.0 - e.value)
        move_dist *= slow_factor
        self.progress += move_dist / seg
        if self.progress >= 1.0:
            excess = (self.progress - 1.0) * seg
            self.route_index += 1
            self.progress = 0.0
            if self.route_index >= len(route) - 1:
                self.x, self.y = route[-1]
                self.finished = True
                self.progress = 1.0
            else:
                p0 = route[self.route_index]
                p1 = route[self.route_index + 1]
                seg2 = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
                frac = excess / seg2 if seg2 > 0 else 0.0
                self.x = p0[0] + (p1[0] - p0[0]) * frac
                self.y = p0[1] + (p1[1] - p0[1]) * frac
        else:
            self.x = p0[0] + (p1[0] - p0[0]) * self.progress
            self.y = p0[1] + (p1[1] - p0[1]) * self.progress

    def update(self, dt_ms: float, game=None) -> None:
        if self.is_dead() or self.finished:
            # still tick regen? no if dead
            if not self.is_dead():
                self._regen_timer_ms += dt_ms
                if self._regen_timer_ms >= 1000 and self.regeneration > 0:
                    self.heal(self.regeneration * (self._regen_timer_ms / 1000.0))
                    self._regen_timer_ms %= 1000
            for e in self.effects:
                e.update(dt_ms)
            self.effects = [e for e in self.effects if not e.expired()]
            return
        self._move_along_route(dt_ms)
        # regeneration
        self._regen_timer_ms += dt_ms
        if self._regen_timer_ms >= 1000 and self.regeneration > 0:
            self.heal(self.regeneration)
            self._regen_timer_ms %= 1000
        # poison tick
        for e in self.effects:
            e.update(dt_ms)
            if e.kind == "poison":
                e.tick_ms += dt_ms
                if e.tick_ms >= 800:
                    self.apply_damage(e.value, true=True)
                    e.tick_ms -= 800
        self.effects = [e for e in self.effects if not e.expired()]
