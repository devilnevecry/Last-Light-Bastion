"""Last Light: Bastion - core game configuration and balance constants."""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
BASE_WIDTH = 1280
BASE_HEIGHT = 800
MIN_WIDTH = 960
MIN_HEIGHT = 720
FPS_TARGET = 60
TILE_SIZE = 32
GRID_COLS = 24
GRID_ROWS = 18
UI_PANEL_WIDTH = 300

# ---------------------------------------------------------------------------
# Colors (RGB) - cohesive neon / energy barrier palette
# ---------------------------------------------------------------------------
COLOR_BG = (16, 14, 24)
COLOR_PANEL = (26, 22, 38)
COLOR_PANEL_BRIGHT = (42, 36, 58)
COLOR_GRID = (40, 34, 56)
COLOR_PATH = (58, 48, 80)
COLOR_PATH_HINT = (90, 74, 120)
COLOR_OBSTACLE = (34, 30, 46)
COLOR_PLACEMENT = (0, 200, 160)
COLOR_PLACEMENT_INVALID = (200, 60, 60)
COLOR_TEXT = (230, 230, 240)
COLOR_TEXT_DIM = (150, 150, 170)
COLOR_ACCENT = (120, 220, 255)
COLOR_GOLD = (255, 215, 100)
COLOR_HEALTH = (60, 240, 100)
COLOR_DANGER = (240, 80, 80)
COLOR_WARNING = (255, 180, 60)
COLOR_FROST = (140, 200, 255)
COLOR_POISON = (120, 220, 100)
COLOR_ARC = (200, 140, 255)
COLOR_CANNON = (255, 140, 60)

# ---------------------------------------------------------------------------
# Economy
# ---------------------------------------------------------------------------
STARTING_CURRENCY = 120
BASE_HEALTH = 100
SELL_REFUND = 0.7
BASE_KILL_REWARD = 10
WAVE_CLEAR_BONUS = 50
INTEREST_PER_10 = 1  # +1 currency per 10 held at wave end, capped
INTEREST_CAP = 25

TOWER_BASE_COSTS = {
    "archer": 45,
    "cannon": 75,
    "frost": 60,
    "arc": 80,
    "poison": 70,
    "support": 90,
}

UPGRADE_COSTS = {
    "archer": [60, 110],
    "cannon": [100, 180],
    "frost": [75, 140],
    "arc": [100, 190],
    "poison": [90, 170],
    "support": [110, 210],
}

# ---------------------------------------------------------------------------
# Tower stats: (range, attack_speed_ms, damage, projectile_speed, cost)
# upgrade multipliers per level (level 1 = base, level 2 / 3 apply)
# ---------------------------------------------------------------------------
TOWER_STATS = {
    "archer": {
        "range": 140,
        "cooldown_ms": 700,
        "damage": 18,
        "projectile_speed": 560,
        "projectile": "arrow",
        "splash": 0,
        "chain": 0,
        "slow": 0.0,
        "slow_ms": 0,
        "dot": 0,
        "dot_ms": 0,
        "support_multiplier": 1.0,
    },
    "cannon": {
        "range": 110,
        "cooldown_ms": 1500,
        "damage": 55,
        "projectile_speed": 420,
        "projectile": "shell",
        "splash": 70,
        "chain": 0,
        "slow": 0.0,
        "slow_ms": 0,
        "dot": 0,
        "dot_ms": 0,
        "support_multiplier": 1.0,
    },
    "frost": {
        "range": 120,
        "cooldown_ms": 900,
        "damage": 8,
        "projectile_speed": 460,
        "projectile": "ice",
        "splash": 25,
        "chain": 0,
        "slow": 0.5,
        "slow_ms": 1200,
        "dot": 0,
        "dot_ms": 0,
        "support_multiplier": 1.0,
    },
    "arc": {
        "range": 105,
        "cooldown_ms": 1100,
        "damage": 26,
        "projectile_speed": 720,
        "projectile": "arc",
        "splash": 0,
        "chain": 2,
        "slow": 0.0,
        "slow_ms": 0,
        "dot": 0,
        "dot_ms": 0,
        "support_multiplier": 1.0,
    },
    "poison": {
        "range": 130,
        "cooldown_ms": 950,
        "damage": 10,
        "projectile_speed": 400,
        "projectile": "venom",
        "splash": 0,
        "chain": 0,
        "slow": 0.0,
        "slow_ms": 0,
        "dot": 6,
        "dot_ms": 800,
        "support_multiplier": 1.0,
    },
    "support": {
        "range": 150,
        "cooldown_ms": 0,
        "damage": 0,
        "projectile_speed": 0,
        "projectile": None,
        "splash": 0,
        "chain": 0,
        "slow": 0.0,
        "slow_ms": 0,
        "dot": 0,
        "dot_ms": 0,
        "support_multiplier": 1.35,
    },
}

# Per-level multiplier applied to damage / splash / dot / slow / range.
UPGRADE_MULTIPLIERS = {
    1: {"damage": 1.0, "range": 1.0, "cooldown": 1.0},
    2: {"damage": 1.6, "range": 1.15, "cooldown": 0.9},
    3: {"damage": 2.5, "range": 1.3, "cooldown": 0.8},
}

# Tower upgrade descriptions keyed by tower type and level.
UPGRADE_DESCRIPTIONS = {
    "archer": {
        1: "Fast, accurate single-shot attacks.",
        2: "Vampiric rounds - shots deal extra damage.",
        3: "Barrage - fires three arrows per volley.",
    },
    "cannon": {
        1: "Heavy shells explode on impact.",
        2: "Shrapnel - wider blast radius.",
        3: "Barrage fire - two shells per volley.",
    },
    "frost": {
        1: "Ice bolts chill enemies in a small area.",
        2: "Deep freeze - stronger slow, wider area.",
        3: "Glacial storm - slows and damages nearby foes.",
    },
    "arc": {
        1: "Lightning chains to nearby targets.",
        2: "Overcharge - additional chain hop.",
        3: "Storm surge - damage and stun on first hit.",
    },
    "poison": {
        1: "Venomous darts deal damage over time.",
        2: "Virulent toxin - stronger and longer poison.",
        3: "Plague cloud - poison spreads on death.",
    },
    "support": {
        1: "Amplifies damage of nearby towers.",
        2: "Overclock - boosts attack speed of allies.",
        3: "Bastion aura - damage, speed, and range boost.",
    },
}

# ---------------------------------------------------------------------------
# Enemy archetypes
# ---------------------------------------------------------------------------
ENEMY_STATS = {
    "basic": {
        "max_hp": 120,
        "speed": 70,
        "armor": 0,
        "resistance": 0.0,
        "reward": 12,
        "size": 10,
        "flying": False,
        "regeneration": 0.0,
        "color": COLOR_TEXT_DIM,
    },
    "fast": {
        "max_hp": 55,
        "speed": 125,
        "armor": 0,
        "resistance": 0.0,
        "reward": 14,
        "size": 9,
        "flying": False,
        "regeneration": 0.0,
        "color": (120, 255, 140),
    },
    "armored": {
        "max_hp": 260,
        "speed": 45,
        "armor": 8,
        "resistance": 0.0,
        "reward": 20,
        "size": 13,
        "flying": False,
        "regeneration": 0.0,
        "color": (160, 160, 170),
    },
    "heavy": {
        "max_hp": 700,
        "speed": 30,
        "armor": 14,
        "resistance": 0.15,
        "reward": 35,
        "size": 16,
        "flying": False,
        "regeneration": 0.0,
        "color": (140, 100, 90),
    },
    "flying": {
        "max_hp": 90,
        "speed": 95,
        "armor": 0,
        "resistance": 0.25,
        "reward": 18,
        "size": 11,
        "flying": True,
        "regeneration": 0.0,
        "color": (200, 140, 255),
    },
    "regenerating": {
        "max_hp": 200,
        "speed": 55,
        "armor": 2,
        "resistance": 0.05,
        "reward": 16,
        "size": 12,
        "flying": False,
        "regeneration": 3.0,  # hp per second
        "color": (140, 255, 140),
    },
    "elite": {
        "max_hp": 420,
        "speed": 65,
        "armor": 6,
        "resistance": 0.10,
        "reward": 40,
        "size": 14,
        "flying": False,
        "regeneration": 0.0,
        "color": (255, 120, 120),
    },
}

ENEMY_DESCRIPTIONS = {
    "basic": "Standard frontline attacker.",
    "fast": "Swift and fragile; rushes the Bastion.",
    "armored": "Thick plating reduces physical damage.",
    "heavy": "Slow but extremely durable.",
    "flying": "Moves over terrain; only ranged towers can target.",
    "regenerating": "Slowly restores health over time.",
    "elite": "Balanced, tough, and rewarding.",
}

# ---------------------------------------------------------------------------
# Bosses
# ---------------------------------------------------------------------------
BOSS_STATS = {
    "void_reaver": {
        "max_hp": 4500,
        "speed": 28,
        "armor": 10,
        "resistance": 0.20,
        "reward": 500,
        "size": 30,
        "flying": False,
        "color": (180, 60, 220),
        "abilities": ["teleport", "void_bolt"],
    },
    "flame_titan": {
        "max_hp": 6200,
        "speed": 22,
        "armor": 6,
        "resistance": 0.40,
        "reward": 650,
        "size": 34,
        "flying": False,
        "color": (255, 90, 40),
        "abilities": ["fire_wave", "ember_strike"],
    },
    "storm_colossus": {
        "max_hp": 5400,
        "speed": 25,
        "armor": 8,
        "resistance": 0.10,
        "reward": 580,
        "size": 32,
        "flying": True,
        "color": (100, 160, 255),
        "abilities": ["chain_lightning", "gale_push"],
    },
}

# ---------------------------------------------------------------------------
# Wave definitions (data-driven)
# Each wave: enemies list of {type, count, delay_ms, hp_mult, speed_mult}
# intermission_ms is the preparation time after the wave clears.
# ---------------------------------------------------------------------------
WAVES: dict[int, dict] = {}

# Map 1 waves (introductory)
WAVES[1] = {
    "enemies": [
        {"type": "basic", "count": 8, "delay_ms": 700},
        {"type": "basic", "count": 6, "delay_ms": 600},
        {"type": "fast", "count": 4, "delay_ms": 500},
        {"type": "armored", "count": 3, "delay_ms": 900},
    ],
    "intermission_ms": 12000,
}
WAVES[2] = {
    "enemies": [
        {"type": "basic", "count": 10, "delay_ms": 550},
        {"type": "fast", "count": 6, "delay_ms": 450},
        {"type": "flying", "count": 3, "delay_ms": 800},
        {"type": "armored", "count": 4, "delay_ms": 850},
    ],
    "intermission_ms": 12000,
}
WAVES[3] = {
    "enemies": [
        {"type": "basic", "count": 12, "delay_ms": 450},
        {"type": "fast", "count": 8, "delay_ms": 400},
        {"type": "regenerating", "count": 3, "delay_ms": 1000},
        {"type": "armored", "count": 5, "delay_ms": 700},
        {"type": "heavy", "count": 2, "delay_ms": 1200},
    ],
    "intermission_ms": 14000,
}
WAVES[4] = {
    "enemies": [
        {"type": "fast", "count": 10, "delay_ms": 350},
        {"type": "flying", "count": 5, "delay_ms": 600},
        {"type": "regenerating", "count": 4, "delay_ms": 900},
        {"type": "elite", "count": 3, "delay_ms": 1000},
    ],
    "intermission_ms": 14000,
}
WAVES[5] = {
    "enemies": [
        {"type": "basic", "count": 15, "delay_ms": 350},
        {"type": "fast", "count": 10, "delay_ms": 300},
        {"type": "armored", "count": 6, "delay_ms": 600},
        {"type": "heavy", "count": 3, "delay_ms": 1000},
        {"type": "flying", "count": 4, "delay_ms": 700},
        {"type": "elite", "count": 4, "delay_ms": 900},
    ],
    "intermission_ms": 16000,
    "boss": "void_reaver",
    "boss_hp_mult": 0.6,
}

# Map 2 waves
WAVES[6] = {
    "enemies": [
        {"type": "fast", "count": 12, "delay_ms": 300},
        {"type": "armored", "count": 6, "delay_ms": 650},
        {"type": "flying", "count": 4, "delay_ms": 700},
    ],
    "intermission_ms": 14000,
}
WAVES[7] = {
    "enemies": [
        {"type": "basic", "count": 14, "delay_ms": 320},
        {"type": "regenerating", "count": 5, "delay_ms": 850},
        {"type": "elite", "count": 4, "delay_ms": 900},
        {"type": "heavy", "count": 3, "delay_ms": 1100},
    ],
    "intermission_ms": 15000,
}
WAVES[8] = {
    "enemies": [
        {"type": "flying", "count": 8, "delay_ms": 500},
        {"type": "fast", "count": 12, "delay_ms": 280},
        {"type": "armored", "count": 6, "delay_ms": 600},
        {"type": "regenerating", "count": 4, "delay_ms": 900},
    ],
    "intermission_ms": 15000,
}
WAVES[9] = {
    "enemies": [
        {"type": "elite", "count": 6, "delay_ms": 700},
        {"type": "heavy", "count": 4, "delay_ms": 1000},
        {"type": "flying", "count": 6, "delay_ms": 550},
        {"type": "basic", "count": 20, "delay_ms": 250},
    ],
    "intermission_ms": 17000,
}
WAVES[10] = {
    "enemies": [
        {"type": "basic", "count": 25, "delay_ms": 220},
        {"type": "fast", "count": 15, "delay_ms": 240},
        {"type": "armored", "count": 8, "delay_ms": 500},
        {"type": "heavy", "count": 4, "delay_ms": 900},
        {"type": "flying", "count": 5, "delay_ms": 600},
        {"type": "regenerating", "count": 4, "delay_ms": 950},
        {"type": "elite", "count": 5, "delay_ms": 850},
    ],
    "intermission_ms": 18000,
    "boss": "flame_titan",
    "boss_hp_mult": 0.7,
}

# Map 3 waves
WAVES[11] = {
    "enemies": [
        {"type": "armored", "count": 8, "delay_ms": 500},
        {"type": "regenerating", "count": 5, "delay_ms": 800},
        {"type": "flying", "count": 5, "delay_ms": 600},
    ],
    "intermission_ms": 15000,
}
WAVES[12] = {
    "enemies": [
        {"type": "elite", "count": 6, "delay_ms": 600},
        {"type": "heavy", "count": 4, "delay_ms": 900},
        {"type": "fast", "count": 14, "delay_ms": 260},
    ],
    "intermission_ms": 16000,
}
WAVES[13] = {
    "enemies": [
        {"type": "flying", "count": 10, "delay_ms": 450},
        {"type": "armored", "count": 8, "delay_ms": 550},
        {"type": "regenerating", "count": 6, "delay_ms": 800},
        {"type": "elite", "count": 5, "delay_ms": 750},
    ],
    "intermission_ms": 17000,
}
WAVES[14] = {
    "enemies": [
        {"type": "heavy", "count": 6, "delay_ms": 800},
        {"type": "fast", "count": 16, "delay_ms": 240},
        {"type": "flying", "count": 8, "delay_ms": 500},
        {"type": "elite", "count": 6, "delay_ms": 700},
    ],
    "intermission_ms": 18000,
}
WAVES[15] = {
    "enemies": [
        {"type": "basic", "count": 30, "delay_ms": 200},
        {"type": "fast", "count": 20, "delay_ms": 220},
        {"type": "armored", "count": 10, "delay_ms": 400},
        {"type": "heavy", "count": 6, "delay_ms": 800},
        {"type": "flying", "count": 8, "delay_ms": 450},
        {"type": "regenerating", "count": 6, "delay_ms": 850},
        {"type": "elite", "count": 7, "delay_ms": 750},
    ],
    "intermission_ms": 20000,
    "boss": "storm_colossus",
    "boss_hp_mult": 0.8,
}

# Map 4 waves (branching routes)
WAVES[16] = {
    "enemies": [
        {"type": "fast", "count": 14, "delay_ms": 280},
        {"type": "flying", "count": 6, "delay_ms": 550},
        {"type": "armored", "count": 7, "delay_ms": 600},
    ],
    "intermission_ms": 16000,
}
WAVES[17] = {
    "enemies": [
        {"type": "elite", "count": 8, "delay_ms": 600},
        {"type": "heavy", "count": 5, "delay_ms": 900},
        {"type": "regenerating", "count": 6, "delay_ms": 750},
        {"type": "flying", "count": 7, "delay_ms": 500},
    ],
    "intermission_ms": 17000,
}
WAVES[18] = {
    "enemies": [
        {"type": "basic", "count": 24, "delay_ms": 240},
        {"type": "fast", "count": 18, "delay_ms": 260},
        {"type": "armored", "count": 9, "delay_ms": 450},
        {"type": "heavy", "count": 5, "delay_ms": 850},
    ],
    "intermission_ms": 18000,
}
WAVES[19] = {
    "enemies": [
        {"type": "flying", "count": 10, "delay_ms": 420},
        {"type": "elite", "count": 8, "delay_ms": 650},
        {"type": "heavy", "count": 6, "delay_ms": 800},
        {"type": "regenerating", "count": 7, "delay_ms": 720},
    ],
    "intermission_ms": 19000,
}
WAVES[20] = {
    "enemies": [
        {"type": "basic", "count": 32, "delay_ms": 190},
        {"type": "fast", "count": 22, "delay_ms": 210},
        {"type": "armored", "count": 12, "delay_ms": 380},
        {"type": "heavy", "count": 7, "delay_ms": 700},
        {"type": "flying", "count": 9, "delay_ms": 420},
        {"type": "regenerating", "count": 7, "delay_ms": 780},
        {"type": "elite", "count": 8, "delay_ms": 700},
    ],
    "intermission_ms": 22000,
    "boss": "void_reaver",
    "boss_hp_mult": 0.9,
}

# Map 5 waves (dual routes)
WAVES[21] = {
    "enemies": [
        {"type": "elite", "count": 10, "delay_ms": 500},
        {"type": "heavy", "count": 6, "delay_ms": 800},
        {"type": "flying", "count": 8, "delay_ms": 480},
    ],
    "intermission_ms": 18000,
}
WAVES[22] = {
    "enemies": [
        {"type": "regenerating", "count": 8, "delay_ms": 700},
        {"type": "elite", "count": 10, "delay_ms": 550},
        {"type": "heavy", "count": 7, "delay_ms": 750},
        {"type": "flying", "count": 9, "delay_ms": 460},
    ],
    "intermission_ms": 19000,
}
WAVES[23] = {
    "enemies": [
        {"type": "basic", "count": 35, "delay_ms": 180},
        {"type": "fast", "count": 25, "delay_ms": 200},
        {"type": "armored", "count": 14, "delay_ms": 360},
        {"type": "heavy", "count": 8, "delay_ms": 650},
    ],
    "intermission_ms": 20000,
}
WAVES[24] = {
    "enemies": [
        {"type": "flying", "count": 12, "delay_ms": 400},
        {"type": "elite", "count": 12, "delay_ms": 500},
        {"type": "heavy", "count": 8, "delay_ms": 680},
        {"type": "regenerating", "count": 9, "delay_ms": 700},
    ],
    "intermission_ms": 21000,
}
WAVES[25] = {
    "enemies": [
        {"type": "basic", "count": 40, "delay_ms": 160},
        {"type": "fast", "count": 30, "delay_ms": 180},
        {"type": "armored", "count": 16, "delay_ms": 340},
        {"type": "heavy", "count": 10, "delay_ms": 600},
        {"type": "flying", "count": 12, "delay_ms": 380},
        {"type": "regenerating", "count": 10, "delay_ms": 680},
        {"type": "elite", "count": 12, "delay_ms": 620},
    ],
    "intermission_ms": 25000,
    "boss": "flame_titan",
    "boss_hp_mult": 1.0,
}

# Endless wave template: wave 26+ scales by index.
ENDLESS_BASE_WAVE = 25

# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------
ACHIEVEMENTS: dict[str, dict] = {
    "first_blood": {
        "title": {"ru": "Первая кровь", "en": "First Blood"},
        "desc": {"ru": "Уничтожь первого врага.", "en": "Destroy your first enemy."},
        "condition": "kills_total >= 1",
        "reward": 25,
    },
    "tower_builder": {
        "title": {"ru": "Строитель башен", "en": "Tower Builder"},
        "desc": {"ru": "Построй любую башню.", "en": "Build your first tower."},
        "condition": "towers_built >= 1",
        "reward": 25,
    },
    "master_builder": {
        "title": {"ru": "Мастер строительства", "en": "Master Builder"},
        "desc": {"ru": "Построй 10 башен за одно прохождение карты.", "en": "Build 10 towers in a single map run."},
        "condition": "towers_built_run >= 10",
        "reward": 50,
    },
    "full_upgrade": {
        "title": {"ru": "Максимальное улучшение", "en": "Full Upgrade"},
        "desc": {"ru": "Улучшите башню до 3 уровня.", "en": "Upgrade a tower to level 3."},
        "condition": "max_tower_level >= 3",
        "reward": 50,
    },
    "wave_survivor": {
        "title": {"ru": "Выживший", "en": "Wave Survivor"},
        "desc": {"ru": "Пройдите 10 волн.", "en": "Survive 10 waves."},
        "condition": "waves_survived >= 10",
        "reward": 75,
    },
    "boss_slayer": {
        "title": {"ru": "Битва с боссом", "en": "Boss Slayer"},
        "desc": {"ru": "Победите первого босса.", "en": "Defeat your first boss."},
        "condition": "bosses_defeated >= 1",
        "reward": 100,
    },
    "perfect_defense": {
        "title": {"ru": "Идеальная защита", "en": "Perfect Defense"},
        "desc": {
            "ru": "Завершите миссию, не потеряв очко здоровья базы.",
            "en": "Complete a mission without losing base health.",
        },
        "condition": "damage_taken == 0 and mission_complete",
        "reward": 150,
    },
    "all_towers": {
        "title": {"ru": "Арсенал", "en": "Arsenal"},
        "desc": {"ru": "Построй каждый тип башни хотя бы раз.", "en": "Build every tower type at least once."},
        "condition": "tower_types_built >= 6",
        "reward": 100,
    },
    "endless_warrior": {
        "title": {"ru": "Вечный воин", "en": "Endless Warrior"},
        "desc": {"ru": "Достигните 30-й волны в бесконечном режиме.", "en": "Reach wave 30 in Endless mode."},
        "condition": "endless_wave >= 30",
        "reward": 200,
    },
    "campaign_conqueror": {
        "title": {"ru": "Завоеватель kampanii", "en": "Campaign Conqueror"},
        "desc": {"ru": "Пройдите все 5 карт кампании.", "en": "Complete all 5 campaign maps."},
        "condition": "campaign_complete",
        "reward": 300,
    },
    "wealthy": {
        "title": {"ru": "Богач", "en": "Wealthy"},
        "desc": {"ru": "Накопите 500 единиц валюты одновременно.", "en": "Hold 500 currency at once."},
        "condition": "currency_peak >= 500",
        "reward": 75,
    },
    "flying_counter": {
        "title": {"ru": "П超过 ceiling", "en": "Ceiling Breaker"},
        "desc": {"ru": "Уничтожьте 20 летающих врагов.", "en": "Destroy 20 flying enemies."},
        "condition": "flying_kills >= 20",
        "reward": 75,
    },
}

# ---------------------------------------------------------------------------
# Campaign maps
# ---------------------------------------------------------------------------
MAP_ORDER = ["wastes", "spire", "delta", "rift", "bastion"]
MAP_NAMES = {
    "wastes": {"ru": "Пустоши", "en": "The Wastes"},
    "spire": {"ru": "Шпиль", "en": "The Spire"},
    "delta": {"ru": "Дельта", "en": "The Delta"},
    "rift": {"ru": "Разлом", "en": "The Rift"},
    "bastion": {"ru": "Бастион", "en": "The Bastion"},
}
MAP_DESCRIPTIONS = {
    "wastes": {"ru": "Введение в защиту Бастиона.", "en": "Introduction to the Bastion's defense."},
    "spire": {"ru": "Летающие враги появляются над шпилем.", "en": "Flying enemies appear above the spire."},
    "delta": {
        "ru": "Ветвящиеся маршруты требуют разделенной обороны.",
        "en": "Branching routes require split defense.",
    },
    "rift": {"ru": "Два маршрута одновременно.", "en": "Two simultaneous routes."},
    "bastion": {"ru": "Финальный рубеж с удвоенными путями.", "en": "Final line with doubled paths."},
}
MAP_UNLOCK_COST = {
    "wastes": 0,
    "spire": 300,
    "delta": 700,
    "rift": 1200,
    "bastion": 1800,
}
# wave index range per map (inclusive)
MAP_WAVE_RANGES = {
    "wastes": (1, 5),
    "spire": (6, 10),
    "delta": (11, 15),
    "rift": (16, 20),
    "bastion": (21, 25),
}

# Star thresholds (percentage of base health remaining)
STAR_THRESHOLDS = [50, 75, 100]

TARGET_MODES = ["first", "last", "strongest", "weakest", "closest"]

GAME_SPEEDS = [0.5, 1.0, 1.5, 2.0, 3.0]

# ---------------------------------------------------------------------------
# Derived helpers
# ---------------------------------------------------------------------------


def wave_for_map(map_key: str) -> tuple[int, int]:
    return MAP_WAVE_RANGES[map_key]


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
