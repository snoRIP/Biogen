"""
Rendering utilities for the Bio-Gen Pro UI.
Includes effects like glows and specialized drawing functions for agents.
"""

import pygame
import pygame.gfxdraw
import math

# Global cache to store pre-rendered glow surfaces (performance boost)
_glow_cache = {}

def draw_glow(screen, pos, radius, color, intensity=1.0):
    """
    Draws a soft, semi-transparent glow effect.
    Uses pre-rendering and caching to avoid expensive gfxdraw calls.
    """
    if radius < 1: 
        return
    
    # Generate unique cache key
    r_key = int(radius)
    c_key = (color[0], color[1], color[2])
    i_key = int(intensity * 10)
    key = (r_key, c_key, i_key)
    
    # Create surface if not in cache
    if key not in _glow_cache:
        # Create a surface with per-pixel alpha (SRCALPHA)
        surf_size = r_key * 2 + 2
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        
        # Draw concentric circles with decreasing alpha
        for r in range(r_key, 0, -2):
            alpha = int((1 - r/r_key) * 40 * intensity)
            if alpha <= 0: continue
            pygame.gfxdraw.filled_circle(surf, r_key, r_key, r, (*c_key, alpha))
        
        _glow_cache[key] = surf
    
    # Blit the cached glow onto the screen
    glow_surf = _glow_cache[key]
    rect = glow_surf.get_rect(center=(int(pos[0]), int(pos[1])))
    screen.blit(glow_surf, rect, special_flags=pygame.BLEND_ALPHA_SDL2)

def draw_agent_body(screen, pos, angle, size, color, cam_zoom):
    """
    Draws an agent as a sharp, anti-aliased triangle.
    Adjusts size based on camera zoom.
    """
    s = int(size * cam_zoom)
    if s < 1: s = 1
    
    # Define triangle points relative to agent angle
    p1 = pos + pygame.Vector2(s * 1.5, 0).rotate(angle)
    p2 = pos + pygame.Vector2(-s, -s).rotate(angle)
    p3 = pos + pygame.Vector2(-s, s).rotate(angle)
    
    points = [(int(p.x), int(p.y)) for p in [p1, p2, p3]]
    
    # Draw filled shape and an AA outline
    pygame.gfxdraw.filled_polygon(screen, points, color)
    pygame.gfxdraw.aapolygon(screen, points, (255, 255, 255, 150))

def clamp(val, min_v, max_v):
    """Clamps a value between a minimum and maximum range."""
    return max(min_v, min(max_v, val))
