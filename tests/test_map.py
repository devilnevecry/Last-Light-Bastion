"""Tests for the map system, pathfinding, and placement validation."""

from __future__ import annotations

import itertools

from base import *  # noqa: F403
from map import ALL_MAPS, _line_tiles, validate_all_maps


def test_all_maps_validate():
    errors = validate_all_maps()
    for key, errs in errors.items():
        assert not errs, f"map {key} has validation errors: {errs}"


def test_five_maps():
    assert len(ALL_MAPS) == 5
    assert set(ALL_MAPS) == {"wastes", "spire", "delta", "rift", "bastion"}


def test_line_tiles():
    tiles = _line_tiles(1, 9, 5, 9)
    assert (1, 9) in tiles
    assert (5, 9) in tiles
    assert all(y == 9 for _, y in tiles)


def test_route_has_entry_and_exit():
    for m in ALL_MAPS.values():
        assert len(m.routes) >= 1
        for route in m.routes:
            assert len(route) >= 2
            start = route[0]
            end = route[-1]
            assert m.in_bounds(*start)
            assert m.in_bounds(*end)


def test_can_place_tower_excludes_path_and_obstacle():
    m = ALL_MAPS["wastes"]
    # path cell cannot host tower
    route = m.routes[0]
    assert m.is_path(*route[0])
    assert not m.can_place_tower(*route[0])
    # obstacle cell cannot host tower
    obs = next(iter(m.obstacles))
    assert m.is_obstacle(*obs)
    assert not m.can_place_tower(*obs)
    # out of bounds
    assert not m.can_place_tower(-1, 0)
    assert not m.can_place_tower(m.cols, 0)


def test_route_never_touches_obstacles():
    for m in ALL_MAPS.values():
        for route in m.routes:
            for (x0, y0), (x1, y1) in itertools.pairwise(route):
                for tx, ty in _line_tiles(x0, y0, x1, y1):
                    assert not m.is_obstacle(tx, ty), f"obstacle on route {m.key}"


def test_multi_route_maps():
    assert len(ALL_MAPS["delta"].routes) == 2
    assert len(ALL_MAPS["rift"].routes) == 2
    assert len(ALL_MAPS["bastion"].routes) == 2


def test_placement_tiles_available():
    for m in ALL_MAPS.values():
        tiles = m.placement_tiles()
        assert len(tiles) > 0
        for x, y in tiles:
            assert m.can_place_tower(x, y)


def test_path_connectivity_no_gaps():
    """Every route segment is a contiguous line; no floating waypoints."""
    for m in ALL_MAPS.values():
        for route in m.routes:
            for (x0, y0), (x1, y1) in itertools.pairwise(route):
                seg = _line_tiles(x0, y0, x1, y1)
                # consecutive tiles in the line are adjacent (8-connected)
                for (ax, ay), (bx, by) in itertools.pairwise(seg):
                    assert max(abs(bx - ax), abs(by - ay)) <= 1
