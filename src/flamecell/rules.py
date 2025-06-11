import numpy as np
# Rules
# ignite under certain probability, humidity and wind
def ignite(x, y, state, health, neighbors, prob=0.15, humidity=0.4, wind=np.array([0,0]), **kwargs):
    if state in ["TREE", "GRASS"]:
        ignition_prob = 0.0
        for neighbor_state, dx, dy in neighbors:
            if neighbor_state == "FIRE":
                ignition_prob += 1 + (dx * wind[0] + dy * wind[1]) * 0.05     
        if np.random.rand() < ignition_prob * prob * (1 - humidity):
            return "FIRE", health  # Start burning
    return state, health

def burning(x, y, state, health, neighbors, **kwargs):
    if state == "FIRE":
        health -= np.random.randint(1,3)
        if health <= 0:
            return "ASH", 0
    return state, health