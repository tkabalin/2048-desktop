from gui import GameGUI
import sys, os, ctypes
import tkinter as tk
from constants import THEMES


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