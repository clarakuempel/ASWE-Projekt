from datetime import datetime, timezone

import numpy as np
# TODO for debugging date:
# from dateutil.tz import tzutc
from dateutil import parser

from service import URLS


def get_news_headlines(news_data, offset=0):
    stories = news_data["entries"]
    sentence = f"Current headlines for you preferred topics are '{stories[0 + offset]['title']}' and " \
               f"'{stories[1 + offset]['title']}'"
    return {
        "tts": sentence
    }


def get_news_abstract(news_data, index=0):
    stories = news_data["entries"]
    sentence = f"More information about the article '{stories[index]['title']}: {stories[index]['summary']}"
    return {
        "tts": sentence
    }


def get_covid_situation(covid_data, ags):
    week_incidence = covid_data["data"][str(ags)]["weekIncidence"]
    sentence = f"Remember washing your hands, the weekly incidence is at {week_incidence:.1f}."
    return {
        "tts": sentence
    }


def get_event_overview(rapla_data):
    results = []
    next_lecture = None
    is_first_lecture = True
    is_next_lecture = True
    for event in rapla_data["events"]:
        start = parser.isoparse(event["start"])
        date_now = datetime.now(timezone.utc)
        # date_now = datetime(2021, 10, 14, 7, tzinfo=tzutc())
        # TODO: date for debugging: datetime(2021, 10, 14, 5, tzinfo=tzutc())
        if start.date() == date_now.date():
            start_delta = start - date_now
            if start_delta.total_seconds() < 0:
                is_first_lecture = False
                # already started
                end = parser.isoparse(event["end"])
                end_delta = end - date_now
                if end_delta.total_seconds() < 0:
                    # already ended
                    sentence = f"Lecture {parse_lecture_title(event['title'])} is already over."
                else:
                    sentence = f"Lecture {parse_lecture_title(event['title'])} is currently ongoing and " \
                               f"is taking place {parse_lecture_type(event['type'])}."
            else:
                hours, remainder = divmod(start_delta.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                sentence = f"The {'first' if is_first_lecture else 'next'} lecture starts in "
                has_hours = False
                if hours > 0:
                    sentence += f"{int(hours)} hours "
                    has_hours = True
                if minutes > 0:
                    sentence += f"{'and ' if has_hours else ''}{int(minutes)} minutes"
                sentence += f". It is {parse_lecture_title(event['title'])} and " \
                            f"is taking place {parse_lecture_type(event['type'])}."
                if is_next_lecture:
                    next_lecture = sentence
                    is_next_lecture = False
            results.append(sentence)
    if not results:
        results = ["You have no lectures today."]
    return results, next_lecture


def parse_lecture_title(title):
    return title.rstrip().replace(" [ Teiln]", "").replace(" - Online", "").replace(" [19 Teiln]", "")


def parse_lecture_type(event_type):
    return 'online' if event_type == "Online-Format (ohne Raumbelegung)" else "on site"


def get_next_event(rapla_data):
    day_events, next_lecture = get_event_overview(rapla_data)
    sentence = day_events[0] if next_lecture is None else next_lecture
    return {
        "tts": sentence
    }


def get_current_weather(weather_data):
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
