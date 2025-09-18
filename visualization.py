"""
Visualization and rendering for the language evolution simulation
"""

import math
import tkinter as tk
import tkinter.font as tkfont
from functools import lru_cache
from typing import Dict, Tuple, Optional

from config import CONFIG
from world import World, Community
from simulation import LanguageEvolutionSimulation
from phonology import PHONEMES, RGB_PROJ

def dot(a, b) -> float:
    """Dot product of two vectors"""
    return sum(x*y for x, y in zip(a, b))

@lru_cache(maxsize=4096)
def word_to_color_cached(word_key: str) -> Tuple[int, int, int]:
    """Convert word to RGB color based on phonological features"""
    if not word_key:
        return (200, 200, 200)
    
    segs = list(word_key)
    r = g = b = 0.0
    n = 0
    
    for s in segs:
        if s not in PHONEMES:
            continue
        vec = PHONEMES[s]
        r += dot(vec, RGB_PROJ[0])
        g += dot(vec, RGB_PROJ[1])
        b += dot(vec, RGB_PROJ[2])
        n += 1
    
    if n == 0:
        return (200, 200, 200)
    
    r /= n; g /= n; b /= n
    
    def squash(x: float) -> int:
        x = math.tanh(0.6*x)
        x = 0.5 + 0.47*x
        return max(0, min(255, int(x*255)))
    
    R, G, B = squash(r), squash(g), squash(b)
    return (R, G, B)

def rgb_hex(rgb: Tuple[int,int,int]) -> str:
    """Convert RGB tuple to hex string"""
    return "#%02x%02x%02x" % rgb

def text_color_for_bg(rgb: Tuple[int,int,int]) -> str:
    """Choose text color (black/white) for given background"""
    R, G, B = rgb
    Y = 0.2126*R + 0.7152*G + 0.0722*B
    return "#000000" if Y > 135 else "#ffffff"

class LanguageRenderer:
    """Handles rendering of the language evolution simulation"""
    
    def __init__(self, root: tk.Tk, world: World, simulation: LanguageEvolutionSimulation):
        self.world = world
        self.simulation = simulation
        self.root = root
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=CONFIG.CANVAS_W, height=CONFIG.CANVAS_H, 
                               bg="#101010", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Font cache
        self.font_cache: Dict[int, tkfont.Font] = {}
        
        # Bind resize event
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Calculate initial cell size
        self.cell_w = max(1, CONFIG.CANVAS_W // max(1, world.width))
        self.cell_h = max(1, CONFIG.CANVAS_H // max(1, world.height))
    
    def _on_resize(self, event):
        """Handle canvas resize"""
        self.cell_w = max(1, event.width // max(1, self.world.width))
        self.cell_h = max(1, event.height // max(1, self.world.height))
    
    def _get_font_for_cell(self) -> tkfont.Font:
        """Get appropriate font size for current cell size"""
        px = max(CONFIG.MIN_FONT_PX, 
                min(CONFIG.MAX_FONT_PX, int(min(self.cell_w, self.cell_h) * 0.55)))
        
        if px not in self.font_cache:
            try:
                self.font_cache[px] = tkfont.Font(
                    family="Consolas" if tk.TkVersion >= 8.5 else "Courier", 
                    size=px, weight="bold"
                )
            except:
                self.font_cache[px] = tkfont.Font(size=px, weight="bold")
        
        return self.font_cache[px]
    
    def draw(self):
        """Draw the current state of the simulation"""
        W, H = self.world.width, self.world.height
        cw, ch = self.cell_w, self.cell_h
        
        self.canvas.delete("all")
        font = self._get_font_for_cell()
        
        # Draw communities
        for y in range(H):
            for x in range(W):
                community = self.world.get_community_at(x, y)
                if community is None:
                    continue
                
                x0, y0 = x * cw, y * ch
                x1, y1 = x0 + cw, y0 + ch
                
                # Determine color and text
                if community.language_id >= 0:
                    language = self.simulation.get_language_by_id(community.language_id)
                    if language:
                        # Get a sample word for coloring
                        sample_word = ""
                        if language.lexicon:
                            sample_meaning = next(iter(language.lexicon))
                            sample_word = language.lexicon[sample_meaning].string_form
                        
                        rgb = word_to_color_cached(sample_word)
                        text = language.name[:4]  # Abbreviated name
                    else:
                        rgb = (100, 100, 100)
                        text = "???"
                else:
                    rgb = (30, 30, 30)
                    text = ""
                
                fill = rgb_hex(rgb)
                
                # Draw cell
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=fill, fill=fill)
                
                # Draw text if there's a language
                if text:
                    text_color = text_color_for_bg(rgb)
                    self.canvas.create_text((x0+x1)//2, (y0+y1)//2, text=text, 
                                          font=font, fill=text_color)
        
        # Draw boundaries between different languages
        if CONFIG.DRAW_BOUNDARIES:
            self._draw_language_boundaries()
    
    def _draw_language_boundaries(self):
        """Draw boundaries between different languages"""
        W, H = self.world.width, self.world.height
        cw, ch = self.cell_w, self.cell_h
        line_color = "#000000"
        
        for y in range(H):
            for x in range(W):
                community = self.world.get_community_at(x, y)
                if community is None or community.language_id < 0:
                    continue
                
                # Check right neighbor
                right_neighbor = self.world.get_community_at(x + 1, y)
                if (right_neighbor is not None and 
                    right_neighbor.language_id != community.language_id):
                    X = (x + 1) * cw
                    self.canvas.create_line(X, y * ch, X, (y + 1) * ch, 
                                          fill=line_color, width=2)
                
                # Check bottom neighbor
                bottom_neighbor = self.world.get_community_at(x, y + 1)
                if (bottom_neighbor is not None and 
                    bottom_neighbor.language_id != community.language_id):
                    Y = (y + 1) * ch
                    self.canvas.create_line(x * cw, Y, (x + 1) * cw, Y, 
                                          fill=line_color, width=2)

class LanguageEvolutionApp:
    """Main application class"""
    
    def __init__(self):
        # Generate world
        from world import generate_procedural_world
        mask = generate_procedural_world(
            CONFIG.GRID_W, CONFIG.GRID_H, 
            CONFIG.LAND_PROB_INIT, CONFIG.ISLAND_BIAS, CONFIG.SMOOTH_STEPS
        )
        self.world = World(mask)
        
        # Create simulation
        self.simulation = LanguageEvolutionSimulation(self.world)
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Language Evolution Simulator")
        self.root.geometry(f"{CONFIG.CANVAS_W}x{CONFIG.CANVAS_H}")
        
        # Create renderer
        self.renderer = LanguageRenderer(self.root, self.world, self.simulation)
        
        # Bind keys
        self.root.bind("<KeyPress-q>", lambda e: self.root.destroy())
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<KeyPress-r>", lambda e: self._reset_simulation())
        self.root.bind("<KeyPress-n>", lambda e: self._new_world())
        self.root.bind("<space>", lambda e: self._toggle_pause())
        
        # Control state
        self.paused = False
        
        # Start simulation loop
        self._simulation_loop()
    
    def _reset_simulation(self):
        """Reset the simulation with same world"""
        self.simulation = LanguageEvolutionSimulation(self.world)
    
    def _new_world(self):
        """Generate new world and reset simulation"""
        from world import generate_procedural_world
        mask = generate_procedural_world(
            CONFIG.GRID_W, CONFIG.GRID_H, 
            CONFIG.LAND_PROB_INIT, CONFIG.ISLAND_BIAS, CONFIG.SMOOTH_STEPS
        )
        self.world = World(mask)
        self.simulation = LanguageEvolutionSimulation(self.world)
        self.renderer.world = self.world
        self.renderer.simulation = self.simulation
    
    def _toggle_pause(self):
        """Toggle simulation pause"""
        self.paused = not self.paused
        print("Simulation", "paused" if self.paused else "resumed")
    
    def _simulation_loop(self):
        """Main simulation loop"""
        if not self.paused:
            self.simulation.step()
            self.renderer.draw()
        
        # Schedule next update
        self.root.after(50, self._simulation_loop)  # ~20 FPS
    
    def run(self):
        """Start the application"""
        print("Language Evolution Simulator")
        print("Controls:")
        print("  Q/Esc - Quit")
        print("  R - Reset simulation")
        print("  N - New world")
        print("  Space - Pause/Resume")
        print()
        
        self.root.focus_set()  # Enable key bindings
        self.root.mainloop()

def main():
    """Main entry point"""
    import random
    random.seed()  # Use random seed
    
    app = LanguageEvolutionApp()
    app.run()

if __name__ == "__main__":
    main()