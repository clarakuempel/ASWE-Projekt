import abc
import os

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibmcloudant.cloudant_v1 import CloudantV1
from typing import Final

from database_interface import DBInterface

_DB_NAME_PREFS: Final = 'preferences'
_DB_NAME_HABITS: Final = 'habits'
_EXCEPTION_CONNECT: Final = Exception("Call connect() first")


class Database(DBInterface, abc.ABC):
    """
    Singleton for Database
    Uses Cloudant
    Prerequisites:
        .env config in the form of:
            APIKey = "example API Key"
            URL = "example URL"
    Usage:
        - Generate, i.e., get singleton object with <class-name>.get_instance()
        - call initialize() to connect to the database and prepare it (consists of connect() and create_dbs())
        - Use the methods defined in the interface to save and load data.
    """
    __instance = None  # static singleton instance
    __service = None  # Cloudant service

    @classmethod
    def get_instance(cls) -> 'Database':
        """
        Method to access singleton-instance. Creates instance if not exists.
        :return: Singleton of database-connector
        """
        if cls.__instance is None:
            cls()
        return cls.__instance

    @staticmethod
    def _api_error_handler(ae) -> None:
        """
        Handles Cloudant API errors
        :param ae: ApiException object
        :return: None
        """
        print("Method failed")
        print(" - status code: " + str(ae.code))
        print(" - error message: " + ae.message)
        if "reason" in ae.http_response.json():
            print(" - reason: " + ae.http_response.json()["reason"])
        raise ae

    @staticmethod
    def _doc_key(user_id: str) -> str:
        """
        Converter user_id to key for Cloudant
        :param user_id: User id
        :return: Key for Cloudant-entry
        """
        return ":" + user_id

    def _fetch(self, user_id: str, db: str) -> dict:
        """
        Queries db of a user with the id user_id

        :param user_id: unique user id
        :return: object with all properties or None if document doesn't exist
        """
        if self.__service is None:
            raise _EXCEPTION_CONNECT
        try:
            return self.__service.get_document(
                db=db,
                doc_id=self._doc_key(user_id)
            ).get_result()
        except ApiException as ae:
            if ae.code == 404:
                return None
            self._api_error_handler(ae)

    def _store(self, user_id: str, data: dict, db: str) -> None:
        """
        Save a document associated with a user by user_id

        :param user_id: unique user id
        :param data: document to be stored
        :param db: database to use
        :return: None
        """
        if self.__service is None:
            raise _EXCEPTION_CONNECT
        doc = dict()
        doc.update({'_id': self._doc_key(user_id)})
        doc.update(data)

        try:
            old_doc = self._fetch(user_id, db)
            response = self.__service.put_document(db=db,
                                                   doc_id=self._doc_key(user_id),
                                                   document=doc,
                                                   ) \
                .get_result() \
                if old_doc is None else \
                self.__service.put_document(db=db,
                                            doc_id=self._doc_key(user_id),
                                            document=doc,
                                            rev=old_doc['_rev']
                                            ) \
                    .get_result()
        except ApiException as ae:
            self._api_error_handler(ae)
            return
        if not response['ok']:
            raise Exception("Error while posting document")

    def __init__(self):
        """
        'Private' constructor.
        Throws exception if singleton-instance already exists.
        """
        if self.__class__.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__class__.__instance = self

    def initialize(self) -> None:
        """
        Pipeline for setting up database
        1. connect
        2. create databases if not exist

        :return: None
        """
        self.connect()
        self.create_dbs()

    def connect(self) -> None:
        """
        Connects to IBM Cloudant via IAMAuthenticator
        Based on API-Key and URL defined in .env file

        :return: None
        """
        authenticator = IAMAuthenticator(os.environ.get("DB_API_KEY"))
        authenticator.set_disable_ssl_verification(True)
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(os.environ.get("DB_URL"))
        service.set_disable_ssl_verification(True)
        self.__service = service

    def create_dbs(self) -> None:
        """
        Creates all databases.

        :return: None
        """
        if self.__service is None:
            raise _EXCEPTION_CONNECT
        try:
            try:
                response = self.__service \
                    .put_database(db=_DB_NAME_PREFS).get_result()
                if not response['ok']:
                    raise Exception("Error while creation of database: " + _DB_NAME_PREFS)
            except ApiException as ae:
                if ae.code == 412 and ae.message == "file_exists":
                    # DB already exists
                    pass
                else:
                    raise ae
            try:
                response = self.__service \
                    .put_database(db=_DB_NAME_HABITS).get_result()
                if not response['ok']:
                    raise Exception("Error while creation of database: " + _DB_NAME_HABITS)
            except ApiException as ae:
                if ae.code == 412 and ae.message == "file_exists":
                    # DB already exists
                    pass
                else:
                    raise ae
        except ApiException as ae:
            self._api_error_handler(ae)
            return

    def store_prefs(self, user_id: str, preferences: dict) -> None:
        """
        Save the preferences associated with a user by user_id

        :param user_id: unique user id
        :param preferences: document to be stored
        :return: None
        """
        return self._store(user_id, preferences, _DB_NAME_PREFS)

    def load_prefs(self, user_id: str) -> dict:
        """
        Invokes query to database and processes response.

        :param user_id: unique user id
        :return: object with all properties or None if document not found
        """

        prefs = self._fetch(user_id, _DB_NAME_PREFS)
        if prefs is None:
            return None
        del prefs['_id']
        del prefs['_rev']
        return prefs

    def store_habits(self, user_id: str, habits: object) -> None:
        """
        Save the habits associated with a user by user_id
        :param user_id: unique user id
        :param habits: document to be stored
        :return: None
        """
        return self._store(user_id, habits, _DB_NAME_HABITS)

    def load_habits(self, user_id: str) -> object:
        """
        Invokes query to database and processes response.

        :param user_id: unique user id
        :return: object with all properties or None if document not found
        """

        habits = self._fetch(user_id, _DB_NAME_HABITS)
        if habits is None:
            return None
        del habits['_id']
        del habits['_rev']
        return habits
