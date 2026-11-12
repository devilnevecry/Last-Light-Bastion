"""Settings and persistence wrapper."""

from __future__ import annotations

from typing import Any


class Settings:
    def __init__(self, data: dict[str, Any] | None = None) -> None:
        raw = {}
        if data is not None:
            raw = data.get("settings", {})
        self.language: str = raw.get("language", "ru")
        self.volume: float = float(raw.get("volume", 0.7))
        self.fullscreen: bool = bool(raw.get("fullscreen", False))
        self.game_speed: float = float(raw.get("game_speed", 1.0))

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "volume": self.volume,
            "fullscreen": self.fullscreen,
            "game_speed": self.game_speed,
        }

    def clamp_speed(self, speeds) -> float:
        for s in speeds:
            if abs(self.game_speed - s) < 1e-6:
                return self.game_speed
        return speeds[0] if speeds else 1.0
