import logging
import re
from datetime import datetime
from Parsers.IcvParser import IcvParser, LoginError


class IcvBoardParser(IcvParser):

    page_num = 1
    board_url = None
    results = []
    pages = None

    def __init__(self, session_handler, board_id, page=1):
        super().__init__(session_handler)
        self.board_id = board_id
        self._change_page(page)

    def _change_page(self, new_page):
        self.page_num = new_page
        self.board_url = f"https://www.icv-crew.com/forum/index.php?board={self.board_id}.{self._get_page_id()}"

    def get_updates(self, page=None):
        # Parse the content and return the board
        if page:
            self._change_page(page)
        self.get_this_page(self.board_url, True)
        if not self.is_user_logged_in():
            print("Utente non loggato")
            logging.error("Utente non loggato")
            raise LoginError("Utente non loggato")
        else:
            self.pages = self._count_pages()
            self.results = self.extract_list_posts()
            return self.results

    def get_pages(self):
        if not self.pages:
            self.get_updates()
        return self.pages

    def _count_pages(self):
        page_div = self.page.find('div', class_='pagesection')
        if page_div:
            pages = page_div.find_all('a', class_='nav_page')
            if pages:
                return int(pages[-2].get_text())
        return 1

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
                self._extract_type(line_info, div)
                self._extract_title(line_info, div)
                self._extract_creation_info(line_info, div)
                self._extract_updates(line_info, div)
                posts.append(line_info)
        return posts

    @staticmethod
    def _extract_type(line_info, div):
        if 'sticky' in div.get('class', []) or 'locked' in div.get('class', []):
            line_info['type'] = 'pinned'

    @staticmethod
    def _extract_title(line_info, div):
        preview_span = div.find('span', class_='preview')
        if preview_span:
            title_text = preview_span.get_text(strip=True)
            line_info['name'] = title_text
            line_info['url'] = IcvParser.get_post_id(preview_span.find('a')['href']) if preview_span.find('a') else None
            if title_text.startswith("LISTA TITOLI"):
                line_info['type'] = 'title_list'
            elif "type" not in line_info:
                line_info['type'] = 'post'

    @staticmethod
    def _extract_creation_info(line_info, div):
        subtitle = div.find('p', class_='floatleft')
        if subtitle:
            text = subtitle.get_text()
            match = re.search(r"Aperto da (.*?)(?: il)? (.*)", text)
            if match:
                line_info['creator'] = match.group(1)
                line_info['creation_date'] = IcvParser.date_parser(match.group(2))
            else:
                print(f"Errore nel parsing della data: {text}")
                logging.warning(f"Errore nel parsing della data: {text}")
        creator_info = subtitle.find('a')
        if creator_info:
            line_info['creator_profile'] = IcvParser.get_user_id(creator_info.get('href'))

    @staticmethod
    def _extract_updates(line_info, div):
        div_info = div.find('div', class_='lastpost')
        if div_info:
            last_post_list = div_info.find_all('a')
            if last_post_list:
                text = last_post_list[0].get_text()
                line_info['last_post_date'] = IcvParser.date_parser(text)
            if len(last_post_list) > 1:
                a = last_post_list[1]
                line_info['last_post_name'] = a.get_text()
                line_info['last_post_profile'] = IcvParser.get_user_id(a.get('href'))

