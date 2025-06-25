#!/usr/bin/env python3
import json
import logging
import os

import config
from flask import Flask, render_template, request

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__, template_folder="templates")


def load_all_data():
    d = {}
    base = getattr(config, "ACTUAL_DIR", None) or os.path.join(os.path.dirname(__file__), "data", "actual")
    if not os.path.isdir(base):
        return d
    for f in os.listdir(base):
        if not f.endswith(".json"):
            continue
        try:
            raw = json.loads(open(os.path.join(base, f), encoding="utf-8").read())
        except Exception:
            raw = []
        cls = f.split("_", 1)[0]
        entries = []
        for e in raw:
            entries.append(
                {
                    "Start": e.get("start", ""),
                    "End": e.get("end", ""),
                    "Subject": e.get("subjects", [""])[0],
                    "Room": e.get("rooms", [""])[0],
                    "Teacher": e.get("teachers", [""])[0],
                }
            )
        d.setdefault(cls, []).extend(entries)
    return d


def get_groups(data):
    grp = {"05": [], "06": [], "07": [], "08": [], "09": [], "10": [], "IFS": [], "EF": [], "Q1": [], "Q2": []}
    for c in data:
        k = c[:2]
        if k in grp:
            grp[k].append(c)
        elif c.startswith("IFS"):
            grp["IFS"].append(c)
        elif c.startswith("EF"):
            grp["EF"].append(c)
        elif c.startswith("Q1"):
            grp["Q1"].append(c)
        elif c.startswith("Q2"):
            grp["Q2"].append(c)
    return {g: v for g, v in grp.items() if v}


@app.route("/")
def show():
    data = load_all_data()
    groups = get_groups(data)
    keys = list(groups)
    g = request.args.get("group", keys[0] if keys else "")
    cls = groups.get(g, [])
    slots = sorted({f"{e['Start']} - {e['End']}" for ps in data.values() for e in ps})
    return render_template(
        "class_template.html",
        class_data=data,
        class_names=cls,
        time_slots=slots,
        groups=json.dumps(keys),
        current_group=g,
        refresh_interval=config.HTML_REFRESH_INTERVAL,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT_ROTATOR, debug=config.DEBUG_MODE)
