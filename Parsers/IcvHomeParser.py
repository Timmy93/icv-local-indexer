from Parsers.IcvParser import IcvParser


class IcvHomeParser(IcvParser):

    def __init__(self, session_handler):
        super().__init__(session_handler)
        self.home_url = "https://www.icv-crew.com/forum/index.php"
        self.get_this_page(self.home_url)

    def get_board_list(self):
        """
        Get the list of boards from the home page
        :return:
        """
        board_list = []
        for container in self.page.find_all('div', class_='main_container'):
            board_section = container.find('h3', class_='catbg')
            section_name = board_section.get_text().strip() if board_section else ""
            for board in container.find_all('a', class_='mobile_subject'):
                board_info = {
                    'section': section_name,
                    'name': board.get_text().strip(),
                    'id': self.get_board_id(board['href']),
                }
                board_list.append(board_info)
        return board_list

