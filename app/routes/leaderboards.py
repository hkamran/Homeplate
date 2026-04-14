from flask import Blueprint, render_template

from app.constants import LEADERBOARD_DISPLAY_NAMES
from app.services.leaders import get_hitting_leaders, get_pitching_leaders

leaderboards_bp = Blueprint("leaderboards", __name__)


@leaderboards_bp.route("/leaderboards")
def leaderboards():
    return render_template(
        "leaderboards.html",
        hitting_leaders=get_hitting_leaders(limit=10),
        pitching_leaders=get_pitching_leaders(limit=10),
        display_names=LEADERBOARD_DISPLAY_NAMES,
    )
