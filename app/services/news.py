import logging

from app import news_client
from app.constants import MLB_TEAMS

logger = logging.getLogger(__name__)

TEAM_SLUG_MAP = {t["id"]: t["slug"] for t in MLB_TEAMS}


def get_mlb_news(limit=4):
    """Fetch recent MLB news stories."""
    try:
        return news_client.get_mlb_news(limit=limit)
    except Exception:
        logger.exception("Failed to fetch MLB news")
        return []


def get_team_news(team_id, limit=4):
    """Fetch team-specific news stories."""
    try:
        slug = TEAM_SLUG_MAP.get(team_id, "")
        if slug:
            return news_client.get_team_news(slug, limit=limit)
    except Exception:
        logger.exception("Failed to fetch news for team %s", team_id)
    return []
