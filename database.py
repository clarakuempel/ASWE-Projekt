import abc
import secrets
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1


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

    def init(self):
        pass

    def get_service(self) -> CloudantV1:
        return self.__service

    def create_dbs(self) -> None:
        if self.__service is None:
            raise Exception("Call connect() first")
        response = self.__service\
            .put_database(db='products', partitioned=True).get_result()
        if not response["ok"]:
            raise Exception("Error while creation of databases")
