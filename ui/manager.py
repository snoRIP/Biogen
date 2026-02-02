"""
The UI Manager handles the Heads-Up Display (HUD) and data visualization.
Includes performance metrics, population stats, and neural network inspection.
"""

import pygame
import pygame.gfxdraw
import utils.config as config
import ui.render_utils as utils

class UIManager:
    """
    Renders semi-transparent panels and detailed simulation metrics 
    in a 'Scientific Cyberpunk' style.
    """
    def __init__(self):
        # Professional Monospace Fonts
        self.font = pygame.font.SysFont("Consolas", 14)
        self.font_bold = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 11)
        
        # Data History for Graphs
        self.history = {
            'pop': [], 'avg_energy': [],
            'fps': [], 'sim_time': []
        }
        self.tick = 0
        
        # Profile Data
        self.current_fps = 0
        self.min_fps = 999
        self.max_fps = 0
        self.current_sim_time = 0
        self.current_render_time = 0
        
        # HUD Theme Colors
        self.COLOR_BG = (5, 10, 20, 180)      # Transparent dark blue
        self.COLOR_BORDER = (0, 255, 180, 100) # Mint accent with alpha
        self.COLOR_ACCENT = (0, 255, 180)

    def update_metrics(self, sim, fps, sim_time, render_time=0):
        """Saves current performance data and updates history buffers."""
        self.current_fps = fps
        self.current_sim_time = sim_time
        self.current_render_time = render_time
        
        # Update Min/Max FPS (Skipping the initial startup lag)
        if fps > 5:
            self.min_fps = min(self.min_fps, fps)
            self.max_fps = max(self.max_fps, fps)
            
        self.tick += 1
        if self.tick >= 30: # Append to history every 30 frames
            self.tick = 0
            self.history['pop'].append(len(sim.agents))
            self.history['fps'].append(fps)
            self.history['sim_time'].append(sim_time)
            
            if sim.agents:
                avg_e = sum(a.energy for a in sim.agents) / len(sim.agents)
                self.history['avg_energy'].append(avg_e)
            else:
                self.history['avg_energy'].append(0)
            
            # Keep history buffer fixed at 40 points
            for k in self.history:
                if len(self.history[k]) > 40: 
                    self.history[k].pop(0)

    def _draw_panel(self, screen, x, y, w, h, title=""):
        """Draws a semi-transparent 'glass' panel with a border and title."""
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.COLOR_BG, (0, 0, w, h), border_radius=4)
        pygame.draw.rect(surf, self.COLOR_BORDER, (0, 0, w, h), 1, border_radius=4)
        screen.blit(surf, (x, y))
        
        if title:
            t_surf = self.font_bold.render(title.upper(), True, self.COLOR_ACCENT)
            screen.blit(t_surf, (x + 10, y - 22))

    def draw(self, screen, sim, selected, camera):
        """Main draw call for the entire UI layer."""
        
        # 1. Performance Panel (Top Left)
        self._draw_panel(screen, 20, 40, 240, 110, "System Performance")
        perf_stats = [
            f"FPS: {int(self.current_fps)} [MIN:{int(self.min_fps)} MAX:{int(self.max_fps)}]",
            f"SIM LOGIC: {self.current_sim_time:.1f}ms",
            f"RENDERING: {self.current_render_time:.1f}ms",
            f"TIME SCALE: {sim.time_scale}x"
        ]
        for i, text in enumerate(perf_stats):
            color = self.COLOR_ACCENT if i != 0 else (255, 200, 0)
            img = self.font.render(text, True, color)
            screen.blit(img, (35, 50 + i * 20))

        # 2. Population Panel (Top Center)
        self._draw_panel(screen, 300, 40, 280, 110, "Population Metrics")
        pop_stats = [
            f"TOTAL AGENTS: {len(sim.agents)}",
            f"DOMINANT: {sim.stats['dominant_type']}",
            f"AVG FITNESS: {sim.stats['avg_fitness']:.1f}",
            f"AVG SPEED: {sim.stats['avg_speed']:.2f}"
        ]
        for i, text in enumerate(pop_stats):
            img = self.font.render(text, True, (210, 230, 250))
            screen.blit(img, (315, 50 + i * 20))

        # 3. Bottom History Graphs
        graph_w, graph_h = 160, 60
        self._draw_panel(screen, 20, config.HEIGHT - 90, graph_w * 4 + 60, 80)
        self._draw_graph(screen, 35, config.HEIGHT - 80, graph_w, graph_h, 
                         self.history['pop'], "POP", config.CLR_ACCENT)
        self._draw_graph(screen, 210, config.HEIGHT - 80, graph_w, graph_h, 
                         self.history['avg_energy'], "ENERGY", config.CLR_ENERGY)
        self._draw_graph(screen, 385, config.HEIGHT - 80, graph_w, graph_h, 
                         self.history['fps'], "FPS", (255, 200, 0))
        self._draw_graph(screen, 560, config.HEIGHT - 80, graph_w, graph_h, 
                         self.history['sim_time'], "SIM", (200, 100, 255))

        # 4. Right Side Inspector
        panel_x = config.WIDTH - config.UI_PANEL_W + 20
        self._draw_panel(screen, panel_x, 40, config.UI_PANEL_W - 40, 160, 
                         "Environmental Scanner")
        
        # Minimap (Embedded in panel)
        mm_size = 140
        mm_x = panel_x + (config.UI_PANEL_W - 40 - mm_size) // 2
        mm_y = 50
        pygame.draw.rect(screen, (0, 0, 0), (mm_x, mm_y, mm_size, mm_size))
        pygame.draw.rect(screen, self.COLOR_BORDER, (mm_x, mm_y, mm_size, mm_size), 1)
        
        # Render dots for agents on minimap
        step = max(1, len(sim.agents) // 400)
        for a in sim.agents[::step]:
            mx = mm_x + (a.pos.x / config.WORLD_SIZE[0]) * mm_size
            my = mm_y + (a.pos.y / config.WORLD_SIZE[1]) * mm_size
            pygame.gfxdraw.pixel(screen, int(mx), int(my), a.base_color)

        # 5. Neural Core Inspector (Bottom Right)
        if selected:
            # Individual Agent Inspector
            self._draw_panel(screen, panel_x, 220, config.UI_PANEL_W - 40, 500, 
                             "Neural Core Inspector")
            self._draw_brain(screen, panel_x + 10, 240, config.UI_PANEL_W - 60, 300, 
                             selected.brain)
            
            info_y = 560
            info_txt = [
                f"IDENTIFIER: {id(selected) % 10000:04d}",
                f"ARCHETYPE: {selected.archetype}",
                f"GENERATION: {selected.gen}",
                f"AGE: {int(selected.age)} CYCLES",
                f"ENERGY LEVEL: {int(selected.energy)}%",
                f"HYDRATION: {int(selected.thirst)}%",
                f"GENETIC SPEED: {selected.dna['speed']:.2f}"
            ]
            for i, t in enumerate(info_txt):
                lbl, val = t.split(": ")
                img_lbl = self.font_small.render(lbl + ":", True, (150, 150, 170))
                img_val = self.font.render(val, True, self.COLOR_ACCENT)
                screen.blit(img_lbl, (panel_x + 20, info_y + i * 22))
                screen.blit(img_val, (panel_x + 140, info_y + i * 22))
        else:
            # Species Representative (Dominant Champion)
            dom_type = sim.stats['dominant_type']
            champ = sim.stats['champions'].get(dom_type)
            if champ:
                self._draw_panel(screen, panel_x, 220, config.UI_PANEL_W - 40, 500, 
                                 f"Dominant: {dom_type}")
                self._draw_brain(screen, panel_x + 10, 240, config.UI_PANEL_W - 60, 
                                 300, champ.brain)
                
                info_y = 560
                info_txt = [
                    f"SPECIES: {dom_type}",
                    f"POPULATION: {sim.stats['type_counts'][dom_type]}",
                    f"CHAMPION AGE: {int(champ.age)}",
                    f"AVG FITNESS: {sim.stats['avg_fitness']:.1f}",
                    "",
                    "STATUS: DOMINATING WORLD"
                ]
                for i, t in enumerate(info_txt):
                    if not t: continue
                    img = self.font.render(t, True, self.COLOR_ACCENT)
                    screen.blit(img, (panel_x + 20, info_y + i * 22))

    def _draw_brain(self, screen, x, y, w, h, nn):
        """Renders the neural network architecture with activations."""
        labels_in = ["Food D", "Food A", "Wat D", "Wat A", "Energy", "Thirst", "LThr", "LRot"]
        labels_out = ["Thrust", "Rotate"]

        pygame.draw.rect(screen, (0, 5, 10, 150), (x, y, w, h), border_radius=8)
        
        layers = [nn.num_in, nn.num_hidden, nn.num_out]
        acts = [nn.ax_in, nn.ax_hid, nn.ax_out]
        layer_x = [x + 60, x + w//2, x + w - 60]
        
        pos_map = []
        for l_idx, count in enumerate(layers):
            l_pos = []
            spacing = (h - 40) / (count + 1)
            for i in range(count):
                l_pos.append((layer_x[l_idx], y + 20 + (i + 1) * spacing))
            pos_map.append(l_pos)

        # Draw Connections
        for l in range(2):
            weights = nn.w_ih if l == 0 else nn.w_ho
            for i, p1 in enumerate(pos_map[l]):
                if i >= len(weights): break
                for j, p2 in enumerate(pos_map[l+1]):
                    if j >= len(weights[i]): break
                    w_val = weights[i][j]
                    alpha = int(abs(w_val) * 120 * (abs(acts[l][i]) + 0.2))
                    color = (0, 255, 180) if w_val > 0 else (255, 50, 80)
                    pygame.draw.line(screen, (*color, min(255, alpha)), p1, p2, 1)

        # Draw Nodes and Labels
        for l_idx, layer in enumerate(pos_map):
            for i, p in enumerate(layer):
                val = int(abs(acts[l_idx][i]) * 155)
                pygame.gfxdraw.filled_circle(screen, int(p[0]), int(p[1]), 5, (50, 50, 70))
                pygame.gfxdraw.filled_circle(screen, int(p[0]), int(p[1]), 3, 
                                            (100+val, 100+val, 255))
                pygame.gfxdraw.aacircle(screen, int(p[0]), int(p[1]), 3, (255,255,255))
                
                if l_idx == 0:
                    txt = self.font_small.render(labels_in[i], True, (150, 150, 170))
                    screen.blit(txt, (p[0] - 50, p[1] - 6))
                elif l_idx == 2:
                    txt = self.font_small.render(labels_out[i], True, (150, 150, 170))
                    screen.blit(txt, (p[0] + 10, p[1] - 6))

    def _draw_graph(self, screen, x, y, w, h, data, label, color):
        """Draws a simple line graph for historical data."""
        if len(data) > 1:
            mx, mn = max(data), min(data)
            r = mx - mn if mx != mn else 1
            pts = [(x + (i/(len(data)-1))*w, y + h - ((v-mn)/r)*h) 
                   for i, v in enumerate(data)]
            pygame.draw.lines(screen, color, False, pts, 1)
            
            t_surf = self.font_small.render(f"{label}: {int(data[-1])}", True, color)
            screen.blit(t_surf, (x, y - 14))