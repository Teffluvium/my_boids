"""Tests for spatial_grid.py"""

import pygame as pg
import pytest

from my_boids.boids import Boid
from my_boids.spatial_grid import SpatialGrid


@pytest.fixture
def grid():
    """Return a spatial grid with cell size of 100."""
    return SpatialGrid(cell_size=100)


@pytest.fixture
def boids_in_grid():
    """Return a list of boids positioned in a grid pattern."""
    return [
        Boid(pos=pg.Vector2(50, 50)),  # Cell (0, 0)
        Boid(pos=pg.Vector2(150, 50)),  # Cell (1, 0)
        Boid(pos=pg.Vector2(50, 150)),  # Cell (0, 1)
        Boid(pos=pg.Vector2(150, 150)),  # Cell (1, 1)
        Boid(pos=pg.Vector2(250, 250)),  # Cell (2, 2)
    ]


def test_spatial_grid_initialization(grid):
    """Test that a spatial grid initializes correctly."""
    assert grid.cell_size == 100
    assert len(grid.grid) == 0


def test_insert_single_boid(grid):
    """Test inserting a single boid into the grid."""
    boid = Boid(pos=pg.Vector2(50, 50))
    grid.insert(boid)

    assert grid.get_boid_count() == 1
    assert grid.get_cell_count() == 1


def test_insert_multiple_boids_same_cell(grid):
    """Test inserting multiple boids into the same cell."""
    boid1 = Boid(pos=pg.Vector2(50, 50))
    boid2 = Boid(pos=pg.Vector2(75, 75))

    grid.insert(boid1)
    grid.insert(boid2)

    assert grid.get_boid_count() == 2
    assert grid.get_cell_count() == 1


def test_insert_multiple_boids_different_cells(grid, boids_in_grid):
    """Test inserting boids into different cells."""
    for boid in boids_in_grid:
        grid.insert(boid)

    assert grid.get_boid_count() == 5
    assert grid.get_cell_count() == 5


def test_clear_grid(grid, boids_in_grid):
    """Test clearing all boids from the grid."""
    for boid in boids_in_grid:
        grid.insert(boid)

    assert grid.get_boid_count() == 5

    grid.clear()

    assert grid.get_boid_count() == 0
    assert grid.get_cell_count() == 0


def test_get_nearby_boids_within_radius(grid):
    """Test finding boids within a search radius."""
    boid1 = Boid(pos=pg.Vector2(50, 50))
    boid2 = Boid(pos=pg.Vector2(60, 60))
    boid3 = Boid(pos=pg.Vector2(200, 200))

    grid.insert(boid1)
    grid.insert(boid2)
    grid.insert(boid3)

    # Search near boid1, should find boid1 and boid2 but not boid3
    nearby = grid.get_nearby_boids(pg.Vector2(50, 50), search_radius=50)

    assert len(nearby) == 2
    assert boid1 in nearby
    assert boid2 in nearby
    assert boid3 not in nearby


def test_get_nearby_boids_across_cells(grid):
    """Test finding boids across multiple cells."""
    boid1 = Boid(pos=pg.Vector2(95, 95))  # Near edge of cell (0, 0)
    boid2 = Boid(pos=pg.Vector2(105, 105))  # Near edge of cell (1, 1)

    grid.insert(boid1)
    grid.insert(boid2)

    # Search at the boundary, should find both boids
    nearby = grid.get_nearby_boids(pg.Vector2(100, 100), search_radius=20)

    assert len(nearby) == 2
    assert boid1 in nearby
    assert boid2 in nearby


def test_get_nearby_boids_empty_cells(grid):
    """Test searching in an area with no boids."""
    boid = Boid(pos=pg.Vector2(50, 50))
    grid.insert(boid)

    # Search far away from any boids
    nearby = grid.get_nearby_boids(pg.Vector2(500, 500), search_radius=50)

    assert len(nearby) == 0


def test_get_nearby_boids_large_radius(grid, boids_in_grid):
    """Test finding boids with a large search radius."""
    for boid in boids_in_grid:
        grid.insert(boid)

    # Search with a large radius that covers all boids
    nearby = grid.get_nearby_boids(pg.Vector2(150, 150), search_radius=200)

    assert len(nearby) == 5


def test_get_nearby_boids_zero_radius(grid):
    """Test finding boids with zero search radius."""
    boid = Boid(pos=pg.Vector2(50, 50))
    grid.insert(boid)

    # Search with zero radius at exact boid position
    nearby = grid.get_nearby_boids(pg.Vector2(50, 50), search_radius=0)

    # Should find the boid at distance 0
    assert len(nearby) == 1
    assert boid in nearby


def test_cell_calculation():
    """Test that cells are calculated correctly for different cell sizes."""
    grid_small = SpatialGrid(cell_size=50)
    grid_large = SpatialGrid(cell_size=200)

    boid = Boid(pos=pg.Vector2(100, 100))

    # With cell_size=50, position (100, 100) should be in cell (2, 2)
    cell_small = grid_small._get_cell(boid.pos)
    assert cell_small == (2, 2)

    # With cell_size=200, position (100, 100) should be in cell (0, 0)
    cell_large = grid_large._get_cell(boid.pos)
    assert cell_large == (0, 0)


def test_negative_positions(grid):
    """Test that the grid handles negative positions correctly."""
    boid = Boid(pos=pg.Vector2(-50, -50))
    grid.insert(boid)

    assert grid.get_boid_count() == 1

    # Should be able to find the boid
    nearby = grid.get_nearby_boids(pg.Vector2(-50, -50), search_radius=50)
    assert len(nearby) == 1
    assert boid in nearby
