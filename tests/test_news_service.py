from unittest.mock import patch

from app.services.news import get_mlb_news, get_team_news


class TestGetMlbNews:
    def test_returns_news(self):
        articles = [{"title": "Story 1"}, {"title": "Story 2"}]
        with patch("app.services.news.news_client") as mock_client:
            mock_client.get_mlb_news.return_value = articles
            result = get_mlb_news(limit=2)

        assert len(result) == 2
        mock_client.get_mlb_news.assert_called_once_with(limit=2)

    def test_returns_empty_on_error(self):
        with patch("app.services.news.news_client") as mock_client:
            mock_client.get_mlb_news.side_effect = Exception("RSS down")
            result = get_mlb_news()

        assert result == []


class TestGetTeamNews:
    def test_returns_team_news(self):
        articles = [{"title": "Blue Jays win"}]
        with patch("app.services.news.news_client") as mock_client:
            mock_client.get_team_news.return_value = articles
            result = get_team_news(141, limit=4)  # 141 = TOR -> slug "bluejays"

        assert len(result) == 1
        mock_client.get_team_news.assert_called_once_with("bluejays", limit=4)

    def test_returns_empty_for_unknown_team(self):
        result = get_team_news(99999)
        assert result == []

    def test_returns_empty_on_error(self):
        with patch("app.services.news.news_client") as mock_client:
            mock_client.get_team_news.side_effect = Exception("RSS down")
            result = get_team_news(141)

        assert result == []
