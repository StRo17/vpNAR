#!/usr/bin/env python3
"""
Lädt den Stundenplan von heute aus WebUntis und speichert ihn unter
data/actual/<klasse>_<YYYY-MM-DD>.json ab.
"""
import json, logging, sys
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import webuntis

# ─── Basispfad & Env ─────────────────────────────────────────────────────────
BASEDIR = Path(__file__).parent
load_dotenv(dotenv_path=BASEDIR.parent / ".env")

SERVER    = sys.getenv("WEBUNTIS_SERVER")
USERNAME  = sys.getenv("WEBUNTIS_USER")
PASSWORD  = sys.getenv("WEBUNTIS_PASSWORD")
SCHOOL    = sys.getenv("WEBUNTIS_SCHOOL")

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
        useragent="ActualLoadBot/1.0"
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
        return
    out = []
    for p in table:
        out.append({
            "start":    p.start.strftime("%H:%M"),
            "end":      p.end.strftime("%H:%M"),
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
        with login() as session:
            for klass in session.klassen():
                save_timetable(session, klass, heute)
    except Exception as e:
        logging.error(f"Fehler: {e}")

if __name__ == "__main__":
    main()
