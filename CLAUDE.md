# Boston Needle Map - Project Guide

## Quick Reference
- **Package manager:** uv (not pip/poetry)
- **CLI framework:** Typer
- **Data validation:** Pydantic v2
- **AI agents:** pydantic-ai (available, not yet actively used)
- **Linting:** ruff + mypy (strict mode)
- **Git hooks:** lefthook (runs ruff + mypy on pre-commit)
- **Python version:** 3.12+
- **UI exploration:** Streamlit (with folium + plotly)

## Commands
- `uv run boston-needle-map run` -- run the full pipeline (generates docs/index.html)
- `uv run boston-needle-map run 2023 2024 2025` -- specific years
- `uv run boston-needle-map run --no-cache` -- skip cache
- `uv run boston-needle-map explore` -- launch Streamlit dashboard
- `uv run boston-needle-map cache-clear` -- clear tmp/ cache
- `uv run boston-needle-map serve` -- preview at localhost:8000
- `uv run ruff check src/` -- lint
- `uv run ruff format src/` -- format
- `uv run mypy src/` -- type check
- `uv run pytest` -- run tests

## Architecture
- `src/boston_needle_map/` -- main package
  - `cli.py` -- Typer CLI entrypoint
  - `config.py` -- constants (CKAN URLs, resource IDs, bounding box)
  - `models.py` -- Pydantic models (CleanedRecord, DashboardStats, etc.)
  - `fetcher.py` -- CKAN API data fetching
  - `cleaner.py` -- raw record normalization and validation
  - `analytics.py` -- stats computation (heatmap bins, neighborhoods, hourly)
  - `renderer.py` -- HTML dashboard generation (for GitHub Pages)
  - `cache.py` -- tmp/ directory caching for fetched data
  - `app.py` -- Streamlit interactive dashboard
- `templates/dashboard.html` -- HTML template with $PLACEHOLDER tokens
- `docs/` -- generated output for GitHub Pages (do not edit manually)
- `tmp/` -- cached API responses (gitignored)

## Conventions
- All data flows through Pydantic models (CleanedRecord, DashboardStats)
- Never commit secrets or API keys
- Generated files go to docs/; never edit docs/ manually
- Cache files go to tmp/; this directory is gitignored
- Use `python-dateutil` for datetime parsing
