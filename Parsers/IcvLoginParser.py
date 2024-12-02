from http.client import responses
from bs4 import BeautifulSoup
from Parsers.IcvParser import IcvParser


class IcvLoginParser(IcvParser):

    login_url = "https://www.icv-crew.com/forum/index.php?action=login2"

    def __init__(self, session_handler):
        super().__init__(session_handler)

    def login(self, username: str, password: str) -> bool:
        if self.is_user_logged_in(username):
            print("Utente già loggato")
            return True
        else:
            return self._login(username, password)

    def _get_hidden_fields(self):
        form_id = "frmLogin"
        form = self.page.find('form', id=form_id)
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

    def _check_login(self, response):
        """
        Check if the login was successful
        :param response: The response from the login request
        :return: True if the login was successful, False otherwise
        """
        if response.status_code != 200:
            print(f"Errore durante il login: {responses[response.status_code]}")
            return False
        else:
            self.html = response.text
            self.page = BeautifulSoup(response.text, 'html.parser')
            if self.is_user_logged_in():
                print("Login effettuato")
                self.session_handler.save_session()
                return True
            else:
                print("Login fallito")
                return False

    def _login(self, username: str, password: str) -> bool:
        """
        Login to the site
        :param username: The username
        :param password: The user password
        :return: The login outcome
        """
        data = {
            "user": username,
            "passwrd": password,
            "cookielength": "3153600"
        }
        for field in self._get_hidden_fields():
            data[field["name"]] = field["value"]
        session = self.session_handler.get_session()
        response = session.post(self.login_url, data=data, allow_redirects=True)
        return self._check_login(response)