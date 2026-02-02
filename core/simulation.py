"""
The Simulation class manages the entire simulation state.
Handles the update loop, spatial partitioning, and population statistics.
"""

import pygame
import random
import utils.config as config
from core.spatial_grid import SpatialGrid
from core.agent import Agent
from core.world import Resource, Spawner

class Simulation:
    """
    Orchestrates agents and resources, managing the simulation lifecycle.
    """
    def __init__(self):
        # Optimization grid
        self.grid = SpatialGrid(config.WORLD_SIZE[0], config.WORLD_SIZE[1], 
                               config.GRID_CELL_SIZE)
        
        # Entities
        self.agents = [Agent() for _ in range(config.INITIAL_POP)]
        self.spawners = [Spawner('food') for _ in range(12)] + \
                        [Spawner('water') for _ in range(8)]
        self.resources = set() # Use set for O(1) removal
        
        # Statistics & Analytics
        self.heatmap = [[0 for _ in range(config.HEATMAP_RESOLUTION)] 
                        for _ in range(config.HEATMAP_RESOLUTION)]
        self.max_gen = 1
        self.history = {'pop': [], 'energy': [], 'fitness': []}
        
        # Detailed archetype stats
        self.stats = {
            'avg_speed': 0, 'avg_fitness': 0,
            'dominant_type': "NONE", 'type_counts': {},
            'champions': {} # Oldest agent per type
        }
        self.stats_timer = 0
        
        # Control flags
        self.paused = False
        self.time_scale = 1
        self.day_progress = 0.0
        self.accumulator = 0.0 # For adaptive logic steps

    def update(self, dt):
        """Updates the simulation logic with an adaptive time step."""
        if self.paused: 
            return
            
        # Update day/night cycle based on real time
        self.day_progress = (self.day_progress + config.DAY_NIGHT_CYCLE_SPEED * \
                            dt * self.time_scale) % 1.0
        
        # Add elapsed time to accumulator
        self.accumulator += dt * self.time_scale
        
        # Safety cap to avoid "spiral of death" during heavy load
        if self.accumulator > 10.0: 
            self.accumulator = 10.0
            
        # Process logic in fixed steps of 1.0
        while self.accumulator >= 1.0:
            self._step(1.0)
            self.accumulator -= 1.0
        
        # Update aggregated stats every 30 frames
        self.stats_timer += 1
        if self.stats_timer >= 30:
            self.stats_timer = 0
            self._update_stats()

    def _update_stats(self):
        """Calculates global population statistics."""
        if not self.agents: 
            return
        
        total_speed = 0
        total_age = 0
        counts = {"GATHERER": 0, "HUNTER": 0, "EXPLORER": 0}
        champs = {"GATHERER": None, "HUNTER": None, "EXPLORER": None}
        
        for a in self.agents:
            total_speed += a.dna['speed']
            total_age += a.age
            counts[a.archetype] += 1
            
            # Find the "Champion" (oldest) of each archetype
            if champs[a.archetype] is None or a.age > champs[a.archetype].age:
                champs[a.archetype] = a
            
        # Store results
        self.stats['avg_speed'] = total_speed / len(self.agents)
        self.stats['avg_fitness'] = total_age / len(self.agents)
        self.stats['type_counts'] = counts
        self.stats['dominant_type'] = max(counts, key=counts.get)
        self.stats['champions'] = champs

    def _step(self, dt):
        """A single fixed logic step of the simulation."""
        # 1. Clear and Rebuild Spatial Grid
        self.grid.clear()
        for r in self.resources: 
            self.grid.insert(r)
        for a in self.agents: 
            self.grid.insert(a)
        
        # 2. Auto-Seed (Maintain minimum population)
        if len(self.agents) < config.MIN_POP:
            self.agents.extend([Agent() for _ in range(5)])

        new_agents = []
        active_agents = []
        
        # 3. Update Agents
        for a in self.agents:
            if not a.alive: 
                continue
            
            # Update Heatmap (Lowered frequency for performance)
            if random.random() < 0.2:
                hx = int((a.pos.x / config.WORLD_SIZE[0]) * config.HEATMAP_RESOLUTION)
                hy = int((a.pos.y / config.WORLD_SIZE[1]) * config.HEATMAP_RESOLUTION)
                if 0 <= hx < config.HEATMAP_RESOLUTION and 0 <= hy < config.HEATMAP_RESOLUTION:
                    self.heatmap[hx][hy] += 1

            # Find nearby objects using the spatial grid
            nearby = self.grid.get_nearby(a.pos, a.dna['sense'])
            
            food = []
            water = []
            others = []
            
            for e in nearby:
                if e == a: continue
                if isinstance(e, Resource):
                    if not e.active: continue
                    if e.type == 'food': food.append(e)
                    else: water.append(e)
                else:
                    others.append(e)
            
            # Process Agent AI and Physics
            a.update(dt, food, water, others)
            
            # 4. Handle Resource Consumption
            for r in food:
                if r.active and a.pos.distance_squared_to(r.pos) < 400:
                    a.energy = min(100, a.energy + 35)
                    r.active = False # Mark as consumed
                    if r in self.resources: 
                        self.resources.remove(r)
            
            for r in water:
                if a.pos.distance_squared_to(r.pos) < 400:
                    a.thirst = min(100, a.thirst + 4.0 * dt)

            # 5. Reproduction
            if a.energy > config.REPRO_THRESHOLD:
                # Crowding factor (reproduction slows as population reaches max)
                pop_factor = 1.0 - (len(self.agents) / config.MAX_POP)
                if random.random() < 0.005 * pop_factor:
                    a.energy -= config.REPRO_COST
                    child = a.reproduce()
                    new_agents.append(child)
                    self.max_gen = max(self.max_gen, child.gen)

            if a.alive:
                active_agents.append(a)
                
        # Update agent list
        self.agents = active_agents + new_agents
        
        # 6. Performance Soft Limit (Keep the youngest agents)
        if len(self.agents) > config.MAX_POP:
            self.agents.sort(key=lambda x: x.age) 
            self.agents = self.agents[:config.MAX_POP]
        
        # 7. Resource Regeneration
        if len(self.resources) < 600:
            if random.random() < 0.5:
                self.resources.add(random.choice(self.spawners).spawn())
