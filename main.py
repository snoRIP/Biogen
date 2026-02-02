"""
Bio-Gen Pro: Evolutionary Neural Laboratory
Main entry point for the simulation.
"""

import pygame
import pygame.gfxdraw
import utils.config as config
from core.simulation import Simulation
from ui.camera import Camera
from ui.manager import UIManager
from core.world import Resource
import ui.render_utils as render_utils

def main():
    """Initializes Pygame and runs the main application loop."""
    pygame.init()
    
    # Initialize display with performance-oriented flags
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), 
                                     pygame.DOUBLEBUF | pygame.HWSURFACE)
    pygame.display.set_caption("Bio-Gen Pro: Research Laboratory")
    clock = pygame.time.Clock()
    
    # Core systems
    sim = Simulation()
    cam = Camera()
    ui = UIManager()
    
    # Interaction state
    selected_agent = None
    panning = False
    
    running = True
    while running:
        # Calculate Delta Time (Normalized to 60 FPS)
        # dt = 1.0 means 1 frame elapsed at 60 FPS
        dt = clock.tick(config.FPS) / 16.6
        if dt > 2.0: dt = 2.0 # Cap lag spikes
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
                
            if event.type == pygame.KEYDOWN:
                # Simulation Controls
                if event.key == pygame.K_SPACE: sim.paused = not sim.paused
                if event.key == pygame.K_1: sim.time_scale = 1
                if event.key == pygame.K_2: sim.time_scale = 2
                if event.key == pygame.K_3: sim.time_scale = 5
                if event.key == pygame.K_r: cam.reset_view()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click: Select Agent
                    m_pos = pygame.mouse.get_pos()
                    # Only select if not clicking the UI panel
                    if m_pos[0] < config.WIDTH - config.UI_PANEL_W:
                        m_world = cam.to_world(m_pos)
                        selected_agent = None
                        cam.followed_agent = None
                        
                        # Find agent under mouse using spatial grid
                        nearby = sim.grid.get_nearby(m_world, 50 / cam.zoom)
                        for e in nearby:
                            if not isinstance(e, Resource): # It's an Agent
                                if e.pos.distance_to(m_world) < 30 / cam.zoom:
                                    selected_agent = e
                                    cam.followed_agent = e
                                    break
                                    
                if event.button == 3: # Right Click: Start Panning
                    panning = True
                    
                if event.button in [4, 5]: # Scroll Wheel: Zoom
                    cam.handle_zoom(1 if event.button == 4 else -1, 
                                   pygame.mouse.get_pos())
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3: 
                    panning = False
                    
            if event.type == pygame.MOUSEMOTION and panning:
                cam.pan(event.rel)

        # 2. Simulation Logic
        sim_start = pygame.time.get_ticks()
        sim.update(dt)
        sim_time = pygame.time.get_ticks() - sim_start
        
        # 3. Camera Update
        cam.update(dt)
        
        # 4. Rendering
        render_start = pygame.time.get_ticks()
        screen.fill(config.CLR_VOID)
        
        # 4a. Draw Background World Grid
        grid_step = 500
        start_x = int((cam.world_center.x - (config.WIDTH / cam.zoom)) / grid_step) * grid_step
        end_x = int((cam.world_center.x + (config.WIDTH / cam.zoom)) / grid_step) * grid_step
        start_y = int((cam.world_center.y - (config.HEIGHT / cam.zoom)) / grid_step) * grid_step
        end_y = int((cam.world_center.y + (config.HEIGHT / cam.zoom)) / grid_step) * grid_step
        
        for gx in range(start_x, end_x + grid_step, grid_step):
            p1 = cam.to_screen(pygame.Vector2(gx, start_y))
            p2 = cam.to_screen(pygame.Vector2(gx, end_y))
            pygame.draw.line(screen, config.CLR_GRID, p1, p2, 1)
        for gy in range(start_y, end_y + grid_step, grid_step):
            p1 = cam.to_screen(pygame.Vector2(start_x, gy))
            p2 = cam.to_screen(pygame.Vector2(end_x, gy))
            pygame.draw.line(screen, config.CLR_GRID, p1, p2, 1)

        # 4b. Draw World Entities (Culling via Spatial Grid)
        view_radius = (max(config.WIDTH, config.HEIGHT) / cam.zoom) * 0.7
        visible_entities = sim.grid.get_nearby(cam.world_center, view_radius)
        
        # Separate entities for layered drawing
        visible_resources = [e for e in visible_entities if isinstance(e, Resource)]
        visible_agents = [e for e in visible_entities if not isinstance(e, Resource)]

        # Level of Detail (LOD) check
        use_glow = cam.zoom > 0.15 
        
        # Draw Resources
        for r in visible_resources:
            sc_pos = cam.to_screen(r.pos)
            color = config.CLR_FOOD if r.type == 'food' else config.CLR_WATER
            if use_glow:
                render_utils.draw_glow(screen, sc_pos, int(15 * cam.zoom), color, 0.4)
            pygame.draw.circle(screen, color, (int(sc_pos.x), int(sc_pos.y)), 
                               max(1, int(3 * cam.zoom)))
        
        # Draw Agents
        for a in visible_agents:
            sc_pos = cam.to_screen(a.pos)
            size = max(2, int(7 * cam.zoom))
            
            if use_glow:
                render_utils.draw_glow(screen, sc_pos, int(12 * cam.zoom), 
                                      a.base_color, 0.3)
            
            if cam.zoom > 0.08: # Complex triangle body
                render_utils.draw_agent_body(screen, sc_pos, a.angle, 7, 
                                             a.base_color, cam.zoom)
            else: # Far zoom: just a colored pixel
                pygame.gfxdraw.pixel(screen, int(sc_pos.x), int(sc_pos.y), 
                                     a.base_color)
            
            # Draw selection circle
            if a == selected_agent:
                pygame.gfxdraw.aacircle(screen, int(sc_pos.x), int(sc_pos.y), 
                                        size + 10, (255, 255, 255))

        # 4c. Environmental Effects (Night Overlay)
        if sim.day_progress > 0.5:
            # 0 at 0.5/1.0, 1 at 0.75
            dist_from_mid = abs(sim.day_progress - 0.75) * 4 
            night_alpha = (1.0 - dist_from_mid) * 160
            
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
            overlay.set_alpha(int(night_alpha))
            overlay.fill((5, 5, 20))
            screen.blit(overlay, (0, 0))

        # 5. UI and Analytics
        ui.draw(screen, sim, selected_agent, cam)
        
        # Profiling metrics
        render_time = pygame.time.get_ticks() - render_start
        ui.update_metrics(sim, clock.get_fps(), sim_time, render_time)
        
        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
