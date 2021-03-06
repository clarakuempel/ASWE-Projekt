import json
import os
import random

from service import api, utility
from database.database import Database

with open(os.path.join(os.path.dirname(__file__), '../database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)


def load_data(session_id: str):
    """
    Load all required data for the Sports Coach usecase.
    :return: Dict with rapla, weather, gym, and video data
    """
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
    video_image = yt[r]["thumbnail"]
    video_link = yt[r]["url"]

    prefs = Database.get_instance().load_prefs(session_id)

    gym_id = prefs.get("gym") if prefs else default_user_prefs.get("gym")
    gym_data = api.get_gym_utilization(gym_id).json()
    utilization = utility.parse_gym_utilization(gym_data)

    with open(os.path.join(os.path.dirname(__file__), '../database/gym_selection.json'), encoding='utf-8') as gym_f:
        gyms = json.load(gym_f)
    gym_name = "McFit"
    for gym in gyms:
        if gym["id"] == gym_id:
            gym_name = gym["studioName"]
            break
    gym = {
        "auslastung": utilization,
        "name": gym_name
    }

    print(gym)

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
           }, {"image": video_image, "link": video_link}
