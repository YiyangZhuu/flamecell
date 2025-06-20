from flamecell import sim_utils

def test_grid_init():
    grid = Grid(width=10, height=10)
    assert grid.state.shape == (10, 10)
