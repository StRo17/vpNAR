#!/usr/bin/env python3
import os
import json
import threading
import time
import logging
from datetime import date
from flask import Flask, render_template_string

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

app_student = Flask("student_app")
app_teacher = Flask("teacher_app")

data_lock = threading.Lock()
sub_data = {}


def load_substitution_data():
    """Lädt alle Vertretungen für heute aus data/vertretungen."""
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
    """Hintergrundthread: alle 7.15 Min. Vertretungen neu laden."""
    while True:
        logging.info("Reload Vertretungen …")
        new = load_substitution_data()
        with data_lock:
            sub_data.clear()
            sub_data.update(new)
        time.sleep(60)


threading.Thread(target=data_reload_loop, daemon=True).start()


def load_banner_json():
    """Lädt banner_config.json bei jedem Request frisch ein."""
    path = os.path.join(os.path.dirname(__file__), "banner_config.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"mode": "none", "text": ""}


student_template = """
<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="60">
<title>Schüler-Vertretungen</title>
<style>
  body { margin:0; font-family:sans-serif; }
  #table-container {
    height: calc(100vh - 10vh);
    overflow-y: auto;
    padding: 10px;
    padding-bottom: 20vh;
  }
  table {
    width: 95%;
    border-collapse: collapse;
    font-size: 1.5vw;
    margin: 0 auto;
  }
  th, td {
    border: 1px solid #333;
    padding: 8px;
    text-align: center;
  }
  th {
    background: #0066CC;
    color: #fff;
  }
  #banner {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 10vh;
    border-top: 1px solid #444;
    padding: 8px;
    background: #e0e0e0;
    font-size: 8vh;
    line-height: 10vh;
    text-align: center;
    color: red;
    overflow: hidden;
    white-space: nowrap;
  }
  .signature {
    text-align: right;
    font-size: 1vw;
    color: #666;
    margin-top: 1em;
  }
  .footer-spacer { 
    height: 10vh; 
  }
</style>
</head><body>
  <div id="table-container">
    <h2>Vertretungen am {{ today }}</h2>
    <table>
      <tr><th>Klasse</th><th>Stunde</th><th>Raum</th><th>Fach</th><th>Lehrer</th></tr>
      {% for kl, periods in data.items() %}
        {% for p in periods %}
        <tr>
          <td>{{ kl }}</td>
          <td>{{ p.start }}–{{ p.end }}</td>
          <td>{{ p.rooms|join(", ") }}</td>
          <td>{{ p.subjects|join(", ") }}</td>
          <td>{{ p.teachers|join(", ") }}</td>
        </tr>
        {% endfor %}
      {% endfor %}
    </table>
    <div class="signature">@Nargang</div>
    <div class="footer-spacer"></div>
  </div>

  <div id="banner">
    {% if banner.mode=='text' %}{{ banner.text }}{% endif %}
  </div>

  <script>
    const speed = 50;       // ms pro Schritt
    const step = 1;         // px pro Schritt
    const pause = 2000;     // ms Pause am Ende
    const container = document.getElementById('table-container');
    let scrolling = true;

    function scrollStep() {
      if (!scrolling) return;
      container.scrollBy(0, step);
      if (container.scrollTop + container.clientHeight >= container.scrollHeight) {
        scrolling = false;
        setTimeout(() => {
          container.scrollTo({ top: 0, behavior: 'smooth' });
          setTimeout(() => scrolling = true, 500);
        }, pause);
      }
    }

    setInterval(scrollStep, speed);
  </script>
</body></html>
"""

teacher_template = """
<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="60">
<title>Lehrer-Vertretungen</title>
<style>
  body { margin:0; font-family:sans-serif; }
  #table-container {
    height: calc(100vh - 10vh);
    overflow-y: auto;
    padding: 10px;
    padding-bottom: 20vh;
  }
  table {
    width: 95%;
    border-collapse: collapse;
    font-size: 1.5vw;
    margin: 0 auto;
  }
  th, td {
    border: 1px solid #333;
    padding: 8px;
    text-align: center;
  }
  th {
    background: #CC6600;
    color: #fff;
  }
  #banner {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 10vh;
    border-top: 1px solid #444;
    padding: 8px;
    background: #e0e0e0;
    font-size: 8vh;
    line-height: 10vh;
    text-align: center;
    color: red;
    overflow: hidden;
    white-space: nowrap;
  }
  .signature {
    text-align: right;
    font-size: 1vw;
    color: #666;
    margin-top: 1em;
  }
  .footer-spacer {
    height: 10vh;
  }
</style>
</head><body>
  <div id="table-container">
    <h2>Vertretungen am {{ today }}</h2>
    <table>
      <tr><th>Lehrer</th><th>Stunde</th><th>Raum</th><th>Klasse</th><th>Fach</th></tr>
      {% for row in rows %}
      <tr>
        <td>{{ row.teacher }}</td>
        <td>{{ row.start }}–{{ row.end }}</td>
        <td>{{ row.rooms|join(", ") }}</td>
        <td>{{ row.klasse }}</td>
        <td>{{ row.subjects|join(", ") }}</td>
      </tr>
      {% endfor %}
    </table>
    <div class="signature">@Nargang</div>
    <div class="footer-spacer"></div>
  </div>

  <div id="banner">
    {% if banner.mode=='text' %}{{ banner.text }}{% endif %}
  </div>

  <script>
    const speed = 50;
    const step = 1;
    const pause = 2000;
    const container = document.getElementById('table-container');
    let scrolling = true;

    function scrollStep() {
      if (!scrolling) return;
      container.scrollBy(0, step);
      if (container.scrollTop + container.clientHeight >= container.scrollHeight) {
        scrolling = false;
        setTimeout(() => {
          container.scrollTo({ top: 0, behavior: 'smooth' });
          setTimeout(() => scrolling = true, 500);
        }, pause);
      }
    }

    setInterval(scrollStep, speed);
  </script>
</body></html>
"""


@app_student.route("/")
def student_view():
    with data_lock:
        raw = dict(sub_data)
    # Klassen alphabetisch sortieren
    data = {kl: raw[kl] for kl in sorted(raw)}
    banner = load_banner_json()
    return render_template_string(
        student_template, data=data, banner=banner, today=date.today().isoformat()
    )


@app_teacher.route("/")
def teacher_view():
    with data_lock:
        raw = dict(sub_data)
    # Für jede Vertretung einen Eintrag pro Lehrer, dann global nach Kürzel sortieren
    rows = []
    for kl, periods in raw.items():
        for p in periods:
            for teacher in p.get("teachers", []):
                rows.append(
                    {
                        "teacher": teacher,
                        "start": p.get("start", ""),
                        "end": p.get("end", ""),
                        "rooms": p.get("rooms", []),
                        "subjects": p.get("subjects", []),
                        "klasse": kl,
                    }
                )
    rows.sort(key=lambda r: r["teacher"])
    banner = load_banner_json()
    return render_template_string(
        teacher_template, rows=rows, banner=banner, today=date.today().isoformat()
    )


if __name__ == "__main__":
    from threading import Thread

    t1 = Thread(target=lambda: app_student.run(host="0.0.0.0", port=5000))
    t2 = Thread(target=lambda: app_teacher.run(host="0.0.0.0", port=5001))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
