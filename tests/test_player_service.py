from unittest.mock import patch

from app.services.player import (
    _add_calculated_stats,
    _extract_stats_by_type,
    get_game_log,
    get_player,
    get_player_stats,
    is_pitcher,
)


class TestIsPitcher:
    def test_pitcher(self):
        player = {"primaryPosition": {"type": "Pitcher"}}
        assert is_pitcher(player) is True

    def test_hitter(self):
        player = {"primaryPosition": {"type": "Infielder"}}
        assert is_pitcher(player) is False

    def test_missing_position(self):
        assert is_pitcher({}) is False


class TestExtractStatsByType:
    def test_finds_matching_type(self):
        stats = [
            {"type": {"displayName": "yearByYear"}, "group": {"displayName": "hitting"}, "splits": [{"season": "2024"}]},
            {"type": {"displayName": "career"}, "group": {"displayName": "hitting"}, "splits": [{"season": "career"}]},
        ]
        result = _extract_stats_by_type(stats, "yearByYear", "hitting")
        assert len(result) == 1
        assert result[0]["season"] == "2024"

    def test_filters_by_group(self):
        stats = [
            {"type": {"displayName": "yearByYear"}, "group": {"displayName": "hitting"}, "splits": [1]},
            {"type": {"displayName": "yearByYear"}, "group": {"displayName": "pitching"}, "splits": [2]},
        ]
        result = _extract_stats_by_type(stats, "yearByYear", "pitching")
        assert result == [2]

    def test_returns_empty_when_not_found(self):
        stats = [{"type": {"displayName": "career"}, "group": {"displayName": "hitting"}, "splits": []}]
        result = _extract_stats_by_type(stats, "projected", "hitting")
        assert result == []

    def test_empty_stats_list(self):
        assert _extract_stats_by_type([], "yearByYear") == []

    def test_no_group_filter(self):
        stats = [
            {"type": {"displayName": "career"}, "group": {"displayName": "hitting"}, "splits": [{"data": 1}]},
        ]
        result = _extract_stats_by_type(stats, "career")
        assert len(result) == 1


class TestAddCalculatedStats:
    def test_hitter_stats(self):
        stat = {"plateAppearances": 500, "strikeOuts": 100, "baseOnBalls": 50}
        _add_calculated_stats(stat, is_pitcher=False)

        assert stat["soPct"] == 20.0
        assert stat["bbPct"] == 10.0

    def test_pitcher_stats(self):
        stat = {"battersFaced": 400, "strikeOuts": 120, "baseOnBalls": 40}
        _add_calculated_stats(stat, is_pitcher=True)

        assert stat["soPct"] == 30.0
        assert stat["bbPct"] == 10.0

    def test_zero_plate_appearances(self):
        stat = {"plateAppearances": 0, "strikeOuts": 0, "baseOnBalls": 0}
        _add_calculated_stats(stat, is_pitcher=False)

        assert stat["soPct"] is None
        assert stat["bbPct"] is None

    def test_missing_fields_default_to_zero(self):
        stat = {}
        _add_calculated_stats(stat, is_pitcher=False)

        assert stat["soPct"] is None
        assert stat["bbPct"] is None


class TestGetPlayer:
    def test_returns_player(self):
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player.return_value = {"id": 665926, "fullName": "Giménez"}
            result = get_player(665926)

        assert result["fullName"] == "Giménez"

    def test_returns_none(self):
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player.return_value = None
            result = get_player(999)

        assert result is None


class TestGetPlayerStats:
    def test_returns_processed_stats(self):
        api_data = {
            "id": 665926,
            "stats": [
                {
                    "type": {"displayName": "yearByYear"},
                    "group": {"displayName": "hitting"},
                    "splits": [
                        {"season": "2024", "stat": {"plateAppearances": 633, "strikeOuts": 97, "baseOnBalls": 26}},
                    ],
                },
                {
                    "type": {"displayName": "career"},
                    "group": {"displayName": "hitting"},
                    "splits": [
                        {"stat": {"plateAppearances": 2541, "strikeOuts": 472, "baseOnBalls": 137}},
                    ],
                },
            ],
        }
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player_stats.return_value = api_data
            player_data, seasons, projected, career = get_player_stats(665926, False)

        assert len(seasons) == 1
        assert seasons[0]["stat"]["soPct"] == 15.3
        assert career["stat"]["bbPct"] == 5.4
        assert projected is None

    def test_returns_empty_on_error(self):
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player_stats.side_effect = Exception("API down")
            player_data, seasons, projected, career = get_player_stats(665926, False)

        assert player_data is None
        assert seasons == []
        assert projected is None
        assert career is None

    def test_returns_empty_when_no_data(self):
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player_stats.return_value = None
            player_data, seasons, projected, career = get_player_stats(665926, False)

        assert player_data is None
        assert seasons == []


class TestGetGameLog:
    def test_returns_last_n_games(self):
        game_log_data = {
            "stats": [
                {
                    "type": {"displayName": "gameLog"},
                    "splits": [
                        {"date": f"2026-04-{i:02d}"} for i in range(1, 11)
                    ],
                }
            ]
        }
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player_game_log.return_value = game_log_data
            result = get_game_log(665926, False, limit=7)

        assert len(result) == 7
        assert result[0]["date"] == "2026-04-01"

    def test_returns_empty_on_error(self):
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player_game_log.side_effect = Exception("API down")
            result = get_game_log(665926, False)

        assert result == []

    def test_returns_empty_when_no_game_log(self):
        with patch("app.services.player.mlb_client") as mock_client:
            mock_client.get_player_game_log.return_value = {"stats": []}
            result = get_game_log(665926, False)

        assert result == []
