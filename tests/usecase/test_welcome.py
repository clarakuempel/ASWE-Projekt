import json
import os
from unittest import mock

from service import utility
from usecase import welcome
from tests.mock import os_env_mock

with open("tests/mock/rapla_data.json") as f:
    rapla_data = json.load(f)
with open("tests/mock/weather_data.json") as f:
    weather_data = json.load(f)
with open("tests/mock/covid_data.json") as f:
    covid_data = json.load(f)
with open("tests/mock/news_data.json") as f:
    news_data = json.load(f)
with open(os.path.join(os.path.dirname(__file__), '../../database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)

rapla_mock = mock.Mock()
rapla_mock.json.return_value = rapla_data

weather_mock = mock.Mock()
weather_mock.json.return_value = weather_data

covid_mock = mock.Mock()
covid_mock.json.return_value = covid_data


@mock.patch('service.api.get_rapla', return_value=rapla_mock)
@mock.patch('database.database.Database.load_prefs', return_value=None)
@mock.patch('service.api.get_weather_forecast', return_value=weather_mock)
@mock.patch('service.api.get_covid_stats', return_value=covid_mock)
@mock.patch('service.api.get_news_stories', return_value=news_data)
@mock.patch('os.environ.get', return_value=os_env_mock.os_env_mock)
@mock.patch('service.utility.get_events', return_value={"rapla_lectures": ["Test"]})
def test_load_data_for_a_warmly_welcome(*args):
    res, _ = welcome.load_data("123")

    ags = default_user_prefs["location"]["ags"]
    weather, _ = utility.get_current_weather(weather_data)
    del weather['mean']

    assert res["incidence"] == utility.parse_covid_situation(covid_data, ags)
    assert res["lectures"] == ["Test"]
    assert res["news"]["second"]["text"] == utility.parse_news_abstract(news_data, 1)[1]
    assert res["weather"] == weather
