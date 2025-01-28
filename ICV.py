import datetime
import json
import locale
import logging
import os
import time

from DB_classes.DatabaseFactory import DatabaseFactory, FirstSetupRequired
from Parsers.IcvHomeParser import IcvHomeParser
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

    def __init__(self, config):
        self.base_url = "https://www.icv-crew.com/forum/"
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
        self.config = config
        self.logging = logging
        self.initialize_log()
        self.session_handler = SessionHandler()
        self.relevant_boards = self.get_relevant_board()
        self.username = config['Credential']['username']
        self.password = config['Credential']['password']

    def __enter__(self):
        self.connectToDB()
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def initialize_log(self):
        """
        Initialize log file
        :return:
        """
        if not self.config:
            print("Missing configuration")
            exit(1)
        if not self.config.get('Log'):
            print("Missing log settings")
            exit(1)
        filename = os.path.join('Config', self.config['Log'].get('logFile', "icv.log"))
        self.logging.basicConfig(
            filename=filename,
            level=self.config['Log'].get('logLevel', "INFO"),
            format='%(asctime)s %(levelname)-8s %(message)s')
        self.logging.info("ICV Local Indexer - Started")

    def connectToDB(self):
        """
        Connect to backend DB
        :return:
        """
        try:
            return DatabaseFactory.createDatabaseConnection(self.config, self.logging)
        except FirstSetupRequired:
            return DatabaseFactory.requireDatabaseInstallation(self.config, self.logging)


    def login(self):
        """
        Login to the site
        :return: True if the user is logged in
        """
        icv_l = IcvLoginParser(self.session_handler)
        if not icv_l.login(self.username, self.password):
            logging.error("Login fallito")
            raise LoginError("Login fallito")

    def get_board_info(self, board_id, page=1, force_reload=False):
        """
        Get the list of topics from the specified board using cache if available
        Caching only first page
        :param page: The page to extract
        :param board_id: The board ID
        :param force_reload: True to force the reload of the board page
        :return: The list of topics
        """
        if not force_reload and page == 1 and board_id in self.board_info and \
                (datetime.datetime.now() - self.board_info[board_id]["update_time"]).seconds / 3600 < self.minimum_wait_hours:
            print("Using cache")
            self.logging.debug(f"Updating board info [{board_id}] - Using cache")
            pages, updates = self.board_info[board_id]["pages"], self.board_info[board_id]["last_update"]
        else:
            self.logging.info(f"Updating board info [{board_id}] (page #{page})")
            pages, updates = self._get_updates(board_id, page)
        if updates and pages and page == 1:
            self.logging.debug(f"Updating board info - Fetched {len(updates)} updates")
            self.board_info[board_id] = {
                "last_update": updates,
                "pages": pages,
                "update_time": datetime.datetime.now(),
            }
        return updates

    def get_pages(self, board_id):
        """
        Get the number of pages of the board
        :param board_id: The board id
        :return: The number of pages
        """
        if board_id in self.board_info:
            return self.board_info[board_id]["pages"]
        else:
            self.get_board_info(board_id)
            return self.board_info[board_id]["pages"]

    def _get_updates(self, board_id, page):
        """
        Get the list of topics from the specified board
        :param board_id:
        :return:
        """
        icv_b = IcvBoardParser(self.session_handler, board_id, page)
        updates = icv_b.get_updates()
        pages = icv_b.get_pages()
        return pages, updates

    def refresh_all(self):
        """
        Refresh all the boards
        Extract the list of all boards, then for each board extract the new post and
        :return:
        """
        board_list = self.get_boards()
        for board in board_list:
            print(f"Board [{board['id']}]: {board['section']} - {board['name']}")
            if self.required_update_title_list(board['id']):
                print(f"Doing a full update from board {board['id']} - {board['name']}")
                self.get_updates_from_this_board(board)
            # Check updates
            self.analyse_updates(board)

    def required_update_title_list(self, board):
        # Facciamo un full update ogni tot ore per limitare il numero di refresh
        pass

    def get_updates_from_this_board(self, board):
        title_list_ids = self.get_list_title_list(board['id'])
        for title_list in title_list_ids:
            #todo estrarre tutte le info della title list
            pass

    def analyse_updates(self, board):
        """Analyze all the post until it founds no post"""
        available_pages = self.get_pages(board['id'])
        last_posts = self.get_last_posts(board)
        for page in range(1, available_pages):
            new_posts = self.get_new_post_list(board['id'], page)
            for post in new_posts:
                if post["url"] not in last_posts:
                    self.logging.debug(f"The post {post["url"]} - {post["name"]} is new, continuing the analysis")
                    # print(f"The post {post["name"]} is new, continuing the analysis")
                else:
                    self.logging.debug(f"The post {post} is already present, stopping the analysis")
                    print(f"The post {post["url"]} - {post["name"]} is already present, stopping the analysis")
                    return

    def get_list_info(self, list_id):
        """
        Get a rapid list of post from the specified board
        :return: The list of post
        """
        icv_tl = IcvTitleListParser(self.session_handler, list_id)
        title_list = icv_tl.extract_list()
        return title_list

    def get_list_title_list(self, board_id, page):
        """
        Get the list of title list from the specified board
        :param board_id: The board id
        :return: The list of title list
        """
        return self._get_post_this_type("title_list", board_id, page)

    def get_new_post_list(self, board_id, page=1):
        return self._get_post_this_type("post", board_id, page)

    def _get_post_this_type(self, post_type: str, board_id, page) -> list:
        allowed_types = ["post", "title_list", "pinned"]
        post_type = post_type.strip().lower()
        post_list = []
        if post_type in allowed_types:
            board_list = self.get_board_info(board_id, page)
            for topic in board_list:
                if topic["type"] == post_type:
                    post_list.append(topic)
        else:
            self.logging.warning(f"Type {post_type} not allowed")
        return post_list




    def get_post_info(self, post_id, force_thank=False):
        """
        Get the info of the post
        :param post_id: The id of the post
        :return: The info of the post
        """
        try:
            icv_p = IcvPostParser(self.session_handler, post_id)
            info = icv_p.get_info(force_thank)
            self.title_list[post_id] = info["board_id"]
            self.board_info[info["board_id"]] = info
            return info
        except Exception as e:
            print(f"Error: {e} - Cannot extract info from post {post_id}")
            logging.error(f"Error: {e} - Cannot extract info from post {post_id}")
            return None

    def get_boards(self, force_reload=False):
        """
        Get the list of boards
        :return: True if the user is logged in
        """
        extracted_boards = self._extract_boards_from_db()
        if not extracted_boards or force_reload:
            print("Extracting boards")
            extracted_boards = self._update_boards()

        if not self.relevant_boards:
            self.logging.debug("Extracting all boards")
            return extracted_boards
        else:
            relevant_boards_ids = [int(board["id"]) for board in self.relevant_boards]
            return [board for board in extracted_boards if int(board["id"]) in relevant_boards_ids]

    def _update_boards(self):
        # TODO
        icv_h = IcvHomeParser(self.session_handler)
        extracted_boards = icv_h.get_board_list()
        for board in extracted_boards:
            #TODO Aggiungere la board al DB
            print(f"Board: [{board["id"]}] {board["name"]} of section {board["section"]}")
        return extracted_boards

    def _extract_boards_from_db(self):
        """
        Extract the boards from the database
        :return:
        """
        # # TODO
        return []

        # db_boards = self.db_session.query(Board).all()
        # boards = []
        # for board in db_boards:
        #     boards.append({
        #         "id": board.id,
        #         "name": board.board_name,
        #         "section": board.section_name,
        #         "last_modify": board.last_check
        #     })
        # return boards

    def get_relevant_board(self):
        relevant_boards_file = os.path.join("Config", "relevant_boards.json")
        board_list = []
        if os.path.isfile(relevant_boards_file):
            with open(relevant_boards_file, 'r') as f:
                main_boards = json.load(f)
            # Add all the read boards
            for board in main_boards:
                board_list.append(board)
        return board_list

    def get_last_posts(self, board):
        # TODO extract from db the last N post
        return ["177145"]