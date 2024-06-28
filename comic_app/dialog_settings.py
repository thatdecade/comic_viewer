import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class SettingsDialog:
    def __init__(self, parent, settings, parser_enable):
        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        self.result = None
        self.settings = settings
        self.parser_enable = parser_enable

        self.top.title("Settings")

        # Path Selection
        tk.Label(self.top, text="Default Folder Path:").pack(pady=5)
        self.folder_path_entry = tk.Entry(self.top, width=50)
        self.folder_path_entry.pack(pady=5)
        self.folder_path_entry.insert(0, settings.get("folder_path", ""))
        tk.Button(self.top, text="Browse...", command=self.browse_folder_path).pack(pady=5)

        # Local Saving Checkbox
        if self.parser_enable:
            self.local_saving_var = tk.BooleanVar(value=settings.get("local_saving", True))
            self.local_saving_checkbox = tk.Checkbutton(self.top, text="Enable Local Saving", variable=self.local_saving_var)
            self.local_saving_checkbox.pack(pady=5)

        # Date Format Selection
        tk.Label(self.top, text="Date Format:").pack(pady=5)
        self.date_format_entry = tk.Entry(self.top, width=20)
        self.date_format_entry.pack(pady=5)
        self.date_format_entry.insert(0, settings.get("date_format", "%Y-%m-%d"))

        # OK and Cancel buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

    def browse_folder_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, folder_path)

    def on_ok(self):
        if self.parser_enable:
            self.result = {
                "folder_path": self.folder_path_entry.get(),
                "local_saving": self.local_saving_var.get(),
                "date_format": self.date_format_entry.get()
            }
        else:
            self.result = {
                "folder_path": self.folder_path_entry.get(),
                "date_format": self.date_format_entry.get()
            }
        self.top.destroy()

    def on_cancel(self):
        self.top.destroy()
