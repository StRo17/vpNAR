#!/usr/bin/env python3
"""
Prefill: Lädt Stundenpläne für heute bis heute+OFFSET_DAYS
und speichert sie in data/3_future/<klasse>_<YYYY-MM-DD>.json.
"""
import json
import logging
import os
from datetime import date, timedelta
from pathlib import Path

import webuntis
from dotenv import load_dotenv

# ─── Basispfad & Env ─────────────────────────────────────────────────────────
BASEDIR = Path(__file__).parent
# Lade die .env im Anwendungsverzeichnis (nicht /)
load_dotenv(dotenv_path=BASEDIR / ".env")

SERVER = os.getenv("WEBUNTIS_SERVER")
USERNAME = os.getenv("WEBUNTIS_USER")
PASSWORD = os.getenv("WEBUNTIS_PASSWORD")
SCHOOL = os.getenv("WEBUNTIS_SCHOOL")

# ─── Zielverzeichnis ─────────────────────────────────────────────────────────
TARGET_DIR = BASEDIR / "data" / "3_future"
TARGET_DIR.mkdir(parents=True, exist_ok=True)


def extract_list(obj_list):
    names = [getattr(o, "name", None) for o in (obj_list or [])]
    return [n for n in names if n] or ["Unbekannt"]


def main():
    # Initial log
    logging.info("Starte Prefill ...")

    session = webuntis.Session(
        server=SERVER,
        username=USERNAME,
        password=PASSWORD,
        school=SCHOOL,
        useragent="PrefillBot/1.0",
    )

    try:
        # Login once
        session.login()
        logging.info("✔ WebUntis Login erfolgreich")

        # Determine dynamic DAYS if environment value is zero or missing
        try:
            env_days = int(os.getenv("OFFSET_DAYS", "0"))
        except ValueError:
            env_days = 0

        if env_days <= 0:
            # Find the active school year and its end date
            sy_list = session.schoolyears()
            today = date.today()
            end_date = None
            for sy in sy_list:
                # Use sy.startDate and sy.endDate attributes
                if sy.startDate <= today <= sy.endDate:
                    end_date = sy.endDate
                    break
            if end_date is None:
                logging.warning("Aktives Schuljahr nicht gefunden, verwende OFFSET_DAYS")
                days = abs(env_days) or 35
            else:
                days = (end_date - today).days
        else:
            days = env_days

        logging.info(f"Starte Prefill für {days} Tage …")

        klassen = session.klassen()

        # Loop through each day and each class
        for delta in range(days + 1):
            dt = date.today() + timedelta(days=delta)
            ds = dt.isoformat()

            for klass in klassen:
                try:
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
                                "info": getattr(p, "code", None) or getattr(p, "info", None),
                            }
                        )
                    fn = f"{klass.name.lower().replace(' ', '')}_{ds}.json"
                    fp = TARGET_DIR / fn
                    fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
                    logging.info(f"✔ {fn}")
                except Exception as e:
                    logging.error(f"Fehler beim Prefill für {klass.name} am {ds}: {e}")
                    continue

    except Exception as e:
        logging.error(f"Fehler in Prefill-Job: {e}")

    finally:
        # Logout if possible
        try:
            session.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()
