import hashlib
import json
import threading

import requests
from cachetools import TTLCache

DEFAULT_TIMEOUT = 10  # seconds


class MLBClient:
    BASE_URL = "https://statsapi.mlb.com"

    def __init__(self, cache_ttl=300, cache_maxsize=128, timeout=DEFAULT_TIMEOUT):
        self._session = requests.Session()
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self._lock = threading.Lock()
        self._timeout = timeout

    def _make_cache_key(self, endpoint, params):
        """Build a deterministic cache key from endpoint and params."""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get(self, endpoint, params=None):
        cache_key = self._make_cache_key(endpoint, params)

        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        response = self._session.get(
            f"{self.BASE_URL}{endpoint}", params=params, timeout=self._timeout
        )
        response.raise_for_status()
        data = response.json()

        with self._lock:
            self._cache[cache_key] = data
        return data

    def get_teams(self):
        """Get all MLB teams."""
        data = self._get("/api/v1/teams", params={"sportId": 1})
        return data.get("teams", [])

    def get_team(self, team_id):
        """Get a single team by ID."""
        data = self._get(f"/api/v1/teams/{team_id}")
        teams = data.get("teams", [])
        return teams[0] if teams else None

    def get_standings(self, league_ids="103,104"):
        """Get divisional standings. Returns list of division records."""
        data = self._get("/api/v1/standings", params={"leagueId": league_ids})
        return data.get("records", [])

    def get_roster(self, team_id):
        """Get active roster for a team."""
        data = self._get(f"/api/v1/teams/{team_id}/roster")
        return data.get("roster", [])

    def get_roster_with_stats(self, team_id):
        """Get active roster with season stats for each player."""
        data = self._get(
            f"/api/v1/teams/{team_id}/roster/Active",
            params={"hydrate": "person(stats(type=season))"},
        )
        return data.get("roster", [])

    def get_player(self, player_id):
        """Get player biographical info."""
        data = self._get(f"/api/v1/people/{player_id}")
        people = data.get("people", [])
        return people[0] if people else None

    def get_player_stats(self, player_id, stat_types=None, group=None):
        """Get player with stats hydration.

        Args:
            player_id: MLB player ID
            stat_types: list of stat types e.g. ["yearByYear", "projected", "career"]
            group: stat group e.g. "hitting" or "pitching"
        """
        if stat_types is None:
            stat_types = ["yearByYear", "yearByYearAdvanced", "projected", "career"]

        type_str = ",".join(stat_types)
        hydrate = f"stats(type=[{type_str}]),team,currentTeam"
        if group:
            hydrate = f"stats(type=[{type_str}],group=[{group}]),team,currentTeam"

        data = self._get(f"/api/v1/people/{player_id}", params={"hydrate": hydrate})
        people = data.get("people", [])
        return people[0] if people else None

    def get_player_game_log(self, player_id, group="hitting", season=None):
        """Get player game log.

        Args:
            player_id: MLB player ID
            group: "hitting" or "pitching"
            season: season year (optional)
        """
        params = {"hydrate": f"stats(type=[gameLog],group=[{group}])"}
        if season:
            params["season"] = season

        data = self._get(f"/api/v1/people/{player_id}", params=params)
        people = data.get("people", [])
        return people[0] if people else None

    def get_stat_leaders(self, categories, season=None, limit=10):
        """Get statistical leaders.

        Args:
            categories: list of leader categories e.g. ["homeRuns", "battingAverage"]
            season: season year (optional)
            limit: number of leaders per category
        """
        params = {
            "leaderCategories": ",".join(categories),
            "limit": limit,
        }
        if season:
            params["season"] = season

        data = self._get("/api/v1/stats/leaders", params=params)
        return data.get("leagueLeaders", [])

    def get_leader_types(self):
        """Get available leader category types."""
        return self._get("/api/v1/leagueLeaderTypes")

    def get_stat_types(self):
        """Get available stat types."""
        return self._get("/api/v1/statTypes")

    def get_game_types(self):
        """Get available game types."""
        return self._get("/api/v1/gameTypes")
