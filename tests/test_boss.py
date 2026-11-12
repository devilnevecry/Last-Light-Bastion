"""Tests for boss behavior and abilities."""

from __future__ import annotations

from base import *  # noqa: F403
from boss import Boss
from config import BOSS_STATS


def test_three_bosses():
    assert len(BOSS_STATS) == 3
    for bid in ["void_reaver", "flame_titan", "storm_colossus"]:
        assert bid in BOSS_STATS


def test_boss_large_health_pool():
    for bid, _stats in BOSS_STATS.items():
        b = Boss(bid, [(100, 100), (200, 100)])
        assert b.max_hp > 1000
        assert b.hp == b.max_hp


def test_boss_distinct_from_ordinary_enemy():
    b = Boss("flame_titan", [(100, 100), (200, 100)])
    assert len(b.abilities) > 0
    assert b.size > 16


def test_boss_rage_increases_as_hp_drops():
    b = Boss("void_reaver", [(100, 100), (200, 100)])
    early = b.rage
    b.apply_damage(b.max_hp * 0.5)
    late = b.rage
    assert late > early


def test_boss_take_damage():
    b = Boss("storm_colossus", [(100, 100), (200, 100)])
    before = b.hp
    dealt = b.apply_damage(500)
    assert b.hp == before - dealt


def test_boss_death():
    b = Boss("void_reaver", [(100, 100), (200, 100)])
    b.apply_damage(b.max_hp + 1000, true=True)
    assert b.is_dead()
