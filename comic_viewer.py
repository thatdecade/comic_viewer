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
        
        self.comic_manager    = ComicManager(self.settings["comics"], self.user_changed_comic_list_config)

        self.load_settings()
        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        self.create_header()
        self.create_control_frame()
        self.create_image_display()
        self.create_status_bar()
        self.image_handler = ImageHandler(self.image_label, self.status_bar)

    def create_header(self):
        self.header = tk.Label(self, text=self.comic_manager.selected_comic["name"], bg=self.comic_manager.selected_comic["header_bg"], fg=self.comic_manager.selected_comic["header_fg"], font=("Helvetica", 16))
        self.header.pack(fill=tk.X)

    def create_control_frame(self):
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.create_comic_selector()
        self.create_date_selector()
        self.create_navigation_buttons()
        self.create_add_edit_buttons()
        self.create_folder_path_selector()

    def create_comic_selector(self):
        if len(self.comic_manager.comics) > 1 and not hasattr(self, 'comic_selector'):
            tk.Label(self.control_frame, text="Select Comic:").pack(pady=5)
            self.comic_selector = ttk.Combobox(self.control_frame)
            self.comic_selector.pack(pady=5)
            self.comic_selector.bind("<<ComboboxSelected>>", self.on_comic_change)
        if hasattr(self, 'comic_selector'):
            self.comic_selector['values'] = [comic['name'] for comic in self.comic_manager.comics]
            self.comic_selector.set(self.comic_manager.selected_comic["name"])

    def create_date_selector(self):
        tk.Label(self.control_frame, text="Select Date:").pack(pady=5)
        self.date_selector = DateEntry(self.control_frame, width=12, year=self.date.year, month=self.date.month, day=self.date.day, date_pattern='y-mm-dd')
        self.date_selector.pack(pady=5)
        self.date_selector.bind("<<DateEntrySelected>>", self.on_date_change)
        self.date_navigator = DateNavigator(self.date_selector, self)

    def create_navigation_buttons(self):
        self.create_button("Find/Refresh", self.find_comic)
        self.create_button("Next Day", self.date_navigator.next_day)
        self.create_button("Previous Day", self.date_navigator.previous_day)
        self.create_button("Next Week", self.date_navigator.next_week)
        self.create_button("Previous Week", self.date_navigator.previous_week)
        self.create_button("Next Month", self.date_navigator.next_month)
        self.create_button("Previous Month", self.date_navigator.previous_month)
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill=tk.X, pady=10)

    def create_add_edit_buttons(self):
        self.create_button("Add Comic", self.add_comic)
        self.create_button("Edit Comic", self.edit_comic)

    def create_folder_path_selector(self):
        tk.Label(self.control_frame, text="Set Folder Path:").pack(pady=5)
        self.folder_path_entry = tk.Entry(self.control_frame, width=30)
        self.folder_path_entry.insert(0, self.folder_path_display)
        self.folder_path_entry.pack(pady=5)
        tk.Button(self.control_frame, text="Set Path", command=self.set_folder_path).pack(pady=5)

    def create_image_display(self):
        self.image_frame = tk.Frame(self)
        self.image_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(expand=True, fill=tk.BOTH)

    def create_status_bar(self):
        self.status_bar = tk.Label(self, text="Welcome to Comic Viewer", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_button(self, text, command):
        button = tk.Button(self.control_frame, text=text, command=command)
        button.pack(fill=tk.X, pady=5)

    def bind_events(self):
        self.bind("<Configure>", self.on_resize)
        self.bind("<Right>", self.date_navigator.next_day)
        self.bind("<Left>", self.date_navigator.previous_day)
        self.bind("<Up>", self.date_navigator.previous_week)
        self.bind("<Down>", self.date_navigator.next_week)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_resize(self, event):
        if self.initialized:
            self.update_window_size()
        else:
            self.initialized = True
            self.setup_initial_window()
        self.image_handler.update_image(self.image_frame.winfo_width(), self.image_frame.winfo_height(), self.status_bar.winfo_height())

    def update_window_size(self):
        self.window_width = self.winfo_width()
        self.window_height = self.winfo_height()
        self.window_x = self.winfo_x()
        self.window_y = self.winfo_y()

    def setup_initial_window(self):
        if self.window_size:
            self.geometry(self.window_size)
        if self.window_position:
            self.set_window_position()
        self.load_comic_on_startup()

    def set_window_position(self):
        try:
            self.window_x, self.window_y = map(int, self.window_position.split('+'))
            self.geometry(f"+{self.window_x}+{self.window_y}")
        except ValueError:
            print("Invalid window position format. Using default position.")
            self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def set_folder_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, folder_path)
            self.display_latest_image_from_folder()

    def display_latest_image_from_folder(self):
        folder_path = self.get_folder_path()
        short_code  = self.comic_manager.selected_comic["short_code"]
        latest_file_date = None
        latest_file_name = None

        for file in os.listdir(folder_path):
            if short_code in file:
                try:
                    date_str = file.replace(short_code, '').split('.')[0]
                    file_date = datetime.strptime(date_str, "%y%m%d")
                    if latest_file_date is None or file_date > latest_file_date:
                        latest_file_date = file_date
                        latest_file_name = file
                except ValueError:
                    continue

        if latest_file_name:
            file_path = os.path.join(folder_path, latest_file_name)
            self.image_handler.load_image(file_path)
            self.update_status_bar(f"Loaded latest comic: {latest_file_name}")
            
            self.date_selector.set_date(latest_file_date)

    def add_comic(self):
        dialog = ChangeComicDialog(self, self.comic_manager.comics)
        self.wait_window(dialog.top)

        if dialog.result:
            self.process_add_comic(dialog.result)

    def process_add_comic(self, comic_details):
        comic_name, comic_url, short_code, header_bg, header_fg = comic_details
        comic_data = {
            'name': comic_name,
            'url': comic_url,
            'short_code': short_code,
            'header_bg': header_bg,
            'header_fg': header_fg
        }
        self.comic_manager.add_comic(comic_data)

    def user_changed_comic_list_config(self):
        self.create_comic_selector()
        self.update_status_bar(f"Comic updated: {self.comic_manager.selected_comic['name']}")
        self.update_comic_selector()
        self.load_comic_details(self.comic_manager.selected_comic['name'])
        self.find_comic()

    def edit_comic(self):
        selected_comic = self.get_selected_comic()
        comic = self.get_comic_details(selected_comic)

        if comic:
            self.open_edit_comic_dialog(comic)

    def get_selected_comic(self):
        return self.comic_selector.get() if hasattr(self, 'comic_selector') else self.comic_manager.comics[0]['name']

    def get_comic_details(self, selected_comic):
        for comic in self.comic_manager.comics:
            if comic['name'] == selected_comic:
                return comic
        return None

    def open_edit_comic_dialog(self, comic):
        dialog = ChangeComicDialog(self, self.comic_manager.comics, comic)
        self.wait_window(dialog.top)

        if dialog.result:
            self.process_edit_comic(comic['name'], dialog.result)

    def process_edit_comic(self, selected_comic, new_details):
        comic_name, comic_url, short_code, header_bg, header_fg = new_details
        updated_details = {
            'name': comic_name,
            'url': comic_url,
            'short_code': short_code,
            'header_bg': header_bg,
            'header_fg': header_fg
        }
        self.comic_manager.edit_comic(selected_comic, updated_details)

    def update_comic_selector(self):
        if hasattr(self, 'comic_selector'):
            self.comic_selector['values'] = [comic['name'] for comic in self.comic_manager.comics]
            self.comic_selector.set(self.comic_manager.selected_comic['name'])

    def on_comic_change(self, event):
        selected_comic = self.comic_selector.get()
        self.load_comic_details(selected_comic)
        self.find_comic()

    def load_comic_details(self, comic_name):
        comic = self.comic_manager.load_comic_details(comic_name)
        if comic:
            self.comic_manager.selected_comic = comic
            self.header.config(text=self.comic_manager.selected_comic["name"], bg=self.comic_manager.selected_comic["header_bg"], fg=self.comic_manager.selected_comic["header_fg"])
            self.update_status_bar(f"Comic changed to {self.comic_manager.selected_comic['name']}")

    def find_comic(self):
        folder_path = self.get_folder_path()
        self.verify_folder_path(folder_path)

        date_str = self.date_selector.get_date().strftime("%y%m%d")
        file_name_jpg = f"{self.comic_manager.selected_comic['short_code']}{date_str}.jpg"
        file_name_bmp = f"{self.comic_manager.selected_comic['short_code']}{date_str}.bmp"
        file_path_jpg = os.path.join(folder_path, file_name_jpg)
        file_path_bmp = os.path.join(folder_path, file_name_bmp)

        if os.path.exists(file_path_jpg):
            self.image_handler.load_image(file_path_jpg)
            self.update_status_bar(f"Loaded comic from {file_path_jpg}")
        elif os.path.exists(file_path_bmp):
            self.image_handler.load_image(file_path_bmp)
            self.update_status_bar(f"Loaded comic from {file_path_bmp}")
        else:
            self.download_and_save_comic_image(date_str, folder_path, file_path_jpg)

    def get_folder_path(self):
        folder_path = self.folder_path_entry.get()
        if not folder_path:
            folder_path = os.path.join(os.path.expanduser("~"), "Pictures", "comics") if platform.system() == "Windows" else os.path.join(os.path.expanduser("~"), "comics")
        return folder_path

    def verify_folder_path(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        self.update_status_bar(f"Checking folder path: {folder_path}")

    def download_and_save_comic_image(self, date_str, folder_path, file_path_jpg):
        if parser_available:
            self.update_status_bar("Downloading comic image...")
            comic_name = self.comic_manager.selected_comic["url"]
            parser = Image_URL_Parser(comic_name)
            image_url = parser.get_comic_image_url(
                self.date_selector.get_date().year,
                f"{self.date_selector.get_date().month:02d}",
                f"{self.date_selector.get_date().day:02d}"
            )

            if image_url:
                self.fetch_and_save_image(image_url, file_path_jpg)
            else:
                self.handle_image_url_failure()
        else:
            self.update_status_bar("Image not found locally.")
            self.image_handler.clear_image()

    def fetch_and_save_image(self, image_url, file_path_jpg):
        self.update_status_bar("Fetching image from URL...")
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            self.save_image(response, file_path_jpg)
        except requests.RequestException as e:
            self.handle_image_download_failure(e)

    def save_image(self, response, file_path_jpg):
        with open(file_path_jpg, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        self.image_handler.load_image(file_path_jpg)
        self.update_status_bar(f"Downloaded and saved comic to {file_path_jpg}")

    def handle_image_url_failure(self):
        print("Failed to retrieve the comic image URL.")
        self.update_status_bar("Failed to retrieve the comic image URL.")
        self.image_handler.clear_image()

    def handle_image_download_failure(self, error):
        print(f"Error downloading comic image: {error}")
        self.update_status_bar(f"Failed to download the comic image: {error}")
        self.image_handler.clear_image()

    def load_settings(self):
        # Determine default folder path based on the operating system
        if platform.system() == "Windows":
            default_folder_path = os.path.join(os.path.expanduser("~"), "Pictures", "comics")
        else:
            default_folder_path = os.path.join(os.path.expanduser("~"), "comics")

        # Load settings from the settings manager
        self.date = datetime.strptime(self.settings.get("date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        self.folder_path = self.settings.get("folder_path", default_folder_path)
        self.folder_path_display = self.folder_path if self.folder_path else default_folder_path
        self.comic_manager.selected_comic = self.comic_manager.load_comic_details(self.settings.get("selected_comic", self.comic_manager.comics[0]['name']))
        self.window_size = self.settings.get("window_size", "")
        self.window_position = self.settings.get("window_position", "")

    def save_settings(self):
        self.settings.update({
            "date": self.date_selector.get_date().strftime("%Y-%m-%d"),
            "folder_path": self.folder_path_entry.get() if self.folder_path_entry.get() != os.path.expanduser("~") else "",
            "comics": self.comic_manager.comics,
            "selected_comic": self.comic_manager.selected_comic["name"],
            "window_size": f"{self.window_width}x{self.window_height}",
            "window_position": f"{self.window_x}+{self.window_y}"
        })
        self.settings_manager.save_settings(self.settings)

    def load_comic_on_startup(self):
        if self.date.strftime("%Y-%m-%d") != datetime.now().strftime("%Y-%m-%d") or self.folder_path != "":
            self.find_comic()

    def on_date_change(self, event):
        self.find_comic()

    def on_close(self):
        self.save_settings()
        self.destroy()

    def update_status_bar(self, text):
        self.status_bar.config(text=text)
        self.update_idletasks()

if __name__ == "__main__":
    app = ComicViewer()
    app.mainloop()
