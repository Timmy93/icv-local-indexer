import logging
import re
from datetime import datetime
from Parsers.IcvParser import IcvParser


class LoginError(Exception):
    pass


class IcvBoardParser(IcvParser):

    def __init__(self, session_handler, board_id):
        super().__init__(session_handler)
        self.board_id = board_id
        self.board_url = f"https://www.icv-crew.com/forum/index.php?board={board_id}.0"

    def get_updates(self):
        # Parse the content and return the board
        self.get_this_page(self.board_url, True)
        if not self.is_user_logged_in():
            print("Utente non loggato")
            logging.error("Utente non loggato")
            raise LoginError("Utente non loggato")
        else:
            return self.extract_list_posts()

    def extract_list_posts(self):
        """
        Extract the list of posts from the page
        :return: The list of posts
        """
        posts = []
        topic_container = self.page.find('div', id='topic_container')
        if topic_container:
            windowbg_divs = topic_container.find_all('div', class_='windowbg')
            for index, div in enumerate(windowbg_divs, start=1):
                line_info = {'id': index}
                self._extract_title(line_info, div)
                self._extract_creation_info(line_info, div)
                self._extract_updates(line_info, div)
                posts.append(line_info)
        return posts

    @staticmethod
    def _extract_title(line_info, div):
        preview_span = div.find('span', class_='preview')
        if preview_span:
            line_info['name'] = preview_span.get_text(strip=True)
            line_info['link'] = preview_span.find('a')['href'] if preview_span.find('a') else None

    @staticmethod
    def _extract_creation_info(line_info, div):
        subtitle = div.find('p', class_='floatleft')
        if subtitle:
            text = subtitle.get_text()
            match = re.search(r"Aperto da (.*?) il (\d{2}) (\w+) (\d{4}), (\d{2}):(\d{2}):(\d{2})", text)
            if match:
                line_info['creator'] = match.group(1)
                day = match.group(2)
                month_name = match.group(3)
                year = match.group(4)
                hour = match.group(5)
                minute = match.group(6)
                second = match.group(7)
                line_info['creation_date'] = datetime.strptime(f"{day} {month_name} {year} {hour}:{minute}:{second}","%d %B %Y %H:%M:%S")
            else:
                print(f"Errore nel parsing della data: {text}")
                logging.warning(f"Errore nel parsing della data: {text}")
        creator_info = subtitle.find('a')
        if creator_info:
            line_info['creator_profile'] = creator_info.get('href')

    @staticmethod
    def _extract_updates(line_info, div):
        div_info = div.find('div', class_='lastpost')
        if div_info:
            last_post_list = div_info.find_all('a')
            if last_post_list:
                text = last_post_list[0].get_text()
                text = text.replace("Oggi alle", datetime.now().strftime("%d %B %Y")+",")
                match = re.search(r"(\d{2}) (\w+) (\d{4}), (\d{2}):(\d{2}):(\d{2})", text)
                if match:
                    day = match.group(1)
                    month_name = match.group(2)
                    year = match.group(3)
                    hour = match.group(4)
                    minute = match.group(5)
                    second = match.group(6)
                    line_info['last_post_date'] = datetime.strptime(f"{day} {month_name} {year} {hour}:{minute}:{second}",
                                                                   "%d %B %Y %H:%M:%S")
            if len(last_post_list) > 1:
                a = last_post_list[1]
                line_info['last_post_name'] = a.get_text()
                line_info['last_post_profile'] = a.get('href')
