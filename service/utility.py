from datetime import datetime, timezone

import numpy as np
# TODO for debugging date:
# from dateutil.tz import tzutc
from dateutil import parser
from flask import session

from database import Database
from service import service, URLS


def get_news_headlines(offset=0):
    prefs = Database.get_instance().load_prefs(session["id"])
    news_pref = prefs["news"] if prefs is not None else 1  # TODO SET DEFAULT PREFS IN ONE PLACE / CONFIG FILE
    news_data = service.get_news_stories(news_pref)
    stories = news_data["entries"]
    sentence = f"Current headlines for you preferred topics are '{stories[0 + offset]['title']}' and " \
               f"'{stories[1 + offset]['title']}'"
    return {
        "tts": sentence
    }


def get_news_abstract(index=0):
    prefs = Database.get_instance().load_prefs(session["id"])
    news_pref = prefs["news"] if prefs is not None else 1  # TODO SET DEFAULT PREFS IN ONE PLACE / CONFIG FILE
    news_data = service.get_news_stories(news_pref)
    stories = news_data["entries"]
    sentence = f"More information about the article '{stories[index]['title']}: {stories[index]['description']}."
    return {
        "tts": sentence
    }


def get_covid_situation():
    prefs = Database.get_instance().load_prefs(session["id"])
    # TODO SET DEFAULT PREFS IN ONE PLACE / CONFIG FILE
    ags = prefs["location"]["ags"] if prefs is not None else "08111"
    covid_data = service.get_covid_stats(ags)
    week_incidence = covid_data["data"][str(ags)]["weekIncidence"]
    sentence = f"Remember washing your hands, the weekly incidence is at {week_incidence:.1f}."
    return {
        "tts": sentence
    }


def get_next_event():
    rapla_data = service.get_rapla()
    sentence = "You have no upcoming lectures today."
    is_first_lecture = True
    for event in rapla_data["events"]:
        start = parser.isoparse(event["start"])
        date_now = datetime.now(timezone.utc)
        # date_now = datetime(2021, 10, 14, 7, tzinfo=tzutc())
        # TODO: date for debugging: datetime(2021, 10, 14, 5, tzinfo=tzutc())
        if start.date() == date_now.date():
            delta = start - date_now
            if delta.total_seconds() < 0:
                is_first_lecture = False
                continue
            else:
                hours, remainder = divmod(delta.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                sentence = f"Your {'first' if is_first_lecture else 'next'} lecture starts in "
                has_hours = False
                if hours > 0:
                    sentence += f"{int(hours)} hours "
                    has_hours = True
                if minutes > 0:
                    sentence += f"{'and ' if has_hours else ''}{int(minutes)} minutes"
                lecture_type = 'online' if event["type"] == "Online-Format (ohne Raumbelegung)" else "on site"
                lecture_title = event['title'].replace(" - Online  [ Teiln]", "").replace(" [19 Teiln]", "")
                sentence += f". It is {lecture_title} and is taking place {lecture_type}."
                break

    return {
        "tts": sentence
    }


def get_current_weather():
    data = Database.get_instance().load_prefs(session["id"])
    if data is not None:
        lat = data["location"]["lat"]
        lon = data["location"]["lon"]
    else:
        # TODO SET DEFAULT PREFS IN ONE PLACE / CONFIG FILE
        lat = 48.783333
        lon = 9.183333
    weather_data = service.get_weather_forecast(lat, lon)
    description = weather_data["current"]["weather"][0]["description"]
    icon = weather_data["current"]["weather"][0]["icon"]
    current_temp = int(weather_data["current"]["temp"])
    min_temp, max_temp, mean_temp = _get_daily_temperature_points(weather_data["hourly"])

    raining = _is_raining(weather_data["hourly"])

    if mean_temp <= 10:
        recommendation = "Remember to bring a jacket and an umbrella, it will rain later on." if raining else \
            "You will need a jacket."
    elif 10 < mean_temp <= 18:
        recommendation = "Remember to bring a jacket and an umbrella, it will rain later on." if raining else \
            "You will need a light jacket."
    else:
        recommendation = "You dont need a jacket but it will rain later on." if raining else \
            "You dont need a jacket."

    sentence = f"It is currently {current_temp} degrees and {description}. " \
               f"Temperature today will be between {min_temp} and {max_temp} degrees. {recommendation}"
    return {
        "tts": sentence,
        "icon": f"{URLS.OWM_ICON_BASE}{icon}@2x.png"
    }


def _get_daily_temperature_points(hourly_data):
    temperatures = np.array([])
    for item in hourly_data:
        t = item["temp"]
        temperatures = np.append(t, temperatures)
    return int(np.min(temperatures)), int(np.max(temperatures)), int(np.mean(temperatures))


def _is_raining(hourly_data):
    umbrella = False
    for item in hourly_data:
        if item["weather"][0]["main"] in ["Rain", "Thunderstorm", "Drizzle"]:
            umbrella = True
            break
    return umbrella
