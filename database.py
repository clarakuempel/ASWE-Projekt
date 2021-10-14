class DatabaseConnector:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if DatabaseConnector.__instance is None:
            DatabaseConnector()
        return DatabaseConnector.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if DatabaseConnector.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DatabaseConnector.__instance = self
