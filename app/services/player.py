import logging

from app import mlb_client
from app.services.calculations import calc_bb_pct, calc_so_pct

logger = logging.getLogger(__name__)


def _extract_stats_by_type(stats_list, type_name, group_name=None):
    """Find a specific stat type from the player's stats array."""
    for stat in stats_list:
        display_name = stat.get("type", {}).get("displayName", "")
        group = stat.get("group", {}).get("displayName", "")
        if display_name == type_name:
            if group_name and group != group_name:
                continue
            return stat.get("splits", [])
    return []


def _add_calculated_stats(stat_dict, is_pitcher=False):
    """Add SO% and BB% to a stat dictionary in place."""
    if is_pitcher:
        bf = stat_dict.get("battersFaced", 0) or 0
        so = stat_dict.get("strikeOuts", 0) or 0
        bb = stat_dict.get("baseOnBalls", 0) or 0
        stat_dict["soPct"] = calc_so_pct(so, bf)
        stat_dict["bbPct"] = calc_bb_pct(bb, bf)
    else:
        pa = stat_dict.get("plateAppearances", 0) or 0
        so = stat_dict.get("strikeOuts", 0) or 0
        bb = stat_dict.get("baseOnBalls", 0) or 0
        stat_dict["soPct"] = calc_so_pct(so, pa)
        stat_dict["bbPct"] = calc_bb_pct(bb, pa)


def get_player(player_id):
    """Fetch player biographical info. Returns None if not found."""
    return mlb_client.get_player(player_id)


def is_pitcher(player_info):
    """Determine if a player is a pitcher based on primary position."""
    return player_info.get("primaryPosition", {}).get("type", "") == "Pitcher"


def get_player_stats(player_id, is_pitcher_flag):
    """Fetch and process a player's season, projected, and career stats.

    Returns:
        tuple: (player_data, seasons, projected_stat, career_stat)
    """
    group = "pitching" if is_pitcher_flag else "hitting"
    seasons = []
    projected_stat = None
    career_stat = None
    player_data = None

    try:
        player_data = mlb_client.get_player_stats(
            player_id,
            stat_types=["yearByYear", "yearByYearAdvanced", "projected", "career"],
            group=group,
        )
        if not player_data:
            return None, seasons, projected_stat, career_stat

        stats_list = player_data.get("stats", [])

        seasons = _extract_stats_by_type(stats_list, "yearByYear", group)
        for s in seasons:
            if s.get("stat"):
                _add_calculated_stats(s["stat"], is_pitcher_flag)

        projected = _extract_stats_by_type(stats_list, "projected", group)
        if projected:
            projected_stat = projected[0]
            if projected_stat.get("stat"):
                _add_calculated_stats(projected_stat["stat"], is_pitcher_flag)

        career = _extract_stats_by_type(stats_list, "career", group)
        if career:
            career_stat = career[0]
            if career_stat.get("stat"):
                _add_calculated_stats(career_stat["stat"], is_pitcher_flag)

    except Exception:
        logger.exception("Failed to fetch stats for player %s", player_id)

    return player_data, seasons, projected_stat, career_stat


def get_game_log(player_id, is_pitcher_flag, limit=7):
    """Fetch a player's recent game log.

    Returns:
        list: Last N game log entries.
    """
    group = "pitching" if is_pitcher_flag else "hitting"
    try:
        game_log_data = mlb_client.get_player_game_log(player_id, group=group)
        if game_log_data:
            for stat_entry in game_log_data.get("stats", []):
                if stat_entry.get("type", {}).get("displayName") == "gameLog":
                    return stat_entry.get("splits", [])[:limit]
    except Exception:
        logger.exception("Failed to fetch game log for player %s", player_id)
    return []
