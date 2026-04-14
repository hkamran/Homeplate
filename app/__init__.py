from flask import Flask, render_template

from app.clients.mlb_client import MLBClient
from app.clients.mlb_news_client import MLBNewsClient
from app.config import config_map
from app.constants import MLB_TEAMS

# Module-level references — initialized in create_app()
mlb_client: MLBClient = None  # type: ignore[assignment]
news_client: MLBNewsClient = None  # type: ignore[assignment]


def create_app(config_name="development"):
    global mlb_client, news_client

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Initialize clients inside factory so they can be configured per-app
    mlb_client = MLBClient()
    news_client = MLBNewsClient()

    team_abbr_map = {t["id"]: t["abbr"] for t in MLB_TEAMS}

    @app.context_processor
    def inject_globals():
        return dict(
            mlb_teams=MLB_TEAMS,
            team_abbr_map=team_abbr_map,
            team_logo_url=lambda tid: f"https://www.mlbstatic.com/team-logos/{tid}.svg",
            player_headshot_url=lambda pid: f"https://content.mlb.com/images/headshots/current/60x60/{pid}@2x.png",
        )

    from app.routes.landing import landing_bp
    from app.routes.leaderboards import leaderboards_bp
    from app.routes.player import player_bp
    from app.routes.standings import standings_bp
    from app.routes.team import team_bp

    app.register_blueprint(landing_bp)
    app.register_blueprint(standings_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(leaderboards_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    return app
