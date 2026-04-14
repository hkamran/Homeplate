import hashlib
import json
import logging
import os
import time

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = "/cache"
DEFAULT_TTL = 3600  # 1 hour


class DiskCache:
    """Simple file-based JSON cache with TTL expiry.

    Stores responses as JSON files in a directory. Each entry is a JSON file
    containing the data and an expiry timestamp. Expired entries are ignored
    and overwritten on next write.
    """

    def __init__(self, cache_dir=DEFAULT_CACHE_DIR, ttl=DEFAULT_TTL):
        self._cache_dir = cache_dir
        self._ttl = ttl
        os.makedirs(self._cache_dir, exist_ok=True)

    def _key_to_path(self, key):
        hashed = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self._cache_dir, f"{hashed}.json")

    def get(self, key):
        """Retrieve a cached value. Returns None if missing or expired."""
        path = self._key_to_path(key)
        try:
            with open(path) as f:
                entry = json.load(f)
            if entry["expires_at"] > time.time():
                return entry["data"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return None

    def set(self, key, data):
        """Write data to the cache with TTL."""
        path = self._key_to_path(key)
        entry = {
            "data": data,
            "expires_at": time.time() + self._ttl,
        }
        try:
            with open(path, "w") as f:
                json.dump(entry, f)
        except OSError:
            logger.warning("Failed to write cache file: %s", path)
