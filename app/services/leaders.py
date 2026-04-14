import logging

from app import mlb_client
from app.constants import (
    HITTING_CATEGORIES,
    HITTING_STAT_GROUPS,
    LANDING_LEADER_CATEGORIES,
    LEADER_STAT_GROUPS,
    PITCHING_CATEGORIES,
    PITCHING_STAT_GROUPS,
)

logger = logging.getLogger(__name__)


def _filter_leaders(all_leaders, stat_groups):
    """Filter API response to one entry per category using correct stat group."""
    filtered = []
    for entry in all_leaders:
        cat = entry["leaderCategory"]
        group = entry.get("statGroup", "")
        if cat in stat_groups and group == stat_groups[cat]:
            filtered.append(entry)
    return filtered


def get_landing_leaders(limit=1):
    """Fetch top leader for each landing page category (HR, OPS, SO, ERA)."""
    try:
        all_leaders = mlb_client.get_stat_leaders(LANDING_LEADER_CATEGORIES, limit=limit)
        return _filter_leaders(all_leaders, LEADER_STAT_GROUPS)
    except Exception:
        logger.exception("Failed to fetch leaders")
        return []


def get_hitting_leaders(limit=10):
    """Fetch hitting leaderboard data."""
    try:
        all_leaders = mlb_client.get_stat_leaders(HITTING_CATEGORIES, limit=limit)
        return _filter_leaders(all_leaders, HITTING_STAT_GROUPS)
    except Exception:
        logger.exception("Failed to fetch hitting leaders")
        return []


def get_pitching_leaders(limit=10):
    """Fetch pitching leaderboard data."""
    try:
        all_leaders = mlb_client.get_stat_leaders(PITCHING_CATEGORIES, limit=limit)
        return _filter_leaders(all_leaders, PITCHING_STAT_GROUPS)
    except Exception:
        logger.exception("Failed to fetch pitching leaders")
        return []
