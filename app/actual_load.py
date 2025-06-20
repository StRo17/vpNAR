#!/usr/bin/env python3
"""
Lädt den heutigen Stundenplan jeder Klasse aus WebUntis
und legt ihn unter ./data/actual/<klasse>_<yyyy-mm-dd>.json ab.

Auf dem Raspberry Pi wird dieses Skript per cron (oder systemd-Timer) alle
3 Minuten gestartet – deshalb KEINE Endlosschleife hier.
"""
import os
import json
import logging
from datetime import date

import webuntis
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────
# 1.  ENV-Variablen laden
# ──────────────────────────────────────────────────────
load_dotenv("config.env")

SERVER   = os.getenv("WEBUNTIS_SERVER")
USERNAME = os.getenv("WEBUNTIS_USER")
PASSWORD = os.getenv("WEBUNTIS_PASSWORD")
SCHOOL   = os.getenv("WEBUNTIS_SCHOOL")
USERAGENT = "WebUntisClient/1.0"

TARGET_DIR = "./data/actual"
os.makedirs(TARGET_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ──────────────────────────────────────────────────────
# 2.  Hilfsfunktionen
# ──────────────────────────────────────────────────────
def login():
    session = webuntis.Session(
        server=SERVER,
        username=USERNAME,
        password=PASSWORD,
        school=SCHOOL,
        useragent=USERAGENT,
    )
    session.login()
    logging.info("Login erfolgreich.")
    return session


def extract_list(obj_list):
    """Gibt eine Liste gültiger Namen oder ['Unbekannt'] zurück."""
    if obj_list:
        names = [getattr(o, "name", None) for o in obj_list]
        names = [n for n in names if n]        # nur nicht-leere
        if names:
            return names
    return ["Unbekannt"]


def save_timetable_as_json(session, klasse, datum):
    table = session.timetable(klasse=klasse, start=datum, end=datum)
    if not table:
        logging.warning(f"Keine Einträge für {klasse.name} am {datum}.")
        return

    data = []
    for period in table:
        try:
            data.append(
                {
                    "start": period.start.strftime("%H:%M"),
                    "end": period.end.strftime("%H:%M"),
                    "subjects": extract_list(getattr(period, "subjects", [])),
                    "teachers": extract_list(getattr(period, "teachers", [])),
                    "rooms": extract_list(getattr(period, "rooms", [])),
                    "info": getattr(period, "code", None)
                    or getattr(period, "info", None),
                }
            )
        except Exception as pe:
            logging.error(f"{klasse.name}: Fehler in Periode – {pe}")

    filename = (
        f"{klasse.name.lower().replace(' ', '')}_{datum}.json"
    )
    filepath = os.path.join(TARGET_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logging.info(f"✔ Gespeichert: {filepath}")


# ──────────────────────────────────────────────────────
# 3.  Hauptlogik (einmaliger Lauf)
# ──────────────────────────────────────────────────────
def main():
    datum_heute = date.today()
    try:
        session = login()
        for klasse in session.klassen():
            save_timetable_as_json(session, klasse, datum_heute)
        session.logout()
    except Exception as e:
        logging.error(f"Abbruch: {e}")


if __name__ == "__main__":
    main()
