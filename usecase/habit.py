"""
Use Case 2
- Quote $quote
- Book $book
- Bed time $now?, $bed_time
"""
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
    sleep_time: Final = 8

    quote_data = api.get_quote()
    quote, _ = utility.parse_quote(quote_data)

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

    return {
        "quote": quote,
        "book": book,
        "bed_time": bed_time,
        "now": now_time
    }
