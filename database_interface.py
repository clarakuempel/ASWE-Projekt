import abc


class DBInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def store_prefs(self, user_id: str, preferences: dict) -> None:
        """
        Save the preferences associated with a user by user_id

        :param user_id: unique user id
        :param preferences: document to be stored
        :return: None
        """
        pass

    @abc.abstractmethod
    def load_prefs(self, user_id: str) -> dict:
        """
        Queries the preferences of a user with the id user_id

        :param user_id: unique user id
        :return: object with all properties
        """
        pass

    @abc.abstractmethod
    def store_habits(self, user_id: str, habits: dict) -> None:
        """
        Save the habits associated with a user by user_id
        :param user_id: unique user id
        :param habits: document to be stored
        :return: None
        """
        pass

    @abc.abstractmethod
    def load_habits(self, user_id: str) -> dict:
        """
        Queries the habits of a user with the id user_id

        :param user_id: unique user id
        :return: object with all properties
        """
        pass
