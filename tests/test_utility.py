import json
import os
from datetime import datetime

import requests

import service.URLS as URLS
from service.utility import (
    parse_news_headlines,
    parse_news_abstract,
    parse_lecture_title,
    parse_lecture_type,
    get_current_weather,
    get_daily_temperature_points,
    is_raining,
    lecture_titles_to_sentence,
    get_days_until_two_off,
    timedelta_to_sentence, parse_date, parse_covid_situation, parse_air_pollution, parse_quote, parse_wikipedia_extract,
    parse_gym_utilization, parse_youtube_search, parse_bestselling_books, parse_travel_summary, get_events
)


def test_get_events(requests_mock):
    with open("tests/mock/rapla_data.json") as f:
        rapla_data = json.load(f)
    requests_mock.get(URLS.RAPLA_BASE, json=rapla_data)
    os.environ["TIMEZONE"] = "+1"
    rapla_api_response = requests.get(URLS.RAPLA_BASE).json()
    events = get_events(rapla_api_response, date=datetime(2021, 11, 19, 10))
    assert events["rapla_lectures"] == "lectures are Verteilte Systeme and IT Architekturen"
    assert events["rapla_next_lecture"]["start"] == "1 hour and 30 minutes"
    assert events["rapla_next_lecture"]["title"] == "IT Architekturen"
    assert events["rapla_current_lecture"]["end"] == "1 hour"
    assert events["rapla_current_lecture"]["title"] == "Verteilte Systeme"


def test_parse_date():
    string_date = "2021-11-20T10:30:00.1Z"
    parsed_date = parse_date(string_date)
    assert parsed_date == datetime(2021, 11, 20, 10, 30, 0, 100000)


def test_timedelta_to_sentence():
    start = datetime(2021, 11, 20, 10, 17)
    stop = datetime(2021, 11, 20, 12, 53)
    sentence = timedelta_to_sentence(start, stop)
    assert sentence == "2 hours and 36 minutes"


def test_get_days_until_two_off():
    test_day = datetime(2021, 11, 17)
    test_day_2 = datetime(2021, 11, 19)
    test_day_3 = datetime(2021, 11, 20)
    output = get_days_until_two_off(test_day)
    output_2 = get_days_until_two_off(test_day_2)
    output_3 = get_days_until_two_off(test_day_3)
    assert output == "in 3 days"
    assert output_2 == "in one day"
    assert output_3 == "today"


def test_lecture_titles_to_sentence():
    lectures_0 = []
    lectures_1 = ["Advanced Software Engineering"]
    lectures_2 = ["Data Science", "Advanced Software Engineering"]
    lectures_3 = ["Data Science", "Advanced Software Engineering", "Distributed Systems"]
    sentence_0 = lecture_titles_to_sentence(lectures_0)
    sentence_1 = lecture_titles_to_sentence(lectures_1)
    sentence_2 = lecture_titles_to_sentence(lectures_2)
    sentence_3 = lecture_titles_to_sentence(lectures_3)
    assert sentence_0 == ""
    assert sentence_1 == "lecture is Advanced Software Engineering"
    assert sentence_2 == "lectures are Data Science and Advanced Software Engineering"
    assert sentence_3 == "lectures are Data Science, Advanced Software Engineering, and Distributed Systems"


def test_parse_travel_summary(requests_mock):
    with open("tests/mock/travel_data.json") as f:
        travel_data = json.load(f)
    requests_mock.get(URLS.HERE_ROUTING_BASE, json=travel_data)
    travel_api_response = requests.get(URLS.HERE_ROUTING_BASE).json()
    travel_summary = parse_travel_summary(travel_api_response)
    assert travel_summary["length_km"] == 618
    assert travel_summary["duration"] == "6 hours 2 minutes"


def test_parse_bestselling_books(requests_mock):
    with open("tests/mock/book_data.json") as f:
        book_data = json.load(f)
    requests_mock.get(URLS.NYT_BOOKS, json=book_data)
    book_api_response = requests.get(URLS.NYT_BOOKS).json()
    books = parse_bestselling_books(book_api_response)
    assert books[0]["title"] == "THE STRANGER IN THE LIFEBOAT"
    assert books[0]["author"] == "Mitch Albom"
    assert books[0]["description"] == "After a ship explodes, 10 people struggling to survive pull a man " \
                                      "who claims to be the Lord out of the sea."
    assert books[0]["image"] == "https://storage.googleapis.com/du-prd/books/images/9780062888341.jpg"


def test_parse_youtube_search(requests_mock):
    with open("tests/mock/youtube_data.json") as f:
        youtube_data = json.load(f)
    requests_mock.get(URLS.YT_SEARCH_BASE, json=youtube_data)
    yt_api_response = requests.get(URLS.YT_SEARCH_BASE).json()
    videos = parse_youtube_search(yt_api_response)
    assert videos[0]["url"] == "https://www.youtube.com/watch?v=oAPCPjnU1wA"
    assert videos[0]["thumbnail"] == "https://i.ytimg.com/vi/oAPCPjnU1wA/hqdefault.jpg"
    assert videos[0]["title"] == "20 MINUTE FULL BODY WORKOUT(NO EQUIPMENT)"


def test_parse_gym_utilization(requests_mock):
    with open("tests/mock/gym_data.json") as f:
        gym_data = json.load(f)
    requests_mock.get(URLS.GYM_UTIL_BASE, json=gym_data)
    gym_api_response = requests.get(URLS.GYM_UTIL_BASE).json()
    utilization = parse_gym_utilization(gym_api_response)
    assert utilization == 21


def test_parse_wikipedia_extract(requests_mock):
    with open("tests/mock/wiki_data.json") as f:
        wiki_data = json.load(f)
    requests_mock.get(URLS.WIKIPEDIA_BASE, json=wiki_data)
    wiki_api_response = requests.get(URLS.WIKIPEDIA_BASE).json()
    extract = parse_wikipedia_extract(wiki_api_response)
    assert extract.startswith("In computer programming, unit testing is a software testing method")


def test_parse_quote(requests_mock):
    with open("tests/mock/quote_data.json") as f:
        quote_data = json.load(f)
    requests_mock.get(URLS.QUOTE_BASE, json=quote_data)
    quote_api_response = requests.get(URLS.QUOTE_BASE).json()
    quote, author = parse_quote(quote_api_response)
    assert quote == "Great acts are made up of small deeds."
    assert author == "Lao Tzu"


def test_parse_air_pollution(requests_mock):
    with open("tests/mock/aq_data.json") as f:
        aq_data = json.load(f)
    requests_mock.get(URLS.OWM_AQ_BASE, json=aq_data)
    aq_api_response = requests.get(URLS.OWM_AQ_BASE).json()
    aqi = parse_air_pollution(aq_api_response)
    assert aqi == "Moderate"


def test_parse_covid_situation(requests_mock):
    with open("tests/mock/covid_data.json") as f:
        covid_data = json.load(f)
    requests_mock.get(URLS.COVID_BASE, json=covid_data)
    covid_api_response = requests.get(URLS.COVID_BASE).json()
    ags_stuttgart = "08111"
    test_incidence = parse_covid_situation(covid_api_response, ags_stuttgart)
    assert test_incidence == "311.4"


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
    headlines = parse_news_headlines(news_api_response, count=2)
    assert headlines == test_news_headlines


def test_get_news_abstract(requests_mock):
    with open("tests/mock/news_data.json") as f:
        news_data = json.load(f)
    requests_mock.get(URLS.DW_RSS_BASE, json=news_data)
    news_api_response = requests.get(URLS.DW_RSS_BASE).json()
    title, abstract = parse_news_abstract(news_api_response, index=0)
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
