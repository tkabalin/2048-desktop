import random

class Board:
    def __init__(self, grid_size):
        self.grid = []
        self.game_over = False
        self.update_callback = None
        self.grid_size = grid_size
        self.restart()

    def set_update_callback(self, fn):
        self.update_callback = fn

    def get_grid(self):
        return self.grid

    def add_new_tile(self):
        empty_cells = [(r, c)
                       for r in range(self.grid_size)
                       for c in range(self.grid_size)
                       if self.grid[r][c] == 0]
        if not empty_cells:
            return
        r, c = random.choice(empty_cells)
        self.grid[r][c] = 4 if random.random() < 0.1 else 2

    def restart(self):
        self.game_over = False
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.add_new_tile()
        self.add_new_tile()
        if self.update_callback:
            self.update_callback()