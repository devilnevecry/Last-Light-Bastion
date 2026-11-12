"""Programmatic pixel-art style graphics generation (no external assets)."""

from __future__ import annotations

import math

import pygame
from config import (
    COLOR_ACCENT,
    COLOR_ARC,
    COLOR_CANNON,
    COLOR_DANGER,
    COLOR_FROST,
    COLOR_GOLD,
    COLOR_HEALTH,
    COLOR_PANEL,
    COLOR_PANEL_BRIGHT,
    COLOR_PLACEMENT,
    COLOR_POISON,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
)


def _circle(surface: pygame.Surface, color, center, radius) -> None:
    pygame.draw.circle(surface, color, center, radius)


def _ring(surface: pygame.Surface, color, center, radius, width: int = 2) -> None:
    pygame.draw.circle(surface, color, center, radius, width)


def make_tower_image(tower_id: str, size: int = 34) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    body = size // 3

    if tower_id == "archer":
        # wooden post + green top
        pygame.draw.rect(surf, (139, 90, 43), (cx - 5, cy + 2, 10, size - cy - 2))
        pygame.draw.polygon(surf, (90, 160, 90), [(cx - body, cy - 2), (cx + body, cy - 2), (cx, cy - body)])
        _ring(surf, COLOR_TEXT, (cx, cy - body // 2), 6, 2)
    elif tower_id == "cannon":
        pygame.draw.rect(surf, (110, 90, 70), (cx - 6, cy + 2, 12, size - cy - 2))
        pygame.draw.rect(surf, COLOR_CANNON, (cx - body, cy - body, body * 2, body * 2), 3)
        pygame.draw.line(surf, COLOR_CANNON, (cx, cy - body), (cx, cy - body - 8), 4)
    elif tower_id == "frost":
        pygame.draw.rect(surf, (90, 140, 180), (cx - 5, cy + 2, 10, size - cy - 2))
        pygame.draw.polygon(
            surf,
            COLOR_FROST,
            [(cx - body, cy - 2), (cx + body, cy - 2), (cx, cy - body)],
        )
        for off in (-6, 0, 6):
            _ring(surf, COLOR_ACCENT, (cx + off, cy - body // 2), 4, 2)
    elif tower_id == "arc":
        pygame.draw.rect(surf, (100, 80, 140), (cx - 5, cy + 2, 10, size - cy - 2))
        pygame.draw.circle(surf, COLOR_ARC, (cx, cy - body), body)
        _ring(surf, COLOR_TEXT, (cx, cy - body), body - 4, 2)
        pygame.draw.line(surf, COLOR_ARC, (cx - 4, cy - body + 6), (cx + 4, cy - body - 6), 2)
    elif tower_id == "poison":
        pygame.draw.rect(surf, (70, 120, 70), (cx - 5, cy + 2, 10, size - cy - 2))
        pygame.draw.circle(surf, COLOR_POISON, (cx, cy - body), body - 2)
        _ring(surf, COLOR_DANGER, (cx, cy - body), body, 2)
        pygame.draw.line(surf, COLOR_POISON, (cx - 5, cy - body + 5), (cx + 5, cy - body + 5), 2)
    elif tower_id == "support":
        pygame.draw.rect(surf, (140, 120, 200), (cx - 5, cy + 2, 10, size - cy - 2))
        pygame.draw.circle(surf, COLOR_GOLD, (cx, cy - body), body)
        _ring(surf, COLOR_TEXT, (cx, cy - body), body - 4, 2)
        pygame.draw.line(surf, COLOR_GOLD, (cx - 6, cy - body), (cx + 6, cy - body), 2)
    else:
        pygame.draw.rect(surf, COLOR_TEXT, (cx - 6, cy - 6, 12, 12))
    return surf


def make_enemy_image(enemy_id: str, size: int = 20, flying: bool = False) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    from config import ENEMY_STATS

    color = ENEMY_STATS[enemy_id]["color"]

    if enemy_id == "basic":
        pygame.draw.rect(surf, color, (cx - 5, cy - 5, 10, 10))
        _ring(surf, COLOR_TEXT, (cx, cy), 7, 2)
    elif enemy_id == "fast":
        points = [(cx, cy - 6), (cx + 5, cy + 4), (cx - 5, cy + 4)]
        pygame.draw.polygon(surf, color, points)
    elif enemy_id == "armored":
        pygame.draw.rect(surf, color, (cx - 6, cy - 6, 12, 12))
        pygame.draw.rect(surf, COLOR_TEXT, (cx - 3, cy - 6, 6, 12))
    elif enemy_id == "heavy":
        pygame.draw.rect(surf, color, (cx - 7, cy - 7, 14, 14))
        _ring(surf, COLOR_TEXT, (cx, cy), 9, 3)
    elif enemy_id == "flying":
        pygame.draw.circle(surf, color, (cx, cy), 6)
        pygame.draw.ellipse(surf, COLOR_ACCENT, (cx - 8, cy - 3, 16, 6))
        if flying:
            pygame.draw.line(surf, COLOR_TEXT, (cx - 5, cy - 4), (cx - 5, cy - 8), 2)
            pygame.draw.line(surf, COLOR_TEXT, (cx + 5, cy - 4), (cx + 5, cy - 8), 2)
    elif enemy_id == "regenerating":
        pygame.draw.circle(surf, color, (cx, cy), 6)
        _ring(surf, COLOR_POISON, (cx, cy), 8, 2)
    elif enemy_id == "elite":
        pygame.draw.rect(surf, color, (cx - 6, cy - 6, 12, 12))
        pygame.draw.line(surf, COLOR_TEXT, (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
        pygame.draw.line(surf, COLOR_TEXT, (cx + 4, cy - 4), (cx - 4, cy + 4), 2)
    else:
        pygame.draw.circle(surf, color, (cx, cy), 5)
    return surf


def make_boss_image(boss_id: str, size: int = 46) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    from config import BOSS_STATS

    color = BOSS_STATS[boss_id]["color"]

    if boss_id == "void_reaver":
        pygame.draw.circle(surf, color, (cx, cy), 16)
        _ring(surf, COLOR_TEXT, (cx, cy), 20, 3)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            x = cx + math.cos(rad) * 20
            y = cy + math.sin(rad) * 20
            pygame.draw.line(surf, color, (cx, cy), (x, y), 3)
    elif boss_id == "flame_titan":
        pygame.draw.rect(surf, color, (cx - 16, cy - 14, 32, 28), border_radius=6)
        _ring(surf, COLOR_DANGER, (cx, cy), 19, 3)
        for ang in (-30, 30):
            rad = math.radians(ang)
            pygame.draw.line(
                surf,
                COLOR_DANGER,
                (cx + math.cos(rad) * 10, cy - 10 + math.sin(rad) * 10),
                (cx + math.cos(rad) * 26, cy - 22 + math.sin(rad) * 10),
                3,
            )
    elif boss_id == "storm_colossus":
        pygame.draw.circle(surf, color, (cx, cy), 17)
        _ring(surf, COLOR_ACCENT, (cx, cy), 22, 3)
        pygame.draw.line(surf, COLOR_ACCENT, (cx - 22, cy), (cx + 22, cy), 3)
        pygame.draw.line(surf, COLOR_ACCENT, (cx, cy - 22), (cx, cy + 22), 3)
    else:
        pygame.draw.circle(surf, color, (cx, cy), 14)
    return surf


def make_projectile_image(proj_id: str, size: int = 10) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    if proj_id == "arrow":
        pygame.draw.rect(surf, COLOR_TEXT, (cx - 2, cy - 5, 4, 10))
        pygame.draw.polygon(surf, COLOR_TEXT, [(cx - 4, cy - 5), (cx + 4, cy - 5), (cx, cy - 9)])
    elif proj_id == "shell":
        _ring(surf, COLOR_CANNON, (cx, cy), 5, 2)
        pygame.draw.circle(surf, COLOR_CANNON, (cx, cy), 2)
    elif proj_id == "ice":
        pygame.draw.circle(surf, COLOR_FROST, (cx, cy), 4)
        _ring(surf, COLOR_ACCENT, (cx, cy), 4, 2)
    elif proj_id == "arc":
        pygame.draw.circle(surf, COLOR_ARC, (cx, cy), 3)
        pygame.draw.line(surf, COLOR_ARC, (cx - 3, cy), (cx + 3, cy), 2)
    elif proj_id == "venom":
        pygame.draw.circle(surf, COLOR_POISON, (cx, cy), 4)
        pygame.draw.circle(surf, COLOR_DANGER, (cx, cy), 2)
    else:
        pygame.draw.circle(surf, COLOR_TEXT, (cx, cy), 3)
    return surf


def make_particle_image(color, size: int = 6) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    return surf


def make_health_bar(width: int = 24, height: int = 5) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surf, (60, 60, 70), surf.get_rect())
    pygame.draw.rect(surf, COLOR_HEALTH, surf.get_rect())
    return surf


def make_range_circle(radius: int, color=COLOR_PLACEMENT) -> pygame.Surface:
    diameter = radius * 2
    surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, 60), (radius, radius), radius)
    pygame.draw.circle(surf, (*color, 180), (radius, radius), radius, 2)
    return surf


def make_placement_tile(size: int = 32, valid: bool = True) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    color = COLOR_PLACEMENT if valid else COLOR_DANGER
    pygame.draw.rect(surf, (*color, 90), surf.get_rect(), border_radius=4)
    pygame.draw.rect(surf, (*color, 210), surf.get_rect(), width=2, border_radius=4)
    return surf


def make_explosion_frames(count: int = 6, max_radius: int = 30) -> list[pygame.Surface]:
    frames = []
    for i in range(count):
        r = int(max_radius * (i + 1) / count)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        alpha = max(0, 255 - int(255 * (i + 1) / (count + 1)))
        color = (255, 140, 40, alpha)
        pygame.draw.circle(surf, color, (r, r), r)
        pygame.draw.circle(surf, COLOR_GOLD, (r, r), max(1, r // 3), 2)
        frames.append(surf)
    return frames


def make_ui_panel(width: int, height: int) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill(COLOR_PANEL)
    pygame.draw.rect(surf, COLOR_PANEL_BRIGHT, surf.get_rect(), width=2, border_radius=6)
    return surf


def make_button(width: int, height: int, active: bool = True) -> pygame.Surface:
    from config import COLOR_ACCENT

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    base = COLOR_ACCENT if active else COLOR_TEXT_DIM
    surf.fill((*base, 40))
    pygame.draw.rect(surf, (*base, 210), surf.get_rect(), width=2, border_radius=6)
    return surf
