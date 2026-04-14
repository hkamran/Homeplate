from flask import Blueprint, abort, render_template

from app.constants import LEADER_DISPLAY_NAMES
from app.services.leaders import get_landing_leaders
from app.services.news import get_team_news
from app.services.standings import get_team_record
from app.services.team import get_roster_split, get_team

team_bp = Blueprint("team", __name__)


@team_bp.route("/team/<int:team_id>")
def team(team_id):
    team_info = get_team(team_id)
    if not team_info:
        abort(404)

    hitters, pitchers = get_roster_split(team_id)

    return render_template(
        "team.html",
        team=team_info,
        team_record=get_team_record(team_id),
        hitters=hitters,
        pitchers=pitchers,
        news=get_team_news(team_id, limit=4),
        leaders=get_landing_leaders(limit=1),
        leader_display_names=LEADER_DISPLAY_NAMES,
    )
