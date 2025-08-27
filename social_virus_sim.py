import tkinter as tk
import random
from PIL import Image

SCALE = 10          # pixel size per cell (square side length)
STDDEV = 8          # noise stddev for updates (per channel)
SELF_WEIGHT = 2.0   # weight for self vs. neighbors in the mean (2 = self counted twice)

class Host:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # three-channel value in [1..100]
        self.value = tuple(random.randint(1, 100) for _ in range(3))
        self.prev_value = self.value
        self.neighbors = []

def generate_map_from_png(file_path, threshold=128):
    img = Image.open(file_path).convert("L")
    width, height = img.size
    pixels = list(img.getdata())

    hosts = [
        Host(x, y)
        for y in range(height)
        for x in range(width)
        if pixels[y * width + x] < threshold
    ]
    host_dict = {(h.x, h.y): h for h in hosts}

    for h in hosts:
        nbr_pos = [(h.x + 1, h.y), (h.x - 1, h.y), (h.x, h.y + 1), (h.x, h.y - 1)]
        h.neighbors = [host_dict[p] for p in nbr_pos if p in host_dict]

    return hosts, width, height

def _clamp100(n):
    return 1 if n < 1 else 100 if n > 100 else int(n)

def _avg_triplets(triplets):
    # average a list of (r,g,b) tuples; returns floats
    if not triplets:
        return (0.0, 0.0, 0.0)
    s0 = sum(t[0] for t in triplets)
    s1 = sum(t[1] for t in triplets)
    s2 = sum(t[2] for t in triplets)
    n = float(len(triplets))
    return (s0 / n, s1 / n, s2 / n)

def update_hosts(hosts):
    # compute next value from: mean(self * SELF_WEIGHT + neighbors)
    for h in hosts:
        nb_mean = _avg_triplets([n.prev_value for n in h.neighbors]) if h.neighbors else (0.0, 0.0, 0.0)
        # weighted mean: (self counted SELF_WEIGHT times) and neighbors mean once
        new_mean = tuple(
            (h.prev_value[c] * SELF_WEIGHT + nb_mean[c]) / (SELF_WEIGHT + 1.0)
            for c in range(3)
        )
        # add Gaussian noise and clamp to 1..100
        h.value = tuple(_clamp100(random.gauss(new_mean[c], STDDEV)) for c in range(3))

    # commit step
    for h in hosts:
        h.prev_value = h.value

def draw_hosts(canvas, hosts, grid_w, grid_h):
    canvas.delete("all")
    # optional: center/scale to canvas size
    cw = canvas.winfo_width()
    ch = canvas.winfo_height()
    cell_w = max(1, cw // max(1, grid_w))
    cell_h = max(1, ch // max(1, grid_h))
    side = min(cell_w, cell_h)

    for h in hosts:
        x = h.x * side
        y = h.y * side
        # map [1..100] → [0..255]
        r = int(h.value[0] * 2.55)
        g = int(h.value[1] * 2.55)
        b = int(h.value[2] * 2.55)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_rectangle(x, y, x + side, y + side, fill=color, outline="")

tick_count = 0

def tick():
    global tick_count
    tick_count += 1
    print(f"Ticks passed: {tick_count}")

    update_hosts(hosts)
    draw_hosts(canvas, hosts, GRID_W, GRID_H)

    # diagnostics
    if hosts:
        avg_r = sum(h.value[0] for h in hosts) / len(hosts)
        avg_g = sum(h.value[1] for h in hosts) / len(hosts)
        avg_b = sum(h.value[2] for h in hosts) / len(hosts)
        print(f"Average value (R,G,B): {avg_r:.2f}, {avg_g:.2f}, {avg_b:.2f}")

    root.after(16, tick)  # ~60 FPS

# --- run ---
hosts, GRID_W, GRID_H = generate_map_from_png(
    "/Users/sam/documents/code/lang-history-sim/afroeurasia.png",
    threshold=128
)

root = tk.Tk()
root.title("Colored Host Grid (triple values)")
# size roughly matched to map
canvas = tk.Canvas(root, width=min(1200, GRID_W * SCALE), height=min(800, GRID_H * SCALE))
canvas.pack(fill="both", expand=True)

# redraw properly on resize
def _on_resize(_evt):
    draw_hosts(canvas, hosts, GRID_W, GRID_H)
canvas.bind("<Configure>", _on_resize)

tick()
root.mainloop()
