"""Versioned, atomic save system with safe recovery from corrupted data."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

SAVE_VERSION = 2
SAVE_DIR_NAME = "saves"
SAVE_FILE_NAME = "savegame.json"
BACKUP_FILE_NAME = "savegame.bak"


def save_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "saves")


def save_path() -> str:
    return os.path.join(save_dir(), SAVE_FILE_NAME)


def backup_path() -> str:
    return os.path.join(save_dir(), BACKUP_FILE_NAME)


def _default_save() -> dict[str, Any]:
    return {
        "version": SAVE_VERSION,
        "currency": 0,
        "unlocked_maps": ["wastes"],
        "completed_maps": [],
        "map_stars": {},
        "map_best_score": {},
        "achievements": {},
        "best_endless_wave": 0,
        "total_kills": 0,
        "total_towers_built": 0,
        "total_bosses_defeated": 0,
        "settings": {
            "language": "ru",
            "volume": 0.7,
            "fullscreen": False,
            "game_speed": 1.0,
        },
        "stats": {
            "tower_types_built": [],
            "flying_kills": 0,
            "currency_peak": 0,
            "damage_taken_run": 0,
        },
    }


def load() -> dict[str, Any]:
    """Load the save file, recovering from corruption or missing data."""
    path = save_path()
    back = backup_path()
    candidates = [path, back]
    for candidate in candidates:
        if not os.path.isfile(candidate):
            continue
        try:
            with open(candidate, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                raise ValueError("save root is not an object")
            data = _migrate(data)
            data = _validate(data)
            # restore from backup if primary was corrupt
            if candidate == back and os.path.isfile(path):
                try:
                    save(data)
                except OSError:
                    pass
            return data
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    # No valid save: create defaults
    data = _default_save()
    try:
        save(data)
    except OSError:
        pass
    return data


def save(data: dict[str, Any]) -> None:
    """Atomically write the save file."""
    data = dict(data)
    data["version"] = SAVE_VERSION
    directory = save_dir()
    os.makedirs(directory, exist_ok=True)
    path = save_path()
    back = backup_path()
    # keep previous as backup
    if os.path.isfile(path):
        try:
            os.replace(path, back)
        except OSError:
            pass
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".save_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.isfile(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def _migrate(data: dict[str, Any]) -> dict[str, Any]:
    version = data.get("version", 1)
    if version < 2:
        # add stats block if missing
        if "stats" not in data or not isinstance(data["stats"], dict):
            data["stats"] = {
                "tower_types_built": [],
                "flying_kills": 0,
                "currency_peak": 0,
                "damage_taken_run": 0,
            }
    return data


def _validate(data: dict[str, Any]) -> dict[str, Any]:
    default = _default_save()
    for key, value in default.items():
        if key not in data or not isinstance(data[key], type(value)):
            data[key] = value
    # ensure nested settings
    if not isinstance(data.get("settings"), dict):
        data["settings"] = default["settings"]
    for key, value in default["settings"].items():
        data["settings"].setdefault(key, value)
    if not isinstance(data.get("stats"), dict):
        data["stats"] = default["stats"]
    for key, value in default["stats"].items():
        data["stats"].setdefault(key, value)
    if not isinstance(data.get("unlocked_maps"), list):
        data["unlocked_maps"] = default["unlocked_maps"]
    if not isinstance(data.get("completed_maps"), list):
        data["completed_maps"] = default["completed_maps"]
    if not isinstance(data.get("map_stars"), dict):
        data["map_stars"] = {}
    if not isinstance(data.get("map_best_score"), dict):
        data["map_best_score"] = {}
    if not isinstance(data.get("achievements"), dict):
        data["achievements"] = {}
    return data
