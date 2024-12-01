import locale
import os.path
import tomllib

import logging
from datetime import datetime

from ICV import ICV


def fetch_html_from_file(path):
    """
    Legge il contenuto HTML da un file locale.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File non trovato: {path}")
    except Exception as e:
        print(f"Errore durante la lettura del file: {e}")
    return None

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

analyzer = ICV()
try:
    analyzer.restore_session()
except Exception as e:
    analyzer.login(
        config['Credential']['username'],
        config['Credential']['password']
    )
posts = analyzer.get_last_updates("9")
print(posts)
