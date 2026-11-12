"""Tests for campaign progression and achievements."""

from __future__ import annotations

from base import *  # noqa: F403
from campaign import AchievementTracker, Campaign
from config import ACHIEVEMENTS, MAP_ORDER


def test_campaign_has_five_maps():
    assert len(MAP_ORDER) == 5


def test_initial_unlock_only_wastes():
    save_data = {
        "version": 2,
        "unlocked_maps": ["wastes"],
        "completed_maps": [],
        "map_stars": {},
        "map_best_score": {},
        "achievements": {},
        "settings": {},
        "stats": {},
    }
    c = Campaign(save_data)
    assert c.is_unlocked("wastes")
    assert not c.is_unlocked("spire")


def test_complete_map_unlocks_next():
    save_data = {
        "version": 2,
        "unlocked_maps": ["wastes"],
        "completed_maps": [],
        "map_stars": {},
        "map_best_score": {},
        "achievements": {},
        "settings": {},
        "stats": {},
    }
    c = Campaign(save_data)
    newly = c.complete_map("wastes", 3, 1000)
    assert c.is_completed("wastes")
    assert "spire" in newly or c.is_unlocked("spire")


def test_stars_recorded():
    save_data = {
        "version": 2,
        "unlocked_maps": ["wastes"],
        "completed_maps": [],
        "map_stars": {},
        "map_best_score": {},
        "achievements": {},
        "settings": {},
        "stats": {},
    }
    c = Campaign(save_data)
    c.complete_map("wastes", 2, 500)
    assert c.stars_for("wastes") == 2
    c.complete_map("wastes", 3, 2000)
    assert c.stars_for("wastes") == 3


def test_achievements_ten_plus():
    assert len(ACHIEVEMENTS) >= 10


def test_achievement_tracker_unlocks():
    save_data = {
        "version": 2,
        "unlocked_maps": ["wastes"],
        "completed_maps": [],
        "map_stars": {},
        "map_best_score": {},
        "achievements": {},
        "settings": {},
        "stats": {},
    }
    c = Campaign(save_data)
    tracker = AchievementTracker(c)
    ctx = {"kills_total": 1}
    newly = tracker.check("first_blood", "kills_total >= 1", ctx)
    assert "first_blood" in newly
    assert c.achievements["first_blood"] is True


def test_achievement_not_double_unlocked():
    save_data = {
        "version": 2,
        "unlocked_maps": ["wastes"],
        "completed_maps": [],
        "map_stars": {},
        "map_best_score": {},
        "achievements": {"first_blood": True},
        "settings": {},
        "stats": {},
    }
    c = Campaign(save_data)
    tracker = AchievementTracker(c)
    ctx = {"kills_total": 5}
    newly = tracker.check("first_blood", "kills_total >= 1", ctx)
    assert newly == []
