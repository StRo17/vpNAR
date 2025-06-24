from flask import Blueprint, render_template, request
from class_show import load_all_data, get_groups

bp = Blueprint("timetable", __name__, url_prefix="/timetable", template_folder="../templates")


@bp.route("/")
def timetable_view():
    """Stundenplan-Rotator für alle Klassen."""
    class_data = load_all_data()
    group_keys = list(get_groups(class_data).keys())
    grp = request.args.get("group", group_keys[0] if group_keys else "")
    class_names = get_groups(class_data).get(grp, [])
    time_slots = sorted({f"{e['Start']} - {e['End']}" for ps in class_data.values() for e in ps})
    return render_template(
        "class_template.html",
        class_data=class_data,
        class_names=class_names,
        time_slots=time_slots,
        groups=group_keys,
        current_group=grp,
        refresh_interval=10,
    )
