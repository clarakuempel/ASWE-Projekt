import json

import requests

import service.URLS as URLS
from service.utility import (
    get_news_headlines,
    get_news_abstract,
    parse_lecture_title,
    parse_lecture_type,
    get_current_weather,
    get_daily_temperature_points,
    is_raining
)


def test_get_current_weather(requests_mock):
    with open("tests/mock/weather_data.json") as f:
        weather_data = json.load(f)
    requests_mock.get(URLS.OWM_WEATHER_BASE, json=weather_data)
    weather_api_response = requests.get(URLS.OWM_WEATHER_BASE).json()
    parsed_weather, _ = get_current_weather(weather_api_response)
    expected_weather = {
        "min": 5,
        "max": 9,
        "current": 9,
        "mean": 7,
        "rain": True,
        "description": "scattered clouds"
    }
    assert parsed_weather["min"] == expected_weather["min"]
    assert parsed_weather["max"] == expected_weather["max"]
    assert parsed_weather["current"] == expected_weather["current"]
    assert parsed_weather["mean"] == expected_weather["mean"]
    assert parsed_weather["rain"] is expected_weather["rain"]
    assert parsed_weather["description"] == expected_weather["description"]


def test_get_daily_temperature_points(requests_mock):
    with open("tests/mock/weather_data.json") as f:
        weather_data = json.load(f)
    requests_mock.get(URLS.OWM_WEATHER_BASE, json=weather_data)
    weather_api_response = requests.get(URLS.OWM_WEATHER_BASE).json()
    min_temp, max_temp, mean_temp = get_daily_temperature_points(weather_api_response["hourly"])
    assert min_temp == 5
    assert max_temp == 9
    assert mean_temp == 7


def test_is_raining(requests_mock):
    with open("tests/mock/weather_data.json") as f:
        weather_data = json.load(f)
    requests_mock.get(URLS.OWM_WEATHER_BASE, json=weather_data)
    weather_api_response = requests.get(URLS.OWM_WEATHER_BASE).json()
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
    requests_mock.get(URLS.DW_RSS_BASE, json=news_data)
    news_api_response = requests.get(URLS.DW_RSS_BASE).json()
    headlines = get_news_headlines(news_api_response, count=2)
    assert headlines == test_news_headlines


def test_get_news_abstract(requests_mock):
    with open("tests/mock/news_data.json") as f:
        news_data = json.load(f)
    requests_mock.get(URLS.DW_RSS_BASE, json=news_data)
    news_api_response = requests.get(URLS.DW_RSS_BASE).json()
    title, abstract = get_news_abstract(news_api_response, index=0)
    assert title == test_news_title
    assert abstract == test_news_abstract


test_news_headlines = [
    "Japan stabbing attack: At least 17 injured on Tokyo train",
    "Czech cable car crashes to ground, kills one"
]
test_news_title = "Japan stabbing attack: At least 17 injured on Tokyo train"

test_news_abstract = "The suspect, who was reportedly dressed as the \"Joker\" character, " \
                     "was arrested for attempted murder after the stabbing rampage. " \
                     "He also started a fire on the train, with smoke filling the carriage."
