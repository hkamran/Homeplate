import logging

from flask import Blueprint, render_template

from app import mlb_client, news_client
from app.constants import (
    DIVISION_NAMES,
    DIVISION_ORDER,
    LANDING_LEADER_CATEGORIES,
    LEADER_DISPLAY_NAMES,
    LEADER_STAT_GROUPS,
)

logger = logging.getLogger(__name__)

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/")
def index():
    ordered_standings = []
    news = []
    leaders = []

    try:
        standings = mlb_client.get_standings()
        standings_by_div = {r["division"]["id"]: r for r in standings}
        ordered_standings = [standings_by_div[div_id] for div_id in DIVISION_ORDER if div_id in standings_by_div]
    except Exception:
        logger.exception("Failed to fetch standings")

    try:
        news = news_client.get_mlb_news(limit=4)
    except Exception:
        logger.exception("Failed to fetch news")

    try:
        all_leaders = mlb_client.get_stat_leaders(LANDING_LEADER_CATEGORIES, limit=1)
        for entry in all_leaders:
            cat = entry["leaderCategory"]
            group = entry.get("statGroup", "")
            if cat in LEADER_STAT_GROUPS and group == LEADER_STAT_GROUPS[cat]:
                leaders.append(entry)
    except Exception:
        logger.exception("Failed to fetch leaders")

    return render_template(
        "landing.html",
        standings=ordered_standings,
        division_names=DIVISION_NAMES,
        news=news,
        leaders=leaders,
        leader_display_names=LEADER_DISPLAY_NAMES,
    )
