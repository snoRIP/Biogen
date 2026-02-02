"""
Simple unit tests for the Bio-Gen Pro core logic.
Uses standard Python unittest framework.
"""

import unittest
import pygame
from core.simulation import Simulation
from core.agent import Agent
from core.brain import NeuralNetwork
import utils.config as config

class TestBioGen(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Pygame must be initialized for Vector2 and other tools
        pygame.init()

    def test_simulation_init(self):
        """Verify that the simulation starts with the correct population."""
        sim = Simulation()
        self.assertEqual(len(sim.agents), config.INITIAL_POP)
        self.assertGreater(len(sim.spawners), 0)

    def test_agent_metabolism(self):
        """Verify that agents lose energy over time."""
        agent = Agent()
        initial_energy = agent.energy
        # Update with dt=100 (simulating many ticks)
        agent.update(100.0, [], [], [])
        self.assertLess(agent.energy, initial_energy)

    def test_neural_network_output(self):
        """Verify that the neural network returns valid ranges."""
        nn = NeuralNetwork()
        inputs = [0.5] * 8
        outputs = nn.predict(inputs)
        self.assertEqual(len(outputs), 2)
        for out in outputs:
            self.assertGreaterEqual(out, -1.0)
            self.assertLessEqual(out, 1.0)

    def test_spatial_grid(self):
        """Verify that the spatial grid correctly retrieves nearby objects."""
        sim = Simulation()
        sim.resources.clear()
        
        # Place a resource at a known location
        from core.world import Resource
        res = Resource(pygame.Vector2(100, 100), 'food')
        sim.resources.add(res)
        
        # Rebuild grid
        sim.grid.clear()
        sim.grid.insert(res)
        
        # Check nearby from (100, 100)
        nearby = sim.grid.get_nearby(pygame.Vector2(105, 105), 50)
        self.assertIn(res, nearby)

if __name__ == '__main__':
    unittest.main()
