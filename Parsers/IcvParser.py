from bs4 import BeautifulSoup


class IcvParser:

    home_url = "https://www.icv-crew.com/forum/"

    def __init__(self, session_handler):
        self.session_handler = session_handler
        self.html = None
        self.page = None

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
