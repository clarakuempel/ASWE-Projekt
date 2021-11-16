"""
Use Case 4
- $days_off_date
- $city, $travel_duration
- $wikipedia
"""
from service import api, utility
import random


def load_data():
    days_off_date = utility.get_days_until_two_off()

    r = random.randrange(0, 10)
    # todo city list
    cities = [{
        "city": "Amsterdam",
        "lat": 52.377956,
        "lon": 4.897070
    }]
    print("City ", r)
    city = cities[0]["city"]
    lat = cities[0]["lat"]
    lon = cities[0]["lon"]

    # todo get user location, stuttgart = 48.783333, 9.183333
    travel_data = api.get_travel_summary(48.783333, 9.183333, lat, lon).json()
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
