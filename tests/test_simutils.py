import pytest
import numpy as np
from unittest.mock import patch, MagicMock
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
    (1, "EMPTY")
])
def test_raster_to_cell(value, expected):
    assert raster_to_cell(value) == expected

def test_raster_to_cell_type_error():
    with pytest.raises(TypeError):
        raster_to_cell("0")

def test_raster_to_grid_shape_and_values():
    data = np.array([[31, 32], [5, 0]])
    grid = raster_to_grid(data)
    assert grid.state.shape == (2, 2)
    assert grid.state[0, 0] == "TREE"
    assert grid.health[0, 0] == 10
    assert grid.state[0, 1] == "GRASS"
    assert grid.health[0, 1] == 4
    assert grid.state[1, 0] == "WATER"
    assert grid.health[1, 0] == 0
    assert grid.state[1, 1] == "EMPTY"
    assert grid.health[1, 1] == 0

def test_grid_to_img_shape_and_type():
    grid = Grid(3, 2)
    grid.state[0, 0] = "TREE"
    img = grid_to_img(grid)
    assert img.shape == (2, 3, 3)
    assert img.dtype == np.uint8

def test_plot_grid_returns_figure():
    grid = Grid(2, 2)
    fig = plot_grid(grid)
    assert fig is not None
    assert hasattr(fig, "savefig")  # basic sanity check

def test_plot_risk_map_returns_figure():
    grid = Grid(2, 2)
    sim = Simulation(grid, ruleset=MagicMock())
    fig = plot_risk_map(sim)
    assert fig is not None
    assert hasattr(fig, "savefig")

@patch("flamecell.sim_utils.requests.get")
def test_get_current_wind_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "current": {
            "wind_speed_10m": 3.5,
            "wind_direction_10m": 90
        }
    }
    mock_get.return_value = mock_response

    speed, direction = get_current_wind(50, 6)
    assert speed == 3.5
    assert direction == 90

@patch("flamecell.sim_utils.requests.get")
def test_get_current_wind_failure(mock_get):
    mock_get.side_effect = Exception("Network error")
    msg, direction = get_current_wind(50, 6)
    assert "Network error" in msg
    assert direction is None

@patch("flamecell.sim_utils.from_bounds")
@patch("flamecell.sim_utils.transform_bounds")
def test_crop_and_resample_mocks(transform_bounds_mock, from_bounds_mock):
    mock_src = MagicMock()
    mock_src.read.return_value = np.ones((1, 128, 128))
    mock_src.crs = "EPSG:25832"
    mock_src.transform = "dummy_transform"
    mock_src.window_transform.return_value = "dummy_window_transform"

    transform_bounds_mock.return_value = (1, 2, 3, 4)
    from_bounds_mock.return_value = "window"

    bounds = {
        "_southWest": {"lat": 50.0, "lng": 6.0},
        "_northEast": {"lat": 51.0, "lng": 7.0}
    }

    data, transform = crop_and_resample(mock_src, bounds)
    assert data.shape == (1, 128, 128)
    assert transform == "dummy_window_transform"