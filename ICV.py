import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup

from Parsers.IcvBoardParser import IcvBoardParser, LoginError
from Parsers.IcvLoginParser import IcvLoginParser
from SessionHandler import SessionHandler


class ICV:

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

    def get_last_updates(self, board_id):
        """
        Get the list of topics from the specified board
        :param board_id: The board ID
        :return: The list of topics
        """
        icv_b = IcvBoardParser(self.session_handler, board_id)
        updates = []
        try:
            updates = icv_b.get_updates()
        except LoginError:
            icv_l = IcvLoginParser(self.session_handler)
            # Reuse the loaded html
            icv_l.set_html(icv_b.get_html())
            if icv_l.login(self.username, self.password):
                updates = icv_b.get_updates()
            else:
                logging.error("Login fallito")
                return updates
        return updates

