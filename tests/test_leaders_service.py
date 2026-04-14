from unittest.mock import patch

from app.services.leaders import (
    _filter_leaders,
    get_hitting_leaders,
    get_landing_leaders,
    get_pitching_leaders,
)


class TestFilterLeaders:
    def test_filters_by_stat_group(self):
        leaders = [
            {"leaderCategory": "homeRuns", "statGroup": "hitting", "leaders": []},
            {"leaderCategory": "homeRuns", "statGroup": "pitching", "leaders": []},
            {"leaderCategory": "homeRuns", "statGroup": "catching", "leaders": []},
        ]
        stat_groups = {"homeRuns": "hitting"}
        result = _filter_leaders(leaders, stat_groups)

        assert len(result) == 1
        assert result[0]["statGroup"] == "hitting"

    def test_filters_multiple_categories(self):
        leaders = [
            {"leaderCategory": "homeRuns", "statGroup": "hitting"},
            {"leaderCategory": "strikeouts", "statGroup": "pitching"},
            {"leaderCategory": "strikeouts", "statGroup": "hitting"},
        ]
        stat_groups = {"homeRuns": "hitting", "strikeouts": "pitching"}
        result = _filter_leaders(leaders, stat_groups)

        assert len(result) == 2

    def test_returns_empty_when_no_match(self):
        leaders = [{"leaderCategory": "homeRuns", "statGroup": "catching"}]
        stat_groups = {"homeRuns": "hitting"}
        result = _filter_leaders(leaders, stat_groups)

        assert result == []

    def test_empty_input(self):
        assert _filter_leaders([], {"homeRuns": "hitting"}) == []


class TestGetLandingLeaders:
    def test_returns_filtered_leaders(self):
        api_response = [
            {"leaderCategory": "homeRuns", "statGroup": "hitting", "leaders": [{"rank": 1}]},
            {"leaderCategory": "homeRuns", "statGroup": "catching", "leaders": [{"rank": 1}]},
            {"leaderCategory": "strikeouts", "statGroup": "pitching", "leaders": [{"rank": 1}]},
        ]
        with patch("app.services.leaders.mlb_client") as mock_client:
            mock_client.get_stat_leaders.return_value = api_response
            result = get_landing_leaders(limit=1)

        assert len(result) == 2

    def test_returns_empty_on_error(self):
        with patch("app.services.leaders.mlb_client") as mock_client:
            mock_client.get_stat_leaders.side_effect = Exception("API down")
            result = get_landing_leaders()

        assert result == []


class TestGetHittingLeaders:
    def test_calls_with_hitting_categories(self):
        with patch("app.services.leaders.mlb_client") as mock_client:
            mock_client.get_stat_leaders.return_value = []
            get_hitting_leaders(limit=5)

        args = mock_client.get_stat_leaders.call_args
        categories = args[0][0]
        assert "homeRuns" in categories
        assert "battingAverage" in categories

    def test_returns_empty_on_error(self):
        with patch("app.services.leaders.mlb_client") as mock_client:
            mock_client.get_stat_leaders.side_effect = Exception("API down")
            result = get_hitting_leaders()

        assert result == []


class TestGetPitchingLeaders:
    def test_calls_with_pitching_categories(self):
        with patch("app.services.leaders.mlb_client") as mock_client:
            mock_client.get_stat_leaders.return_value = []
            get_pitching_leaders(limit=5)

        args = mock_client.get_stat_leaders.call_args
        categories = args[0][0]
        assert "earnedRunAverage" in categories
        assert "strikeOuts" in categories

    def test_returns_empty_on_error(self):
        with patch("app.services.leaders.mlb_client") as mock_client:
            mock_client.get_stat_leaders.side_effect = Exception("API down")
            result = get_pitching_leaders()

        assert result == []
