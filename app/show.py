import os
import json
import threading
import time
import logging
from datetime import date
from flask import Flask, render_template

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

app_student = Flask("student_app", template_folder="templates")
app_teacher = Flask("teacher_app", template_folder="templates")

data_lock = threading.Lock()
sub_data = {}


def load_substitution_data():
    base = os.path.join(os.path.dirname(__file__), "data", "vertretungen")
    today = date.today().strftime("%Y-%m-%d")
    result = {}
    if not os.path.isdir(base):
        logging.warning("Verzeichnis nicht gefunden: %s", base)
        return result
    for fn in os.listdir(base):
        if fn.endswith(f"_{today}.json"):
            kl = fn.split("_")[0]
            path = os.path.join(base, fn)
            try:
                with open(path, encoding="utf-8") as f:
                    result[kl] = json.load(f)
            except Exception as e:
                logging.error("Fehler beim Laden %s: %s", fn, e)
                result[kl] = []
    return result


def data_reload_loop():
    while True:
        logging.info("Reload Vertretungen …")
        new = load_substitution_data()
        with data_lock:
            sub_data.clear()
            sub_data.update(new)
        time.sleep(60)


threading.Thread(target=data_reload_loop, daemon=True).start()


def load_banner_json():
    path = os.path.join(os.path.dirname(__file__), "banner_config.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"mode": "none", "text": ""}


@app_student.route("/")
def student_view():
    with data_lock:
        raw = dict(sub_data)
    data = {kl: raw[kl] for kl in sorted(raw)}
    banner = load_banner_json()
    return render_template(
        "student_template.html",
        data=data,
        banner=banner,
        today=date.today().isoformat()
    )


@app_teacher.route("/")
def teacher_view():
    with data_lock:
        raw = dict(sub_data)
    rows = []
    for kl, periods in raw.items():
        for p in periods:
            for teacher in p.get("teachers", []):
                rows.append({
                    "teacher": teacher,
                    "start": p.get("start", ""),
                    "end": p.get("end", ""),
                    "rooms": p.get("rooms", []),
                    "subjects": p.get("subjects", []),
                    "klasse": kl
                })
    rows.sort(key=lambda r: r["teacher"])
    banner = load_banner_json()
    return render_template(
        "teacher_template.html",
        rows=rows,
        banner=banner,
        today=date.today().isoformat()
    )


if __name__ == "__main__":
    from threading import Thread
    t1 = Thread(target=lambda: app_student.run(host="0.0.0.0", port=5000))
    t2 = Thread(target=lambda: app_teacher.run(host="0.0.0.0", port=5001))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
