#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting development server..."
docker compose up --build -d

echo "==> Tailing logs (Ctrl+C to stop)..."
docker compose logs -f
