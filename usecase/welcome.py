from service import utility


def get_welcome_text():
    """
    1. Rapla
    2. Wetter
    3. Covid Incidence
    4. News
    :return:
    """
    rapla = utility.get_first_event()
    weather = utility.get_current_weather()
    # covid = utility.get_covid_situation()

    return {
        "data": [
            rapla,
            weather
        ]
    }
