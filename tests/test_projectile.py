"""Tests for projectiles: movement, collision, splash, chain, effects."""

from __future__ import annotations

import math

from base import *  # noqa: F403
from enemy import Enemy, StatusEffect
from projectile import Projectile
from tower import ProjectileData


def test_projectile_moves_toward_target():
    data = ProjectileData(0, 0, 100, 0, speed=200, damage=10, proj_id="arrow")
    p = Projectile(data)
    p.update(100)
    assert p.x > 0
    p.update(400)
    assert not p.alive


def test_projectile_collision_detected():
    data = ProjectileData(0, 0, 100, 0, speed=200, damage=10, proj_id="arrow")
    p = Projectile(data)
    p.x, p.y = 95, 0
    e = Enemy("basic", [(0, 0), (100, 0)])
    e.x, e.y = 95, 0
    assert p.collides_with(e)


def test_projectile_deals_damage():
    data = ProjectileData(0, 0, 100, 0, speed=200, damage=1000, proj_id="arrow")
    p = Projectile(data)
    p.x, p.y = 50, 0
    e = Enemy("basic", [(0, 0), (100, 0)])
    e.x, e.y = 50, 0
    assert p.collides_with(e)
    e.apply_damage(p.data.damage)
    assert e.is_dead()


def test_splash_damages_nearby_enemies():
    target = Enemy("basic", [(0, 0), (100, 0)])
    target.x, target.y = 50, 0
    neighbor = Enemy("basic", [(0, 0), (100, 0)])
    neighbor.x, neighbor.y = 60, 0
    splash = 30.0
    assert math.hypot(neighbor.x - target.x, neighbor.y - target.y) <= splash
    neighbor.apply_damage(100 * 0.6)
    assert neighbor.hp < neighbor.max_hp


def test_chain_hops_between_targets():
    src = Enemy("basic", [(0, 0), (100, 0)])
    src.x, src.y = 50, 0
    t1 = Enemy("basic", [(0, 0), (100, 0)])
    t1.x, t1.y = 60, 0
    t2 = Enemy("basic", [(0, 0), (100, 0)])
    t2.x, t2.y = 70, 0
    assert math.hypot(t1.x - src.x, t1.y - src.y) <= 90
    assert math.hypot(t2.x - t1.x, t2.y - t1.y) <= 90


def test_poison_effect_applied():
    e = Enemy("basic", [(0, 0), (100, 0)])
    e.add_effect(StatusEffect("poison", 6, 800))
    assert any(eff.kind == "poison" for eff in e.effects)


def test_slow_effect_applied():
    e = Enemy("basic", [(0, 0), (100, 0)])
    e.add_effect(StatusEffect("slow", 0.5, 1000))
    assert any(eff.kind == "slow" for eff in e.effects)
