import hashlib
import threading
import xml.etree.ElementTree as ET

import requests
from cachetools import TTLCache

from app.clients.disk_cache import DiskCache

DEFAULT_TIMEOUT = 10  # seconds


class MLBNewsClient:
    MLB_NEWS_URL = "https://www.mlb.com/feeds/news/rss.xml"
    TEAM_NEWS_URL = "https://www.mlb.com/{team_slug}/feeds/news/rss.xml"

    def __init__(self, cache_ttl=300, cache_maxsize=64, timeout=DEFAULT_TIMEOUT, disk_cache=None):
        self._session = requests.Session()
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self._lock = threading.Lock()
        self._timeout = timeout
        self._disk_cache = disk_cache or DiskCache()

    def _make_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()

    def _fetch_feed(self, url):
        cache_key = self._make_cache_key(url)

        # Layer 1: in-memory cache
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        # Layer 2: disk cache
        disk_data = self._disk_cache.get(cache_key)
        if disk_data is not None:
            with self._lock:
                self._cache[cache_key] = disk_data
            return disk_data

        # Layer 3: HTTP fetch + parse
        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        entries = self._parse_xml(response.content)

        with self._lock:
            self._cache[cache_key] = entries
        self._disk_cache.set(cache_key, entries)
        return entries

    def _parse_xml(self, content):
        """Parse RSS XML directly to capture <image href=""> tags that feedparser misses."""
        root = ET.fromstring(content)
        channel = root.find("channel")
        if channel is None:
            return []

        parsed = []
        for item in channel.findall("item"):
            # Extract image href — MLB uses non-standard <image href="url"/>
            image_el = item.find("image")
            image_url = image_el.get("href") if image_el is not None else None

            # Extract author from dc:creator namespace
            author = ""
            for child in item:
                if child.tag.endswith("creator"):
                    author = child.text or ""
                    break

            parsed.append(
                {
                    "title": self._get_text(item, "title"),
                    "description": self._get_text(item, "description"),
                    "link": self._get_text(item, "link"),
                    "published": self._get_text(item, "pubDate"),
                    "author": author,
                    "image_url": image_url,
                }
            )
        return parsed

    def _get_text(self, parent, tag):
        el = parent.find(tag)
        return el.text.strip() if el is not None and el.text else ""

    def get_mlb_news(self, limit=None):
        """Get recent MLB news stories.

        Args:
            limit: max number of stories to return (None for all)
        """
        entries = self._fetch_feed(self.MLB_NEWS_URL)
        if limit:
            return entries[:limit]
        return entries

    def get_team_news(self, team_slug, limit=None):
        """Get team-specific news stories.

        Args:
            team_slug: team URL slug e.g. "bluejays", "yankees"
            limit: max number of stories to return (None for all)
        """
        url = self.TEAM_NEWS_URL.format(team_slug=team_slug)
        entries = self._fetch_feed(url)
        if limit:
            return entries[:limit]
        return entries
