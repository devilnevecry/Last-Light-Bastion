"""Game state and simulation core. Rendering-independent gameplay logic."""

from __future__ import annotations

import math
import random
from wave import WaveManager

import pygame
from boss import Boss
from config import (
    BASE_HEALTH,
    SELL_REFUND,
    STARTING_CURRENCY,
    TARGET_MODES,
    TOWER_BASE_COSTS,
    UPGRADE_COSTS,
    WAVES,
)
from enemy import Enemy, StatusEffect
from map import ALL_MAPS
from projectile import Projectile
from tower import Tower


class GameState:
    def __init__(self) -> None:
        self.map_key: str | None = None
        self.map = None
        self.tile_size = 32
        self.grid_offset = (40.0, 100.0)
        self.currency = STARTING_CURRENCY
        self.base_health = BASE_HEALTH
        self.base_max_health = BASE_HEALTH
        self.towers: list[Tower] = []
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.warnings: list[dict] = []
        self.explosions: list[dict] = []
        self.particles: list[dict] = []
        self.wave_manager = WaveManager()
        self.paused = False
        self.game_speed = 1.0
        self.selected_tower: Tower | None = None
        self.placement_mode: str | None = None
        self.placement_pos: tuple[int, int] | None = None
        self.mission_complete = False
        self.defeated = False
        self.run_stats = {
            "kills": 0,
            "towers_built": 0,
            "tower_types_built": set(),
            "flying_kills": 0,
            "damage_taken": 0,
            "max_currency": STARTING_CURRENCY,
            "bosses_defeated": 0,
            "waves_survived": 0,
        }
        self._enemy_id_counter = 0
        self._rng = random.Random()

    # ------------------------------------------------------------------ map
    def start_map(self, map_key: str) -> None:
        self.map_key = map_key
        self.map = ALL_MAPS[map_key]
        self.currency = STARTING_CURRENCY
        self.base_health = BASE_HEALTH
        self.base_max_health = BASE_HEALTH
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.warnings = []
        self.explosions = []
        self.particles = []
        self.selected_tower = None
        self.placement_mode = None
        self.placement_pos = None
        self.mission_complete = False
        self.defeated = False
        self.run_stats = {
            "kills": 0,
            "towers_built": 0,
            "tower_types_built": set(),
            "flying_kills": 0,
            "damage_taken": 0,
            "max_currency": STARTING_CURRENCY,
            "bosses_defeated": 0,
            "waves_survived": 0,
        }
        self.wave_manager = WaveManager()
        self.wave_manager.start_campaign()
        self._enemy_id_counter = 0
        self._rng = random.Random()
        self.paused = False

    def grid_to_pixel(self, gx: int, gy: int) -> tuple[float, float]:
        ox, oy = self.grid_offset
        return (
            gx * self.tile_size + ox + self.tile_size / 2,
            gy * self.tile_size + oy + self.tile_size / 2,
        )

    def pixel_to_grid(self, px: float, py: float) -> tuple[int, int]:
        ox, oy = self.grid_offset
        return (int((px - ox) // self.tile_size), int((py - oy) // self.tile_size))

    # ------------------------------------------------------------------ economy / build
    def can_afford(self, amount: int) -> bool:
        return self.currency >= amount

    def start_placement(self, tower_id: str) -> bool:
        if tower_id not in TOWER_BASE_COSTS:
            return False
        if not self.can_afford(TOWER_BASE_COSTS[tower_id]):
            return False
        self.placement_mode = tower_id
        self.placement_pos = None
        self.selected_tower = None
        return True

    def cancel_placement(self) -> None:
        self.placement_mode = None
        self.placement_pos = None

    def try_place_tower(self, gx: int, gy: int) -> bool:
        if self.placement_mode is None or self.map is None:
            return False
        tower_id = self.placement_mode
        cost = TOWER_BASE_COSTS[tower_id]
        if not self.can_afford(cost):
            return False
        if not self.map.can_place_tower(gx, gy):
            return False
        for t in self.towers:
            if t.x == gx and t.y == gy:
                return False
        self.currency -= cost
        tower = Tower(tower_id, gx, gy, self)
        self.towers.append(tower)
        self.run_stats["towers_built"] += 1
        self.run_stats["tower_types_built"].add(tower_id)
        self.placement_mode = None
        self.placement_pos = None
        self.selected_tower = tower
        return True

    def upgrade_selected(self) -> bool:
        if self.selected_tower is None:
            return False
        cost = self.selected_tower.upgrade_cost()
        if cost is None or not self.can_afford(cost):
            return False
        self.currency -= cost
        self.selected_tower.upgrade()
        return True

    def sell_selected(self) -> int:
        if self.selected_tower is None:
            return 0
        tower = self.selected_tower
        value = int(
            TOWER_BASE_COSTS[tower.tower_id] * SELL_REFUND
            + sum(UPGRADE_COSTS[tower.tower_id][i] * SELL_REFUND for i in range(tower.level - 1))
        )
        self.towers = [t for t in self.towers if t is not tower]
        self.currency += value
        self.selected_tower = None
        return value

    def select_tower_at(self, gx: int, gy: int) -> Tower | None:
        for t in self.towers:
            if t.x == gx and t.y == gy:
                self.selected_tower = t
                self.placement_mode = None
                self.placement_pos = None
                return t
        self.selected_tower = None
        return None

    def set_target_mode(self, mode: str) -> None:
        if mode not in TARGET_MODES:
            return
        if self.selected_tower is not None:
            self.selected_tower.target_mode = mode

    # ------------------------------------------------------------------ simulation
    def set_speed(self, speed: float) -> None:
        self.game_speed = speed

    def spawn_enemy(self, enemy_def: dict, route_index: int = 0) -> None:
        if self.map is None:
            return
        route = self.map.routes[route_index % len(self.map.routes)]
        pixel_route = [self.grid_to_pixel(x, y) for (x, y) in route]
        enemy = Enemy(
            enemy_def["type"],
            pixel_route,
            hp_mult=enemy_def.get("hp_mult", 1.0),
            speed_mult=enemy_def.get("speed_mult", 1.0),
        )
        enemy._id = self._enemy_id_counter
        self._enemy_id_counter += 1
        self.enemies.append(enemy)

    def spawn_boss(self, boss_def: dict) -> None:
        if self.map is None:
            return
        route = self.map.routes[0]
        pixel_route = [self.grid_to_pixel(x, y) for (x, y) in route]
        boss = Boss(boss_def["id"], pixel_route, hp_mult=boss_def.get("hp_mult", 1.0))
        boss._id = self._enemy_id_counter
        self._enemy_id_counter += 1
        self.enemies.append(boss)
        self.warnings.append({"kind": "boss_arrival", "boss_id": boss_def["id"], "ms": 2000})

    def update(self, dt_ms: float) -> None:
        if self.paused or self.defeated or self.mission_complete:
            return
        dt = dt_ms * self.game_speed
        # wave
        wave_result = self.wave_manager.update(dt)
        for entry in wave_result.get("spawn", []):
            route_index = len(self.enemies) % max(1, len(self.map.routes)) if self.map else 0
            self.spawn_enemy(entry, route_index)
        if wave_result.get("boss"):
            self.spawn_boss(wave_result["boss"])
        # enemies
        for enemy in self.enemies:
            enemy.update(dt, self)
        # enemies reaching exit deal damage
        for enemy in list(self.enemies):
            if enemy.finished and enemy.alive:
                self.base_health -= 1
                self.run_stats["damage_taken"] += 1
                enemy.alive = False
                if self.base_health <= 0:
                    self.base_health = 0
                    self.defeated = True
        # remove dead/finished
        self.enemies = [e for e in self.enemies if e.alive and not e.finished]
        # wave clearance -> wave_clear / victory
        wm = self.wave_manager
        if wm.wave is not None:
            last_campaign_wave = max(WAVES)
            if wave_result.get("done") and not self.enemies:
                wm.state = "victory" if wm.wave.index >= last_campaign_wave else "wave_clear"
            elif (
                wm.wave.boss_id
                and wm.wave.boss_spawned
                and not any(isinstance(e, Boss) for e in self.enemies)
                and not self.enemies
            ):
                wm.state = "victory" if wm.wave.index >= last_campaign_wave else "wave_clear"
        # towers target & shoot
        now_ms = pygame.time.get_ticks()
        for tower in self.towers:
            support = 1.0
            for other in self.towers:
                if other is not None and other.supports(tower):
                    support *= other.support_multiplier
            effective_cooldown = tower.cooldown_ms / support if support > 0 else tower.cooldown_ms
            if now_ms - tower.last_shot_ms >= effective_cooldown and tower.can_shoot(now_ms):
                target = tower.select_target(self.enemies, now_ms)
                if target is not None:
                    for pd in tower.shoot(target, now_ms):
                        self.projectiles.append(Projectile(pd))
        # projectiles
        for proj in self.projectiles:
            proj.update(dt)
        self._resolve_projectiles()
        self.projectiles = [p for p in self.projectiles if p.alive]
        # particles & warnings & explosions cleanup
        for p in self.particles:
            p["life"] -= dt
            p["x"] += p.get("vx", 0) * (dt / 1000.0)
            p["y"] += p.get("vy", 0) * (dt / 1000.0)
        self.particles = [p for p in self.particles if p.get("life", 0) > 0]
        self.warnings = [w for w in self.warnings if w.get("ms", 0) > 0]
        for w in self.warnings:
            w["ms"] -= dt
            if w.get("callback") and w.get("ms", 0) <= 0:
                try:
                    w["callback"](self)
                except Exception:
                    pass
                w["callback"] = None
        self.explosions = [e for e in self.explosions if e.get("life", 0) > 0]
        for e in self.explosions:
            e["life"] -= dt
            e["frame"] = min(5, int((700 - e["life"]) / 700 * 6))
        # mission victory
        if self.wave_manager.state == "victory" and not self.enemies and not self.projectiles:
            self.mission_complete = True

    # ------------------------------------------------------------------ combat
    def _resolve_projectiles(self) -> None:
        for proj in self.projectiles:
            if not proj.alive:
                continue
            target = None
            for enemy in self.enemies:
                if proj.collides_with(enemy):
                    target = enemy
                    break
            if target is not None:
                proj.hit_targets.add(id(target))
                target.apply_damage(proj.data.damage)
                if proj.data.slow > 0:
                    target.add_effect(StatusEffect("slow", proj.data.slow, proj.data.slow_ms))
                if proj.data.dot > 0:
                    target.add_effect(StatusEffect("poison", proj.data.dot, proj.data.dot_ms))
                if proj.data.splash > 0:
                    self._apply_splash(proj, target)
                if proj.data.chain > 0:
                    self._chain(proj, target)
                if not target.alive:
                    self._on_enemy_death(target)
                proj.alive = False
                if proj.data.splash > 0:
                    self.spawn_explosion(target.x, target.y)

    def _apply_splash(self, proj: Projectile, target) -> None:
        tx, ty = target.x, target.y
        for enemy in self.enemies:
            if id(enemy) in proj.hit_targets:
                continue
            if math.hypot(enemy.x - tx, enemy.y - ty) <= proj.data.splash:
                proj.hit_targets.add(id(enemy))
                enemy.apply_damage(proj.data.splash * 0.6)
                if proj.data.slow > 0:
                    enemy.add_effect(StatusEffect("slow", proj.data.slow * 0.7, proj.data.slow_ms))
                if not enemy.alive:
                    proj.hit_targets.add(id(enemy))
                    self._on_enemy_death(enemy)

    def _chain(self, proj: Projectile, source) -> None:
        self._chain_link(proj, source)

    def _chain_link(self, proj: Projectile, source) -> None:
        if proj.data.chain <= 0 or not proj.alive:
            return
        tx, ty = source.x, source.y
        candidates = [e for e in self.enemies if id(e) not in proj.hit_targets and math.hypot(e.x - tx, e.y - ty) <= 90]
        if not candidates:
            return
        candidates.sort(key=lambda e: math.hypot(e.x - tx, e.y - ty))
        nxt = candidates[0]
        proj.hit_targets.add(id(nxt))
        nxt.apply_damage(proj.data.damage * 0.5)
        if proj.data.slow > 0:
            nxt.add_effect(StatusEffect("slow", proj.data.slow * 0.5, proj.data.slow_ms))
        proj.data.chain -= 1
        if not nxt.alive:
            self._on_enemy_death(nxt)
        self._chain_link(proj, nxt)

    def _on_enemy_death(self, enemy) -> None:
        self.run_stats["kills"] += 1
        self.currency += enemy.reward
        self.run_stats["max_currency"] = max(self.currency, self.run_stats["max_currency"])
        if getattr(enemy, "flying", False):
            self.run_stats["flying_kills"] += 1
        self._spawn_death_particles(enemy.x, enemy.y, enemy.color)
        if isinstance(enemy, Boss):
            self.run_stats["bosses_defeated"] += 1

    def _spawn_death_particles(self, x: float, y: float, color) -> None:
        for _ in range(6):
            ang = self._rng.random() * 6.283
            sp = 40 + self._rng.random() * 60
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(ang) * sp,
                "vy": math.sin(ang) * sp,
                "life": 400,
                "color": color,
                "size": 4,
            })

    def spawn_explosion(self, x: float, y: float, max_radius: int = 26) -> None:
        self.explosions.append({"x": x, "y": y, "life": 700, "max_radius": max_radius, "frame": 0})

    def spawn_explosion_warning(self, target, radius, ms, callback) -> None:
        self.warnings.append({
            "kind": "ability_warning",
            "target": target,
            "radius": radius,
            "ms": ms,
            "callback": callback,
        })
