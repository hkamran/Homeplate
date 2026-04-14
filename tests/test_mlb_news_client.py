from unittest.mock import MagicMock, patch

import pytest

from app.clients.mlb_news_client import MLBNewsClient
from tests.conftest import NullDiskCache

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>MLB News</title>
    <item>
        <title>Story One</title>
        <description>Description one</description>
        <link>https://mlb.com/news/story-one</link>
        <pubDate>Mon, 14 Apr 2026 12:00:00 GMT</pubDate>
        <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Alice Smith</dc:creator>
        <image href="https://img.mlbstatic.com/image1.jpg"/>
    </item>
    <item>
        <title>Story Two</title>
        <description>Description two</description>
        <link>https://mlb.com/news/story-two</link>
        <pubDate>Tue, 15 Apr 2026 08:00:00 GMT</pubDate>
        <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Bob Jones</dc:creator>
        <image href="https://img.mlbstatic.com/image2.jpg"/>
    </item>
</channel>
</rss>"""

SAMPLE_RSS_NO_IMAGE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <item>
        <title>No Image Story</title>
        <description>Desc</description>
        <link>https://mlb.com/news/no-image</link>
        <pubDate>Mon, 14 Apr 2026 12:00:00 GMT</pubDate>
    </item>
</channel>
</rss>"""


def _mock_response(content):
    mock = MagicMock()
    mock.content = content.encode("utf-8")
    mock.raise_for_status.return_value = None
    return mock


class TestGetMLBNews:
    def test_returns_parsed_entries(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)):
            result = client.get_mlb_news()

        assert len(result) == 2
        assert result[0]["title"] == "Story One"
        assert result[0]["author"] == "Alice Smith"
        assert result[1]["title"] == "Story Two"

    def test_limit_parameter(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)):
            result = client.get_mlb_news(limit=1)

        assert len(result) == 1

    def test_calls_correct_url(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)) as mock_get:
            client.get_mlb_news()

        mock_get.assert_called_once_with("https://www.mlb.com/feeds/news/rss.xml", timeout=10)


class TestGetTeamNews:
    def test_returns_team_news(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)):
            result = client.get_team_news("bluejays")

        assert len(result) == 2
        assert result[0]["title"] == "Story One"

    def test_calls_team_url(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)) as mock_get:
            client.get_team_news("yankees")

        mock_get.assert_called_once_with("https://www.mlb.com/yankees/feeds/news/rss.xml", timeout=10)

    def test_limit_parameter(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)):
            result = client.get_team_news("bluejays", limit=1)

        assert len(result) == 1


class TestEntryParsing:
    def test_parses_all_fields(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)):
            result = client.get_mlb_news()

        article = result[0]
        assert article["title"] == "Story One"
        assert article["description"] == "Description one"
        assert article["link"] == "https://mlb.com/news/story-one"
        assert article["published"] == "Mon, 14 Apr 2026 12:00:00 GMT"
        assert article["author"] == "Alice Smith"
        assert article["image_url"] == "https://img.mlbstatic.com/image1.jpg"

    def test_handles_missing_image(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS_NO_IMAGE)):
            result = client.get_mlb_news()

        assert result[0]["image_url"] is None

    def test_handles_missing_author(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS_NO_IMAGE)):
            result = client.get_mlb_news()

        assert result[0]["author"] == ""


class TestCaching:
    def test_caches_feed_results(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)) as mock_get:
            client.get_mlb_news()
            client.get_mlb_news()

        assert mock_get.call_count == 1

    def test_different_urls_not_cached(self):
        client = MLBNewsClient(disk_cache=NullDiskCache())
        with patch.object(client._session, "get", return_value=_mock_response(SAMPLE_RSS)) as mock_get:
            client.get_team_news("bluejays")
            client.get_team_news("yankees")

        assert mock_get.call_count == 2
