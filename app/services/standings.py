import logging

from app import mlb_client
from app.constants import DIVISION_NAMES, DIVISION_ORDER

logger = logging.getLogger(__name__)


def get_split_pct(split_records, split_type):
    """Extract win pct from a team's splitRecords by type."""
    for rec in split_records:
        if rec.get("type") == split_type:
            return rec.get("pct", "-")
    return "-"


def get_ordered_standings():
    """Fetch standings and return ordered by division (AL/NL, East/Central/West)."""
    try:
        records = mlb_client.get_standings()
        standings_by_div = {r["division"]["id"]: r for r in records}
        return [standings_by_div[div_id] for div_id in DIVISION_ORDER if div_id in standings_by_div]
    except Exception:
        logger.exception("Failed to fetch standings")
        return []


def get_team_record(team_id):
    """Find a specific team's record from the standings."""
    try:
        records = mlb_client.get_standings()
        for division in records:
            for rec in division.get("teamRecords", []):
                if rec["team"]["id"] == team_id:
                    return rec
    except Exception:
        logger.exception("Failed to fetch standings for team record")
    return None
