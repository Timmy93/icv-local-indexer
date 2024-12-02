import locale
import os.path
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
try:
    posts = analyzer.get_last_updates("9")
    print(posts)
except ValueError as e:
    print(f"Errore: {e}")
    logging.error(f"Errore: {e}")
    exit(1)
