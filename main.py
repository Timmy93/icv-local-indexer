import locale
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


config = load_settings('config.toml', mandatory_file=True)
locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
online = True

analyzer = ICV(
    config['Credential']['username'],
    config['Credential']['password']
)
board_id = "9"
title_list_id = "45246"
post_id = "135245"

try:
    # start_time = time.time()
    # title_list_ids = analyzer.get_list_title_list(board_id)
    # posts = analyzer.get_last_updates(board_id)
    # print(f"Extracted {len(posts)} updates - Found {len(title_list_ids)} title lists")
    # execution_time = time.time() - start_time
    # start_time = time.time()
    # print(f"Post retrival in: {execution_time} seconds")
    # print("---------------------")
    # list_info = analyzer.get_list_info(title_list_id)
    # execution_time = time.time() - start_time
    # start_time = time.time()
    # print(f"Extracted a list of {len(list_info)} retrival time: {execution_time} seconds")
    # print("---------------------")
    #Estrai le info --> get_info
    start_time = time.time()
    post_info = analyzer.get_post_info(post_id)
    print(f"Post info: {post_info}")
    print(f"Extracted post info in: {time.time() - start_time} seconds")
    print("---------------------")
except ValueError as e:
    print(f"Errore: {e}")
    logging.error(f"Errore: {e}")
    exit(1)
