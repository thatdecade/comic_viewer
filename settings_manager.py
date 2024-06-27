import os
import json
from datetime import datetime

SETTINGS_FILE = "settings.json"
DEFAULT_COMICS = [{
    "name": "Fox Trot",
    "url": "foxtrot",
    "short_code": "ft",
    "header_bg": "#ff0000",
    "header_fg": "#ffffff"
}]

class SettingsManager:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                try:
                    return json.load(f)
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"Error loading settings: {e}. Resetting to default settings.")
                    return self.reset_settings()
        else:
            return self.reset_settings()

    def save_settings(self, settings):
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)

    def reset_settings(self):
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "folder_path": "",
            "comics": DEFAULT_COMICS,
            "selected_comic": DEFAULT_COMICS[0]['name'],
            "window_size": "800x600",
            "window_position": '100+100'
        }
