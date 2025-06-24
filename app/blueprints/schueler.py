# app/blueprints/schueler.py
from flask import Blueprint, render_template
from datetime import date
from utils import load_substitution_data, load_banner_json, HTML_REFRESH

bp = Blueprint(
    "schueler",
    __name__,
    url_prefix="/",                 # Root-Pfad für Schüler-Vertretungen
    template_folder="../templates",
)

@bp.route("/")
def student_view():
    """Schüler-Vertretungsplan (nur NEU)."""
    data = load_substitution_data("schueler")
    # Nur neue (NEU) Einträge zeigen
    data = {
        klass: [p for p in periods if p.get("status") == "NEU"]
        for klass, periods in data.items()
    }
    banner = load_banner_json()
    return render_template(
        "student_template.html",
        data=data,
        banner=banner,
        today=date.today().isoformat(),
        refresh=HTML_REFRESH,
    )