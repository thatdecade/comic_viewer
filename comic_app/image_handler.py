import os
import tkinter as tk
from PIL import Image, ImageTk
import io
import platform
import subprocess

if platform.system() == "Windows":
    import win32clipboard
    from win32clipboard import CF_DIB

class ImageHandler:
    def __init__(self, image_label, status_bar):
        self.image_label = image_label
        self.status_bar = status_bar
        self.image = None
        self.current_file_path = None

    def load_image(self, file_path):
        self.current_file_path = file_path
        try:
            self.image = Image.open(file_path)
            self.update_image(self.image_label.winfo_width(), self.image_label.winfo_height(), self.status_bar.winfo_height())
        except Exception as e:
            print(f"Error loading image: {e}")
            self.clear_image()

    def clear_image(self):
        self.image_label.config(image='')
        self.image_label.image = None
        self.image = None

    def update_image(self, frame_width, frame_height, status_height):
        if self.image:
            window_width = frame_width
            window_height = frame_height - status_height

            if window_width <= 1 or window_height <= 1:
                return

            image_width, image_height = self.image.size

            aspect_ratio = image_width / image_height
            new_width = min(window_width, int(window_height * aspect_ratio))
            new_height = min(window_height, int(window_width / aspect_ratio))

            if new_width <= 0 or new_height <= 0:
                return

            resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            self.image_label.config(image=photo)
            self.image_label.image = photo

    def copy_to_clipboard(self):
        if self.image:
            output = io.BytesIO()
            self.image.convert("RGB").save(output, format="BMP")
            data = output.getvalue()[14:]  # BMP header is 14 bytes long
            output.close()

            if platform.system() == "Windows":
                self.copy_to_clipboard_windows(data)
            elif platform.system() == "Darwin":
                self.copy_to_clipboard_macos(data)
            elif platform.system() == "Linux":
                self.copy_to_clipboard_linux(data)

            self.status_bar.config(text="Image copied to clipboard")

    def copy_to_clipboard_windows(self, data):
        def send_to_clipboard(clip_type, data):
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(clip_type, data)
            win32clipboard.CloseClipboard()

        send_to_clipboard(CF_DIB, data)

    def copy_to_clipboard_macos(self, data):
        p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        p.stdin.write(b'BM' + data)
        p.stdin.close()
        p.wait()

    def copy_to_clipboard_linux(self, data):
        p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'image/bmp'], stdin=subprocess.PIPE)
        p.stdin.write(b'BM' + data)
        p.stdin.close()
        p.wait()

