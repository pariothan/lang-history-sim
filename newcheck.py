#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language‑Virus Simulator (Procedural World)
------------------------------------------
A fast, visual “language‑virus” simulator that spreads short IPA‑like words across a procedurally generated map.

Quick start:
  pip install pillow  # only used for font fallback on some systems; core runs without images
  python language_virus.py

Keys:
  N - new procedural world
  R - reseed infection with starter word
  Q or Esc - quit

Tweakables are in the CONFIG block below.
"""

import math
import random
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image  # noqa: F401  # optional (not required at runtime here)
except Exception:
    pass

import tkinter as tk
import tkinter.font as tkfont

# ---------------------------
# CONFIG
# ---------------------------
class CONFIG:
    # Procedural world gneration (no PNG needed)
    GRID_W = 50
    GRID_H = 50

    LAND_PROB_INIT = 0.25   # initial random land probability
    ISLAND_BIAS   = 0.35    # pushes land toward center (0..1)
    SMOOTH_STEPS  = 5       # cellular automata smoothing passes

    CANVAS_W = 1920
    CANVAS_H = 1080

    STARTER_WORD = ["k", "i", "t"]

    P_MUTATE = 0.003
    P_SPREAD = 0.10

    # Mutation operator choice weights (mutate / delete / add)
    MUTATE_OP_WEIGHTS = (0.6, 0.2, 0.2)

    # Addition “sweet‑spot” (feature distance) and sharpness
    ADD_SWEET_DIST = 2.0
    ADD_SWEET_BETA = 0.7

    # Similarity sharpness for picking a replacement phoneme during mutation
    MUTATE_ALPHA = 0.7

    # Drawing
    DRAW_GRID_LINES = True
    MAX_FONT_PX = 22
    MIN_FONT_PX = 8

    # Console leaderboard
    PRINT_LEADERBOARD = True
    LEADERBOARD_TOPK = 10

# ---------------------------
# PHONOLOGY: FEATURES & INVENTORY
# ---------------------------
FEATURES = [
    "syllabic",     # + vowel, - consonant
    "consonantal",  # + consonant, - vowel/glide
    "sonorant",     # + vowels, nasals, liquids, glides; - obstruents
    "continuant",   # + fricatives/liquids/glides, - stops/nasals
    "nasal",        # + m n, - otherwise
    "lateral",      # + l
    "voice",        # + voiced
    "labial",       # + p b f v m w, rounded vowels
    "coronal",      # + t d s z ʃ ʒ n l r
    "dorsal",       # + k g j w vowels
    "high",         # + i u, - a
    "low",          # + a
    "back",         # + u o, - i e
    "round",        # + u o w; - i e
]

V = Dict[str, int]

def fv(**kw: int) -> List[int]:
    vec = {k: 0 for k in FEATURES}
    vec.update(kw)
    return [vec[f] for f in FEATURES]

PHONEMES: Dict[str, List[int]] = {
    # Vowels
    "i":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, low=-1, back=-1, round=-1),
    "e":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=0,  low=0,  back=-1, round=-1),
    "a":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=-1, low=+1, back=0,  round=-1),
    "o":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=0,  low=0,  back=+1, round=+1),
    "u":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, low=-1, back=+1, round=+1),

    # Stops
    "p":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=+1, coronal=-1, dorsal=-1),
    "b":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1),
    "t":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1),
    "d":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "k":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1),
    "g":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1),

    # Fricatives
    "f":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=+1, coronal=-1, dorsal=-1),
    "v":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1),
    "s":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1),
    "z":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "ʃ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1),
    "ʒ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "h":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=0,  coronal=0,  dorsal=0),

    # Nasals
    "m":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1),
    "n":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),

    # Liquids
    "l":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, lateral=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "r":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),

    # Glides
    "j":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, back=-1, round=-1),
    "w":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, back=+1, round=+1),
}

INVENTORY = sorted(PHONEMES.keys())
IDX = {p: i for i, p in enumerate(INVENTORY)}
SYLLABIC_IDX = FEATURES.index("syllabic")

RGB_PROJ = (
    [ 0.8, -0.4,  0.2,  0.3,  0.1,  0.2,  0.3,  0.6, -0.2,  0.1,  0.9, -0.3, -0.5, -0.6],  # R
    [-0.4,  0.8,  0.1,  0.5,  0.2, -0.2,  0.3,  0.1,  0.6,  0.2, -0.5,  0.7,  0.4, -0.2],  # G
    [ 0.1,  0.2,  0.8, -0.4, -0.2,  0.5, -0.3, -0.2,  0.2,  0.7,  0.3,  0.1, -0.1,  0.9],  # B
)

# ---------------------------
# DISTANCES & SAMPLING TABLES
# ---------------------------

def feature_distance(a: List[int], b: List[int]) -> int:
    d = 0
    for x, y in zip(a, b):
        if x == 0 and y == 0:
            continue
        if x == 0 or y == 0:
            d += 2
        elif x != y:
            d += 1
    return d

VECS = [PHONEMES[p] for p in INVENTORY]
DIST = [[feature_distance(VECS[i], VECS[j]) for j in range(len(INVENTORY))] for i in range(len(INVENTORY))]

MUT_WEIGHTS: List[List[float]] = []
for i in range(len(INVENTORY)):
    row = []
    for j in range(len(INVENTORY)):
        d = DIST[i][j]
        row.append(math.exp(-CONFIG.MUTATE_ALPHA * d))
    MUT_WEIGHTS.append(row)

# ---------------------------
# PROCEDURAL WORLD GENERATION (cellular automata islands)
# ---------------------------

def generate_procedural_mask(w: int, h: int, land_prob: float, island_bias: float, smooth_steps: int) -> List[List[bool]]:
    # Initial random fill with radial bias toward center
    cx, cy = (w-1)/2.0, (h-1)/2.0
    maxr = math.hypot(cx, cy)
    grid = [[False for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r = math.hypot(x - cx, y - cy) / (maxr + 1e-9)
            bias = (1.0 - r) * island_bias
            p = max(0.0, min(1.0, land_prob + bias))
            grid[y][x] = (random.random() < p)

    def count_neighbors8(xx: int, yy: int) -> int:
        c = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = xx + dx, yy + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx]:
                    c += 1
        return c

    # Smooth with common cave rules
    for _ in range(smooth_steps):
        newg = [[False for _ in range(w)] for _ in range(h)]
        for y in range(h):
            for x in range(w):
                n = count_neighbors8(x, y)
                if grid[y][x]:
                    newg[y][x] = (n >= 3)   # survive if not too isolated
                else:
                    newg[y][x] = (n >= 5)   # birth in dense areas
        grid = newg

    return grid

# ---------------------------
# MAP & HOSTS
# ---------------------------
@dataclass
class Host:
    x: int
    y: int
    virus: Optional[List[str]] = None
    cached_word: str = ""

    def set_word(self, segs: List[str]):
        self.virus = list(segs)
        self.cached_word = "".join(segs)


class World:
    def __init__(self, mask: List[List[bool]]):
        self.height = len(mask)
        self.width = len(mask[0]) if self.height else 0
        self.grid: List[List[Optional[Host]]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.land_hosts: List[Host] = []

        for y in range(self.height):
            for x in range(self.width):
                if mask[y][x]:
                    h = Host(x, y)
                    self.grid[y][x] = h
                    self.land_hosts.append(h)

        self.index_of = {(h.x, h.y): i for i, h in enumerate(self.land_hosts)}
        self._perm: List[int] = list(range(len(self.land_hosts)))

    def host_at(self, x: int, y: int) -> Optional[Host]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def neighbors4(self, x: int, y: int) -> List[Host]:
        out = []
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
            h = self.host_at(x+dx, y+dy)
            if h is not None:
                out.append(h)
        return out

    def random_land_host(self) -> Host:
        return random.choice(self.land_hosts)

    def shuffle_perm(self):
        random.shuffle(self._perm)

    def perm(self) -> List[int]:
        return self._perm

# ---------------------------
# WORD UTILITIES
# ---------------------------

def is_syllabic(phon: str) -> bool:
    return PHONEMES[phon][SYLLABIC_IDX] > 0


def syllable_count(word: List[str]) -> int:
    return sum(1 for p in word if is_syllabic(p))


def ensure_has_vowel(word: List[str]):
    if syllable_count(word) == 0:
        vowels = [p for p in INVENTORY if is_syllabic(p)]
        word.insert(len(word)//2, random.choice(vowels))

# ---------------------------
# COLOR MAPPING
# ---------------------------

def dot(a: List[int], b: List[float]) -> float:
    return sum(x*y for x, y in zip(a, b))


@lru_cache(maxsize=4096)
def word_to_color_cached(word_key: str) -> Tuple[int, int, int]:
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
    return "#%02x%02x%02x" % rgb


def text_color_for_bg(rgb: Tuple[int,int,int]) -> str:
    R, G, B = rgb
    Y = 0.2126*R + 0.7152*G + 0.0722*B
    return "#000000" if Y > 135 else "#ffffff"

# ---------------------------
# MUTATION & SPREAD
# ---------------------------

def mutate_replace(seg: str) -> str:
    i = IDX[seg]
    weights = MUT_WEIGHTS[i]
    j = random.choices(range(len(INVENTORY)), weights=weights, k=1)[0]
    return INVENTORY[j]


def mutate_delete(word: List[str]) -> Optional[int]:
    if not word:
        return None
    vowel_positions = [i for i, p in enumerate(word) if is_syllabic(p)]
    if len(vowel_positions) == 1:
        consonant_positions = [i for i, p in enumerate(word) if not is_syllabic(p)]
        if consonant_positions:
            return random.choice(consonant_positions)
        return None
    return random.randrange(0, len(word))


def mutate_add(word: List[str]) -> Tuple[int, str]:
    anchor_idx = random.randrange(0, len(word)) if word else 0
    anchor = word[anchor_idx] if word else random.choice(INVENTORY)
    ai = IDX[anchor]
    weights = []
    for j in range(len(INVENTORY)):
        d = DIST[ai][j]
        w = math.exp(-CONFIG.ADD_SWEET_BETA * (d - CONFIG.ADD_SWEET_DIST)**2)
        weights.append(w)
    pick = random.choices(range(len(INVENTORY)), weights=weights, k=1)[0]
    seg = INVENTORY[pick]
    pos = max(0, min(len(word), anchor_idx + random.choice((0,1))))
    return pos, seg


def try_spread(world: 'World', src: Host):
    if not world.land_hosts:
        return
    world.shuffle_perm()
    sx, sy = src.x, src.y
    for idx in world.perm():
        tgt = world.land_hosts[idx]
        if tgt is src:
            continue
        steps = abs(tgt.x - sx) + abs(tgt.y - sy)
        if steps <= 0:
            continue
        p = (1/3) ** (steps - 1)
        if random.random() < p:
            if src.virus is None:
                return
            tgt.set_word(src.virus)
            return

# ---------------------------
# SIMULATION
# ---------------------------
class Simulation:
    def __init__(self, world: 'World'):
        self.world = world
        self.tick_count = 0
        self.reseed()

    def reseed(self):
        for h in self.world.land_hosts:
            h.virus = None
            h.cached_word = ""
        seed = self.world.random_land_host()
        seed.set_word(list(CONFIG.STARTER_WORD))
        self.tick_count = 0

    def step(self):
        if CONFIG.PRINT_LEADERBOARD and (self.tick_count % 1 == 0):
            counts: Dict[str, int] = {}
            total = 0
            for h in self.world.land_hosts:
                if h.virus:
                    counts[h.cached_word] = counts.get(h.cached_word, 0) + 1
                    total += 1
            top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:CONFIG.LEADERBOARD_TOPK]
            if top:
                print(f"Tick {self.tick_count:5d} | Infected: {total:6d} | Top words:")
                for w, c in top:
                    print(f"  {w:<10s} {c:6d}")

        actors = [h for h in self.world.land_hosts if h.virus]
        random.shuffle(actors)

        for h in actors:
            op = random.choices(("mutate", "delete", "add"), weights=CONFIG.MUTATE_OP_WEIGHTS, k=1)[0]

            if h.virus and op == "mutate" and random.random() < CONFIG.P_MUTATE:
                i = random.randrange(0, len(h.virus))
                h.virus[i] = mutate_replace(h.virus[i])
                ensure_has_vowel(h.virus)
                h.cached_word = "".join(h.virus)

            elif h.virus and op == "delete" and random.random() < CONFIG.P_MUTATE:
                j = mutate_delete(h.virus)
                if j is not None:
                    del h.virus[j]
                    ensure_has_vowel(h.virus)
                    h.cached_word = "".join(h.virus)

            elif op == "add" and random.random() < CONFIG.P_MUTATE:
                pos, seg = mutate_add(h.virus or [])
                (h.virus or []).insert(pos, seg)
                h.virus = h.virus or [seg]
                ensure_has_vowel(h.virus)
                h.cached_word = "".join(h.virus)

            if random.random() < CONFIG.P_SPREAD:
                try_spread(self.world, h)

        self.tick_count += 1

# ---------------------------
# RENDERING
# ---------------------------
class Renderer:
    def __init__(self, root: tk.Tk, world: 'World'):
        self.world = world
        self.root = root
        self.canvas = tk.Canvas(root, width=CONFIG.CANVAS_W, height=CONFIG.CANVAS_H, bg="#101010", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.font_cache: Dict[int, tkfont.Font] = {}
        self.canvas.bind("<Configure>", self._on_resize)
        self.cell_w = max(1, CONFIG.CANVAS_W // max(1, world.width))
        self.cell_h = max(1, CONFIG.CANVAS_H // max(1, world.height))

    def _on_resize(self, ev):
        self.cell_w = max(1, ev.width // max(1, self.world.width))
        self.cell_h = max(1, ev.height // max(1, self.world.height))

    def font_for_cell(self) -> tkfont.Font:
        px = max(CONFIG.MIN_FONT_PX, min(CONFIG.MAX_FONT_PX, int(min(self.cell_w, self.cell_h)*0.55)))
        f = self.font_cache.get(px)
        if f is None:
            f = tkfont.Font(family="Menlo" if sys.platform == "darwin" else "DejaVu Sans Mono", size=px, weight="bold")
            self.font_cache[px] = f
        return f

    def draw(self):
        W, H = self.world.width, self.world.height
        cw, ch = self.cell_w, self.cell_h
        self.canvas.delete("all")
        font = self.font_for_cell()

        for y in range(H):
            for x in range(W):
                h = self.world.host_at(x, y)
                if h is None:
                    continue
                x0, y0 = x*cw, y*ch
                x1, y1 = x0+cw, y0+ch
                rgb = word_to_color_cached(h.cached_word) if h.virus else (30, 30, 30)
                fill = rgb_hex(rgb)
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=fill, fill=fill)
                if h.virus:
                    self.canvas.create_text((x0+x1)//2, (y0+y1)//2, text=h.cached_word, font=font,
                                            fill=text_color_for_bg(rgb))

        if CONFIG.DRAW_GRID_LINES:
            line_color = "#000000"
            for y in range(H):
                for x in range(W):
                    h = self.world.host_at(x, y)
                    if h is None or not h.virus:
                        continue
                    r = self.world.host_at(x+1, y)
                    if r is not None and r.cached_word != h.cached_word:
                        X = (x+1)*cw
                        self.canvas.create_line(X, y*ch, X, (y+1)*ch, fill=line_color)
                    b = self.world.host_at(x, y+1)
                    if b is not None and b.cached_word != h.cached_word:
                        Y = (y+1)*ch
                        self.canvas.create_line(x*cw, Y, (x+1)*cw, Y, fill=line_color)

# ---------------------------
# APP
# ---------------------------
class App:
    def __init__(self):
        mask = generate_procedural_mask(CONFIG.GRID_W, CONFIG.GRID_H, CONFIG.LAND_PROB_INIT, CONFIG.ISLAND_BIAS, CONFIG.SMOOTH_STEPS)
        self.world = World(mask)
        self.sim = Simulation(self.world)

        self.root = tk.Tk()
        self.root.title("Language‑Virus Simulator")
        self.renderer = Renderer(self.root, self.world)

        self.root.bind("<KeyPress-q>", lambda e: self.root.destroy())
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<KeyPress-r>", lambda e: self.sim.reseed())
        self.root.bind("<KeyPress-n>", lambda e: self.regen_world())

        self._loop()

    def regen_world(self):
        mask = generate_procedural_mask(CONFIG.GRID_W, CONFIG.GRID_H, CONFIG.LAND_PROB_INIT, CONFIG.ISLAND_BIAS, CONFIG.SMOOTH_STEPS)
        self.world = World(mask)
        self.sim = Simulation(self.world)
        self.renderer.world = self.world

    def _loop(self):
        self.sim.step()
        self.renderer.draw()
        self.root.after(33, self._loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    random.seed()
    App().run()
