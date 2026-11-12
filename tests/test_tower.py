"""Tests for towers, targeting, upgrades, and projectile emission."""

from __future__ import annotations

from base import *  # noqa: F403
from config import TARGET_MODES, TOWER_BASE_COSTS, UPGRADE_COSTS
from enemy import Enemy
from state import GameState
from tower import Tower


def _make_game():
    gs = GameState()
    gs.start_map("wastes")
    return gs


def test_six_tower_types():
    assert len(TOWER_BASE_COSTS) == 6
    for tid in ["archer", "cannon", "frost", "arc", "poison", "support"]:
        assert tid in TOWER_BASE_COSTS


def test_three_upgrade_levels():
    for _tid, costs in UPGRADE_COSTS.items():
        assert len(costs) == 2  # level1->2, level2->3


def test_tower_stats_and_range():
    gs = _make_game()
    t = Tower("archer", 5, 5, gs)
    assert t.level == 1
    assert t.range > 0
    assert t.cooldown_ms > 0
    assert t.damage > 0


def test_upgrade_applies_effects():
    gs = _make_game()
    t = Tower("cannon", 5, 5, gs)
    dmg1 = t.damage
    rng1 = t.range
    cd1 = t.cooldown_ms
    t.upgrade()
    assert t.level == 2
    assert t.damage > dmg1
    assert t.range > rng1
    assert t.cooldown_ms < cd1
    t.upgrade()
    assert t.level == 3
    assert t.upgrade_cost() is None


def test_upgrade_cost_increases():
    gs = _make_game()
    t = Tower("archer", 5, 5, gs)
    c1 = t.upgrade_cost()
    t.upgrade()
    c2 = t.upgrade_cost()
    assert c2 > c1


def test_sell_value_partial_refund():
    gs = _make_game()
    t = Tower("archer", 5, 5, gs)
    value = t.sell_value()
    assert 0 < value < TOWER_BASE_COSTS["archer"]


def test_targeting_modes():
    for mode in TARGET_MODES:
        assert mode in ["first", "last", "strongest", "weakest", "closest"]


def test_select_target_first_last():
    gs = _make_game()
    t = Tower("archer", 5, 5, gs)
    # build dummy enemies manually
    route = [(100, 100), (200, 100)]
    e1 = Enemy("basic", route)
    e1.x, e1.y = 100, 100
    e1.progress = 0.1
    e2 = Enemy("basic", route)
    e2.x, e2.y = 200, 100
    e2.progress = 0.9
    gs.enemies = [e1, e2]
    # "first" = furthest along the route (first to reach the exit)
    t.target_mode = "first"
    assert t.select_target(gs.enemies, 0) is e2
    t.target_mode = "last"
    assert t.select_target(gs.enemies, 0) is e1


def test_tower_can_shoot_cooldown():
    gs = _make_game()
    t = Tower("archer", 5, 5, gs)
    assert t.can_shoot(0)
    t.last_shot_ms = 0
    assert not t.can_shoot(100)  # cooldown 700


def test_shoot_emits_projectile():
    gs = _make_game()
    t = Tower("archer", 5, 5, gs)
    e = Enemy("basic", [(100, 100), (200, 100)])
    e.x, e.y = 200, 100
    projs = t.shoot(e, 1000)
    assert len(projs) >= 1
    assert projs[0].damage == t.damage


def test_archer_level3_barrage():
    gs = _make_game()
    t = Tower("archer", 5, 5, gs)
    t.level = 3
    t._apply_stats()
    e = Enemy("basic", [(100, 100), (200, 100)])
    e.x, e.y = 200, 100
    projs = t.shoot(e, 1000)
    assert len(projs) == 3


def test_support_boosts():
    gs = _make_game()
    sup = Tower("support", 5, 5, gs)
    arc = Tower("arc", 6, 5, gs)
    assert sup.supports(arc)  # adjacent
    far = Tower("arc", 20, 20, gs)
    assert not sup.supports(far)


def test_placement_cost_deducted():
    gs = _make_game()
    gs.start_placement("archer")
    before = gs.currency
    assert gs.try_place_tower(3, 3)
    assert gs.currency == before - TOWER_BASE_COSTS["archer"]


def test_cannot_place_on_path():
    gs = _make_game()
    gs.start_placement("archer")
    route = gs.map.routes[0][0]
    assert not gs.try_place_tower(*route)


def test_cannot_afford_placement():
    gs = _make_game()
    gs.start_placement("archer")
    gs.currency = 0
    assert not gs.try_place_tower(3, 3)
    assert len(gs.towers) == 0
