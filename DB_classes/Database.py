
class DBConnectionError(Exception):
    pass

class Database:

    def __init__(self, config, log, skip_installation=False):
        self.config = config
        self.logging = log
        if not skip_installation:
            print("First setup required - Start installation")
            #TODO
            self.install()

    def install(self):
        print("Installing MariaDB")
        self.logging.info("Installing MariaDB")
        #TODO
        print("MariaDB installation - Completed")
        self.logging.info("MariaDB installation - Completed")