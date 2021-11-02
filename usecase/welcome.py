from flask import session

from database import Database
from service import utility, service


def get_welcome_text():
    """
    1. Rapla
    2. Wetter
    3. Covid Incidence
    :return: Initial welcome text
    """

    # TODO SET DEFAULT PREFS IN ONE PLACE / CONFIG FILE
    prefs = Database.get_instance().load_prefs(session["id"])
    # news_pref = prefs["news"] if prefs is not None else 1
    # news_data = service.get_news_stories(news_pref)
    ags = prefs["location"]["ags"] if prefs is not None else "08111"
    covid_data = service.get_covid_stats(ags)
    rapla_data = service.get_rapla()

    if prefs is not None:
        lat = prefs["location"]["lat"]
        lon = prefs["location"]["lon"]
    else:
        # TODO SET DEFAULT PREFS IN ONE PLACE / CONFIG FILE
        lat = 48.783333
        lon = 9.183333
    weather_data = service.get_weather_forecast(lat, lon)

    rapla = utility.get_next_event(rapla_data)
    weather = utility.get_current_weather(weather_data)
    covid = utility.get_covid_situation(covid_data, ags)

    tts = f"Good Morning! Time to start your day. {rapla['tts']} {weather['tts']} {covid['tts']}"
    return {
        "tts": tts,
        "weather-icon": weather["icon"]
    }
