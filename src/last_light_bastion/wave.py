"""Data-driven wave system with spawning, intermissions, bosses, and endless mode."""

from __future__ import annotations

import random

from config import ENDLESS_BASE_WAVE, WAVES


class Wave:
    """A single configured wave of enemies."""

    def __init__(self, index: int, config: dict, rng: random.Random) -> None:
        self.index = index
        self.config = config
        self.rng = rng
        self.enemies_to_spawn: list[dict] = []
        self._build_spawn_list()
        self.spawn_cursor = 0
        self.next_spawn_ms = 0.0
        self.intermission_ms = config.get("intermission_ms", 10000)
        self.in_intermission = True
        self.intermission_timer_ms = 0.0
        self.boss_id = config.get("boss")
        self.boss_hp_mult = config.get("boss_hp_mult", 1.0)
        self.boss_spawned = False

    def _build_spawn_list(self) -> None:
        for entry in self.config.get("enemies", []):
            for _ in range(entry.get("count", 0)):
                self.enemies_to_spawn.append({
                    "type": entry["type"],
                    "delay_ms": entry.get("delay_ms", 600),
                    "hp_mult": entry.get("hp_mult", 1.0),
                    "speed_mult": entry.get("speed_mult", 1.0),
                })
        self.rng.shuffle(self.enemies_to_spawn)

    def start_intermission(self) -> None:
        self.in_intermission = True
        self.intermission_timer_ms = 0.0
        self.boss_spawned = False

    def start_spawning(self) -> None:
        self.in_intermission = False
        self.spawn_cursor = 0
        self.next_spawn_ms = 0.0

    def update(self, dt_ms: float) -> dict:
        """Returns {'spawn': [enemy_defs], 'boss': boss_def or None, 'done': bool}."""
        result = {"spawn": [], "boss": None, "done": False}
        if self.in_intermission:
            self.intermission_timer_ms += dt_ms
            if self.intermission_timer_ms >= self.intermission_ms:
                self.start_spawning()
            return result
        # spawning phase
        if self.boss_id and not self.boss_spawned and self.spawn_cursor >= len(self.enemies_to_spawn):
            self.boss_spawned = True
            result["boss"] = {"id": self.boss_id, "hp_mult": self.boss_hp_mult}
            return result
        while self.spawn_cursor < len(self.enemies_to_spawn):
            entry = self.enemies_to_spawn[self.spawn_cursor]
            if self.next_spawn_ms <= 0:
                result["spawn"].append(entry)
                self.spawn_cursor += 1
                if self.spawn_cursor < len(self.enemies_to_spawn):
                    self.next_spawn_ms = self.enemies_to_spawn[self.spawn_cursor]["delay_ms"]
                else:
                    self.next_spawn_ms = 0
                return result
            self.next_spawn_ms -= dt_ms
            break
        if self.spawn_cursor >= len(self.enemies_to_spawn) and not self.boss_id:
            result["done"] = True
        return result


class WaveManager:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.wave_index = 0
        self.wave: Wave | None = None
        self.state = "idle"  # idle, intermission, spawning, wave_clear, victory, defeat
        self.endless = False
        self.endless_wave = 0

    def start_campaign(self, start_index: int = 1) -> None:
        self.endless = False
        self.endless_wave = 0
        self.wave_index = start_index
        self._load_wave(start_index)
        self.state = "intermission"

    def start_endless(self, start_wave: int = 1) -> None:
        self.endless = True
        self.endless_wave = start_wave
        self.wave_index = ENDLESS_BASE_WAVE + start_wave
        self._load_endless_wave(start_wave)
        self.state = "intermission"

    def _load_wave(self, index: int) -> None:
        config = WAVES.get(index)
        if config is None:
            self.state = "victory"
            self.wave = None
            return
        self.wave = Wave(index, config, self.rng)
        self.wave.start_intermission()

    def _load_endless_wave(self, n: int) -> None:
        base = WAVES[ENDLESS_BASE_WAVE].copy()
        scale = 1.0 + (n - 1) * 0.35
        enemies = []
        for entry in base["enemies"]:
            count = max(1, int(entry["count"] * (1 + (n - 1) * 0.25)))
            enemies.append({
                "type": entry["type"],
                "count": count,
                "delay_ms": max(120, int(entry["delay_ms"] / (1 + (n - 1) * 0.1))),
                "hp_mult": scale,
                "speed_mult": min(2.0, 1 + (n - 1) * 0.05),
            })
        config = {"enemies": enemies, "intermission_ms": max(6000, 20000 - (n - 1) * 500)}
        self.wave_index = ENDLESS_BASE_WAVE + n
        self.wave = Wave(self.wave_index, config, self.rng)
        self.wave.start_intermission()

    def next_wave(self) -> None:
        if self.state not in ("intermission", "idle"):
            return
        if self.endless:
            self.endless_wave += 1
            self._load_endless_wave(self.endless_wave)
        else:
            self.wave_index += 1
            self._load_wave(self.wave_index)

    def update(self, dt_ms: float) -> dict:
        if self.wave is None:
            return {"spawn": [], "boss": None, "done": False}
        return self.wave.update(dt_ms)
