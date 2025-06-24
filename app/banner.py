#!/usr/bin/env python3
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
import config

app = Flask(__name__, template_folder="templates")


def load_cfg():
    try:
        with open(config.BANNER_CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logging.exception("Fehler beim Laden der Banner-Konfiguration")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT_BANNER, debug=config.DEBUG_MODE)
