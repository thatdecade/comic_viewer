from PIL import Image, ImageTk

class ImageHandler:
    def __init__(self, image_label, status_bar):
        self.image_label = image_label
        self.status_bar = status_bar
        self.image = None

    def load_image(self, file_path):
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
