from datetime import timedelta, datetime

from service import utility
from usecase import habit
from unittest import mock
import json

with open("tests/mock/quote_data.json") as f:
    quote_data = json.load(f)
with open("tests/mock/book_data.json") as f:
    book_data = json.load(f)

books_mock = mock.Mock()
books_mock.json.return_value = book_data

MOCK_TIMEZONE = "+1"
os_env_mock = mock.MagicMock(side_effect=lambda value: MOCK_TIMEZONE)

rand_index = 1


@mock.patch('service.api.get_quote', return_value=quote_data)
@mock.patch('service.api.get_bestselling_books', return_value=books_mock)
@mock.patch('database.database.Database.load_prefs', return_value=None)
@mock.patch('os.environ.get', return_value=os_env_mock)
@mock.patch('random.randrange', return_value=rand_index)
def test_habit_load_data(*args):
    res = habit.load_data("123")
    books = utility.parse_bestselling_books(book_data)

    assert res["quote"] == quote_data["text"]
    assert res["book"] == f"'{books[rand_index]['title'].title()}' by {books[rand_index]['author']}"
    assert res["bed_time"] == "10:30PM"
    assert res["now"] == (datetime.utcnow() + timedelta(hours=int(MOCK_TIMEZONE))).time().strftime("%I:%M%p")
