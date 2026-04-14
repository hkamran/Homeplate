# All 30 MLB teams with IDs, abbreviations, full names, and URL slugs.
# Used for the navbar dropdown, team abbreviation lookups, and news feed URLs.
MLB_TEAMS = [
    {"id": 109, "abbr": "ARI", "name": "Arizona Diamondbacks", "slug": "dbacks"},
    {"id": 144, "abbr": "ATL", "name": "Atlanta Braves", "slug": "braves"},
    {"id": 110, "abbr": "BAL", "name": "Baltimore Orioles", "slug": "orioles"},
    {"id": 111, "abbr": "BOS", "name": "Boston Red Sox", "slug": "redsox"},
    {"id": 112, "abbr": "CHC", "name": "Chicago Cubs", "slug": "cubs"},
    {"id": 145, "abbr": "CWS", "name": "Chicago White Sox", "slug": "whitesox"},
    {"id": 113, "abbr": "CIN", "name": "Cincinnati Reds", "slug": "reds"},
    {"id": 114, "abbr": "CLE", "name": "Cleveland Guardians", "slug": "guardians"},
    {"id": 115, "abbr": "COL", "name": "Colorado Rockies", "slug": "rockies"},
    {"id": 116, "abbr": "DET", "name": "Detroit Tigers", "slug": "tigers"},
    {"id": 117, "abbr": "HOU", "name": "Houston Astros", "slug": "astros"},
    {"id": 118, "abbr": "KC", "name": "Kansas City Royals", "slug": "royals"},
    {"id": 108, "abbr": "LAA", "name": "Los Angeles Angels", "slug": "angels"},
    {"id": 119, "abbr": "LAD", "name": "Los Angeles Dodgers", "slug": "dodgers"},
    {"id": 146, "abbr": "MIA", "name": "Miami Marlins", "slug": "marlins"},
    {"id": 158, "abbr": "MIL", "name": "Milwaukee Brewers", "slug": "brewers"},
    {"id": 142, "abbr": "MIN", "name": "Minnesota Twins", "slug": "twins"},
    {"id": 121, "abbr": "NYM", "name": "New York Mets", "slug": "mets"},
    {"id": 147, "abbr": "NYY", "name": "New York Yankees", "slug": "yankees"},
    {"id": 133, "abbr": "OAK", "name": "Oakland Athletics", "slug": "athletics"},
    {"id": 143, "abbr": "PHI", "name": "Philadelphia Phillies", "slug": "phillies"},
    {"id": 134, "abbr": "PIT", "name": "Pittsburgh Pirates", "slug": "pirates"},
    {"id": 135, "abbr": "SD", "name": "San Diego Padres", "slug": "padres"},
    {"id": 137, "abbr": "SF", "name": "San Francisco Giants", "slug": "giants"},
    {"id": 136, "abbr": "SEA", "name": "Seattle Mariners", "slug": "mariners"},
    {"id": 138, "abbr": "STL", "name": "St. Louis Cardinals", "slug": "cardinals"},
    {"id": 139, "abbr": "TB", "name": "Tampa Bay Rays", "slug": "rays"},
    {"id": 140, "abbr": "TEX", "name": "Texas Rangers", "slug": "rangers"},
    {"id": 141, "abbr": "TOR", "name": "Toronto Blue Jays", "slug": "bluejays"},
    {"id": 120, "abbr": "WSH", "name": "Washington Nationals", "slug": "nationals"},
]

# Stable MLB division IDs — these haven't changed since 1998.
# Hardcoded to control display order (AL left column, NL right column) and avoid
# an extra API call. The standings API returns divisions in an unpredictable order.
DIVISION_ORDER = [201, 202, 200, 204, 205, 203]
DIVISION_NAMES = {
    201: "AL East",
    202: "AL Central",
    200: "AL West",
    204: "NL East",
    205: "NL Central",
    203: "NL West",
}

# Categories to request from the StatsAPI leaders endpoint
LANDING_LEADER_CATEGORIES = ["homeRuns", "onBasePlusSlugging", "strikeOuts", "earnedRunAverage"]

# The API returns leaderCategory as lowercase keys (e.g. "homeRuns"), but uses
# non-user-friendly names. Map them to readable display names for the UI.
LEADER_DISPLAY_NAMES = {
    "homeRuns": "Home Runs",
    "onBasePlusSlugging": "OPS",
    "strikeouts": "Strikeouts",
    "earnedRunAverage": "ERA",
}

# The StatsAPI returns duplicate leader entries per category — one for each stat group
# (hitting, pitching, catching). We only want one per category, so we specify which
# stat group is relevant for each. Keys match the API response's leaderCategory field.
LEADER_STAT_GROUPS = {
    "homeRuns": "hitting",
    "onBasePlusSlugging": "hitting",
    "strikeouts": "pitching",
    "earnedRunAverage": "pitching",
}

# Leaderboard page categories — broader set than landing page
HITTING_CATEGORIES = ["homeRuns", "battingAverage", "onBasePlusSlugging", "runsBattedIn"]
PITCHING_CATEGORIES = ["earnedRunAverage", "strikeOuts", "whip", "wins"]

HITTING_STAT_GROUPS = {
    "homeRuns": "hitting",
    "battingAverage": "hitting",
    "onBasePlusSlugging": "hitting",
    "runsBattedIn": "hitting",
}

PITCHING_STAT_GROUPS = {
    "earnedRunAverage": "pitching",
    "strikeouts": "pitching",
    "whip": "pitching",
    "wins": "pitching",
}

# Display names for leaderboard page (superset of landing display names)
LEADERBOARD_DISPLAY_NAMES = {
    "homeRuns": "Home Runs",
    "battingAverage": "Batting Average",
    "onBasePlusSlugging": "OPS",
    "runsBattedIn": "RBI",
    "earnedRunAverage": "ERA",
    "strikeouts": "Strikeouts",
    "whip": "WHIP",
    "wins": "Wins",
}
