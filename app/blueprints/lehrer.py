from datetime import date

from flask import Blueprint, render_template
from utils import HTML_REFRESH, load_banner_json, load_substitution_data

bp = Blueprint(
    "lehrer", __name__, url_prefix="/teacher", template_folder="../templates"
)


@bp.route("/")
def teacher_view():
    diffs = [p for p in load_substitution_data("lehrer") if p.get("status") == "NEU"]
    grouped = {}
    # Group by teacher, start, end, room
    for p in diffs:
        teacher = p.get("teacher", "")
        start = p.get("start", "")
        end = p.get("end", "")
        room = (p.get("rooms") or [""])[0]
        key = (teacher, start, end, room)
        if key not in grouped:
            grouped[key] = {
                "teacher": teacher,
                "start": start,
                "end": end,
                "room": room,
                "classes": set(),
                "subjects": set(),
            }
        grouped[key]["classes"].add(p.get("klasse", ""))
        # assume one subject per entry
        subj = (p.get("subjects") or [""])[0]
        if subj:
            grouped[key]["subjects"].add(subj)

    # Build rows
    rows = []
    for v in grouped.values():
        rows.append(
            {
                "teacher": v["teacher"],
                "start": v["start"],
                "end": v["end"],
                "classes": sorted(v["classes"]),
                "subjects": sorted(v["subjects"]),
                "room": v["room"],
            }
        )
    rows.sort(key=lambda r: (r["teacher"], r["start"]))

    banner = load_banner_json()
    return render_template(
        "teacher_template.html",
        rows=rows,
        banner=banner,
        today=date.today().isoformat(),
        refresh=HTML_REFRESH,
    )


"""
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
"""
