import json
import os
import random
from typing import Final

from service import api, utility
from database.database import Database
from datetime import datetime, date, timedelta

with open(os.path.join(os.path.dirname(__file__), '../database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)


def load_data(session_id: str):
    """
    Load all required data for the Habit Tracker usecase.
    :return: Dict with rapla, video, book, and quote data
    """

    sleep_time: Final = 8

    quote_data = api.get_quote()
    quote, _ = utility.parse_quote(quote_data)

    yt_data = api.get_youtube_search("10 min meditation english").json()
    yt = utility.parse_youtube_search(yt_data)
    r = random.randrange(0, 10)
    video = {
        "title": yt[r]["title"],
    }

    book_data = api.get_bestselling_books().json()
    books = utility.parse_bestselling_books(book_data)
    r = random.randrange(0, 10)
    book = f"'{books[r]['title'].title()}' by {books[r]['author']}"

    prefs = Database.get_instance().load_prefs(session_id)

    wakeup_time_str = prefs['wakeup_time'] if prefs else default_user_prefs.get("wakeup_time")
    wakeup_time = datetime.strptime(wakeup_time_str, "%H:%M").time()
    bed_time = (datetime.combine(date(1, 1, 2), wakeup_time) - timedelta(hours=sleep_time)).time()
    bed_time = bed_time.strftime("%I:%M%p")
    now_time = (datetime.utcnow() + timedelta(hours=int(os.environ.get("TIMEZONE")))).time().strftime("%I:%M%p")

    rapla_next_lecture = None
    rapla_data = api.get_rapla().json()
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.replace(hour=5, minute=0)
    events = utility.get_events(rapla_data, tomorrow)
    if "rapla_next_lecture" in events.keys():
        rapla_next_lecture = events["rapla_next_lecture"]

    return {
        "quote": quote,
        "book": book,
        "bed_time": bed_time,
        "now": now_time,
        "rapla_next_lecture": rapla_next_lecture,
        "video": video
    }
