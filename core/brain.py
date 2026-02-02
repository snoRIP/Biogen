"""
Neural Network implementation for Agent brains.
Handles prediction, weight mutation, and structural evolution.
"""

import math
import random
import utils.config as config

class NeuralNetwork:
    """
    A simple Feed-Forward Neural Network with one hidden layer.
    Supports basic evolution via weight mutation and structural changes.
    """
    def __init__(self, weights=None, num_hidden=None):
        self.num_in = 8   # Fixed inputs (Senses, States, Last Outputs)
        self.num_out = 2  # Fixed outputs (Thrust, Rotation)
        
        # Determine hidden layer size
        self.num_hidden = num_hidden if num_hidden is not None else config.HID_NODES
        
        # Initialize weights if not provided (Random initialization)
        if weights:
            self.w_ih, self.w_ho = weights
        else:
            # Input to Hidden layer weights
            self.w_ih = [[random.uniform(-1, 1) for _ in range(self.num_hidden)] 
                        for _ in range(self.num_in)]
            # Hidden to Output layer weights
            self.w_ho = [[random.uniform(-1, 1) for _ in range(self.num_out)] 
                        for _ in range(self.num_hidden)]
        
        # Activation values (for visualization and processing)
        self.ax_in = [0.0] * self.num_in
        self.ax_hid = [0.0] * self.num_hidden
        self.ax_out = [0.0] * self.num_out

    def predict(self, inputs):
        """Processes inputs through the network and returns outputs."""
        self.ax_in = inputs
        
        # Step 1: Input to Hidden layer
        for j in range(self.num_hidden):
            val = sum(inputs[i] * self.w_ih[i][j] for i in range(self.num_in))
            self.ax_hid[j] = math.tanh(val) # Hyperbolic tangent activation
            
        # Step 2: Hidden to Output layer
        for j in range(self.num_out):
            val = sum(self.ax_hid[i] * self.w_ho[i][j] for i in range(self.num_hidden))
            self.ax_out[j] = math.tanh(val)
            
        return self.ax_out

    def mutate(self):
        """Returns a mutated copy of this neural network."""
        # Function to mutate a single weight
        def _mut_w(w):
            if random.random() < 0.1: # 10% chance to mutate each weight
                return w + random.uniform(-0.2, 0.2)
            return w

        # Copy and mutate weights
        new_ih = [[_mut_w(w) for w in row] for row in self.w_ih]
        new_ho = [[_mut_w(w) for w in row] for row in self.w_ho]
        new_hidden = self.num_hidden

        # Structural mutation: Add or remove hidden nodes
        if random.random() < config.MUTATION_RATE_STRUCT:
            if random.random() < 0.5 and new_hidden < config.MAX_HIDDEN_NODES:
                # Add a new hidden node
                for row in new_ih: 
                    row.append(random.uniform(-1, 1))
                new_ho.append([random.uniform(-1, 1) for _ in range(self.num_out)])
                new_hidden += 1
            elif new_hidden > 2:
                # Remove the last hidden node
                for row in new_ih: 
                    row.pop()
                new_ho.pop()
                new_hidden -= 1
        
        return NeuralNetwork((new_ih, new_ho), new_hidden)
