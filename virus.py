import tkinter as tk
import random


def generate_random_map(width, height, density=0.5):
    """Generate a random map with given width and height.

    Args:
    - width (int): Width of the map.
    - height (int): Height of the map.
    - density (float): Probability that a given cell contains a host (value of 1).

    Returns:
    - List[List[int]]: Randomly generated map.
    """
    return [
        [1 if random.random() < density else 0 for _ in range(width)]
        for _ in range(height)
    ]


# Define the H shape

from PIL import Image


def generate_map_from_png(file_path):
    """Generate the H_SHAPE based on a PNG image.

    Args:
        file_path (str): Path to the PNG image.

    Returns:
        List[List[int]]: Map generated from the PNG image.
    """
    # Open the image and convert it to grayscale
    img = Image.open(file_path).convert("L")

    # Ensure the image is of the desired size, say 20x20 for this example
    img = img.resize((100, 100))

    # Extract pixel data
    pixels = list(img.getdata())

    # Create H_SHAPE: 1 for black pixel, 0 otherwise
    threshold = 128  # Pixels below this are considered black
    H_SHAPE = [
        [1 if pixel < threshold else 0 for pixel in pixels[i * 100 : (i + 1) * 100]]
        for i in range(100)
    ]

    return H_SHAPE


# Use this function to get H_SHAPE
H_SHAPE = generate_map_from_png("/Users/sam/Desktop/world.png")


# Virus class to represent the RGB values
class Virus:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def mutate(self):
        def clamp(val, minimum=0, maximum=255):
            return max(minimum, min(val, maximum))

        for channel in ["r", "g", "b"]:
            if random.random() < 0.5:  # 50% chance to mutate each channel
                change = random.randint(1, 15) * random.choice(
                    [-1, 1]
                )  # change value between -5 and 5
                if channel == "r":
                    self.r = clamp(self.r + change)
                elif channel == "g":
                    self.g = clamp(self.g + change)
                elif channel == "b":
                    self.b = clamp(self.b + change)


# Host class
class Host:
    def __init__(self):
        self.virus = None

    def infect(self, virus):
        self.virus = Virus(virus.r, virus.g, virus.b)


# Simulation class
class Simulation:
    def __init__(self):
        self.grid_size = len(H_SHAPE)
        self.hosts = [
            [Host() if H_SHAPE[i][j] == 1 else None for j in range(self.grid_size)]
            for i in range(self.grid_size)
        ]
        self.hosts[56][45].infect(Virus(255, 0, 0))

    def step(self):
        if random.random() < 0.1:
            self.mutate_virus()
        if random.random() < 0.5:
            self.spread_virus()

    def mutate_virus(self):
        for row in self.hosts:
            for host in row:
                if host and host.virus:
                    host.virus.mutate()

    def spread_virus(self):
        infected_coords = [
            (i, j)
            for i in range(self.grid_size)
            for j in range(self.grid_size)
            if self.hosts[i][j] and self.hosts[i][j].virus
        ]
        if infected_coords:
            source_i, source_j = random.choice(infected_coords)

            potential_targets = [
                (i, j)
                for i in range(self.grid_size)
                for j in range(self.grid_size)
                if self.hosts[i][j] and not self.hosts[i][j].virus
            ]

            for target_i, target_j in potential_targets:
                di, dj = target_i - source_i, target_j - source_j
                num_blanks = abs(di) + abs(dj) - 1  # Number of blank spaces jumped
                infection_chance = (
                    1 / 3
                ) ** num_blanks  # Infection chance decreases exponentially
                if random.random() < infection_chance:
                    self.hosts[target_i][target_j].infect(
                        self.hosts[source_i][source_j].virus
                    )
                    return  # Stop after infecting one host


# App class for the GUI
class App:
    def __init__(self, master):
        self.simulation = Simulation()
        self.canvas = tk.Canvas(master, width=1000, height=1000)
        self.canvas.pack()
        self.update()

    def update(self):
        self.simulation.step()
        self.draw()
        self.canvas.after(1, self.update)

    def draw(self):
        self.canvas.delete("all")
        for i, row in enumerate(self.simulation.hosts):
            for j, host in enumerate(row):
                if host:
                    x, y = 10 + j * 10, 10 + i * 10  # Reducing spacing and offset
                    if host.virus:
                        color = (
                            f"#{host.virus.r:02x}{host.virus.g:02x}{host.virus.b:02x}"
                        )
                    else:
                        color = "gray"
                    self.canvas.create_oval(
                        x, y, x + 8, y + 8, fill=color
                    )  # Reducing size of host


root = tk.Tk()
app = App(root)
root.mainloop()
