"""Tests for the wave system: spawning, intermission, bosses, endless."""

from __future__ import annotations

import random
from wave import WaveManager

from base import *  # noqa: F403
from config import WAVES


def test_25_campaign_waves():
    indices = sorted(WAVES)
    campaign = [i for i in indices if i <= 25]
    assert len(campaign) == 25


def test_wave_spawn_list_built():
    wm = WaveManager(random.Random(1))
    wm.start_campaign(1)
    wave = wm.wave
    assert wave is not None
    total = sum(e["count"] for e in WAVES[1]["enemies"])
    assert len(wave.enemies_to_spawn) == total


def test_intermission_then_spawning():
    wm = WaveManager(random.Random(1))
    wm.start_campaign(1)
    assert wm.wave.in_intermission
    wm.update(20000)
    assert not wm.wave.in_intermission


def test_boss_wave_flag():
    wm = WaveManager(random.Random(1))
    wm.start_campaign(5)  # wave 5 has boss void_reaver
    # advance through intermission
    wm.update(20000)
    # spawn all enemies then boss
    while wm.wave and not wm.wave.boss_spawned and wm.wave.spawn_cursor < len(wm.wave.enemies_to_spawn):
        wm.update(1000)
    result = wm.update(0)
    assert result["boss"] is not None


def test_next_wave_advances():
    wm = WaveManager(random.Random(1))
    wm.start_campaign(1)
    first = wm.wave.index
    wm.next_wave()
    assert wm.wave.index == first + 1


def test_endless_mode_scales():
    wm = WaveManager(random.Random(1))
    wm.start_endless(1)
    w1 = wm.wave
    wm.next_wave()
    w2 = wm.wave
    assert wm.endless_wave == 2
    assert w2.index > w1.index


def test_endless_difficulty_increases():
    wm = WaveManager(random.Random(1))
    wm.start_endless(1)
    n1 = sum(e["count"] for e in wm.wave.config["enemies"])
    wm.next_wave()
    n2 = sum(e["count"] for e in wm.wave.config["enemies"])
    assert n2 >= n1
