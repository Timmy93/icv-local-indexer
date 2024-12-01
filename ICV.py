import logging
import os
import pickle
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests import session


class ICV:

    session_file = os.path.join('Config', 'session_file')

    def __init__(self, session=None):
        self.username = None
        self.user_id = None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
        self.base_url = "https://www.icv-crew.com/forum/"
        self.session = session
        self.session = self._get_session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
        })
        self.soup = BeautifulSoup(self._fetch_html(self.base_url), 'html.parser')

    def restore_session(self):
        try:
            with open(self.session_file, "rb") as file:
                self.session.cookies.update(pickle.load(file))
            print("Sessione ripristinata")
        except FileNotFoundError:
            print("File sessione non trovato")
        except Exception as e:
            print(f"Errore durante il ripristino della sessione: {e}")
        raise Exception("Sessione non ripristinata")

    def _create_session(self):
        print("Creating session")
        self.session = requests.Session()

    def _get_session(self):
        if not self.session:
            self._create_session()
        return self.session

    def login(self, username, password):
        self._get_session()
        self.username = username
        login_url = self.base_url + "index.php?action=login2"
        data = {
            "user": username,
            "passwrd": password,
            "cookielength": "3153600"
        }
        for field in self._get_hidden_fields():
            data[field["name"]] = field["value"]
        self.session.post(login_url, data=data, allow_redirects=True)
        print("Login effettuato")
        self._save_session()

    def _get_hidden_fields(self):
        form_id = "frmLogin"
        form = self.soup.find('form', id=form_id)
        if not form:
            raise ValueError(f"Form con id '{form_id}' non trovato.")

        hidden_fields = []
        # Cerca tutti gli input di tipo hidden all'interno del form
        for hidden_input in form.find_all('input', type='hidden'):
            name = hidden_input.get('name')  # Estrai l'attributo name
            value = hidden_input.get('value', '')  # Estrai il valore (default '')

            if name:  # Aggiungi solo se ha un name valido
                hidden_fields.append({'name': name, 'value': value})

        return hidden_fields


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

    def is_user_logged_in(self, username):
        """
        Verifica se l'utente specificato è loggato.
        Cerca il nome utente nel contenuto HTML.
        """
        user_element = self.soup.find('a', {'id': 'profile_menu_top'})
        if user_element and username in user_element.get_text():
            return True
        return False

    def is_thank_button_clicked(self):
        """
        Verifica se il pulsante "Ringrazia" è presente.
        Controlla se è visibile l'elemento <span class="saythanks_label">Ringrazia</span>.
        """
        thank_button = self.soup.find('span', {'class': 'saythanks_label'}, string="Ringrazia")
        return not thank_button

    def _get_url(self, url):
        self._get_session()
        try:
            response = self.session.get(url)
            response.raise_for_status()  # Controlla eventuali errori HTTP
            return response.text
        except requests.RequestException as e:
            print(f"Errore durante il download della pagina HTML: {e}")
            return None

    def get_last_updates(self, board_id):
        """
        Get the list of topics from the specified board
        :param board_id: The board ID
        :return: The list of topics
        """
        board_url = self.base_url + f"index.php?board={board_id}.0"
        html = self._get_url(board_url)
        return self.extract_list_posts(html)

    def extract_list_posts(self, html):
        """
        Estrae la lista dei post dal contenuto HTML
        :param html: Il contenuto HTML
        :return: La lista dei post
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        topic_container = soup.find('div', id='topic_container')
        if topic_container:
            windowbg_divs = topic_container.find_all('div', class_='windowbg')
            for index, div in enumerate(windowbg_divs, start=1):
                line_info = {'id': index}
                self._extract_title(line_info, div)
                self._extract_creation_info(line_info, div)
                self._extract_updates(line_info, div)
                posts.append(line_info)
        return posts

    def _extract_title(self, line_info, div):
        preview_span = div.find('span', class_='preview')
        if preview_span:
            line_info['name'] = preview_span.get_text(strip=True)
            line_info['link'] = preview_span.find('a')['href'] if preview_span.find('a') else None

    def _extract_creation_info(self, line_info, div):
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

    def _extract_updates(self, line_info, div):
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

    def _fetch_html(self, url):
        """
        The HTML content from the specified URL
        :param url: The URL to fetch
        :return: The HTML content as string
        """
        session = self._get_session()
        try:
            response = session.get(url)
            response.raise_for_status()  # Controlla eventuali errori HTTP
            return response.text
        except requests.RequestException as e:
            print(f"Errore durante il download della pagina HTML: {e}")
            return None

    def _save_session(self):
        with open(self.session_file, "wb") as file:
            pickle.dump(self.session, file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Salvo la sessione")
        self._save_session()

