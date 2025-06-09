from flamecell import Grid
import numpy as np
import matplotlib.pyplot as plt

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
            grid.cells[y][x].state = state
            if state == "TREE":
                grid.cells[y][x].health = 10
            elif state =="GRASS":
                grid.cells[y][x].health = 4
    return grid

def grid_to_img(grid):
    img = np.zeros((grid.height, grid.width, 3), dtype=np.uint8)
    for y in range(grid.height):
        for x in range(grid.width):
            img[y, x, 0] = color_map[grid.cells[y][x].state][0] * 255
            img[y, x, 1] = color_map[grid.cells[y][x].state][1] * 255
            img[y, x, 2] = color_map[grid.cells[y][x].state][2] * 255
    return img 

def plot_grid(grid):
    img = np.zeros((grid.height, grid.width, 3))
    for y in range(grid.height):
        for x in range(grid.width):
            img[y, x] = color_map[grid.cells[y][x].state]

    fig, ax = plt.subplots()
    ax.imshow(img, interpolation='none')
    ax.set_xticks([])
    ax.set_yticks([])
    return fig