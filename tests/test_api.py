from datetime import datetime, timezone

import urllib3
from dateutil import parser

from service import api


def test_get_news_api():
    """
    Test if news api is functional
    """
    urllib3.disable_warnings()
    news_feed = api.get_news_stories()
    last_update = parser.isoparse(news_feed["channel"]["updated"]).date()
    assert news_feed["channel"]["title"] == "Deutsche Welle"
    assert last_update == datetime.now(timezone.utc).date()


def test_get_rapla():
    """
    Tests if rapla api is available
    """
    urllib3.disable_warnings()
    data = api.get_rapla()
    assert data.status_code == 200
    # We expect an error because no key is configured
    assert data.text == "Error parsing rapla timetable."


def test_get_quote():
    """
    Test if quote api is functional
    """
    urllib3.disable_warnings()
    quote = api.get_quote(seed=42)
    assert quote["author"] == "Pearl Buck"
    assert quote["text"] == "One faces the future with ones past."


def test_get_weather_forecast():
    """
    Test if weather api is available
    """
    urllib3.disable_warnings()
    response = api.get_weather_forecast(0, 0)
    # We expect 401 because no key is configured
    assert response.status_code == 401
    assert response.json()["message"].startswith("Invalid API key.")


def test_get_air_pollution():
    """
    Test if air pollution api is available
    """
    urllib3.disable_warnings()
    response = api.get_air_pollution(0, 0)
    # We expect 401 because no key is configured
    assert response.status_code == 401
    assert response.json()["message"].startswith("Invalid API key.")


def test_get_wikipedia_extract():
    """
    Test if wikipedia api is functional
    """
    urllib3.disable_warnings()
    response = api.get_wikipedia_extract("Unit testing")
    extract = response.json()["query"]["pages"]["222828"]["extract"]
    assert response.status_code == 200
    assert extract.startswith("In computer programming, unit testing is a software testing method")


def test_get_gym_utilization():
    """
    Test if gym utilization api is functional
    """
    urllib3.disable_warnings()
    mc_fit_stuttgart = "1731421430"
    response = api.get_gym_utilization(mc_fit_stuttgart)
    data = response.json()
    test_utilization = int(data["items"][0]["percentage"])
    assert response.status_code == 200
    assert test_utilization >= 0
    assert test_utilization <= 100


def test_get_covid_stats():
    """
    Test if covid api is functional
    """
    urllib3.disable_warnings()
    ags_stuttgart = "08111"
    response = api.get_covid_stats(ags_stuttgart)
    data = response.json()["data"]
    city = data[ags_stuttgart]["name"]
    incidence = data[ags_stuttgart]["weekIncidence"]
    assert city == "Stuttgart"
    assert isinstance(incidence, float)


def test_get_youtube_search():
    """
    Test if youtube api is available
    """
    urllib3.disable_warnings()
    response = api.get_youtube_search("Home workout")
    # We expect 400 because no key is configured
    assert response.status_code == 400
    assert response.json()["error"]["message"].startswith("API key not valid")


def test_get_bestselling_books():
    """
    Test if NYT books api is available
    """
    urllib3.disable_warnings()
    response = api.get_bestselling_books()
    # We expect 401 because no key is configured
    assert response.status_code == 401


def test_get_travel_summary():
    """
    Test if routing api is available
    """
    urllib3.disable_warnings()
    response = api.get_travel_summary(0, 0, 1, 1)
    # We expect 401 because no key is configured
    assert response.status_code == 401
    assert response.json()["error_description"] == "apiKey invalid. apiKey not found."
