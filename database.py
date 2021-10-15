import abc
import secrets
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1
from typing import Final

_DB_NAME: Final = 'products'
_EXCEPTION_CONNECT: Final = Exception("Call connect() first")


class DBInterface(metaclass=abc.ABCMeta):
    # ToDo fully define interface
    # @abc.abstractmethod
    def load_data_source(self, path: str, file_name: str) -> str:
        """Load in the file for extracting text."""
        pass

    # @abc.abstractmethod
    def extract_text(self, full_file_name: str) -> dict:
        """Extract text from the currently loaded file."""
        raise Exception("Interface function is not implemented")


class Database(DBInterface):
    __instance = None
    __service = None

    @classmethod
    def get_instance(cls) -> object:
        """
        Method to access singleton-instance. Creates instance if not exists.
        :return: Singleton of database-connector
        """
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        """
        'Private' constructor.
        Throws exception if singleton-instance already exists.
        """
        if self.__class__.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__class__.__instance = self
            self.__instance.connect()  # ToDo Remove

    def connect(self) -> None:
        """
        Connects to IBM Cloudant via IAMAuthenticator
        based on API-Key and URL defined in ./secrets.py

        :return: None
        """
        authenticator = IAMAuthenticator(secrets.APIKey)
        authenticator.set_disable_ssl_verification(True)
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(secrets.URL)
        service.set_disable_ssl_verification(True)
        self.__service = service

    def get_service(self) -> CloudantV1:
        return self.__service

    def create_dbs(self) -> None:
        if self.__service is None:
            raise _EXCEPTION_CONNECT
        response = self.__service \
            .put_database(db=_DB_NAME).get_result()
        if not response['ok']:
            raise Exception("Error while creation of databases")

    def store(self) -> None:
        if self.__service is None:
            raise _EXCEPTION_CONNECT
        key = "person1" + "-preferences"
        doc = {
            '_id': ":" + key,
            'name': 'test',
            'age': 18
        }

        response = self.__service.post_document(db=_DB_NAME, document=doc)\
            .get_result()
        if not response['ok']:
            raise Exception("Error while posting document")

    def get_all_docs(self):
        # Catch 404
        return self.__service.post_all_docs(
            db=_DB_NAME,
            include_docs=True,
            startkey='',
            limit=10
        ).get_result()
