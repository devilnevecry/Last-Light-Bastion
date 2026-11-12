"""Tests for the versioned atomic save system and corruption recovery."""

from __future__ import annotations

import os

import save
from base import *  # noqa: F403


def _monkeypatch_dir(monkeypatch, directory):
    monkeypatch.setattr(save, "save_dir", lambda: directory)
    monkeypatch.setattr(save, "save_path", lambda: os.path.join(directory, "savegame.json"))
    monkeypatch.setattr(save, "backup_path", lambda: os.path.join(directory, "savegame.bak"))


def test_save_and_load_roundtrip(monkeypatch, tmp_path):
    directory = str(tmp_path)
    _monkeypatch_dir(monkeypatch, directory)
    data = save.load()
    data["currency"] = 42
    data["unlocked_maps"] = ["wastes", "spire"]
    save.save(data)
    loaded = save.load()
    assert loaded["currency"] == 42
    assert loaded["unlocked_maps"] == ["wastes", "spire"]
    assert loaded["version"] == save.SAVE_VERSION


def test_missing_save_creates_defaults(monkeypatch, tmp_path):
    directory = str(tmp_path)
    _monkeypatch_dir(monkeypatch, directory)
    data = save.load()
    assert data["version"] == save.SAVE_VERSION
    assert "wastes" in data["unlocked_maps"]


def test_corrupted_save_recovers(monkeypatch, tmp_path):
    directory = str(tmp_path)
    _monkeypatch_dir(monkeypatch, directory)
    path = save.save_path()
    os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("{not valid json")
    data = save.load()
    assert data["version"] == save.SAVE_VERSION


def test_atomic_save_no_temp_left(monkeypatch, tmp_path):
    directory = str(tmp_path)
    _monkeypatch_dir(monkeypatch, directory)
    save.save(save.load())
    leftovers = [f for f in os.listdir(directory) if f.startswith(".save_")]
    assert leftovers == []


def test_backup_restored_when_primary_corrupt(monkeypatch, tmp_path):
    directory = str(tmp_path)
    _monkeypatch_dir(monkeypatch, directory)
    data = save.load()
    data["currency"] = 100
    save.save(data)  # primary = 100
    data["currency"] = 999
    save.save(data)  # backup = 100, primary = 999
    # corrupt primary
    with open(save.save_path(), "w", encoding="utf-8") as f:
        f.write("corrupt")
    loaded = save.load()
    assert loaded["currency"] == 100
