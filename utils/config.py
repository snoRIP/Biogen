"""
Configuration constants for the Bio-Gen Pro simulation.
This file contains all the tweakable parameters for physics, 
metabolism, visuals, and UI.
"""

import pygame

# --- Display & UI Settings ---
WIDTH, HEIGHT = 1440, 850         # Screen resolution
WORLD_SIZE = (5000, 5000)        # Total size of the simulation world
UI_PANEL_W = 380                 # Width of the right-side inspector panel
FPS = 60                         # Target frames per second

# --- Colors (Scientific Cyberpunk Theme) ---
CLR_VOID = (3, 5, 12)            # Background color
CLR_GRID = (15, 22, 35)          # Grid line color
CLR_UI_BG = (10, 15, 25, 200)    # UI panel background
CLR_ACCENT = (0, 255, 180)       # Mint Neon (Primary accent)
CLR_ENERGY = (0, 255, 120)       # Green (Energy/Food)
CLR_THIRST = (0, 180, 255)       # Blue (Thirst/Water)
CLR_FOOD = (255, 210, 0)         # Gold (Food resource)
CLR_WATER = (0, 180, 255)        # Azure (Water resource)
CLR_HUNTER = (255, 50, 80)       # Red Neon (Predator color)
CLR_EXPLORER = (200, 100, 255)   # Purple Neon (Explorer color)
CLR_AGENT = (0, 255, 150)        # Default agent color
CLR_TEXT = (210, 230, 250)       # Default text color

# --- Simulation & Metabolism ---
INITIAL_POP = 80                 # Starting number of agents
MIN_POP = 20                     # Auto-respawn threshold
MAX_POP = 150                    # Soft limit for performance
BASE_STAT = 100.0                # Initial energy/thirst
DECAY_ENERGY = 0.015             # Energy lost per tick
DECAY_THIRST = 0.02              # Thirst lost per tick
REPRO_THRESHOLD = 75.0           # Energy required to reproduce
REPRO_COST = 40.0                # Energy cost to create offspring

# --- Neural Network (AI) Settings ---
HID_NODES = 6                    # Initial hidden layer size
MAX_HIDDEN_NODES = 12            # Maximum allowed hidden nodes
MUTATION_RATE_STRUCT = 0.05      # Chance for structural brain mutation

# --- Visual Effects & Camera ---
GLOW_INTENSITY = 0.5             # Strength of the glow effect
DAY_NIGHT_CYCLE_SPEED = 0.0003   # Speed of the light cycle
CAMERA_LERP = 0.12               # Panning smoothness (0-1)
ZOOM_LERP = 0.08                 # Zooming smoothness (0-1)
MIN_ZOOM = 0.04                  # Minimum zoom out level
MAX_ZOOM = 6.0                   # Maximum zoom in level

# --- Performance Optimization ---
GRID_CELL_SIZE = 200             # Size of each cell in the spatial grid
HEATMAP_RESOLUTION = 50          # Resolution of the activity heatmap