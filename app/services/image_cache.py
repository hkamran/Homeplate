import hashlib
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

DEFAULT_IMAGE_CACHE_DIR = "/cache/images"
DEFAULT_IMAGE_TTL = 86400  # 24 hours


class ImageCache:
    """Caches remote images to disk and serves them locally."""

    def __init__(self, cache_dir=DEFAULT_IMAGE_CACHE_DIR, ttl=DEFAULT_IMAGE_TTL):
        self._cache_dir = cache_dir
        self._ttl = ttl
        os.makedirs(self._cache_dir, exist_ok=True)

    def _url_to_path(self, url):
        hashed = hashlib.md5(url.encode()).hexdigest()
        # Preserve extension from URL
        ext = ".png"
        if ".svg" in url:
            ext = ".svg"
        elif ".jpg" in url or ".jpeg" in url:
            ext = ".jpg"
        return os.path.join(self._cache_dir, f"{hashed}{ext}")

    def _meta_path(self, path):
        return path + ".meta"

    def get(self, url):
        """Get cached image bytes and content type. Returns (bytes, content_type) or (None, None)."""
        path = self._url_to_path(url)
        meta_path = self._meta_path(path)

        try:
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    parts = f.read().strip().split("\n")
                    expires_at = float(parts[0])
                    content_type = parts[1] if len(parts) > 1 else "image/png"

                if expires_at > time.time() and os.path.exists(path):
                    with open(path, "rb") as f:
                        return f.read(), content_type
        except (OSError, ValueError):
            pass

        return None, None

    def fetch_and_cache(self, url):
        """Fetch image from URL, cache it, return (bytes, content_type)."""
        # Check cache first
        data, content_type = self.get(url)
        if data is not None:
            return data, content_type

        # Fetch from remote
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception:
            logger.warning("Failed to fetch image: %s", url)
            return None, None

        data = resp.content
        content_type = resp.headers.get("Content-Type", "image/png")
        path = self._url_to_path(url)

        try:
            with open(path, "wb") as f:
                f.write(data)
            with open(self._meta_path(path), "w") as f:
                f.write(f"{time.time() + self._ttl}\n{content_type}")
        except OSError:
            logger.warning("Failed to write image cache: %s", path)

        return data, content_type
