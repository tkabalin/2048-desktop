from constants import THEMES
from board import Board
from solver import Solver
import util, push
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import tkinter as tk

class GameGUI:
    def __init__(self, master, root_dir, tile_size, font_size, initial_theme_name):
        self.master = master
        self.root_dir = root_dir
        self.tile_size = tile_size
        self.font_size = font_size
        self.theme_name = initial_theme_name
        self.theme = THEMES[initial_theme_name]

        self.board = Board(grid_size = 4)
        self.board.set_update_callback(self.update_gui)
        self.solver = Solver(self.board, self, delay = 0)

        self.cells = [[None] * self.board.grid_size for _ in range(self.board.grid_size)]
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

        for i in range(self.board.grid_size):
            for j in range(self.board.grid_size):
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
        for i in range(self.board.grid_size):
            for j in range(self.board.grid_size):
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
