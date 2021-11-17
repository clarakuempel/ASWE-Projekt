import database
from database import database_interface
from unittest import mock


@mock.patch('database.database.Database')
def test_store_prefs(MockClass):
    database.database.Database()
    assert MockClass is database.database.Database
    assert MockClass.called


def test_interface():
    assert issubclass(database.database.Database, database_interface.DBInterface)
