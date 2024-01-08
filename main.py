import tkinter as tk
import random
from PIL import Image


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


H_SHAPE = generate_map_from_png("world.png")


def feature_distance(phoneme1, phoneme2):
    """Compute the 'distance' between two phonemes based on binary features."""
    distance = 0
    for feature, value in phoneme1.items():
        if phoneme2[feature] == "0" or value == "0":
            distance += 2
        elif phoneme2[feature] != value:
            distance += 1
    return distance


def syllabic_count(word):
    """Count the number of +syllabic phonemes in a word."""
    return sum(1 for char in word if phonemes[char].get("syllabic") == "+")


phonemes = dict()
phonemes["i"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["y"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "+",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["j"] = {
    "syllabic": "-",
    "consonantal": "-",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["u"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "+",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["ʊ"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "-",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["o"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "-",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "+",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["ɔ"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "-",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "+",
    "tense": "-",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["e"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["ɑ"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "-",
    "back": "+",
    "low": "+",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["æ"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "-",
    "back": "-",
    "low": "+",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "-",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["ɪ"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "-",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["w"] = {
    "syllabic": "-",
    "consonantal": "-",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "+",
    "tense": "-",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["r"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["l"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "+",
}
phonemes["p"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["b"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["t"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["d"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["θ"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["ð"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["n"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "-",
    "nasal": "+",
    "strident": "-",
    "lateral": "-",
}
phonemes["s"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["z"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["ʃ"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["č"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["ʒ"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["k"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["x"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["χ"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["g"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["h"] = {
    "syllabic": "-",
    "consonantal": "-",
    "high": "-",
    "back": "-",
    "low": "+",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}


def readFeatures(phoneme):
    return set(phonemes[phoneme])


class Virus:
    def __init__(self, word):
        self.word = [char for char in word if char in phonemes]

    def mutate(self):
        operation = random.choice(["mutate", "delete", "add"])
        idx = random.randint(0, len(self.word) - 1)

        if operation == "mutate":
            char = self.word[idx]
            char_features = phonemes[char]

            # Calculate similarity of features for all phonemes
            distances = {
                phoneme: feature_distance(char_features, phonemes[phoneme])
                for phoneme in phonemes
            }

            # Convert distances to probabilities (inverse)
            min_distance = min(distances.values())
            max_distance = max(distances.values())
            probabilities = [
                (max_distance + 1 - distances[phoneme]) for phoneme in phonemes
            ]

            total_prob = sum(probabilities)
            probabilities = [p / total_prob for p in probabilities]

            # Choose replacement based on similarity probabilities
            replacement = random.choices(list(phonemes.keys()), probabilities)[0]
            self.word[idx] = replacement

        elif operation == "delete" and len(self.word) > 1:
            syllabics = syllabic_count(self.word)

            # Construct deletion probabilities
            probabilities = []
            for char in self.word:
                if phonemes[char].get("syllabic") == "+" and syllabics == 1:
                    # If the char is +syllabic and it's the only one, heavily disfavor its deletion
                    probabilities.append(0.01)  # Almost no chance to delete
                else:
                    probabilities.append(1)

            # Normalize probabilities
            total_prob = sum(probabilities)
            probabilities = [p / total_prob for p in probabilities]

            # Select a character for deletion based on probabilities
            char_to_delete = random.choices(self.word, probabilities)[0]
            self.word.remove(char_to_delete)

        elif operation == "add" and len(self.word) < 5:
            sweet_spot_distance = 2
            distances = {
                phoneme: abs(
                    feature_distance(phonemes[phoneme], phonemes[self.word[idx]])
                    - sweet_spot_distance
                )
                for phoneme in phonemes
            }

            # Convert distances to probabilities (inverse, so that lower distances have higher probabilities)
            min_distance = min(distances.values())
            max_distance = max(distances.values())
            probabilities = [
                (max_distance + 1 - distances[phoneme]) for phoneme in phonemes
            ]

            total_prob = sum(probabilities)
            probabilities = [p / total_prob for p in probabilities]

            new_char = random.choices(list(phonemes.keys()), probabilities)[0]
            self.word.insert(idx, new_char)


class Host:
    def __init__(self):
        self.virus = None

    def infect(self, virus):
        self.virus = Virus("".join(virus.word))


class Simulation:
    def __init__(self):
        self.grid_size = len(H_SHAPE)
        self.virus_counts = {}
        self.hosts = [
            [Host() if H_SHAPE[i][j] == 1 else None for j in range(self.grid_size)]
            for i in range(self.grid_size)
        ]
        valid_hosts_coords = [
            (i, j)
            for i in range(self.grid_size)
            for j in range(self.grid_size)
            if self.hosts[i][j]
        ]

        if valid_hosts_coords:
            i, j = random.choice(valid_hosts_coords)
            self.hosts[i][j].infect(Virus("mɪnjyen"))

    def update_virus_counts(self):
        self.virus_counts = {}
        for row in self.hosts:
            for host in row:
                if host and host.virus:
                    virus_word = "".join(host.virus.word)
                    self.virus_counts[virus_word] = (
                        self.virus_counts.get(virus_word, 0) + 1
                    )

    def print_leaderboard(self):
        sorted_viruses = sorted(
            self.virus_counts.items(), key=lambda x: x[1], reverse=True
        )
        print("Top 10 Viruses:")
        for i, (virus_word, count) in enumerate(sorted_viruses[:10]):
            print(f"{i+1}. {virus_word}: {count} hosts")

    def step(self):
        self.update_virus_counts()
        self.print_leaderboard()
        for row in self.hosts:
            for host in row:
                if host and host.virus:
                    if random.random() < 0.001:
                        self.mutate_virus(host)
                    if random.random() < 0.1:
                        self.spread_virus(host)

    def mutate_virus(self, host):
        host.virus.mutate()

    def spread_virus(self, source_host):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.hosts[i][j] == source_host:
                    source_i, source_j = i, j
                    break

        infected_coords = [
            (i, j)
            for i in range(self.grid_size)
            for j in range(self.grid_size)
            if self.hosts[i][j] and self.hosts[i][j].virus
        ]
        potential_targets = [
            (i, j)
            for i in range(self.grid_size)
            for j in range(self.grid_size)
            if self.hosts[i][j]
        ]
        random.shuffle(potential_targets)

        for target_i, target_j in potential_targets:
            di, dj = target_i - source_i, target_j - source_j
            num_blanks = abs(di) + abs(dj) - 1
            infection_chance = (1 / 3) ** num_blanks
            if random.random() < infection_chance:
                self.hosts[target_i][target_j].infect(
                    self.hosts[source_i][source_j].virus
                )
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
        self.canvas.delete("all")
        rows = len(self.simulation.hosts)
        columns = len(self.simulation.hosts[0]) if rows > 0 else 0
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        width = canvas_width / columns
        height = canvas_height / rows
        font_size = int(min(width, height) / 2)
        font_tuple = ("Arial", font_size)

        for i, row in enumerate(self.simulation.hosts):
            for j, host in enumerate(row):
                if host:
                    x, y = width * j, height * i
                    word = "".join(host.virus.word) if host.virus else ""
                    self.canvas.create_text(
                        x + (width // 2), y + (height // 2), text=word, font=font_tuple
                    )

                    if j < len(row) - 1 and (
                        not self.simulation.hosts[i][j + 1]
                        or (
                            self.simulation.hosts[i][j + 1].virus
                            and "".join(self.simulation.hosts[i][j + 1].virus.word)
                            != word
                        )
                    ):
                        self.canvas.create_line(
                            x + width, y, x + width, y + height, fill="black"
                        )

                    if i < len(self.simulation.hosts) - 1 and (
                        not self.simulation.hosts[i + 1][j]
                        or (
                            self.simulation.hosts[i + 1][j].virus
                            and "".join(self.simulation.hosts[i + 1][j].virus.word)
                            != word
                        )
                    ):
                        self.canvas.create_line(
                            x, y + height, x + width, y + height, fill="black"
                        )


root = tk.Tk()
app = App(root)
root.mainloop()
