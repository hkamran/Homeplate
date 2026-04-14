#!/usr/bin/env bash
set -euo pipefail

echo "==> Running linter..."
docker compose exec web uv run ruff check app/ tests/

echo "==> Running formatter check..."
docker compose exec web uv run ruff format --check app/ tests/

echo "==> Running tests..."
docker compose exec web uv run pytest -v
