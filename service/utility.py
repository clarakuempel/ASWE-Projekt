from datetime import datetime, timezone

import numpy as np
# TODO for debugging date:
# from dateutil.tz import tzutc
from dateutil import parser

from service import URLS


def get_news_headlines(news_data, count=1):
    stories = news_data["entries"]
    headlines = [stories[i]["title"] for i in range(0, count)]
    return headlines


def get_news_abstract(news_data, index=0):
    stories = news_data["entries"]
    title = stories[index]["title"]
    abstract = stories[index]["summary"]
    return title, abstract


def get_covid_situation(covid_data, ags):
    week_incidence = covid_data["data"][str(ags)]["weekIncidence"]
    return f"{week_incidence:.1f}"


def get_event_overview(rapla_data):
    results = []
    next_lecture = None
    is_next_lecture = True
    for event in rapla_data["events"]:
        start = parser.isoparse(event["start"])
        date_now = datetime.now(timezone.utc)
        # date_now = datetime(2021, 10, 14, 7, tzinfo=tzutc())
        # TODO: date for debugging: datetime(2021, 10, 14, 5, tzinfo=tzutc())
        if start.date() == date_now.date():
            start_delta = start - date_now
            if start_delta.total_seconds() >= 0:
                if is_next_lecture:
                    next_lecture = parse_lecture_title(event['title'])
                    is_next_lecture = False
            results.append(parse_lecture_title(event['title']))
    if not results:
        results = []
    return results, next_lecture


def parse_lecture_title(title):
    return title.replace(" [ Teiln]", "").replace(" - Online", "").replace(" [19 Teiln]", "").rstrip()


def parse_lecture_type(event_type):
    return 'online' if event_type == "Online-Format (ohne Raumbelegung)" else "on site"


def get_next_event(rapla_data):
    _, next_lecture = get_event_overview(rapla_data)
    return next_lecture


def get_current_weather(weather_data):
    description = weather_data["current"]["weather"][0]["description"]
    icon = weather_data["current"]["weather"][0]["icon"]
    current_temp = int(weather_data["current"]["temp"])

    min_temp, max_temp, mean_temp = get_daily_temperature_points(weather_data["hourly"])
    raining = is_raining(weather_data["hourly"])

    weather = {
        "min": min_temp,
        "max": max_temp,
        "current": current_temp,
        "mean": mean_temp,
        "rain": raining,
        "description": description
    }
    return weather, f"{URLS.OWM_ICON_BASE}{icon}@2x.png"


def get_daily_temperature_points(hourly_data):
    temperatures = np.array([])
    for item in hourly_data:
        t = item["temp"]
        temperatures = np.append(t, temperatures)
    return int(np.min(temperatures)), int(np.max(temperatures)), int(np.mean(temperatures))


def is_raining(hourly_data):
    rain = False
    for item in hourly_data:
        if item["weather"][0]["main"] in ["Rain", "Thunderstorm", "Drizzle"]:
            rain = True
            break
    return rain
