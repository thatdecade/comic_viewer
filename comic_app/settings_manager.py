import json
import os

DEFAULT_COMICS = [{
    "name": "Fox Trot",
    "url": "foxtrot",
    "short_code": "ft",
    "header_bg": "#ff0000",
    "header_fg": "#ffffff"
}]

DEFAULT_SETTINGS = {
    "comics": DEFAULT_COMICS,
    "SECRET_KEY": "",
    "folder_path": os.getenv('COMIC_VIEWER_PATH', os.path.join(os.path.expanduser("~"), "Pictures", "comics"))
}

SETTINGS_FILE = 'settings.json'

class SettingsManager:
    def __init__(self, settings_file_path):
        self.settings_file = settings_file_path
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            settings_dir = os.path.dirname(self.settings_file)
            if settings_dir:  # Check if settings_dir is not empty
                os.makedirs(settings_dir, exist_ok=True)
            settings = DEFAULT_SETTINGS
        else:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)

        # Ensure all default settings are present
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = value

        return settings

    def save_settings(self, settings):
        settings_dir = os.path.dirname(self.settings_file)
        if settings_dir:  # Check if settings_dir is not empty
            os.makedirs(settings_dir, exist_ok=True)
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
