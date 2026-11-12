"""Deterministic balance harness: damage formulas, costs, wave scaling."""

from __future__ import annotations

from base import *  # noqa: F403
from config import (
    BOSS_STATS,
    ENDLESS_BASE_WAVE,
    ENEMY_STATS,
    STARTING_CURRENCY,
    TOWER_BASE_COSTS,
    TOWER_STATS,
    UPGRADE_COSTS,
    UPGRADE_MULTIPLIERS,
    WAVES,
)
from enemy import Enemy


def test_every_tower_has_strategic_cost():
    for tid, cost in TOWER_BASE_COSTS.items():
        assert cost > 0
        assert tid in TOWER_STATS
        assert tid in UPGRADE_COSTS
        assert len(UPGRADE_COSTS[tid]) == 2


def test_damage_armor_formula_bounded():
    # damage after armor never negative, resistance caps at <1
    for eid, s in ENEMY_STATS.items():
        assert 0 <= s["resistance"] < 1.0
        assert s["armor"] >= 0
        e = Enemy(eid, [(0, 0), (100, 0)])
        dealt = e.apply_damage(1000)
        assert dealt >= 0
        assert dealt <= 1000


def test_upgrade_multipliers_increase_power():
    for level in [1, 2, 3]:
        m = UPGRADE_MULTIPLIERS[level]
        if level > 1:
            prev = UPGRADE_MULTIPLIERS[level - 1]
            assert m["damage"] > prev["damage"]


def test_wave_composition_data_driven():
    assert len(WAVES) == 25
    for _idx, cfg in WAVES.items():
        assert "enemies" in cfg
        assert "intermission_ms" in cfg
        total = sum(e["count"] for e in cfg["enemies"])
        assert total > 0


def test_wave_has_enemies_and_scales_overall():
    totals = []
    for idx in range(1, 26):
        cfg = WAVES[idx]
        total = sum(e["count"] for e in cfg["enemies"])
        totals.append(total)
        assert total > 0
    # the final campaign wave should be no easier than the first
    assert totals[-1] >= totals[0]


def test_endless_scales_without_immediate_impossibility():
    WAVES[ENDLESS_BASE_WAVE]
    for n in [1, 2, 5, 10, 30]:
        scale = 1.0 + (n - 1) * 0.35
        hp = ENEMY_STATS["basic"]["max_hp"] * scale
        # even at wave 30, basic hp stays finite and beatable
        assert hp < 5000


def test_boss_hp_large_but_finite():
    for _bid, s in BOSS_STATS.items():
        assert s["max_hp"] > 2000
        assert s["max_hp"] < 20000
        assert len(s["abilities"]) >= 1


def test_economy_can_recover():
    # starting currency can always afford cheapest tower
    cheapest = min(TOWER_BASE_COSTS.values())
    assert STARTING_CURRENCY >= cheapest
    # kill reward positive
    for s in ENEMY_STATS.values():
        assert s["reward"] > 0
