from datetime import date

from flask import Blueprint, render_template
from utils import HTML_REFRESH, load_banner_json, load_substitution_data

bp = Blueprint("lehrer", __name__, url_prefix="/teacher", template_folder="../templates")


@bp.route("/")
def teacher_view():
    """Lehrer-Vertretungsplan (nur NEU)."""
    diffs = load_substitution_data("lehrer")
    diffs = [p for p in diffs if p.get("status") == "NEU"]
    rows = []
    for p in diffs:
        rows.append(
            {
                "teacher": p.get("teacher", ""),
                "start": p.get("start", ""),
                "end": p.get("end", ""),
                "klasse": p.get("klasse", ""),
                "subjects": p.get("subjects", []),
                "rooms": p.get("rooms", []),
            }
        )
    rows.sort(key=lambda r: (r["teacher"], r["start"]))
    banner = load_banner_json()
    return render_template(
        "teacher_template.html", rows=rows, banner=banner, today=date.today().isoformat(), refresh=HTML_REFRESH
    )
