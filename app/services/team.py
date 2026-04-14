import logging

from app import mlb_client

logger = logging.getLogger(__name__)


def get_team(team_id):
    """Fetch team info. Returns None if not found."""
    return mlb_client.get_team(team_id)


def get_roster_split(team_id):
    """Fetch active roster and split into hitters and pitchers.

    Returns:
        tuple: (hitters, pitchers) — each a list of dicts with
               id, name, number, position, and stats keys.
    """
    hitters = []
    pitchers = []

    try:
        roster = mlb_client.get_roster_with_stats(team_id)
    except Exception:
        logger.exception("Failed to fetch roster for team %s", team_id)
        return hitters, pitchers

    for player in roster:
        person = player.get("person", {})
        position = player.get("position", {})
        pos_type = position.get("type", "")
        pos_abbr = position.get("abbreviation", "")

        stats = {}
        for stat_group in person.get("stats", []):
            if stat_group.get("type", {}).get("displayName") == "season":
                splits = stat_group.get("splits", [])
                if splits:
                    stats = splits[-1].get("stat", {})

        entry = {
            "id": person.get("id"),
            "name": person.get("fullName", ""),
            "number": player.get("jerseyNumber", ""),
            "position": pos_abbr,
            "age": person.get("currentAge", ""),
            "bat_side": person.get("batSide", {}).get("code", ""),
            "throw_hand": person.get("pitchHand", {}).get("code", ""),
            "stats": stats,
        }

        if pos_type == "Pitcher":
            pitchers.append(entry)
        else:
            hitters.append(entry)

    return hitters, pitchers
