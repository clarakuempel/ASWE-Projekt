import requests
import urllib3

import service.URLS as URLS


def test_get_news_api():
    urllib3.disable_warnings()
    news_api_response = requests.get(f"{URLS.DW_RSS_BASE}-en-all", verify=False)
    # Test if API is available
    assert news_api_response.ok is True
    # Test if API returns XML feed
    assert news_api_response.headers["Content-Type"] == "text/xml; charset=UTF-8"
