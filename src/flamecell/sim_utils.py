from flamecell import Grid
import numpy as np
import matplotlib.pyplot as plt
import requests


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

