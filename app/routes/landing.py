from flask import Blueprint, render_template

from app.constants import DIVISION_NAMES, LEADER_DISPLAY_NAMES
from app.services.leaders import get_landing_leaders
from app.services.news import get_mlb_news
from app.services.standings import get_ordered_standings

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/")
def index():
    return render_template(
        "landing.html",
        standings=get_ordered_standings(),
        division_names=DIVISION_NAMES,
        news=get_mlb_news(limit=4),
        leaders=get_landing_leaders(limit=1),
        leader_display_names=LEADER_DISPLAY_NAMES,
    )
