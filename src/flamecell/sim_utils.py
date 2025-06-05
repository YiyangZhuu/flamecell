def raster_to_cell(pixel_value):
    if pixel_value < 50:
        return "WATER"
    elif pixel_value < 150:
        return "EMPTY"
    elif pixel_value < 190:
        return "TREE"
    else: 
        return "GRASS"
