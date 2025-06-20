#!/usr/bin/env python3
"""
Lädt Pläne für <heute + OFFSET_DAYS> (Default 49) für alle Klassen
und legt sie unter ./data/3_future/<klasse>_<yyyy-mm-dd>.json ab.
"""
import os, json, logging
from datetime import datetime, timedelta
import webuntis
from dotenv import load_dotenv

load_dotenv("config.env")

SERVER      = os.getenv("WEBUNTIS_SERVER")
USERNAME    = os.getenv("WEBUNTIS_USER")
PASSWORD    = os.getenv("WEBUNTIS_PASSWORD")
SCHOOL      = os.getenv("WEBUNTIS_SCHOOL")
USERAGENT   = "OrigLoadBot"

OFFSET_DAYS = int(os.getenv("OFFSET_DAYS", "21"))   # z. B. 21 / 28 … / 49
TARGET_DIR  = "./data/3_future"

os.makedirs(TARGET_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

def extract_list(obj_list):
    if obj_list:
        names = [getattr(o, "name", None) for o in obj_list]
        names = [n for n in names if n]
        if names:
            return names
    return ["Unbekannt"]

def main():
    target_date = datetime.now() + timedelta(days=OFFSET_DAYS)
    ds = target_date.strftime("%Y-%m-%d")

    with webuntis.Session(server=SERVER,
                          username=USERNAME,
                          password=PASSWORD,
                          school=SCHOOL,
                          useragent=USERAGENT).login() as s:

        for k in s.klassen():
            fname = f"{k.name.lower().replace(' ', '')}_{ds}.json"
            fpath = os.path.join(TARGET_DIR, fname)

            try:
                table = s.timetable(klasse=k, start=target_date, end=target_date)
                data  = []
                for p in table:
                    data.append({
                        "start":    p.start.strftime("%H:%M"),
                        "end":      p.end.strftime("%H:%M"),
                        "subjects": extract_list(getattr(p,"subjects",[])),
                        "teachers": extract_list(getattr(p,"teachers",[])),
                        "rooms":    extract_list(getattr(p,"rooms",[])),
                        "info":     getattr(p,"code",None) or getattr(p,"info",None)
                    })
                with open(fpath,"w",encoding="utf-8") as f:
                    json.dump(data,f,ensure_ascii=False,indent=2)
                logging.info("✔ %s", fname)
            except Exception as e:
                logging.error("⚠ %s – %s", k.name, e)

if __name__ == "__main__":
    main()
