import json
import os.path
import time
import tomllib
import logging
from ICV import ICV

def load_settings(file: str, mandatory_file=False):
    """
    Load setting from toml file
    :return:
    """
    try:
        path = os.path.join('Config', file)
        # return toml.load(path)
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        logging.error(f"Missing setting file: {file}")
        print(f"Missing setting file: {file}")
        if mandatory_file:
            logging.error(f"Stopping icv_indexer")
            print(f"Stopping icv_indexer")
            exit(1)

def main():
    config = load_settings('config.toml', mandatory_file=True)
    analyzer = ICV(config)
    board_id = "9"
    title_list_id = "45246"
    post_ids = ["135245", "198538", "111972"]
    main_boards = None

    try:
        with analyzer as a:
            print("Starting")
            boards = a.refresh_all()
            print(f"Boards found: {len(boards)}")
            exit()
            # execution_time = time.time() - start_time
            # start_time = time.time()
            # print(f"Post retrival in: {execution_time} seconds")
            # print("---------------------")
            # list_info = a.get_list_info(title_list_id)
            # execution_time = time.time() - start_time
            # start_time = time.time()
            # print(f"Extracted a list of {len(list_info)} retrival time: {execution_time} seconds")
            # print("---------------------")

            #Estrai le info --> get_info
        #     for post_id in post_ids:
        #         start_time = time.time()
        #         post_info = a.get_post_info(post_id)
        #         print(f"Post info: {post_info}")
        #         print(f"Extracted post info in: {time.time() - start_time} seconds")
        #         print("---------------------")
    except ValueError as e:
        print(f"Errore: {e}")
        logging.error(f"Errore: {e}")
        exit(1)

if __name__ == "__main__":
    main()