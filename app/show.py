#!/usr/bin/env python3
import os
import json
import logging
from datetime import date
from flask import Flask, jsonify
from utils import load_substitution_data, load_banner_json, HTML_REFRESH

# Flask application
app = Flask(__name__, template_folder="templates")

# Banner JSON endpoint
@app.route("/banner.json")
def banner_api():
    return jsonify(load_banner_json())

# Register blueprints
from blueprints.schueler import bp as schueler_bp
from blueprints.lehrer import bp as lehrer_bp
from blueprints.timetable import bp as timetable_bp

app.register_blueprint(schueler_bp)
app.register_blueprint(lehrer_bp)
app.register_blueprint(timetable_bp)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app.run(host="0.0.0.0", port=5000, debug=False)