import os
import re
from datetime import datetime, timedelta

import numpy as np
# TODO for debugging date:
# from dateutil.tz import tzutc
from dateutil import parser

# Two different scopes to deal with: Python console and flask
try:
    import URLS
except ModuleNotFoundError:
    from service import URLS


def parse_travel_summary(travel_data):
    """
    Parse the routing api response
    :param travel_data: api response as json
    :return: travel summary containing length_km and duration
    """
    data = travel_data["routes"][0]["sections"][0]["travelSummary"]
    hours, remainder = divmod(data["duration"], 3600)
    minutes, _ = divmod(remainder, 60)
    travel_summary = {
        "length_km": int(data["length"] / 1000),
        "duration": f"{hours} hours {minutes} minutes"
    }
    return travel_summary


def parse_bestselling_books(book_data):
    """
    Parse book api response
    :param book_data: api response as json
    :return: List of books with title, author, description, and cover image
    """
    books = []
    for b in book_data["results"]["books"]:
        book = {
            "title": b["title"],
            "author": b["author"],
            "description": b["description"],
            "image": b["book_image"]
        }
        books.append(book)
    return books


def parse_youtube_search(youtube_data):
    """
    Parse youtube api response
    :param youtube_data: api response as json
    :return: List of videos with title, url, and thumbnail
    """
    results = []
    for v in youtube_data["items"]:
        video = {
            "url": f"{URLS.YT_VIDEO_BASE}{v['id']['videoId']}",
            "thumbnail": v["snippet"]["thumbnails"]["high"]["url"],
            "title": v['snippet']['title']
        }
        results.append(video)
    return results


def parse_gym_utilization(gym_data):
    """
    Parse gym api response
    :param gym_data: api response as json
    :return: utilization percentage
    """
    percentage = 0
    for entry in gym_data["items"]:
        if entry["isCurrent"]:
            percentage = entry["percentage"]
    return percentage


def parse_wikipedia_extract(wiki_data):
    """
    Parse wikipedia api response
    :param wiki_data: api response as json
    :return: Extract as string
    """
    pages = wiki_data["query"]["pages"]
    page_id = None
    for key in pages:
        page_id = key
        break
    extract = str(pages[page_id]["extract"])
    # Remove nested parentheses
    for i in range(0, 5):
        extract = re.sub(r"\([^(]+?\)", "", extract)
        if extract.find("(") == -1:
            break
    return extract


def parse_quote(quote_data):
    """
    Parse quote data
    :param quote_data: api response as json
    :return: quote, author
    """
    author = quote_data["author"]
    quote = quote_data["text"]
    return quote, author


def parse_air_pollution(air_pol_data):
    """
    Parse air quality api response
    :param air_pol_data: api response as json
    :return: Air quality as readable string
    """
    aqi_numeric = air_pol_data["list"][0]["main"]["aqi"]
    aqi_map = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }
    aqi = aqi_map.get(aqi_numeric, "not available")
    return aqi


def parse_news_headlines(news_data, count=1):
    """
    Parse news api response to return headlines
    :param news_data: api response as json
    :param count: Amount of news headlines
    :return: news headlines
    """
    stories = news_data["entries"]
    headlines = [stories[i]["title"] for i in range(0, count)]
    return headlines


def parse_news_abstract(news_data, index=0):
    """
    Parse news api response to return news summary
    :param news_data: api response as json
    :param index: index of the news article
    :return: title, abstract
    """
    stories = news_data["entries"]
    title = stories[index]["title"]
    abstract = stories[index]["summary"]
    return title, abstract


def parse_covid_situation(covid_data, ags):
    """
    Parse covid api data
    :param covid_data: api response as json
    :param ags: AGS key for the specific location
    :return: weekly incidence
    """
    week_incidence = covid_data["data"][str(ags)]["weekIncidence"]
    return f"{week_incidence:.1f}"


def parse_date(string):
    """
    Parse a date and time string to datetime object
    :param string: date and time string
    :return: datetime object
    """
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
    date -= timedelta(hours=int(os.environ.get("TIMEZONE")))  # date to utc
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
    """
    Convert the timedelta between two datetime objects to human-readable form
    :param datetime1: First datetime
    :param datetime2: Second datetime
    :return: timedelta as human-readable string
    """
    delta = datetime1 - datetime2 if datetime1 >= datetime2 else datetime2 - datetime1
    minutes, _ = divmod(delta.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    hours, minutes = int(hours), int(minutes)
    string = f"{hours} hours" if hours > 1 else f"{hours} hour" if hours == 1 else ""
    string += " and " if hours > 0 and minutes > 0 else ""
    string += f"{minutes} minutes" if minutes > 1 else f"{minutes} minute" if minutes == 1 else ""
    return string if string != "" else "now"


def get_days_until_two_off(date=datetime.now()):
    """
    You are free "today / in one day / in 3 days" for a two day trip
    :param date:
    :return: "today / in one day / in 3 days"
    """
    delta = 5 - date.weekday() if date.weekday() != 6 else 6
    string = ""
    if delta == 0:
        string += "today"
    elif delta == 1:
        string += "in one day"
    else:
        string += f"in {delta} days"

    return string


def lecture_titles_to_sentence(lecture_titles: list):
    """
    Parse list of lecture titles to sentence
    :param lecture_titles: List of lecture titles
    :return: List as natural language enumeration
    """
    if len(lecture_titles) >= 3:
        last_lecture = lecture_titles.pop()
        return "lectures are " + ", ".join(lecture_titles) + f", and {last_lecture}"
    elif len(lecture_titles) == 2:
        return "lectures are " + f"{lecture_titles[0]} and {lecture_titles[1]}"
    elif len(lecture_titles) == 1:
        return "lecture is " + lecture_titles[0]
    else:
        return ""


def parse_lecture_title(title):
    """
    Parse lecture title
    :param title: Lecture title from rapla
    :return: Lecture title without unnecessary
    """
    return title.replace(" [ Teiln]", "").replace(" - Online", "").replace(" [19 Teiln]", "").rstrip()


def parse_lecture_type(event_type):
    """
    Parse lecture type
    :param event_type: rapla event time
    :return: 'online' or 'on site'
    """
    return 'online' if event_type == "Online-Format (ohne Raumbelegung)" else "on site"


def get_current_weather(weather_data):
    """
    Parse weather api response
    :param weather_data: api response as json
    :return: return weather dict with min, max, current, mean, rain, and description
    """
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
    """
    Parse hourly weather data to get 24h temperature points
    :param hourly_data: hourly_data return by weather api
    :return: min, max, and mean temperature for the next 24h
    """
    temperatures = np.array([])
    for item in hourly_data:
        t = item["temp"]
        temperatures = np.append(t, temperatures)
    return int(np.min(temperatures)), int(np.max(temperatures)), int(np.mean(temperatures))


def is_raining(hourly_data):
    """
    Parse hourly weather data check if there is rain forecasted
    :param hourly_data: hourly_data return by weather api
    :return: boolean if rain is forecasted in the next 24h
    """
    rain = False
    for item in hourly_data:
        if item["weather"][0]["main"] in ["Rain", "Thunderstorm", "Drizzle"]:
            rain = True
            break
    return rain
