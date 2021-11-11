from datetime import datetime, timezone, timedelta
from typing import Final

import numpy as np
# TODO for debugging date:
# from dateutil.tz import tzutc
from dateutil import parser

# Two different scopes to deal with: Python console and flask
try:
    import URLS
except ModuleNotFoundError:
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


def parse_date(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_events(rapla_data, date=datetime.now()):  # Debug: datetime(2021, 11, 11, 10)
    """
    Get current lecture (+ time until it ends as string),
    events of the passed day,
    and next lecture (+ time until then as string)
    :param rapla_data: rapla data from rapla API
    :param date: date object, defaults to now
    :return: dict with keys 'rapla_lectures', 'rapla_next_lecture'.'title', 'rapla_next_lecture'.'start',
    'rapla_current_lecture'.'title', 'rapla_current_lecture'.'end'
    """
    current_time_zone: Final = +1
    date -= timedelta(hours=current_time_zone)  # date to utc
    events_of_date = [event for event in rapla_data['events']
                      if parser.isoparse(event['start']).date() == date.date()]
    current_lecture = next((event for event in events_of_date
                            if parse_date(event['start'])
                            <= date <= parse_date(event['end'])),
                           None)
    next_lecture = next((event for event in events_of_date
                         if parse_date(event['start']) >= date), None)

    ret = {}
    if events_of_date:
        ret['rapla_lectures'] = lecture_titles_to_sentence(
            [parse_lecture_title(event['title']) for event in events_of_date])
    if next_lecture:
        ret['rapla_next_lecture'] = {}
        ret['rapla_next_lecture']['title'] = parse_lecture_title(next_lecture['title'])
        ret['rapla_next_lecture']['start'] = timedelta_to_sentence(parse_date(next_lecture['start']), date)
    if current_lecture:
        ret['rapla_current_lecture'] = {}
        ret['rapla_current_lecture']['title'] = parse_lecture_title(current_lecture['title'])
        ret['rapla_current_lecture']['end'] = timedelta_to_sentence(parse_date(current_lecture['end']), date)

    return ret


def timedelta_to_sentence(datetime1, datetime2):
    delta = datetime1 - datetime2 if datetime1 >= datetime2 else datetime2 - datetime1
    minutes, _ = divmod(delta.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    hours, minutes = int(hours), int(minutes)
    string = f"{hours} hours" if hours > 1 else f"{hours} hour" if hours == 1 else ""
    string += " and " if hours > 0 and minutes > 0 else ""
    string += f"{minutes} minutes" if minutes > 1 else f"{minutes} minute" if minutes == 1 else ""
    return string if string != "" else "now"


def lecture_titles_to_sentence(lecture_titles: list):
    if len(lecture_titles) >= 3:
        last_lecture = lecture_titles.pop()
        return "lectures are " + ", ".join(lecture_titles) + f", and {last_lecture}"
    elif len(lecture_titles) == 2:
        return "lectures are " + f"{lecture_titles[0]} and {lecture_titles[1]}"
    elif len(lecture_titles) == 1:
        return "lecture is " + lecture_titles[0]
    else:
        return ""


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
