import json

import requests

from service.utility import get_news_headlines, get_news_abstract, parse_lecture_title, parse_lecture_type, \
    get_current_weather, get_daily_temperature_points, is_raining


def test_get_current_weather(requests_mock):
    with open("tests/mock/weather_data.json") as f:
        weather_data = json.load(f)
    requests_mock.get("https://api.openweathermap.org/data/2.5/onecall", json=weather_data)
    weather_api_response = requests.get("https://api.openweathermap.org/data/2.5/onecall").json()
    tts_output = get_current_weather(weather_api_response)["tts"]
    assert tts_output == test_current_weather


def test_get_daily_temperature_points(requests_mock):
    with open("tests/mock/weather_data.json") as f:
        weather_data = json.load(f)
    requests_mock.get("https://api.openweathermap.org/data/2.5/onecall", json=weather_data)
    weather_api_response = requests.get("https://api.openweathermap.org/data/2.5/onecall").json()
    min_temp, max_temp, mean_temp = get_daily_temperature_points(weather_api_response["hourly"])
    assert min_temp == 5
    assert max_temp == 9
    assert mean_temp == 7


def test_is_raining(requests_mock):
    with open("tests/mock/weather_data.json") as f:
        weather_data = json.load(f)
    requests_mock.get("https://api.openweathermap.org/data/2.5/onecall", json=weather_data)
    weather_api_response = requests.get("https://api.openweathermap.org/data/2.5/onecall").json()
    assert is_raining(weather_api_response["hourly"]) is True


def test_parse_lecture_title():
    test_title_1 = "Advanced Software Engineering [ Teiln]"
    test_title_2 = "Advanced Software Engineering [19 Teiln]"
    test_title_3 = "Maschinelles Lernen - Online [ Teiln]"
    assert parse_lecture_title(test_title_1) == "Advanced Software Engineering"
    assert parse_lecture_title(test_title_2) == "Advanced Software Engineering"
    assert parse_lecture_title(test_title_3) == "Maschinelles Lernen"


def test_parse_lecture_type():
    event_online = "Online-Format (ohne Raumbelegung)"
    event_onsite = "RB41-0.18"
    assert parse_lecture_type(event_online) == "online"
    assert parse_lecture_type(event_onsite) == "on site"


def test_get_news_headlines(requests_mock):
    with open("tests/mock/news_data.json") as f:
        news_data = json.load(f)
    requests_mock.get("https://rss.dw.com/rdf/rss-en-all", json=news_data)
    news_api_response = requests.get("https://rss.dw.com/rdf/rss-en-all").json()
    tts_output = get_news_headlines(news_api_response)["tts"]
    assert tts_output == test_news_headlines


def test_get_news_abstract(requests_mock):
    with open("tests/mock/news_data.json") as f:
        news_data = json.load(f)
    requests_mock.get("https://rss.dw.com/rdf/rss-en-all", json=news_data)
    news_api_response = requests.get("https://rss.dw.com/rdf/rss-en-all").json()
    tts_output = get_news_abstract(news_api_response)["tts"]
    print(test_news_abstract)
    assert tts_output == test_news_abstract


test_current_weather = "It is currently 9 degrees and scattered clouds. " \
                       "Temperature today will be between 5 and 9 degrees. " \
                       "Remember to bring a jacket and an umbrella, it will rain later on."

test_news_headlines = "Current headlines for you preferred topics are " \
                      "'Japan stabbing attack: At least 17 injured on Tokyo train' and " \
                      "'Czech cable car crashes to ground, kills one'"
test_news_abstract = "More information about the article " \
                     "'Japan stabbing attack: At least 17 injured on Tokyo train: " \
                     "The suspect, who was reportedly dressed as the \"Joker\" character, " \
                     "was arrested for attempted murder after the stabbing rampage. " \
                     "He also started a fire on the train, with smoke filling the carriage."
