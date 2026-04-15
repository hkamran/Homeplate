from flask import Blueprint, Response, abort, request

from app.services.image_cache import ImageCache

images_bp = Blueprint("images", __name__)

_cache = ImageCache()

# Allowed URL prefixes to prevent open proxy
ALLOWED_PREFIXES = [
    "https://www.mlbstatic.com/",
    "https://content.mlb.com/",
    "https://img.mlbstatic.com/",
    "https://prod-gameday.mlbstatic.com/",
]


@images_bp.route("/images/proxy")
def proxy_image():
    url = request.args.get("url", "")
    if not url or not any(url.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        abort(400)

    data, content_type = _cache.fetch_and_cache(url)
    if data is None:
        abort(404)

    return Response(data, content_type=content_type, headers={"Cache-Control": "public, max-age=86400"})
