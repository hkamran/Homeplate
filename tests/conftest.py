import pytest

from app.clients.mlb_client import MLBClient
from app.clients.mlb_news_client import MLBNewsClient


@pytest.fixture
def mlb_client():
    return MLBClient(cache_ttl=60)


@pytest.fixture
def news_client():
    return MLBNewsClient(cache_ttl=60)
