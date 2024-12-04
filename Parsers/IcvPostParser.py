import re
import time

import logging
from datetime import datetime

from Parsers.IcvParser import IcvParser, LoginError


class IcvPostParser(IcvParser):

    # The list of all messages
    messages = []
    # True if magnet from first message are visible
    already_thanked = False
    # The url of the post
    post_url = None

    def __init__(self, session_handler, post_id):
        super().__init__(session_handler)
        self.topic_id = post_id
        self._change_page(self.page_num)

    def _change_page(self, new_page):
        self.page = new_page
        self.post_url = f"https://www.icv-crew.com/forum/index.php?topic={self.topic_id}.{self._get_page_id()}"

    def get_info(self):
        self.get_this_page(self.post_url, True)
        if not self.is_user_logged_in():
            print("Utente non loggato")
            logging.error("Utente non loggato")
            raise LoginError("Utente non loggato")
        else:
            return self.extract_post_info()

    def extract_post_info(self):
        post = self.page.find('div', id='forumposts')
        if post:
            self.messages = self._extract_messages(post)
            if self.messages:
                # Get info only from first message
                post_info = {}
                message = self.messages[0]
                self._extract_lateral_bar(message, post_info)
                self._extract_info(message, post_info)
                return post_info
        else:
            return None

    def _extract_lateral_bar(self, message, post_info):
        lateral_bar = message.find('div', class_='poster')
        if lateral_bar:
            post_info['creator'] = lateral_bar.find('h4').find_all('a')[-1].get_text()
            post_info['creator_profile'] = IcvParser.get_user_id(lateral_bar.find('h4').find_all('a')[-1]['href'])

    @staticmethod
    def _extract_info(message, post_info):
        """
        Extract the information from the first message of this post
        :param message: The html code of the message
        :param post_info: The dictionary where to store the information
        :return:
        """
        post_info['date'] = IcvParser.date_parser(message.find('a', class_='smalltext').get_text())
        post_info['title'] = message.find('a', class_='smalltext')['title']
        modified_span = message.find('span', class_='modified')
        if modified_span:
            modify_date = modified_span.get_text()
            modify_date = modify_date.replace("Oggi alle", datetime.now().strftime("%d %B %Y")+",")
            match = re.search(r"Ultima modifica: (.*? \d+:\d+:\d+) di (.*)", modify_date)
            if match:
                post_info['last_modified'] = IcvParser.date_parser(match.group(1))
                post_info['last_modified_by'] = match.group(2)

    def _extract_messages(self, post):
        return post.find_all('div', class_='windowbg')