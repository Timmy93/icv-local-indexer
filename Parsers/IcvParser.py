import re
from datetime import datetime

from bs4 import BeautifulSoup


class LoginError(Exception):
    pass

class IcvParser:

    home_url = "https://www.icv-crew.com/forum/index.php"

    def __init__(self, session_handler):
        self.session_handler = session_handler
        self.html = None
        self.page_num = 1
        self.page = None

    def _get_page_id(self):
        return (self.page_num - 1) * 20

    def get_this_page(self, page_url, force_reload=False):
        """
        Load the html page if not present
        :param force_reload: True to force the reload of the page
        :param page_url: The url to load
        :return:
        """
        if self.html and not force_reload:
            self.set_html(self.html)
        else:
            self.set_html(self.session_handler.fetch_html(page_url))

    def get_html(self):
        return self.html

    def set_html(self, html):
        self.html = html
        self.page = BeautifulSoup(html, 'html.parser')


    def is_user_logged_in(self, username=None):
        """
        Check if the user is logged in. If the username is provided, check if the correct user is logged.
        """
        self.get_this_page(self.home_url)
        user_element = self.page.find('a', {'id': 'profile_menu_top'})
        if not user_element:
            return False
        elif not username:
            return True
        else:
            return username not in user_element.get_text()


    @staticmethod
    def get_post_id(url):
        if url:
            return url.split('=')[-1].split('.')[0]
        return None

    @staticmethod
    def get_board_id(url):
        return IcvParser.get_post_id(url)

    @staticmethod
    def get_user_id(url):
        if url:
            return url.split('=')[-1]
        return None

    @staticmethod
    def date_parser(date_text):
        """
        Parse the date in the format dd/mm/yyyy
        """
        date = None
        date_text = date_text.replace("Oggi alle", datetime.now().strftime("%d %B %Y") + ",")
        match = re.search(r"(\d{2}) (\w+) (\d{4}), (\d{2}):(\d{2}):(\d{2})", date_text)
        if match:
            day = match.group(1)
            month_name = match.group(2)
            year = match.group(3)
            hour = match.group(4)
            minute = match.group(5)
            second = match.group(6)
            date = datetime.strptime(f"{day} {month_name} {year} {hour}:{minute}:{second}", "%d %B %Y %H:%M:%S")
        return date