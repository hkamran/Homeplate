import pytest

from app.clients.disk_cache import DiskCache
from app.clients.mlb_client import MLBClient
from app.clients.mlb_news_client import MLBNewsClient


class NullDiskCache(DiskCache):
    """No-op disk cache for tests — never reads or writes to disk."""

    def __init__(self):
        self._cache_dir = None
        self._ttl = 0

    def get(self, key):
        return None

    def set(self, key, data):
        pass


@pytest.fixture
def mlb_client():
    return MLBClient(cache_ttl=60, disk_cache=NullDiskCache())


@pytest.fixture
def news_client():
    return MLBNewsClient(cache_ttl=60, disk_cache=NullDiskCache())
