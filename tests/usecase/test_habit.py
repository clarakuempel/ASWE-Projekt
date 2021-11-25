from datetime import timedelta, datetime

from service import utility
from usecase import habit
from unittest import mock
from tests.mock import os_env_mock
import json

with open("tests/mock/quote_data.json") as f:
    quote_data = json.load(f)
with open("tests/mock/book_data.json") as f:
    book_data = json.load(f)
with open("tests/mock/youtube_data.json") as f:
    yt_data = json.load(f)
with open("tests/mock/rapla_data.json") as f:
    rapla_data = json.load(f)

books_mock = mock.Mock()
books_mock.json.return_value = book_data

yt_mock = mock.Mock()
yt_mock.json.return_value = yt_data

rapla_mock = mock.Mock()
rapla_mock.json.return_value = rapla_data

rand_index = 1

get_events = {"rapla_next_lecture": {
    "title": "Test",
    "start": "2020"
}}


@mock.patch('service.api.get_quote', return_value=quote_data)
@mock.patch('service.api.get_bestselling_books', return_value=books_mock)
@mock.patch('database.database.Database.load_prefs', return_value=None)
@mock.patch('os.environ.get', return_value=os_env_mock.os_env_mock)
@mock.patch('random.randrange', return_value=rand_index)
@mock.patch('service.api.get_youtube_search', return_value=yt_mock)
@mock.patch('service.api.get_rapla', return_value=rapla_mock)
@mock.patch('service.utility.get_events', return_value=get_events)
def test_habit_load_data(*args):
    res = habit.load_data("123")

    books = utility.parse_bestselling_books(book_data)
    yt = utility.parse_youtube_search(yt_data)
    video = {
        "title": yt[rand_index]["title"],
    }

    assert res["quote"] == quote_data["text"]
    assert res["book"] == f"'{books[rand_index]['title'].title()}' by {books[rand_index]['author']}"
    assert res["bed_time"] == "10:30PM"
    assert res["now"] == (datetime.utcnow() + timedelta(hours=int(os_env_mock.MOCK_TIMEZONE))).time().strftime(
        "%I:%M%p")
    assert res["video"] == video
    assert res["rapla_next_lecture"] == get_events["rapla_next_lecture"]
