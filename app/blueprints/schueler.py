from datetime import date

from flask import Blueprint, render_template
from utils import HTML_REFRESH, load_banner_json, load_substitution_data

bp = Blueprint("schueler", __name__, template_folder="../templates")


@bp.route("/")
def student_view():
    """Schüler-Vertretungsplan (nur NEU)."""
    data = load_substitution_data("schueler")
    data = {kl: [p for p in ps if p.get("status") == "NEU"] for kl, ps in data.items()}
    banner = load_banner_json()
    return render_template(
        "student_template.html", data=data, banner=banner, today=date.today().isoformat(), refresh=HTML_REFRESH
    )
