import logging

from flask import Blueprint, render_template

from app import mlb_client

logger = logging.getLogger(__name__)

leaderboards_bp = Blueprint("leaderboards", __name__)

HITTING_CATEGORIES = ["homeRuns", "battingAverage", "onBasePlusSlugging", "runsBattedIn"]
PITCHING_CATEGORIES = ["earnedRunAverage", "strikeOuts", "whip", "wins"]

DISPLAY_NAMES = {
    "homeRuns": "Home Runs",
    "battingAverage": "Batting Average",
    "onBasePlusSlugging": "OPS",
    "runsBattedIn": "RBI",
    "earnedRunAverage": "ERA",
    "strikeouts": "Strikeouts",
    "whip": "WHIP",
    "wins": "Wins",
}

# Map each requested category to the stat group we want from the API response
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


def _filter_leaders(all_leaders, stat_groups):
    """Filter API response to one entry per category using correct stat group."""
    filtered = []
    for entry in all_leaders:
        cat = entry["leaderCategory"]
        group = entry.get("statGroup", "")
        if cat in stat_groups and group == stat_groups[cat]:
            filtered.append(entry)
    return filtered


@leaderboards_bp.route("/leaderboards")
def leaderboards():
    hitting_leaders = []
    pitching_leaders = []

    try:
        all_hitting = mlb_client.get_stat_leaders(HITTING_CATEGORIES, limit=10)
        hitting_leaders = _filter_leaders(all_hitting, HITTING_STAT_GROUPS)
    except Exception:
        logger.exception("Failed to fetch hitting leaders")

    try:
        all_pitching = mlb_client.get_stat_leaders(PITCHING_CATEGORIES, limit=10)
        pitching_leaders = _filter_leaders(all_pitching, PITCHING_STAT_GROUPS)
    except Exception:
        logger.exception("Failed to fetch pitching leaders")

    return render_template(
        "leaderboards.html",
        hitting_leaders=hitting_leaders,
        pitching_leaders=pitching_leaders,
        display_names=DISPLAY_NAMES,
    )
