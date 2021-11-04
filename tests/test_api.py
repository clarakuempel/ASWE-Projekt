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
