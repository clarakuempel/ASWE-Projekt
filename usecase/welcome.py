import json
import os

from database.database import Database
from service import api, utility

with open(os.path.join(os.path.dirname(__file__), '../database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)


def load_data(session_id: str):
    """
    Load all required data for the Welcome usecase.
    :return: Dict with rapla, weather, news, and covid data
    """
    rapla_lectures = None
    rapla_data = api.get_rapla().json()
    events = utility.get_events(rapla_data)
    if "rapla_lectures" in events.keys():
        rapla_lectures = events["rapla_lectures"]

    prefs = Database.get_instance().load_prefs(session_id)
    location: dict = prefs["location"] if prefs else default_user_prefs["location"]

    lat = location.get("lat", default_user_prefs.get("location").get("lat"))
    lon = location.get("lon", default_user_prefs.get("location").get("lon"))
    weather_data = api.get_weather_forecast(lat, lon).json()
    weather, icon = utility.get_current_weather(weather_data)

    ags = location.get("ags", default_user_prefs.get("location").get("ags"))
    covid_data = api.get_covid_stats(ags).json()
    incidence = utility.parse_covid_situation(covid_data, ags)

    news_data = api.get_news_stories(int(prefs.get("news") if prefs else default_user_prefs.get("news")))
    news_headlines = utility.parse_news_headlines(news_data, 2)

    news = {
        "first": {
            "title": news_headlines[0],
            "text": utility.parse_news_abstract(news_data, 0)[1]
        },
        "second": {
            "title": news_headlines[1],
            "text": utility.parse_news_abstract(news_data, 1)[1]
        }
    }

    return {
               "weather": {
                   "min": weather["min"],
                   "max": weather["max"],
                   "current": weather["current"],
                   "rain": weather["rain"],
                   "description": weather["description"]
               },
               "lectures": rapla_lectures,
               "incidence": incidence,
               "news": news,
           }, {"image": icon}
