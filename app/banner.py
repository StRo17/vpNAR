#!/usr/bin/env python3
import json
import subprocess
import config
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__, template_folder="templates")


def load_cfg():
    try:
        return json.loads(open(config.BANNER_CONFIG_PATH, encoding="utf-8").read())
    except BaseException:
        return {"mode": "none", "text": ""}


def save_cfg(c):
    with open(config.BANNER_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)


@app.route("/", methods=["GET", "POST"])
def edit():
    c = load_cfg()
    if request.method == "POST":
        c["mode"] = request.form["mode"]
        c["text"] = request.form["text"]
        save_cfg(c)
        return redirect(url_for("edit"))
    return render_template("banner_template.html", **c)


@app.route("/banner.json")
def api():
    return jsonify(load_cfg())


@app.route("/run_script", methods=["POST"])
def run_script():
    # Map Button-Name zu Skript-Datei
    script_map = {
        "shift": "shift.py",
        "actual_load": "actual_load.py",
        "original_load": "original_load.py",
        "compare": "compare.py",
    }
    script = request.form.get("script")
    if script in script_map:
        try:
            # Skript aufrufen (ggf. Pfad anpassen!)
            subprocess.run(["python3", script_map[script]], check=True)
            # Erfolgsmeldung an Template (optional)
            message = f"{script_map[script]} erfolgreich ausgeführt."
        except subprocess.CalledProcessError as e:
            message = f"Fehler beim Ausführen von {script_map[script]}: {e}"
    else:
        message = "Unbekanntes Skript."
    # Konfiguration wie sonst laden und Meldung ins Template geben
    c = load_cfg()
    c["message"] = message
    return render_template("banner_template.html", **c)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT_BANNER, debug=config.DEBUG_MODE)
