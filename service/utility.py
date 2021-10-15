from datetime import datetime, timezone

import numpy as np
# TODO for debugging date: from dateutil.tz import tzutc
from dateutil import parser
from flask import session

from service import service, URLS


def get_covid_situation():
    STUTTGART_AGS = "08111"
    # TODO Get AGS based on user location
    # TODO AS OF 15.10.21 COVID API IS RETURNING 502 https://api.corona-zahlen.org/docs/
    covid_data = service.get_covid_stats(STUTTGART_AGS)
    return covid_data


def get_first_event():
    rapla_data = service.get_rapla()
    sentence = "No lecture today."
    is_first_lecture = True
    for event in rapla_data["events"]:
        start = parser.isoparse(event["start"])
        date_now = datetime.now(timezone.utc)
        # TODO: date for debugging: datetime(2021, 10, 14, 5, tzinfo=tzutc())
        if start.date() == date_now.date():
            delta = start - date_now
            if delta.total_seconds() < 0:
                is_first_lecture = False
                continue
            else:
                hours, remainder = divmod(delta.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                sentence = f"The {'first' if is_first_lecture else 'next'} lecture starts in "
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
        "tts": sentence,
        "display": {
            "message": sentence,
            "data": None
        }
    }


def get_current_weather():
    STUTTGART_LAT = 48.783333
    STUTTGART_LON = 9.183333
    # TODO Get location from user preference
    print(f"GET LOCATION FOR USER {session['id']}")
    weather_data = service.get_weather_forecast(STUTTGART_LAT, STUTTGART_LON)
    description = weather_data["current"]["weather"][0]["description"]
    icon = weather_data["current"]["weather"][0]["icon"]
    current_temp = int(weather_data["current"]["temp"])
    min_temp, max_temp, mean_temp = _get_daily_temperature_points(weather_data["hourly"])

    raining = _is_raining(weather_data["hourly"])

    if mean_temp <= 10:
        recommendation = "You will need a jacket and an umbrella." if raining else "You will need a jacket."
    elif 10 < mean_temp <= 18:
        recommendation = "You will need a light jacket and an umbrella." if raining else "You will need a light jacket."
    else:
        recommendation = "You dont need a jacket but it will rain." if raining else "You dont need a jacket."

    sentence = f"It is currently {current_temp} degrees and {description}. " \
               f"Temperature today will be between {min_temp} and {max_temp} degrees. {recommendation}"
    return {
        "tts": sentence,
        "display": {
            "message": sentence,
            "data": {
                "icon": f"{URLS.OWM_ICON_BASE}{icon}@2x.png"
            }
        }
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
        if item["weather"] in ["Rain", "Thunderstorm", "Drizzle"]:
            umbrella = True
            break
    return umbrella
