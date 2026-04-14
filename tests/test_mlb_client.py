from unittest.mock import MagicMock, patch

import pytest

from app.clients.mlb_client import MLBClient
from tests.conftest import NullDiskCache


@pytest.fixture
def client():
    return MLBClient(cache_ttl=60, disk_cache=NullDiskCache())


def _mock_response(json_data, status_code=200):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.status_code = status_code
    mock.raise_for_status.return_value = None
    return mock


class TestGetTeams:
    def test_returns_teams_list(self, client):
        teams_data = {
            "teams": [
                {"id": 141, "name": "Toronto Blue Jays"},
                {"id": 147, "name": "New York Yankees"},
            ]
        }
        with patch.object(client._session, "get", return_value=_mock_response(teams_data)):
            result = client.get_teams()

        assert len(result) == 2
        assert result[0]["id"] == 141
        assert result[1]["name"] == "New York Yankees"

    def test_calls_correct_endpoint(self, client):
        teams_data = {"teams": []}
        with patch.object(client._session, "get", return_value=_mock_response(teams_data)) as mock_get:
            client.get_teams()

        mock_get.assert_called_once_with(
            "https://statsapi.mlb.com/api/v1/teams",
            params={"sportId": 1},
            timeout=10,
        )


class TestGetTeam:
    def test_returns_single_team(self, client):
        team_data = {"teams": [{"id": 141, "name": "Toronto Blue Jays"}]}
        with patch.object(client._session, "get", return_value=_mock_response(team_data)):
            result = client.get_team(141)

        assert result["id"] == 141

    def test_returns_none_for_empty(self, client):
        with patch.object(client._session, "get", return_value=_mock_response({"teams": []})):
            result = client.get_team(999)

        assert result is None


class TestGetStandings:
    def test_returns_division_records(self, client):
        standings_data = {
            "records": [
                {
                    "division": {"id": 201, "name": "American League East"},
                    "teamRecords": [
                        {
                            "team": {"id": 141, "name": "Toronto Blue Jays"},
                            "wins": 90,
                            "losses": 72,
                            "winningPercentage": ".556",
                            "divisionRank": "1",
                        }
                    ],
                }
            ]
        }
        with patch.object(client._session, "get", return_value=_mock_response(standings_data)):
            result = client.get_standings()

        assert len(result) == 1
        assert result[0]["division"]["id"] == 201
        assert result[0]["teamRecords"][0]["wins"] == 90

    def test_calls_with_league_ids(self, client):
        with patch.object(client._session, "get", return_value=_mock_response({"records": []})) as mock_get:
            client.get_standings("103")

        mock_get.assert_called_once_with(
            "https://statsapi.mlb.com/api/v1/standings",
            params={"leagueId": "103"},
            timeout=10,
        )


class TestGetRoster:
    def test_returns_roster_list(self, client):
        roster_data = {
            "roster": [
                {
                    "person": {"id": 665926, "fullName": "Andrés Giménez"},
                    "jerseyNumber": "0",
                    "position": {"abbreviation": "2B"},
                    "status": {"code": "A"},
                }
            ]
        }
        with patch.object(client._session, "get", return_value=_mock_response(roster_data)):
            result = client.get_roster(141)

        assert len(result) == 1
        assert result[0]["person"]["fullName"] == "Andrés Giménez"

    def test_calls_correct_endpoint(self, client):
        with patch.object(client._session, "get", return_value=_mock_response({"roster": []})) as mock_get:
            client.get_roster(141)

        mock_get.assert_called_once_with(
            "https://statsapi.mlb.com/api/v1/teams/141/roster",
            params=None,
            timeout=10,
        )


class TestGetRosterWithStats:
    def test_calls_with_hydrate(self, client):
        with patch.object(client._session, "get", return_value=_mock_response({"roster": []})) as mock_get:
            client.get_roster_with_stats(141)

        mock_get.assert_called_once_with(
            "https://statsapi.mlb.com/api/v1/teams/141/roster/Active",
            params={"hydrate": "person(stats(type=season))"},
            timeout=10,
        )


class TestGetPlayer:
    def test_returns_player(self, client):
        player_data = {
            "people": [
                {
                    "id": 665926,
                    "fullName": "Andrés Giménez",
                    "primaryPosition": {"abbreviation": "2B"},
                    "batSide": {"code": "L"},
                    "pitchHand": {"code": "R"},
                }
            ]
        }
        with patch.object(client._session, "get", return_value=_mock_response(player_data)):
            result = client.get_player(665926)

        assert result["fullName"] == "Andrés Giménez"
        assert result["batSide"]["code"] == "L"

    def test_returns_none_for_missing(self, client):
        with patch.object(client._session, "get", return_value=_mock_response({"people": []})):
            result = client.get_player(999999)

        assert result is None


class TestGetPlayerStats:
    def test_default_stat_types(self, client):
        player_data = {"people": [{"id": 665926, "stats": []}]}
        with patch.object(client._session, "get", return_value=_mock_response(player_data)) as mock_get:
            client.get_player_stats(665926)

        args, kwargs = mock_get.call_args
        assert "yearByYear" in kwargs["params"]["hydrate"]
        assert "yearByYearAdvanced" in kwargs["params"]["hydrate"]
        assert "projected" in kwargs["params"]["hydrate"]
        assert "career" in kwargs["params"]["hydrate"]

    def test_custom_stat_types(self, client):
        player_data = {"people": [{"id": 665926, "stats": []}]}
        with patch.object(client._session, "get", return_value=_mock_response(player_data)) as mock_get:
            client.get_player_stats(665926, stat_types=["career"], group="pitching")

        args, kwargs = mock_get.call_args
        hydrate = kwargs["params"]["hydrate"]
        assert "career" in hydrate
        assert "pitching" in hydrate

    def test_returns_player_with_stats(self, client):
        player_data = {
            "people": [
                {
                    "id": 665926,
                    "stats": [
                        {
                            "type": {"displayName": "yearByYear"},
                            "group": {"displayName": "hitting"},
                            "splits": [
                                {"season": "2024", "stat": {"avg": ".252", "homeRuns": 9}}
                            ],
                        }
                    ],
                }
            ]
        }
        with patch.object(client._session, "get", return_value=_mock_response(player_data)):
            result = client.get_player_stats(665926)

        assert result["stats"][0]["splits"][0]["stat"]["avg"] == ".252"


class TestGetPlayerGameLog:
    def test_calls_with_group(self, client):
        player_data = {"people": [{"id": 665926, "stats": []}]}
        with patch.object(client._session, "get", return_value=_mock_response(player_data)) as mock_get:
            client.get_player_game_log(665926, group="pitching", season=2026)

        args, kwargs = mock_get.call_args
        assert "gameLog" in kwargs["params"]["hydrate"]
        assert "pitching" in kwargs["params"]["hydrate"]
        assert kwargs["params"]["season"] == 2026

    def test_returns_game_log_splits(self, client):
        player_data = {
            "people": [
                {
                    "id": 665926,
                    "stats": [
                        {
                            "type": {"displayName": "gameLog"},
                            "splits": [
                                {
                                    "date": "2026-04-10",
                                    "stat": {"hits": 2, "atBats": 4},
                                    "opponent": {"name": "Boston Red Sox"},
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        with patch.object(client._session, "get", return_value=_mock_response(player_data)):
            result = client.get_player_game_log(665926)

        split = result["stats"][0]["splits"][0]
        assert split["date"] == "2026-04-10"
        assert split["stat"]["hits"] == 2


class TestGetStatLeaders:
    def test_returns_leaders(self, client):
        leaders_data = {
            "leagueLeaders": [
                {
                    "leaderCategory": "homeRuns",
                    "leaders": [
                        {
                            "rank": 1,
                            "value": "25",
                            "person": {"fullName": "Aaron Judge"},
                        }
                    ],
                }
            ]
        }
        with patch.object(client._session, "get", return_value=_mock_response(leaders_data)):
            result = client.get_stat_leaders(["homeRuns"])

        assert result[0]["leaderCategory"] == "homeRuns"
        assert result[0]["leaders"][0]["value"] == "25"

    def test_calls_with_params(self, client):
        with patch.object(
            client._session, "get", return_value=_mock_response({"leagueLeaders": []})
        ) as mock_get:
            client.get_stat_leaders(["homeRuns", "battingAverage"], season=2026, limit=5)

        args, kwargs = mock_get.call_args
        assert kwargs["params"]["leaderCategories"] == "homeRuns,battingAverage"
        assert kwargs["params"]["season"] == 2026
        assert kwargs["params"]["limit"] == 5


class TestCaching:
    def test_caches_responses(self, client):
        teams_data = {"teams": [{"id": 141}]}
        with patch.object(client._session, "get", return_value=_mock_response(teams_data)) as mock_get:
            client.get_teams()
            client.get_teams()

        assert mock_get.call_count == 1

    def test_different_params_not_cached(self, client):
        with patch.object(
            client._session, "get", return_value=_mock_response({"records": []})
        ) as mock_get:
            client.get_standings("103")
            client.get_standings("104")

        assert mock_get.call_count == 2


class TestErrorHandling:
    def test_raises_on_http_error(self, client):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("404 Not Found")

        with patch.object(client._session, "get", return_value=mock_resp):
            with pytest.raises(Exception, match="404 Not Found"):
                client.get_teams()
