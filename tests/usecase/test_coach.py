import json
from unittest import mock

from service import utility
from usecase import coach

with open("tests/mock/rapla_data.json") as f:
    rapla_data = json.load(f)
with open("tests/mock/youtube_data.json") as f:
    yt_data = json.load(f)
with open("tests/mock/weather_data.json") as f:
    weather_data = json.load(f)
with open("tests/mock/gym_data.json") as f:
    gym_data = json.load(f)

gym_mock = mock.Mock()
gym_mock.json.return_value = gym_data

rapla_mock = mock.Mock()
rapla_mock.json.return_value = rapla_data

yt_mock = mock.Mock()
yt_mock.json.return_value = yt_data

weather_mock = mock.Mock()
weather_mock.json.return_value = weather_data

rand_index = 0

get_events = {
    "rapla_next_lecture": {
        "title": "Test",
        "start": "2020"
    },
    "rapla_current_lecture": {
        "title": "Test2",
        "end": "2021"
    },
    "rapla_lectures": [
        {
            "title": "A"
        },
        {
            "title": "B"
        }
    ]
}


@mock.patch('database.database.Database.load_prefs', return_value=None)
@mock.patch('service.api.get_rapla', return_value=rapla_mock)
@mock.patch('service.utility.get_events', return_value=get_events)
@mock.patch('service.api.get_youtube_search', return_value=yt_mock)
@mock.patch('random.randrange', return_value=rand_index)
@mock.patch('service.api.get_weather_forecast', return_value=weather_mock)
@mock.patch('service.api.get_gym_utilization', return_value=gym_mock)
def test_coach_load(*args):
    res = coach.load_data("123")

    weather, _ = utility.get_current_weather(weather_data)
    del weather['mean']

    rapla_res = {rapla_key: res[rapla_key] for rapla_key in
                 ['rapla_lectures', 'rapla_current_lecture', 'rapla_next_lecture']}
    yt = utility.parse_youtube_search(yt_data)
    video = {
        "title": yt[rand_index]["title"],
    }

    gym = {
        "auslastung": utility.parse_gym_utilization(gym_data),
        "name": "McFIT Stuttgart-Mitte"
    }

    assert res["weather"] == weather
    assert rapla_res == get_events
    assert res["video"] == video
    assert res["gym"] == gym
