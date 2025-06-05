from flamecell import Grid

def raster_to_cell(pixel_value):
    if pixel_value < 50:
        return "WATER"
    elif pixel_value < 150:
        return "EMPTY"
    elif pixel_value < 190:
        return "TREE"
    else: 
        return "GRASS"


def raster_to_grid(data):
    height, width = data.shape
    grid = Grid(width, height)
    for y in range(height):
        for x in range(width):
            state = raster_to_cell(data[y,x])
            grid.cells[y][x].state = state
            grid.cells[y][x].health 3 if state == "TREE" else 0
    return grid