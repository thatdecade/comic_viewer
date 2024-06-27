import tkinter as tk
from tkinter import colorchooser, messagebox

class ChangeComicDialog:
    def __init__(self, parent, comics, comic=None):
        top = self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        self.result = None

        self.comics = comics
        self.comic = comic

        tk.Label(top, text="Comic Name: (e.g., Baby Blues)").pack(pady=5)
        self.comic_name_entry = tk.Entry(top)
        self.comic_name_entry.pack(pady=5)
        if comic:
            self.comic_name_entry.insert(0, comic['name'])

        tk.Label(top, text="Parser URL Snippet: (e.g., babyblues)").pack(pady=5)
        self.comic_url_entry = tk.Entry(top)
        self.comic_url_entry.pack(pady=5)
        if comic:
            self.comic_url_entry.insert(0, comic['url'])

        tk.Label(top, text="Image Short Code: (e.g., bb)").pack(pady=5)
        self.short_code_entry = tk.Entry(top)
        self.short_code_entry.pack(pady=5)
        if comic:
            self.short_code_entry.insert(0, comic['short_code'])

        tk.Label(top, text="Header Background Color:").pack(pady=5)
        self.header_bg_button = tk.Button(top, text="Choose Color", command=self.choose_header_bg)
        self.header_bg_button.pack(pady=5)
        self.header_bg = comic.get('header_bg', '#ff0000') if comic else '#ff0000'
        self.header_fg = comic.get('header_fg', '#ffffff') if comic else '#ffffff'
        self.header_bg_label = tk.Label(top, text=self.header_bg, bg=self.header_bg, width=20)
        self.header_bg_label.pack(pady=5)

        tk.Button(top, text="OK", command=self.on_ok).pack(pady=5)

    def choose_header_bg(self):
        color_code = colorchooser.askcolor(title="Choose Header Background Color")
        if color_code:
            self.header_bg = color_code[1]
            self.header_fg = self.contrast_color(self.header_bg, '#ffffff', '#000000')
            self.header_bg_label.config(text=self.header_bg, bg=self.header_bg, fg=self.header_fg)
        self.top.lift()  # Bring the dialog back to focus

    def on_ok(self):
        comic_name = self.comic_name_entry.get().strip()
        comic_url  = self.comic_url_entry.get().strip()
        short_code = self.short_code_entry.get().strip()

        if comic_name and comic_url and short_code:
            if self.comic:
                unique_compare_list = [comic for comic in self.comics if comic != self.comic]
            else:
                unique_compare_list = self.comics

            if any(comic_name == comic['name'] for comic in unique_compare_list):
                messagebox.showerror("Error", "Comic name must be unique.")
                return
            if any(comic_url == comic['url'] for comic in unique_compare_list):
                messagebox.showerror("Error", "Comic URL must be unique.")
                return
            if any(short_code == comic['short_code'] for comic in unique_compare_list):
                messagebox.showerror("Error", "Image short code must be unique.")
                return

            self.result = (comic_name, comic_url, short_code, self.header_bg, self.header_fg)
            print(f"User Entered: {self.result}")
            self.top.destroy()
        else:
            messagebox.showerror("Error", "All fields are required.")
    
    def contrast_color(self, bg_color, light_color, dark_color):
        color = bg_color[1:] if bg_color[0] == '#' else bg_color
        r = int(color[0:2], 16)  # hexToR
        g = int(color[2:4], 16)  # hexToG
        b = int(color[4:6], 16)  # hexToB
        uicolors = [r / 255, g / 255, b / 255]
        c = list(map(lambda col: col / 12.92 if col <= 0.03928 else pow((col + 0.055) / 1.055, 2.4), uicolors))
        L = (0.2126 * c[0]) + (0.7152 * c[1]) + (0.0722 * c[2])
        return dark_color if L > 0.179 else light_color
            
if __name__ == "__main__":
    print("Debug Mode Testing")
    root = tk.Tk()
    root.withdraw()

    comics = [{"name": "Comic Name", "url": "comicsnippet", "short_code": "cn", "header_bg": "#0000ff", "header_fg": "#ffffff"}]
    dialog = ChangeComicDialog(root, comics)
    
    root.after(0, lambda: [root.deiconify(), dialog.top.deiconify()])
    root.mainloop()
