import json
import os

from database.database import Database
from service import api, utility
import random

with open(os.path.join(os.path.dirname(__file__), '../database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)


def load_data(session_id: str):
    """
    Load all required data for the Holiday Finder usecase.
    :return: Dict with travel, wikipedia, weather, and covid data
    """
    days_off_date = utility.get_days_until_two_off()

    cities = [
        {
            "city": "Zell im Fichtelgebirge",
            "lat": 50.133578,
            "lon": 11.821875,
            "ags": "09475"
        },
        {
            "city": "Munich",
            "lat": 48.140205,
            "lon": 11.575175,
            "ags": "09162"
        },
        {
            "city": "Berlin",
            "lat": 52.520008,
            "lon": 13.404954,
            "ags": "11001"
        },
        {
            "city": "Dresden",
            "lat": 51.050407,
            "lon": 13.737262,
            "ags": "14612"
        },
        {
            "city": "Leipzig",
            "lat": 51.3396955,
            "lon": 12.3730747,
            "ags": "14713"
        },
        {
            "city": "Augsburg",
            "lat": 48.366512,
            "lon": 10.894446,
            "ags": "09761"
        },
        {
            "city": "Hamburg",
            "lat": 53.551086,
            "lon": 9.993682,
            "ags": "02000"
        },
        {
            "city": "Heidelberg",
            "lat": 49.398750,
            "lon": 8.672434,
            "ags": "08221"
        },
        {
            "city": "Potsdam",
            "lat": 52.391842,
            "lon": 13.063561,
            "ags": "12054"
        }
    ]
    r = random.randrange(0, len(cities))
    city = cities[r]["city"]
    dest_lat = cities[r]["lat"]
    dest_lon = cities[r]["lon"]
    dest_ags = cities[r]["ags"]

    prefs = Database.get_instance().load_prefs(session_id)

    location: dict = prefs.get("location") if prefs else default_user_prefs.get("location")
    lat = location.get("lat", default_user_prefs.get("location").get("lat"))
    lon = location.get("lon", default_user_prefs.get("location").get("lon"))
    travel_data = api.get_travel_summary(lat, lon, dest_lat, dest_lon).json()
    travel_summary = utility.parse_travel_summary(travel_data)

    weather_data = api.get_weather_forecast(dest_lat, dest_lon).json()
    weather, icon = utility.get_current_weather(weather_data)

    covid_data = api.get_covid_stats(dest_ags).json()
    incidence = utility.parse_covid_situation(covid_data, dest_ags)

    wikipedia_data = api.get_wikipedia_extract(city).json()
    wikipedia = utility.parse_wikipedia_extract(wikipedia_data)
    wikipedia = wikipedia.split("\n")[0]

    return {
        "days_off_date": days_off_date,
        "city": city,
        "travel_duration": travel_summary["duration"],
        "wikipedia": wikipedia,
        "weather": {
            "min": weather["min"],
            "max": weather["max"],
            "current": weather["current"],
            "rain": weather["rain"],
            "description": weather["description"]
        },
        "incidence": incidence
    }
