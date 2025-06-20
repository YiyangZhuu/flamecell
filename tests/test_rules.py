import numpy as np
import pytest
from flamecell.rules import ignite, burning

@pytest.mark.parametrize("state, neighbors, expected", [
    ("TREE", [("FIRE", 0, 1)], "FIRE"),
    ("GRASS", [("FIRE", 1, 0)], "FIRE"),
    ("TREE", [], "TREE"),
    ("WATER", [("FIRE", 0, 1)], "WATER"),
])
def test_ignite_triggers_fire(monkeypatch, state, neighbors, expected):
    monkeypatch.setattr(np.random, "rand", lambda: 0.0)  # Force ignition
    new_state, _ = ignite(0, 0, state, 10, neighbors, prob=1.0, humidity=0.0)
    assert new_state == expected

def test_ignite_does_not_trigger_without_fire_neighbor():
    new_state, _ = ignite(0, 0, "TREE", 10, [("ASH", 0, 1)], prob=1.0, humidity=0.0)
    assert new_state == "TREE"

@pytest.mark.parametrize("initial_health", [1, 2])
def test_burning_to_ash(monkeypatch, initial_health):
    monkeypatch.setattr(np.random, "randint", lambda a, b: initial_health)
    new_state, new_health = burning(0, 0, "FIRE", initial_health, [])
    assert new_state == "ASH"
    assert new_health == 0

def test_burning_still_fire(monkeypatch):
    monkeypatch.setattr(np.random, "randint", lambda a, b: 1)
    new_state, new_health = burning(0, 0, "FIRE", 3, [])
    assert new_state == "FIRE"
    assert new_health == 2