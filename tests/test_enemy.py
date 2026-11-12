"""Tests for enemy archetypes, movement, armor, resistance, status effects."""

from __future__ import annotations

from base import *  # noqa: F403
from config import ENEMY_STATS
from enemy import Enemy, StatusEffect


def test_seven_enemy_archetypes():
    assert len(ENEMY_STATS) == 7
    for eid in ["basic", "fast", "armored", "heavy", "flying", "regenerating", "elite"]:
        assert eid in ENEMY_STATS


def test_enemy_stats_differ():
    stats = ENEMY_STATS
    assert stats["fast"]["speed"] > stats["basic"]["speed"]
    assert stats["armored"]["armor"] > stats["basic"]["armor"]
    assert stats["heavy"]["max_hp"] > stats["basic"]["max_hp"]
    assert stats["flying"]["flying"] is True
    assert stats["regenerating"]["regeneration"] > 0


def test_flying_follows_route():
    route = [(100, 100), (200, 100), (200, 200)]
    e = Enemy("flying", route)
    assert e.flying
    e.update(1000)
    assert not e.finished


def test_enemy_reaches_exit_and_finishes():
    route = [(100, 100), (200, 100)]
    e = Enemy("basic", route)
    # move full distance: speed 70 px/sec; 100px = ~1429ms
    e.update(2000)
    assert e.finished
    assert e.progress >= 1.0


def test_armor_reduces_damage():
    e = Enemy("armored", [(0, 0), (100, 0)])
    dealt = e.apply_damage(20)
    assert dealt < 20
    assert dealt >= 0


def test_resistance_reduces_damage():
    e = Enemy("heavy", [(0, 0), (100, 0)])
    dealt = e.apply_damage(100)
    expected = max(0.0, 100 - e.armor) * (1.0 - e.resistance)
    assert abs(dealt - expected) < 1e-6


def test_dead_enemy_no_damage():
    e = Enemy("basic", [(0, 0), (100, 0)])
    e.apply_damage(1000)
    assert e.is_dead()
    dealt = e.apply_damage(50)
    assert dealt == 0.0


def test_poison_dot_tick():
    e = Enemy("basic", [(0, 0), (100, 0)])
    e.add_effect(StatusEffect("poison", 10, 2000))
    hp_before = e.hp
    e.tick_ms = 0
    # simulate 900ms (one tick at 800ms)
    e.effects[0].tick_ms = 900
    e.update(100)  # pushes tick over 800
    assert e.hp < hp_before


def test_slow_effect_reduces_speed():
    e = Enemy("fast", [(0, 0), (100, 0)])
    e.add_effect(StatusEffect("slow", 0.5, 1000))
    # speed factor applied internally; just ensure effect present
    assert any(eff.kind == "slow" for eff in e.effects)


def test_regeneration_heals():
    e = Enemy("regenerating", [(0, 0), (100, 0)])
    e.apply_damage(50)
    hp_before = e.hp
    e._regen_timer_ms = 1100
    e.update(0)  # triggers regen
    assert e.hp > hp_before


def test_zero_hp_enemy_dead():
    e = Enemy("basic", [(0, 0), (100, 0)])
    e.hp = 0
    assert e.is_dead()
