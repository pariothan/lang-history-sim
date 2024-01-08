import tkinter as tk
import random
from PIL import Image


class Host:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = random.randint(1, 1)
        self.prev_value = self.value
        self.neighbors = []


def generate_map_from_png(file_path):
    img = Image.open(file_path).convert("L")
    width, height = img.size
    pixels = list(img.getdata())
    threshold = 128
    hosts = [
        Host(x, y)
        for y in range(height)
        for x in range(width)
        if pixels[y * width + x] < threshold
    ]
    host_dict = {(host.x, host.y): host for host in hosts}
    for host in hosts:
        neighbor_positions = [
            (host.x + dx, host.y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
        ]
        host.neighbors = [
            host_dict[pos] for pos in neighbor_positions if pos in host_dict
        ]
    return hosts


def update_hosts(hosts):
    for host in hosts:
        neighbors_prev_values_avg = (
            sum(neighbor.prev_value for neighbor in host.neighbors)
            / len(host.neighbors)
            if host.neighbors
            else 0
        )
        new_mean = (host.prev_value + host.prev_value + neighbors_prev_values_avg) / 3

        host.value = max(1, min(int(random.gauss(new_mean, 15)), 100))
        host.prev_value = host.value


def draw_hosts(canvas, hosts):
    canvas.delete("all")
    for host in hosts:
        x, y = host.x * 10, host.y * 10  # Scale positions for better visibility
        gray_value = 255 - int(
            host.value * 2.55
        )  # Scale the host value to the range 0-255
        color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"  # Convert to hexadecimal
        canvas.create_rectangle(
            x - 5, y - 5, x + 5, y + 5, fill=color, outline=""
        )  # Draw a square with the specified color


tick_count = 0  # Add this line to initialize a tick counter


def tick():
    global tick_count  # Existing line
    tick_count += 1  # Existing line
    print(f"Ticks passed: {tick_count}")  # Existing line
    update_hosts(hosts)
    draw_hosts(canvas, hosts)

    # New lines to calculate and print the average value of all hosts
    total_value = sum(host.value for host in hosts)
    average_value = total_value / len(hosts) if hosts else 0
    print(f"Average value of all hosts: {average_value}")

    root.after(1, tick)  # Existing line


hosts = generate_map_from_png("/Users/sam/Desktop/world.png")

root = tk.Tk()
canvas = tk.Canvas(root, width=1000, height=1000)  # Adjust canvas size as needed
canvas.pack()
tick()  # Start simulation

root.mainloop()
