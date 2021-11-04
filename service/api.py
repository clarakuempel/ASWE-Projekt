import os
import random

import feedparser
import requests
import warnings

import exception
from . import URLS


def get_quote(seed: int = None, return_seed: bool = False):
    """
    Get inspirational quote.

    :param return_seed: (Optional) If true, used seed is returned as well
    :param seed: (Optional) Seed for random generator to return pre-determined quote (Seed is index of array)
    :return: Quote as dict with keys 'text', 'author', and - if return_seed == True 'seed'
    """
    r = requests.get(
        URLS.QUOTE_BASE, verify=False)
    if r.ok:
        quotes = r.json()
        if seed is not None:
            if seed >= len(quotes):
                warnings.warn(
                    f"Warning: Seed was above or equal length of quotes: {len(quotes)}. "
                    f"Using random quote instead.")
                seed = None
        seed = random.randint(0, len(quotes)) if seed is None else seed
        quote = quotes[seed]
        if return_seed:
            quote["seed"] = seed
        return quote

    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_rapla():
    """
    Get Rapla schedule for the next 7 days
    :return: API response as json
    """
    rapla_key = os.environ.get("RAPLA_KEY")
    if not rapla_key:
        raise exception.InvalidConfiguration("No Rapla key configured")
    r = requests.get(
        URLS.RAPLA_BASE +
        rapla_key +
        URLS.RAPLA_PARAMETER, verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_weather_forecast(lat, lon, exclude="minutely,daily,alerts", units="metric", lang="en"):
    """
    Get the weather forecast for specific location.

    More information https://openweathermap.org/api/one-call-api

    :param lat: Latitude
    :param lon: Longitude
    :param exclude: Exclude forecast categories (optional)
    :param units: Unit of measurement  (optional)
    :param lang: Language  (optional)
    :return: API response as json
    """
    api_key = os.environ.get("OWM_API_KEY")
    if not api_key:
        raise exception.InvalidConfiguration("No OpenWeatherMap api key configured")
    r = requests.get(
        URLS.OWM_WEATHER_BASE + f"?lat={lat}&lon={lon}&exclude={exclude}&appid={api_key}&units={units}&lang={lang}",
        verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_air_pollution(lat, lon):
    """
    Get air quality for a specific location.
    Air Quality Index (AQI) scale 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor

    More information https://openweathermap.org/api/air-pollution

    :param lat: Latitude
    :param lon: Longitude
    :return: API response as json
    """
    api_key = os.environ.get("OWM_API_KEY")
    if not api_key:
        raise exception.InvalidConfiguration("No OpenWeatherMap api key configured")
    r = requests.get(
        URLS.OWM_AQ_BASE + f"?lat={lat}&lon={lon}&appid={api_key}", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_sunrise_sunset(lat, lon, date="today"):
    """
    Get sunrise and sunset information for a specific location.

    More information: https://sunrise-sunset.org/api

    :param lat: Latitude
    :param lon: Longitude
    :param date: Date in YYYY-MM-DD format (optional)
    :return: API response as json
    """
    r = requests.get(
        URLS.SUNRISE_BASE + f"?lat={lat}&lon={lon}&date={date}&formatted=0", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_wikipedia_extract(search_title):
    """
    Get the extract of a Wikipedia page. Automatically redirects to synonyms.

    :param search_title: Title of the Wikipedia page
    :return: API response as json
    """
    r = requests.get(
        URLS.WIKIPEDIA_BASE + f"&titles={search_title}", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_gym_utilization(gym_id):
    """
    Get the 24h utilization for a specific gym
    :param gym_id: Gym id
    :return: API response as json
    """
    r = requests.get(
        URLS.GYM_UTIL_BASE + f"?tx_brastudioprofilesmcfitcom_brastudioprofiles%5BstudioId%5D={gym_id}", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_covid_stats(ags):
    """
    Get covid stats using the Amtliche Gemeindeschlüssel (AGS)
    :param ags: Amtliche Gemeindeschlüssel
    :return: API response as json
    """
    r = requests.get(
        URLS.COVID_BASE + f"{ags}", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_youtube_search(search_term):
    """
    Search for youtube videos. Returns 10 search results.
    :param search_term: Search term
    :return: API response as json
    """
    api_key = os.environ.get("GOOGLE_YT_KEY")
    if not api_key:
        raise exception.InvalidConfiguration("No Google Youtube api key configured")
    r = requests.get(
        URLS.YT_SEARCH_BASE + f"?part=snippet&maxResults=10&q={search_term}&key={api_key}", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_news_stories(topic_key=1):
    """
    Get the Deutsche Welle RSS feed.

    Topics: 1 - All, 2 - Business, 3 - Science, 4 - Sports

    :param topic_key: News Feed topic
    :return:  JSON like object containing RSS fee
    """
    topic_mapping = {
        1: "-en-all",
        2: "-en-bus",
        3: "_en_science",
        4: "-en-sports"
    }
    if topic_key not in topic_mapping.keys():
        topic_key = 1
    d = feedparser.parse(f"{URLS.DW_RSS_BASE}{topic_mapping[topic_key]}")
    return d


def get_bestselling_books(fiction=True):
    """
    Get the The New York Times Best Sellers lists for either fiction or non-fiction books.
    :param fiction: Fiction or non-fiction books (optional, default=True)
    :return: API response as json
    """
    api_key = os.environ.get("NYT_KEY")
    if not api_key:
        raise exception.InvalidConfiguration("No NYT API key configured")
    if fiction:
        list_name = "hardcover-fiction"
    else:
        list_name = "hardcover-nonfiction"
    r = requests.get(
        URLS.NYT_BOOKS + f"{list_name}.json?api-key={api_key}", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_travel_summary(org_lat, org_lon, dest_lat, dest_lon):
    """
    Get the travel summary for a car route
    :param org_lat: Origin latitude
    :param org_lon: Origin longitude
    :param dest_lat: Destination latitude
    :param dest_lon: Destination longitude
    :return: API response as json
    """
    api_key = os.environ.get("HERE_API_KEY")
    if not api_key:
        raise exception.InvalidConfiguration("No HERE API key configured")
    r = requests.get(
        URLS.HERE_ROUTING_BASE + f"?transportMode=car&origin={org_lat},{org_lon}&destination={dest_lat},{dest_lon}"
                                 f"&return=travelSummary&apiKey={api_key}", verify=False)
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")