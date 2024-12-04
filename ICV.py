import datetime
import logging
import time

from Parsers.IcvBoardParser import IcvBoardParser
from Parsers.IcvLoginParser import IcvLoginParser
from Parsers.IcvParser import LoginError
from Parsers.IcvPostParser import IcvPostParser
from Parsers.IcvTitleListParser import IcvTitleListParser
from SessionHandler import SessionHandler


class ICV:

    board_info = {}
    title_list = {}
    minimum_wait_hours = 6

    def __init__(self, username, password):
        self.base_url = "https://www.icv-crew.com/forum/"
        self.session_handler = SessionHandler()
        self.username = username
        self.password = password

    def get_updates_on_this_section(self, section_id):
        pass

    def _get_topic(self, topic_id):
        topic_url = self.base_url + "index.php?topic=" + str(topic_id)
        return self._get_url(topic_url)

    def get_magnet(self, topic_id):
        topic_html = self._get_topic(topic_id)
        message_html, message_id, member_id = self.extract_first_post(topic_html)
        if self.is_thank_button_clicked():
            magnet = self.get_magnet_already_thanked(topic_html)
        else:
            magnet = self.thank_and_get_magnet(topic_id, message_id, member_id)

    def thank_and_get_magnet(self, topic_id, message_id, member_id):
        """
        Send the thanks request and get the magnet link from the response
        :param topic_id: The topic where there is the message to thank
        :param message_id: The message to thank
        :param member_id: The user that send the message
        :return: The magnet link as list of objects
        """
        button_url = self.base_url + f"action=thank;msg={message_id};member={member_id};topic={topic_id};refresh=1;ajax=1;xml=1"

    def get_magnet_already_thanked(self):
        pass

    def is_thank_button_clicked(self):
        """
        Verifica se il pulsante "Ringrazia" è presente.
        Controlla se è visibile l'elemento <span class="saythanks_label">Ringrazia</span>.
        """
        thank_button = self.soup.find('span', {'class': 'saythanks_label'}, string="Ringrazia")
        return not thank_button

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

    def parse_list_info(self, post_id):
        """
        Extract the list info from the specified post id
        :param post_id: The id of the title list post
        :return:
        """
        icv_tl = IcvTitleListParser(self.session_handler, post_id)
        for update in updates:
            if update["type"] == "title_list":
                if update["id"] not in self.title_list:
                    self.title_list[update["id"]] = {
                        "board_id": update["board_id"],
                        "list": [],
                        "last_update": None,
                    }

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

    def get_list_title_list(self, board_id):
        """
        Get the list of title list from the specified board
        :param board_id: The board id
        :return: The list of title list
        """
        title_list_id = []
        update_list = self.get_last_updates(board_id)
        for topic in update_list:
            if topic["type"] == "title_list":
                title_list_id.append(topic["id"])
        return title_list_id

    def get_post_info(self, post_id):
        """
        Get the info of the post
        :param post_id: The id of the post
        :return: The info of the post
        """
        icv_p = IcvPostParser(self.session_handler, post_id)
        return icv_p.get_info()