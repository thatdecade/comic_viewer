from datetime import timedelta
from dateutil.relativedelta import relativedelta

class DateNavigator:
    def __init__(self, date_selector, comic_viewer):
        self.date_selector = date_selector
        self.comic_viewer = comic_viewer

    def next_day(self, event=None):
        new_date = self.date_selector.get_date() + timedelta(days=1)
        self.date_selector.set_date(new_date)
        self.comic_viewer.find_comic()

    def previous_day(self, event=None):
        new_date = self.date_selector.get_date() - timedelta(days=1)
        self.date_selector.set_date(new_date)
        self.comic_viewer.find_comic()

    def next_week(self, event=None):
        new_date = self.date_selector.get_date() + timedelta(weeks=1)
        self.date_selector.set_date(new_date)
        self.comic_viewer.find_comic()

    def previous_week(self, event=None):
        new_date = self.date_selector.get_date() - timedelta(weeks=1)
        self.date_selector.set_date(new_date)
        self.comic_viewer.find_comic()

    def next_month(self):
        new_date = self.date_selector.get_date() + relativedelta(months=1)
        self.date_selector.set_date(new_date)
        self.comic_viewer.find_comic()

    def previous_month(self):
        new_date = self.date_selector.get_date() - relativedelta(months=1)
        self.date_selector.set_date(new_date)
        self.comic_viewer.find_comic()
