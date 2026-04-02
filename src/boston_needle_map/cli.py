"""Typer CLI for the Boston 311 Needle Hotspot Pipeline."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from boston_needle_map.cache import clear_cache, load_cached, save_cache
from boston_needle_map.cleaner import clean
from boston_needle_map.config import RESOURCE_IDS
from boston_needle_map.fetcher import fetch_year
from boston_needle_map.models import CleanedRecord

app = typer.Typer(
    name="boston-needle-map",
    help="Boston 311 Needle Hotspot Pipeline",
)


@app.command()
def run(
    years: Annotated[list[int] | None, typer.Argument(help="Years to fetch (defaults to last 3 + current)")] = None,
    output_dir: Annotated[str, typer.Option("--output-dir", "-o", help="Output directory")] = "docs",
    use_cache: Annotated[bool, typer.Option("--cache/--no-cache", help="Use tmp/ cache for fetched data")] = True,
) -> None:
    """Fetch needle records, compute stats, and generate the HTML dashboard."""
    from boston_needle_map.analytics import compute_stats
    from boston_needle_map.renderer import generate_html

    if years is None:
        now = datetime.now().year
        years = [y for y in range(now - 2, now + 1) if y in RESOURCE_IDS]

    out = Path(output_dir)

    typer.echo(f"\u2554{'=' * 46}\u2557")
    typer.echo("\u2551  Boston 311 Needle Hotspot Pipeline          \u2551")
    typer.echo(f"\u2551  Years: {', '.join(str(y) for y in years):<37s} \u2551")
    typer.echo(f"\u255a{'=' * 46}\u255d")

    all_records: list[CleanedRecord] = []
    for year in years:
        raw: list[dict[str, object]]
        if use_cache:
            cached = load_cached(year)
            if cached is not None:
                raw = cached
            else:
                raw = fetch_year(year)
                if raw:
                    save_cache(year, raw)
        else:
            raw = fetch_year(year)

        cleaned = [r for r in (clean(row) for row in raw) if r is not None]
        typer.echo(f"  \u2713 {year}: {len(raw)} raw \u2192 {len(cleaned)} valid")
        all_records.extend(cleaned)

    if not all_records:
        typer.echo("\n\u26a0 No records retrieved. Writing placeholder page.")
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(
            "<html><body><h1>No data available</h1>"
            "<p>The pipeline could not retrieve data from data.boston.gov. "
            "Check the CKAN API or resource IDs.</p></body></html>"
        )
        return

    typer.echo(f"\n  Total valid records: {len(all_records):,}")
    typer.echo("  Computing stats...")

    stats = compute_stats(all_records)
    html = generate_html(stats)

    out.mkdir(parents=True, exist_ok=True)
    out_path = out / "index.html"
    out_path.write_text(html, encoding="utf-8")
    typer.echo(f"  \u2713 Wrote {out_path} ({len(html):,} bytes)")

    # Also dump raw data as JSON
    data_path = out / "needle_data.json"
    data_path.write_text(
        json.dumps(
            {
                "generated": stats.generated,
                "total": stats.total,
                "years": stats.years,
                "records": [r.model_dump() for r in all_records],
            }
        ),
        encoding="utf-8",
    )
    typer.echo(f"  \u2713 Wrote {data_path}")
    typer.echo("\n  Done. Preview with: boston-needle-map serve")


@app.command()
def explore() -> None:
    """Launch the Streamlit dashboard for interactive data exploration."""
    app_path = Path(__file__).parent / "app.py"
    typer.echo("Launching Streamlit app...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=False)


@app.command(name="cache-clear")
def cache_clear_cmd() -> None:
    """Clear all cached data in tmp/."""
    clear_cache()
    typer.echo("Cache cleared.")


@app.command()
def serve(
    port: Annotated[int, typer.Option("--port", "-p", help="Port to serve on")] = 8000,
    directory: Annotated[str, typer.Option("--dir", "-d", help="Directory to serve")] = "docs",
) -> None:
    """Serve the output directory locally for preview."""
    import functools
    import http.server

    d = Path(directory)
    if not d.exists():
        typer.echo(f"Directory {d} does not exist. Run 'boston-needle-map run' first.")
        raise typer.Exit(1)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(d))
    typer.echo(f"Serving {d}/ at http://localhost:{port}")
    with http.server.HTTPServer(("", port), handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    app()
