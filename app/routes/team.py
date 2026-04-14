import logging

from flask import Blueprint, abort, render_template

from app import mlb_client, news_client
from app.constants import MLB_TEAMS
from app.constants import (
    LANDING_LEADER_CATEGORIES,
    LEADER_DISPLAY_NAMES,
    LEADER_STAT_GROUPS,
)

logger = logging.getLogger(__name__)

team_bp = Blueprint("team", __name__)

TEAM_SLUG_MAP = {t["id"]: t["slug"] for t in MLB_TEAMS}


@team_bp.route("/team/<int:team_id>")
def team(team_id):
    team_info = mlb_client.get_team(team_id)
    if not team_info:
        abort(404)

    hitters = []
    pitchers = []
    try:
        roster = mlb_client.get_roster_with_stats(team_id)
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
                "stats": stats,
            }

            if pos_type == "Pitcher":
                pitchers.append(entry)
            else:
                hitters.append(entry)
    except Exception:
        logger.exception("Failed to fetch roster for team %s", team_id)

    team_news = []
    try:
        slug = TEAM_SLUG_MAP.get(team_id, "")
        if slug:
            team_news = news_client.get_team_news(slug, limit=4)
    except Exception:
        logger.exception("Failed to fetch news for team %s", team_id)

    leaders = []
    try:
        all_leaders = mlb_client.get_stat_leaders(LANDING_LEADER_CATEGORIES, limit=1)
        for entry in all_leaders:
            cat = entry["leaderCategory"]
            group = entry.get("statGroup", "")
            if cat in LEADER_STAT_GROUPS and group == LEADER_STAT_GROUPS[cat]:
                leaders.append(entry)
    except Exception:
        logger.exception("Failed to fetch leaders")

    team_record = None
    try:
        standings = mlb_client.get_standings()
        for division in standings:
            for rec in division.get("teamRecords", []):
                if rec["team"]["id"] == team_id:
                    team_record = rec
                    break
            if team_record:
                break
    except Exception:
        logger.exception("Failed to fetch standings for team record")

    return render_template(
        "team.html",
        team=team_info,
        team_record=team_record,
        hitters=hitters,
        pitchers=pitchers,
        news=team_news,
        leaders=leaders,
        leader_display_names=LEADER_DISPLAY_NAMES,
    )
