"""Static HTML dashboard generation for GitHub Pages."""

import json
from pathlib import Path

from boston_needle_map.models import DashboardStats

# Project root: src/boston_needle_map/../../ = project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_TEMPLATE_PATH = _PROJECT_ROOT / "templates" / "dashboard.html"


def _load_template() -> str:
    """Load the HTML template from the templates directory."""
    return _TEMPLATE_PATH.read_text(encoding="utf-8")


def generate_html(stats: DashboardStats) -> str:
    """Inject computed stats into the HTML template."""
    html = _load_template()
    html = html.replace("$GENERATED", stats.generated)
    html = html.replace("$TOTAL", f"{stats.total:,}")
    html = html.replace("$PEAK_HOOD", stats.peak_hood)
    html = html.replace("${PEAK_HOUR}", str(stats.peak_hour))
    html = html.replace("$PEAK_DOW", stats.peak_dow)
    html = html.replace("$AVG_MONTHLY", str(stats.avg_monthly))
    html = html.replace("$YEARS_JSON", json.dumps(stats.years))
    html = html.replace("$YEAR_MONTHLY_JSON", json.dumps(stats.year_monthly))
    html = html.replace("$YEARS", ", ".join(str(y) for y in stats.years))
    html = html.replace("$HEAT_KEYS_JSON", json.dumps({k: v for k, v in stats.heat_keys.items()}))
    html = html.replace("$MARKERS_JSON", json.dumps([m.model_dump() for m in stats.markers]))
    html = html.replace("$HOODS_JSON", json.dumps([h.model_dump() for h in stats.hoods]))
    html = html.replace("$HOURLY_JSON", json.dumps(stats.hourly))
    html = html.replace("$ZIP_STATS_JSON", json.dumps([z.model_dump() for z in stats.zip_stats]))
    return html
