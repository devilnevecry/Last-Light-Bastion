"""Resource loading and graphics caching."""

from __future__ import annotations

import os
from functools import lru_cache

import graphics
import pygame


@lru_cache(maxsize=None)
def font_path(preferred: tuple[str, ...] = ("arial.ttf", "segoeui.ttf")) -> str | None:
    """Return the path to a Cyrillic-capable TTF font, or None."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = os.path.join(windir, "Fonts")
    for name in preferred:
        candidate = os.path.join(fonts_dir, name)
        if os.path.isfile(candidate):
            return candidate
    return None


@lru_cache(maxsize=None)
def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    path = font_path()
    if path is not None:
        try:
            return pygame.font.Font(path, size)
        except pygame.error:
            pass
    return pygame.font.SysFont(None, size, bold=bold)


class GraphicsCache:
    """Caches generated surfaces keyed by (kind, args)."""

    def __init__(self) -> None:
        self._cache: dict[tuple, pygame.Surface] = {}

    def tower(self, tower_id: str, size: int = 34) -> pygame.Surface:
        key = ("tower", tower_id, size)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_tower_image(tower_id, size)
            self._cache[key] = surf
        return surf

    def enemy(self, enemy_id: str, size: int = 20, flying: bool = False) -> pygame.Surface:
        key = ("enemy", enemy_id, size, flying)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_enemy_image(enemy_id, size, flying)
            self._cache[key] = surf
        return surf

    def boss(self, boss_id: str, size: int = 46) -> pygame.Surface:
        key = ("boss", boss_id, size)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_boss_image(boss_id, size)
            self._cache[key] = surf
        return surf

    def projectile(self, proj_id: str, size: int = 10) -> pygame.Surface:
        key = ("projectile", proj_id, size)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_projectile_image(proj_id, size)
            self._cache[key] = surf
        return surf

    def particle(self, color: tuple[int, int, int], size: int = 6) -> pygame.Surface:
        key = ("particle", color, size)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_particle_image(color, size)
            self._cache[key] = surf
        return surf

    def health_bar(self, width: int = 24, height: int = 5) -> pygame.Surface:
        key = ("health_bar", width, height)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_health_bar(width, height)
            self._cache[key] = surf
        return surf

    def range_circle(self, radius: int) -> pygame.Surface:
        key = ("range", radius)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_range_circle(radius)
            self._cache[key] = surf
        return surf

    def placement_tile(self, size: int = 32, valid: bool = True) -> pygame.Surface:
        key = ("placement", size, valid)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_placement_tile(size, valid)
            self._cache[key] = surf
        return surf

    def explosion(self, index: int, count: int = 6, max_radius: int = 30) -> pygame.Surface:
        key = ("explosion", index, count, max_radius)
        surf = self._cache.get(key)
        if surf is None:
            frames = graphics.make_explosion_frames(count, max_radius)
            # store all frames under index 0 and return by index
            self._cache[("explosion_all", count, max_radius)] = frames
            surf = frames[index]
            self._cache[key] = surf
        return surf

    def explosion_frames(self, count: int = 6, max_radius: int = 30) -> list[pygame.Surface]:
        key = ("explosion_all", count, max_radius)
        frames = self._cache.get(key)
        if frames is None:
            frames = graphics.make_explosion_frames(count, max_radius)
            self._cache[key] = frames
        return frames

    def ui_panel(self, width: int, height: int) -> pygame.Surface:
        key = ("panel", width, height)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_ui_panel(width, height)
            self._cache[key] = surf
        return surf

    def button(self, width: int, height: int, active: bool = True) -> pygame.Surface:
        key = ("button", width, height, active)
        surf = self._cache.get(key)
        if surf is None:
            surf = graphics.make_button(width, height, active)
            self._cache[key] = surf
        return surf


GRAPHICS = GraphicsCache()
