#!/usr/bin/env bash
set -euo pipefail

echo "==> Building and starting Docker Compose..."
docker compose up --build -d

echo "==> Waiting for app to start..."
sleep 3

echo "==> Verifying app is running..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ | grep -q "200"; then
    echo "==> App is running at http://localhost:5000"
else
    echo "==> App failed to start. Check logs with: docker compose logs"
    exit 1
fi

echo "==> Running tests..."
docker compose exec web uv run pytest -v

echo "==> Setup complete!"
