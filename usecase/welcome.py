"""
Use Case1
- Wetter: $weather.rain, $weather.current, $weather.min
- Incidence
- News headlines
- news abstract
- News preference
"""
from service import api, utility


def load_data():
    rapla_lectures = None
    rapla_data = api.get_rapla().json()
    events = utility.get_events(rapla_data)
    if "rapla_lectures" in events.keys():
        rapla_lectures = events["rapla_lectures"]

    weather_data = api.get_weather_forecast(48.783333, 9.183333).json()
    weather, icon = utility.get_current_weather(weather_data)

    covid_data = api.get_covid_stats("08111").json()
    incidence = utility.parse_covid_situation(covid_data, "08111")

    news_data = api.get_news_stories(1)
    news_headlines = utility.parse_news_headlines(news_data, 2)

    preference = "Word Wide news"

    news = {
        "first": {
            "title": news_headlines[0],
            "text": utility.parse_news_abstract(news_data, 0)
        },
        "second": {
            "title": news_headlines[1],
            "text": utility.parse_news_abstract(news_data, 1)
        },
        "preference": preference

    }

    return {
        "weather": {
            "min": weather["min"],
            "max": weather["max"],
            "current": weather["current"],
            "rain": weather["rain"],
            "description": weather["description"]
        },
        "lectures": rapla_lectures,
        "incidence": incidence,
        "news": news,
    }
