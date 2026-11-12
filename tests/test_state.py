"""Tests for the core game simulation state."""

from __future__ import annotations

from base import *  # noqa: F403
from config import BASE_HEALTH, STARTING_CURRENCY
from enemy import Enemy
from projectile import Projectile
from state import GameState


def _new_game():
    gs = GameState()
    gs.start_map("wastes")
    return gs


def test_initial_economy():
    gs = _new_game()
    assert gs.currency == STARTING_CURRENCY
    assert gs.base_health == BASE_HEALTH


def test_build_and_upgrade_cycle():
    gs = _new_game()
    gs.start_placement("archer")
    cost_before = gs.currency
    assert gs.try_place_tower(3, 3)
    assert gs.currency == cost_before - 45
    assert len(gs.towers) == 1
    t = gs.towers[0]
    assert t.level == 1
    uc = t.upgrade_cost()
    assert gs.currency >= uc
    gs.currency -= uc
    t.upgrade()
    assert t.level == 2


def test_sell_refund():
    gs = _new_game()
    gs.start_placement("archer")
    gs.try_place_tower(3, 3)
    after_build = gs.currency
    value = gs.sell_selected()
    assert value > 0
    assert gs.currency == after_build + value
    assert len(gs.towers) == 0
    assert gs.selected_tower is None


def test_insufficient_resources_block_build():
    gs = _new_game()
    gs.start_placement("archer")
    gs.currency = 0
    assert not gs.try_place_tower(3, 3)
    assert len(gs.towers) == 0


def test_invalid_placement_blocked():
    gs = _new_game()
    gs.start_placement("archer")
    route = gs.map.routes[0][0]
    assert not gs.try_place_tower(*route)
    assert len(gs.towers) == 0


def test_enemy_reaching_exit_damage_base():
    gs = _new_game()
    hp_before = gs.base_health
    # spawn an enemy already at the final waypoint by forcing finished
    e = Enemy("basic", [(100, 100), (200, 100)])
    e.x, e.y = 200, 100
    e.finished = True
    gs.enemies = [e]
    gs.update(0)
    assert gs.base_health == hp_before - 1
    assert not e.alive


def test_defeat_when_base_zero():
    gs = _new_game()
    gs.base_health = 1
    e = Enemy("basic", [(100, 100), (200, 100)])
    e.x, e.y = 200, 100
    e.finished = True
    gs.enemies = [e]
    gs.update(0)
    assert gs.defeated


def test_simultaneous_exit_damage():
    gs = _new_game()
    gs.base_health = 2
    e1 = Enemy("basic", [(100, 100), (200, 100)])
    e1.x, e1.y = 200, 100
    e1.finished = True
    e2 = Enemy("basic", [(100, 100), (200, 100)])
    e2.x, e2.y = 200, 100
    e2.finished = True
    gs.enemies = [e1, e2]
    gs.update(0)
    assert gs.base_health == 0
    assert gs.defeated


def test_multiple_projectiles_same_target():
    gs = _new_game()
    gs.start_placement("archer")
    gs.try_place_tower(3, 3)
    t = gs.towers[0]
    e = Enemy("basic", [(200, 100), (300, 100)])
    e.x, e.y = 200, 100
    e.hp = 5
    gs.enemies = [e]
    # manually shoot twice and drive projectiles into the enemy
    for _ in range(2):
        for pd in t.shoot(e, 1000):
            p = Projectile(pd)
            p.x, p.y = e.x, e.y
            gs.projectiles.append(p)
    gs._resolve_projectiles()
    assert e.is_dead()


def test_pause_freezes_simulation():
    gs = _new_game()
    gs.paused = True
    currency = gs.currency
    gs.update(5000)
    assert gs.currency == currency
