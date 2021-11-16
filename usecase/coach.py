"""
Use Case 3
- $rapla_lectures, $rapla_current_lecture, $rapla_next_lecture
- weather
- gym $gym.name, $gym.auslastung
- video $video.title
"""

import random

from service import api, utility


def load_data():
    rapla_lectures, rapla_current_lecture, rapla_next_lecture = None, None, None
    rapla_data = api.get_rapla().json()
    events = utility.get_events(rapla_data)
    if "rapla_lectures" in events.keys():
        rapla_lectures = events["rapla_lectures"]
    if "rapla_current_lecture" in events.keys():
        rapla_current_lecture = events["rapla_current_lecture"]
    if "rapla_next_lecture" in events.keys():
        rapla_next_lecture = events["rapla_next_lecture"]

    yt_data = api.get_youtube_search("home workout pamela reif 20 min").json()
    yt = utility.parse_youtube_search(yt_data)
    r = random.randrange(0, 10)
    video = {
        "title": yt[r]["title"],
    }

    # todo user prefs -> gym
    gym_data = api.get_gym_utilization(1731421430).json()
    utilization = utility.parse_gym_utilization(gym_data)
    gym = {
        "auslastung": utilization,
        "name": "McFIT Stuttgart-Mitte"
    }

    # todo user prefs -> user location
    weather_data = api.get_weather_forecast(48.783333, 9.183333).json()
    weather, icon = utility.get_current_weather(weather_data)

    return {
        "rapla_lectures": rapla_lectures,
        "rapla_current_lecture": rapla_current_lecture,
        "rapla_next_lecture": rapla_next_lecture,
        "video": video,
        "gym": gym,
        "weather": {
            "min": weather["min"],
            "max": weather["max"],
            "current": weather["current"],
            "rain": weather["rain"],
            "description": weather["description"]
        }
    }
