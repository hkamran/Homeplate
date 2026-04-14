from unittest.mock import patch

from app.services.team import get_roster_split, get_team


class TestGetTeam:
    def test_returns_team_info(self):
        with patch("app.services.team.mlb_client") as mock_client:
            mock_client.get_team.return_value = {"id": 141, "name": "Toronto Blue Jays"}
            result = get_team(141)

        assert result["name"] == "Toronto Blue Jays"

    def test_returns_none_when_not_found(self):
        with patch("app.services.team.mlb_client") as mock_client:
            mock_client.get_team.return_value = None
            result = get_team(999)

        assert result is None


class TestGetRosterSplit:
    def _make_roster_entry(self, name, pos_type, pos_abbr, jersey="0", stats=None):
        person = {"id": 1, "fullName": name, "stats": []}
        if stats:
            person["stats"] = [{"type": {"displayName": "season"}, "splits": [{"stat": stats}]}]
        return {
            "person": person,
            "position": {"type": pos_type, "abbreviation": pos_abbr},
            "jerseyNumber": jersey,
        }

    def test_splits_hitters_and_pitchers(self):
        roster = [
            self._make_roster_entry("Batter One", "Infielder", "SS"),
            self._make_roster_entry("Pitcher One", "Pitcher", "SP"),
            self._make_roster_entry("Batter Two", "Outfielder", "CF"),
        ]
        with patch("app.services.team.mlb_client") as mock_client:
            mock_client.get_roster_with_stats.return_value = roster
            hitters, pitchers = get_roster_split(141)

        assert len(hitters) == 2
        assert len(pitchers) == 1
        assert hitters[0]["name"] == "Batter One"
        assert pitchers[0]["name"] == "Pitcher One"

    def test_extracts_season_stats(self):
        roster = [
            self._make_roster_entry(
                "Slugger",
                "Infielder",
                "1B",
                stats={"homeRuns": 25, "avg": ".300"},
            ),
        ]
        with patch("app.services.team.mlb_client") as mock_client:
            mock_client.get_roster_with_stats.return_value = roster
            hitters, _ = get_roster_split(141)

        assert hitters[0]["stats"]["homeRuns"] == 25
        assert hitters[0]["stats"]["avg"] == ".300"

    def test_empty_stats_when_no_season_data(self):
        roster = [self._make_roster_entry("Rookie", "Infielder", "2B")]
        with patch("app.services.team.mlb_client") as mock_client:
            mock_client.get_roster_with_stats.return_value = roster
            hitters, _ = get_roster_split(141)

        assert hitters[0]["stats"] == {}

    def test_returns_empty_on_error(self):
        with patch("app.services.team.mlb_client") as mock_client:
            mock_client.get_roster_with_stats.side_effect = Exception("API down")
            hitters, pitchers = get_roster_split(141)

        assert hitters == []
        assert pitchers == []

    def test_preserves_player_info(self):
        roster = [
            self._make_roster_entry("Test Player", "Catcher", "C", jersey="27"),
        ]
        with patch("app.services.team.mlb_client") as mock_client:
            mock_client.get_roster_with_stats.return_value = roster
            hitters, _ = get_roster_split(141)

        assert hitters[0]["name"] == "Test Player"
        assert hitters[0]["position"] == "C"
        assert hitters[0]["number"] == "27"
