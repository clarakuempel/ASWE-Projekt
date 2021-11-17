"""
Use Case 2
- Quote $quote
- Book $book
- Bed time $now?, $bed_time
"""
import random

from service import api, utility


def load_data():
    quote_data = api.get_quote()
    quote, _ = utility.parse_quote(quote_data)

    book_data = api.get_bestselling_books().json()
    books = utility.parse_bestselling_books(book_data)
    r = random.randrange(0, 10)
    book = f"'{books[r]['title'].title()}' by {books[r]['author']}"

    # Todo -> Load database preferences and get "wake up" time to calc $bed_time
    # todo user prefs -> wakeup time
    bed_time = "12 PM"

    return {
        "quote": quote,
        "book": book,
        "bed_time": bed_time
    }
