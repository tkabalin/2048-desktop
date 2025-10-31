import random
import tkinter as tk
from tkinter import messagebox
import ctypes
import os
from PIL import Image, ImageTk
import util
import push
import sys


THEMES = {
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
        },
        "BG_COLOUR": "#bbada0",
    },

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
        },
        "BG_COLOUR": "#b4b6c2",
    },
}

def open_settings(game):
    """Opens a small popup window for settings."""
    settings_window = tk.Toplevel(game.master)
    settings_window.title("Settings")
    settings_window.resizable(False, False)
    settings_window.configure(bg=game.master["bg"])
    win_width, win_height = 250, 180
    center_window(settings_window, win_width, win_height, game.master)



def center_window(window, width, height, parent):
    """Centers 'window' of given width/height over the parent window."""
    # Parent position
    parent.update_idletasks()
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    # Calculate position
    x = parent_x + (parent_width // 2) - (width // 2)
    y = parent_y + (parent_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")

def center_root(root, width, height):
    """Centers the root window on the screen."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f"{width}x{height}+{x}+{y}")





class Game2048:
    def __init__(self, master):
        # Create the window
        self.master = master
        master.title("2048 Game")
        master.resizable(False, False)

        self.grid = []
        util.create_grid(self.grid)
        self.add_block()
        self.add_block()

        self.cells = [[None]*4 for _ in range(4)]
        self.init_gui()
        self.update_gui()
        self.game_over = False
        master.bind("<Key>", self.key_pressed)

    def init_gui(self):
        # Top frame for settings or other controls
        self.top_frame = tk.Frame(self.master, bg=BG_COLOUR)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))

        # Gear button inside the top frame
        gear_path = os.path.join(ROOT_DIR, "assets", "settings.png")
        gear_img = Image.open(gear_path) # CREDIT: https://www.flaticon.com/free-icons/options

        gear_size = int(TILE_SIZE * 0.25) 
        gear_img = gear_img.resize((gear_size, gear_size), Image.Resampling.LANCZOS)

        # Convert to PhotoImage for Tkinter
        gear_image = ImageTk.PhotoImage(gear_img)

        self.gear_button = tk.Button(
            self.top_frame,
            image=gear_image,
            bg=BG_COLOUR,
            borderwidth=0,
            activebackground=BG_COLOUR,
            command=lambda: open_settings(self)
        )
        self.gear_button.image = gear_image
        self.gear_button.pack(side="right", padx=10)  # right-aligned in top frame

        self.restart_button = tk.Button(
            self.top_frame,
            text="Restart",
            bg=BG_COLOUR,
            borderwidth=0,
            activebackground=BG_COLOUR,
            command=self.restart
        )
        self.restart_button.pack(side="right", padx=10)  # right-aligned in top frame

        self.background = tk.Frame(self.master, bg=BG_COLOUR, width=400, height=400)
        self.background.grid(padx=10, pady=10)
        for i in range(4):
            for j in range(4):
                cell_frame = tk.Frame(
                    self.background,
                    bg=TILE_COLORS[0][0],
                    width=100,
                    height=100
                )

                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                cell_label = tk.Label(
                    cell_frame,
                    text="",
                    bg=TILE_COLORS[0][0],
                    fg=TILE_COLORS[0][1],
                    font=("Helvetica", 24, "bold"),
                    width=4,
                    height=2
                )
                cell_label.grid(sticky="nsew")
                self.cells[i][j] = cell_label

        # Ensure all cells expand evenly
        for i in range(4):
            self.background.grid_rowconfigure(i, weight=1)
            self.background.grid_columnconfigure(i, weight=1)


    def add_block(self):
        options = [2,2,2,2,2,4]
        chosen = options[random.randint(0,len(options)-1)]
        found = False
        while not found:
            x = random.randint(0, 3)
            y = random.randint(0, 3)
            if self.grid[x][y] == 0:
                self.grid[x][y] = chosen
                found = True

    def update_gui(self):
        for i in range(4):
            for j in range(4):
                value = self.grid[i][j]
                bg_color, fg_color = TILE_COLORS.get(value, ("#3c3a32", "#f9f6f2")) # Default fallback colour
                self.cells[i][j].config(text=str(value) if value != 0 else "", bg=bg_color, fg=fg_color)
        self.master.update_idletasks()

    def update_theme(self, theme):
        global TILE_COLORS, BG_COLOUR
        TILE_COLORS = theme["TILE_COLORS"]
        BG_COLOUR = theme["BG_COLOUR"]
        self.master.configure(bg=BG_COLOUR)
        self.background.configure(bg=BG_COLOUR)
        self.update_gui()
    
    def restart(self):
        self.game_over = False
        self.grid = []
        util.create_grid(self.grid)
        self.add_block()
        self.add_block()
        self.update_gui()

    def key_pressed(self, event):   # Accepts both arrows and WSAD
        key = event.keysym.lower()

        # Shortcuts
        if key == 'z':
            self.random_strat()
            return
        if key == 'x':
            self.corner_strat()
            return
        if key == 'c':
            self.max_merge_strat()
            return

        saved_grid = util.copy_grid(self.grid)
        
        if key == 'up' or key == 'w':
            push.push_up(self.grid)
        elif key == 'down' or key == 's':
            push.push_down(self.grid)
        elif key == 'left' or key == 'a':
            push.push_left(self.grid)
        elif key == 'right' or key == 'd':
            push.push_right(self.grid)

        if not util.grid_equal(saved_grid, self.grid):  # Only add a block if the grid has changed
            self.add_block()
        
        self.make_move()

    def make_move(self):
        self.update_gui()
        
        if util.check_won(self.grid):
            self.game_over = True
            messagebox.showinfo("2048", "You won!")
        elif util.check_lost(self.grid):
            self.game_over = True
            messagebox.showinfo("2048", "Game Over!")

    def random_strat(self):
        if self.game_over:
            return  # Stop running when game is over
        saved_grid = util.copy_grid(self.grid)
        num = random.randint(0, 3)

        match num:
            case 0:
                push.push_up(self.grid)
            case 1:
                push.push_down(self.grid)
            case 2:
                push.push_left(self.grid)
            case 3:
                push.push_right(self.grid)
            
        if not util.grid_equal(saved_grid, self.grid):  # Only add a block if the grid has changed
            self.add_block()

        self.make_move()
        if not self.game_over:
            self.master.after(0, self.random_strat)

    def corner_strat(self):
        if self.game_over:
            return

        saved_grid = util.copy_grid(self.grid)

        # Priority order: LEFT, UP, DOWN, RIGHT
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

        # Add a new block if the grid changed
        if not util.grid_equal(saved_grid, self.grid):
            self.add_block()

        self.make_move()

        if not self.game_over:
            self.master.after(0, self.corner_strat)

    def max_merge_strat(self):  # not working properly
        if self.game_over:
            return
        
        saved_grid = [row[:] for row in self.grid]
        
        move = self.best_merge_move(self.grid)
        if move == "up":
            push.push_up(self.grid)
        elif move == "down":
            push.push_down(self.grid)
        elif move == "left":
            push.push_left(self.grid)
        elif move == "right":
            push.push_right(self.grid)
        elif move == None:  # Choose the first possible move
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

        
        if not util.grid_equal(saved_grid, self.grid):
            self.add_block()
        
        self.make_move()
        if not self.game_over:
            self.master.after(0, self.max_merge_strat)  # Recurse

    def count_merges(self, grid, move_func):
        original_grid_copy = [row[:] for row in grid] # For checking if grid changed
        temp_grid = [row[:] for row in grid]          # For applying the move
        
        original_sum = sum(sum(row) for row in temp_grid)
        
        move_func(temp_grid)
        
        # Check if the move did anything at all
        is_valid_move = not util.grid_equal(original_grid_copy, temp_grid)
        
        new_sum = sum(sum(row) for row in temp_grid)
        merged_value = new_sum - original_sum
        
        return merged_value, is_valid_move # Return both

    def best_merge_move(self, grid):
        moves = [
            ("up", push.push_up),
            ("down", push.push_down),
            ("left", push.push_left),
            ("right", push.push_right)
        ]
        
        best_move = None
        max_merge = -1
        
        for name, func in moves:
            merged, is_valid = self.count_merges(grid, func) # Unpack tuple
            
            # Only consider moves that actually change the grid
            if is_valid:
                if merged > max_merge:
                    max_merge = merged
                    best_move = name
        
        # If all valid moves have merge_value=0, this will pick the first valid one.
        # If no moves are valid, this will correctly return None.
        return best_move


if __name__ == "__main__":
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        ROOT_DIR = sys._MEIPASS
    except AttributeError:
        # Development environment
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.dirname(SCRIPT_DIR)

    # Increase DPI where possible
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    # Initialise window
    root = tk.Tk()

    # Set scalling
    dpi = root.winfo_fpixels('1i')
    MIN_SCALE = 1.5   
    scale = max(dpi / 96.0, MIN_SCALE)
    TILE_SIZE = int(100 * scale)
    FONT_SIZE = int(24 * scale)
    root.tk.call('tk', 'scaling', scale)
    
    # center_root(root, win_width, win_height)  NEED TO IMPLEMENT

    # Set the theme
    current_theme = THEMES["colourful"]
    TILE_COLORS = current_theme["TILE_COLORS"]
    BG_COLOUR = current_theme["BG_COLOUR"]
    root.configure(bg=BG_COLOUR)

    # Set the icon
    icon_path = os.path.join(ROOT_DIR, "assets", "2048-icon.png")
    icon_image = tk.PhotoImage(file=icon_path)
    root.iconphoto(True, icon_image)

    # Start the game
    game = Game2048(root)
  
    root.mainloop()
