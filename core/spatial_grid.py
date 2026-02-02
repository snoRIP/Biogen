"""
Spatial Grid for performance optimization.
Partitions the world into cells to make proximity checks much faster.
"""

import pygame
import utils.config as config

class SpatialGrid:
    """
    An efficient 2D grid that reduces the complexity of finding nearby objects.
    Instead of checking every object against every other object (O(N^2)), 
    we only check objects in neighboring grid cells.
    """
    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.cols = int(width // cell_size) + 1
        self.rows = int(height // cell_size) + 1
        self.grid = {} # Map (x, y) coordinates to list of entities

    def clear(self):
        """Resets the grid for the next frame."""
        self.grid.clear()

    def _get_key(self, pos):
        """Calculates the grid cell coordinates for a given position."""
        # We assume the position is within world bounds for speed
        return (int(pos.x // self.cell_size), int(pos.y // self.cell_size))

    def insert(self, entity):
        """Adds an entity into the appropriate grid cell."""
        key = self._get_key(entity.pos)
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(entity)

    def get_nearby(self, pos, radius):
        """Returns all entities within grid cells covered by the given radius."""
        cx, cy = self._get_key(pos)
        # Determine how many cells the radius spans
        r_cells = int(radius // self.cell_size) + 1
        
        nearby = []
        # Localize grid access for micro-performance
        grid_ref = self.grid
        
        # Iterate through neighboring cells
        for i in range(cx - r_cells, cx + r_cells + 1):
            # Check bounds
            if i < 0 or i >= self.cols: continue
            for j in range(cy - r_cells, cy + r_cells + 1):
                if j < 0 or j >= self.rows: continue
                
                key = (i, j)
                if key in grid_ref:
                    nearby.extend(grid_ref[key])
                    
        return nearby