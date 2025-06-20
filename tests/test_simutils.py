import pytest
from flamecell.sim_utils import Grid

def test_grid_init():
    grid = Grid(10, 10)
    assert grid.state.shape == (10, 10)
