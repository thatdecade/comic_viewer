import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import platform
import requests

from comic_app.settings_manager import SettingsManager, SETTINGS_FILE
from comic_app.comic_manager import ComicManager
from comic_app.image_handler import ImageHandler
from comic_app.date_navigator import DateNavigator
from comic_app.dialog_change_comic import ChangeComicDialog

try:
    from comic_app.image_url_parser import Image_URL_Parser
    parser_available = True
except ImportError:
    parser_available = False

class ComicViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.initialized = False
        self.title("Comic Viewer")
        self.geometry("800x600")

        self.settings_manager = SettingsManager(SETTINGS_FILE)
        self.settings         = self.settings_manager.settings
        
        self.comic_manager    = ComicManager(self.settings["comics"])
        self.selected_comic   = self.comic_manager.selected_comic

        self.load_settings()
        self.create_widgets()
        
        self.bind("<Configure>", self.on_resize)
        self.bind("<Right>", self.date_navigator.next_day)
        self.bind("<Left>", self.date_navigator.previous_day)
        self.bind("<Up>", self.date_navigator.previous_week)
        self.bind("<Down>", self.date_navigator.next_week)

    def create_widgets(self):
        # Header
        self.header = tk.Label(self, text=self.selected_comic["name"], bg=self.selected_comic["header_bg"], fg=self.selected_comic["header_fg"], font=("Helvetica", 16))
        self.header.pack(fill=tk.X)

        # Control Frame
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Comic Selector
        if len(self.comic_manager.comics) > 1:
            tk.Label(self.control_frame, text="Select Comic:").pack(pady=5)
            self.comic_selector = ttk.Combobox(self.control_frame, values=[comic['name'] for comic in self.comic_manager.comics])
            self.comic_selector.pack(pady=5)
            self.comic_selector.bind("<<ComboboxSelected>>", self.on_comic_change)
            self.comic_selector.set(self.selected_comic["name"])

        # Date Selector
        tk.Label(self.control_frame, text="Select Date:").pack(pady=5)
        self.date_selector = DateEntry(self.control_frame, width=12, year=self.date.year, month=self.date.month, day=self.date.day, date_pattern='y-mm-dd')
        self.date_selector.pack(pady=5)
        self.date_selector.bind("<<DateEntrySelected>>", self.on_date_change)
        
        self.date_navigator = DateNavigator(self.date_selector, self)

        # Buttons
        self.create_button("Find/Refresh", self.find_comic)
        self.create_button("Next Day", self.date_navigator.next_day)
        self.create_button("Previous Day", self.date_navigator.previous_day)
        self.create_button("Next Week", self.date_navigator.next_week)
        self.create_button("Previous Week", self.date_navigator.previous_week)
        self.create_button("Next Month", self.date_navigator.next_month)
        self.create_button("Previous Month", self.date_navigator.previous_month)

        # Add a separator
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        self.create_button("Add Comic", self.add_comic)
        self.create_button("Edit Comic", self.edit_comic)

        # Folder Path Selector
        tk.Label(self.control_frame, text="Set Folder Path:").pack(pady=5)
        self.folder_path_entry = tk.Entry(self.control_frame, width=30)
        self.folder_path_entry.insert(0, self.folder_path_display)
        self.folder_path_entry.pack(pady=5)
        tk.Button(self.control_frame, text="Set Path", command=self.set_folder_path).pack(pady=5)

        # Image Display
        self.image_frame = tk.Frame(self)
        self.image_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Status Bar
        self.status_bar = tk.Label(self, text="Welcome to Comic Viewer", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.image_handler = ImageHandler(self.image_label, self.status_bar)
        
    def create_button(self, text, command):
        button = tk.Button(self.control_frame, text=text, command=command)
        button.pack(fill=tk.X, pady=5)

    def on_resize(self, event):
        if self.initialized:
            self.window_width = self.winfo_width()
            self.window_height = self.winfo_height()
            self.window_x = self.winfo_x()
            self.window_y = self.winfo_y()
        if not self.initialized:
            self.initialized = True

            if self.window_size:
                self.geometry(self.window_size)

            if self.window_position:
                try:
                    self.window_x, self.window_y = map(int, self.window_position.split('+'))
                    self.geometry(f"+{self.window_x}+{self.window_y}")
                except ValueError:
                    print("Invalid window position format. Using default position.")
                    self.center_window()

            self.load_comic_on_startup()
        else:
            self.image_handler.update_image(self.image_frame.winfo_width(), self.image_frame.winfo_height(), self.status_bar.winfo_height())

    def set_folder_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, folder_path)

    def add_comic(self):
        dialog = ChangeComicDialog(self, self.comic_manager.comics)
        self.wait_window(dialog.top)

        if dialog.result:
            comic_name, comic_url, short_code, header_bg, header_fg = dialog.result
            comic_details = {
                'name': comic_name,
                'url': comic_url,
                'short_code': short_code,
                'header_bg': header_bg,
                'header_fg': header_fg
            }
            self.comic_manager.add_comic(comic_details)
            self.settings_manager.save_settings(self.settings)
            self.status_bar.config(text=f"Comic added: {comic_name}")
            self.create_comic_selector()
            self.comic_selector['values'] = [comic['name'] for comic in self.comic_manager.comics]
            self.comic_selector.set(comic_name)
            self.load_comic_details(comic_name)
            self.find_comic()

    def edit_comic(self):
        if hasattr(self, 'comic_selector'):
            selected_comic = self.comic_selector.get()
        else:
            selected_comic = self.comic_manager.comics[0]['name']
        
        for comic in self.comic_manager.comics:
            if comic['name'] == selected_comic:
                dialog = ChangeComicDialog(self, self.comic_manager.comics, comic)
                self.wait_window(dialog.top)

                if dialog.result:
                    comic_name, comic_url, short_code, header_bg, header_fg = dialog.result
                    new_details = {
                        'name': comic_name,
                        'url': comic_url,
                        'short_code': short_code,
                        'header_bg': header_bg,
                        'header_fg': header_fg
                    }
                    self.comic_manager.edit_comic(selected_comic, new_details)
                    self.settings_manager.save_settings(self.settings)
                    self.status_bar.config(text=f"Comic edited: {comic_name}")
                    
                    if hasattr(self, 'comic_selector'):
                        self.comic_selector['values'] = [comic['name'] for comic in self.comic_manager.comics]
                        self.comic_selector.set(comic_name)
                    
                    self.load_comic_details(comic_name)
                    self.find_comic()
                break

    def create_comic_selector(self):
        if len(self.comic_manager.comics) > 1 and not hasattr(self, 'comic_selector'):
            tk.Label(self.control_frame, text="Select Comic:").pack(pady=5)
            self.comic_selector = ttk.Combobox(self.control_frame, values=[comic['name'] for comic in self.comic_manager.comics])
            self.comic_selector.pack(pady=5)
            self.comic_selector.bind("<<ComboboxSelected>>", self.on_comic_change)
            self.comic_selector.set(self.selected_comic["name"])
        
    def on_comic_change(self, event):
        selected_comic = self.comic_selector.get()
        self.load_comic_details(selected_comic)
        self.find_comic()

    def load_comic_details(self, comic_name):
        comic = self.comic_manager.load_comic_details(comic_name)
        if comic:
            self.selected_comic = comic
            self.header.config(text=self.selected_comic["name"], bg=self.selected_comic["header_bg"], fg=self.selected_comic["header_fg"])
            self.status_bar.config(text=f"Comic changed to {self.selected_comic['name']}")

    def find_comic(self):
        folder_path = self.folder_path_entry.get()
        if not folder_path:
            if platform.system() == "Windows":
                folder_path = os.path.join(os.path.expanduser("~"), "Pictures", "comics")
            else:
                folder_path = os.path.join(os.path.expanduser("~"), "comics")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        self.status_bar.config(text=f"Checking folder path: {folder_path}")
        self.update_idletasks()

        date_str = self.date_selector.get_date().strftime("%y%m%d")
        file_name_jpg = f"{self.selected_comic['short_code']}{date_str}.jpg"
        file_name_bmp = f"{self.selected_comic['short_code']}{date_str}.bmp"
        file_path_jpg = os.path.join(folder_path, file_name_jpg)
        file_path_bmp = os.path.join(folder_path, file_name_bmp)

        if os.path.exists(file_path_jpg):
            self.image_handler.load_image(file_path_jpg)
            self.status_bar.config(text=f"Loaded comic from {file_path_jpg}")
            self.update_idletasks()
        elif os.path.exists(file_path_bmp):
            self.image_handler.load_image(file_path_bmp)
            self.status_bar.config(text=f"Loaded comic from {file_path_bmp}")
            self.update_idletasks()
        else:
            if parser_available:
                self.status_bar.config(text="Downloading comic image...")
                self.update_idletasks()
                comic_name = self.selected_comic["url"]
                parser = Image_URL_Parser(comic_name)
                image_url = parser.get_comic_image_url(
                    self.date_selector.get_date().year,
                    f"{self.date_selector.get_date().month:02d}",
                    f"{self.date_selector.get_date().day:02d}"
                )

                if image_url:
                    self.status_bar.config(text="Fetching image from URL...")
                    self.update_idletasks()
                    try:
                        response = requests.get(image_url, stream=True)
                        response.raise_for_status()

                        if not os.path.exists(folder_path):
                            self.status_bar.config(text="Invalid folder path. Unable to save comic image.")
                            self.update_idletasks()
                            return

                        self.status_bar.config(text="Saving comic image...")
                        self.update_idletasks()
                        with open(file_path_jpg, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        self.image_handler.load_image(file_path_jpg)
                        self.status_bar.config(text=f"Downloaded and saved comic to {file_path_jpg}")
                        self.update_idletasks()
                    except requests.RequestException as e:
                        print(f"Error downloading comic image: {e}")
                        self.status_bar.config(text=f"Failed to download the comic image: {e}")
                        self.image_handler.clear_image()
                        self.update_idletasks()
                else:
                    print("Failed to retrieve the comic image URL.")
                    self.status_bar.config(text="Failed to retrieve the comic image URL.")
                    self.image_handler.clear_image()
                    self.update_idletasks()
            else:
                self.status_bar.config(text="Image not found locally.")
                self.image_handler.clear_image()
                self.update_idletasks()

    def save_settings(self):
        self.settings.update({
            "date": self.date_selector.get_date().strftime("%Y-%m-%d"),
            "folder_path": self.folder_path_entry.get() if self.folder_path_entry.get() != os.path.expanduser("~") else "",
            "comics": self.comic_manager.comics,
            "selected_comic": self.selected_comic["name"],
            "window_size": f"{self.window_width}x{self.window_height}",
            "window_position": f"{self.window_x}+{self.window_y}"
        })
        self.settings_manager.save_settings(self.settings)

    def load_settings(self):
        self.date = datetime.strptime(self.settings.get("date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        self.folder_path = self.settings.get("folder_path", "")
        self.folder_path_display = self.folder_path if self.folder_path else os.path.join(os.path.expanduser("~"), "comics")
        self.selected_comic = self.comic_manager.load_comic_details(self.settings.get("selected_comic", self.comic_manager.comics[0]['name']))
        self.window_size = self.settings.get("window_size", "")
        self.window_position = self.settings.get("window_position", "")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def load_comic_on_startup(self):
        if self.date.strftime("%Y-%m-%d") != datetime.now().strftime("%Y-%m-%d") or self.folder_path != "":
            self.find_comic()

    def on_date_change(self, event):
        self.find_comic()

    def on_close(self):
        self.save_settings()
        self.destroy()

if __name__ == "__main__":
    app = ComicViewer()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
