"""Spatial grid for efficient neighbor finding in boids simulation.

This module implements a spatial hash grid that partitions 2D space into cells.
Boids are placed into cells based on their position, allowing for O(1) lookup
of nearby boids instead of checking all boids in the simulation.
"""

from collections import defaultdict

import pygame as pg

from my_boids.boids import Boid


class SpatialGrid:
    """A spatial hash grid for efficient neighbor queries.

    The grid divides 2D space into cells of a fixed size. Boids are assigned
    to cells based on their position. When searching for neighbors, only
    boids in the same cell and adjacent cells need to be checked.

    Attributes:
        cell_size (float): The size of each grid cell in pixels.
        grid (dict): A dictionary mapping cell coordinates to lists of boids.
    """

    def __init__(self, cell_size: float):
        """Initialize the spatial grid.

        Args:
            cell_size (float): The size of each grid cell. Should be set to
                approximately the visual range of boids for optimal performance.
        """
        self.cell_size = cell_size
        self.grid: dict[tuple[int, int], list[Boid]] = defaultdict(list)

    def clear(self) -> None:
        """Remove all boids from the grid."""
        self.grid.clear()

    def _get_cell(self, pos: pg.Vector2) -> tuple[int, int]:
        """Get the grid cell coordinates for a position.

        Args:
            pos (pg.Vector2): The position to map to a cell.

        Returns:
            tuple[int, int]: The (x, y) cell coordinates.
        """
        cell_x = int(pos.x // self.cell_size)
        cell_y = int(pos.y // self.cell_size)
        return (cell_x, cell_y)

    def insert(self, boid: Boid) -> None:
        """Insert a boid into the grid based on its position.

        Args:
            boid (Boid): The boid to insert.
        """
        cell = self._get_cell(boid.pos)
        self.grid[cell].append(boid)

    def get_nearby_boids(
        self,
        pos: pg.Vector2,
        search_radius: float,
    ) -> list[Boid]:
        """Get all boids within a search radius of a position.

        This method checks the cell containing the position and all adjacent
        cells, then filters by actual distance.

        Args:
            pos (pg.Vector2): The center position to search around.
            search_radius (float): The maximum distance to include boids.

        Returns:
            list[Boid]: A list of boids within the search radius.
        """
        nearby_boids: list[Boid] = []
        center_cell = self._get_cell(pos)

        # Calculate how many cells to check in each direction
        # Add 1 to ensure we cover the full search radius
        cells_to_check = int(search_radius // self.cell_size) + 1

        # Check all cells in the search area
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    # Filter boids by actual distance
                    for boid in self.grid[cell]:
                        if boid.pos.distance_to(pos) <= search_radius:
                            nearby_boids.append(boid)

        return nearby_boids

    def get_cell_count(self) -> int:
        """Get the number of occupied cells in the grid.

        Returns:
            int: The number of cells containing at least one boid.
        """
        return len(self.grid)

    def get_boid_count(self) -> int:
        """Get the total number of boids in the grid.

        Returns:
            int: The total number of boids across all cells.
        """
        return sum(len(boids) for boids in self.grid.values())
