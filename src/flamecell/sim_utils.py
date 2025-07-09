"""
Forest Fire Simulation Framework

This module provides classes and functions for simulating and visualizing a forest 
fireusing cellular automata. It supports raster input, dynamic rule-based evolution,
and external weather data integration.
"""

import numbers
import requests
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
import sys
sys.path.append("../flamecell/src")
from flamecell.rules import *

class Grid:
    """
    Grid represents the simulation area with state and health matrices.

    Parameters
    ----------
    width : int
        Width of the grid.
    height : int
        Height of the grid.

    Raises
    ------
    ValueError
        If width or height is not a positive integer.
    """

    def __init__(self, width, height):
        if not isinstance(width, int) or width <= 0:
            raise ValueError("Width must be a positive integer")
        if not isinstance(height, int) or height <= 0:
            raise ValueError("Height must be a positive integer")
        self.width = width
        self.height = height
        self.state = np.full((height, width), "EMPTY", dtype=object)
        self.health = np.zeros((height, width), dtype=int)

class RuleSet:
    """
    RuleSet manages and applies update rules to each cell.
    """

    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        """
        Add a transition rule.

        Parameters
        ----------
        rule : callable
            A rule function to apply to cells.
        """
        self.rules.append(rule)

    def apply(self, x, y, state_matrix, health_matrix, neighbors, **kwargs):
        """
        Apply all rules to a specific cell.

        Parameters
        ----------
        x, y : int
            Coordinates of the cell.
        state_matrix : np.ndarray
            Current state matrix.
        health_matrix : np.ndarray
            Current health matrix.
        neighbors : list of tuple
            Neighbor states and relative positions.
        kwargs : dict
            Additional parameters like wind, humidity, etc.

        Returns
        -------
        tuple
            New state and health of the cell.
        """
        new_state = state_matrix[y, x]
        new_health = health_matrix[y, x]
        for rule in self.rules:
            new_state, new_health = rule(x, y, new_state, new_health, neighbors, **kwargs)
        return new_state, new_health

class Simulation:
    """
    Manages simulation steps and grid evolution.

    Parameters
    ----------
    grid : Grid
        The simulation grid.
    ruleset : RuleSet
        The ruleset to apply during updates.
    """

    def __init__(self, grid, ruleset):
        self.grid = grid
        self.ruleset = ruleset
        self.step_count = 0
        self.max_steps = 1000
        self.ignite_time = np.zeros_like(grid.state, dtype=np.int32)

    def step(self, prob=0.2, humidity=0.4, wind=np.array([0,0]), **kwargs):
        """
        Advances the simulation by one step.

        Parameters
        ----------
        prob : float
            Base ignition probability.
        humidity : float
            Environmental humidity.
        wind : np.ndarray
            Wind vector (dx, dy).
        kwargs : dict
            Additional arguments passed to rule functions.
        """
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
                state, health = self.ruleset.apply(x, y, self.grid.state, self.grid.health, neighbors, prob=prob, humidity=humidity, wind=wind, **kwargs)
                new_state[y, x] = state
                new_health[y, x] = health
        # Apply new state
        self.grid.state = new_state
        self.grid.health = new_health
        self.step_count += 1



# color map for visualization, relative RGB values from [0.0, 1.0]
color_map = {
    "FIRE": (1.0, 0.5, 0),
    "TREE": (0.1, 0.45, 0.1),
    "GRASS": (0.6, 1.0, 0.6),
    "WATER": (0.0, 0.0, 1.0),
    "ASH": (0.0, 0.0, 0.0),
    "EMPTY": (1.0, 1.0, 1.0),
}

def raster_to_cell(pixel_value):
    """
    Convert raster pixel value to cell type.

    Parameters
    ----------
    pixel_value : int
        Raster pixel classification code.

    Returns
    -------
    str
        Corresponding cell type.

    Raises
    ------
    TypeError
        If input is not an integer.
    """
    if not isinstance(pixel_value, numbers.Integral):
        raise TypeError("Pixel Value should be non-negative integer")
    
    if pixel_value in (4, 5):
        return "WATER"
    if pixel_value == 31:
        return "TREE"
    if pixel_value in (22, 32):
        return "GRASS"
    return "EMPTY"

def raster_to_grid(data):
    """
    Convert raster data into a Grid object.

    Parameters
    ----------
    data : np.ndarray
        Raster classification matrix.

    Returns
    -------
    Grid
        Initialized simulation grid.
    """
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
    """
    Convert grid state to RGB image array.

    Parameters
    ----------
    grid : Grid
        Simulation grid.

    Returns
    -------
    np.ndarray
        RGB image array.
    """
    img = np.zeros((grid.height, grid.width, 3), dtype=np.uint8)
    for y in range(grid.height):
        for x in range(grid.width):
            r, g, b = color_map[grid.state[y][x]]
            img[y, x] = [int(r * 255), int(g * 255), int(b * 255)]
    return img

def plot_grid(grid):
    """
    Display the grid state as an image.

    Parameters
    ----------
    grid : Grid
        Simulation grid.

    Returns
    -------
    matplotlib.figure.Figure
        Figure object for visualization.
    """
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
    """
    Overlay risk heatmap based on ignition time over the current grid state.

    Parameters
    ----------
    sim : Simulation
        Simulation object.

    Returns
    -------
    matplotlib.figure.Figure
        Figure object with overlayed heatmap.
    """
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

    Parameters
    ----------
    lat, lon : float
        Latitude. Longitude.

    Returns
    -------
    tuple
        (wind speed in m/s, wind direction in degrees)
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
        return wind_speed, wind_direction, time
    except Exception as e:
        return str(e), None
        

    
def get_current_humidity(lat, lon):
    """
    Get current relative humidity using Open-Meteo API.

    Parameters
    ----------
    lat, lon : float
        Latitude. Longitude.

    Returns
    -------
    float or str
        Relative humidity (%) or error message.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=relative_humidity_2m"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        humidity = data['current']['relative_humidity_2m']
        time = data['current']['time']
        return humidity, time
    except Exception as e:
        return str(e), None
    
def get_current_temperature(lat, lon):
    """
    Get current temperature using Open-Meteo API.

    Parameters
    ----------
    lat, lon : float
        Latitude. Longitude.

    Returns
    -------
    float or str
        Temperature (°C) or error message.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data['current']['temperature_2m']
        time = data['current']['time']
        return temp, time
    except Exception as e:
        return str(e), None

def crop_and_resample(src, bounds, output_size=(128, 128)):
    """
    Crop raster to bounds and resample to specified size.

    Parameters
    ----------
    src : rasterio.DatasetReader
        Open land use map.
    bounds : dict
        Leaflet-style bounds with '_southWest' and '_northEast'.
    output_size : tuple
        Desired output shape (width, height).

    Returns
    -------
    tuple
        (resampled data, transform)
    """
    south = bounds['_southWest']['lat']
    west = bounds['_southWest']['lng']
    north = bounds['_northEast']['lat']
    east = bounds['_northEast']['lng']

    src_crs = src.crs  # Get CRS from the raster dataset
    bounds_projected = transform_bounds('EPSG:4326', src_crs, west, south, east, north)
    # Create window from bounds
    window = from_bounds(*bounds_projected, transform=src.transform)

    # Calculate the transform and shape of the windowed output
    transform = src.window_transform(window)
    
    # Read and resample the data in the window
    data = src.read(
        window=window,
        out_shape=(
            src.count,  # number of bands
            output_size[1],  # height
            output_size[0]   # width
        ),
        #resampling=Resampling.nearest,
        resampling=Resampling.mode,
    )
    return data, transform

def normalize(arr):
    """
    Normalize array to 0–255 (uint8).

    Parameters
    ----------
    arr : np.ndarray
        Input numeric array.

    Returns
    -------
    np.ndarray
        Normalized uint8 array.
    """
    arr = arr.astype('float32')
    arr -= arr.min()
    arr /= arr.max()
    arr *= 255
    return arr.astype('uint8')

