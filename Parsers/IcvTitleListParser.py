import time

from Parsers.IcvParser import IcvParser, LoginError


class IcvTitleListParser(IcvParser):

    title_list = []
    # The url of the post
    post_url = None

    def __init__(self, session_handler, post_id):
        super().__init__(session_handler)
        self.topic_id = post_id
        self._change_page(self.page_num)

    def _change_page(self, new_page):
        self.page = new_page
        self.post_url = f"https://www.icv-crew.com/forum/index.php?topic={self.topic_id}.{self._get_page_id()}"

    def extract_list(self):
        start_time = time.time()
        self.get_this_page(self.post_url, True)
        print(f"\t\tPagina caricata in {time.time() - start_time} secondi")
        if not self.is_user_logged_in():
            print("Utente non loggato")
            raise LoginError("Utente non loggato")
        else:
            return self._extract_list_titles()

    def _extract_list_titles(self):
        """
        Extract the list of titles from the page
        :return: The list of titles
        """
        titles = []
        start_time = time.time()
        for title in self.page.find_all('li', class_='windowbg'):
            info = {}
            self._extract_info(title, info)
            titles.append(info)
        print(f"\t\tEstratti {len(titles)} titoli in {time.time() - start_time} secondi")
        return titles

    @staticmethod
    def _extract_info(section, info):
        section = section.find('a')
        if section:
            info['title'] = section.get_text()
            # info['url'] = section.get('href')
            info['id'] = IcvParser.get_post_id(section.get('href'))
            #
            # print(f"ID: {info['id']} - Titolo: {info['title']}")
            # if random.random() < 0.2:
            #     print("Uscita con probabilità del 20%")
            #     exit()


