from service import utility


def get_welcome_text():
    """
    1. Rapla
    2. Wetter
    3. Covid Incidence
    4. News
    :return: Initial welcome text
    """
    rapla = utility.get_first_event()
    weather = utility.get_current_weather()
    covid = utility.get_covid_situation()
    news = utility.get_new_stories()

    tts = f"Good Morning! Time to start your day. {rapla['tts']} {weather['tts']} {covid['tts']} {news['tts']}"
    return {
        "tts": tts,
        "weather-icon": weather["icon"]
    }
