import json

import requests

from service.utility import get_news_headlines


def test_get_news_headlines(requests_mock):
    with open("tests/mock/news_data.json") as f:
        news_data = json.load(f)
    requests_mock.get("https://www.dw.com/", json=news_data)
    news_api_response = requests.get("https://www.dw.com/").json()
    tts_output = get_news_headlines(news_api_response)["tts"]
    assert tts_output == news_headlines


news_headlines = "Current headlines for you preferred topics are " \
                 "'Japan stabbing attack: At least 17 injured on Tokyo train' and " \
                 "'Czech cable car crashes to ground, kills one'"
