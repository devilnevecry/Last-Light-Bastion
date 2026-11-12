"""Map system: grids, routes, obstacles, placement validation."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

from config import GRID_COLS, GRID_ROWS


def _line_tiles(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Bresenham supercover-ish line of grid cells between two points."""
    tiles: list[tuple[int, int]] = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        tiles.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return tiles


@dataclass
class MapData:
    key: str
    name: str
    description: str
    cols: int = GRID_COLS
    rows: int = GRID_ROWS
    routes: list[list[tuple[int, int]]] = field(default_factory=list)
    obstacles: set[tuple[int, int]] = field(default_factory=set)
    entry_pixel: tuple[float, float] = (0.0, 0.0)
    exit_pixel: tuple[float, float] = (0.0, 0.0)
    base_pixel: tuple[float, float] = (0.0, 0.0)
    spawn_pixel: tuple[float, float] = (0.0, 0.0)

    def __post_init__(self) -> None:
        self._path_tiles: set[tuple[int, int]] = set()
        self._route_path_tiles: list[set[tuple[int, int]]] = []
        for route in self.routes:
            tiles: set[tuple[int, int]] = set()
            for (x0, y0), (x1, y1) in itertools.pairwise(route):
                for tx, ty in _line_tiles(x0, y0, x1, y1):
                    tiles.add((tx, ty))
            self._route_path_tiles.append(tiles)
            self._path_tiles |= tiles

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def is_path(self, x: int, y: int) -> bool:
        return (x, y) in self._path_tiles

    def is_obstacle(self, x: int, y: int) -> bool:
        return (x, y) in self.obstacles

    def can_place_tower(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        if self.is_path(x, y):
            return False
        if self.is_obstacle(x, y):
            return False
        return True

    def route_tiles(self, route_index: int) -> set[tuple[int, int]]:
        if 0 <= route_index < len(self._route_path_tiles):
            return self._route_path_tiles[route_index]
        return set()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.routes:
            errors.append(f"map {self.key}: no routes defined")
            return errors
        for i, route in enumerate(self.routes):
            if len(route) < 2:
                errors.append(f"map {self.key}: route {i} has fewer than 2 waypoints")
                continue
            for x, y in route:
                if not self.in_bounds(x, y):
                    errors.append(f"map {self.key}: route {i} waypoint {(x, y)} out of bounds")
            for (x0, y0), (x1, y1) in itertools.pairwise(route):
                for tx, ty in _line_tiles(x0, y0, x1, y1):
                    if not self.in_bounds(tx, ty):
                        errors.append(f"map {self.key}: route {i} segment {(x0, y0)}-{(x1, y1)} out of bounds")
                    if (tx, ty) in self.obstacles:
                        errors.append(f"map {self.key}: route {i} crosses obstacle at {(tx, ty)}")
        # path and obstacles must be disjoint
        overlap = self._path_tiles & self.obstacles
        if overlap:
            errors.append(f"map {self.key}: path overlaps obstacles at {sorted(overlap)}")
        return errors

    def placement_tiles(self) -> list[tuple[int, int]]:
        tiles = []
        for y in range(self.rows):
            for x in range(self.cols):
                if self.can_place_tower(x, y):
                    tiles.append((x, y))
        return tiles


# ---------------------------------------------------------------------------
# Map definitions
# ---------------------------------------------------------------------------


def _obstacles(*coords: tuple[int, int]) -> set[tuple[int, int]]:
    return set(coords)


def map_wastes() -> MapData:
    return MapData(
        key="wastes",
        name="The Wastes",
        description="Introduction to the Bastion's defense.",
        routes=[
            [(1, 9), (5, 9), (5, 5), (12, 5), (12, 12), (20, 12), (20, 9), (22, 9)],
        ],
        obstacles=_obstacles(
            (3, 5),
            (4, 5),
            (7, 11),
            (8, 11),
            (9, 11),
            (15, 8),
            (16, 8),
            (17, 8),
            (2, 14),
            (3, 14),
            (20, 4),
            (21, 4),
        ),
        entry_pixel=(1 * 32 + 16, 9 * 32 + 16),
        exit_pixel=(22 * 32 + 16, 9 * 32 + 16),
        base_pixel=(23 * 32 + 16, 10 * 32 + 16),
        spawn_pixel=(1 * 32 + 16, 9 * 32 + 16),
    )


def map_spire() -> MapData:
    return MapData(
        key="spire",
        name="The Spire",
        description="Flying enemies appear above the spire.",
        routes=[
            [(1, 16), (1, 10), (7, 10), (7, 4), (14, 4), (14, 10), (22, 10), (22, 16)],
        ],
        obstacles=_obstacles(
            (3, 12),
            (4, 12),
            (5, 12),
            (10, 6),
            (11, 6),
            (12, 6),
            (13, 6),
            (7, 13),
            (8, 13),
            (9, 13),
            (19, 13),
            (20, 13),
        ),
        entry_pixel=(1 * 32 + 16, 16 * 32 + 16),
        exit_pixel=(22 * 32 + 16, 16 * 32 + 16),
        base_pixel=(23 * 32 + 16, 10 * 32 + 16),
        spawn_pixel=(1 * 32 + 16, 16 * 32 + 16),
    )


def map_delta() -> MapData:
    return MapData(
        key="delta",
        name="The Delta",
        description="Branching routes require split defense.",
        routes=[
            [(1, 8), (6, 8), (6, 4), (14, 4), (14, 8), (20, 8), (22, 8)],
            [(1, 8), (6, 8), (6, 12), (14, 12), (14, 8), (20, 8), (22, 8)],
        ],
        obstacles=_obstacles(
            (9, 8),
            (10, 8),
            (11, 8),
            (3, 4),
            (4, 4),
            (3, 12),
            (4, 12),
            (17, 4),
            (18, 4),
            (17, 12),
            (18, 12),
        ),
        entry_pixel=(1 * 32 + 16, 8 * 32 + 16),
        exit_pixel=(22 * 32 + 16, 8 * 32 + 16),
        base_pixel=(23 * 32 + 16, 10 * 32 + 16),
        spawn_pixel=(1 * 32 + 16, 8 * 32 + 16),
    )


def map_rift() -> MapData:
    return MapData(
        key="rift",
        name="The Rift",
        description="Two simultaneous routes.",
        routes=[
            [(1, 6), (8, 6), (8, 2), (16, 2), (16, 6), (22, 6)],
            [(1, 14), (8, 14), (8, 16), (16, 16), (16, 14), (22, 14)],
        ],
        obstacles=_obstacles(
            (4, 10),
            (5, 10),
            (6, 10),
            (18, 10),
            (19, 10),
            (20, 10),
            (3, 3),
            (4, 3),
            (3, 17),
            (4, 17),
        ),
        entry_pixel=(1 * 32 + 16, 10 * 32 + 16),
        exit_pixel=(22 * 32 + 16, 10 * 32 + 16),
        base_pixel=(23 * 32 + 16, 10 * 32 + 16),
        spawn_pixel=(1 * 32 + 16, 10 * 32 + 16),
    )


def map_bastion() -> MapData:
    return MapData(
        key="bastion",
        name="The Bastion",
        description="Final line with doubled paths.",
        routes=[
            [(1, 5), (6, 5), (6, 2), (12, 2), (12, 8), (18, 8), (18, 5), (22, 5)],
            [(1, 13), (6, 13), (6, 16), (12, 16), (12, 10), (18, 10), (18, 13), (22, 13)],
        ],
        obstacles=_obstacles(
            (9, 8),
            (10, 8),
            (11, 8),
            (3, 2),
            (4, 2),
            (3, 16),
            (4, 16),
            (17, 2),
            (18, 2),
            (17, 16),
            (18, 16),
        ),
        entry_pixel=(1 * 32 + 16, 10 * 32 + 16),
        exit_pixel=(22 * 32 + 16, 10 * 32 + 16),
        base_pixel=(23 * 32 + 16, 10 * 32 + 16),
        spawn_pixel=(1 * 32 + 16, 10 * 32 + 16),
    )


ALL_MAPS: dict[str, MapData] = {
    "wastes": map_wastes(),
    "spire": map_spire(),
    "delta": map_delta(),
    "rift": map_rift(),
    "bastion": map_bastion(),
}


def validate_all_maps() -> dict[str, list[str]]:
    return {key: m.validate() for key, m in ALL_MAPS.items()}
