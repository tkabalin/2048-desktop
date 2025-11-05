# --- Imports ---

import random
import tkinter as tk
from tkinter import messagebox
import ctypes
import os
from PIL import Image, ImageTk
import util
import push
import sys
from enum import Enum

# --- Constants ---

THEMES = {
    "colourful": {
        "TILE_COLORS": {
            0: ("#cecfd7", "#f9f6f2"),
            2: ("#5c707b", "#f9f6f2"),
            4: ("#42b5a6", "#f9f6f2"),
            8: ("#9d600f", "#f9f6f2"),
            16: ("#b92c92", "#f9f6f2"),
            32: ("#0F4C52", "#f9f6f2"),
            64: ("#00abd6", "#f9f6f2"),
            128: ("#018652", "#f9f6f2"),
            256: ("#ff6d00", "#f9f6f2"),
            512: ("#c6d601", "#f9f6f2"),
            1024: ("#00457c", "#f9f6f2"),
            2048: ("#ffd203", "#f9f6f2"),
            "default": ("#3c3a32", "#f9f6f2")
        },
        "BG_COLOUR": "#b4b6c2",
    },
    "classic": {
        "TILE_COLORS": {
            0: ("#cdc1b4", "#776e65"),
            2: ("#eee4da", "#776e65"),
            4: ("#ede0c8", "#776e65"),
            8: ("#f2b179", "#f9f6f2"),
            16: ("#f59563", "#f9f6f2"),
            32: ("#f67c5f", "#f9f6f2"),
            64: ("#f65e3b", "#f9f6f2"),
            128: ("#edcf72", "#f9f6f2"),
            256: ("#edcc61", "#f9f6f2"),
            512: ("#edc850", "#f9f6f2"),
            1024: ("#edc53f", "#f9f6f2"),
            2048: ("#edc22e", "#f9f6f2"),
            "default": ("#3c3a32", "#f9f6f2")
        },
        "BG_COLOUR": "#bbada0",
    },
    "dark": {
        "TILE_COLORS": {
            0: ("#3a3a3c", "#9e9e9e"),
            2: ("#4f4f4f", "#f2f2f2"),
            4: ("#6a6a6a", "#f2f2f2"),
            8: ("#b58900", "#fdf6e3"),
            16: ("#cb4b16", "#fdf6e3"),
            32: ("#dc322f", "#fdf6e3"),
            64: ("#d33682", "#fdf6e3"),
            128: ("#6c71c4", "#fdf6e3"),
            256: ("#268bd2", "#fdf6e3"),
            512: ("#2aa198", "#fdf6e3"),
            1024: ("#859900", "#fdf6e3"),
            2048: ("#b71c1c", "#ffffff"),
            "default": ("#3c3a32", "#f9f6f2")
        },
        "BG_COLOUR": "#1e1e1e",
    },
}


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


# --- Board Logic ---

class Board:
    GRID_SIZE = 4

    def __init__(self):
        self.grid = []
        self.game_over = False
        self.update_callback = None
        self.restart()

    def set_update_callback(self, fn):
        self.update_callback = fn

    def get_grid(self):
        return self.grid

    def add_new_tile(self):
        empty_cells = [(r, c)
                       for r in range(self.GRID_SIZE)
                       for c in range(self.GRID_SIZE)
                       if self.grid[r][c] == 0]
        if not empty_cells:
            return
        r, c = random.choice(empty_cells)
        self.grid[r][c] = 4 if random.random() < 0.1 else 2

    def restart(self):
        self.game_over = False
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.add_new_tile()
        self.add_new_tile()
        if self.update_callback:
            self.update_callback()


# --- Solver (Autoplay) ---

class Solver:
    def __init__(self, board: Board, gui):
        self.board = board
        self.gui = gui
        self.running_strategy = None

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
                push.push_up(self.grid)
            case 1:
                push.push_down(self.grid)
            case 2:
                push.push_left(self.grid)
            case 3:
                push.push_right(self.grid)

        if not util.grid_equal(saved_grid, grid):
            self.board.add_new_tile()

        self.gui.make_move()
        if not self.board.game_over:
            self.running_strategy = self.gui.master.after(0, self.random_strat)

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
            self.running_strategy = self.gui.master.after(0, self.corner_strat)

    def max_merge_strat(self):  # TODO: Fix
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
            push.push_left(self.grid)
            if not util.grid_equal(saved_grid, self.grid):
                moved = True

            if not moved:
                push.push_up(self.grid)
                if not util.grid_equal(saved_grid, self.grid):
                    moved = True

            if not moved:
                push.push_down(self.grid)
                if not util.grid_equal(saved_grid, self.grid):
                    moved = True

            if not moved:
                push.push_right(self.grid)

        if not util.grid_equal(saved_grid, grid):
            self.board.add_new_tile()
        self.gui.make_move()
        if not self.board.game_over:
            self.running_strategy = self.gui.master.after(0, self.max_merge_strat)

    def count_merges(self, grid):
        original_grid_copy = [row[:] for row in grid]
        temp_grid = [row[:] for row in grid]

        original_sum = sum(sum(row) for row in temp_grid)
        
        # Check if the move did anything at all
        is_valid_move = not util.grid_equal(original_grid_copy, temp_grid)

        new_sum = sum(sum(row) for row in temp_grid)
        merged_value = new_sum - original_sum
        
        return merged_value, is_valid_move

    def best_merge_move(self, grid):
        moves = [
            ("up", push.push_up),
            ("down", push.push_down),
            ("left", push.push_left),
            ("right", push.push_right)
        ]
        best_move = None
        max_merge = -1
        for name in moves:
            merged, is_valid = self.count_merges(grid)
            if is_valid and merged > max_merge:
                max_merge = merged
                best_move = name
        return best_move


# --- View / Controller ---

class GameGUI:
    def __init__(self, master, root_dir, tile_size, font_size, initial_theme_name):
        self.master = master
        self.root_dir = root_dir
        self.tile_size = tile_size
        self.font_size = font_size
        self.theme_name = initial_theme_name
        self.theme = THEMES[initial_theme_name]

        self.board = Board()
        self.board.set_update_callback(self.update_gui)
        self.solver = Solver(self.board, self)

        self.cells = [[None] * Board.GRID_SIZE for _ in range(Board.GRID_SIZE)]
        self.init_gui()
        self.update_gui()
        self.master.bind("<Key>", self.key_pressed)

    def init_gui(self):
        bg_colour = self.theme["BG_COLOUR"]
        self.master.configure(bg=bg_colour)

        # Settings bar
        self.top_frame = tk.Frame(self.master, bg=bg_colour)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        # Settings button
        try:
            gear_path = os.path.join(self.root_dir, "assets", "settings.png")
            gear_img = Image.open(gear_path) # CREDIT: https://www.flaticon.com/free-icons/options
            gear_size = int(self.tile_size * 0.25)
            gear_img = gear_img.resize((gear_size, gear_size), Image.Resampling.LANCZOS)
            gear_image = ImageTk.PhotoImage(gear_img)
            self.gear_button = tk.Button(
                self.top_frame,
                image=gear_image,
                bg=bg_colour,
                borderwidth=0,
                activebackground=bg_colour,
                command=self.open_settings
            )
            self.gear_button.image = gear_image
            self.gear_button.pack(side="right", padx=10)
        except Exception as e:
            print(f"Could not load settings icon: {e}")
            self.gear_button = tk.Button(self.top_frame, text="Settings", command=self.open_settings)
            self.gear_button.pack(side="right", padx=10)

        # Restart button
        self.restart_button = tk.Button(
            self.top_frame,
            text="Restart",
            bg=bg_colour,
            fg=self.theme["TILE_COLORS"][2][1],
            borderwidth=0,
            activebackground=bg_colour,
            command=self.restart_game
        )
        self.restart_button.pack(side="right", padx=10)

        # Main board
        self.background = tk.Frame(self.master, bg=bg_colour)
        self.background.grid(row=1, column=0, padx=10, pady=10)

        for i in range(Board.GRID_SIZE):
            for j in range(Board.GRID_SIZE):
                cell_frame = tk.Frame(
                    self.background,
                    bg=self.theme["TILE_COLORS"][0][0],
                    width=self.tile_size,
                    height=self.tile_size
                )
                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                cell_label = tk.Label(
                    cell_frame,
                    text="",
                    bg=self.theme["TILE_COLORS"][0][0],
                    fg=self.theme["TILE_COLORS"][0][1],
                    font=("Helvetica", self.font_size, "bold"),
                    width=4,
                    height=2
                )
                cell_label.pack(expand=True, fill="both")
                self.cells[i][j] = cell_label

    def restart_game(self):
        self.solver.stop()
        self.board.restart()
        self.update_gui()

    def key_pressed(self, event): # Accepts both arrows and WSAD
        key = event.keysym.lower()
        if key in ['up', 'w', 'down', 's', 'left', 'a', 'right', 'd']:  # If user tries to interact
            self.solver.stop()
        
        ##### TEMP #####
        if key == 'z':
            self.solver.random_strat()
            return
        if key == 'x':
            self.solver.corner_strat()
            return
        if key == 'c':
            self.solver.max_merge_strat()
            return
        ######

        grid = self.board.grid
        saved_grid = util.copy_grid(grid)

        if key in ['up', 'w']:
            push.push_up(grid)
        elif key in ['down', 's']:
            push.push_down(grid)
        elif key in ['left', 'a']:
            push.push_left(grid)
        elif key in ['right', 'd']:
            push.push_right(grid)
        
        if not util.grid_equal(saved_grid, grid):   # Only add a block if the grid has changed
            self.board.add_new_tile()

        self.make_move()

    def make_move(self):
        self.update_gui()
        grid = self.board.grid
        if util.check_won(grid):
            self.board.game_over = True
            messagebox.showinfo("2048", "You won!")
        elif util.check_lost(grid):
            self.board.game_over = True
            messagebox.showinfo("2048", "Game Over!")

    def update_theme(self, theme_name):
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        bg_colour = self.theme["BG_COLOUR"]
        self.master.configure(bg=bg_colour)
        self.top_frame.configure(bg=bg_colour)
        self.background.configure(bg=bg_colour)
        self.restart_button.configure(bg=bg_colour, fg=self.theme["TILE_COLORS"][2][1])
        try:
            self.gear_button.configure(bg=bg_colour, activebackground=bg_colour)
        except Exception:
            pass
        self.update_gui()

    def update_gui(self):
        grid = self.board.get_grid()
        for i in range(Board.GRID_SIZE):
            for j in range(Board.GRID_SIZE):
                value = grid[i][j]
                # Get colors, using 'default' if value > 2048
                bg_color, fg_color = self.theme["TILE_COLORS"].get(value, self.theme["TILE_COLORS"]["default"])
                text = str(value) if value != 0 else ""
                label = self.cells[i][j]
                label.config(text=text, bg=bg_color, fg=fg_color)

                # Adjust font size for larger numbers
                if len(text) > 4:
                    label.config(font=("Helvetica", self.font_size - 8, "bold"))
                elif len(text) > 2:
                    label.config(font=("Helvetica", self.font_size - 4, "bold"))
                else:
                    label.config(font=("Helvetica", self.font_size, "bold"))

        self.master.update_idletasks()

    def open_settings(self):
        SettingsWindow(self.master, self.theme_name, self.update_theme)


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, current_theme_name, theme_callback):
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.theme_callback = theme_callback
        self.parent = parent
        self.current_theme_name = tk.StringVar(value=current_theme_name)
        self.configure(bg=parent.cget("bg"))
        self.create_widgets()
        self.center_window(250, 180)

    def create_widgets(self):
        tk.Label(self, text="Select Theme:", bg=self.parent.cget("bg"), fg="#FFFFFF").pack(pady=(10, 5))
        for theme_name in THEMES.keys():
            rb = tk.Radiobutton(
                self,
                bg=self.parent.cget("bg"),
                fg="#FFFFFF",
                text=theme_name.title(),
                variable=self.current_theme_name,
                value=theme_name,
                activebackground=self.parent.cget("bg"),
                command=self.apply_and_close
            )
            rb.pack(anchor="w", padx=20)

    def apply_and_close(self):
        selected_theme = self.current_theme_name.get()
        self.theme_callback(selected_theme)
        self.destroy()

    def center_window(self, width, height):
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


# --- App Wrapper ---

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root_dir = self._find_root_directory()
        self._setup_DPI_and_scaling()
        self._load_config_and_assets()
        self.game = GameGUI(
            self.root,
            self.root_dir,
            self.tile_size,
            self.font_size,
            self.initial_theme_name
        )
        self._center_root()

    def _find_root_directory(self):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            return sys._MEIPASS
        except AttributeError:
            # Development environment
            script_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.dirname(script_dir)

    def _setup_DPI_and_scaling(self):
        # Increase DPI where possible
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
        
        # Set scalling 
        # TODO: Improve scaling behaviour 
        dpi = self.root.winfo_fpixels('1i')
        MIN_SCALE = 1.5
        scale = max(dpi / 96.0, MIN_SCALE)
        self.tile_size = int(100 * scale)
        self.font_size = int(24 * scale)
        self.root.tk.call('tk', 'scaling', scale)

    def _load_config_and_assets(self):
        self.initial_theme_name = "colourful"
        initial_theme = THEMES[self.initial_theme_name]
        self.root.title("2048 Game")
        self.root.configure(bg=initial_theme["BG_COLOUR"])
        self.root.resizable(False, False)
        try:
            icon_path = os.path.join(self.root_dir, "assets", "2048-icon.png")
            icon_image = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon_image)
        except Exception as e:
            print(f"Could not load window icon: {e}")

    def _center_root(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()


# --- Main Execution ---

if __name__ == "__main__":
    app = Application()
    app.run()
