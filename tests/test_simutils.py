from sim_utils import *

def test_grid_init():
    grid = Grid(width=10, height=10)
    assert grid.state.shape == (10, 10)
