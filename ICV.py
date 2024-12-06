import datetime
import logging

from Parsers.IcvBoardParser import IcvBoardParser
from Parsers.IcvLoginParser import IcvLoginParser
from Parsers.IcvParser import LoginError
from Parsers.IcvPostParser import IcvPostParser
from Parsers.IcvTitleListParser import IcvTitleListParser
from SessionHandler import SessionHandler


class ICV:
    # La lista di tutte le board [board_id] -> {last_update, pages, update_time}
    board_info = {}
    # La lista di tutti i titoli [post_id] -> {board_id}
    title_list = {}
    minimum_wait_hours = 6

    def __init__(self, username, password):
        self.base_url = "https://www.icv-crew.com/forum/"
        self.session_handler = SessionHandler()
        self.username = username
        self.password = password

    def get_last_updates(self, board_id, force_reload=False):
        """
        Get the list of topics from the specified board using cache if available
        :param board_id: The board ID
        :param force_reload: True to force the reload of the board page
        :return: The list of topics
        """
        if not force_reload and board_id in self.board_info and \
                (datetime.datetime.now() - self.board_info[board_id]["update_time"]).seconds / 3600 < self.minimum_wait_hours:
            print("Using cache")
            pages, updates = self.board_info[board_id]["pages"], self.board_info[board_id]["last_update"]
        else:
            pages, updates = self._get_updates(board_id)
        if updates and pages:
            self.board_info[board_id] = {
                "last_update": updates,
                "pages": pages,
                "update_time": datetime.datetime.now(),
            }
        return updates

    def _get_updates(self, board_id):
        """
        Get the list of topics from the specified board
        :param board_id:
        :return:
        """
        icv_b = IcvBoardParser(self.session_handler, board_id)
        updates = []
        pages = 0
        try:
            updates = icv_b.get_updates()
            pages = icv_b.get_pages()
        except LoginError:
            icv_l = IcvLoginParser(self.session_handler)
            # Reuse the loaded html
            icv_l.set_html(icv_b.get_html())
            if icv_l.login(self.username, self.password):
                updates = icv_b.get_updates()
                pages = icv_b.get_pages()
            else:
                logging.error("Login fallito")
        return pages, updates

    def get_list_info(self, list_id):
        """
        Get a rapid list of post from the specified board
        :return: The list of post
        """
        icv_tl = IcvTitleListParser(self.session_handler, list_id)
        title_list = icv_tl.extract_list()
        return title_list

    def get_post_info(self, post_id):
        """
        Get the info of the post
        :param post_id: The id of the post
        :return: The info of the post
        """
        try:
            icv_p = IcvPostParser(self.session_handler, post_id)
            info = icv_p.get_info()
            self.title_list[post_id] = info["board_id"]
            self.board_info[info["board_id"]] = info
            return info
        except Exception as e:
            print(f"Error: {e} - Cannot extract info from post {post_id}")
            logging.error(f"Error: {e} - Cannot extract info from post {post_id}")
            return None

