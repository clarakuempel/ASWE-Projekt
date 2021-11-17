"""
Use Case 4
- $days_off_date
- $city, $travel_duration
- $wikipedia
"""
import json
import os

from flask import session

from database.database import Database
from service import api, utility
import random

with open(os.path.join(os.path.dirname(__file__), '../database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)


def load_data():
    days_off_date = utility.get_days_until_two_off()

    cities = [{
        "city": "Amsterdam",
        "lat": 52.377956,
        "lon": 4.897070
    },
        {
            "city": "Zell im Fichtelgebirge",
            "lat": 50.133578,
            "lon": 11.821875
        },
        {
            "city": "Strasbourg",
            "lat": 48.580865,
            "lon": 7.743881
        },
        {
            "city": "Lyon",
            "lat": 45.761531,
            "lon": 4.847827
        },
        {
            "city": "Munich",
            "lat": 48.140205,
            "lon": 11.575175
        },
        {
            "city": "Geneva",
            "lat": 46.203753,
            "lon": 6.143416
        }
    ]
    r = random.randrange(0, len(cities))
    city = cities[r]["city"]
    dest_lat = cities[r]["lat"]
    dest_lon = cities[r]["lon"]

    prefs = Database.get_instance().load_prefs(session["id"])

    location: dict = prefs.get("location") if prefs else default_user_prefs.get("location")
    lat = location.get("lat", default_user_prefs.get("location").get("lat"))
    lon = location.get("lon", default_user_prefs.get("location").get("lon"))
    travel_data = api.get_travel_summary(lat, lon, dest_lat, dest_lon).json()
    travel_summary = utility.parse_travel_summary(travel_data)

    wikipedia_data = api.get_wikipedia_extract(city).json()
    wikipedia = utility.parse_wikipedia_extract(wikipedia_data)
    wikipedia = wikipedia.split("\n")[0]

    return {
        "days_off_date": days_off_date,
        "city": city,
        "travel_duration": travel_summary["duration"],
        "wikipedia": wikipedia
    }
