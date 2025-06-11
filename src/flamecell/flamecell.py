from rules.py import * 

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = np.full((height, width), "EMPTY", dtype=object)
        self.health = np.zeros((height, width), dtype=int)

    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.state[y, x], self.health[y, x]
        return None, None

    def set_cell(self, x, y, state, health):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.state[y, x] = state
            self.health[y, x] = health

class RuleSet:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def apply(self, x, y, state_matrix, health_matrix, neighbors, **kwargs):
        new_state = state_matrix[y, x]
        new_health = health_matrix[y, x]
        for rule in self.rules:
            new_state, new_health = rule(x, y, new_state, new_health, neighbors, **kwargs)
        return new_state, new_health

class Simulation:
    def __init__(self, grid, ruleset):
        self.grid = grid
        self.ruleset = ruleset
        self.step_count = 0
        self.max_steps = 1000

    def step(self, prob=0.2, humidity=0.4, wind=np.array([0,0])):
        # Seperate the loop for njit optimization
        new_state = self.grid.state.copy()
        new_health = self.grid.health.copy()
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                # calculate neighbors
                neighbors = []
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height:
                            neighbor_state = self.grid.state[ny, nx]
                            neighbors.append((neighbor_state, dx, dy))
                # apply all the rules
                state, health = self.ruleset.apply(x, y, self.grid.state, self.grid.health, neighbors, prob=prob, humidity=humidity, wind=wind)
                new_state[y, x] = state
                new_health[y, x] = health
        # Apply new state
        self.grid.state = new_state
        self.grid.health = new_health
        self.step_count += 1

