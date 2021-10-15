from service import service


def test_news():
    feed = service.get_news_stories()
    assert type(feed) is not str
    assert type(feed["entries"][0]["title"]) is str
