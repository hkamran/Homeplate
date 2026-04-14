from flask import Blueprint, render_template

from app.constants import DIVISION_NAMES
from app.services.standings import get_ordered_standings, get_split_pct

standings_bp = Blueprint("standings", __name__)


@standings_bp.route("/standings")
def standings():
    return render_template(
        "standings.html",
        standings=get_ordered_standings(),
        division_names=DIVISION_NAMES,
        get_split_pct=get_split_pct,
    )
