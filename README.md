# Home Base - MLB Team and Player Stats

A Python web application that displays MLB news, standings, team rosters, and player statistics. Data is sourced live from the MLB StatsAPI and MLB RSS feeds.

## Tech Stack

- **Backend:** Python 3.12, Flask, Jinja2
- **Frontend:** Bootstrap 5, Inter & Chivo Mono fonts
- **Data:** MLB StatsAPI, MLB RSS feeds
- **Package Manager:** UV
- **Containerization:** Docker Compose
- **Linting/Formatting:** Ruff (with pre-commit hooks)
- **Caching:** 2-layer — in-memory TTLCache + disk cache (1 hour TTL)

## Getting Started

The primary way to run this project is via Docker Compose.

```bash
docker compose up --build
```

Open http://localhost:5000

That's it. The app will build, install dependencies, and start with hot-reload enabled.

### Scripts

| Script | Description |
|--------|-------------|
| `./scripts/bootstrap.sh` | Build, start, verify, and run tests |
| `./scripts/run_dev.sh` | Start dev server and tail logs |
| `./scripts/run_tests.sh` | Run linter, formatter check, and tests |

### Without Docker

Requires [UV](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
uv sync
uv run flask --app run.py run --debug
```

## Running Tests

```bash
# Via script (lint + format + tests)
./scripts/run_tests.sh

# Or directly
docker compose exec web uv run pytest -v
```

94 tests covering API clients, all services, and calculations.

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Landing | `/` | Divisional standings, MLB news, league leaders |
| Standings | `/standings` | Full standings with Home/Away/1Run/Extra Inning win pcts |
| Team | `/team/<id>` | Roster (hitters + pitchers with stats), team news, leaders |
| Player | `/player/<id>` | Bio, season/career/projected stats, SO%/BB% calculated, last 7 games |
| Leaderboards | `/leaderboards` | Top 10 leaders in 4 hitting + 4 pitching categories |

## Project Structure

```
app/
├── __init__.py              # Flask app factory
├── config.py                # App configuration
├── constants.py             # MLB teams, divisions, leader categories
├── clients/
│   ├── mlb_client.py        # StatsAPI client (HTTP, caching, thread-safe)
│   ├── mlb_news_client.py   # RSS feed client (XML parsing, caching)
│   └── disk_cache.py        # File-based JSON cache with TTL
├── services/
│   ├── calculations.py      # SO% and BB% calculations
│   ├── standings.py         # Standings ordering and split pct extraction
│   ├── news.py              # MLB and team news fetching
│   ├── leaders.py           # Stat leader filtering by category/group
│   ├── team.py              # Team info and roster splitting
│   └── player.py            # Player stats, game log, calculated stats
├── routes/                  # Flask blueprints (thin HTTP handlers)
├── templates/               # Jinja2 templates
└── static/
    ├── css/style.css        # Global styles
    └── img/                 # Logo assets
scripts/
├── bootstrap.sh             # Full setup: build, start, verify, test
├── run_dev.sh               # Start dev server with log tailing
└── run_tests.sh             # Lint + format + test
tests/                       # 94 tests (clients, services, calculations)
```

## Data Sources

- **StatsAPI:** https://statsapi.mlb.com — teams, standings, rosters, player stats, leaders
- **RSS Feeds:** https://www.mlb.com/feeds/news/rss.xml — MLB and team-specific news
- **Graphics:** Team logos, player headshots from MLB CDN
