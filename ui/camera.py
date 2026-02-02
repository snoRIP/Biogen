"""
Camera system for the simulation.
Handles smooth panning, zooming centered on the mouse, and agent following.
"""

import pygame
import utils.config as config

class Camera:
    """
    Manages the transformation between World coordinates and Screen coordinates.
    Uses Linear Interpolation (LERP) for professional movement smoothness.
    """
    def __init__(self):
        # Current state (what is actually rendered)
        self.zoom = 1.0
        self.world_center = pygame.Vector2(config.WORLD_SIZE) / 2
        
        # Target state (where the camera is trying to go)
        self.target_zoom = self.zoom
        self.target_world_center = pygame.Vector2(self.world_center)
        
        self.offset = pygame.Vector2(0, 0)
        self.followed_agent = None
        
        self.reset_view()

    def reset_view(self):
        """Quickly resets the camera to show the entire simulation world."""
        self.followed_agent = None
        # Calculate zoom to fit world within screen (minus UI panel)
        zoom_x = (config.WIDTH - config.UI_PANEL_W) / config.WORLD_SIZE[0]
        zoom_y = config.HEIGHT / config.WORLD_SIZE[1]
        
        self.target_zoom = min(zoom_x, zoom_y) * 0.9
        self.target_world_center = pygame.Vector2(config.WORLD_SIZE) / 2
        
        # Initialize if it's the first run
        if not hasattr(self, 'zoom'):
            self.zoom = self.target_zoom
            self.world_center = pygame.Vector2(self.target_world_center)

    def update(self, dt):
        """Interpolates camera properties toward their targets."""
        
        # 1. Smooth Zoom Interpolation
        zoom_diff = self.target_zoom - self.zoom
        if abs(zoom_diff) > 0.0001:
            self.zoom += zoom_diff * config.ZOOM_LERP * dt
        else:
            self.zoom = self.target_zoom

        # 2. Update Target for Following
        if self.followed_agent:
            if self.followed_agent.alive:
                self.target_world_center = pygame.Vector2(self.followed_agent.pos)
            else:
                self.followed_agent = None

        # 3. Smooth Pan Interpolation
        center_diff = self.target_world_center - self.world_center
        if center_diff.length_squared() > 0.01:
            self.world_center += center_diff * config.CAMERA_LERP * dt
        else:
            self.world_center = pygame.Vector2(self.target_world_center)

        # 4. Final Offset Calculation
        # Map World (0,0) to Screen pixels
        visual_center = pygame.Vector2((config.WIDTH - config.UI_PANEL_W) / 2, 
                                      config.HEIGHT / 2)
        self.offset = visual_center - (self.world_center * self.zoom)

    def to_screen(self, world_pos):
        """Converts a coordinate from the World to the Screen."""
        return (world_pos * self.zoom) + self.offset

    def to_world(self, screen_pos):
        """Converts a coordinate from the Screen to the World."""
        return (pygame.Vector2(screen_pos) - self.offset) / self.zoom

    def handle_zoom(self, scroll_val, mouse_pos):
        """Adjusts target zoom and offsets to keep the mouse world position stable."""
        mouse_world_before = self.to_world(mouse_pos)
        
        # Update zoom level
        zoom_step = 1.2
        if scroll_val > 0:
            self.target_zoom *= zoom_step
        else:
            self.target_zoom /= zoom_step
        
        # Clamp zoom to limits
        self.target_zoom = max(config.MIN_ZOOM, 
                               min(self.target_zoom, config.MAX_ZOOM))
        
        # Recalculate target center to keep mouse world position under the cursor
        visual_center = pygame.Vector2((config.WIDTH - config.UI_PANEL_W) / 2, 
                                      config.HEIGHT / 2)
        new_target_offset = pygame.Vector2(mouse_pos) - \
                           (mouse_world_before * self.target_zoom)
        
        self.target_world_center = (visual_center - new_target_offset) / self.target_zoom

    def pan(self, rel):
        """Moves the camera target based on mouse relative movement."""
        world_rel = pygame.Vector2(rel) / self.zoom
        self.target_world_center -= world_rel
        if world_rel.length_squared() > 0:
            self.followed_agent = None # Break following on manual pan