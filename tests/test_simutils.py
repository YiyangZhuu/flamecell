import pytest
from flamecell.sim_utils import Grid

def test_grid_init():
    with pytest.raises(ValueError, match="Width must be a positive integer"):
        Grid("10", 5)
    with pytest.raises(ValueError, match="Height must be a positive integer"):
        Grid(10, -5)
    
