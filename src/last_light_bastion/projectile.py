"""Projectiles: movement, collision, chaining, and effects."""

from __future__ import annotations

import math

from tower import ProjectileData


class Projectile:
    def __init__(self, data: ProjectileData) -> None:
        self.data = data
        self.x = data.x
        self.y = data.y
        self.alive = True
        self.hit_targets: set[int] = set()
        self.chain_hops_left = data.chain
        dx = data.target_x - data.x
        dy = data.target_y - data.y
        dist = math.hypot(dx, dy)
        self.vx = (dx / dist * data.speed) if dist > 0 else 0.0
        self.vy = (dy / dist * data.speed) if dist > 0 else 0.0

    def update(self, dt_ms: float) -> None:
        if not self.alive:
            return
        self.data.speed * (dt_ms / 1000.0)
        self.x += self.vx * (dt_ms / 1000.0)
        self.y += self.vy * (dt_ms / 1000.0)
        dx = self.data.target_x - self.x
        dy = self.data.target_y - self.y
        if math.hypot(dx, dy) < 6:
            self.alive = False

    def collides_with(self, enemy) -> bool:
        if not enemy.alive or id(enemy) in self.hit_targets:
            return False
        return math.hypot(enemy.x - self.x, enemy.y - self.y) < enemy.size + 5
