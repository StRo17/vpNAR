#!/usr/bin/env python3
"""
Prefill: Lädt Stundenpläne für heute bis heute+OFFSET_DAYS
und speichert sie in ./data/3_future/<klasse>_<yyyy-mm-dd>.json.
"""
import os
import json
import logging
from datetime import date, timedelta

import webuntis
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
# 1) ENV laden (erwartet WEBUNTIS_*, OFFSET_DAYS optional)
# ──────────────────────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "config.env"))

SERVER     = os.getenv("WEBUNTIS_SERVER")
SCHOOL     = os.getenv("WEBUNTIS_SCHOOL")
USERNAME   = os.getenv("WEBUNTIS_USER")
PASSWORD   = os.getenv("WEBUNTIS_PASSWORD")
USERAGENT  = os.getenv("WEBUNTIS_USERAGENT", "PrefillBot")
OFFSET_DAYS= int(os.getenv("OFFSET_DAYS", "35"))
TARGET_DIR = os.path.join(os.path.dirname(__file__), "data", "3_future")

# ──────────────────────────────────────────────────────────────────────────────
# 2) Setup
# ──────────────────────────────────────────────────────────────────────────────
os.makedirs(TARGET_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def extract_list(obj_list):
    """Extrahiere Namen aus WebUntis-Objekten, gib ['Unbekannt'] zurück, wenn leer."""
    names = [getattr(o, "name", None) for o in obj_list]
    names = [n for n in names if n]
    return names or ["Unbekannt"]

def fetch_for_class_and_date(session, klass, dt):
    """Hole timetable für eine Klasse an einem Datum."""
    # hier _genau_ ein keyword-Argument: klasse=klass
    table = session.timetable(klasse=klass, start=dt, end=dt)
    out = []
    for p in table:
        out.append({
            "start":    p.start.strftime("%H:%M"),
            "end":      p.end.strftime("%H:%M"),
            "subjects": extract_list(getattr(p, "subjects", [])),
            "teachers": extract_list(getattr(p, "teachers", [])),
            "rooms":    extract_list(getattr(p, "rooms", [])),
            "info":     getattr(p, "code", None) or getattr(p, "info", None)
        })
    return out

# ──────────────────────────────────────────────────────────────────────────────
# 3) Hauptprogramm
# ──────────────────────────────────────────────────────────────────────────────
def main():
    logging.info("Starte Prefill für %d Tage …", OFFSET_DAYS)
    with webuntis.Session(
        server=SERVER,
        school=SCHOOL,
        username=USERNAME,
        password=PASSWORD,
        useragent=USERAGENT
    ).login() as session:

        klassen = session.klassen()
        for delta in range(0, OFFSET_DAYS + 1):
            dt = date.today() + timedelta(days=delta)
            ds = dt.isoformat()
            for klass in klassen:
                fname = f"{klass.name.lower().replace(' ', '')}_{ds}.json"
                fpath = os.path.join(TARGET_DIR, fname)
                try:
                    data = fetch_for_class_and_date(session, klass, dt)
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    logging.info("✔ %s", fname)
                except Exception as e:
                    logging.error("✗ %s für %s: %s", klass.name, ds, e)

    logging.info("Prefill fertig.")

if __name__ == "__main__":
    main()
