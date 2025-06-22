#!/usr/bin/env python3
"""
Vergleicht ./data/actual/*_<yyyy-mm-dd>.json mit
./data/original/*_<yyyy-mm-dd>.json und schreibt Änderungen nach
./data/vertretungen/*_<yyyy-mm-dd>.json
"""
import os
import json
import logging
from pathlib import Path
from datetime import date

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

BASE = Path("./data")
DIR_ACT = BASE / "actual"
DIR_ORIG = BASE / "original"
DIR_DIFF = BASE / "vertretungen"
DIR_DIFF.mkdir(parents=True, exist_ok=True)

today_str = date.today().strftime("%Y-%m-%d")


def load_json(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def period_key(p) -> str:
    """Eindeutiger Schlüssel pro Stunde + Raum + Fach + Lehrer"""
    return (
        p["start"],
        p["end"],
        "|".join(sorted(p["rooms"])),
        "|".join(sorted(p["subjects"])),
        "|".join(sorted(p["teachers"])),
    )


def diff_lists(orig, act):
    orig_map = {period_key(p): p for p in orig}
    act_map = {period_key(p): p for p in act}

    diffs = []

    # entfallen / geändert
    for k, p in orig_map.items():
        if k not in act_map:
            diffs.append({"status": "ENTFÄLLT", **p})

    # neu hinzu- / geändert
    for k, p in act_map.items():
        if k not in orig_map:
            diffs.append({"status": "NEU", **p})

    return diffs


def main():
    for act_file in DIR_ACT.glob(f"*_{today_str}.json"):
        orig_file = DIR_ORIG / act_file.name
        vert_file = DIR_DIFF / act_file.name

        orig = load_json(orig_file)
        act = load_json(act_file)

        if not orig:
            logging.warning("Kein Original für %s", act_file.name)
            continue

        changes = diff_lists(orig, act)

        with open(vert_file, "w", encoding="utf-8") as f:
            json.dump(changes, f, ensure_ascii=False, indent=2)

        logging.info("Δ %s – %d Änderungen", act_file.name, len(changes))


if __name__ == "__main__":
    main()
