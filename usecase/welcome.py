from service import utility


def get_welcome_text():
    """
    1. Rapla
    2. Wetter
    3. Covid Incidence
    :return: Initial welcome text
    """
    rapla = utility.get_next_event()
    weather = utility.get_current_weather()
    covid = utility.get_covid_situation()

    tts = f"Good Morning! Time to start your day. {rapla['tts']} {weather['tts']} {covid['tts']}"
    return {
        "tts": tts,
        "weather-icon": weather["icon"]
    }
