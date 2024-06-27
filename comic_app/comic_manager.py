class ComicManager:
    def __init__(self, comics):
        self.comics = comics
        self.selected_comic = comics[0]

    def add_comic(self, comic_details):
        self.comics.append(comic_details)
        self.selected_comic = comic_details

    def edit_comic(self, selected_comic_name, new_details):
        for comic in self.comics:
            if comic['name'] == selected_comic_name:
                comic.update(new_details)
                self.selected_comic = comic
                break

    def load_comic_details(self, comic_name):
        for comic in self.comics:
            if comic['name'] == comic_name:
                self.selected_comic = comic
                return comic
        return None
