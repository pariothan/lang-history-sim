import tkinter as tk
import random
from PIL import Image
import math
from functools import lru_cache

def generate_map_from_png(file_path):
    img = Image.open(file_path).convert("L")
    width, height = img.size
    pixels = list(img.getdata())
    threshold = 128
    H_SHAPE = [
        [1 if pixel < threshold else 0 for pixel in pixels[i * width : (i + 1) * width]]
        for i in range(height)
    ]
    return H_SHAPE

H_SHAPE = generate_map_from_png("lang-history-sim/fantasyworld.png")

def feature_distance(phoneme1, phoneme2):
    distance = 0
    for feature, value in phoneme1.items():
        if phoneme2[feature] == "0" or value == "0":
            distance += 2
        elif phoneme2[feature] != value:
            distance += 1
    return distance

def syllabic_count(word):
    return sum(1 for char in word if phonemes[char].get("syllabic") == "+")

# --------------------- PHONEME FEATURE TABLE ---------------------
phonemes = dict()
phonemes["i"] = {"syllabic":"+","consonantal":"-","high":"+","back":"-","low":"-","anterior":"-","coronal":"-","round":"-","tense":"+","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["y"] = {"syllabic":"+","consonantal":"-","high":"+","back":"-","low":"-","anterior":"-","coronal":"-","round":"+","tense":"+","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["j"] = {"syllabic":"-","consonantal":"-","high":"+","back":"-","low":"-","anterior":"-","coronal":"-","round":"-","tense":"+","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["u"] = {"syllabic":"+","consonantal":"-","high":"+","back":"+","low":"-","anterior":"-","coronal":"-","round":"+","tense":"+","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["ʊ"] = {"syllabic":"+","consonantal":"-","high":"+","back":"+","low":"-","anterior":"-","coronal":"-","round":"-","tense":"-","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["o"] = {"syllabic":"+","consonantal":"-","high":"-","back":"+","low":"-","anterior":"-","coronal":"-","round":"+","tense":"+","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["ɔ"] = {"syllabic":"+","consonantal":"-","high":"-","back":"+","low":"-","anterior":"-","coronal":"-","round":"+","tense":"-","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["e"] = {"syllabic":"+","consonantal":"-","high":"-","back":"-","low":"-","anterior":"-","coronal":"-","round":"-","tense":"+","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["ɑ"] = {"syllabic":"+","consonantal":"-","high":"-","back":"+","low":"+","anterior":"-","coronal":"-","round":"-","tense":"+","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["æ"] = {"syllabic":"+","consonantal":"-","high":"-","back":"-","low":"+","anterior":"-","coronal":"-","round":"-","tense":"-","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["ɪ"] = {"syllabic":"+","consonantal":"-","high":"+","back":"-","low":"-","anterior":"-","coronal":"-","round":"-","tense":"-","voice":"0","continuant":"0","nasal":"0","strident":"0","lateral":"0"}
phonemes["w"] = {"syllabic":"-","consonantal":"-","high":"+","back":"+","low":"-","anterior":"-","coronal":"-","round":"+","tense":"-","voice":"0","continuant":"+","nasal":"-","strident":"-","lateral":"-"}
phonemes["r"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"-","coronal":"+","round":"0","tense":"0","voice":"+","continuant":"+","nasal":"-","strident":"-","lateral":"-"}
phonemes["l"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"+","continuant":"+","nasal":"-","strident":"-","lateral":"+"}
phonemes["p"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"-","round":"0","tense":"0","voice":"-","continuant":"-","nasal":"-","strident":"-","lateral":"-"}
phonemes["b"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"-","round":"0","tense":"0","voice":"+","continuant":"-","nasal":"-","strident":"-","lateral":"-"}
phonemes["t"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"-","continuant":"-","nasal":"-","strident":"-","lateral":"-"}
phonemes["d"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"+","continuant":"-","nasal":"-","strident":"-","lateral":"-"}
phonemes["θ"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"-","continuant":"+","nasal":"-","strident":"-","lateral":"-"}
phonemes["ð"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"+","continuant":"+","nasal":"-","strident":"-","lateral":"-"}
phonemes["n"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"+","continuant":"-","nasal":"+","strident":"-","lateral":"-"}
phonemes["s"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"-","continuant":"+","nasal":"-","strident":"+","lateral":"-"}
phonemes["z"] = {"syllabic":"-","consonantal":"+","high":"-","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"+","continuant":"+","nasal":"-","strident":"+","lateral":"-"}
phonemes["ʃ"] = {"syllabic":"-","consonantal":"+","high":"+","back":"-","low":"-","anterior":"-","coronal":"+","round":"0","tense":"0","voice":"-","continuant":"+","nasal":"-","strident":"+","lateral":"-"}
phonemes["č"] = {"syllabic":"-","consonantal":"+","high":"+","back":"-","low":"-","anterior":"+","coronal":"+","round":"0","tense":"0","voice":"-","continuant":"+","nasal":"-","strident":"+","lateral":"-"}
phonemes["ʒ"] = {"syllabic":"-","consonantal":"+","high":"+","back":"-","low":"-","anterior":"-","coronal":"+","round":"0","tense":"0","voice":"+","continuant":"+","nasal":"-","strident":"+","lateral":"-"}
phonemes["k"] = {"syllabic":"-","consonantal":"+","high":"+","back":"+","low":"-","anterior":"-","coronal":"-","round":"0","tense":"0","voice":"-","continuant":"-","nasal":"-","strident":"-","lateral":"-"}
phonemes["x"] = {"syllabic":"-","consonantal":"+","high":"+","back":"+","low":"-","anterior":"-","coronal":"-","round":"0","tense":"0","voice":"-","continuant":"+","nasal":"-","strident":"-","lateral":"-"}
phonemes["χ"] = {"syllabic":"-","consonantal":"+","high":"+","back":"+","low":"-","anterior":"-","coronal":"-","round":"0","tense":"0","voice":"+","continuant":"+","nasal":"-","strident":"-","lateral":"-"}
phonemes["g"] = {"syllabic":"-","consonantal":"+","high":"+","back":"+","low":"-","anterior":"-","coronal":"-","round":"0","tense":"0","voice":"-","continuant":"-","nasal":"-","strident":"-","lateral":"-"}
phonemes["h"] = {"syllabic":"-","consonantal":"-","high":"-","back":"-","low":"+","anterior":"-","coronal":"-","round":"0","tense":"0","voice":"-","continuant":"+","nasal":"-","strident":"-","lateral":"-"}
# -----------------------------------------------------------------

FEATURES = ("syllabic","consonantal","high","back","low","anterior","coronal","round","tense","voice","continuant","nasal","strident","lateral")

def _feat_to_num(v: str) -> int:
    return 1 if v == "+" else (-1 if v == "-" else 0)

# ---------- Precompute per-phoneme numeric vector and color projections ----------
W_R = ( 0.82,-0.41, 0.33, 0.27,-0.58, 0.19, 0.44,-0.21, 0.55, 0.17, 0.36,-0.49, 0.23,-0.12)
W_G = (-0.37, 0.79,-0.28,-0.55, 0.14, 0.52, 0.18, 0.33,-0.24, 0.47,-0.51, 0.12, 0.40, 0.09)
W_B = ( 0.11, 0.28, 0.76,-0.36, 0.49,-0.27, 0.15, 0.61, 0.07,-0.58, 0.22, 0.35,-0.33, 0.41)

PHONEME_KEYS = tuple(phonemes.keys())
NUM_VEC = {p: tuple(_feat_to_num(phonemes[p][k]) for k in FEATURES) for p in PHONEME_KEYS}
PHONEME_COLOR = {
    p: (
        sum(v*w for v, w in zip(NUM_VEC[p], W_R)),
        sum(v*w for v, w in zip(NUM_VEC[p], W_G)),
        sum(v*w for v, w in zip(NUM_VEC[p], W_B)),
    )
    for p in PHONEME_KEYS
}

# ---------- Precompute distance matrix and weight tables ----------
DIST = {a: {b: feature_distance(phonemes[a], phonemes[b]) for b in PHONEME_KEYS} for a in PHONEME_KEYS}
MUTATE_WEIGHTS = {}
for a in PHONEME_KEYS:
    row = DIST[a]
    m = max(row.values())
    MUTATE_WEIGHTS[a] = [(m + 1 - row[b]) for b in PHONEME_KEYS]

SWEET = 2
ADD_WEIGHTS = {}
for a in PHONEME_KEYS:
    vals = [abs(DIST[a][b] - SWEET) for b in PHONEME_KEYS]
    m = max(vals)
    ADD_WEIGHTS[a] = [(m + 1 - v) for v in vals]

def _to_byte(x):
    y = math.tanh(x)
    z = int((y * 0.5 + 0.5) * 200)
    v = 35 + z
    if v < 35: v = 35
    elif v > 235: v = 235
    return v

def _rgb_to_hex(r,g,b): return f"#{r:02x}{g:02x}{b:02x}"

@lru_cache(maxsize=8192)
def word_to_color(word: str):
    if not word:
        return ("#eeeeee", "#222222")
    chars = [c for c in word if c in phonemes]
    if not chars:
        return ("#dddddd", "#222222")
    sr = sg = sb = 0.0
    for ch in chars:
        r,g,b = PHONEME_COLOR[ch]
        sr += r; sg += g; sb += b
    n = len(chars)
    r = _to_byte(sr / n); g = _to_byte(sg / n); b = _to_byte(sb / n)
    luminance = 0.2126*r + 0.7152*g + 0.0722*b
    text = "#000000" if luminance > 150 else "#ffffff"
    return (_rgb_to_hex(r,g,b), text)

def readFeatures(phoneme):
    return set(phonemes[phoneme])

class Virus:
    def __init__(self, word):
        self.word = [char for char in word if char in phonemes]

    def mutate(self):
        if not self.word:
            return
        op = random.choice(["mutate", "delete", "add"])
        idx = random.randint(0, len(self.word) - 1)
        if op == "mutate":
            base = self.word[idx]
            replacement = random.choices(PHONEME_KEYS, weights=MUTATE_WEIGHTS[base])[0]
            self.word[idx] = replacement
        elif op == "delete" and len(self.word) > 1:
            syllabics = syllabic_count(self.word)
            probs = []
            _phonemes = phonemes
            for ch in self.word:
                if _phonemes[ch].get("syllabic") == "+" and syllabics == 1:
                    probs.append(0.01)
                else:
                    probs.append(1.0)
            char_to_delete = random.choices(self.word, weights=probs)[0]
            self.word.remove(char_to_delete)
        elif op == "add" and len(self.word) < 5:
            base = self.word[idx]
            new_char = random.choices(PHONEME_KEYS, weights=ADD_WEIGHTS[base])[0]
            self.word.insert(idx, new_char)

class Host:
    def __init__(self):
        self.virus = None
        self.cached_word = ""  # keep a cached string for speed

    def refresh_cached_word(self):
        self.cached_word = "".join(self.virus.word) if (self.virus and self.virus.word) else ""

    def infect(self, virus):
        # clone into new Virus (same as before), then refresh cache
        self.virus = Virus("".join(virus.word))
        self.refresh_cached_word()

class Simulation:
    def __init__(self):
        self.grid_size = len(H_SHAPE)
        self.virus_counts = {}
        gs = self.grid_size
        shape = H_SHAPE
        self.hosts = [
            [Host() if shape[i][j] == 1 else None for j in range(gs)]
            for i in range(gs)
        ]

        # precompute valid coords & a coord map for O(1) lookup of a host's position
        self.valid_coords = [(i, j) for i in range(gs) for j in range(gs) if self.hosts[i][j]]
        self.coord_of = {self.hosts[i][j]: (i, j) for (i, j) in self.valid_coords}

        # a reusable index array we can shuffle (avoid re-allocating big lists)
        self._perm_indices = list(range(len(self.valid_coords)))

        if self.valid_coords:
            i, j = random.choice(self.valid_coords)
            self.hosts[i][j].infect(Virus("kit"))

    def update_virus_counts(self):
        vc = {}
        for row in self.hosts:
            for host in row:
                if host and host.virus:
                    w = host.cached_word  # use cache
                    vc[w] = vc.get(w, 0) + 1
        self.virus_counts = vc

    def print_leaderboard(self):
        sorted_viruses = sorted(self.virus_counts.items(), key=lambda x: x[1], reverse=True)
        print("Top 10 Viruses:")
        for i, (virus_word, count) in enumerate(sorted_viruses[:10]):
            print(f"{i+1}. {virus_word}: {count} hosts")

    def step(self):
        self.update_virus_counts()
        self.print_leaderboard()

        hosts = self.hosts
        # snapshot of current actors to prevent double-acting
        acting_hosts = [h for row in hosts for h in row if (h and h.virus)]
        random.shuffle(acting_hosts)

        for host in acting_hosts:
            if random.random() < 0.003:
                self.mutate_virus(host)   # keeps cached string in sync
            if random.random() < 0.1:
                self.spread_virus(host)

    def mutate_virus(self, host):
        host.virus.mutate()
        host.refresh_cached_word()  # keep cache updated

    def spread_virus(self, source_host):
        si, sj = self.coord_of[source_host]  # O(1) lookup
        hosts = self.hosts

        # shuffle a reusable permutation of indices to iterate targets without replacement
        perm = self._perm_indices[:]        # shallow copy of small ints list
        random.shuffle(perm)

        src_virus = hosts[si][sj].virus
        for idx in perm:
            ti, tj = self.valid_coords[idx]
            # skip if target is the source tile
            if ti == si and tj == sj:
                continue
            di, dj = ti - si, tj - sj
            num_blanks = abs(di) + abs(dj) - 1
            infection_chance = (1 / 3) ** num_blanks
            if random.random() < infection_chance:
                hosts[ti][tj].infect(src_virus)  # Host.infect updates cache
                return

class App:
    def __init__(self, master):
        self.simulation = Simulation()
        self.canvas = tk.Canvas(master, width=3000, height=1500)
        self.canvas.pack()
        self.update()

    def update(self):
        self.simulation.step()
        self.draw()
        self.canvas.after(1, self.update)

    def draw(self):
        canvas = self.canvas
        canvas.delete("all")
        hosts = self.simulation.hosts
        rows = len(hosts)
        columns = len(hosts[0]) if rows > 0 else 0
        if rows == 0 or columns == 0:
            return

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        width = cw / columns
        height = ch / rows
        font_size = max(6, int(min(width, height) / 2))
        font_tuple = ("Arial", font_size)

        for i, row in enumerate(hosts):
            y = height * i
            # read cached words (no joins here)
            row_words = [h.cached_word if h else "" for h in row]
            for j, host in enumerate(row):
                if host:
                    x = width * j
                    word = row_words[j]
                    fill, text_color = word_to_color(word)

                    canvas.create_rectangle(x, y, x + width, y + height, fill=fill, outline="")
                    canvas.create_text(x + (width / 2), y + (height / 2),
                                       text=word, font=font_tuple, fill=text_color)

                    if j < len(row) - 1:
                        right_word = row_words[j + 1]
                        if right_word != word:
                            canvas.create_line(x + width, y, x + width, y + height, fill="#000000")

                    if i < rows - 1:
                        below = hosts[i + 1][j]
                        below_word = below.cached_word if (below and below.virus) else ""
                        if below_word != word:
                            canvas.create_line(x, y + height, x + width, y + height, fill="#000000")

root = tk.Tk()
app = App(root)
root.mainloop()
