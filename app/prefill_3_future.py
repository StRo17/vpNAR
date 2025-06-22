#!/usr/bin/env python3
"""
Prefill: Lädt Stundenpläne für heute bis heute+OFFSET_DAYS
und speichert sie in data/3_future/<klasse>_<YYYY-MM-DD>.json.
"""
import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv
import webuntis

# ─── Basispfad & Env ─────────────────────────────────────────────────────────
BASEDIR = Path(__file__).parent
load_dotenv(dotenv_path=BASEDIR.parent / ".env")

SERVER = sys.getenv("WEBUNTIS_SERVER")
USERNAME = sys.getenv("WEBUNTIS_USER")
PASSWORD = sys.getenv("WEBUNTIS_PASSWORD")
SCHOOL = sys.getenv("WEBUNTIS_SCHOOL")
DAYS = int(sys.getenv("OFFSET_DAYS", "35"))

# ─── Zielverzeichnis ─────────────────────────────────────────────────────────
TARGET_DIR = BASEDIR / "data" / "3_future"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def extract_list(obj_list):
    names = [getattr(o, "name", None) for o in (obj_list or [])]
    return [n for n in names if n] or ["Unbekannt"]


def main():
    logging.info(f"Starte Prefill für {DAYS} Tage …")
    try:
        with webuntis.Session(
            server=SERVER,
            username=USERNAME,
            password=PASSWORD,
            school=SCHOOL,
            useragent="PrefillBot/1.0",
        ).login() as session:
            klassen = session.klassen()
            for delta in range(DAYS + 1):
                dt = date.today() + timedelta(days=delta)
                ds = dt.isoformat()
                for klass in klassen:
                    table = session.timetable(klasse=klass, start=dt, end=dt)
                    out = []
                    for p in table:
                        out.append(
                            {
                                "start": p.start.strftime("%H:%M"),
                                "end": p.end.strftime("%H:%M"),
                                "subjects": extract_list(getattr(p, "subjects", [])),
                                "teachers": extract_list(getattr(p, "teachers", [])),
                                "rooms": extract_list(getattr(p, "rooms", [])),
                                "info": getattr(p, "code", None)
                                or getattr(p, "info", None),
                            }
                        )
                    fn = f"{klass.name.lower().replace(' ', '')}_{ds}.json"
                    fp = TARGET_DIR / fn
                    fp.write_text(
                        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    logging.info(f"✔ {fn}")
    except Exception as e:
        logging.error(f"Fehler: {e}")


if __name__ == "__main__":
    main()
