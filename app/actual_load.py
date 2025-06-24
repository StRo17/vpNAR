#!/usr/bin/env python3
"""
Lädt den Stundenplan von heute aus WebUntis und speichert ihn unter
data/actual/<klasse>_<YYYY-MM-DD>.json ab.
"""
import json
import logging
import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import webuntis

# ─── Basispfad & Env ─────────────────────────────────────────────────────────
BASEDIR = Path(__file__).parent
load_dotenv(dotenv_path=BASEDIR.parent / ".env")

SERVER = os.getenv("WEBUNTIS_SERVER")
USERNAME = os.getenv("WEBUNTIS_USER")
PASSWORD = os.getenv("WEBUNTIS_PASSWORD")
SCHOOL = os.getenv("WEBUNTIS_SCHOOL")

# ─── Zielverzeichnis ─────────────────────────────────────────────────────────
TARGET_DIR = BASEDIR / "data" / "actual"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def login():
    session = webuntis.Session(
        server=SERVER,
        username=USERNAME,
        password=PASSWORD,
        school=SCHOOL,
        useragent="ActualLoadBot/1.0",
    )
    session.login()
    logging.info("✔ WebUntis Login erfolgreich")
    return session


def extract_list(obj_list):
    names = [getattr(o, "name", None) for o in (obj_list or [])]
    return [n for n in names if n] or ["Unbekannt"]


def save_timetable(session, klass, dt):
    table = session.timetable(klasse=klass, start=dt, end=dt)
    if not table:
        logging.warning(f"Keine Einträge für {klass.name} am {dt}")
    out = []
    for p in (table or []):
        out.append({
            "start": p.start.strftime("%H:%M"),
            "end":   p.end.strftime("%H:%M"),
            "subjects": extract_list(getattr(p, "subjects", [])),
            "teachers": extract_list(getattr(p, "teachers", [])),
            "rooms":    extract_list(getattr(p, "rooms", [])),
            "info":     getattr(p, "code", None) or getattr(p, "info", None),
        })
    fn = f"{klass.name.lower().replace(' ', '')}_{dt.isoformat()}.json"
    fp = TARGET_DIR / fn
    fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info(f"✔ Gespeichert: {fp}")


def main():
    heute = date.today()
    try:
        session = login()
    except Exception as e:
        logging.error(f"Fehler beim Login: {e}")
        return

    for klass in session.klassen():
        try:
            save_timetable(session, klass, heute)
        except Exception as e:
            logging.error(f"Fehler bei {klass.name}: {e}")
    try:
        session.logout()
    except Exception:
        pass


if __name__ == "__main__":
    main()
