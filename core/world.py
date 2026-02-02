"""
World objects and resource definitions.
Includes Resources (Food/Water) and Spawners that distribute them.
"""

import pygame
import random
import utils.config as config

class Resource:
    """A collectible resource in the world (Food or Water)."""
    def __init__(self, pos, r_type):
        self.pos = pygame.Vector2(pos)
        self.type = r_type # 'food' or 'water'
        self.active = True # False if already consumed in this step

class Spawner:
    """A point that generates resources within a specific radius."""
    def __init__(self, r_type):
        self.type = r_type
        # Pick a random location away from the borders
        self.pos = pygame.Vector2(
            random.uniform(200, config.WORLD_SIZE[0] - 200),
            random.uniform(200, config.WORLD_SIZE[1] - 200)
        )
        self.radius = random.uniform(300, 600)

    def spawn(self):
        """Generates a new Resource object within the spawner's area."""
        angle = random.uniform(0, 360)
        dist = random.uniform(0, self.radius)
        offset = pygame.Vector2(dist, 0).rotate(angle)
        
        spawn_pos = self.pos + offset
        
        # Keep within world boundaries
        spawn_pos.x %= config.WORLD_SIZE[0]
        spawn_pos.y %= config.WORLD_SIZE[1]
        
        return Resource(spawn_pos, self.type)