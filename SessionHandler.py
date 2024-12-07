import logging
import os
import pickle
import time

import requests


class SessionHandler:

    session_file = os.path.join('Config', 'session_file')
    last_request = None
    minimum_pause = 1.5

    def __init__(self):
        self.session = requests.Session()
        self._setup_session()

    def get_session(self):
        return self.session

    def fetch_html(self, url, is_json=False):
        """
        The HTML content from the specified URL
        :param url: The URL to fetch
        :return: The HTML content as string
        """
        if self.last_request and time.time() - self.last_request < self.minimum_pause:
            print("Waiting...")
            time.sleep(self.minimum_pause - (time.time() - self.last_request))
        self.last_request = time.time()
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            if not is_json:
                return response.text
            else:
                return response.json()
        except requests.RequestException as e:
            print(f"Cannot retrieve the HTML page: {e}")
            logging.warning(f"Cannot retrieve the HTML page: {e}")
            return None

    def _setup_session(self):
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept-Encoding": "gzip, deflate, br",
        })
        self._restore_session()

    def _restore_session(self):
        """Restores a previous session from a file"""
        try:
            with open(self.session_file, "rb") as file:
                self.session.cookies.update(pickle.load(file))
            print("Sessione ripristinata")
            logging.info("Sessione ripristinata")
        except FileNotFoundError:
            logging.info("File sessione non trovato")
        except Exception as e:
            logging.info(f"Errore durante il ripristino della sessione: {e}")

    def save_session(self):
        """
        Stores the session in a file
        :return:
        """
        with open(self.session_file, "wb") as file:
            # noinspection PyTypeChecker
            pickle.dump(self.session.cookies, file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Salvo la sessione")
        self.save_session()