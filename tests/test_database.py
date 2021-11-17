import database
from database import database_interface
from unittest import mock


@mock.patch('database.Database')
def test_store_prefs(MockClass):
    database.Database()
    assert MockClass is database.Database
    assert MockClass.called


def test_interface():
    assert issubclass(database.Database, database_interface.DBInterface)
