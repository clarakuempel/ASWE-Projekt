import json
from unittest import mock

from service import utility
from usecase import holiday

with open("tests/mock/weather_data.json") as f:
    weather_data = json.load(f)

with open("tests/mock/covid_data.json") as f:
    covid_data = json.load(f)
with open("tests/mock/travel_data.json") as f:
    travel_data = json.load(f)
with open("tests/mock/wiki_data.json") as f:
    wiki_data = json.load(f)

weather_mock = mock.Mock()
weather_mock.json.return_value = weather_data

covid_mock = mock.Mock()
covid_mock.json.return_value = covid_data
incidence = 420.69

travel_mock = mock.Mock()
travel_mock.json.return_value = travel_data

wiki_mock = mock.Mock()
wiki_mock.json.return_value = wiki_data

rand_index = 0


@mock.patch('database.database.Database.load_prefs', return_value=None)
@mock.patch('random.randrange', return_value=rand_index)
@mock.patch('service.api.get_weather_forecast', return_value=weather_mock)
@mock.patch('service.api.get_covid_stats', return_value=covid_mock)
@mock.patch('service.utility.parse_covid_situation', return_value=incidence)
@mock.patch('service.api.get_travel_summary', return_value=travel_mock)
@mock.patch('service.api.get_wikipedia_extract', return_value=wiki_mock)
def test_holiday_load(*args):
    res, _ = holiday.load_data("123")

    weather, _ = utility.get_current_weather(weather_data)
    del weather['mean']

    incidence_test = utility.parse_covid_situation(covid_data, "09475")

    wikipedia = utility.parse_wikipedia_extract(wiki_data)
    wikipedia = wikipedia.split("\n")[0]

    assert res["days_off_date"] == utility.get_days_until_two_off()
    assert res["city"] == "Zell im Fichtelgebirge"
    assert res["travel_duration"] == utility.parse_travel_summary(travel_data)["duration"]
    assert res["wikipedia"] == wikipedia
    assert res["weather"] == weather
    assert res["incidence"] == incidence_test
