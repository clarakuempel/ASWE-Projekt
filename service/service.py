import os

import requests

import exception
from . import URLS


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
        URLS.RAPLA_PARAMETER)
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
        URLS.OWM_WEATHER_BASE + f"?lat={lat}&lon={lon}&exclude={exclude}&appid={api_key}&units={units}&lang={lang}")
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
        URLS.OWM_AQ_BASE + f"?lat={lat}&lon={lon}&appid={api_key}")
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
    :return:
    """
    r = requests.get(
        URLS.SUNRISE_BASE + f"?lat={lat}&lon={lon}&date={date}&formatted=0")
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")


def get_wikipedia_extract(search_title):
    """
    Get the extract of a Wikipedia page. Automatically redirects to synonyms.

    :param search_title: Title of the Wikipedia page
    :return:
    """
    r = requests.get(
        URLS.WIKIPEDIA_BASE + f"&titles={search_title}")
    if r.ok:
        return r.json()
    else:
        raise requests.HTTPError(f"Request not OK: {r.text}")
