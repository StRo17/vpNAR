#!/usr/bin/env python3
"""
Lädt den Original-Plan für heute+OFFSET_DAYS und speichert in data/original/.
"""
import json
import logging
import sys
import os
from datetime import datetime, timedelta
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
DAYS = int(os.getenv("OFFSET_DAYS", "35"))

# ─── Zielverzeichnis ─────────────────────────────────────────────────────────
TARGET_DIR = BASEDIR / "data" / "original"
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
        useragent="OrigLoadBot/1.0",
    )
    session.login()
    logging.info("✔ WebUntis Login erfolgreich")
    return session


def extract_list(obj_list):
    names = [getattr(o, "name", None) for o in (obj_list or [])]
    return [n for n in names if n] or ["Unbekannt"]


def main():
    target = datetime.now() + timedelta(days=DAYS)
    ds = target.date().isoformat()
    try:
        with login() as session:
            for klass in session.klassen():
                table = session.timetable(klasse=klass, start=target, end=target)
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
