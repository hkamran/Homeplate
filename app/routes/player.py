import logging

from flask import Blueprint, abort, render_template

from app import mlb_client
from app.services.calculations import calc_bb_pct, calc_so_pct

logger = logging.getLogger(__name__)

player_bp = Blueprint("player", __name__)


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
    """Add SO% and BB% to a stat dictionary."""
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
    return stat_dict


@player_bp.route("/player/<int:player_id>")
def player(player_id):
    player_info = mlb_client.get_player(player_id)
    if not player_info:
        abort(404)

    primary_pos = player_info.get("primaryPosition", {}).get("type", "")
    is_pitcher = primary_pos == "Pitcher"
    group = "pitching" if is_pitcher else "hitting"

    # Fetch full stats — if this fails, show page with bio only
    seasons = []
    projected_stat = None
    career_stat = None
    player_data = player_info

    try:
        player_data = mlb_client.get_player_stats(
            player_id,
            stat_types=["yearByYear", "yearByYearAdvanced", "projected", "career"],
            group=group,
        ) or player_info

        stats_list = player_data.get("stats", [])

        seasons = _extract_stats_by_type(stats_list, "yearByYear", group)
        for s in seasons:
            if s.get("stat"):
                _add_calculated_stats(s["stat"], is_pitcher)

        projected = _extract_stats_by_type(stats_list, "projected", group)
        if projected:
            projected_stat = projected[0]
            if projected_stat.get("stat"):
                _add_calculated_stats(projected_stat["stat"], is_pitcher)

        career = _extract_stats_by_type(stats_list, "career", group)
        if career:
            career_stat = career[0]
            if career_stat.get("stat"):
                _add_calculated_stats(career_stat["stat"], is_pitcher)
    except Exception:
        logger.exception("Failed to fetch stats for player %s", player_id)

    # Game log (last 7 games)
    game_log = []
    try:
        game_log_data = mlb_client.get_player_game_log(player_id, group=group)
        if game_log_data:
            for stat_entry in game_log_data.get("stats", []):
                if stat_entry.get("type", {}).get("displayName") == "gameLog":
                    game_log = stat_entry.get("splits", [])[:7]
                    break
    except Exception:
        logger.exception("Failed to fetch game log for player %s", player_id)

    return render_template(
        "player.html",
        player=player_data,
        is_pitcher=is_pitcher,
        seasons=seasons,
        projected=projected_stat,
        career=career_stat,
        game_log=game_log,
    )
