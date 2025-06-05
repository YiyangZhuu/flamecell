import numpy as np

class Cell:
    def __init__(self, state="EMPTY", health=0):
        # state can be "EMPTY", "TREE", "GRASS", "FIRE", "ASH", "WATER"
        self.state = state
        self.health = health
        # neighbors are relative coordinates
        # e.g. (-1, 0) means left neighbor
        self.neighbors = [(dx, dy) for dx in [-1, 0, 1]
                          for dy in [-1, 0, 1]
                          if not (dx == 0 and dy == 0)]

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = np.array([[Cell() for _ in range(width)] for _ in range(height)])

    def get_state(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None

class RuleSet:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def apply(self, cell, neighbors):
        new_state = cell.state
        new_health = cell.health
        for rule in self.rules:
            new_state, new_health = rule(cell, neighbors, new_state, new_health)
        return new_state, new_health

class Simulation:
    def __init__(self, grid, ruleset):
        self.grid = grid
        self.ruleset = ruleset
        self.step_count = 0
        self.max_steps = 1000

    def run(self):
        while self.step_count < self.max_steps:
            #print(f"Step {self.step_count}")
            new_states = [[None for _ in range(self.grid.width)] for _ in range(self.grid.height)]

            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    cell = self.grid.cells[y][x]
                    neighbors = [
                        self.grid.get_state(x + dx, y + dy)
                        for dx, dy in cell.neighbors
                        if self.grid.get_state(x + dx, y + dy) is not None
                    ]
                    new_states[y][x] = self.ruleset.apply(cell, neighbors)

            # Apply new states
            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    state, health = new_states[y][x]
                    self.grid.cells[y][x].state = state
                    self.grid.cells[y][x].health = health
            
            self.step_count += 1

# Rules
def ignite_if_neighbor_burning(cell, neighbors, state, health):
    if state == "TREE":
        for neighbor in neighbors:
            if neighbor and neighbor.state == "FIRE":
                return "FIRE", 3  # Start burning with health 3
    return state, health


def burning(cell, neighbors, state, health):
    if state == "FIRE":
        health -= 1
        if health <= 0:
            return "ASH", 0
    return state, health

def main():
    # Test run
    width, height = 10, 10
    grid = Grid(width, height)
    # Fill the grid with trees
    for y in range(height):
        for x in range(width):
            grid.cells[y][x].state = "TREE"
            grid.cells[y][x].health = 3  # Set health for trees

    # set water
    for x in range(width):
        grid.cells[3][x].state = "WATER"
        grid.cells[height - 1][x].state = "WATER"

    # Ignite the center
    grid.cells[height // 2][width // 2].state = "FIRE"

    ruleset = RuleSet()
    ruleset.add_rule(ignite_if_neighbor_burning)
    ruleset.add_rule(burning)

    sim = Simulation(grid, ruleset)
    sim.max_steps = 10
    sim.run()

    # Print resulting grid states
    for row in grid.cells:
        print(" ".join(cell.state[0] for cell in row))

main()
