from flask import Blueprint, abort, render_template

from app.services.player import get_game_log, get_player, get_player_stats, is_pitcher

player_bp = Blueprint("player", __name__)


@player_bp.route("/player/<int:player_id>")
def player(player_id):
    player_info = get_player(player_id)
    if not player_info:
        abort(404)

    pitcher = is_pitcher(player_info)
    player_data, seasons, projected, career = get_player_stats(player_id, pitcher)

    return render_template(
        "player.html",
        player=player_data or player_info,
        is_pitcher=pitcher,
        seasons=seasons,
        projected=projected,
        career=career,
        game_log=get_game_log(player_id, pitcher),
    )
