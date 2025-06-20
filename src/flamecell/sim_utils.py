import numpy as np
import matplotlib.pyplot as plt
import requests
from rules import * 

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = np.full((height, width), "EMPTY", dtype=object)
        self.health = np.zeros((height, width), dtype=int)

    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.state[y, x], self.health[y, x]
        return None, None

    def set_cell(self, x, y, state, health):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.state[y, x] = state
            self.health[y, x] = health

class RuleSet:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def apply(self, x, y, state_matrix, health_matrix, neighbors, **kwargs):
        new_state = state_matrix[y, x]
        new_health = health_matrix[y, x]
        for rule in self.rules:
            new_state, new_health = rule(x, y, new_state, new_health, neighbors, **kwargs)
        return new_state, new_health

class Simulation:
    def __init__(self, grid, ruleset):
        self.grid = grid
        self.ruleset = ruleset
        self.step_count = 0
        self.max_steps = 1000
        self.ignite_time = np.zeros_like(grid.state, dtype=np.int32)

    def step(self, prob=0.2, humidity=0.4, wind=np.array([0,0])):
        # Seperate the loop for njit optimization
        new_state = self.grid.state.copy()
        new_health = self.grid.health.copy()
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if new_state[y, x] == "FIRE":
                    self.ignite_time[y, x] = self.step_count
                # calculate neighbors
                neighbors = []
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height:
                            neighbor_state = self.grid.state[ny, nx]
                            neighbors.append((neighbor_state, dx, dy))
                # apply all the rules
                state, health = self.ruleset.apply(x, y, self.grid.state, self.grid.health, neighbors, prob=prob, humidity=humidity, wind=wind)
                new_state[y, x] = state
                new_health[y, x] = health
        # Apply new state
        self.grid.state = new_state
        self.grid.health = new_health
        self.step_count += 1



# color map for visualization [0.0, 1.0]
color_map = {
    "FIRE": (1.0, 0.5, 0),
    "TREE": (0.1, 0.45, 0.1),
    "GRASS": (0.6, 1.0, 0.6),
    "WATER": (0.0, 0.0, 1.0),
    "ASH": (0.0, 0.0, 0.0),
    "EMPTY": (1.0, 1.0, 1.0),
}

def raster_to_cell(pixel_value):
    if pixel_value == 5 or pixel_value == 4:
        return "WATER"
    elif pixel_value == 31:
        return "TREE"
    elif pixel_value == 32 or pixel_value == 22:
        return "GRASS"
    else:
        return "EMPTY"

def raster_to_grid(data):
    height, width = data.shape
    grid = Grid(width, height)
    for y in range(height):
        for x in range(width):
            state = raster_to_cell(data[y,x])
            grid.state[y, x] = state
            if state == "TREE":
                grid.health[y, x] = 10
            elif state =="GRASS":
                grid.health[y, x] = 4
    return grid

def grid_to_img(grid):
    img = np.zeros((grid.height, grid.width, 3), dtype=np.uint8)
    for y in range(grid.height):
        for x in range(grid.width):
            img[y, x, 0] = color_map[grid.state[y][x]][0] * 255
            img[y, x, 1] = color_map[grid.state[y][x]][1] * 255
            img[y, x, 2] = color_map[grid.state[y][x]][2] * 255
    return img 

def plot_grid(grid):
    img = np.zeros((grid.height, grid.width, 3))
    for y in range(grid.height):
        for x in range(grid.width):
            img[y, x] = color_map[grid.state[y][x]]

    fig, ax = plt.subplots()
    ax.imshow(img, interpolation='none')
    ax.set_xticks([])
    ax.set_yticks([])
    return fig

def plot_risk_map(sim):
    base = np.zeros((sim.grid.height, sim.grid.width, 3))
    for y in range(sim.grid.height):
        for x in range(sim.grid.width):
            base[y, x] = color_map[sim.grid.state[y][x]]

    fig, ax = plt.subplots()
    ax.imshow(base, interpolation='none')

    # Overlay risk heatmap in red scale with transparency
    heat = ax.imshow(sim.ignite_time, cmap='hot', alpha=0.4, interpolation='none')

    ax.set_xticks([])
    ax.set_yticks([])
    return fig


def get_current_wind(lat, lon):
    """
    Get current wind speed and direction using Open-Meteo API.
    Returns:
        wind_speed (float): in m/s
        wind_direction (float): in degrees (0° is North, 90° is East)
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=wind_speed_10m,wind_direction_10m"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        wind_speed = data['current']['wind_speed_10m']
        wind_direction = data['current']['wind_direction_10m']
        return wind_speed, wind_direction
    except Exception as e:
        return str(e), None

