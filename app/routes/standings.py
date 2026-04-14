import logging

from flask import Blueprint, render_template

from app import mlb_client
from app.constants import DIVISION_NAMES, DIVISION_ORDER

logger = logging.getLogger(__name__)

standings_bp = Blueprint("standings", __name__)


def _get_split_pct(split_records, split_type):
    """Extract win pct from a team's splitRecords by type."""
    for rec in split_records:
        if rec.get("type") == split_type:
            return rec.get("pct", "-")
    return "-"


@standings_bp.route("/standings")
def standings():
    ordered_standings = []
    try:
        records = mlb_client.get_standings()
        standings_by_div = {r["division"]["id"]: r for r in records}
        ordered_standings = [standings_by_div[div_id] for div_id in DIVISION_ORDER if div_id in standings_by_div]
    except Exception:
        logger.exception("Failed to fetch standings")

    return render_template(
        "standings.html",
        standings=ordered_standings,
        division_names=DIVISION_NAMES,
        get_split_pct=_get_split_pct,
    )
