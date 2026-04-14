# Home Base - MLB Team and Player Stats

A Python web application that displays MLB news, standings, team rosters, and player statistics using data from the MLB StatsAPI and RSS feeds.

## Tech Stack

- **Backend:** Python 3.12, Flask, Jinja2
- **Frontend:** Bootstrap 5, Inter & Chivo Mono fonts
- **Data:** MLB StatsAPI, MLB RSS feeds
- **Package Manager:** UV
- **Containerization:** Docker Compose

## Quick Start

### With Docker Compose (recommended)

```bash
docker compose up --build
```

Open http://localhost:5000

### Without Docker

Requires [UV](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
uv sync
uv run flask --app run.py run --debug
```

## Running Tests

```bash
# In Docker
docker compose exec web uv run pytest -v

# Locally
uv run pytest -v
```

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
├── __init__.py          # Flask app factory
├── config.py            # Configuration + MLB team data
├── clients/
│   ├── mlb_client.py    # StatsAPI client with TTL caching
│   └── mlb_news_client.py  # RSS feed client
├── services/
│   └── calculations.py  # SO% and BB% calculations
├── routes/              # Flask blueprints (one per page)
├── templates/           # Jinja2 templates
└── static/
    ├── css/style.css    # Global styles
    └── img/             # Logo assets
tests/
├── test_mlb_client.py
└── test_mlb_news_client.py
```

## Data Sources

- **StatsAPI:** https://statsapi.mlb.com — teams, standings, rosters, player stats, leaders
- **RSS Feeds:** https://www.mlb.com/feeds/news/rss.xml — MLB and team-specific news
- **Graphics:** Team logos, player headshots, ballpark images from MLB CDN
