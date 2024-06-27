class ComicManager:
    def __init__(self, comics, callback):
        self.comics = comics
        self.selected_comic = comics[0]
        self.callback = callback

    def add_comic(self, comic_details):
        self.comics.append(comic_details)
        self.selected_comic = comic_details
        if hasattr(self, 'callback') and self.callback:
            self.callback()

    def edit_comic(self, selected_comic_name, new_details):
        for comic in self.comics:
            if comic['name'] == selected_comic_name:
                comic.update(new_details)
                self.selected_comic = comic
                break
        if hasattr(self, 'callback') and self.callback:
            self.callback()

    def load_comic_details(self, comic_name):
        for comic in self.comics:
            if comic['name'] == comic_name:
                self.selected_comic = comic
                return comic
        return None
