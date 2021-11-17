"""
Use Case 3
- $rapla_lectures, $rapla_current_lecture, $rapla_next_lecture
- weather
- gym $gym.name, $gym.auslastung
- video $video.title
"""
import json
import os
import random

from flask import session

from service import api, utility
from database.database import Database

with open(os.path.join(os.path.dirname(__file__), '../database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)


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

    prefs = Database.get_instance().load_prefs(session["id"])

    gym_data = api.get_gym_utilization(prefs.get("gym") if prefs else default_user_prefs.get("gym")).json()
    utilization = utility.parse_gym_utilization(gym_data)
    gym = {
        "auslastung": utilization,
        "name": "McFIT Stuttgart-Mitte"
    }  # TODO Wäre fresh, wenn Name sich mit ändert

    location: dict = prefs.get("location") if prefs else default_user_prefs.get("location")
    lat = location.get("lat", default_user_prefs.get("location").get("lat"))
    lon = location.get("lon", default_user_prefs.get("location").get("lon"))
    weather_data = api.get_weather_forecast(lat, lon).json()
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
