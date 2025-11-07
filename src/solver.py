from board import Board
import push
import util
import random


class Solver:
    def __init__(self, board: Board, gui, delay):
        self.board = board
        self.gui = gui
        self.running_strategy = None
        self.delay = delay.get()

    def stop(self):
        if self.running_strategy:
            self.gui.master.after_cancel(self.running_strategy)
            self.running_strategy = None

    def random_strat(self):
        if self.board.game_over:
            return
        
        grid = self.board.grid
        saved_grid = util.copy_grid(grid)
        move = random.randint(0, 3)
        match move:
            case 0:
                push.push_up(self.board.grid)
            case 1:
                push.push_down(self.board.grid)
            case 2:
                push.push_left(self.board.grid)
            case 3:
                push.push_right(self.board.grid)

        if not util.grid_equal(saved_grid, grid):
            self.board.add_new_tile()

        self.gui.make_move()
        if not self.board.game_over:
            self.running_strategy = self.gui.master.after(self.delay, self.random_strat)

    def corner_strat(self):
        if self.board.game_over:
            return

        grid = self.board.grid
        saved_grid = util.copy_grid(grid)

        # Priority order: LEFT, UP, DOWN, RIGHT
        moved = False

        push.push_left(grid)
        if not util.grid_equal(saved_grid, grid):
            moved = True
        if not moved:
            push.push_up(grid)
            if not util.grid_equal(saved_grid, grid):
                moved = True
        if not moved:
            push.push_down(grid)
            if not util.grid_equal(saved_grid, grid):
                moved = True
        if not moved:
            push.push_right(grid)

        if not util.grid_equal(saved_grid, grid):
            self.board.add_new_tile()

        self.gui.make_move()

        if not self.board.game_over:
            self.running_strategy = self.gui.master.after(self.delay, self.corner_strat)

    def max_merge_strat(self):  
        if self.board.game_over:
            return
        grid = self.board.grid
        saved_grid = util.copy_grid(grid)
        move = self.best_merge_move(grid)
        if move == "up":
            push.push_up(grid)
        elif move == "down":
            push.push_down(grid)
        elif move == "left":
            push.push_left(grid)
        elif move == "right":
            push.push_right(grid)
        else: # Choose the first possible move
            moved = False
            push.push_left(self.board.grid)
            if not util.grid_equal(saved_grid, self.board.grid):
                moved = True

            if not moved:
                push.push_up(self.board.grid)
                if not util.grid_equal(saved_grid, self.board.grid):
                    moved = True

            if not moved:
                push.push_down(self.board.grid)
                if not util.grid_equal(saved_grid, self.board.grid):
                    moved = True

            if not moved:
                push.push_right(self.board.grid)

        if not util.grid_equal(saved_grid, grid):
            self.board.add_new_tile()
        self.gui.make_move()
        if not self.board.game_over:
            self.running_strategy = self.gui.master.after(self.delay, self.max_merge_strat)

    def count_empty(self, grid, move_function):
        temp_grid = [row[:] for row in grid]
        
        move_function(temp_grid)
        # Check if the move did anything at all
        is_valid_move = not util.grid_equal(grid, temp_grid)
        
        if not is_valid_move:
            return 0, False

        # Count the number of empty (zero) tiles in the new grid
        empty_tiles = 0
        for r in range(4):
            for c in range(4):
                if temp_grid[r][c] == 0:
                    empty_tiles += 1
        
        # The "best" move is the one that creates the most empty space.
        move_score = empty_tiles
        
        return move_score, is_valid_move

    def best_merge_move(self, grid):
        moves = [
            ("up", push.push_up),
            ("down", push.push_down),
            ("left", push.push_left),
            ("right", push.push_right)
        ]
        best_move = None
        max_score = -1
        for name, move_function in moves:
            score, is_valid = self.count_empty(grid, move_function)           
            
            if is_valid and score > max_score:
                max_score = score
                best_move = name
        return best_move