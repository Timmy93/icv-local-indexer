import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

from AvinapticParser import AvinapticParser
from Parsers.IcvParser import IcvParser, LoginError


class IcvPostParser(IcvParser):

    # The list of all messages
    messages = []
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
                message = self.messages[0]
                post_info = {
                    'id': self.topic_id,
                    'message_id': self._get_msg_id(message),
                }
                self._extract_board_info(post_info)
                self._extract_lateral_bar(message, post_info)
                self._extract_info(message, post_info)
                self._search_report(message, post_info)
                self._search_magnet(message, post_info)
                return post_info
        else:
            return None

    def _extract_board_info(self, post_info):
        board_info = self.page.find('div', class_='navigate_section')
        if board_info:
            sections = board_info.find_all('li')
            if sections and len(sections) > 2:
                post_info['board'] = sections[-2].find('a').get_text()
                post_info['board_id'] = IcvParser.get_board_id(sections[-2].find('a')['href'])

    @staticmethod
    def _extract_lateral_bar(message, post_info):
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

    def _search_report(self, message, post_info):
        report_div = message.find(lambda tag: tag.name == 'details' and r"Info sul file" in tag.get_text())
        if report_div:
            spoiler_content = report_div.find('div', class_='spoiler_content')
            if spoiler_content:
                for br in spoiler_content.find_all("br"):
                    br.replace_with("\n")
                post_info['report'] = spoiler_content.get_text(strip=True, separator = '\n',)
            else:
                post_info['report'] = report_div.get_text(strip=True)
        else:
            post_info['report'] = None
            print("No report found")
        if post_info['report']:
            ap = AvinapticParser(post_info['report'])
            post_info['report'] = ap.get_summary()

    def _search_magnet(self, message, post_info):
        """
        Extract the magnet links from the first message of this post
        :param message:
        :param post_info:
        :return:
        """
        if not self.is_thank_button_clicked(message):
            self.thank_and_get_magnet(post_info)
        else:
            self.get_magnet_already_thanked(message, post_info)


    def thank_and_get_magnet(self, post_info):
        """
        Send the thanks request and get the magnet link from the response
        :param post_info: The dictionary where to store the information
        :return: The magnet link as list of objects
        """
        button_url = self.home_url + f"?action=thank;msg={post_info['message_id']};member={post_info['creator_profile']};topic={post_info['id']};refresh=1;ajax=1;xml=1"
        response = self.session_handler.fetch_html(button_url, is_json=True)
        if response['result'] == 'success':
            refresh_html = response['refresh']
            refreshed_page = BeautifulSoup(refresh_html, 'html.parser')
            self.get_magnet_already_thanked(refreshed_page, post_info)
            print(f"Post: {post_info['title']} - Message: {post_info['message_id']} of {post_info['creator']} thanked")
        else:
            post_info['magnet_links'] = []
            print(f"Error thanking message post {post_info['title']}")
            logging.error(f"Error thanking message post {post_info['title']}")
            raise Exception(f"Error thanking message post {post_info['title']}")

    def get_magnet_already_thanked(self, message, post_info):
        """
         Search all the <a> elements and get the href attribute if is a magnet link
        :param message: The html code of the message
        :param post_info: The dictionary where to store the information
        :return: The magnet link as list of objects
        """
        # Search all the a elements and get the href attribute if it starts with "magnet:"
        magnet_links_a = message.find_all('a', href=re.compile(r'^magnet:'))
        post_info['magnet_links'] = []
        for a in magnet_links_a:
            magnet_info = {
                'text': a.get_text(),
                'href': a.get('href')
            }
            post_info['magnet_links'].append(magnet_info)
        print(f"Found {len(post_info['magnet_links'])} magnet links")

    def is_thank_button_clicked(self, message):
        """
        Verifica se il pulsante "Ringrazia" è presente.
        Controlla se è visibile l'elemento <span class="saythanks_label">Ringrazia</span>.
        """
        thank_button = message.find('span', {'class': 'saythanks_label'}, string="Ringrazia")
        return not thank_button

    def _get_msg_id(self, message):
        if not message:
            return None
        else:
            return int(message['id'].split('msg')[-1]) if message and 'id' in message.attrs else None
