"""
Visualization and rendering for the language evolution simulation
"""

import math
import tkinter as tk
import tkinter.font as tkfont
import colorsys
from functools import lru_cache
from typing import Dict, Tuple, Optional
from enum import Enum

from config import CONFIG
from world import World, Community
from simulation import LanguageEvolutionSimulation
from phonology import PHONEMES, RGB_PROJ

class MapMode(Enum):
    LANGUAGE_NAME = "language_name"
    VOCABULARY_ITEM = "vocabulary_item" 
    PHONOLOGICAL_RULES = "phonological_rules"
    LANGUAGE_FAMILY = "language_family"
    PHONEME_COUNT = "phoneme_count"
    SPEAKER_COUNT = "speaker_count"
    PRESTIGE = "prestige"

def dot(a, b) -> float:
    """Dot product of two vectors"""
    return sum(x*y for x, y in zip(a, b))

@lru_cache(maxsize=4096)
def hash_to_color(key: str) -> Tuple[int, int, int]:
    """Convert any string to a stable color using hash-based HSV"""
    if not key:
        return (200, 200, 200)
    
    # Hash the key to get consistent colors
    hash_val = hash(key) % 360  # Hue from 0-360
    
    # Convert HSV to RGB with fixed saturation and value
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(hash_val / 360.0, 0.7, 0.85)
    return (int(r * 255), int(g * 255), int(b * 255))

def gradient_color(value: int, min_val: int, max_val: int) -> Tuple[int, int, int]:
    """Map a numeric value to a color gradient"""
    if max_val == min_val:
        return (100, 150, 200)  # Default blue
    
    # Normalize to 0-1
    normalized = max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    # Blue to red gradient
    r = int(normalized * 255)
    g = int((1 - normalized) * 100)
    b = int((1 - normalized) * 255)
    return (r, g, b)

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
        
        # Mapmode state
        self.current_mapmode = MapMode.LANGUAGE_NAME
        self.current_vocabulary_word = "water"  # Default vocabulary item to display
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=CONFIG.CANVAS_W, height=CONFIG.CANVAS_H, 
                               bg="#101010", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Font cache
        self.font_cache: Dict[int, tkfont.Font] = {}
        
        # Bind resize event
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Bind click event
        self.canvas.bind("<Button-1>", self._on_click)
        
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
                min(CONFIG.MAX_FONT_PX, int(min(self.cell_w, self.cell_h) * 0.4)))
        
        if px not in self.font_cache:
            try:
                self.font_cache[px] = tkfont.Font(
                    family="Consolas" if tk.TkVersion >= 8.5 else "Courier", 
                    size=px, weight="normal"
                )
            except:
                self.font_cache[px] = tkfont.Font(size=px, weight="normal")
        
        return self.font_cache[px]
    
    def _should_show_text(self, x: int, y: int, language_id: int) -> bool:
        """Determine if this cell should show text based on its position in contiguous area"""
        W, H = self.world.width, self.world.height
        
        # Count same-language neighbors (4-connected only)
        neighbors_same = 0
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H:
                neighbor = self.world.get_community_at(nx, ny)
                if neighbor and neighbor.language_id == language_id:
                    neighbors_same += 1
        
        # Always show text for completely isolated cells
        if neighbors_same == 0:
            return True
            
        # Show text for small clusters (1-2 neighbors)
        if neighbors_same <= 1:
            return True
            
        # For larger areas, sparse grid pattern to avoid crowding
        text_spacing = 8  # Much wider spacing
        offset_x = (y % 2) * (text_spacing // 2)  # Stagger rows
        if (x + offset_x) % text_spacing == 3 and y % text_spacing == 3:
            return True
            
        # Show text only at strict language borders (not map edges)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H:
                neighbor = self.world.get_community_at(nx, ny)
                if neighbor is None or neighbor.language_id != language_id:
                    # Language boundary - only show if it's a significant border
                    border_count = 0
                    for dx2, dy2 in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx2, ny2 = x + dx2, y + dy2
                        if 0 <= nx2 < W and 0 <= ny2 < H:
                            neighbor2 = self.world.get_community_at(nx2, ny2)
                            if neighbor2 is None or neighbor2.language_id != language_id:
                                border_count += 1
                    # Only show text if this is a real border (2+ different neighbors)
                    if border_count >= 2:
                        return True
                    break
        
        return False
    
    def cycle_mapmode(self):
        """Cycle to the next mapmode"""
        modes = list(MapMode)
        current_index = modes.index(self.current_mapmode)
        self.current_mapmode = modes[(current_index + 1) % len(modes)]
        mode_descriptions = {
            MapMode.LANGUAGE_NAME: "Language Names",
            MapMode.VOCABULARY_ITEM: f"Vocabulary: {self.current_vocabulary_word}", 
            MapMode.PHONOLOGICAL_RULES: "Phonological Rules",
            MapMode.LANGUAGE_FAMILY: "Language Families",
            MapMode.PHONEME_COUNT: "Phoneme Counts",
            MapMode.SPEAKER_COUNT: "Speaker Counts",
            MapMode.PRESTIGE: "Language Prestige"
        }
        print(f"Mapmode: {mode_descriptions.get(self.current_mapmode, self.current_mapmode.value)}")
    
    def cycle_vocabulary_word(self):
        """Cycle to the next vocabulary word for vocabulary mapmode"""
        common_words = ["water", "fire", "tree", "stone", "fish", "bird", "sun", "moon", "hand", "head"]
        try:
            current_index = common_words.index(self.current_vocabulary_word)
            self.current_vocabulary_word = common_words[(current_index + 1) % len(common_words)]
        except ValueError:
            self.current_vocabulary_word = common_words[0]
        print(f"Vocabulary word: {self.current_vocabulary_word}")
        if self.current_mapmode == MapMode.VOCABULARY_ITEM:
            print(f"Mapmode: Vocabulary: {self.current_vocabulary_word}")
    
    def _get_mapmode_display_info(self, language, community_count: int) -> Tuple[str, str]:
        """Get display text and color key for current mapmode"""
        if self.current_mapmode == MapMode.LANGUAGE_NAME:
            return self._get_language_name_info(language)
        elif self.current_mapmode == MapMode.VOCABULARY_ITEM:
            return self._get_vocabulary_item_info(language)
        elif self.current_mapmode == MapMode.PHONOLOGICAL_RULES:
            return self._get_phonological_rules_info(language)
        elif self.current_mapmode == MapMode.LANGUAGE_FAMILY:
            return self._get_language_family_info(language)
        elif self.current_mapmode == MapMode.PHONEME_COUNT:
            return self._get_phoneme_count_info(language)
        elif self.current_mapmode == MapMode.SPEAKER_COUNT:
            return self._get_speaker_count_info(language, community_count)
        elif self.current_mapmode == MapMode.PRESTIGE:
            return self._get_prestige_info(language)
        else:
            return self._get_language_name_info(language)
    
    def _get_language_name_info(self, language) -> Tuple[str, str]:
        """Get info for language name mapmode - show actual language names"""
        language_name = language.name if hasattr(language, 'name') and language.name else f"Lang{language.id}"
        # Use language ID for consistent coloring
        color_key = str(language.id)
        # Strip apostrophes from display text
        clean_name = language_name.replace("'", "")
        display_text = clean_name[:8] if len(clean_name) <= 8 else clean_name[:6] + ".."
        return color_key, display_text
    
    def _get_vocabulary_item_info(self, language) -> Tuple[str, str]:
        """Get info for vocabulary item mapmode"""
        if language.lexicon and self.current_vocabulary_word in language.lexicon:
            word_obj = language.lexicon[self.current_vocabulary_word]
            word_form = word_obj.string_form
            display_text = word_form[:8] if len(word_form) <= 8 else word_form[:6] + ".."
            return word_form, display_text
        return "", "---"
    
    def _get_phonological_rules_info(self, language) -> Tuple[str, str]:
        """Get info for phonological rules mapmode"""
        # Summarize phonotactic constraints
        constraints = language.phonotactic_constraints
        if hasattr(constraints, 'syllable_types') and constraints.syllable_types:
            # Get dominant syllable type
            dominant_type = max(constraints.syllable_types.items(), key=lambda x: x[1])
            if hasattr(dominant_type[0], 'name'):
                rule_summary = dominant_type[0].name[:4]  # First 4 chars of syllable type
            else:
                rule_summary = str(dominant_type[0])[:4]
            return rule_summary, rule_summary
        # Fallback: use phoneme count as proxy for rule complexity
        phoneme_count = len(language.phoneme_inventory)
        if phoneme_count < 20:
            rule_summary = "SIMP"
        elif phoneme_count < 40:
            rule_summary = "MED"
        else:
            rule_summary = "COMP"
        return rule_summary, rule_summary
    
    def _get_language_family_info(self, language) -> Tuple[str, str]:
        """Get info for language family mapmode - trace to root ancestor"""
        # Find root ancestor by walking parent chain
        root_ancestor = language
        visited = {language.id}  # Prevent infinite loops
        
        while (hasattr(root_ancestor, 'parent_id') and 
               root_ancestor.parent_id is not None and 
               root_ancestor.parent_id not in visited):
            parent = self.simulation.get_language_by_id(root_ancestor.parent_id)
            if parent:
                visited.add(root_ancestor.parent_id)
                root_ancestor = parent
            else:
                break
        
        family_id = f"family_{root_ancestor.id}"
        return family_id, f"F{root_ancestor.id}"
    
    def _get_phoneme_count_info(self, language) -> Tuple[str, str]:
        """Get info for phoneme count mapmode"""
        count = len(language.phoneme_inventory)
        # Use count as both color key and display
        count_str = str(count)
        return count_str, count_str
    
    def _get_speaker_count_info(self, language, community_count: int) -> Tuple[str, str]:
        """Get info for speaker count mapmode"""
        # Use community count as proxy for speaker count
        count_str = str(community_count)
        return count_str, count_str
    
    def _get_prestige_info(self, language) -> Tuple[str, str]:
        """Get info for prestige mapmode"""
        # Convert prestige to integer (multiply by 1000 for precision in display)
        prestige_int = int(language.prestige * 1000)
        # Format for display (show as percentage)
        prestige_display = f"{int(language.prestige * 100)}%"
        return str(prestige_int), prestige_display
    
    def draw(self):
        """Draw the current state of the simulation"""
        W, H = self.world.width, self.world.height
        cw, ch = self.cell_w, self.cell_h
        
        self.canvas.delete("all")
        font = self._get_font_for_cell()
        
        # First pass: count communities per language for speaker count mapmode
        language_community_counts = {}
        for y in range(H):
            for x in range(W):
                community = self.world.get_community_at(x, y)
                if community is not None and community.language_id >= 0:
                    language_community_counts[community.language_id] = language_community_counts.get(community.language_id, 0) + 1
        
        # Pre-compute numeric values for gradient modes to get proper min/max
        language_numeric_values = {}
        gradient_min, gradient_max = 0, 1
        if self.current_mapmode in [MapMode.PHONEME_COUNT, MapMode.SPEAKER_COUNT, MapMode.PRESTIGE]:
            for lang_id, count in language_community_counts.items():
                language = self.simulation.get_language_by_id(lang_id)
                if language:
                    if self.current_mapmode == MapMode.PHONEME_COUNT:
                        language_numeric_values[lang_id] = len(language.phoneme_inventory)
                    elif self.current_mapmode == MapMode.SPEAKER_COUNT:
                        language_numeric_values[lang_id] = count
                    elif self.current_mapmode == MapMode.PRESTIGE:
                        # Convert prestige to integer (multiply by 1000 for precision)
                        language_numeric_values[lang_id] = int(language.prestige * 1000)
            
            # Compute global min/max once
            if language_numeric_values:
                all_values = list(language_numeric_values.values())
                gradient_min, gradient_max = min(all_values), max(all_values)
        
        # Cache mapmode display info per language
        language_display_info = {}  # Cache display info per language
        
        # Draw communities
        for y in range(H):
            for x in range(W):
                community = self.world.get_community_at(x, y)
                if community is None:
                    continue
                
                x0, y0 = x * cw, y * ch
                x1, y1 = x0 + cw, y0 + ch
                
                # Determine color and text using mapmode system
                if community.language_id >= 0:
                    language = self.simulation.get_language_by_id(community.language_id)
                    if language:
                        # Get cached mapmode display info for this language
                        if community.language_id not in language_display_info:
                            community_count = language_community_counts.get(community.language_id, 0)
                            color_key, display_text = self._get_mapmode_display_info(language, community_count)
                            language_display_info[community.language_id] = (color_key, display_text)
                        
                        color_key, display_text = language_display_info[community.language_id]
                        
                        # Use appropriate color function based on mapmode
                        if self.current_mapmode == MapMode.VOCABULARY_ITEM:
                            rgb = word_to_color_cached(color_key) if color_key else (100, 100, 100)
                        elif self.current_mapmode in [MapMode.PHONEME_COUNT, MapMode.SPEAKER_COUNT, MapMode.PRESTIGE]:
                            # Use gradient colors for numeric modes with pre-computed min/max
                            value = language_numeric_values.get(community.language_id, 0)
                            rgb = gradient_color(value, gradient_min, gradient_max)
                        else:
                            # Use hash-based colors for categorical modes
                            rgb = hash_to_color(color_key) if color_key else (100, 100, 100)
                        
                        # Determine if this cell should show text
                        should_show = self._should_show_text(x, y, community.language_id)
                        text = display_text if should_show else ""
                    else:
                        rgb = (100, 100, 100)
                        text = "???"
                else:
                    rgb = (30, 30, 30)
                    text = ""
                
                fill = rgb_hex(rgb)
                
                # Draw cell
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=fill, fill=fill)
                
                # Draw text if determined to show it
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
        
        def should_draw_boundary(community1, community2):
            """Check if boundary should be drawn between two communities"""
            if community1.language_id == community2.language_id:
                return False
            
            # Get languages and compare names without apostrophes
            lang1 = self.simulation.get_language_by_id(community1.language_id)
            lang2 = self.simulation.get_language_by_id(community2.language_id)
            
            if lang1 and lang2:
                name1 = lang1.name.replace("'", "") if hasattr(lang1, 'name') and lang1.name else f"Lang{lang1.id}"
                name2 = lang2.name.replace("'", "") if hasattr(lang2, 'name') and lang2.name else f"Lang{lang2.id}"
                return name1 != name2
            
            return True  # Draw boundary if we can't get language info
        
        for y in range(H):
            for x in range(W):
                community = self.world.get_community_at(x, y)
                if community is None or community.language_id < 0:
                    continue
                
                # Check right neighbor
                right_neighbor = self.world.get_community_at(x + 1, y)
                if (right_neighbor is not None and 
                    should_draw_boundary(community, right_neighbor)):
                    X = (x + 1) * cw
                    self.canvas.create_line(X, y * ch, X, (y + 1) * ch, 
                                          fill=line_color, width=2)
                
                # Check bottom neighbor
                bottom_neighbor = self.world.get_community_at(x, y + 1)
                if (bottom_neighbor is not None and 
                    should_draw_boundary(community, bottom_neighbor)):
                    Y = (y + 1) * ch
                    self.canvas.create_line(x * cw, Y, (x + 1) * cw, Y, 
                                          fill=line_color, width=2)
    
    def _on_click(self, event):
        """Handle mouse click on canvas"""
        # Calculate which cell was clicked
        grid_x = event.x // max(1, self.cell_w)
        grid_y = event.y // max(1, self.cell_h)
        
        # Check bounds explicitly
        if not (0 <= grid_x < self.world.width and 0 <= grid_y < self.world.height):
            return
        
        # Get the community at that position
        community = self.world.get_community_at(grid_x, grid_y)
        if community is None or community.language_id < 0:
            return
        
        # Get the language
        language = self.simulation.get_language_by_id(community.language_id)
        if language is None:
            return
        
        # Open language detail window
        LanguageDetailWindow(self.root, language)

class LanguageDetailWindow:
    """Window for displaying detailed language information"""
    
    def __init__(self, parent: tk.Tk, language):
        from language import Language
        self.language: Language = language
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Language Details: {language.name}")
        self.window.geometry("800x600")
        self.window.configure(bg="#f0f0f0")
        
        # Make window modal
        self.window.transient(parent)
        
        # Setup UI first
        self._create_widgets()
        
        # Center window on parent
        self.window.update_idletasks()  # Ensure window is fully created
        
        # Safe grab set after window is ready
        try:
            self.window.grab_set()
        except tk.TclError:
            pass  # Window might not be viewable yet, ignore gracefully
    
    def _create_widgets(self):
        """Create the UI widgets"""
        # Create scrollable main frame
        canvas = tk.Canvas(self.window, bg="#f0f0f0")
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(scrollable_frame, text=self.language.name, 
                              font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=(0, 20))
        
        # Language Overview Section
        self._create_overview_section(scrollable_frame)
        
        # Phonological System Section
        self._create_phonology_section(scrollable_frame)
        
        # Vocabulary Section
        self._create_vocabulary_section(scrollable_frame)
    
    def _create_overview_section(self, parent):
        """Create the language overview section"""
        overview_frame = tk.LabelFrame(parent, text="Language Overview", 
                                     font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333")
        overview_frame.pack(fill="x", pady=(0, 10))
        
        # Create a grid for the overview information
        details_frame = tk.Frame(overview_frame, bg="#f0f0f0")
        details_frame.pack(padx=10, pady=10, fill="x")
        
        # Language ID
        tk.Label(details_frame, text="Language ID:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").grid(row=0, column=0, sticky="w", padx=(0, 10))
        tk.Label(details_frame, text=str(self.language.id), font=("Arial", 10), 
                bg="#f0f0f0", fg="#666").grid(row=0, column=1, sticky="w")
        
        # Generation
        tk.Label(details_frame, text="Generation:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").grid(row=1, column=0, sticky="w", padx=(0, 10))
        tk.Label(details_frame, text=str(self.language.generation), font=("Arial", 10), 
                bg="#f0f0f0", fg="#666").grid(row=1, column=1, sticky="w")
        
        # Prestige
        prestige_pct = f"{self.language.prestige:.1%}"
        tk.Label(details_frame, text="Prestige:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").grid(row=2, column=0, sticky="w", padx=(0, 10))
        tk.Label(details_frame, text=prestige_pct, font=("Arial", 10), 
                bg="#f0f0f0", fg="#666").grid(row=2, column=1, sticky="w")
        
        # Conservatism
        conservatism_pct = f"{self.language.conservatism:.1%}"
        tk.Label(details_frame, text="Conservatism:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").grid(row=3, column=0, sticky="w", padx=(0, 10))
        tk.Label(details_frame, text=conservatism_pct, font=("Arial", 10), 
                bg="#f0f0f0", fg="#666").grid(row=3, column=1, sticky="w")
        
        # Phoneme count (with defensive fallback)
        try:
            phoneme_count = self.language.get_phoneme_count()
        except AttributeError:
            phoneme_count = len(getattr(self.language, 'phoneme_inventory', set()))
        tk.Label(details_frame, text="Phonemes:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").grid(row=4, column=0, sticky="w", padx=(0, 10))
        tk.Label(details_frame, text=str(phoneme_count), font=("Arial", 10), 
                bg="#f0f0f0", fg="#666").grid(row=4, column=1, sticky="w")
        
        # Vocabulary size (with defensive fallback)
        try:
            vocab_size = self.language.get_vocabulary_size()
        except AttributeError:
            vocab_size = len(getattr(self.language, 'lexicon', {}))
        tk.Label(details_frame, text="Vocabulary Size:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").grid(row=5, column=0, sticky="w", padx=(0, 10))
        tk.Label(details_frame, text=str(vocab_size), font=("Arial", 10), 
                bg="#f0f0f0", fg="#666").grid(row=5, column=1, sticky="w")
        
        # Parent language (if any)
        if self.language.parent_id is not None:
            tk.Label(details_frame, text="Parent Language ID:", font=("Arial", 10, "bold"), 
                    bg="#f0f0f0", fg="#333").grid(row=6, column=0, sticky="w", padx=(0, 10))
            tk.Label(details_frame, text=str(self.language.parent_id), font=("Arial", 10), 
                    bg="#f0f0f0", fg="#666").grid(row=6, column=1, sticky="w")
    
    def _create_phonology_section(self, parent):
        """Create the phonological system section"""
        from phonology import is_syllabic
        
        phonology_frame = tk.LabelFrame(parent, text="Phonological System", 
                                      font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333")
        phonology_frame.pack(fill="x", pady=(10, 0))
        
        phonology_content = tk.Frame(phonology_frame, bg="#f0f0f0")
        phonology_content.pack(padx=10, pady=10, fill="x")
        
        # Get phoneme inventory
        phoneme_inventory = getattr(self.language, 'phoneme_inventory', set())
        
        if not phoneme_inventory:
            no_phonemes_label = tk.Label(phonology_content, text="No phoneme inventory available", 
                                       font=("Arial", 10), bg="#f0f0f0", fg="#666")
            no_phonemes_label.pack()
            return
        
        # Categorize phonemes with defensive handling
        vowels = []
        consonants = []
        other = []
        
        for phoneme in sorted(phoneme_inventory):
            try:
                if is_syllabic(phoneme):
                    vowels.append(phoneme)
                else:
                    consonants.append(phoneme)
            except (KeyError, ValueError):
                # Handle unknown phonemes
                other.append(phoneme)
        
        # Display vowels
        if vowels:
            vowel_frame = tk.Frame(phonology_content, bg="#f0f0f0")
            vowel_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(vowel_frame, text=f"Vowels ({len(vowels)}):", font=("Arial", 10, "bold"), 
                    bg="#f0f0f0", fg="#333").pack(anchor="w")
            
            vowel_text = " ".join(vowels)
            tk.Label(vowel_frame, text=vowel_text, font=("Arial", 10), 
                    bg="#f0f0f0", fg="#666", wraplength=600, justify="left").pack(anchor="w", padx=(20, 0))
        
        # Display consonants
        if consonants:
            consonant_frame = tk.Frame(phonology_content, bg="#f0f0f0")
            consonant_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(consonant_frame, text=f"Consonants ({len(consonants)}):", font=("Arial", 10, "bold"), 
                    bg="#f0f0f0", fg="#333").pack(anchor="w")
            
            consonant_text = " ".join(consonants)
            tk.Label(consonant_frame, text=consonant_text, font=("Arial", 10), 
                    bg="#f0f0f0", fg="#666", wraplength=600, justify="left").pack(anchor="w", padx=(20, 0))
        
        # Display other/unknown phonemes if any
        if other:
            other_frame = tk.Frame(phonology_content, bg="#f0f0f0")
            other_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(other_frame, text=f"Other ({len(other)}):", font=("Arial", 10, "bold"), 
                    bg="#f0f0f0", fg="#333").pack(anchor="w")
            
            other_text = " ".join(other)
            tk.Label(other_frame, text=other_text, font=("Arial", 10), 
                    bg="#f0f0f0", fg="#666", wraplength=600, justify="left").pack(anchor="w", padx=(20, 0))
        
        # Total count
        total_frame = tk.Frame(phonology_content, bg="#f0f0f0")
        total_frame.pack(fill="x", pady=(10, 0))
        
        total_parts = []
        if vowels:
            total_parts.append(f"{len(vowels)} vowels")
        if consonants:
            total_parts.append(f"{len(consonants)} consonants")
        if other:
            total_parts.append(f"{len(other)} other")
        
        total_text = f"Total phonemes: {len(phoneme_inventory)}"
        if total_parts:
            total_text += f" ({', '.join(total_parts)})"
        
        tk.Label(total_frame, text=total_text, font=("Arial", 9, "italic"), 
                bg="#f0f0f0", fg="#888").pack(anchor="w")
        
        # Add phonotactic constraints information
        self._add_phonotactic_info(phonology_content)
    
    def _create_vocabulary_section(self, parent):
        """Create the searchable vocabulary section"""
        vocab_frame = tk.LabelFrame(parent, text="Vocabulary", 
                                  font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333")
        vocab_frame.pack(fill="x", pady=(10, 0))
        
        vocab_content = tk.Frame(vocab_frame, bg="#f0f0f0")
        vocab_content.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Get lexicon
        lexicon = getattr(self.language, 'lexicon', {})
        
        if not lexicon:
            no_vocab_label = tk.Label(vocab_content, text="No vocabulary available", 
                                    font=("Arial", 10), bg="#f0f0f0", fg="#666")
            no_vocab_label.pack()
            return
        
        # Search frame
        search_frame = tk.Frame(vocab_content, bg="#f0f0f0")
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self._filter_vocabulary())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 10))
        search_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # Results frame with scrollbar
        results_container = tk.Frame(vocab_content, bg="#f0f0f0")
        results_container.pack(fill="both", expand=True)
        
        # Create scrollable text widget for vocabulary display
        vocab_scroll = tk.Scrollbar(results_container)
        vocab_scroll.pack(side="right", fill="y")
        
        self.vocab_text = tk.Text(results_container, height=15, font=("Consolas", 9), 
                                bg="white", fg="#333", wrap="word", 
                                yscrollcommand=vocab_scroll.set, state="disabled")
        self.vocab_text.pack(side="left", fill="both", expand=True)
        vocab_scroll.config(command=self.vocab_text.yview)
        
        # Store original lexicon for filtering
        self.original_lexicon = lexicon
        
        # Display all vocabulary initially
        self._display_vocabulary(lexicon)
    
    def _filter_vocabulary(self):
        """Filter vocabulary based on search term"""
        search_term = self.search_var.get().lower().strip()
        
        if not search_term:
            # Show all vocabulary
            filtered_lexicon = self.original_lexicon
        else:
            # Filter by meaning or word form
            filtered_lexicon = {}
            for meaning, word in self.original_lexicon.items():
                word_form = word.string_form if hasattr(word, 'string_form') else str(word)
                if (search_term in meaning.lower() or 
                    search_term in word_form.lower()):
                    filtered_lexicon[meaning] = word
        
        self._display_vocabulary(filtered_lexicon)
    
    def _display_vocabulary(self, lexicon_dict):
        """Display the vocabulary in the text widget"""
        self.vocab_text.config(state="normal")
        self.vocab_text.delete("1.0", "end")
        
        if not lexicon_dict:
            self.vocab_text.insert("end", "No matching vocabulary found.")
        else:
            # Sort by meaning for consistent display
            sorted_items = sorted(lexicon_dict.items(), key=lambda x: x[0].lower())
            
            for i, (meaning, word) in enumerate(sorted_items):
                # Get word form
                word_form = word.string_form if hasattr(word, 'string_form') else str(word)
                
                # Format entry
                entry = f"{meaning:<20} → {word_form}"
                
                # Add origin information if available
                if hasattr(word, 'origin_lang_id') and hasattr(word, 'borrowed_from'):
                    if word.borrowed_from is not None:
                        entry += f"  (borrowed from lang {word.borrowed_from})"
                    elif hasattr(word, 'generation') and word.generation > 0:
                        entry += f"  (gen {word.generation})"
                
                self.vocab_text.insert("end", entry)
                if i < len(sorted_items) - 1:
                    self.vocab_text.insert("end", "\n")
            
            # Add summary
            total_count = len(lexicon_dict)
            self.vocab_text.insert("end", f"\n\nShowing {total_count} word(s)")
        
        self.vocab_text.config(state="disabled")
    
    def _add_phonotactic_info(self, parent):
        """Add phonotactic constraints information to the phonology section"""
        try:
            phonotactic_info = self.language.get_phonotactic_info()
            constraint_summary = self.language.get_constraint_summary()
        except AttributeError:
            # Fallback for languages without constraint info
            return
        
        # Constraints summary frame
        constraints_frame = tk.Frame(parent, bg="#f0f0f0")
        constraints_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(constraints_frame, text="Phonotactic Rules:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").pack(anchor="w")
        
        # Summary
        summary_label = tk.Label(constraints_frame, text=constraint_summary, 
                               font=("Arial", 9), bg="#f0f0f0", fg="#666",
                               wraplength=600, justify="left")
        summary_label.pack(anchor="w", padx=(20, 0), pady=(5, 0))
        
        # Syllable structure details
        syllable_frame = tk.Frame(parent, bg="#f0f0f0")
        syllable_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(syllable_frame, text="Syllable Structure Preferences:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg="#333").pack(anchor="w")
        
        # Show top syllable types
        syllable_types = phonotactic_info.get('syllable_types', {})
        if syllable_types:
            sorted_types = sorted(syllable_types.items(), key=lambda x: x[1], reverse=True)
            syll_text = ""
            for syll_type, prob in sorted_types[:5]:  # Show top 5
                syll_text += f"{syll_type.value}: {prob:.1%}   "
            
            tk.Label(syllable_frame, text=syll_text, font=("Consolas", 9), 
                    bg="#f0f0f0", fg="#666", wraplength=600, justify="left").pack(anchor="w", padx=(20, 0))
        
        # Word length info
        word_length = phonotactic_info.get('word_length', {})
        if word_length:
            length_frame = tk.Frame(parent, bg="#f0f0f0")
            length_frame.pack(fill="x", pady=(5, 0))
            
            length_text = f"Word Length: {word_length['min_syllables']}-{word_length['max_syllables']} syllables (prefers {word_length['preferred_syllables']})"
            tk.Label(length_frame, text=length_text, font=("Arial", 9), 
                    bg="#f0f0f0", fg="#666").pack(anchor="w", padx=(20, 0))
        
        # Coda constraints
        allowed_codas = phonotactic_info.get('allowed_codas', [])
        if allowed_codas:
            coda_frame = tk.Frame(parent, bg="#f0f0f0")
            coda_frame.pack(fill="x", pady=(5, 0))
            
            coda_text = f"Allowed syllable codas: {' '.join(allowed_codas)}"
            tk.Label(coda_frame, text=coda_text, font=("Consolas", 9), 
                    bg="#f0f0f0", fg="#666", wraplength=600, justify="left").pack(anchor="w", padx=(20, 0))
        
        # Consonant clusters
        onset_clusters = phonotactic_info.get('onset_clusters', 0)
        coda_clusters = phonotactic_info.get('coda_clusters', 0)
        if onset_clusters > 0 or coda_clusters > 0:
            cluster_frame = tk.Frame(parent, bg="#f0f0f0")
            cluster_frame.pack(fill="x", pady=(5, 0))
            
            cluster_text = f"Consonant clusters: {onset_clusters} onset types, {coda_clusters} coda types"
            tk.Label(cluster_frame, text=cluster_text, font=("Arial", 9), 
                    bg="#f0f0f0", fg="#666").pack(anchor="w", padx=(20, 0))
        
        # Gemination
        gemination = phonotactic_info.get('gemination', {})
        if gemination.get('allowed', False):
            gem_frame = tk.Frame(parent, bg="#f0f0f0")
            gem_frame.pack(fill="x", pady=(5, 0))
            
            geminable = gemination.get('geminable_consonants', [])
            gem_text = f"Gemination: {gemination['probability']:.1%} chance"
            if geminable:
                gem_text += f" ({' '.join(geminable[:8])}{'...' if len(geminable) > 8 else ''})"
            
            tk.Label(gem_frame, text=gem_text, font=("Consolas", 9), 
                    bg="#f0f0f0", fg="#666", wraplength=600, justify="left").pack(anchor="w", padx=(20, 0))
        
        # Mora information
        if phonotactic_info.get('mora_based', False):
            mora_constraints = phonotactic_info.get('mora_constraints', {})
            if mora_constraints:
                mora_frame = tk.Frame(parent, bg="#f0f0f0")
                mora_frame.pack(fill="x", pady=(5, 0))
                
                mora_text = f"Mora system: {mora_constraints['min_mora']}-{mora_constraints['max_mora']} mora per word"
                tk.Label(mora_frame, text=mora_text, font=("Arial", 9), 
                        bg="#f0f0f0", fg="#666").pack(anchor="w", padx=(20, 0))

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
        self.root.bind("<KeyPress-m>", lambda e: self._cycle_mapmode())
        self.root.bind("<KeyPress-v>", lambda e: self._cycle_vocabulary_word())
        
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
    
    def _cycle_mapmode(self):
        """Cycle mapmode and redraw"""
        self.renderer.cycle_mapmode()
        self.renderer.draw()
        self.root.focus_set()  # Ensure window keeps focus for key events
    
    def _cycle_vocabulary_word(self):
        """Cycle vocabulary word and redraw"""
        self.renderer.cycle_vocabulary_word()
        self.renderer.draw()
        self.root.focus_set()  # Ensure window keeps focus for key events
    
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
        print("  M - Cycle mapmode (language name/vocabulary/rules/family/phonemes/speakers)")
        print("  V - Cycle vocabulary word (when in vocabulary mapmode)")
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