"""
The Agent class represents a living creature in the simulation.
Handles DNA, Neural Network (brain), metabolism, and movement.
"""

import pygame
import random
import math
import utils.config as config
from core.brain import NeuralNetwork

class Agent:
    """
    An autonomous agent that evolves and survives based on its neural network.
    """
    def __init__(self, pos=None, brain=None, gen=1, dna=None):
        # Initial position (Random if not specified)
        self.pos = pygame.Vector2(pos) if pos else pygame.Vector2(
            random.uniform(0, config.WORLD_SIZE[0]), 
            random.uniform(0, config.WORLD_SIZE[1])
        )
        self.angle = random.uniform(0, 360)
        self.brain = brain if brain else NeuralNetwork()
        self.gen = gen
        
        # Homeostasis (Survival Stats)
        self.energy = config.BASE_STAT
        self.thirst = config.BASE_STAT
        self.alive = True
        self.age = 0.0
        
        # DNA: Genetic traits that can be mutated
        if dna:
            self.dna = dna
        else:
            self.dna = {
                'speed': random.uniform(0.8, 1.4),
                'sense': random.uniform(300, 600),
                'hunter_factor': random.random(),    # High = Predatory behavior
                'exploration_drive': random.random() # High = Faster movement
            }
        
        # Archetype determination for visuals
        if self.dna['hunter_factor'] > 0.7:
            self.base_color = config.CLR_HUNTER
            self.archetype = "HUNTER"
        elif self.dna['exploration_drive'] > 0.7:
            self.base_color = config.CLR_EXPLORER
            self.archetype = "EXPLORER"
        else:
            self.base_color = config.CLR_AGENT
            self.archetype = "GATHERER"
            
        self.last_out = [0.0, 0.0] # Store last brain output for inputs

    def update(self, dt, food, water, others):
        """Update the agent's logic and movement."""
        self.age += dt
        
        # 1. Perception (Sense nearest resources)
        f_dist, f_ang = self._sense(food, self.dna['sense'])
        w_dist, w_ang = self._sense(water, self.dna['sense'])
        
        # 2. Decision Making (Neural Network)
        # Inputs: Senses, Internal States, and Previous Actions
        inputs = [
            f_dist, f_ang, w_dist, w_ang, 
            self.energy/100, self.thirst/100, 
            self.last_out[0], self.last_out[1]
        ]
        thrust, rotate = self.brain.predict(inputs)
        self.last_out = [thrust, rotate]
        
        # 3. Physics & Movement
        self.angle += rotate * 15 * dt
        dir_vec = pygame.Vector2(1, 0).rotate(self.angle)
        
        # Calculate speed based on DNA and brain output
        actual_speed = (thrust + 1.1) * 2.0 * self.dna['speed']
        if self.archetype == "EXPLORER": 
            actual_speed *= 1.2
        
        self.pos += dir_vec * actual_speed * dt
        # World Wrapping
        self.pos.x %= config.WORLD_SIZE[0]
        self.pos.y %= config.WORLD_SIZE[1]
        
        # 4. Metabolism (Costs for living and moving)
        m_cost = (abs(thrust) + abs(rotate)) * 0.01
        decay_mult = 1.2 if self.archetype == "EXPLORER" else 1.0
        
        self.energy -= (config.DECAY_ENERGY + m_cost) * decay_mult * dt
        self.thirst -= config.DECAY_THIRST * decay_mult * dt
        
        # Death check
        if self.energy <= 0 or self.thirst <= 0:
            self.alive = False
            
        # 5. Hunter Behavior
        if self.archetype == "HUNTER" and self.energy < 70:
            for other in others:
                if other != self and self.pos.distance_squared_to(other.pos) < 400: # 20px
                    # Attack successful!
                    other.energy -= 40
                    self.energy = min(100, self.energy + 30)
                    if other.energy <= 0: 
                        other.alive = False

    def _sense(self, targets, max_dist):
        """Finds the nearest target and returns normalized distance and angle."""
        if not targets: 
            return 1.0, 0.0
        
        nearest = None
        min_d_sq = max_dist * max_dist
        
        for t in targets:
            d_sq = self.pos.distance_squared_to(t.pos)
            if d_sq < min_d_sq:
                min_d_sq = d_sq
                nearest = t
        
        if nearest:
            dist = math.sqrt(min_d_sq)
            vec = nearest.pos - self.pos
            target_ang = math.degrees(math.atan2(vec.y, vec.x))
            # Calculate smallest angle difference
            ang_diff = (target_ang - self.angle + 180) % 360 - 180
            return dist / max_dist, ang_diff / 180.0
            
        return 1.0, 0.0

    def reproduce(self):
        """Creates a mutated child based on the parent's genes."""
        new_brain = self.brain.mutate()
        # Mutate DNA traits slightly
        new_dna = {k: max(0.1, min(1.0, v + random.uniform(-0.1, 0.1))) 
                  for k, v in self.dna.items()}
        
        # Offset child position slightly
        offset = pygame.Vector2(random.uniform(-30, 30), random.uniform(-30, 30))
        offspring_pos = self.pos + offset
        
        return Agent(pos=offspring_pos, brain=new_brain, 
                     gen=self.gen + 1, dna=new_dna)