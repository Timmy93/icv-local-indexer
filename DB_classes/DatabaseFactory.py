from DB_classes.Database import Database


class FirstSetupRequired(Exception):
    pass


class DatabaseFactory:

    @staticmethod
    def createDatabaseConnection(config, logging):
        try:
            return Database(config['DB'], logging)
        except DBConnectionError:
            logging.error("Cannot use MariaDB - Fix configuration or delete db_host from Config to use SQLite")
            print("Cannot use MariaDB - Fix configuration or delete db_host from Config to use SQLite")
            exit(1)
        except FirstSetupRequired as e:
            logging.warning("First setup required")
            raise e
        except Exception as e:
            logging.error("Unknown error - Delete db_host from Config to use SQLite")
            logging.error(e)
            print("Unknown error - Delete db_host from Config to use SQLite")
            exit(1)

    @staticmethod
    def requireDatabaseInstallation(config, logging):
        print("First setup required - Start installation")
        logging.info("First setup required - Start installation")
        if DatabaseFactory.usingMariaDB(config):
            print("Installing MariaDB")
            logging.info("Installing MariaDB")
            db = Database(config['DB'], logging, skip_installation_check=True)
            data = []
            if DatabaseFactory.migrationFromSQLitePossible(config):
                data = DatabaseFactory.getDataFromSQLite(config, logging)
            if not db.install(data):
                print("Cannot create db - Abort installation")
                logging.error("Cannot create db - Abort installation")
                raise Exception("Cannot install MariaDB")
            print("MariaDB installation - Completed")
            logging.info("MariaDB installation - Completed")
            return Database(config['DB'], logging)
        else:
            print("Unexpected DB installation required")
            logging.error("Unexpected DB installation required")
            raise Exception("Unexpected DB installation required")
