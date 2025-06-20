import pytest
import numpy as np
from flamecell.sim_utils import Grid, RuleSet, Simulation
from flamecell.sim_utils import (
    raster_to_cell,
    raster_to_grid,
    grid_to_img,
    plot_grid,
    plot_risk_map,
    get_current_wind,
    crop_and_resample
)

def test_grid_init():
    with pytest.raises(ValueError, match="Width must be a positive integer"):
        Grid("10", 5)
    with pytest.raises(ValueError, match="Height must be a positive integer"):
        Grid(10, -5)

def test_ruleset_add_and_apply_rule():
    def dummy_rule(x, y, state, health, neighbors, **kwargs):
        return "BURNED", 0

    ruleset = RuleSet()
    ruleset.add_rule(dummy_rule)

    state_matrix = np.full((5, 5), "TREE", dtype=object)
    health_matrix = np.full((5, 5), 5, dtype=int)
    new_state, new_health = ruleset.apply(2, 2, state_matrix, health_matrix, neighbors=[])

    assert new_state == "BURNED"
    assert new_health == 0

def test_simulation_step():
    def ignite_rule(x, y, state, health, neighbors, **kwargs):
        if state == "TREE":
            return "FIRE", health - 1
        return state, health

    grid = Grid(3, 3)
    grid.state[1, 1] = "TREE"
    grid.health[1, 1] = 3

    ruleset = RuleSet()
    ruleset.add_rule(ignite_rule)

    sim = Simulation(grid, ruleset)
    sim.step()

    assert grid.state[1, 1] == "FIRE"
    assert grid.health[1, 1] == 2

def test_simulation_step_count_increments():
    grid = Grid(3, 3)
    ruleset = RuleSet()
    sim = Simulation(grid, ruleset)

    sim.step()
    sim.step()

    assert sim.step_count == 2

@pytest.mark.parametrize("value, expected", [
    (5, "WATER"),
    (4, "WATER"),
    (31, "TREE"),
    (32, "GRASS"),
    (22, "GRASS"),
    (1, "EMPTY"),
    ("0", TypeError)
])
def test_raster_to_cell(value, expected):
    assert raster_to_cell(value) == expected
