from unittest.mock import patch

from app.services.standings import get_ordered_standings, get_split_pct, get_team_record


class TestGetSplitPct:
    def test_finds_matching_type(self):
        splits = [
            {"type": "home", "pct": ".666"},
            {"type": "away", "pct": ".333"},
        ]
        assert get_split_pct(splits, "home") == ".666"
        assert get_split_pct(splits, "away") == ".333"

    def test_returns_dash_when_not_found(self):
        splits = [{"type": "home", "pct": ".500"}]
        assert get_split_pct(splits, "extraInning") == "-"

    def test_empty_splits(self):
        assert get_split_pct([], "home") == "-"

    def test_missing_pct_field(self):
        splits = [{"type": "home"}]
        assert get_split_pct(splits, "home") == "-"


class TestGetOrderedStandings:
    def test_orders_by_division(self):
        records = [
            {"division": {"id": 204}, "name": "NL East"},
            {"division": {"id": 201}, "name": "AL East"},
            {"division": {"id": 200}, "name": "AL West"},
        ]
        with patch("app.services.standings.mlb_client") as mock_client:
            mock_client.get_standings.return_value = records
            result = get_ordered_standings()

        # DIVISION_ORDER: 201, 202, 200, 204, 205, 203
        assert result[0]["name"] == "AL East"
        assert result[1]["name"] == "AL West"
        assert result[2]["name"] == "NL East"

    def test_skips_missing_divisions(self):
        records = [{"division": {"id": 201}, "name": "AL East"}]
        with patch("app.services.standings.mlb_client") as mock_client:
            mock_client.get_standings.return_value = records
            result = get_ordered_standings()

        assert len(result) == 1

    def test_returns_empty_on_error(self):
        with patch("app.services.standings.mlb_client") as mock_client:
            mock_client.get_standings.side_effect = Exception("API down")
            result = get_ordered_standings()

        assert result == []


class TestGetTeamRecord:
    def test_finds_team_record(self):
        records = [
            {
                "teamRecords": [
                    {"team": {"id": 141}, "wins": 90, "losses": 72},
                    {"team": {"id": 147}, "wins": 85, "losses": 77},
                ]
            }
        ]
        with patch("app.services.standings.mlb_client") as mock_client:
            mock_client.get_standings.return_value = records
            result = get_team_record(141)

        assert result["wins"] == 90

    def test_returns_none_when_not_found(self):
        records = [{"teamRecords": [{"team": {"id": 141}}]}]
        with patch("app.services.standings.mlb_client") as mock_client:
            mock_client.get_standings.return_value = records
            result = get_team_record(999)

        assert result is None

    def test_returns_none_on_error(self):
        with patch("app.services.standings.mlb_client") as mock_client:
            mock_client.get_standings.side_effect = Exception("API down")
            result = get_team_record(141)

        assert result is None
