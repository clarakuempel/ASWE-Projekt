import json

import requests

from service.utility import get_news_headlines, get_news_abstract


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


test_news_headlines = "Current headlines for you preferred topics are " \
                      "'Japan stabbing attack: At least 17 injured on Tokyo train' and " \
                      "'Czech cable car crashes to ground, kills one'"
test_news_abstract = "More information about the article " \
                     "'Japan stabbing attack: At least 17 injured on Tokyo train: " \
                     "The suspect, who was reportedly dressed as the \"Joker\" character, " \
                     "was arrested for attempted murder after the stabbing rampage. " \
                     "He also started a fire on the train, with smoke filling the carriage."
