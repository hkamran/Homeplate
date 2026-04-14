import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = False
    MLB_API_BASE_URL = "https://statsapi.mlb.com"
    MLB_NEWS_RSS_URL = "https://www.mlb.com/feeds/news/rss.xml"


class DevelopmentConfig(Config):
    DEBUG = True


config_map = {
    "development": DevelopmentConfig,
    "production": Config,
}
